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
APP_DIR="$BENCH_DIR/apps/lms"

# Site name. Override via env (compose / Dokploy). Defaults to `localhost` so
# http://localhost:8000 works with no custom hostname.
SITE_NAME="${SITE_NAME:-localhost}"

# Credentials. The old hard-coded 123/admin were fine for a laptop and are not
# fine on a public VPS; compose passes these through so Dokploy can override.
DB_ROOT_PASSWORD="${DB_ROOT_PASSWORD:-123}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin}"

# Serving mode. developer_mode makes Frappe re-read sources per request and
# skips the built-asset fast paths, so a deployment wants it off.
DEVELOPER_MODE="${DEVELOPER_MODE:-0}"
# DEV_SERVER=1 keeps the Procfile's `bench serve` (Werkzeug's development WSGI
# server). 0 replaces it with gunicorn — see configure_procfile below.
DEV_SERVER="${DEV_SERVER:-0}"
GUNICORN_WORKERS="${GUNICORN_WORKERS:-2}"

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
FRONTEND_MODULES="$APP_DIR/frontend/node_modules"
[ -d "$FRONTEND_MODULES" ] && sudo chown frappe:frappe "$FRONTEND_MODULES"

# Make the bind-mounted checkout writable by the user we run as.
#
# The mount carries the host's ownership, and Dokploy clones the repo as root
# while everything in here runs as `frappe` (uid 1000) — so the whole tree
# arrives readable but not writable. That is not just a tidiness problem: vite
# bundles vite.config.js and writes the result *next to it* as
# vite.config.js.timestamp-*.mjs before it will build, so the build dies on
# "EACCES: permission denied, open .../vite.config.js.timestamp-...mjs" before
# bundling a single module. The build outputs land in the mount too
# (lms/public/frontend/, lms/www/_lms.html, lms/public/css/jutsu-web.css), as
# does the egg-info that `pip install -e` writes.
#
# node_modules and .git are both pruned. node_modules is a separate named volume,
# the line above already fixes its mount point, and walking it costs minutes.
# .git is left at the host's ownership on purpose: bench only ever reads it (git
# describe, for app versions), and chowning it would hand Dokploy's own root-owned
# clone back a tree git then refuses to touch. Marking it safe.directory gets the
# container's git past the "detected dubious ownership" refusal without changing
# anything on the host.
#
# The -w guard keeps the chown a no-op on Docker Desktop, where the mount is
# already writable by the container user and a recursive chown is pure latency.
ensure_app_writable() {
    git config --global --add safe.directory "$APP_DIR" 2>/dev/null || true
    if [ -w "$APP_DIR/frontend" ] && [ -w "$APP_DIR/lms/public" ] && [ -w "$APP_DIR" ]; then
        return 0
    fi
    echo ">>> Bind mount belongs to another uid; taking ownership of the checkout..."
    sudo find "$APP_DIR" \( -name node_modules -o -name .git \) -prune -o \
        -exec chown frappe:frappe {} +
}

# compose gates this container on both healthchecks, but `docker stack deploy`
# (Swarm) drops depends_on entirely, and that dropped gate is what used to kill
# this container: `bench new-site` hit a MariaDB still running its first-boot
# initialisation, failed, and `set -e` ended the script — and with it the
# container. Cheap enough to re-check here rather than rely on the orchestrator.
wait_for_tcp() {
    local host=$1 port=$2 label=$3 waited=0
    until (exec 3<>"/dev/tcp/$host/$port") 2>/dev/null; do
        [ "$waited" -ge 180 ] && { echo "FATAL: $label ($host:$port) never came up"; exit 1; }
        [ $((waited % 15)) -eq 0 ] && echo ">>> Waiting for $label at $host:$port..."
        sleep 3
        waited=$((waited + 3))
    done
    echo ">>> $label is up."
}

# Builds the Vue SPA into lms/public/frontend/ and writes lms/www/_lms.html.
# `yarn build` also regenerates lms/public/css/jutsu-web.css, which themes
# Frappe's own server-rendered pages (login, sign-up).
#
# Both of those paths are in .gitignore, so every Dokploy deploy clones a tree
# with neither in it. The build used to live in the cold-start branch only,
# which meant the first deploy built the SPA and every deploy after it served an
# app whose entry template and asset bundle no longer existed on disk.
build_frontend() {
    echo ">>> Building the Vue frontend (vite build, not a dev server)..."
    cd "$APP_DIR/frontend"
    yarn install
    yarn build
    cd "$BENCH_DIR"
}

