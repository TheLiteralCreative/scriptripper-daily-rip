# Tightened Prompts (JSON + website description)

*Below are nine of the most critical/overlapping prompts, fully tightened. (If this direction matches your intent, I’ll apply the same treatment to the remaining nine.)*

## A) Action Items Tracker (merged)
{
  "task_name": "Action Items Tracker",
  "prompt": "**1. Role & Goal:** Act as a diligent project coordinator to build a live Action Item Tracker that captures all actionable tasks and their current status.\n\n**2. Core Instruction:** Scan the full transcript and extract every explicit action item (assigned tasks, requests with owners, or commitments). For each item, infer its current status from surrounding language. Normalize owner names to the exact spoken form. If a due date is explicitly stated, capture it; if only relative (e.g., \"next Friday\"), leave blank rather than guessing.\n\n**3. Formatting Constraints:** Output MUST be a Markdown table with exactly these columns, in order: 'Task' | 'Assigned To' | 'Due Date' | 'Status'. Allowed 'Status' values: 'New' | 'In Progress' | 'Completed' | 'Blocked'. Use YYYY-MM-DD when a specific date is stated; otherwise leave blank. Sort rows by Due Date (soonest first), then Task alphabetically.\n\n**4. Negative Constraints:** If no action items are found, respond with exactly: `No action items identified in this section.` Output ONLY the table or the fallback phrase."
}

### Website description
What: Finds every concrete to-do with owner, due date, and live status.
Why: Turns talk into accountable work—no loose ends.
How: 4-column table (Task, Assigned To, Due Date, Status) with status inferred from context; sorted by due date.
Who: PMs and team leads handing off to Jira/Asana.

## B) Key Decisions Log (with Top 3)
{
  "task_name": "Key Decisions Log",
  "prompt": "**1. Role & Goal:** Act as a meticulous record-keeper and analyst. Capture final decisions and synthesize their strategic significance.\n\n**2. Core Instruction:** First extract all final decisions explicitly agreed by participants. Then, derive 'Top 3 Takeaways' strictly from those decisions—do not use other transcript content.\n\n**3. Formatting Constraints:**\n**Section 1 - Key Decisions Log:** numbered list; each item states the decision and who made the final call or who agreed.\n**Section 2 - Top 3 Takeaways:** add a Level 3 heading '### Top 3 Takeaways from Decisions' followed by a numbered list of exactly three takeaways derived only from Section 1.\n\n**4. Negative Constraints:** Exclude options discussed but not chosen. Takeaways must reference only decisions listed in Section 1."
}

### Website description
What: Logs every final decision and distills the three biggest implications.
Why: Locks alignment and momentum.
How: Numbered decision list with owners → “Top 3 Takeaways” derived only from those decisions.
Who: Execs/PMs who need crisp outcomes.

## C) Client Expectations Report
{
  "task_name": "Client Expectations Report",
  "prompt": "**1. Role & Goal:** Act as a client relationship manager and behavioral analyst.\n\n**2. Core Instruction:** Capture explicit delivery expectations, implicit relational expectations, and assess perceived emotional state—each supported by evidence from the transcript.\n\n**3. Formatting Constraints:** Use Level 3 headings exactly:\n### Explicit Expectations (To-Dos)\n### Implicit Expectations (Relational)\n### Client's Perceived Emotional State\nUnder 'Explicit', bullet concrete tasks/deliverables/deadlines. Under 'Implicit' and 'Emotional State', justify each point with a direct quote or specific example (include speaker/timestamp if present).\n\n**4. Negative Constraints:** Output ONLY the report sections. Do not add filler."
}

### Website description
What: Pulls the client’s concrete asks, unspoken relational signals, and emotional tone.
Why: Prevents misalignment and surprise escalations.
How: Three sections with justification quotes/examples.
Who: Account managers & consultants.

