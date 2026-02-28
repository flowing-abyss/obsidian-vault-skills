---
name: monthly-review
description: "Generates a monthly review block in the monthly note: velocity metrics (notes created, tasks closed, sources processed), thematic analysis (growing vs stagnant categories), stale notes alert (untouched 30+ days in active areas), and project health (projects stuck 2+ weeks). Creates the monthly note if it doesn't exist. INVOKE when the user wants a monthly review or month summary. Triggers: 'monthly review', 'month summary', 'итоги месяца', 'месячный обзор', 'обзор месяца', 'что за месяц'."
---

# Monthly Review

Generates a monthly review without asking questions. Aggregates data across the full month and writes a `[!monthly-review]-` block into the monthly note, then appends a minimal space for the user's own reflections.

## Language Detection

Before generating any content, detect the user's writing language. Read the 5 most recent daily notes (`periodic/daily/YYYY-MM-DD.md`). In non-frontmatter, non-wikilink, non-tag text, count Cyrillic vs Latin characters. If Cyrillic > 30% → write the entire review in Russian. Otherwise → English.

Apply to ALL section headers, metric labels, inference lines (→), and participation prompts. Callout types and wikilinks remain unchanged regardless of detected language.

## Monthly Note Format

**Path:** `periodic/monthly/YYYY-MM.md`

**Compute parent quarter** (cross-platform, using `obsidian eval`):
```bash
obsidian eval code="const d=new Date();const q=Math.ceil((d.getMonth()+1)/3);d.getFullYear()+'-Q'+q"
# output: 2026-Q1
```

**Frontmatter (exact from template):**
```yaml
---
tags:
  - periodic/month
up:
  - "[[periodic/quarterly/YYYY-QN|YYYY-QN]]"
created: YYYY-MM-DDTHH:mm:ssZ
updated: YYYY-MM-DDTHH:mm:ssZ
reviewed: false
cssclasses:
  - hide-backlinks
---

> [!success]- 🔻 history 🔻
> `$=await dv.view("templates/views/periodic", {type: "week"})`
```

If the monthly note already exists — find `[!monthly-review]-` and replace it. Otherwise create with the template above, then append the review block after `[!success]-`.

## Execution Flow

```
User: "monthly review" / "итоги месяца" / "месячный обзор"
    |
1. Determine current month (YYYY-MM) and its date range
    |
2. Find or create periodic/monthly/YYYY-MM.md
    |
3. Detect language from last 5 daily notes
    |
4. Gather IN PARALLEL:
   a. Velocity — count notes, tasks, sources from this month
   b. Planned vs actual — read user-written sections from this month's weekly notes
   c. Thematic analysis — wikilink frequency in weekly reviews + daily notes
   d. Stale notes — find notes not updated 30+ days in hot categories
   e. Project health — find projects stuck 14+ days without update
    |
5. For each section: collect data → derive one "→" inference from the specific pattern
    |
6. Write [!monthly-review]- callout into monthly note
    |
7. Append user participation section below the callout (outside it)
    |
8. Minimal chat confirmation
```

## Velocity

Count activity created or completed during YYYY-MM.

### Notes created
```bash
obsidian search query="[created: YYYY-MM]" path=base/notes total    # notes in base/notes
obsidian search query="[created: YYYY-MM]" path=base/additions total  # notes in additions
```

*Notes created = new ideas that made it into the knowledge base this month — the output side of the system.*

### Tasks closed
```bash
obsidian search query="✅ YYYY-MM" total  # count lines with completion marker for this month
```

*Tasks closed = completed actions tracked in the GTD system. Not emails, not informal to-dos — only tasks in the vault.*

### Sources processed
```bash
obsidian search query="[status: 🟩] [end: YYYY-MM]" path=sources total
```

*Sources processed = books, articles, videos, courses, etc. marked as finished (status: 🟩 + end date set). These are inputs to the system.*

Format:

