#!/bin/bash
# Builds a bench around THIS checkout.
#
# This script used to run `bench get-app lms`, which resolves the bare name `lms`
# to https://github.com/frappe/lms and clones a fresh copy inside the container —
# so nothing in your working tree, and nothing on your fork, ever reached the
# running app. docker-compose.yml now bind-mounts the repo straight onto
# apps/lms and this registers that directory as the app instead of cloning.
#
# apps/lms is mounted at a real path rather than symlinked because bench
# discovers apps by listing apps/, and an editable pip install has to point at a
# stable location.

# No -u: the node bootstrap below probes variables that are legitimately unset.
set -eo pipefail

BENCH_DIR=/home/frappe/frappe-bench

# Site name. Override via env (compose / Dokploy). Defaults to `localhost` so
# http://localhost:8000 works with no custom hostname.
SITE_NAME="${SITE_NAME:-localhost}"

# The container command is not a login shell, so node is not on PATH yet. This
# previously exported a path built from $NODE_VERSION_DEVELOP, which this image
# does not set — the unset variable expanded to empty and the bogus path was
# ignored, so it only "worked" because nothing here needed node. Building the
# SPA does, so source nvm and select a version explicitly.
export NVM_DIR="${NVM_DIR:-/home/frappe/.nvm}"
# shellcheck source=/dev/null
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use "${NODE_VERSION:-24}" >/dev/null 2>&1 || nvm use default >/dev/null 2>&1 || true

command -v node >/dev/null || { echo "FATAL: node is not on PATH"; exit 1; }
command -v yarn >/dev/null || { echo "FATAL: yarn is not on PATH"; exit 1; }
echo ">>> Using node $(node -v), yarn $(yarn -v)"

# The SPA build OOMs at node's default heap ("FATAL ERROR: Ineffective
# mark-compacts near heap limit", exit 134): pdfjs-dist, editorjs, prosemirror
# and plyr are rolled up in one pass. Set above the warm-start branch so a
# rebuild in an existing bench inherits it too.
export NODE_OPTIONS="${NODE_OPTIONS:---max-old-space-size=6144}"

# frontend/node_modules is a named volume (see docker-compose.yml), and a fresh
# named volume is created root-owned while yarn here runs as `frappe` — without
# this the install dies on "EACCES: permission denied, mkdir". Non-recursive on
# purpose: the volume is empty on a first run, and on later runs its contents
# are already ours. Above the warm-start branch, which exec's straight out.
FRONTEND_MODULES="$BENCH_DIR/apps/lms/frontend/node_modules"
[ -d "$FRONTEND_MODULES" ] && sudo chown frappe:frappe "$FRONTEND_MODULES"

if [ -d "$BENCH_DIR/apps/frappe" ]; then
    echo ">>> Bench already exists, skipping init"
    cd "$BENCH_DIR"
    # exec, not a bare call: this branch used to fall through to `bench init`
    # once the server stopped, re-running the whole setup on every restart.
    exec bench start
fi

echo ">>> Creating a new bench around your local LMS clone..."

# Docker creates the parent directories of a nested bind mount itself, as root,
# so frappe-bench/ and frappe-bench/apps/ arrive root-owned and `bench init`
# dies with "Permission denied: /home/frappe/frappe-bench/sites". Chown just
# those two — NOT -R, which would recurse into your host repo.
sudo chown frappe:frappe "$BENCH_DIR" "$BENCH_DIR/apps"

# --ignore-exist: frappe-bench/ is already non-empty, because Docker created the
# apps/lms bind mount before this script ran.
#
# --skip-assets: `bench init` ends with a `bench build`, and bench discovers apps
# by listing apps/, where the mount has already put lms. It would try to build an
# app whose Python package is not installed yet and die on "ModuleNotFoundError:
# No module named 'lms'". Assets are built further down, once lms is a real
# editable install.
bench init \
    --ignore-exist \
    --skip-redis-config-generation \
    --skip-assets \
    "$BENCH_DIR"

cd "$BENCH_DIR"

# Use containers instead of localhost
bench set-mariadb-host mariadb
bench set-redis-cache-host redis://redis:6379
bench set-redis-queue-host redis://redis:6379
bench set-redis-socketio-host redis://redis:6379

# Remove redis, watch from Procfile
sed -i '/redis/d' ./Procfile
sed -i '/watch/d' ./Procfile

# Register the bind-mounted checkout as the `lms` app. This replaces
# `bench get-app lms`, which cloned upstream frappe/lms over the top of it.
# Before `bench get-app payments`, which builds assets and would otherwise hit
# the missing-module error described above.
echo ">>> Registering the bind-mounted local clone as the 'lms' app..."
./env/bin/pip install --no-cache-dir -e apps/lms
grep -qxF lms sites/apps.txt 2>/dev/null || echo lms >> sites/apps.txt

bench get-app payments

bench new-site "$SITE_NAME" \
--force \
--mariadb-root-password 123 \
--admin-password admin \
--no-mariadb-socket

bench --site "$SITE_NAME" install-app payments
bench --site "$SITE_NAME" install-app lms
bench --site "$SITE_NAME" set-config developer_mode 1
bench --site "$SITE_NAME" clear-cache
bench use "$SITE_NAME"
# resolve any Host header (localhost, 127.0.0.1, ...) to this site
bench set-config -g default_site "$SITE_NAME"

# The Vue SPA. `yarn build` also regenerates lms/public/css/jutsu-web.css, which
# themes Frappe's own server-rendered pages (login, sign-up).
echo ">>> Building the Vue frontend..."
cd "$BENCH_DIR/apps/lms/frontend"
yarn install
yarn build

cd "$BENCH_DIR"
# Full build, not --app lms: `bench init --skip-assets` above means frappe's own
# assets have never been built in this bench.
bench build

echo ">>> Ready. The app is at http://localhost:8000/lms/"
echo ">>> Site: $SITE_NAME (Administrator / admin)"
exec bench start
