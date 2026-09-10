## Local source development with PostgreSQL

Copy the environment template once after cloning the repository:

```
cp .env.example .env
```

Edit `.env` when you want to change the site, credentials, branches, images, or
host ports. The real `.env` is ignored by Git.

Start the whole stack -- Postgres, Redis, the Frappe backend and the frontend dev
server -- from the repository root:

```
docker compose -f docker/docker-compose.dev.yml up
```

Nothing needs to be installed or started on your machine; there is no separate
`yarn install` or `yarn dev` to run.

Three ports:

| | | |
|---|---|---|
| `http://localhost:8080` | vite, with **hot reload** | use this while developing |
| `http://localhost:8000` | the prebuilt bundle, plus `/login` and `/app` (the desk) | |
| `http://localhost:8025` | every email the site sends | see below |

The default local login is `Administrator` / `admin`.

### Email

Two flows are unusable without a working mail server: **Login with Email Link**
and the verification message on **sign-up**. Frappe does not fail loudly when
outgoing mail is unconfigured — it takes a quiet fallback branch, so the page
reports success and no mail is sent. Sign-up in particular still creates the
account, then says "Please ask your administrator to verify your sign-up"
rather than "Please check your email", which reads as a broken form.

The `mailpit` container catches all of it. Open **http://localhost:8025** and
the message is there, links live. Nothing is relayed anywhere: no upstream
server is configured, no credentials exist, and a message addressed to a real
person is held in the same local inbox as everything else. The inbox lives in
memory, so `down` empties it.

The site points at it through `site_config` (`mail_server`, `mail_port`), set by
`init-dev.sh` on every start, so there is no Email Account record to create.

#### Sending for real (SendGrid)

Put a key in `.env` and mail goes out through SendGrid instead:

```
SENDGRID_API_KEY=SG.xxxxxxxx
FROM_EMAIL=you@yourdomain.com
```

Then restart: `docker compose -f docker/docker-compose.dev.yml up -d frappe`.
It prints which one it chose on boot — `>>> Outgoing mail: SendGrid, as …` or
`>>> Outgoing mail: mailpit, …`. Clearing `SENDGRID_API_KEY` and restarting
switches back and wipes the stored key.

Two things to know before the first send:

- The username SendGrid's relay expects is the literal string `apikey`, not
  your key and not your email. `init-dev.sh` sets that for you.
- `FROM_EMAIL` must be a **verified sender** or on an authenticated domain in
  your SendGrid account. An unverified one is rejected with a 403 whose message
  does not say so.

The key is written into `sites/<site>/site_config.json` in plain text. That file
lives in the `bench` docker volume rather than your checkout, so it will not be
committed, but `docker compose down -v` is what actually removes it.

Any other relay works the same way: leave `SENDGRID_API_KEY` empty and point
`MAIL_SERVER` / `MAIL_PORT` at it. An Email Account created in the desk takes
precedence over all of these.

The app owns the site root: `/`, `/courses`, `/batches` — there is no `/lms`
prefix. Frappe's own pages are untouched beside it (`/login`, `/app` for the
desk, `/api`). Set `LMS_PATH=lms` in `.env` to put the prefix back.

Edit any file under `frontend/src` and the browser updates on save -- the vite
container watches your checkout through the bind mount. Python edits reload the
backend by themselves too; changes to DocType JSON still need a
`bench --site localhost migrate`.

The first `up` takes around fifteen minutes: it creates the bench, installs the
apps, and builds the frontend. Later ones take seconds. The bench now lives in a
named volume rather than the container, so `down` keeps it -- only `down -v`
starts over:

```
docker compose -f docker/docker-compose.dev.yml down -v --remove-orphans
docker compose -f docker/docker-compose.dev.yml up
```

### Running the tests

In the container, where the dependencies actually live:

```
docker compose -f docker/docker-compose.dev.yml exec frontend \
  bash -lc 'cd apps/lms/frontend && yarn test'
```

`frontend/node_modules` belongs to the containers now -- it is a named volume,
separate from anything in your checkout. Two reasons. Native binaries like
rollup and esbuild are compiled per platform, so a `yarn install` on macOS and
one inside the Linux container overwrite each other's and only the last one
works. And `@framework/ui` is a symlink into the bench (`apps/frappe/ui`), which
exists only inside the container -- one suite, `ravenSettings`, fails to resolve
it anywhere else.

## Deploying to production

`docker/docker-compose.dev.yml` is **not** deployable, and the failure is not
subtle: it builds the entire bench at container start from a bind-mounted
working tree — clone Frappe, compile the Python deps, `yarn install`,
`yarn build` — then serves the result with Werkzeug in developer mode. Fifteen
minutes of work on every deploy, several GB of RAM to do it, and a debug server
on the public internet at the end. A PaaS gives up waiting long before it
finishes.

