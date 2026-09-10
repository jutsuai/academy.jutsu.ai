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