```markdown
> **Velocity:**
> - Notes created: 14 (base/notes: 11, additions: 3)
> - Tasks closed: 47
> - Sources processed: 6
```

**→ Inference:** After collecting velocity, derive one data-specific observation. Look for:
- Sources >> Notes: consuming more than synthesizing — knowledge accumulates but isn't being processed
- Notes >> Sources: actively building the knowledge base from internal thinking or previous material
- Low across all three: rest month, or was something blocking the system?
- Compare to previous month if its `[!monthly-review]-` block is available — show delta

Write the inference in detected language. Skip if no clear pattern.

## Planned vs Actual

Read the user-written sections from this month's weekly notes. Specifically: text BELOW the `[!weekly-review]-` callout block in each of the month's weekly notes (typically 4–5 notes). This is what the user wrote as their own focus and reflections after each weekly review.

Look for:
- "Focus for next week:" / "Фокус на следующую неделю:" entries
- Any stated goals or intentions written below the callout

Cross-reference with what actually happened (velocity data, themes, project progress).

```markdown
> **Planned vs Actual:**
> - Stated: focus on [[writing process]], finish [[Blog Draft]]
> - Actual: [[learning systems]] dominated (14 refs), [[Blog Draft]] still 🟦
> - Unplanned: [[productivity systems]] emerged mid-month
```

If no user-written sections found in any weekly notes — write:
```markdown
> **Planned vs Actual:** No weekly focus recorded this month. Write your focus after each weekly review — it will feed this section next month.
```

**→ Inference:** Was the drift from the stated focus intentional (genuine reprioritization) or reactive (distraction, events)? A large gap between planned and actual with no explanation in the user's notes is a signal worth examining.

Write the inference in detected language. Skip this "→" if no stated focus existed.

## Thematic Analysis

Identify which knowledge areas received attention and which were ignored.

### What grew
Aggregate all wikilinks from this month's weekly notes (`periodic/weekly/YYYY-W*.md` where the week falls within the month) and the month's daily notes. Count frequency of links to:
- `base/_meta-notes/`
- `base/notes/`

Top 3–5 by mention count = **growing** categories.

### What stagnated
Cross-reference: take meta-notes that were active in the **previous month's** weekly reviews but absent this month. If no previous month data exists — skip stagnation, only show growth.

```markdown
> **Themes:**
> - Growing: [[writing process]] (18), [[learning systems]] (11), [[productivity]] (7)
> - Stagnating: [[computer science]], [[economics]] — active last month, 0 mentions now
```

If no previous month data — show only "Growing:" line.

**→ Inference:** After listing themes, derive one data-specific observation. Look for:
- Multiple themes growing simultaneously → broad sprint or scattered focus — is depth happening anywhere?
- A theme grew in mentions but no new note was created → reading/thinking without writing
- A theme the user said they wanted to focus on (from weekly focus sections) ended up stagnating → it's harder than expected
- Only 1 theme active → intense focus, or are other areas being neglected?

Write the inference in detected language. Skip if no clear pattern.

## Stale Notes Alert

Surface notes in currently-active knowledge areas that haven't been touched in 30+ days.

### Process
1. Take the top 3 growing themes from Thematic Analysis (the hot meta-notes/categories this month)
2. For each: find notes that link to it (via wikilinks or `up:` frontmatter)
3. Filter: keep only notes where `updated:` frontmatter is older than 30 days from today
4. Sort by `updated:` date ascending (oldest first)
5. Show up to 3 per theme, max 9 total

```markdown
> **Stale notes:**
> - [[note about topic X]] — last updated 2025-11-14 (97 days)
> - [[another relevant note]] — last updated 2025-12-03 (78 days)
> - [[old concept note]] — last updated 2026-01-02 (48 days)
```

*These notes live in your most active knowledge areas but haven't been touched in over a month. They may contain outdated thinking, or untapped connections to your recent work.*

