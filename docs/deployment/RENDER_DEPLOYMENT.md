# Deploying ScriptRipper to Render

Distilled from the pre-pivot Render guides (`RENDER_DEPLOYMENT_GUIDE.md`,
`DEPLOY_TO_RENDER.md`, `START_HERE_RENDER.md`) and rewritten for the current
single-service architecture. Read `README.md` in this folder first if you haven't.

---

## Target architecture

ScriptRipper deploys as **one Render Web Service** running the FastAPI app. Everything
else it depends on lives *outside* Render:

```
        ┌──────────────────────────────┐
        │   Render Web Service         │
        │   scriptripper  (Docker)     │
        │   FastAPI + BackgroundTasks  │
        └──────────────┬───────────────┘
                        │  (connection strings in env vars)
        ┌───────────────┼────────────────┬───────────────┐
        ▼               ▼                ▼               ▼
     Neon            Upstash          Cloudflare       Resend
   PostgreSQL         Redis              R2            (email)
```

The old setup had Render host the database, Redis, and a separate worker. It no longer
does. Render runs the app; Neon/Upstash/R2/Resend are managed separately and reached over
the network. You do **not** create a database or Redis instance inside Render.

---

## Before you start

You need these accounts and keys ready. The full walkthrough for generating each one is
in `docs/ScriptRipper_Daily-Rip(pivot)/Daily Rip Credential Setup Guide.md`. The
`/env-setup` command checks them.

- A GitHub repo with the ScriptRipper code pushed to `main`
- Neon connection string (`DATABASE_URL`)
- Upstash connection string (`REDIS_URL`)
- Groq API key (`GROQ_API_KEY`)
- Cloudflare R2 keys (`R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_ENDPOINT_URL`, `R2_BUCKET_NAME`)
- Resend API key (`RESEND_API_KEY`) and a verified `FROM_EMAIL`
- A `CRON_SECRET_KEY` — generate with `openssl rand -hex 32`
- Stripe keys — see `STRIPE_BILLING.md`

---

## Step 1 — Add a Dockerfile

The repo does not have a `Dockerfile` yet. Render can build a Python app without one, but
Docker gives you a predictable, reproducible build — and ScriptRipper has a hard
non-Python requirement: **`ffmpeg`**, used to chunk audio before sending it to Groq
Whisper (Whisper has a 25 MB upload limit). A plain Python build would not include it.

Below is the salvaged Dockerfile pattern, corrected for the current layout (`app/`,
`requirements.txt`, and `alembic/` all live at the repo root — there is no `api/`
subfolder anymore):

