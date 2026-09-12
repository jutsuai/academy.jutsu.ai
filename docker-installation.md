**Step 1:** Clone the repo

```
$ git clone https://github.com/frappe/lms.git

$ cd lms

$ cd docker
```

**Step 2:** Create the shared network, once per machine

The compose file attaches the app to `dokploy-network` so Dokploy's Traefik can
route to it in production. Dokploy creates that network on its own servers; on a
laptop you create it yourself, once:

```
$ docker network create dokploy-network
```

**Step 3:** Run docker-compose

```
$ docker-compose up
```

The first run builds the Vue SPA with `vite build` and can take several minutes
before port 8000 answers. Vite is a build step here, not a server: it writes
`lms/public/frontend/`, which Frappe then serves at `/assets/lms/frontend/`.
There is no `vite dev` or `vite preview` process in this stack.

**Step 4:** Visit the website at http://localhost:8000/

You'll have to go through the setup wizard to setup the website for the first time you access it. Login using the following credentials to complete the setup wizard.

```
Username: Administrator
password: admin
```

These credentials are intended for local development only. Change the administrator password before using the site outside a local test environment.

## Loading demo data

The LMS app creates demo data when the setup wizard completes. If you need to recreate the demo course after clearing it, run the following command from another terminal while the Docker services are running:

```
$ docker-compose exec frappe bash -lc "cd frappe-bench && bench --site localhost execute lms.demo.demo_data.create_demo_data"
```

This creates the sample course, instructor, learners, lessons, quizzes, and progress records used for local evaluation. To remove the demo course later, open the user menu in the LMS interface and choose **Clear Demo Data**.

## Stopping the server

Press `ctrl+c` in the terminal to stop the server. You can also run `docker-compose down` in another terminal to stop it.

To completely reset the instance, do the following:

```
$ docker-compose down --volumes
$ docker-compose up
```


## Configuration

All of these are optional locally and settable from Dokploy's **Environment**
tab in a deployment.

| Variable | Default | What it does |
| --- | --- | --- |
| `SITE_NAME` | `localhost` | Frappe site name. Set it to the domain you serve from. Changing it on an existing deployment creates the new site rather than failing. |
| `DB_ROOT_PASSWORD` | `123` | MariaDB root password. **Change this before exposing the stack.** |
| `ADMIN_PASSWORD` | `admin` | Password for the `Administrator` user. **Change this too.** |
| `DEVELOPER_MODE` | `0` | Frappe's developer mode. Leave at `0` for a deployment. |
| `DEV_SERVER` | `0` | `0` runs gunicorn. `1` runs `bench serve`, Werkzeug's development server. |
| `GUNICORN_WORKERS` | `2` | Web workers. Roughly `2 x CPU + 1`, bounded by RAM. |
| `NODE_OPTIONS` | `--max-old-space-size=6144` | Heap for the SPA build. Lower it on a small host; if the build dies at exit 137 the kernel OOM-killed it. |

## Deploying on Dokploy

Create a **Compose** service pointing at this repo with compose path
`./docker/docker-compose.yml`, then:

1. Set `SITE_NAME`, `DB_ROOT_PASSWORD` and `ADMIN_PASSWORD` under **Environment**.
2. Add your domain under **Domains**, targeting service `frappe` on port `8000`.
3. Deploy, and watch the `frappe` logs — the first deploy runs `bench init`, creates
   the site and builds the SPA, so expect several quiet minutes.

The container publishes 8000 and 9000 on `127.0.0.1` only; Traefik reaches it over
`dokploy-network`. To poke at it directly, tunnel in with
`ssh -L 8000:localhost:8000 <host>`.

### Why a redeploy rebuilds the frontend

`lms/public/frontend/` and `lms/www/_lms.html` are both in `.gitignore`, so every
Dokploy deploy clones a tree without them. `docker/init.sh` checks for those two
paths on every start and reruns `yarn build` when they are missing, which on a
redeploy is always. A plain container restart, where the files are still on disk,
skips the build and starts in seconds.
