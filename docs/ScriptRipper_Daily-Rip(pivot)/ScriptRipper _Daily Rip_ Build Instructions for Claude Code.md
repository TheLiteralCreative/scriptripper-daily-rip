# ScriptRipper "Daily Rip" Build Instructions for Claude Code

**Author:** Manus AI
**Date:** April 2026
**Target Agent:** Claude Code (or similar CLI-based AI agent)

## 1. Project Context & Scope

This document provides executable instructions for refactoring the existing `ScriptRipper` codebase into the **"Daily Rip"** automated pipeline. 

The goal is to transition the application from a manual, user-triggered transcription analysis tool into a fully automated, zero-cost pipeline that ingests daily content (podcasts, YouTube, articles), transcribes it, analyzes it using existing prompt profiles, and emails a consolidated report.

### Core Objectives
1. **Unify the Architecture:** Merge the separate FastAPI API and Python RQ Background Worker into a single FastAPI service to eliminate the need for a paid worker instance.
2. **Implement Zero-Cost Providers:** Swap OpenAI/Anthropic for Groq (LLM & Whisper), AWS S3 for Cloudflare R2, Render PostgreSQL for Neon, and SendGrid for Resend.
3. **Build the Ingestion Engine:** Create new database models and endpoints for managing `Subscriptions` (RSS, YouTube, URLs) and `ContentItems`.
4. **Automate the Pipeline:** Expose a secure `/api/cron/daily-rip` endpoint that triggers the daily ingestion, transcription, analysis, and email delivery process.

---

## 2. File Structure & Mapping

The existing monorepo structure will be modified. Claude Code must execute these changes.

### Current Structure (Relevant Paths)
```
/api/app/
  ├── config/settings.py
  ├── models/
  ├── routes/
  │   ├── analyze.py
  │   └── jobs.py
  └── services/
      ├── llm.py
      └── email.py
/worker/
  ├── main.py
  └── tasks/analysis.py
/shared/
  └── analysis_engine.py
```

### Target Structure (Post-Refactor)
```
/api/app/
  ├── config/settings.py          # Update with new provider keys (Groq, Resend, etc.)
  ├── models/
  │   ├── subscription.py         # NEW: Defines Subscription and ContentItem tables
  │   └── rip_report.py           # NEW: Defines DailyRip and RipItem tables
  ├── routes/
  │   ├── analyze.py              # Keep existing manual analysis for legacy support
  │   ├── subscriptions.py        # NEW: CRUD for content sources
  │   └── cron.py                 # NEW: The Daily Rip trigger endpoint
  ├── services/
  │   ├── llm.py                  # Refactor to use Groq by default
  │   ├── transcription.py        # NEW: Groq Whisper API integration
  │   ├── ingestion.py            # NEW: RSS parsing and YouTube caption extraction
  │   ├── email.py                # Refactor to use Resend API
  │   └── storage.py              # Refactor to use Cloudflare R2 (boto3)
  └── worker/                     # NEW FOLDER (Moved from root)
      └── tasks.py                # Background tasks using FastAPI BackgroundTasks
```

---

## 3. Database Schema Updates

Claude Code must generate SQLAlchemy models and Alembic migrations for the following entities.

### `Subscription`
Tracks the sources the user wants to monitor.
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key to users)
- `name`: String (e.g., "Lex Fridman Podcast")
- `source_type`: Enum (rss, youtube, blog)
- `source_url`: String
- `active`: Boolean (Default: True)
- `last_checked_at`: DateTime

### `ContentItem`
Tracks individual episodes or articles ingested from subscriptions.
- `id`: UUID (Primary Key)
- `subscription_id`: UUID (Foreign Key)
- `title`: String
- `url`: String
- `published_at`: DateTime
- `status`: Enum (pending, transcribed, analyzed, failed)
- `transcript_text`: Text (Nullable)
- `audio_url`: String (Nullable)

### `DailyRip`
Tracks the consolidated daily reports.
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key)
- `date`: Date
- `status`: Enum (processing, completed, delivered)
- `report_markdown`: Text
- `s3_archive_url`: String

---

## 4. Step-by-Step Execution Directives for Claude Code

When initiating the build, pass these explicit directives to Claude Code. It should execute them sequentially, waiting for confirmation between phases.