Use `docker/docker-compose.prod.yml` instead. It runs one image, built by
`Dockerfile` at the repo root, six ways:

| service | what it runs |
|---|---|
| `configurator` | one-shot: writes `common_site_config.json`, creates the site on a first deploy, `bench migrate` on every later one, then exits |
| `backend` | gunicorn, `frappe.app:application` |
| `websocket` | `apps/frappe/socketio.js` |
| `worker` | `bench worker`, all three queues |
| `scheduler` | `bench schedule` |
| `nginx` | stock `nginx:alpine`, serving `/assets` and `/files` off the shared volume and proxying the rest |

Everything except `configurator` waits for it to exit successfully, so nothing
serves traffic against an unmigrated schema and no two services race to migrate.

### Dokploy

1. Create a **Compose** application pointed at this repository.
2. Set the compose path to `docker/docker-compose.prod.yml`.
3. Paste `.env.prod.example` into the Environment tab and fill in the four
   required values: `SITE_NAME`, `POSTGRES_PASSWORD`, `ADMIN_PASSWORD`, and one
   of `SENDGRID_API_KEY` / `MAIL_SERVER`. Compose refuses to start without the
   first three rather than quietly creating a site with a guessable password.
4. Attach your domain to the **`nginx`** service, port **8080**.
5. Deploy.

The first deploy builds the image, which takes roughly fifteen minutes and wants
about 8 GB of RAM — `yarn build` alone runs Node with a 6 GB heap. **If your
build host has less, the build fails rather than degrades**; that is the single
most likely cause of a failed first deploy. Later deploys reuse the layer cache
and only rebuild from the `COPY` of your source onward.

Containers then start in seconds, because nothing is left to compile.

### Things worth knowing

**`SITE_NAME` is internal, not your domain.** nginx sends it as
`X-Frappe-Site-Name` on every proxied request, so the site keeps working
whatever hostname the router puts in `Host`. Changing it later means creating a
new site, so pick one and keep it.

**Assets live in the image, state lives in the volume.** The `sites` volume
holds `site_config.json` and uploads; it is mounted over `sites/`, which hides
the assets the image built there. The entrypoint copies them back on every
start — unconditionally, because on a redeploy the volume already holds the
*previous* image's assets and an "only if missing" check would serve those
forever while the Python moved on.

**Postgres, not MariaDB.** This matches the dev stack, at the cost Frappe
documents: it calls Postgres support beta. Two Postgres-only `GROUP BY` bugs in
this app have already been found and fixed (`get_certified_participants`,
`get_lesson_completion_stats`); MariaDB tolerated both because Frappe runs it
without `ONLY_FULL_GROUP_BY`. Expect to meet more of them, and reach for
`docker compose ... logs backend` when a page renders empty rather than erroring.

**Back up the volumes.** `postgres-data` and `sites` are the deployment. The
rest is reproducible from this repository.

```bash
docker compose -f docker/docker-compose.prod.yml exec backend \
  bench --site "$SITE_NAME" backup --with-files
```

**Redis queue durability.** `redis-queue` has a volume because it holds jobs
that have been accepted but not yet run; `redis-cache` deliberately does not.

## Upstream disposable Docker setup

**Step 1:** Clone the repo

```
$ git clone https://github.com/frappe/lms.git

$ cd lms

$ cd docker
```

**Step 2:** Run docker-compose

```
$ docker-compose up
```

**Step 3:** Visit the website at http://localhost:8000/

You'll have to go through the setup wizard to setup the website for the first time you access it. Login using the following credentials to complete the setup wizard.

```
Username: Administrator
password: admin
```

These credentials are intended for local development only. Change the administrator password before using the site outside a local test environment.

## Loading demo data

The LMS app creates demo data when the setup wizard completes. If you need to recreate the demo course after clearing it, run the following command from another terminal while the Docker services are running:

```
$ docker-compose exec frappe bash -lc "cd frappe-bench && bench --site lms.localhost execute lms.demo.demo_data.create_demo_data"
```

This creates the sample course, instructor, learners, lessons, quizzes, and progress records used for local evaluation. To remove the demo course later, open the user menu in the LMS interface and choose **Clear Demo Data**.

## Stopping the server

Press `ctrl+c` in the terminal to stop the server. You can also run `docker-compose down` in another terminal to stop it.

To completely reset the instance, do the following:

```
$ docker-compose down --volumes
$ docker-compose up
```
