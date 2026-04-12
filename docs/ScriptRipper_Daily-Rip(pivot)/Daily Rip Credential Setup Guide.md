# Daily Rip Credential Setup Guide

**Author:** Manus AI
**Date:** April 2026

This document provides step-by-step instructions for manually generating the API keys and connection strings required to run the ScriptRipper "Daily Rip" zero-cost pipeline.

Follow these steps sequentially to populate your local `.env` file before executing the Claude Code build instructions.

---

## 1. Groq (LLM & Transcription)

Groq provides the Llama 3.3 70B model for text analysis and the Whisper Large V3 model for audio transcription. Both are accessed via the same API key [1].

1. Navigate to the **[GroqCloud API Keys Page](https://console.groq.com/keys)** and log in.
2. Click the **Create API Key** button.
3. Name the key "Daily Rip" and click **Submit**.
4. Copy the generated key immediately (it starts with `gsk_`).
5. Add it to your `.env` file:
   ```env
   GROQ_API_KEY=gsk_your_key_here
   ```

## 2. Neon (PostgreSQL Database)

Neon provides serverless PostgreSQL hosting with a generous free tier [2].

1. Navigate to the **[Neon Signup Page](https://console.neon.tech/signup)** and create an account.
2. Click **Create Project**.
3. Name the project "ScriptRipper", select your preferred region, and click **Create Project**.
4. You will be redirected to the project dashboard. A modal will appear with your connection details.
5. Ensure the format is set to **Postgres** (not Prisma or Node.js).
6. Copy the connection string (it starts with `postgresql://`).
7. Add it to your `.env` file:
   ```env
   DATABASE_URL=postgresql://user:password@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

## 3. Upstash (Redis Queue & Cache)

Upstash provides serverless Redis, which is required for the background task queue [3].

1. Navigate to the **[Upstash Console](https://console.upstash.com/)** and log in.
2. Click **Create Database** under the Redis section.
3. Name the database "scriptripper-queue", select a region close to your Neon database, and ensure the "Free" tier is selected. Click **Create**.
4. Once the database is active, scroll down to the **Connect** section.
5. Click the **Redis** tab (not REST or GraphQL).
6. Copy the connection string (it starts with `rediss://`).
7. Add it to your `.env` file:
   ```env
   REDIS_URL=rediss://default:password@endpoint.upstash.io:32000
   ```

## 4. Cloudflare R2 (Object Storage)

Cloudflare R2 provides S3-compatible object storage for archiving the generated Markdown reports without egress fees [4].

1. Navigate to the **[Cloudflare R2 Dashboard](https://dash.cloudflare.com/?to=/:account/r2)**. (You may need to add a payment method to enable R2, but the free tier covers 10GB).
2. Click **Create bucket**. Name it `scriptripper-artifacts` and click **Create**.
3. Go back to the main R2 dashboard and click **Manage R2 API Tokens** (on the right side of the screen).
4. Click **Create API token**.
5. Name it "Daily Rip App".
6. Under Permissions, select **Object Read & Write**.
7. Click **Create API Token**.
8. Copy the Access Key ID, Secret Access Key, and the S3 API Endpoint URL.
9. Add them to your `.env` file:
   ```env
   R2_ACCESS_KEY_ID=your_access_key
   R2_SECRET_ACCESS_KEY=your_secret_key
   R2_ENDPOINT_URL=https://your_account_id.r2.cloudflarestorage.com
   R2_BUCKET_NAME=scriptripper-artifacts
   ```

## 5. Resend (Email Delivery)

Resend handles the delivery of the final Daily Rip email report [5].

1. Navigate to the **[Resend Dashboard](https://resend.com/login)** and log in.
2. Click **API Keys** in the left sidebar, then click **Create API Key**.
3. Name it "Daily Rip", give it **Full Access**, and click **Add**.
4. Copy the key (it starts with `re_`).
5. Add it to your `.env` file:
   ```env
   RESEND_API_KEY=re_your_key_here
   ```
6. **Important:** Before you can send emails, you must verify your sending domain. Click **Domains** in the left sidebar, click **Add Domain**, enter your domain (e.g., `scriptripper.com`), and add the provided DNS records to your domain registrar (e.g., GoDaddy, Namecheap).

## 6. Security Secret

FastAPI requires a secret key to secure the cron endpoint from unauthorized triggers.

1. Open your terminal and run the following command to generate a secure random string:
   ```bash
   openssl rand -hex 32
   ```
2. Copy the output and add it to your `.env` file:
   ```env
   CRON_SECRET_KEY=your_generated_hex_string
   ```

---

## Final `.env` Checklist

Your final `.env` file should look exactly like this:

```env
# Application
ENVIRONMENT=production
CRON_SECRET_KEY=your_generated_hex_string

# Database & Queue
DATABASE_URL=postgresql://...
REDIS_URL=rediss://...

# LLM & Transcription
GROQ_API_KEY=gsk_...

# Storage
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_ENDPOINT_URL=https://...
R2_BUCKET_NAME=scriptripper-artifacts

# Email
RESEND_API_KEY=re_...
FROM_EMAIL=reports@yourdomain.com
```

Once this file is populated and saved in the root of your `ScriptRipper_Re-Do` folder, you are ready to execute the Claude Code build instructions.

---

## References

[1] GroqCloud API Keys. Available: https://console.groq.com/keys
[2] Neon PostgreSQL Signup. Available: https://console.neon.tech/signup
[3] Upstash Redis Console. Available: https://console.upstash.com/
[4] Cloudflare R2 Dashboard. Available: https://dash.cloudflare.com/?to=/:account/r2
[5] Resend Email Signup. Available: https://resend.com/signup
