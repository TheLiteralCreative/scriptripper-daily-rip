# ScriptRipper — Deployment Documentation

This folder holds the deployment, billing, and operations knowledge for ScriptRipper.

It exists because a previous version of ScriptRipper was actually deployed once before
the "Daily Rip" pivot. That work produced a pile of deployment guides, scripts, and
config files. Rather than lose that hard-won knowledge, the useful parts were salvaged,
corrected for the current architecture, and rewritten into the three guides here.

| File | What it covers |
|------|----------------|
| `RENDER_DEPLOYMENT.md` | Getting ScriptRipper running on Render — Docker, services, env vars, domain, the daily-rip cron trigger |
| `STRIPE_BILLING.md` | Setting up the Stripe subscription/billing flow and webhooks |
| `OPERATIONS_PLAYBOOK.md` | Day-2 troubleshooting — reading logs, fixing CORS, diagnosing failed deploys |

---

## Where this came from

**Source:** `ScriptRipper_Archive_20260412.zip` (in the repo root) — specifically the
`ScriptRipper/` and `ScriptRipper/ScriptRipper+/` folders inside it. About 15 deployment
files were read and triaged: Render guides, a Stripe setup guide, Dockerfiles, a
`render.yaml` Blueprint, deploy scripts, and three `.claude/commands/` files that were
early attempts at turning the deployment process into reusable skills.

**Why it needed rewriting, not copying.** The archive is *pre-pivot*. Back then
ScriptRipper was a three-service application. The pivot to "Daily Rip" collapsed it into
one. Copying the old guides verbatim would have planted instructions that quietly
contradict the current design — the most dangerous kind of stale documentation, because
it looks authoritative. So every guide here was rebuilt against the architecture defined
in `CLAUDE.md` and `.claude/commands/env-setup.md`.

### The pivot, in one table

This is the single most useful thing to understand before reading the guides. The left
column is what the archive describes. The right column is what we are actually building.

| Concern | Pre-pivot (the archive) | Current (what we deploy) |
|---------|-------------------------|--------------------------|
| Services | 3: API + Next.js web + background worker | **1: a single FastAPI service** |
| Background jobs | Separate worker process | `fastapi.BackgroundTasks` inside the one service |
| Database | Render-hosted PostgreSQL | **Neon** (external, serverless Postgres) |
| Redis | Render-hosted Redis | **Upstash** (external, serverless Redis) |
| Object storage | `S3_*` env vars | **Cloudflare R2** — `R2_*` env vars |
| LLM + transcription | Gemini (default) + others | **Groq** — one `GROQ_API_KEY` covers Llama 3.3 70B *and* Whisper |
| Email | PurelyMail (SMTP) | **Resend** |
| Orchestration | n8n | None — removed |
| Auth on the cron job | — | `Authorization: Bearer <CRON_SECRET_KEY>` |
| Considered hosts | Railway, Vercel, Render | **Render** (decision locked) |

When a salvaged guide said "deploy the worker" or "set `S3_BUCKET_NAME`," that line was
either rewritten or dropped. Nothing in these three files should reference the old shape.

---

## What was discarded, and why

Not everything was worth keeping. These were intentionally left behind in the archive:

- **Railway deploy scripts** (`deploy_railway.sh`, `railway-deploy.js`) — Render is the
  locked choice. Railway is dead weight now.
- **Vercel deploy guide** (`VERCEL_DEPLOY.md`) — it targeted a Next.js frontend. The
  current frontend is React/Vite and its hosting is still a separate decision.
- **The worker Dockerfile and n8n docker-compose service** — there is no worker and no
  n8n anymore.
- **The old `render.yaml`** — kept only as a *reference for structure*. It describes
  three Docker services plus a Render database. A new, single-service `render.yaml` will
  be written fresh during the build phase.

The reasoning matters more than the list: salvage keeps *durable knowledge* (how Render's
dashboard works, how Stripe webhooks behave, how to read a failed deploy) and discards
*stale decisions* (which host, how many services).

---

## ⚠️ Security flags found during salvage

Two real credentials were found exposed while reading these files. **Both should be
rotated.** Neither is reproduced in any guide in this folder.

1. **A Stripe test secret key** (`sk_test_...`) was hardcoded into the old
   `STRIPE_SETUP_GUIDE.md` and `create-stripe-price.js`. It is a *test-mode* key, so the
   risk is low — but it is a live credential sitting in a file. Rotate it in the Stripe
   dashboard (Developers → API keys → roll the key) and never hardcode keys again; read
   them from `.env`.

2. **A GitHub Personal Access Token** (`ghp_...`) is currently sitting in plaintext in
   the repo's root `.env` file. `.env` is gitignored, so it is probably not on GitHub —
   but a token in a file is a token that can leak. **Revoke it now** at
   `github.com/settings/tokens` and generate a fresh one if you still need it. A separate
   note: that `.env` file is malformed (it holds a URL and a token, not the
   `KEY=value` pairs the app expects). Run `/env-setup` to rebuild it properly.

---

## How this connects to the Media Rippers Kit

ScriptRipper is meant to become the template for every future Ripper. That means these
three guides are not just ScriptRipper's deployment docs — they are the **first draft of
the Kit's deployment chapter**. Once ScriptRipper is actually live on Render and the
steps here are proven, the generic parts (the Render walkthrough, the Stripe flow, the
operations playbook) get lifted into `media-rippers-kit` so the next Ripper starts from a
working recipe instead of a blank page.

Read them in this order when the build phase begins: `RENDER_DEPLOYMENT.md` first, then
`STRIPE_BILLING.md`, and keep `OPERATIONS_PLAYBOOK.md` open as a reference when something
breaks.
