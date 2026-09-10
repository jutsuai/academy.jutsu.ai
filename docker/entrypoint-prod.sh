#!/bin/bash
# One entrypoint for every Frappe service in docker-compose.prod.yml.
#
# The compose file runs the SAME image six ways -- configurator, gunicorn,
# websocket, worker, scheduler -- and the first argument picks which. Everything
# they share (waiting on Postgres and Redis, laying the baked assets back over
# the volume) happens here once rather than being repeated per service.
#
# Deliberately NOT here: creating the site and running migrations. Those are the
# configurator's job alone, because six services racing to run `bench migrate`
# against one database is how you get a half-applied schema.

set -eo pipefail

BENCH_DIR=/home/frappe/frappe-bench
cd "$BENCH_DIR"

SITE="${SITE_NAME:?SITE_NAME is required}"
DB_HOST="${DB_HOST:-postgres}"
DB_PORT="${DB_PORT:-5432}"
REDIS_CACHE="${REDIS_CACHE:-redis-cache:6379}"
REDIS_QUEUE="${REDIS_QUEUE:-redis-queue:6379}"
SOCKETIO_PORT="${SOCKETIO_PORT:-9000}"

log() { echo ">>> [$(date -u +%H:%M:%S)] $*"; }

wait_for() {
    local host=$1 port=$2 label=$3 tries=${4:-60}
    log "waiting for $label ($host:$port)"
    for _ in $(seq 1 "$tries"); do
        if (echo > "/dev/tcp/$host/$port") >/dev/null 2>&1; then
            log "$label is up"
            return 0
        fi
        sleep 2
    done
    log "FATAL: $label never came up"
    return 1
}

# The sites volume is mounted over sites/, which hides the assets the image
# built into sites/assets. Copy them back on every start rather than only when
# missing: on a redeploy the volume already holds the PREVIOUS image's assets,
# and a "only if absent" check would serve those forever while the Python code
# moved on. Cheap enough -- it is a local copy of a few tens of MB.
restore_assets() {
    if [ -d /home/frappe/baked-assets ]; then
        mkdir -p "$BENCH_DIR/sites/assets"
        cp -a /home/frappe/baked-assets/. "$BENCH_DIR/sites/assets/"
        log "assets restored from the image"
    fi
}

# common_site_config.json lives in the volume, so it survives redeploys and has
# to be rewritten each time in case a host or port changed. `bench set-config -g`
# is the supported way to touch it; editing the JSON by hand loses bench's own
# type handling.
write_common_config() {
    bench set-config -g db_host "$DB_HOST"
    bench set-config -gp db_port "$DB_PORT"
    bench set-config -g redis_cache "redis://$REDIS_CACHE"
    bench set-config -g redis_queue "redis://$REDIS_QUEUE"
    bench set-config -g redis_socketio "redis://$REDIS_QUEUE"
    bench set-config -gp socketio_port "$SOCKETIO_PORT"
    # Off, explicitly. developer_mode rebuilds DocType files on the fly and
    # leaks tracebacks to the browser; the dev stack turns it on and this is the
    # one place that difference actually matters.
    bench set-config -gp developer_mode 0
    bench set-config -gp maintenance_mode 0
    ls -1 apps > sites/apps.txt
}

