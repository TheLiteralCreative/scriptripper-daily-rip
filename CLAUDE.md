# ScriptRipper Daily Rip — Claude Code Context

## What this project is

A personal media intelligence workbench. It ingests RSS feeds, YouTube channels, and web articles daily; transcribes audio/video via Groq Whisper; runs user-selected analysis tasks ("rips") against each transcript; assembles structured per-subscription documents and a master daily index; and delivers the output by email and archives it to cloud storage.

Designed as a single-user personal tool first, SaaS-forward by architecture from day one.

## Vocabulary

| Term | Meaning |
|------|---------|
| **Rip** | A single named analysis task — one prompt applied to one transcript |
| **Rip Profile** | A saved, named collection of rips assigned to a subscription |
| **Favorites** | User-starred rips stored on UserProfile; used to seed new subscription profiles |
| **SubscriptionDocument** | Output doc for one subscription: header + TOC + one section per rip |
| **DailyReport** | Master index document for one day; links to all SubscriptionDocuments |
| **ContentItem** | A single ingested episode, video, or article |
| **RipResult** | The output of one rip task run against one ContentItem |

## Output naming convention

`YYYY-MM-DD__daily-report.md`
`YYYY-MM-DD__[subscription-slug]__[rip-profile-name].md`

Archive lookup hierarchy: **Date → Subscription → Rip-Spec → Content**

## Architecture decisions (locked)

- **Single FastAPI service** — no separate worker. Background tasks via `fastapi.BackgroundTasks`.
- **Stack (corrected 2026-06-24 to match `.env` + reality):** Gemini default LLM (Anthropic / OpenAI / Groq also wired, provider-switchable via `DEFAULT_LLM_PROVIDER`); Groq Whisper for transcription; **Neon** PostgreSQL (schema live as of 2026-06-24); Redis (host TBD under NODE-01); Cloudflare R2 storage; **PurelyMail** email (NOT Resend). *(Prior header said "Groq LLM / Upstash / Resend" — superseded.)*
- **Hosting (decided 2026-06-24):** Runs on **NODE-01** (always-on home server), **NOT Render** — reuses SignalRipper's Cloudflare Tunnel + launchd pattern. Render stays a later config flip if a SaaS trigger fires. Rationale + supersede note in SignalRipper's `docs/HOSTING-ROADMAP.md`.
- **SQLAlchemy 2.0** — `Mapped`/`mapped_column` syntax throughout.
- **SaaS-forward:** User IDs on all models. Auth layer exists from day one.
- **Cron endpoint:** `POST /api/cron/daily-rip` protected by `Authorization: Bearer <CRON_SECRET_KEY>`.
- **Idempotency:** check `source_url` against existing `ContentItem` records before inserting.
- **Error isolation:** one failed item must not abort the pipeline. Log and continue.
- **Personal relevance:** additive prompt injection using `UserProfile.context_text`. Never alters base rip output.

## Prompt architecture

- 17 legacy prompts archived in `docs/prompt-archive/` — reference only.
- Legacy meetings/presentations split is NOT enforced as a pipeline constraint.
- Rip profiles are user-composed from a flat library of available tasks.
- Each prompt follows the 4-block structure: Role & Goal / Core Instruction / Formatting Constraints / Negative Constraints.
- Personal relevance is an optional 5th block appended at runtime if `context_text` is set.

## Key files

| Path | Purpose |
|------|---------|
| `docs/FORWARD_PLAN.md` | Phase tracker, decisions pending, UP NEXT list |
| `docs/session-log/` | Per-session logs |
| `docs/prompt-archive/` | Legacy prompt profiles (reference) |
| `docs/ScriptRipper_Daily-Rip(pivot)/` | Original architecture plan + build instructions + credential guide |
| `docs/deployment/` | Render deploy guide, Stripe billing guide, operations playbook — salvaged from the pre-pivot archive and rewritten for the current stack |
| `.env` | Secrets (gitignored) — see `/env-setup` |

## Slash commands

| Command | When to use |
|---------|-------------|
| `/session-open` | Start of every session — produces Session Brief |
| `/session-close` | End of every session — commits, updates FORWARD_PLAN, writes log |
| `/env-setup` | First setup or when credentials need updating |

## Rules

- Never commit `.env` or any file containing secrets.
- Do not apply Alembic migrations without explicit user confirmation.
- Groq Whisper: 25MB file size limit — always chunk audio via ffmpeg before sending.
- Frontend technology is TBD — do not scaffold the frontend until confirmed.
- The legacy prompt split (meetings vs. presentations) is preserved as archive reference only. Do not re-impose it as a pipeline constraint.
- Personal relevance prompt injection is always additive and optional — never modify the base rip prompt text.
