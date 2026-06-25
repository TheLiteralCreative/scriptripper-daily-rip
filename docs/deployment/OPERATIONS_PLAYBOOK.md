# Operations Playbook

What to do when ScriptRipper is deployed and something needs checking or fixing.
Distilled from the archive's `render-oversight.md` (an early attempt at a Render
operations skill) and the pre-deploy validation script, corrected for the
single-service architecture.

This is a reference, not a procedure — jump to the section you need.

---

## Reading service health

In the Render dashboard, a service shows one of:

| Indicator | Meaning |
|-----------|---------|
| Deployed / Available | Healthy and serving |
| Building / Deploying | A deploy is in progress — wait |
| Failed deploy | Build or startup broke — check Logs |
| Suspended | Free-tier limit hit, or manually suspended |

A free-tier service also **sleeps after inactivity**. The first request after a sleep
takes a few seconds while it wakes — that is normal, not a fault.

---

## Reading the logs

Service → **Logs** tab — real-time stream. Patterns worth recognizing:

**Healthy startup:**
```
Application startup complete
Uvicorn running on http://0.0.0.0:8000
```

**Things that mean trouble:**
```
ModuleNotFoundError: No module named 'X'
   → a package is missing from requirements.txt

could not connect to server  /  password authentication failed
   → DATABASE_URL is wrong, or Neon is unreachable

redis.exceptions.ConnectionError
   → REDIS_URL is wrong, or Upstash is unreachable

CORS error  (seen in the browser console, not the server log)
   → the frontend's domain isn't in CORS_ORIGINS
```

---

## Common problems and fixes

### The service won't start

Read the **Logs** tab and find the *first* error — later errors are usually
consequences. Most failures are one of:

- **Missing dependency** — `ModuleNotFoundError`. Add the package to `requirements.txt`,
  commit, push. The push triggers a rebuild.
- **Missing environment variable** — the app crashes reading config. Add the variable in
  the Environment tab (it redeploys on save). Cross-check against the `/env-setup`
  registry.
- **Bad connection string** — `DATABASE_URL` / `REDIS_URL` malformed or pointing at a
  paused Neon/Upstash instance. Verify the string and that the external service is awake.

### CORS errors from the frontend

The browser console shows a CORS error when the frontend's domain isn't allowed.
Fix: add every frontend URL (including preview/staging URLs) to the `CORS_ORIGINS` env var
on the `scriptripper` service. Save — it redeploys automatically. The `RENDER_API_KEY`
trick in `RENDER_DEPLOYMENT.md` (Step "useful") does this from the command line.

### Database connection failures

1. Confirm `DATABASE_URL` is the current Neon string and includes `?sslmode=require`.
2. Check the Neon dashboard — a free-tier Neon project can pause when idle; the first
   connection wakes it.
3. Use the Shell tab (below) to test the connection directly.

### A deploy succeeded but behavior is stale

A code change needs a deploy; an env-var change needs a redeploy. If you changed an env
var, confirm the redeploy actually ran (Events tab). To force a clean rebuild without a
code change: **Manual Deploy** button, top-right of the service page.

---

## Shell access — the most useful tool

Service → **Shell** tab. It opens a terminal *inside the running container*, with every
environment variable present. Connect takes ~10 seconds; you land in `/app`.

Use it for:

```bash
# Apply database migrations (the manual step from RENDER_DEPLOYMENT.md)
alembic upgrade head

# Confirm the app can see the database
python -c "from app.database import engine; print('DB import OK')"

# Inspect what env vars are actually set
env | grep -E "DATABASE|REDIS|R2|GROQ|STRIPE"

# Look around
ls -la /app
```

This is also where you'd run a one-off fix — e.g. manually upgrading a user who paid but
wasn't auto-upgraded (see `STRIPE_BILLING.md`).

---

## Rollback

Render has no one-click rollback. To revert: in git, check out or revert to the last good
commit and push it to `main`. Auto-deploy picks it up and deploys the older code. This is
why small, frequent commits matter — they make "the last good commit" easy to find.

---

## Managing Render from the command line (optional)

With a Render API key (`dashboard.render.com/u/settings/api-keys`) you can script common
operations instead of clicking:

```bash
export RENDER_API_KEY=rnd_xxxxx

# List all services (find the srv-... ID)
curl -H "Authorization: Bearer $RENDER_API_KEY" \
  https://api.render.com/v1/services

# Update one env var (triggers a redeploy)
curl -X PUT \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  https://api.render.com/v1/services/<srv-ID>/env-vars/<KEY> \
  -d '{"value": "new_value"}'

# Trigger a manual deploy
curl -X POST \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  https://api.render.com/v1/services/<srv-ID>/deploys
```

The `<srv-ID>` is in the service's dashboard URL. For day-to-day work the dashboard is
fine — the API matters when you want a repeatable script (which is exactly what the Kit
will want later).

---

## Pre-deploy sanity check

The archive shipped a `pre_deploy_check.sh` that validated the repo before deploying.
Most of its checks assumed the old three-service layout, but the *idea* is sound. The
checks still worth running before any deploy, adapted to one service:

- `Dockerfile` exists at the repo root and has a `FROM` and a `CMD`.
- `requirements.txt` exists and includes the critical packages: `fastapi`, `uvicorn`,
  `sqlalchemy`, `alembic`, `groq`, `boto3`, `stripe`.
- `app/main.py` imports without a syntax error: `python -m py_compile app/main.py`.
- A health/readiness route exists in `app/main.py`.
- Working tree is committed and pushed — Render deploys what's on GitHub, not what's on
  your laptop.
- `.env` is gitignored (it is — confirmed in `.gitignore`) and contains no secrets bound
  for a tracked file.

A short check like this catches the boring failures (uncommitted code, a missing
package) before they cost a five-minute build cycle to discover.