## D) Friction & Foresight Report
{
  "task_name": "Friction & Foresight Report",
  "prompt": "**1. Role & Goal:** Act as an experienced mediator and strategic advisor.\n\n**2. Core Instruction:** Provide (1) explicitly stated disagreements/open loops and (2) predicted future friction based on perspectives/subtext. Each point must include a concrete, actionable advice line.\n\n**3. Formatting Constraints:** Use exactly:\n### Current Disagreements & Open Loops\n### Potential Future Friction Points\nUnder each, bullets in the form: '- <issue>. (<people involved>). **Advice:** <actionable step>'.\n\n**4. Negative Constraints:** Output ONLY the report. If no issues, respond exactly: `No significant disagreements or risks identified.`"
}

### Website description
What: Flags current disputes and likely flashpoints—each paired with advice.
Why: Defuses risk early.
How: Two sections, bulleted issues with people + bold Advice.
Who: Facilitators, product leads, client services.

## E) Communication Insights (Start–Stop–Continue)
{
  "task_name": "Communication Insights (SSC)",
  "prompt": "**1. Role & Goal:** Act as an expert communications consultant and strategic coach.\n\n**2. Core Instruction:** (1) Analyze communication styles, dynamics, and subtext. (2) Produce a Start–Stop–Continue plan strictly tied to those insights.\n\n**3. Formatting Constraints:**\n### Key Communication Insights\n- Bullet each insight and justify with a specific example or quote (include speaker/timestamp when available).\n\n### Strategic Action Plan (Start-Stop-Continue)\n- **Start:** 1–3 concrete actions tied to insights.\n- **Stop:** 1–3 behaviors to discontinue, tied to insights.\n- **Continue:** 1–3 effective behaviors to maintain, tied to insights.\n\n**4. Negative Constraints:** No generic advice; every recommendation must trace to a specific evidenced insight."
}

### Website description
What: Surfaces team dynamics and turns them into a Start–Stop–Continue plan.
Why: Improves collaboration and cuts repeat misfires.
How: Evidence-backed insights + targeted actions mapped one-to-one.
Who: Team leads, coaches, client managers.

## F) Full Record Markdown (verbatim formatter)
{
  "task_name": "Full Record Markdown",
  "prompt": "**1. Role & Goal:** Act as a document formatter to re-render the transcript as a complete Markdown document.\n\n**2. Core Instruction:** Rewrite the entire transcript verbatim (wording preserved) into a single Markdown file with structure (title, meta, sections by timestamps).\n\n**3. Formatting Constraints:** Begin with an H1 title, then a meta line (date, participants if present). Use H2 headings for major time blocks; preserve speaker names and timestamps.\n\n**4. Negative Constraints:** Output ONLY the formatted Markdown. No commentary."
}

### Website description
What: Converts raw transcript into clean, shareable Markdown.
Why: Makes long notes readable and navigable.
How: H1 + meta + H2 sections by time; speakers/timestamps preserved.
Who: Ops teams, archivists, minute-takers.

## G) Timestamped Outline & Recipes (merged Deep + Expanded)
{
  "task_name": "Timestamped Outline & Recipes",
  "prompt": "**1. Role & Goal:** Act as a technical analyst/writer to produce a comprehensive, standalone Markdown outline so users can capture details without watching the source.\n\n**2. Core Instruction:** Transform the entire transcript into a detailed, multi-section outline following the talk’s logical flow. After the outline, add optional sections only if supported: 'Quick Process Recipes', 'Stand-out Quote', 'Call to Action', 'Top 3 Takeaways'.\n\n**3. Formatting Constraints:** H1 title is the video title. Provide a bold meta line with Speaker, Published Date (today’s date), and estimated Run-time. Main section headings are H2 'HH:MM–HH:MM Descriptive Title'. Under each, list concrete details as '-' bullets (definitions, stats, pros/cons, code), using code blocks where relevant. 'Quick Process Recipes' is a Markdown table with columns: | Task | Timestamp | Steps |. 'Top 3 Takeaways' is a numbered list.\n\n**4. Negative Constraints:** Preserve original wording for quotes/commands/statistics. Output ONLY the Markdown; omit optional sections when not present."
}

