#!/bin/bash
# Dev variant of init.sh.
#
# Upstream init.sh runs `bench get-app lms`, which clones a FRESH copy of LMS from
# GitHub inside the container — so edits to your local checkout never reach the running
# app. Here the host repo is bind-mounted straight onto apps/lms by docker-compose.dev.yml,
# and this script registers that directory as the app instead of cloning anything.
#
# apps/lms is bind-mounted at a real path (not a symlink) on purpose: frontend/package.json
# declares `"@framework/ui": "link:../../frappe/ui"`, which only resolves from
# apps/lms/frontend, and frontend/vite.config.js hard-fails if that link dangles.

# No -u: the node bootstrap below probes variables that are legitimately unset.
set -eo pipefail

# The container command is not a login shell, so node is not on PATH yet. Upstream
# init.sh exports a path built from $NODE_VERSION_DEVELOP, which this image does not
# set -- it ships NODE_VERSION=24 and two nvm-managed versions. There the unset
# variable expands to empty and the bogus path is simply ignored, so it "works" by
# accident. Source nvm and select a version explicitly instead.
export NVM_DIR="${NVM_DIR:-/home/frappe/.nvm}"
# shellcheck source=/dev/null
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use "${NODE_VERSION:-24}" >/dev/null 2>&1 || nvm use default >/dev/null 2>&1 || true

command -v node >/dev/null || { echo "FATAL: node is not on PATH"; exit 1; }
command -v yarn >/dev/null || { echo "FATAL: yarn is not on PATH"; exit 1; }
echo ">>> Using node $(node -v), yarn $(yarn -v)"

# The SPA build OOMs at node's default heap ("FATAL ERROR: Ineffective mark-compacts near
# heap limit", exit 134). This frontend pulls in pdfjs-dist, editorjs, prosemirror, plyr
# and face-api.js, and rolls them up in one pass. Set above the branch below so an
# already-built bench inherits it for `yarn dev` as well.
export NODE_OPTIONS="${NODE_OPTIONS:---max-old-space-size=6144}"

