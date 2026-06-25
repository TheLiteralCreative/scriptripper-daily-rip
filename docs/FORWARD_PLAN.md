# ScriptRipper Daily Rip — Forward Plan

**Last updated:** 2026-06-24
**Current version:** 0.3.1 (database schema live on Neon — first migration `5e4aca780667` applied)
**Architecture ref:** `docs/ScriptRipper_Daily-Rip(pivot)/ScriptRipper _Daily Rip_ Architecture & Pivot Plan.md`
**Build instructions (legacy ref):** `docs/ScriptRipper_Daily-Rip(pivot)/ScriptRipper _Daily Rip_ Build Instructions for Claude Code.md`
**Prompt archive:** `docs/prompt-archive/`

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

> Credentials + first migration: **DONE 2026-06-24.** Env wired, schema live on Neon.

1. **[CLAUDE]** App-runtime DB fix: `database_async_url` must handle Neon SSL — asyncpg rejects the `sslmode`/`channel_binding` query params that psycopg2 accepts. Strip/convert them for asyncpg before the app first connects. (Migration path already works; this is the *running app* path.)
2. **[TOGETHER]** Bring ScriptRipper online on NODE-01: serve FastAPI via launchd, schedule the Daily Rip (launchd `StartCalendarInterval` or local cron → `POST /api/cron/daily-rip`), optional Cloudflare Tunnel + Access for the GUI. Reuse SignalRipper's `deploy/launchd/` + tunnel pattern.
3. **[CLAUDE]** Phase 2: Verify service layer end-to-end — Gemini LLM, Groq Whisper, PurelyMail SMTP, R2 upload/download each get a minimal test call.
4. **[CLAUDE]** Phase 3: Ingestion engine — `ingestion.py` with `check_subscriptions()`, RSS + YouTube + article paths, idempotency check.
5. **[CLAUDE]** Phase 4: Rip pipeline — task execution, document assembly, TOC generation.
6. **[YOU, low priority]** Rotate the GitHub PAT that was in the old root `.env` (backed up as `.env.backup_pre-wire`); decommission the 4 stale `scriptripper-*` Render services.

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

## Notes & Constraints

- Groq Whisper: 25MB file size limit — ffmpeg chunking required before upload
- Idempotency: always check `source_url` against existing `ContentItem` records
- Error isolation: one failed transcription must not abort the full daily pipeline
- Legacy `meetings`/`presentations` prompt split is preserved in archive as reference but NOT enforced as a pipeline constraint — rip profiles are user-composed
- Personal relevance prompt injection is additive — base rip output is never altered, only extended
- SaaS-forward design: User IDs on all models, auth layer exists from day one (even if only one account)
