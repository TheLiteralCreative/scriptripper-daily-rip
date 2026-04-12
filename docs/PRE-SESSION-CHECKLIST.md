# ScriptRipper Daily Rip — Pre-Session Setup Checklist

*Complete these before the next Claude Code session. Claude will verify them at session open.*

---

## 1. Fix the broken credential in `vision/scriptripper-api.env`

Line 13 is malformed — two variables got merged into one. It currently reads:

```
GOOGLE_CLIENT_SECRET="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\nSENTRY_DSN=https://..."
```

It should be two separate lines:

```
GOOGLE_CLIENT_SECRET=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
SENTRY_DSN=https://0582f1b44a9a0c0dfb4831fb5703dfe9@o4510329582125057.ingest.us.sentry.io/4510329612599296
```

Fix this file directly (it's gitignored — safe to edit).

---

## 2. Get missing credentials and add them everywhere

Four variables are missing from the env entirely. You need to source them and add them to:
- `vision/scriptripper-api.env` (local reference)
- Render environment variables (the live service)
- Your local `.env` (for local dev — copy from `vision/scriptripper-api.env`)

| Variable | Where to get it | Notes |
|----------|----------------|-------|
| `GROQ_API_KEY` | console.groq.com → API Keys | Needed for Whisper transcription |
| `R2_ACCESS_KEY_ID` | Cloudflare dashboard → R2 → Manage R2 API Tokens | Create an R2-specific token |
| `R2_SECRET_ACCESS_KEY` | Same as above — only shown once at creation | |
| `R2_ENDPOINT_URL` | Cloudflare dashboard → R2 → bucket → Settings | Format: `https://<account_id>.r2.cloudflarestorage.com` |
| `CRON_SECRET_KEY` | Generate any random string | e.g. run: `openssl rand -hex 32` in terminal |

---

## 3. Add `DATABASE_URL_EXTERNAL` for local Alembic runs

The `DATABASE_URL` in the existing env is the **Render-internal** URL — it only works from inside Render's network. For running Alembic migrations from your local machine, you need the **external** URL.

**Where to find it:**
Render dashboard → your PostgreSQL service → **External Database URL**

Add it as `DATABASE_URL_EXTERNAL` to your local `.env` only. Do NOT add it to Render env vars (not needed there — Render already has the internal URL).

---

## 4. Update Render service to deploy from the new repo

The existing Render API service (`scriptripper-api.onrender.com`) is currently pointed at the old ScriptRipper GitHub repo. It needs to point to the new one.

**Steps:**
1. Render dashboard → `scriptripper-api` service → Settings
2. Under **Repository**, disconnect the old repo
3. Connect: `TheLiteralCreative/scriptripper-daily-rip`
4. Set **Root Directory** to leave blank (repo root)
5. Set **Build Command**: `pip install -r requirements.txt`
6. Set **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
7. Do NOT deploy yet — wait until after the first Alembic migration

---

## 5. Run the first Alembic migration (do this with Claude)

Don't run this solo — we'll do it together at the start of the next session.

What will happen:
1. Confirm the migration looks correct (Claude will show you the generated SQL)
2. Run: `alembic revision --autogenerate -m "initial schema"`
3. Run: `alembic upgrade head` against the Render external URL
4. Verify tables created in Render PostgreSQL

**Prerequisite:** `DATABASE_URL_EXTERNAL` must be set in your local `.env` first (step 3 above).

---

## 6. Local dev environment (optional but useful)

If you want to run the app locally before deploying:

```bash
# From ScriptRipper_Re-Do/
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run backend
uvicorn app.main:app --reload

# In a second terminal — run frontend dev server
cd frontend
npm install
npm run dev
# Frontend at http://localhost:5173 — proxies /api to :8000
```

---

## Summary checklist

- [ ] Fix `GOOGLE_CLIENT_SECRET` in `vision/scriptripper-api.env` (line 13)
- [ ] Get `GROQ_API_KEY` from Groq console
- [ ] Create Cloudflare R2 API token → get `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_ENDPOINT_URL`
- [ ] Generate `CRON_SECRET_KEY` (`openssl rand -hex 32`)
- [ ] Add all missing vars to `vision/scriptripper-api.env` and Render env vars
- [ ] Get Render external Postgres URL → add as `DATABASE_URL_EXTERNAL` to local `.env`
- [ ] Update Render service to point at `TheLiteralCreative/scriptripper-daily-rip`
- [ ] Do NOT trigger a Render deploy yet — wait for Alembic migration with Claude

---

*Next session starts with: `/session-open` → verify credentials → run Alembic migration → deploy.*
