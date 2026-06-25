# ScriptRipper — NODE-01 Deployment Runbook

**Status:** NOT yet executed.
**Gated on:** the Daily Rip pipeline being built to a working end-to-end (Phases 2–5).
Deploying before that only schedules a job that calls a **stub** (`app/api/cron.py` currently
returns "pipeline not yet implemented"). See `docs/FORWARD_PLAN.md` → "Road to a functional tool."

**Pattern:** mirrors SignalRipper (Synthetic-Marketer) on NODE-01 — a proven setup. Primary
references (in the `Synthetic-Marketer` repo): `docs/DEDICATED-HOST-SETUP.md`,
`docs/REMOTE-HOSTING.md`, `docs/CLOUDFLARE-ACCESS-SETUP.md`, and `deploy/launchd/`.

---

## 0. Before deploy — code must be pushed
The repo is `TheLiteralCreative/scriptripper-daily-rip`. After the working pipeline is
committed on the laptop, **`git push`** so NODE-01 can clone the latest. Secrets are NOT in
git (`.env`, `vision/` are gitignored) — they transfer separately (step 4).

## 1. Prerequisites on NODE-01 (one-time)
1. **Code:** `git clone` into `/Users/literalcreative/srv/apps/scriptripper` (SignalRipper's
   layout). Private repo → needs git auth on NODE-01 (SSH key or PAT).
2. **System deps:** Python 3.9+ and **ffmpeg** (`brew install ffmpeg`). `transcription.py`
   chunks audio with ffmpeg before Groq Whisper (25 MB limit) — without it, transcription fails.
3. **Python env:** `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
   (includes `greenlet`, required by SQLAlchemy async).
4. **Secrets:** copy the laptop's `.env` into the NODE-01 app dir. Transfer securely; do NOT
   commit. Same Neon / Groq / R2 / PurelyMail values.
5. **Port:** SignalRipper uses 8000. **ScriptRipper uses 8001** (avoid collision).
6. **Smoke test on NODE-01:** `python scripts/smoke_db.py` (confirms Neon reachable from the
   home network), then `uvicorn app.main:app --host 127.0.0.1 --port 8001` and curl
   `/api/health`.

## 2. launchd — serve the app (keep-alive + restart on boot)
Create `~/Library/LaunchAgents/com.literalcreative.scriptripper.plist`, modeled on
SignalRipper's plist:
- **ProgramArguments:** `<app>/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8001`
  (or a small `start.py` like SignalRipper's).
- **WorkingDirectory:** `/Users/literalcreative/srv/apps/scriptripper`
- **RunAtLoad:** true · **KeepAlive:** true · **ThrottleInterval:** 10
- **Logs:** `/Users/literalcreative/srv/logs/scriptripper.out.log` / `.err.log`
- Load: `launchctl load -w ~/Library/LaunchAgents/com.literalcreative.scriptripper.plist`

## 3. launchd — schedule the Daily Rip
Create `~/Library/LaunchAgents/com.literalcreative.scriptripper-cron.plist`:
- **StartCalendarInterval:** `{ Hour: 6, Minute: 0 }` (your delivery time).
- **ProgramArguments:** a small script that POSTs the local cron endpoint —
  `curl -X POST http://127.0.0.1:8001/api/cron/daily-rip -H "Authorization: Bearer $CRON_SECRET_KEY"`
  (read the secret from `.env`) — OR a python entrypoint that calls `run_daily_pipeline` directly.
- **RunAtLoad:** false (don't fire on every reboot).
- **Prereq:** the cron endpoint must be wired to the real pipeline first (Phase 5).

## 4. Optional — public GUI access (only if you want the web UI off-LAN)
Cloudflare Tunnel + Access, mirroring SignalRipper's `com.literalcreative.cloudflared` /
`signalripper.literalcreative.com`. Suggested hostname `scriptripper.literalcreative.com`.
**Not needed** for the cron + email path — the tool delivers by email regardless. Reference:
SignalRipper `docs/REMOTE-HOSTING.md` + `CLOUDFLARE-ACCESS-SETUP.md`.

## 5. Verification checklist
- [ ] `launchctl list | grep scriptripper` shows both agents; app survives a reboot.
- [ ] `/api/health` responds on 127.0.0.1:8001.
- [ ] Manual cron trigger produces a real `DailyReport` — emailed + archived to R2.
- [ ] Scheduled job fires at the set time and delivers.
- [ ] (If tunnel) GUI reachable and gated by Cloudflare Access.

## 6. After deploy
- Decommission the 4 stale `scriptripper-*` Render services (worker / web / api / redis).
- Update `FORWARD_PLAN.md` + `PORTFOLIO.md` (ScriptRipper → LIVE on NODE-01).

---

## Known wrinkles to expect (not blockers — flagged so they're not surprises)
- **Auth for seeding subscriptions.** API write endpoints are gated by `get_current_user`
  (Google OAuth + JWT). The cron endpoint uses `CRON_SECRET_KEY` (no user auth), but to create
  the first User + Subscription you need either the OAuth flow working or a one-off seed script /
  temporary local bypass. Resolve during Phase 3/first-end-to-end, before deploy.
- **asyncpg SSL** is handled (`connect_args ssl=True` when DATABASE_URL carries `sslmode`).
- **Frontend (Phase 6)** is optional for the headless cron+email tool; it's for
  setup/subscription management and can follow deployment.