# True when the build outputs the running site needs are missing.
frontend_assets_missing() {
    [ ! -f "$APP_DIR/lms/public/frontend/index.html" ] ||
        [ ! -f "$APP_DIR/lms/www/_lms.html" ]
}

# Creates the Frappe site and installs the apps into it.
#
# Called from the cold path and, on an existing bench, whenever sites/$SITE_NAME
# is absent. That second case is the one that used to crash-loop the container:
# change SITE_NAME in Dokploy (localhost -> academy.jutsu.ai, say) against a
# bench volume that already exists and every later `bench --site "$SITE_NAME"`
# failed on a site that was never created.
create_site() {
    cd "$BENCH_DIR"
    echo ">>> Creating site $SITE_NAME..."
    bench new-site "$SITE_NAME" \
        --force \
        --mariadb-root-password "$DB_ROOT_PASSWORD" \
        --admin-password "$ADMIN_PASSWORD" \
        --no-mariadb-socket

    bench --site "$SITE_NAME" install-app payments
    bench --site "$SITE_NAME" install-app lms
    bench use "$SITE_NAME"
    # resolve any Host header (localhost, 127.0.0.1, ...) to this site
    bench set-config -g default_site "$SITE_NAME"
}

# Swap the Procfile's web process. `bench serve` is Werkzeug's development
# server — single-threaded, reloading, and explicitly not for production — so
# unless DEV_SERVER=1 this points the web line at gunicorn instead, matching
# what `bench setup supervisor` generates for a production bench.
configure_procfile() {
    cd "$BENCH_DIR"
    # `bench start` needs this file and every branch below rewrites it in place,
    # so a missing one is an exit rather than a degraded start. Regenerate first.
    [ -f ./Procfile ] || bench setup procfile
    if [ "$DEV_SERVER" = "1" ]; then
        echo ">>> Web process: bench serve (development)"
        sed -i "s|^web:.*|web: bench serve --port 8000|" ./Procfile
    elif [ -x "$BENCH_DIR/env/bin/gunicorn" ]; then
        echo ">>> Web process: gunicorn, $GUNICORN_WORKERS workers"
        sed -i "s|^web:.*|web: sh -c 'cd sites \&\& exec ../env/bin/gunicorn -b 0.0.0.0:8000 -w $GUNICORN_WORKERS -t 120 --preload frappe.app:application'|" ./Procfile
    else
        # Never fail the boot over this: a served dev server beats no service.
        echo ">>> WARNING: gunicorn not found in env/bin, falling back to bench serve"
        sed -i "s|^web:.*|web: bench serve --port 8000|" ./Procfile
    fi
}

ensure_app_writable

wait_for_tcp mariadb 3306 MariaDB
wait_for_tcp redis 6379 Redis

if [ -d "$BENCH_DIR/apps/frappe" ]; then
    echo ">>> Bench already exists, skipping init"
    cd "$BENCH_DIR"
    NEEDS_FULL_ASSET_BUILD=0
else
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

    # `bench init --skip-assets` above means frappe's own assets have never been
    # built in this bench, so the first build has to cover every app, not just lms.
    NEEDS_FULL_ASSET_BUILD=1
fi

cd "$BENCH_DIR"
[ -d "$BENCH_DIR/sites/$SITE_NAME" ] || create_site

# Applied on every start, not just at init, so flipping the env var in Dokploy
# actually takes effect on redeploy.
#
# -p/--parse stores an int rather than a string, and that matters here: Frappe
# reads this as `if conf.developer_mode`, where the *string* "0" is truthy — so
# without --parse, DEVELOPER_MODE=0 would leave developer mode switched on.
# Guarded rather than asserted: a bench whose set-config lacks the flag should
# log and carry on, not crash-loop the container.
bench --site "$SITE_NAME" set-config -p developer_mode "$DEVELOPER_MODE" ||
    echo ">>> WARNING: could not set developer_mode=$DEVELOPER_MODE, leaving as-is"

if [ "$NEEDS_FULL_ASSET_BUILD" = "1" ] || frontend_assets_missing; then
    build_frontend
    if [ "$NEEDS_FULL_ASSET_BUILD" = "1" ]; then
        bench build
    else
        bench build --app lms
    fi
else
    echo ">>> Frontend build outputs already present, skipping vite build"
fi

bench --site "$SITE_NAME" clear-cache
configure_procfile

echo ">>> Ready. The app is at http://localhost:8000/lms/"
echo ">>> Site: $SITE_NAME (Administrator / \$ADMIN_PASSWORD)"
exec bench start