### Phase 1: Environment & Dependency Setup
> **Claude Code Prompt:** "Read `api/requirements.txt`. Remove `openai`, `anthropic`, and `sendgrid`. Add `groq`, `resend`, `feedparser` (for RSS), and `yt-dlp` (for YouTube audio). Update `api/app/config/settings.py` to include environment variables for `GROQ_API_KEY`, `RESEND_API_KEY`, and Cloudflare R2 credentials. Run tests to ensure the app still boots."

### Phase 2: Database Migration
> **Claude Code Prompt:** "Create the SQLAlchemy models for `Subscription`, `ContentItem`, and `DailyRip` in `api/app/models/`. Generate an Alembic revision that creates these tables. Do not apply the migration yet; output the migration script for my review."

### Phase 3: Service Layer Refactoring
> **Claude Code Prompt:** "Refactor `api/app/services/llm.py` to use the `groq` Python client. Ensure it still supports the existing `TranscriptAnalyzer` interface in `shared/analysis_engine.py`. Create `api/app/services/transcription.py` that accepts an audio file path or URL and returns text using the Groq Whisper API. Refactor `api/app/services/email.py` to use the Resend SDK instead of SendGrid."

### Phase 4: The Ingestion Engine
> **Claude Code Prompt:** "Create `api/app/services/ingestion.py`. Write a function `check_subscriptions()` that iterates through active `Subscription` records. If it's an RSS feed, use `feedparser` to find items published in the last 24 hours. If it's YouTube, use `yt-dlp` to check for new videos. Save new findings as `ContentItem` records with status 'pending'."

### Phase 5: The Daily Rip Pipeline
> **Claude Code Prompt:** "Create `api/app/routes/cron.py`. Add a secure POST endpoint `/api/cron/daily-rip` (protected by a secret bearer token). This endpoint should trigger a FastAPI `BackgroundTask` that: 1) Runs `check_subscriptions()`. 2) Iterates through 'pending' `ContentItems`, transcribing them via Groq Whisper if necessary. 3) Runs the transcribed text through `TranscriptAnalyzer` using the 'Overview Summary' and 'Action Items' prompts. 4) Concatenates the results into a single Markdown document. 5) Emails the document via Resend. 6) Uploads the Markdown to Cloudflare R2."

### Phase 6: Worker Unification
> **Claude Code Prompt:** "Delete the root `/worker` directory entirely. Ensure all background processing logic now lives inside the FastAPI application using `fastapi.BackgroundTasks`. Update `render.yaml` to remove the `scriptripper-worker` service definition."

---

## 5. Quality Assurance & Benchmarks

Claude Code must implement the following checks during the build:

1. **Prompt Compatibility:** Ensure the new Groq LLM integration correctly parses the existing `meetings_prompts.json` and `presentations_prompts.json` formats without modification.
2. **Audio File Limits:** Groq Whisper has a 25MB file size limit per request. Claude Code must implement a chunking utility in `transcription.py` using `pydub` or `ffmpeg` to split audio files larger than 25MB before sending them to the API.
3. **Idempotency:** The ingestion engine must check the `source_url` of new content against existing `ContentItem` records to prevent duplicating episodes if the cron job runs twice.
4. **Error Handling:** If one podcast fails to transcribe, the Daily Rip pipeline must catch the exception, log it, and continue processing the remaining subscriptions so the daily email is still sent.

---

## 6. Required Agent Skills & Context

To successfully execute this plan, Claude Code (or any agent) should leverage the following skills and contextual knowledge:

- **FastAPI Background Tasks:** Understanding how to use `BackgroundTasks` to return a 202 Accepted response to a cron ping while processing the heavy transcription/LLM workload asynchronously.
- **yt-dlp Audio Extraction:** Skill in configuring `yt-dlp` to extract *only* audio (m4a/mp3) from YouTube URLs to save bandwidth and storage before passing to Whisper.
- **SQLAlchemy 2.0:** Utilizing modern SQLAlchemy 2.0 syntax (using `Mapped` and `mapped_column`) as established in the existing `api/app/models/user.py` file.
- **Markdown Aggregation:** Skill in formatting clean, readable Markdown reports that combine multiple analysis outputs with clear headers, bullet points, and timestamps.
