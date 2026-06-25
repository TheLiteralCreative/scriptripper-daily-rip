# ScriptRipper Daily Rip — Forward Plan

**Last updated:** 2026-06-24
**Current version:** 0.3.1 (database schema live on Neon — first migration `5e4aca780667` applied)
**Architecture ref:** `docs/ScriptRipper_Daily-Rip(pivot)/ScriptRipper _Daily Rip_ Architecture & Pivot Plan.md`
**Build instructions (legacy ref):** `docs/ScriptRipper_Daily-Rip(pivot)/ScriptRipper _Daily Rip_ Build Instructions for Claude Code.md`
**Prompt archive:** `docs/prompt-archive/`
**Original alpha (reference only):** `ScriptRipper_Archive_20260412.zip` → see "Reference Material — Original Alpha" below.

---

## Architecture Contract (locked decisions)

### Output Structure
- **DailyReport** — master index document per day; indexes all subscription documents and their TOCs
- **SubscriptionDocument** — one per subscription per day; header + TOC + one section per rip task that ran
- **Naming convention:** `YYYY-MM-DD__daily-report.md` / `YYYY-MM-DD__[subscription-slug]__[rip-profile-name].md`
- **Archive lookup:** Date → Subscription → Rip-Spec → Content (3-level hierarchy)

### Rip / Task System
- A **Rip** = one named analysis task (prompt)
- A **Rip Profile** = a saved, named collection of rips assigned to a subscription
- **Favorites** = user-starred rips stored on UserProfile; seeded via "Apply favorites" button when creating a subscription
- Subscription setup: apply favorites → add/remove from full rip library (checkbox list) → save profile

### Personal Relevance Layer
- **Phase 1:** Questionnaire at user setup → stored as `UserProfile.context_text`
- **Prompt injection:** Each rip has an optional appended block using `context_text` for personalized application suggestions. Additive — does not alter base rip output.
- **Phase 2 (future):** Replace static `context_text` with live query to a personal AI model via MCP/API. Data model unchanged.

### UI (5 surfaces)
1. **Dashboard** — today's Daily Report, archive browser
2. **Subscriptions** — add/edit sources, assign rip profiles
3. **Rip Library** — all available tasks, mark favorites, preview prompts
4. **User Profile** — questionnaire, personal context, future model connection
5. **Settings** — credentials, delivery preferences, cron schedule

### Data Model (shape locked)
```
User
 ├── UserProfile         (context_text, questionnaire fields)
 ├── FavoriteRips        (list of rip task_names)
 └── Subscriptions
      └── Subscription
           ├── source_type, source_url, active, last_checked_at
           ├── rip_profile (ordered list of task_names)
           └── ContentItems
                └── ContentItem
                     ├── title, url, published_at, status
                     ├── transcript_text
                     └── RipResults
                          └── RipResult (task_name, result_markdown)

DailyReport             (date, status, archive_url)
 └── SubscriptionDocument (subscription_id, document_markdown, archive_url, toc_json)
```

### Stack (locked)
- **Backend:** FastAPI (single service, BackgroundTasks — no separate worker)
- **LLM:** Gemini (default, confirmed from existing env) — Anthropic + OpenAI keys also present
- **Transcription:** Groq Whisper Large V3
- **Database:** **Neon** PostgreSQL (decided 2026-06-24). Schema live — migration `5e4aca780667` applied to `neondb`. Connection string in `.env` (`DATABASE_URL` + `DATABASE_URL_EXTERNAL`). *(Was: Render PostgreSQL — superseded.)*
- **Queue/cache:** Redis — host TBD under NODE-01 (local Redis or Upstash). Render `scriptripper-redis` is legacy.
- **Storage:** Cloudflare R2 / S3-compatible — bucket: `scriptripper-artifacts`
- **Email:** PurelyMail (NOT Resend) — smtp.purelymail.com:587, from: noreply@scriptripper.com
- **Payments:** Stripe (live keys present in env — handle with care)
- **Monitoring:** Sentry (DSN configured in env)
- **Deployment:** **NODE-01** home server (decided 2026-06-24) — Cloudflare Tunnel + launchd, same pattern as SignalRipper. *(Was: Render — superseded; see CLAUDE.md + SignalRipper `HOSTING-ROADMAP.md` supersede note. The 4 stale `scriptripper-*` Render services are decommission candidates.)*
- **Frontend:** TBD — first decision of Phase 0