### Website description
What: Full, timestamped outline with optional recipes/CTA/quotes/takeaways.
Why: Lets readers grasp everything fast without the video.
How: H1 + bold meta; H2 time ranges; dense bullets; recipes table.
Who: Content editors, enablement teams, note-takers.

## H) Audience Activation Artifacts
{
  "task_name": "Audience Activation Artifacts",
  "prompt": "**1. Role & Goal:** Act as a versatile content strategist and creator; repurpose core ideas into platform-ready artifacts.\n\n**2. Core Instruction:** Analyze the full transcript and generate only the artifact types supported by content; rephrase/reformat for the new context (no copy-paste except natural quotes).\n\n**3. Formatting Constraints:** Use Level 3 headings for each produced type with these titles: 'Tweet length takeaways', 'Social Snippets', 'Slide ready bullet lists', 'FAQ Pairs', 'Reflection Prompts', 'Journaling Questions', 'Coaching deliverables', 'Resource list', 'KPI / Metric Formulas', 'Dashboards'. Tweets: 2–3 items ≤280 chars with hashtags. FAQ: '**Q:**' / '**A:**' lines. Slides: concise, titled list. Resource list: clean bullets. Coaching: small exercise/checklist.\n\n**4. Negative Constraints:** Omit unsupported categories entirely. Ensure all content is transcript-inspired and tailored; no filler."
}

### Website description
What: Spins the talk into tweets, social snippets, slide bullets, FAQs, exercises, and more.
Why: Extends reach across channels with zero extra drafting.
How: Strict headings; platform-ready formats (tweets, Q&A, lists, KPIs).
Who: Creators, marketers, coaches.

## I) Tutorial How-To Extractor
{
  "task_name": "Tutorial Step-Down & Actionable How-To Extractor",
  "prompt": "**1. Role & Goal:** Act as a precise tutorial extractor/editor; convert how-to/workflow segments into executable steps a novice can follow.\n\n**2. Core Instruction:** Process the full transcript to detect distinct tutorials. For each: (a) title; (b) prerequisites; (c) numbered steps with Do/Why/Expected Result; (d) inputs/variables table; (e) validation checklist; (f) pitfalls/troubleshooting/variations if present. Preserve meaning; expand compressed steps; note '(Reordered for clarity)' if you reorder. Include brief verbatim evidence quotes with timestamps where available.\n\n**3. Formatting Constraints:** Emit one or more tutorial blocks in transcript order, each with EXACT sections: '# Tutorial: <name>' → '## Summary' → optional '## Prerequisites' → optional '## Inputs & Variables (Table)' (| Name | Type | Source | Example | Notes |) → '## Step-by-Step Instructions' (with Action/Why/Expected Result/Evidence/Command mini-schema) → optional '## Node Parameters (Table)' (| Node | Parameter | Value | Where Set (UI path) | Notes |) → '## Validation Checklist' (fallback line 'No validation steps were stated.' if none) → optional '## Common Pitfalls' → optional '## Troubleshooting' → optional '## Variations & Extensions' → optional '## References'.\n\n**4. Negative Constraints:** If no actionable tutorial content exists, output ONLY: \"No actionable tutorial content found in this transcript.\" If a tutorial lacks concrete steps, in its 'Step-by-Step Instructions' output ONLY: \"No steps could be extracted.\" Omit optional headings when empty; never invent URLs, credentials, or secrets."
}

### Website description
What: Converts tutorials hidden in the talk into step-by-step guides with inputs, parameters, and validation.
Why: Saves hours turning videos into docs novices can execute.
How: One or more blocks with tables, checklists, quotes+timestamps, troubleshooting.
Who: Educators, dev-tool instructors, enablement.

## J) Important Quotes
{
  "task_name": "Important Quotes",
  "prompt": "**1. Role & Goal:** Act as a journalist capturing the most impactful statements.\n\n**2. Core Instruction:** Identify 3–5 of the most significant, insightful, or impactful quotes that capture the essence of the conversation. Quotes must be verbatim.\n\n**3. Formatting Constraints:** Output as bullets. For each, bold the timestamp (if present), include the speaker's name, then the verbatim quote text.\n\n**4. Negative Constraints:** If no valid quotes are found, respond exactly: `No significant quotes identified in this section.` Output ONLY the quotes or the fallback phrase."
}