**→ Inference:** Stale notes in hot categories mean attention is flowing into the area but not reaching the existing knowledge base. Worth asking: are these notes complete and filed, outdated and needing revision, or simply forgotten?

If nothing stale in active areas — skip section silently.

## Project Health

Find projects that may be stuck or neglected.

### Stuck projects
```bash
obsidian search query="[status: 🟦]" path=projects  # in-progress projects
obsidian search query="[status: 🟥]" path=projects  # planned projects
# Then filter by updated: frontmatter date — keep only those 14+ days before today
```

For each stuck project: show name, status, and how many days since last update.

### Dormant projects
Projects with `status: 🟥` (planned) that have `created:` older than 30 days and no recent mentions in daily or weekly notes. Use `obsidian search query="[status: 🟥]" path=projects` then filter by `created:` date.

```markdown
> **Project health:**
> - [[Long-form Essay Collection]] 🟦 — no update for 23 days
> - [[Home Lab Documentation]] 🟦 — no update for 41 days
> - [[Course Outline Draft]] 🟥 — planned 35 days ago, never started
```

**→ Inference:** After listing, derive one data-specific observation. Look for:
- Project stuck 30+ days: is it genuinely in progress or silently abandoned?
- Dormant backlog growing: planning without execution — the gap between intention and action
- All projects updated recently: healthy execution pace — worth noting

Write the inference in detected language. If all projects were updated recently — write: `All active projects updated within 14 days.` (in detected language)

## Output Format

Full callout written into monthly note:

```markdown
> [!monthly-review]- Monthly review — YYYY-MM
> **Velocity:**
> - Notes created: N (base/notes: N, additions: N)
> - Tasks closed: N
> - Sources processed: N
> → [inference about velocity balance — only if clear pattern]
>
> **Planned vs Actual:**
> - Stated: ...
> - Actual: ...
> → [inference about gap — only if stated focus existed]
>
> **Themes:**
> - Growing: [[theme-a]] (N), [[theme-b]] (N)
> - Stagnating: [[theme-c]], [[theme-d]]
> → [inference about attention pattern — only if clear pattern]
>
> **Stale notes:**
> - [[note title]] — last updated YYYY-MM-DD (N days)
> → [inference about knowledge base freshness]
>
> **Project health:**
> - [[Project Name]] 🟦 — no update for N days
> → [inference about execution pattern — only if clear pattern]
```

**Rules:**
- Write into note — never just output to chat
- Collapsed by default (`-` suffix on callout)
- Callout title includes month: `[!monthly-review]- Monthly review — 2026-02`
- All labels translated to detected language
- Skip sections with no content — don't write empty headers
- Skip "→" inference lines where no clear pattern exists — never write generic lines
- Every reference = `[[wikilink]]`, never vague filenames or paths

## User Participation Sections

After the `[!monthly-review]-` callout, appended **outside it** (in the note body), with a horizontal rule separator:

**Default form (always):**
```markdown
---
**Мои выводы / My conclusions:**

**Фокус на следующий месяц / Focus for next month:**
```

**Extended form (when review data shows a specific sharp pattern):**
```markdown
---
*[One direct question from the review's most significant finding — e.g., "[[learning systems]] вытеснил запланированный фокус — это новый приоритет или отклонение?" / "Did [[learning systems]] replace your planned focus, or is this a new priority?"]*

**Мои выводы / My conclusions:**

**Фокус на следующий месяц / Focus for next month:**
```

Write the italic question in detected language. Use extended form only when a pattern is unambiguous.

**Note:** The "Focus for next month" section is read by the quarterly-review skill when computing Planned vs Actual.

## Chat Output

After writing, confirm minimally:

```
Review written → periodic/monthly/2026-02.md

Velocity: 14 notes, 47 tasks, 6 sources.
Themes: writing process (18), learning systems (11).
Stale: 3 notes.
Projects: 2 stuck, 1 dormant.
```

If the note was created — first line: `Created periodic/monthly/2026-02.md + review.`
Adapt language of confirmation to match detected language.