---

## Phase Status

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 0 | Frontend tech decision + project scaffolding | **Done** — React SPA + FastAPI (single Render service) |
| Phase 1 | Backend foundation (settings, models, Alembic, auth skeleton) | **Done** — all models, API routers, service stubs, Alembic wired |
| Phase 2 | Service layer (Gemini LLM, Groq Whisper, PurelyMail, R2 storage) | **Next** |
| Phase 3 | Ingestion engine (RSS/feedparser, YouTube/yt-dlp, article scraping) | Pending |
| Phase 4 | Rip pipeline (task execution, document assembly, TOC generation) | Pending |
| Phase 5 | Delivery + archive (DailyReport assembly, email, R2 archive) | Pending |
| Phase 6 | Frontend — Subscriptions, Rip Library, Dashboard, User Profile | Pending |
| Phase 7 | Cron endpoint + automation wiring | Pending |
| Phase 8 | Personal relevance layer (questionnaire, prompt injection) | Pending |
| Phase 9 | Personal AI model integration (MCP/API, future) | Deferred |

---

## UP NEXT

> **DONE 2026-06-24:** env wired; schema live on Neon; app-runtime DB connectivity (asyncpg/SSL) fixed + smoke-tested (`scripts/smoke_db.py`); FastAPI app boots & serves locally.

### Road to a functional tool — build the pipeline FIRST, deploy to NODE-01 LAST

**"Functional" = Phases 2–5 produce one real daily report emailed to you.** The scaffold is a
shell (models, API, auth, DB, server) but the *engine* is not built: `app/api/cron.py` is a
**stub**, and `app/services/ingestion.py` (Phase 3) does not exist. Deploying before the
pipeline exists only schedules a job that calls a stub. Deployment is the wrapper, not the next step.

1. **[CLAUDE]** Phase 2 — verify the service layer end-to-end with the real creds: Gemini LLM, Groq Whisper (**needs ffmpeg**), PurelyMail SMTP, R2 upload/download. (Written in April, never run.)
2. **[CLAUDE]** Phase 3 — ingestion engine: `app/services/ingestion.py` (**does not exist**) — `check_subscriptions()`, RSS/feedparser, YouTube/yt-dlp, article/BeautifulSoup, idempotency on `(subscription_id, source_url)`.
3. **[CLAUDE]** Phase 4 — rip pipeline: run rips against transcripts (`llm.py`), assemble `SubscriptionDocument`s + TOC.
4. **[CLAUDE]** Phase 5 — delivery + archive: assemble `DailyReport` index, email via PurelyMail, archive to R2. **Wire `cron.py` to the real `run_daily_pipeline`** (replace the stub).
5. **[TOGETHER]** First end-to-end on the laptop: create a User + one Subscription (via API/seed — GUI is Phase 6, so seed via API; note auth wrinkle in deploy doc), trigger the cron endpoint, confirm a real report lands in your inbox.
6. **[TOGETHER]** Deploy to NODE-01 — full runbook in `docs/deployment/NODE-01-DEPLOYMENT.md` (launchd serve on :8001 + scheduled Daily Rip + optional Cloudflare Tunnel). Decommission stale Render services.
7. **[YOU, low priority]** Rotate the GitHub PAT (in `.env.backup_pre-wire`).

*Phase 6 (React GUI) can follow the headless tool — it's for setup/subscription management, not required for the cron+email path.*

---

## Completed