### Website description
What: Pulls the 3–5 lines that matter most—word-for-word.
Why: Preserves pivotal moments for sharing and follow-up.
How: Bulleted items with bold timestamps, speaker, and exact quote.
Who: Execs, comms, and enablement teams.

## K) Participants & Roles
{
  "task_name": "Participants & Roles",
  "prompt": "**1. Role & Goal:** Act as a meticulous meeting administrator whose sole job is to identify participants.\n\n**2. Core Instruction:** List every unique person speaking or mentioned by name. Include role only if explicitly stated.\n\n**3. Formatting Constraints:** Simple bulleted list. Use EXACT formats: '- **[Name]** ([Role])' if role known; else '- **[Name]**'. Alphabetize by last name when available; otherwise by first name.\n\n**4. Negative Constraints:** If no participants or roles are mentioned, respond exactly: `No participants identified in this section.` Output ONLY the list or the fallback phrase."
}

### Website description
What: Identifies everyone involved and their roles (when stated).
Why: Helps teams map stakeholders fast.
How: Clean, alphabetized bullets in a fixed format.
Who: Coordinators, assistants, onboarding users.

## L) Content Nuggets
{
  "task_name": "Content Nuggets",
  "prompt": "**1. Role & Goal:** Act as a knowledge management specialist and content curator extracting self-contained, reusable 'nuggets'.\n\n**2. Core Instruction:** Scan the entire transcript for the nugget categories listed under 'CONTENT NUGGETS TO EXTRACT'. Group extracted nuggets by category; ensure each is understandable without outside context.\n\n**3. Formatting Constraints:** Use a Level 3 heading (###) for each category found. Under each, list bullets as: '- **[Nugget Name]:** \"[Direct quote or detailed summary]\" (Context: <why/when it matters>)'.\n\n**4. Negative Constraints:** Omit categories with no findings. Focus on concrete, specific information; avoid vague statements."
}

### Website description
What: Harvests high-value tidbits—tools, stats, steps, frameworks, lessons.
Why: Makes insights portable for docs, posts, and training.
How: Categorized bullets with a brief context note.
Who: Content ops, enablement, knowledge bases.

## M) Relationship & Dependency Map
{
  "task_name": "Relationship & Dependency Map",
  "prompt": "**1. Role & Goal:** Act as a systems thinker and strategic analyst mapping the internal logic of the transcript.\n\n**2. Core Instruction:** Identify explicit or strongly implied relationships among concepts, tools, and ideas, grouped under: Concept Dependencies; Comparisons / Alternatives; Cross-References; Evolving Sequences / Roadmaps.\n\n**3. Formatting Constraints:**\n- **Concept Dependencies:** '**[B]** *depends on* **[A]** — <quote/explanation>'.\n- **Comparisons / Alternatives:** Use a Markdown table if pros/cons are stated; otherwise concise bullets.\n- **Cross-References:** Bullet the referenced work/person + context.\n- **Evolving Sequences / Roadmaps:** Numbered list of phases/milestones.\n\n**4. Negative Constraints:** Map only explicitly stated or strongly implied links. Omit headings with no findings."
}

### Website description
What: Shows how ideas and tools connect and in what order.
Why: Prevents mis-sequencing and clarifies choices.
How: Dependency statements, comparison tables, references, and roadmaps.
Who: Architects, curriculum designers, strategists.

## N) Structural & Contextual Metadata
{
  "task_name": "Structural & Contextual Metadata",
  "prompt": "**1. Role & Goal:** Act as a data librarian and content strategist extracting a structured 'data header' for archival and discovery.\n\n**2. Core Instruction:** From the metadata block and transcript content, identify the requested fields and mark missing items clearly.\n\n**3. Formatting Constraints:** Output a bulleted key-value list using EXACT field names: Video Title; URL; Channel / Speaker(s); Credibility & Future Filtering; Publish Date; Key Segment Timestamps; Audience Level; Primary Topic Tags; Format Type; Visual References.\n\n**4. Negative Constraints:** If a field cannot be found or reasonably inferred, write 'Not available'. Do not fabricate."
}

