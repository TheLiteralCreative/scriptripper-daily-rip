# ScriptRipper — What You Told Me You Wanted

*Reconstructed from session log. Your words, my synthesis.*

---

## The One-Word Brief: EASY

You said it twice and meant it both times. Not "simple" as in stripped-down. EASY as in frictionless. A single click — whether that's a browser bookmark or a desktop icon — gets you in. No spinning up servers. No waking up clouds. No ceremony.

The deeper point: if this tool works the way it's supposed to, you barely touch it. You set it up once. You add subscriptions when you want to. After that, it runs. Every day, at a defined time, it does its job and delivers the result to your inbox. You read it, you discard it, and the tool has already archived it in case you need it later. That's the contract. You are not the operator — you are the recipient.

---

## What the Tool Actually Does

ScriptRipper watches a curated list of content sources — RSS feeds, YouTube channels, podcasts, articles — and every day it:

1. Pulls whatever was published
2. Transcribes the audio/video
3. Runs the selected analysis tasks ("rips") against each transcript
4. Assembles the results into structured documents
5. Emails them to you
6. Archives everything

You described the email as a "throw-away document delivered for download, digestion and discard." Not precious. Not permanent. The email is the consumption layer. The archive is the permanent record. That distinction matters for how the output is designed.

---

## The Rip System — What You Actually Said

You don't want a monolithic analysis. You want **modular, selectable tasks** — each one extracting something specific from the source material. A "rip" is a single named task. A "rip profile" is the collection of tasks you've assigned to a given subscription.

You described wanting to pull **multiple documents from a single source** — for example: a broad overview of the full piece, plus a targeted breakdown of one specific element (a step-by-step how-to, a list of actionable items, a set of ideas specifically relevant to you). The same source content, multiple lenses.

You want users — starting with yourself — to be able to look at the available rip library and say: "these are the things I want to know." Checkbox selection. Explicit, intentional choices.

### On the legacy meetings/presentations split

The original tool split everything into two silos — "meetings" (multi-party conversations) and "presentations" (single-sided content like podcasts and YouTube). You said this distinction **may not need to be enforced as an early-stage pipeline gate** in the new version. Your preference: a broad top-of-funnel that accepts everything and figures out how to get *something useful* out of it, rather than routing failures or edge cases into dead ends. Flexibility over rigidity. Get something out of everything.

The legacy prompts are retained in `docs/prompt-archive/` — not as constraints, but as a **starting library and source of inspiration** for the new rip designs.

---

## Favorites and Subscription Setup

When a user wants to add a new subscription, they shouldn't have to configure it from scratch every time. You described a flow:

- User marks certain rips as **Favorites** in their profile
- When setting up a new subscription, an **"Apply Favorite Rips"** button pre-populates the profile
- User can then add or remove rips from the full library (checkbox list) to customize for that specific subscription
- Save and done

Favorites live on the user profile. They're a shortcut, not a lock-in.

---

## Personal Relevance — The Big Vision

This is the part you were most forward-looking about, and it's worth quoting you directly:

> "I'm imagining a way that allows this tool to be used BY a personal Model with insights into the user's habits, interests, and professional profile... By providing access, either through MCP, API, CLI to a user's personal model, their user profile could become a powerful aspect of this already powerful tool by 'knowing the user better than they know themselves' so to speak."

The near-term version: a questionnaire at setup that establishes your interests, professional context, and points of reference. This gets stored as `context_text` on your user profile and gets appended to each rip prompt — adding a "How does this specifically benefit ME?" layer to every output. Additive. Never replaces the base rip. Just makes the result more personally actionable.

The future version: connect a personal AI model (Custom GPT, a Claude project, whatever) via MCP or API. The tool queries your model as part of the rip process. Your model knows you. The rip results reflect that. Personalized recommendations, not generic analysis.

You called this a **"BIG value add"** — both for personal use and as a differentiator if this ever becomes a product.

---

## The Output Structure — Your Exact Design

You laid this out precisely:

**Per subscription, per day:**
- One document
- Uniform header: date, title, source info
- TOC on page one identifying all rips contained within
- Each rip gets its own section

**Per day, across all subscriptions:**
- One **Daily Report** — a master index document
- Lists all subscription documents and their TOCs
- This is what gets emailed

**The archive hierarchy:**
`Date → Subscription → Rip-Spec → Content`

Three levels of reference. The naming convention follows from that hierarchy. The structure of the database mirrors it.

---

## The Interface

You want a GUI. Not instead of the CLI — in addition to it. The CLI is a valid access point and should remain one. But you were clear: a tool that can only be used through the terminal is not meeting the "EASY" standard.

You described **5 surfaces** you need:

1. **Dashboard** — today's report, archive browser
2. **Subscriptions** — add/manage sources, assign rip profiles
3. **Rip Library** — browse all available tasks, mark favorites, preview what each rip produces
4. **User Profile** — questionnaire, personal context, future model connection
5. **Settings** — credentials, delivery preferences, schedule

On the previous UI: "I didn't dislike it, but I believe it can probably be more intuitive or user-friendly based on the elements we've discussed. Optimization is key, but not at the expense of value or usability. Keep it as simple as we can without dumbing it down."

---

## On Building for the Future Without Over-Engineering the Present

You were explicit about this tension. This is a personal tool first. You're not launching a SaaS tomorrow. But:

> "That shouldn't preclude the need for a GUI, and it should not limit the potential of future SaaS-application if our efforts prove successful on the strictly local level."

> "We should plan for that to avoid building ourselves into a 'myopic use-case corner.'"

The instruction: build it for one user (you), but architect it so a second user isn't a rebuild. User IDs on all models. Auth from day one. The seams for multi-tenancy exist even if only one account ever uses them.

---

## On Memory and Continuity

> "EVERY time I use Claude Code, if possible, I'd like you to learn from what we do and retain that knowledge in whatever way suits you and serves the process best. Optimization is what I'm after."

The memory system exists for this reason. Every session should build on the last. No re-deriving context. No hide-and-seek with prior decisions.

---

## What's Already Built (as of 2026-04-12)

- `scriptripper.com` — live, auth page loading, DNS configured on GoDaddy
- Render: API service deployed (`scriptripper-api.onrender.com`), PostgreSQL provisioned, Redis provisioned
- Google OAuth: configured
- Stripe: live keys present
- PurelyMail: configured for `noreply@scriptripper.com`
- Sentry: wired
- All credentials in `vision/scriptripper-api.env` (gitignored)

The existing infrastructure is the foundation. We build on top of it — we don't replace it.
