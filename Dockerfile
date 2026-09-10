# Production image for the LMS.
#
# The difference from docker/docker-compose.dev.yml is WHEN the work happens.
# The dev stack builds the bench at container start, from a bind-mounted copy of
# your working tree, and then runs Werkzeug. Every deploy re-clones Frappe,
# re-installs Python deps and re-runs `yarn build` -- roughly fifteen minutes and
# several GB of RAM, inside the container, while the orchestrator waits. That is
# what times out on a PaaS.
#
# Here all of it happens once, at image build time, and the running containers
# start in seconds with nothing left to compile. The app is baked in rather than
# mounted, so a deploy is "pull the new image", not "clone and rebuild".
#
# Every runtime service -- web, websocket, worker, scheduler -- runs THIS image
# with a different command, which is the shape frappe_docker uses. nginx is the
# one exception; it runs the stock nginx:alpine and reads the shared sites
# volume.

ARG BENCH_IMAGE=frappe/bench:latest
FROM ${BENCH_IMAGE}

ARG FRAPPE_BRANCH=develop
ARG PAYMENTS_REPO=https://github.com/frappe/payments
ARG PAYMENTS_BRANCH=develop
# The SPA rolls pdfjs-dist, editorjs, prosemirror, plyr and face-api.js in one
# pass and OOMs at Node's default heap ("Ineffective mark-compacts near heap
# limit", exit 134). Lower it only if your build host cannot spare this, and
# expect the build to fail rather than degrade.
ARG NODE_MEMORY_MB=6144

ENV BENCH_DIR=/home/frappe/frappe-bench
ENV NODE_OPTIONS=--max-old-space-size=${NODE_MEMORY_MB}
ENV PATH="/home/frappe/frappe-bench/env/bin:${PATH}"
ENV PYTHONUNBUFFERED=1

USER frappe
WORKDIR /home/frappe

# nvm rather than the image's bare PATH: this image ships NODE_VERSION plus two
# nvm-managed versions, and none of them is on PATH for a non-login shell.
# Written to .bashrc-independent profile so every later RUN sees it.
SHELL ["/bin/bash", "-lc"]

# --skip-assets, because assets are built further down once lms is a real
# editable install -- `bench init`'s own build would try to build an app whose
# Python package does not exist yet and die on ModuleNotFoundError.
RUN . "$NVM_DIR/nvm.sh" \
    && nvm use "${NODE_VERSION:-24}" \
    && bench init \
        --skip-redis-config-generation \
        --skip-assets \
        --frappe-branch "${FRAPPE_BRANCH}" \
        "${BENCH_DIR}"

WORKDIR ${BENCH_DIR}

# payments before lms: lms's hooks import it, and `bench get-app` runs an install
# that would otherwise fail resolving the dependency.
RUN . "$NVM_DIR/nvm.sh" \
    && nvm use "${NODE_VERSION:-24}" \
    && bench get-app --skip-assets --branch "${PAYMENTS_BRANCH}" "${PAYMENTS_REPO}"

# The app itself. Copied, not cloned: the image must be built from the commit
# being deployed, not from whatever is on GitHub's default branch.
#
# --chown because COPY defaults to root and every later step runs as frappe.
COPY --chown=frappe:frappe . ${BENCH_DIR}/apps/lms

# Editable install so `import lms` resolves, plus the apps.txt line bench reads
# to discover the app. Both are what `bench get-app` would have done.
#
# Regenerated from the directory listing rather than appended to. `bench get-app
# payments` leaves sites/apps.txt without a trailing newline, so an `echo lms >>`
# lands on the same line and the file reads
#
#     frappe
#     paymentslms
#
# which every later bench command turns into `ModuleNotFoundError: No module
# named 'paymentslms'` -- including `bench build`, several steps later, where it
# looks like a problem with the build flags rather than with this line. Listing
# apps/ is also what frappe_docker's configurator does, and it cannot drift from
# what is actually installed.
RUN env/bin/pip install --no-cache-dir -e apps/lms
RUN ls -1 apps > sites/apps.txt && cat sites/apps.txt

# The SPA. `yarn build` also runs build-web-theme and copies the Jinja entry
# point to lms/www/_lms.html, so the server-rendered shell and the bundle stay
# in step.
RUN . "$NVM_DIR/nvm.sh" \
    && nvm use "${NODE_VERSION:-24}" \
    && cd apps/lms/frontend \
    && yarn install --frozen-lockfile \
    && yarn build \
    && yarn cache clean

# --apps with ONE comma-separated value, not a repeated --app. `--app` takes a
# single string (frappe/commands/utils.py: `if not apps and app: apps = app`),
# so click keeps only... worse, it concatenates: three --app flags arrive as
# "paymentslms" and the build dies on ModuleNotFoundError for an app of that
# name. Naming the apps also keeps esbuild from walking every app on the bench.
#
# --production forces minification. Without it the mode is inferred from
# developer_mode in the site config, and at image build time there is no site
# yet -- so it happens to be right, by accident, which is not a thing to rely on.
RUN . "$NVM_DIR/nvm.sh" \
    && nvm use "${NODE_VERSION:-24}" \
    && bench build --apps frappe,payments,lms --production

# Assets are built into sites/assets, and sites/ is a VOLUME at runtime -- the
# mount hides whatever the image put there. Keep a copy outside the mount point
# so the entrypoint can lay it back down on every start, which also means a new
# image's assets reach an existing volume instead of the stale ones persisting.
RUN cp -a "${BENCH_DIR}/sites/assets" /home/frappe/baked-assets

COPY --chown=frappe:frappe docker/entrypoint-prod.sh /home/frappe/entrypoint-prod.sh
RUN chmod +x /home/frappe/entrypoint-prod.sh

EXPOSE 8000 9000
ENTRYPOINT ["/home/frappe/entrypoint-prod.sh"]
CMD ["gunicorn"]