- ✓ **2026-06-24 session:** env wired (`vision/scriptripper-api.env` → root `.env`); fixed model name-collision (`date: Mapped[date]` in `report.py`) via `from __future__ import annotations`; fixed Alembic async/sync + SSL (sync psycopg2 + `sslmode=require`); **chose Neon** for DB; generated + applied first migration `5e4aca780667` — all 8 tables live; **hosting decision: NODE-01 over Render**; updated canon docs (this file, CLAUDE.md, SignalRipper HOSTING-ROADMAP supersede note, PORTFOLIO, CITY_PLAN).
- ✓ Legacy codebase reconnaissance (read-only, GitHub) — 2026-04-12
- ✓ Architecture contract established — 2026-04-12
- ✓ Legacy prompt profiles archived to `docs/prompt-archive/` — 2026-04-12
- ✓ Project scaffolding: `.claude/commands/`, `CLAUDE.md`, `FORWARD_PLAN.md`, session log dir — 2026-04-12
- ✓ Global toolkit installed: `/session-open`, `/session-close`, `/render-oversight`, `/render-diagnose`, `/deploy`, `/godaddy-dns`, `/auth-oversight`, `/database-oversight` — 2026-04-12
- ✓ Legacy archive zip (`ScriptRipper_Archive_20260412.zip`) reviewed — credentials extracted to `vision/scriptripper-api.env` — 2026-04-12
- ✓ Existing Render infrastructure confirmed: keep PostgreSQL, Redis, API service — 2026-04-12
- ✓ Stack corrected: PurelyMail (not Resend), Gemini default LLM, Stripe + Sentry wired — 2026-04-12
- ✓ Phase 0 complete: React SPA + FastAPI confirmed (single Render service) — 2026-04-12
- ✓ Phase 1 complete: Full scaffold — app/, models, API routers, service stubs, Alembic, frontend skeleton — 2026-04-12

---

## Decisions Pending

| Decision | Owner | Blocking |
|----------|-------|---------|
| Email recipient(s) — single address or configurable | YOU | Phase 5 |
| Rip prompt redesign — adapt legacy 17 prompts or rewrite for new structure | TOGETHER | Phase 4 |
| ~~Frontend technology~~ | ~~TOGETHER~~ | Resolved: React SPA served by FastAPI (single service) |
| ~~Deployment target~~ | ~~YOU~~ | Resolved 2026-06-24: **NODE-01** (was Render — superseded) |
| ~~Database host~~ | ~~TOGETHER~~ | Resolved 2026-06-24: **Neon** (Postgres; schema live) |

---

## User's Vision (verbatim — the north star)

### On ease of use
> "EASY. That's my ask. Whether it's an icon on my desktop or a bookmark in my browser, I'd like to gain access with a single click, and avoid having to spin up any virtual servers or wake up any clouds... I just want it to be EASY."

> "If it's working the way it's supposed to, my interaction with the tool will be limited to the initial set-up, and any additional subscriptions I choose to add once I've got it up and running. What we've been describing is a model that executes at a particular time each day, delivering a particular product at that particular time."

> "If we're talking about a 'throw-away' document delivered via email for download, digestion and discard (because it's also being archived by the tool itself in case I need to reference something from a previous delivery) then maybe Render IS the answer."

The tool runs itself. The user reviews output. Email is the delivery mechanism — ephemeral by design, archived by the system.

### On GUI vs CLI
> "I do think there needs to be a method by which the user is able to interact with the tool that isn't limited to the CLI, although, the CLI IS as important an access point."

Both matter. GUI for setup and subscription management. CLI remains valid. No sacrificing UX for simplicity.

### On the rip system and prompt design
> "I would like to start with a tool that I will use, and that leverages the existing identification of desired outputs included in the legacy project. Eventually, if all goes as planned, the usefulness and optimization of this tool to my process, will demand that I share this with others who might also experience a similar benefit from the tool's adoption and use. We should plan for that to avoid building ourselves into a 'myopic use-case' corner."

> "The user should have the opportunity to identify specifically what it is they hope to parse from the selected media with any given 'rip'. Potentially, I may want multiple documents created from a single source."

> "Setting up a process of selection/recognition that weaves together the ScriptRipper experience is something worth noting as a goal or priority."