# Same shape as init-dev.sh's set_mail: SendGrid when a key is present,
# otherwise whatever SMTP host is configured. Written per-site rather than
# globally so a second site on this bench can differ.
write_mail_config() {
    bench --site "$SITE" set-config auto_email_id "${FROM_EMAIL:-no-reply@$SITE}"
    bench --site "$SITE" set-config email_sender_name "${MAIL_SENDER_NAME:-Jutsu Academy}"

    if [ -n "${SENDGRID_API_KEY:-}" ]; then
        log "outgoing mail: SendGrid, as ${FROM_EMAIL:-no-reply@$SITE}"
        # SendGrid's relay wants the literal string `apikey` as the username and
        # the key as the password. FROM_EMAIL must be a verified sender or on an
        # authenticated domain, or every send comes back 403.
        bench --site "$SITE" set-config mail_server "${SENDGRID_HOST:-smtp.sendgrid.net}"
        bench --site "$SITE" set-config -p mail_port "${SENDGRID_PORT:-587}"
        bench --site "$SITE" set-config -p use_tls 1
        bench --site "$SITE" set-config -p disable_mail_smtp_authentication 0
        bench --site "$SITE" set-config mail_login apikey
        bench --site "$SITE" set-config mail_password "$SENDGRID_API_KEY"
    elif [ -n "${MAIL_SERVER:-}" ]; then
        log "outgoing mail: ${MAIL_SERVER}"
        bench --site "$SITE" set-config mail_server "$MAIL_SERVER"
        bench --site "$SITE" set-config -p mail_port "${MAIL_PORT:-587}"
        bench --site "$SITE" set-config -p use_tls "${MAIL_USE_TLS:-1}"
        bench --site "$SITE" set-config mail_login "${MAIL_LOGIN:-}"
        bench --site "$SITE" set-config mail_password "${MAIL_PASSWORD:-}"
    else
        # Loud, because this is the state where sign-up and "Login with Email
        # Link" both silently do nothing: Frappe takes a quiet fallback branch
        # and the page still reports success.
        log "WARNING: no outgoing mail configured. Sign-up verification and"
        log "WARNING: email-link login will report success and send nothing."
    fi
}

create_or_migrate_site() {
    if [ -f "sites/$SITE/site_config.json" ]; then
        log "site $SITE exists; migrating"
        bench --site "$SITE" migrate
    else
        log "creating site $SITE"
        bench new-site "$SITE" \
            --db-type postgres \
            --db-host "$DB_HOST" \
            --db-port "$DB_PORT" \
            --db-root-username "${DB_ROOT_USER:?DB_ROOT_USER is required}" \
            --db-root-password "${DB_ROOT_PASSWORD:?DB_ROOT_PASSWORD is required}" \
            --admin-password "${ADMIN_PASSWORD:?ADMIN_PASSWORD is required}" \
            --install-app payments \
            --install-app lms \
            --set-default
    fi

    write_mail_config
    bench --site "$SITE" set-config lms_path "${LMS_PATH-}"
    bench --site "$SITE" clear-cache
}

wait_for "$DB_HOST" "$DB_PORT" postgres
wait_for "${REDIS_CACHE%%:*}" "${REDIS_CACHE##*:}" redis-cache
wait_for "${REDIS_QUEUE%%:*}" "${REDIS_QUEUE##*:}" redis-queue
restore_assets

case "$1" in
    configurator)
        # The only service that writes schema. Everything else waits on it
        # finishing (service_completed_successfully in the compose file).
        write_common_config
        create_or_migrate_site
        log "configuration complete"
        ;;

    gunicorn)
        # (2 x cores) + 1 is Gunicorn's own guidance; threads help because
        # Frappe requests are mostly waiting on Postgres, not on CPU.
        exec env/bin/gunicorn \
            --chdir="$BENCH_DIR/sites" \
            --bind=0.0.0.0:8000 \
            --threads="${GUNICORN_THREADS:-4}" \
            --workers="${GUNICORN_WORKERS:-2}" \
            --worker-class=gthread \
            --worker-tmp-dir=/dev/shm \
            --timeout="${GUNICORN_TIMEOUT:-120}" \
            --preload \
            --access-logfile=- \
            frappe.app:application
        ;;

    websocket)
        exec node "$BENCH_DIR/apps/frappe/socketio.js"
        ;;

    worker)
        exec bench worker --queue "${WORKER_QUEUES:-short,default,long}"
        ;;

    scheduler)
        exec bench schedule
        ;;

    *)
        exec "$@"
        ;;
esac