BENCH_DIR=/home/frappe/frappe-bench
SITE=${SITE_NAME:-lms.localhost}
SITE_ADMIN_PASSWORD=${SITE_ADMIN_PASSWORD:-admin}
POSTGRES_HOST=${POSTGRES_HOST:-postgres}
POSTGRES_PORT=${POSTGRES_PORT:-5432}
POSTGRES_USER=${POSTGRES_USER:-postgres}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-123}
FRAPPE_BRANCH=${FRAPPE_BRANCH:-develop}
PAYMENTS_REPO=${PAYMENTS_REPO:-https://github.com/frappe/payments}
PAYMENTS_BRANCH=${PAYMENTS_BRANCH:-develop}
SOCKETIO_PORT=${SOCKETIO_PORT:-9000}
# Where the app is mounted. Empty (the default) means the site root, so the app is
# at http://localhost:8000/ and its pages are /courses, /batches and so on. Set
# LMS_PATH=lms to put it back under a /lms prefix.
#
# `${LMS_PATH-}` with one dash, not `:-`: "" is a real value here and the two-dash
# form would treat it as unset. The app has supported both shapes all along
# (hooks.py is_lms_at_root); this only chooses one.
LMS_PATH="${LMS_PATH-}"

# frontend/node_modules is a named volume (see docker-compose.dev.yml), and a fresh
# named volume is created root-owned, while yarn here runs as `frappe` -- so without
# this the install dies on "EACCES: permission denied, mkdir .../node_modules/...".
# Non-recursive, like the chown further down: the volume is empty on a first run, and
# on later runs everything inside it is already ours. Above the branch below, because
# the warm path exec's straight into `bench start` and would never reach it.
FRONTEND_MODULES="$BENCH_DIR/apps/lms/frontend/node_modules"
[ -d "$FRONTEND_MODULES" ] && sudo chown frappe:frappe "$FRONTEND_MODULES"

# Mount point, applied on every start so that changing LMS_PATH in .env actually
# takes effect. It has to happen BEFORE `bench start`: hooks.py builds
# website_route_rules and website_redirects at module import, reading this config
# as it goes, and Frappe then caches the result per site. Change it under a running
# server and the old routes stay until both the process and the cache are cleared.
set_lms_path() {
    cd "$BENCH_DIR"
    bench --site "$SITE" set-config lms_path "$LMS_PATH"
    bench --site "$SITE" clear-cache
}

# Outgoing mail. SendGrid when SENDGRID_API_KEY is set, mailpit when it is not.
#
# Something has to be configured either way. With no outgoing account at all
# Frappe does not fail loudly -- it takes a quiet fallback branch, so "Login
# with Email Link" reports success and sends nothing, and sign-up returns
# "Please ask your administrator to verify your sign-up" instead of "Please
# check your email" (frappe/core/doctype/user/user.py:1197). The account IS
# created either way, but nobody can reach it, so both flows look broken.
#
# site_config rather than an Email Account record, because Frappe reads these
# keys as its fallback outgoing account when no record exists
# (email_account.py:get_account_details_from_site_config), so there is no
# doctype row to create, migrate or keep in sync. An Email Account created in
# the desk still wins over both, which is the escape hatch if you want one.
#
# SendGrid's relay wants the literal string `apikey` as the username and the
# key itself as the password -- the key is NOT the username. Note the key lands
# in sites/$SITE/site_config.json in plain text; that file is in the `bench`
# named volume rather than your checkout, so it is not committable, but
# `docker compose down -v` is what actually removes it. SendGrid also rejects
# any FROM_EMAIL that is not a verified sender or on an authenticated domain,
# with a 403 that says nothing useful -- verify the address first.
set_mail() {
    cd "$BENCH_DIR"
    bench --site "$SITE" set-config auto_email_id "${FROM_EMAIL:-no-reply@lms.localhost}"
    bench --site "$SITE" set-config email_sender_name "${MAIL_SENDER_NAME:-Jutsu Academy}"

    if [ -n "${SENDGRID_API_KEY:-}" ]; then
        echo ">>> Outgoing mail: SendGrid, as ${FROM_EMAIL:-no-reply@lms.localhost}"
        bench --site "$SITE" set-config mail_server "${SENDGRID_HOST:-smtp.sendgrid.net}"
        bench --site "$SITE" set-config -p mail_port "${SENDGRID_PORT:-587}"
        bench --site "$SITE" set-config -p use_tls 1
        bench --site "$SITE" set-config -p disable_mail_smtp_authentication 0
        bench --site "$SITE" set-config mail_login apikey
        bench --site "$SITE" set-config mail_password "$SENDGRID_API_KEY"
    else
        echo ">>> Outgoing mail: mailpit, read it at http://localhost:${MAILPIT_UI_PORT:-8025}"
        bench --site "$SITE" set-config mail_server "${MAIL_SERVER:-mailpit}"
        bench --site "$SITE" set-config -p mail_port "${MAIL_PORT:-1025}"
        bench --site "$SITE" set-config -p disable_mail_smtp_authentication 1
        # Cleared rather than left behind, so switching back from SendGrid does
        # not leave a stale key pointing the site at a server it cannot reach.
        # Frappe skips falsy values when it reads these (email_account.py), so
        # an empty string reads the same as absent.
        bench --site "$SITE" set-config use_tls ""
        bench --site "$SITE" set-config mail_login ""
        bench --site "$SITE" set-config mail_password ""
    fi
}

if [ -d "$BENCH_DIR/apps/frappe" ]; then
    echo ">>> Bench already exists, skipping init."
    set_lms_path
    set_mail
    exec bench start
fi

echo ">>> Creating a new bench around your local LMS clone..."

# Docker creates the parent directories of a nested bind mount itself, as root, so
# frappe-bench/ and frappe-bench/apps/ arrive owned by root and `bench init` dies with
# "Permission denied: /home/frappe/frappe-bench/sites". Chown just those two -- NOT -R,
# which would recurse into the host repo. The mount itself is already writable by this
# user; only the directories Docker made are not.
sudo chown frappe:frappe "$BENCH_DIR" "$BENCH_DIR/apps"

# --ignore-exist: frappe-bench/ is already non-empty, because the apps/lms bind mount
# is created by Docker before this script runs.
#
# --skip-assets matters for the same reason: `bench init` ends with a `bench build`, and
# bench discovers apps by looking in apps/, where the mount has already put lms. It would
# try to build an app whose Python package is not installed yet and die on
# "ModuleNotFoundError: No module named 'lms'". Assets are built further down, once lms
# is a real editable install. CI skips them here too, for the same reason.
bench init \
    --ignore-exist \
    --skip-redis-config-generation \
    --skip-assets \
    --frappe-branch "$FRAPPE_BRANCH" \
    "$BENCH_DIR"

cd "$BENCH_DIR"

# Point bench at the sibling containers rather than localhost.
bench set-config -g db_host "$POSTGRES_HOST"
bench set-config -gp db_port "$POSTGRES_PORT"
bench set-redis-cache-host redis://redis:6379
bench set-redis-queue-host redis://redis:6379
bench set-redis-socketio-host redis://redis:6379
bench set-config -gp socketio_port "$SOCKETIO_PORT"

# Those services run as their own containers, and `watch` is replaced by vite.
sed -i '/redis/d' ./Procfile
sed -i '/watch/d' ./Procfile

# `bench serve` binds 127.0.0.1 by default, which inside a container means the loopback
# of the container itself: the published 8000:8000 mapping forwards to the container's
# external interface, finds nothing listening there, and every request from the host is
# refused. Bind all interfaces so the mapping has something to reach.
sed -i 's|^web: bench serve.*|web: bench serve --port 8000 --host 0.0.0.0|' ./Procfile

# Before `bench get-app`, which builds assets and would hit the same missing module.
echo ">>> Registering the bind-mounted local clone as the 'lms' app..."
./env/bin/pip install --no-cache-dir -e apps/lms
grep -qxF lms sites/apps.txt 2>/dev/null || echo lms >> sites/apps.txt

bench get-app --branch "$PAYMENTS_BRANCH" "$PAYMENTS_REPO"

bench new-site "$SITE" \
    --force \
    --db-type postgres \
    --db-host "$POSTGRES_HOST" \
    --db-port "$POSTGRES_PORT" \
    --db-root-username "$POSTGRES_USER" \
    --db-root-password "$POSTGRES_PASSWORD" \
    --admin-password "$SITE_ADMIN_PASSWORD" \
    --install-app payments

bench --site "$SITE" install-app lms
bench --site "$SITE" set-config developer_mode 1
bench --site "$SITE" clear-cache
bench use "$SITE"

echo ">>> Building the Vue frontend (this is the part you'll be restyling)..."
cd "$BENCH_DIR/apps/lms/frontend"
yarn install
# Safety net for the link vite.config.js asserts on. Harmless when yarn got it right.
mkdir -p node_modules/@framework
ln -sfn "$BENCH_DIR/apps/frappe/ui" node_modules/@framework/ui
yarn build

cd "$BENCH_DIR"
# Full build, not --app lms: `bench init --skip-assets` above means frappe's own assets
# have never been built in this bench.
bench build

set_lms_path
set_mail

if [ -z "$LMS_PATH" ]; then
    echo ">>> Ready. The app is at http://localhost:8000/ (and :8080 with hot reload)."
else
    echo ">>> Ready. The app is at http://localhost:8000/$LMS_PATH/"
fi
echo ">>> Site: $SITE (Administrator / configured SITE_ADMIN_PASSWORD)"
exec bench start