### On personal relevance
> "I'm imagining a way that allows this tool to be used BY a personal Model with insights into the user's habits, interests, and professional profile... By providing access, either through MCP, API, CLI to a user's personal model, their user profile could become a powerful aspect of this already powerful tool by 'knowing the user better than they know themselves' so to speak."

> "If each Prompt contains a 'How does this benefit ME SPECIFICALLY' resulting in custom applications and instructions inspired by the media content — The User will need an easy way to provide the Ripper with that personal information."

### On meetings vs. presentations split
> "This distinction was a fundamental Delta in the pipeline of the original tool, but for the purposes of this new version, it may not be as important to differentiate between the two types of inputs at such an early stage... I'd like to maintain a degree of flexibility and if possible, avoid scenarios where the tool is ill equipped to deliver meaningful, useful reports by allowing for a more broad 'top-of-funnel' acceptance and determining a way to get 'something-out-of-everything.'"

### On UI redesign
> "I didn't dislike the previous interface, but I believe it can probably be more intuitive, or user-friendly based on the elements we've discussed here. Optimization is key, but not at the expense of value or useability. We should keep it as simple as we can without dumbing it down."

### On memory and continuity
> "EVERY time I use Claude Code, if possible, I'd like you to learn from what we do and retain that knowledge in whatever way suits you and serves the process best. Optimization is what I'm after."

---

## Reference Material — Original Alpha (pre-pivot, scriptripper.com)

The **first functional ScriptRipper** — the manual-transcript-upload alpha that ran at
**scriptripper.com** — is preserved (not lost) inside `ScriptRipper_Archive_20260412.zip`
(repo root; gitignored as `*.zip`). The current build is a ground-up rewrite, so this is
**reference only** — but the UI and the worker/automation are worth mining, not reinventing.

Inside the zip:

- **`ScriptRipper/ScriptRipper+/`** — the most mature deployed version (web + api + worker;
  `render.yaml` + `vercel.json`). This *is* the source of the legacy `scriptripper-web` /
  `-api` / `-worker` Render services.
  - **`web/`** — the interface Joel liked: **Next.js 14 + TypeScript + Tailwind + Radix UI +
    React Query + Framer Motion**; `mammoth` (.docx upload parsing), `jszip` / `file-saver`
    (output download). Strongest reference for the GUI (Phase 6). *Caveat:* it's Next.js,
    whereas the pivot chose React-SPA-on-FastAPI — mine the design/components, not the
    framework wholesale. (SignalRipper's FastAPI-served GUI is the other reference point.)
  - **`api/`**, **`worker/`**, **`shared/`** — the original backend + background worker.
- **`ScriptRipper/ScriptRipper-MVP/`** (`apps/` monorepo) and **`ScriptRipper/ScriptRipper_legacy/`**
  — earlier iterations.
- **`ScriptGetter/`** — a sibling **automated content-collection pipeline** project (blueprint +
  punchlist + hosting notes). Directly relevant to Phase 3 (ingestion) and the
  scheduled-collection vision — a prior attempt at exactly that problem.
- **`ScriptRipper-ENV-REF/ScriptRipper.com/`** — env reference for the live site.

To browse it, extract just the needed subtree (e.g. `ScriptRipper/ScriptRipper+/web/src/`
*without* `node_modules` / `.next`) rather than the whole 448 MB archive. The same archive is
also duplicated in the stale top-level `MANUS_Document_Repository/ScriptRipper_Re-Do/` copy
(deletion-pending) — use the canonical one in this repo.

---

## Notes & Constraints

- Groq Whisper: 25MB file size limit — ffmpeg chunking required before upload
- Idempotency: always check `source_url` against existing `ContentItem` records
- Error isolation: one failed transcription must not abort the full daily pipeline
- Legacy `meetings`/`presentations` prompt split is preserved in archive as reference but NOT enforced as a pipeline constraint — rip profiles are user-composed
- Personal relevance prompt injection is additive — base rip output is never altered, only extended
- SaaS-forward design: User IDs on all models, auth layer exists from day one (even if only one account)
