# ScriptRipper "Daily Rip" Architecture & Pivot Plan

## 1. Current State Assessment

I have audited the existing ScriptRipper repository. The good news is that the codebase is a robust, multi-service application with excellent bones for the pivot you are requesting. It is currently designed for manual transcript analysis, but the underlying infrastructure is highly reusable.

### Strengths & Reusable Components
- **Robust API & Worker Architecture:** The separation of the FastAPI backend (`api`) and the background processing worker (`worker`) using Redis and RQ is perfect for long-running, asynchronous tasks like downloading, transcribing, and analyzing media.
- **LLM Abstraction Layer:** The `LLMProviderFactory` in `shared/analysis_engine.py` is highly reusable. It already supports Gemini, OpenAI, and Anthropic, giving us flexibility for the analysis phase.
- **Prompt Profiles:** The existing JSON-based prompt profiles (e.g., `meetings_prompts.json`, `presentations_prompts.json`) provide a strong foundation. We can easily adapt these or create a new "Daily Rip" profile to structure the output exactly as you need.
- **YouTube Transcript Extraction:** The existing `youtube-transcript` route in the Next.js frontend is functional. We will move this logic to the backend worker for automated, headless processing.

### Areas for Pivot
- **From Manual to Automated:** The primary shift is moving from user-uploaded files to automated, scheduled ingestion from RSS feeds, YouTube channels, and web articles.
- **Delivery Mechanism:** Instead of requiring you to log in and download a web UI artifact, the primary output becomes an automated daily email or an archived report delivered directly to you.

## 2. The "Daily Rip" Architecture

To achieve the goal of a daily, automated digest of specific subscriptions, we need to introduce three new core components to the existing stack: an **Ingestion Engine**, a **Transcription Service**, and a **Reporting & Delivery Module**.

### 2.1. Ingestion Engine (The Crawler/Scraper)
A new scheduled job (cron) will run daily to check registered subscriptions for new content.

**Data Model Updates:**
- **Subscription:** URL (RSS, YouTube channel, Blog), Type (audio, video, text), Status.
- **ContentItem:** Title, URL, Published Date, Source, Status (Pending, Transcribed, Analyzed, Delivered).

**Process:**
1. Fetch RSS feeds using a library like `feedparser`.
2. Scrape YouTube channels for new videos using the YouTube Data API or `yt-dlp`.
3. Extract text from blogs/articles using `beautifulsoup4` or a similar scraping tool.
4. Create `ContentItem` records in the PostgreSQL database for any new content published in the last 24 hours.

### 2.2. Transcription Service
Audio and video content requires transcription before the LLM can analyze it.

**Process:**
1. For YouTube videos, the system will first attempt to extract existing captions (moving the existing frontend logic to the backend worker).
2. If captions are unavailable, or for podcast audio files, the worker will download the media using `yt-dlp` or standard HTTP requests.
3. The system will transcribe the audio using a robust transcription model. I recommend integrating the **OpenAI Whisper API** for speed and accuracy, though we could also run a local Whisper model if cost or privacy is a primary concern.

### 2.3. Analysis & Reporting Module
Once all daily content is transcribed or extracted as text, the existing analysis engine takes over.

**Process:**
1. Run each transcript through the configured prompt profiles (e.g., "Overview Summary", "Key Quotes", "Action Items").
2. Aggregate the individual analyses into a single, cohesive "Daily Rip" Markdown or HTML document.
3. **Delivery:** Email the final report using the existing SendGrid integration (`SENDGRID_API_KEY`) and/or archive it to the S3-compatible storage (`S3_BUCKET_NAME`).

## 3. Implementation Protocol & Next Steps

This pivot can be executed in a phased approach to ensure stability and allow for testing at each stage:

### Phase 1: Backend Restructuring & Ingestion
1. Move the YouTube transcript extraction logic from the Next.js frontend to the FastAPI backend/worker.
2. Create the `Subscription` and `ContentItem` database models using SQLAlchemy.
3. Implement the RSS/YouTube ingestion cron job using a scheduler like `apscheduler` or Celery Beat, integrated with the existing Redis/RQ setup.

### Phase 2: Transcription & Analysis Pipeline
1. Integrate an audio transcription service (e.g., Whisper API) for podcasts and videos without existing captions.
2. Modify the worker tasks to process `ContentItem` records automatically upon ingestion.
3. Adapt the existing prompt profiles to generate concise summaries suitable for a daily digest.

### Phase 3: Delivery & Deployment
1. Develop the report generation logic to aggregate the daily analyses into a single document.
2. Implement the email delivery system using SendGrid to send the "Daily Rip".
3. Update the deployment configuration (Render/Railway/Vercel) to support the new scheduled tasks and worker requirements.

## 4. Summary
The existing ScriptRipper infrastructure is exceptionally well-suited for this pivot. By leveraging the current async worker queue, PostgreSQL database, and LLM abstraction, we can build the "Daily Rip" automation layer efficiently. This will transform the tool from a manual utility into an autonomous knowledge-gathering agent that saves you time.