```dockerfile
# Dockerfile  — ScriptRipper single-service build
FROM python:3.11-slim

WORKDIR /app

# System dependencies:
#   ffmpeg            — chunk audio for Groq Whisper (25 MB limit)
#   gcc, libpq-dev    — build psycopg2 (Postgres driver)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first so this layer caches between code changes
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

# Run as a non-root user — good hygiene, carried over from the old build
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Render sets $PORT; bind to it. Default to 8000 for local runs.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

Two things carried over from the old Dockerfile *on purpose* because they were good
practice: the non-root `appuser`, and installing `requirements.txt` in its own layer
before copying code (so editing code doesn't trigger a full dependency reinstall).

> **Migrations:** the old Dockerfile ran a `start.sh` that applied Alembic migrations on
> boot. Per the project rule "do not apply Alembic migrations without explicit user
> confirmation," keep migrations a **manual step** (Step 5) rather than baking them into
> container startup.

---

## Step 2 — `render.yaml` (optional but recommended)

A `render.yaml` "Blueprint" lets Render create the service from the file instead of
clicking through the UI. The archive's `render.yaml` is kept as a structural reference
only — it defines three Docker services plus a Render database, which is the old shape.

A current-architecture Blueprint is a *single* `web` service and *no* `databases:` block
(Neon and Upstash are external). The key Blueprint mechanics worth knowing:

- `sync: false` on an env var means "I will set this manually in the dashboard" — use it
  for every secret (API keys, connection strings, `CRON_SECRET_KEY`).
- Plain `value:` env vars are safe to commit — use them for non-secrets like
  `ENVIRONMENT=production`.

Writing the actual `render.yaml` is best done during the build phase, once the health
check route is confirmed. You can also skip it entirely and use the dashboard (Step 3).

---

## Step 3 — Create the service in the Render dashboard

Browser-only, no CLI needed. At **https://dashboard.render.com**:

1. **New + → Web Service**, connect the ScriptRipper GitHub repo.
2. Name it `scriptripper`.
3. Runtime: **Docker** (Render auto-detects the `Dockerfile`).
4. Branch: `main`. Leave auto-deploy on so pushes to `main` redeploy.
5. Region: pick one and remember it — there is no infra to co-locate now, but keeping a
   consistent region keeps latency to Neon/Upstash predictable if you chose nearby
   regions for those.
6. Plan: **Free** to start. (Cost note at the bottom.)
7. Health check path: set it to the app's readiness route — the old service used
   `/ready`. Confirm the exact route in `app/main.py` before relying on it.

---

## Step 4 — Set environment variables

In the service's **Environment** tab, add every variable from the `/env-setup` registry.
The salvaged `.env.render.example` is the ancestor of this list, but note the corrections:
storage vars are now `R2_*` not `S3_*`, the LLM key is `GROQ_API_KEY` not
`GEMINI_API_KEY`, and email is Resend not PurelyMail.

Minimum set for the app to boot and run the pipeline:

```
ENVIRONMENT=production
DATABASE_URL=postgresql://...        # Neon
REDIS_URL=rediss://...               # Upstash
GROQ_API_KEY=gsk_...
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_ENDPOINT_URL=https://...r2.cloudflarestorage.com
R2_BUCKET_NAME=scriptripper-artifacts
RESEND_API_KEY=re_...
FROM_EMAIL=reports@yourdomain.com
CRON_SECRET_KEY=<openssl rand -hex 32>
```

Add the Stripe variables from `STRIPE_BILLING.md` when you wire up billing.

Saving an env var triggers an automatic redeploy (~2–3 minutes). Watch the **Logs** tab
to confirm the new value loaded.

---

## Step 5 — Run database migrations

After the first deploy finishes, apply the Alembic migrations **manually** (project rule:
no migrations without explicit confirmation):

1. Open the `scriptripper` service → **Shell** tab. Wait ~10 seconds for it to connect.
2. You land in `/app`. Run:
   ```bash
   alembic upgrade head
   ```
3. If there are seed scripts (e.g. seeding the rip library), run them here too.

The Shell tab runs inside the live container with all env vars present — it is the right
place for one-off database work and connection tests.

---

## Step 6 — Custom domain and DNS

ScriptRipper's API should answer at a subdomain (e.g. `api.scriptripper.com`, or whatever
the project decides). In the service: **Settings → Custom Domain → Add**. Render shows
the DNS record to create.

At the domain registrar, add the record Render asks for — typically a `CNAME` pointing
the subdomain at `scriptripper.onrender.com`. The old guide walked through GoDaddy
specifically; any registrar's DNS panel works the same way. DNS propagation takes
10–30 minutes.

Also update `CORS_ORIGINS` so the frontend's domain is allowed to call the API.

---

## Step 7 — The daily-rip cron trigger

This is **new** — the archive had no equivalent because the old worker handled scheduling
internally. The current design exposes `POST /api/cron/daily-rip`, protected by
`Authorization: Bearer <CRON_SECRET_KEY>`. Something external has to call it once a day.

Two reasonable options — this is an open decision, not a settled one:

- **Render Cron Job.** Add a second Render service of type `cron` whose command is a
  single `curl`:
  ```bash
  curl -fsS -X POST https://api.scriptripper.com/api/cron/daily-rip \
       -H "Authorization: Bearer $CRON_SECRET_KEY"
  ```
  Keeps everything on one platform. A Render cron job is a paid feature.
- **External scheduler** — a free service like `cron-job.org`, or a GitHub Actions
  scheduled workflow, that makes the same authenticated request. Zero extra Render cost,
  which fits the zero-cost-stack goal.

Pick this when the build phase reaches the pipeline. It does not block the initial deploy.

---

## Useful: change an env var from the command line

The archive included `update_render_cors.sh`, a small script that updates a Render env
var through Render's API instead of clicking the dashboard. The pattern is worth keeping
for scripted changes (e.g. updating `CORS_ORIGINS` when the frontend domain changes):

```bash
# Get a key at https://dashboard.render.com/u/settings/api-keys
export RENDER_API_KEY=rnd_xxxxx

curl -X PUT \
  "https://api.render.com/v1/services/<SERVICE_ID>/env-vars/CORS_ORIGINS" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"value": "https://scriptripper.com,https://www.scriptripper.com"}'
```

The `<SERVICE_ID>` is the `srv-...` string in the service's dashboard URL. Updating a var
this way still triggers an automatic redeploy.

---

## Cost

The free tier is fine for getting live and testing. Note that a free Render web service
**sleeps after inactivity** and takes a few seconds to wake — acceptable for a personal
tool, not for a snappy customer-facing app. The first paid tier ("Starter") removes the
sleep. Because the database and Redis are now external (Neon/Upstash free tiers, R2's
10 GB free allowance), the *only* thing that costs money on Render itself is the web
service — far cheaper than the old three-service-plus-database setup.
