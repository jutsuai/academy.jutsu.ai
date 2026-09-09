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
SITE=lms.localhost

if [ -d "$BENCH_DIR/apps/frappe" ]; then
    echo ">>> Bench already exists, skipping init."
    cd "$BENCH_DIR"
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
bench init --ignore-exist --skip-redis-config-generation --skip-assets "$BENCH_DIR"

cd "$BENCH_DIR"

# Point bench at the sibling containers rather than localhost.
bench set-mariadb-host mariadb
bench set-redis-cache-host redis://redis:6379
bench set-redis-queue-host redis://redis:6379
bench set-redis-socketio-host redis://redis:6379

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

bench get-app payments

bench new-site "$SITE" \
    --force \
    --mariadb-root-password 123 \
    --admin-password admin \
    --no-mariadb-socket

bench --site "$SITE" install-app payments
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

echo ">>> Ready. LMS at http://lms.localhost:8000 (Administrator / admin)"
exec bench start
