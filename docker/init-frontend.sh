#!/bin/bash
# Starts the vite dev server, in its own container beside the bench.
#
# docker-compose.dev.yml gates this behind the frappe service's healthcheck, so
# by the time it runs, init-dev.sh has already done `yarn install` and created the
# @framework/ui link. Nothing is installed here: the two services share one
# node_modules volume, and a second `yarn install` racing the first is how you get
# a half-written dependency tree.
#
# vite's own settings come from frontend/vite.config.js and are deliberately not
# repeated here -- it binds 0.0.0.0, takes port 8080 from frappe-ui's proxy plugin,
# and that plugin points API calls at 127.0.0.1:8000, which resolves to the bench
# because this container shares the frappe container's network namespace.

set -eo pipefail

# Not a login shell, so node is not on PATH yet. Same nvm bootstrap as init-dev.sh:
# the image ships NODE_VERSION plus two nvm-managed versions and no usable default.
export NVM_DIR="${NVM_DIR:-/home/frappe/.nvm}"
# shellcheck source=/dev/null
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use "${NODE_VERSION:-24}" >/dev/null 2>&1 || nvm use default >/dev/null 2>&1 || true

command -v node >/dev/null || { echo "FATAL: node is not on PATH"; exit 1; }
command -v yarn >/dev/null || { echo "FATAL: yarn is not on PATH"; exit 1; }

FRONTEND_DIR=/home/frappe/frappe-bench/apps/lms/frontend
cd "$FRONTEND_DIR"

# The healthcheck says the bench is serving, which implies install finished. Say so
# plainly if it somehow did not, rather than letting vite fail on a missing import.
if [ ! -x node_modules/.bin/vite ]; then
    echo "FATAL: node_modules is not installed in the shared volume."
    echo "       The frappe service installs it; check its logs, then:"
    echo "         docker compose -f docker/docker-compose.dev.yml down -v"
    exit 1
fi

# vite.config.js hard-fails on a dangling link, with a message that names neither
# the link nor the fix. init-dev.sh creates it; re-assert it here so a bench that
# was built before this file existed still starts.
mkdir -p node_modules/@framework
if [ ! -d node_modules/@framework/ui ]; then
    ln -sfn /home/frappe/frappe-bench/apps/frappe/ui node_modules/@framework/ui
fi

echo ">>> vite starting on http://localhost:8080 (hot reload; edit and save)"
exec yarn dev
