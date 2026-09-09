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

set -euo pipefail

export PATH="${NVM_DIR}/versions/node/v${NODE_VERSION_DEVELOP}/bin/:${PATH}"

BENCH_DIR=/home/frappe/frappe-bench
SITE=lms.localhost

if [ -d "$BENCH_DIR/apps/frappe" ]; then
    echo ">>> Bench already exists, skipping init."
    cd "$BENCH_DIR"
    exec bench start
fi

echo ">>> Creating a new bench around your local LMS clone..."

# --ignore-exist: frappe-bench/ is already non-empty, because the apps/lms bind mount
# is created by Docker before this script runs.
bench init --ignore-exist --skip-redis-config-generation "$BENCH_DIR"

cd "$BENCH_DIR"

# Point bench at the sibling containers rather than localhost.
bench set-mariadb-host mariadb
bench set-redis-cache-host redis://redis:6379
bench set-redis-queue-host redis://redis:6379
bench set-redis-socketio-host redis://redis:6379

# Those services run as their own containers, and `watch` is replaced by vite.
sed -i '/redis/d' ./Procfile
sed -i '/watch/d' ./Procfile

bench get-app payments

echo ">>> Registering the bind-mounted local clone as the 'lms' app..."
./env/bin/pip install --no-cache-dir -e apps/lms
grep -qxF lms sites/apps.txt 2>/dev/null || echo lms >> sites/apps.txt

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
bench build --app lms

echo ">>> Ready. LMS at http://lms.localhost:8000 (Administrator / admin)"
exec bench start