### Website description
What: Builds a complete metadata header for discovery.
Why: Improves search, filtering, and reuse.
How: Fixed key-value bullets with “Not available” where missing.
Who: Librarians, SEO & content ops.

## O) Quality & Credibility Signals
{
  "task_name": "Quality & Credibility Signals",
  "prompt": "**1. Role & Goal:** Act as a critical analyst and fact-checker evaluating quality, credibility, and potential bias from transcript evidence.\n\n**2. Core Instruction:** Produce a 'Credibility Report' for: Speaker credentials; Evidence type; Consensus level; Bias indicators / sponsorship disclosures. Support every assessment with transcript evidence.\n\n**3. Formatting Constraints:** For each signal, use a Level 3 heading. Then provide '**Assessment:** <direct statement>' followed by '- **Evidence:** <direct quote or specific summary>'. If no evidence, state 'No direct evidence found in transcript.'\n\n**4. Negative Constraints:** No external knowledge or assumptions; base everything solely on the transcript."
}

### Website description
What: Scores expertise, evidence style, consensus, and bias.
Why: Reduces risk of amplifying weak or sponsored content.
How: Bold assessments backed by quotes; flags missing evidence.
Who: Editors, educators, researchers.

## P) Processing Health Check
{
  "task_name": "Processing Health Check",
  "prompt": "**1. Role & Goal:** Act as a quality assurance analyst producing a meta-analysis of the transcript's suitability for structured extraction.\n\n**2. Core Instruction:** Generate a report covering: Overall Extraction Confidence; Redundancy Detection; Sentiment / Tonality; Language Complexity Rating.\n\n**3. Formatting Constraints:** Use Level 3 headings for each check. Provide a direct assessment followed by a 1–2 sentence justification with examples when appropriate.\n\n**4. Negative Constraints:** Keep analysis objective and pattern-based; avoid editorializing beyond text support."
}

### Website description
What: Rates how cleanly the transcript can be mined.
Why: Guides whether to trust outputs or request a redo.
How: Four brief assessments with justifications.
Who: Ops/QA managing transcript pipelines.

## Q) One-Paragraph Summary
{
  "task_name": "One-Paragraph Summary",
  "prompt": "**1. Role & Goal:** Act as an executive assistant creating a concise summary for a busy stakeholder.\n\n**2. Core Instruction:** Produce one dense paragraph covering the meeting/presentation purpose, core problems, key decisions, and overall outcome—based solely on the transcript.\n\n**3. Formatting Constraints:** Output must be exactly one paragraph of prose.\n\n**4. Negative Constraints:** If no substantive points exist, respond exactly: `No summary points identified in this section.` Output ONLY the paragraph or the fallback phrase."
}

### Website description
What: Compresses the whole talk into one tight paragraph.
Why: Saves leaders time without losing the plot.
How: Purpose, problems, decisions, outcome in dense prose.
Who: Executives and sponsors.

## R) Overview Summary
{
  "task_name": "Overview Summary",
  "prompt": "**1. Role & Goal:** Act as an analyst preparing a 1–2 page executive briefing.\n\n**2. Core Instruction:** Create a comprehensive overview covering agenda/purpose, core problems and solutions, major debates, and final outcomes including key decisions and action items.\n\n**3. Formatting Constraints:** Write well-structured prose organized into logical paragraphs (not bullets) that read as a formal summary report.\n\n**4. Negative Constraints:** If no substantive points exist, respond exactly: `No summary points identified in this section.` Output ONLY the summary or the fallback phrase."
}

### Website description
What: Narrative brief from purpose to outcomes.
Why: Gives decision-makers full context without noise.
How: Multi-paragraph prose covering problems/solutions, debates, and results.
Who: Execs and PMOs.
