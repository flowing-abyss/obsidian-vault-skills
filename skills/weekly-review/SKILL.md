---
name: weekly-review
description: "Generates a weekly review block in the weekly note: completed tasks, hot themes from daily notes, active project progress, unresolved threads, and 2 reflection questions. Creates the weekly note if it doesn't exist. INVOKE when the user wants a weekly review or week summary. Triggers: 'weekly review', 'week summary', 'итоги недели', 'недельный обзор', 'обзор недели', 'что за неделю'."
---

# Weekly Review

Generates a weekly review without asking questions. Scans vault data and writes a `[!weekly-review]-` block into the weekly note, then appends a minimal space for the user's own reflections.

## Language Detection

Before generating any content, detect the user's writing language. Read the 5 most recent daily notes (`periodic/daily/YYYY-MM-DD.md`). In non-frontmatter, non-wikilink, non-tag text, count Cyrillic vs Latin characters. If Cyrillic > 30% → write the entire review in Russian. Otherwise → English.

Apply to ALL section headers, metric labels, inference lines (→), and participation prompts. Callout types (`[!weekly-review]`) and wikilinks remain unchanged regardless of detected language.

## Weekly Note Format

**Path:** `periodic/weekly/YYYY-WWW.md`

**Compute week and parent month** (cross-platform, using `obsidian eval`):
```bash
# Current ISO 8601 week e.g. 2026-W08
obsidian eval code="(function(){const d=new Date();const dt=new Date(Date.UTC(d.getFullYear(),d.getMonth(),d.getDate()));const day=dt.getUTCDay()||7;dt.setUTCDate(dt.getUTCDate()+4-day);const y=dt.getUTCFullYear();const ys=new Date(Date.UTC(y,0,1));const w=Math.ceil(((dt-ys)/86400000+1)/7);return y+'-W'+String(w).padStart(2,'0')})()"

# Parent month e.g. 2026-02
obsidian eval code="const d=new Date();d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')"
```

**Frontmatter (exact from template):**
```yaml
---
tags:
  - periodic/week
up:
  - "[[periodic/monthly/YYYY-MM|YYYY-MM]]"
created: YYYY-MM-DDTHH:mm:ssZ
updated: YYYY-MM-DDTHH:mm:ssZ
reviewed: false
cssclasses:
  - hide-backlinks
---

> [!success]- 🔻 history 🔻
> `$=await dv.view("templates/views/periodic", {type: "day"})`
```

If the weekly note already exists — find the `[!weekly-review]-` block and replace it. Otherwise create the note with the template above, then append the review block after `[!success]-`.

## Execution Flow

```
User: "weekly review" / "итоги недели" / "недельный обзор"
    |
1. Compute current ISO week (YYYY-WWW) and date range Mon–Sun
    |
2. Find or create periodic/weekly/YYYY-WWW.md
    |
3. Detect language from last 5 daily notes
    |
4. Read 7 daily notes for Mon–Sun (skip missing days silently)
   Also extract: free-text user writing in each note (content OUTSIDE [!briefing]- callout,
   not task lines, not pure wikilinks — what the user actually wrote themselves)
    |
5. Gather IN PARALLEL:
   a. Completed tasks — CLI: obsidian tasks done / obsidian search query="✅ YYYY-MM"
   b. Themes — count wikilinks across daily notes
   c. Project progress — read active projects via obsidian search + mentions in daily notes
   d. Open threads — extract Threads sections from briefing callouts
   e. Journal patterns — aggregate free-text themes from user writing in daily notes
    |
6. For each section: collect data → derive one "→" inference from the specific pattern
    |
7. Generate review callout with inferences
    |
8. Write [!weekly-review]- callout into weekly note
    |
9. Append user participation section below the callout (outside it)
    |
10. Minimal chat confirmation
```

## Completed Tasks

**Search entire vault** for tasks completed this week:
```bash
obsidian tasks done format=json                    # all done tasks with metadata
obsidian search query="✅ YYYY-MM" path=periodic  # count by month (scoped to periodic notes)
```
Filter: keep only lines where ✅ date falls within Mon–Sun of current week

Extract human-readable task text: strip `- [x]`, `#task/*`, `#category/*`, `#priority/*`, and all emoji date markers (`📅`, `⏰`, `✅ YYYY-MM-DD`). Keep only the description.

List as plain bullets with abbreviated weekday (Mon/Tue/Wed/Thu/Fri/Sat/Sun in English, пн/вт/ср/чт/пт/сб/вс in Russian):

```markdown
> **Completed tasks (5):**
> - Write chapter outline for the longform project — Mon
> - Set up automated backup script — Wed
> - Publish draft article — Fri
```

**Never duplicate task markdown** — no `- [x]`, no tags, no emoji. Only the human-readable description + day.

**→ Inference:** After listing tasks, derive one data-specific observation. Look for:
- Tasks clustered on 1–2 days → what blocked the other days?
- One task category dominates (all admin, all writing) → imbalance or intentional sprint?
- Fewer tasks than usual → rest week or something blocked execution?
- Many tasks completed but no project progress → lots of action, little forward movement

Write the inference in detected language. Skip if no clear pattern.

If nothing found — skip section silently.

## Hot Themes

Parse all wikilinks from the 7 daily notes. Count frequency of links pointing to:
- `base/_meta-notes/`
- `base/notes/`

Show top 3–5 by count. Skip structural navigation links (monthly, weekly, project index pages).

```markdown
> **Hot themes:**
> - [[knowledge management]] — 6 mentions
> - [[writing process]] — 4 mentions
> - [[productivity systems]] — 2 mentions
```

**→ Inference:** After listing themes, derive one data-specific observation. Look for:
- Top theme mentioned 4+ times but no new note created this week → thinking without writing
- Many themes at low count (all 2–3) → scattered attention, no single focus this week
- One theme dominates (>50% of all mentions) → deep dive or tunnel vision?
- Theme appears only in the last 2 days → momentum building that could carry into next week

Write the inference in detected language. Skip if no clear pattern.

## Journal Patterns

Read free-text content in each daily note — text that is NOT inside the `[!briefing]-` callout, NOT task lines (`- [ ]` / `- [x]`), and NOT pure wikilink lists. This is what the user wrote themselves: observations, thoughts, diary entries.

If a concept, concern, or question recurs in user-written text across 3+ different days — surface it as a pattern:

```markdown
> **Journal pattern:**
> You kept returning to [topic/concept] across N days — no note yet, but the thinking is accumulating.
```

Skip this section if:
- The user wrote very little free text this week
- No pattern across multiple days is visible
- The pattern duplicates what's already captured in Hot Themes

Do not quote raw journal text. Only summarize the pattern.

## Project Progress

1. `obsidian search query="[status: 🟦]" path=projects` and `obsidian search query="[status: 🟥]" path=projects` → list active projects
2. For each project, search its title in the 7 daily notes via `obsidian search:context query="[[Project Name]]" path=periodic/daily`
3. Extract: decisions made, blockers, progress, next steps from those mentions
4. Write as narrative: status emoji + 1 sentence of what happened this week

```markdown
> **Projects:**
> - [[Personal Blog Relaunch]] 🟦 — drafted two new posts, design still blocked
> - [[Note-taking Workflow v2]] 🟦 — finalized the capture stage, review stage pending
> - [[Podcast Pilot Episode]] 🟥 — no progress this week
```

If a project had no mentions this week — include with status only, no narrative.

**→ Inference:** After listing projects, derive one data-specific observation. Look for:
- Same blocker mentioned 2+ weeks running → the blocker is the real issue, not the project
- Only one project received attention → others are being starved
- Project had no progress but was active the previous week → what interrupted it?

Write the inference in detected language. Skip if no clear pattern.

## Open Threads

Extract `**Threads:**` section from `[!briefing]-` callouts in each of the 7 daily notes.

A thread is "open" if:
- Appears in Threads sections across 2+ different daily notes
- No matching `✅` completion found in vault for that thread

Sort by persistence (most days appearing first):

```markdown
> **Open threads:**
> - Respond to collaboration request — 5 days
> - Schedule dentist appointment — 3 days
> - Draft reply to forum post — 2 days
```

**→ Inference:** After listing threads, derive one data-specific observation. Look for:
- Thread persisting 5+ days → is it actually a priority or can it be closed?
- Multiple threads at exactly 2 days → fragmented attention; many small things unresolved
- All threads are low-friction actions (scheduling, replying) → tendency to defer easy tasks

Write the inference in detected language. Skip if no clear pattern.

## Reflection Questions

Generate **exactly 2** sharp questions grounded in the week's data. Use the accumulated "→" inferences as the primary source — the two most significant patterns of the week become the two questions.

Additional patterns to draw from:

| Pattern | Question type |
|---|---|
| Theme with high mentions but no new note | "What's blocking the conversion into a note?" |
| Project same status 2+ weeks | "What specifically is needed for the next step?" |
| Thread persisting 4+ days without resolution | "Is this a real priority or can it be closed?" |
| Tasks clustered on 1–2 days | "What was preventing work on the other days?" |
| One project dominates all mentions | "Is this intentional or are other projects getting lost?" |
| User journal mentions concept but no wikilink exists | "Is this concept ready to become a note?" |

```markdown
> **Reflection:**
> 1. [[writing process]] appeared 6 times this week but no new note was created — what's blocking the conversion from thinking to writing?
> 2. [[Personal Blog Relaunch]] has been "design blocked" for two weeks — what's the actual next action to unblock it?
```

Questions must be specific: name the actual note, project, or number from this week's data. Never generic.

## Output Format

Full callout written into the weekly note:

```markdown
> [!weekly-review]- Weekly review — YYYY-WWW
> **Completed tasks (N):**
> - Task description — weekday
> → [inference about task pattern — only if pattern found]
>
> **Hot themes:**
> - [[note-or-meta]] — N mentions
> → [inference about theme pattern — only if pattern found]
>
> **Journal pattern:** [one sentence — only if cross-day pattern found]
>
> **Projects:**
> - [[Project Name]] 🟦 — narrative from the week
> → [inference about project portfolio — only if pattern found]
>
> **Open threads:**
> - Thread description — N days
> → [inference about thread accumulation — only if pattern found]
>
> **Reflection:**
> 1. Specific question grounded in data
> 2. Specific question grounded in data
```

**Rules:**
- Write into note — never just output to chat
- Collapsed by default (`-` suffix on callout)
- Callout title includes the week ID: `[!weekly-review]- Weekly review — 2026-W08`
- All labels translated to detected language (e.g. "Задачи завершены", "Горячие темы", etc.)
- Skip sections with no content — don't write empty headers
- Skip "→" inference lines where no clear pattern exists — never write generic "→" lines
- Every reference = `[[wikilink]]`, never vague "in one of the notes"

## User Participation Sections

After the `[!weekly-review]-` callout, appended **outside it** (in the note body), with a horizontal rule separator:

**Default form (always):**
```markdown
---
**Мои выводы / My conclusions:**

**Фокус на следующую неделю / Focus for next week:**
```

**Extended form (when review data shows a specific sharp pattern):**
Replace the section above with:
```markdown
---
*[One direct question from the review's most significant finding — e.g., "Что блокировало [[writing process]] от превращения в заметку?" / "What's blocking [[writing process]] from becoming a note?"]*

**Мои выводы / My conclusions:**

**Фокус на следующую неделю / Focus for next week:**
```

Write the italic question in detected language. Use extended form only when a pattern is unambiguous. Default to the plain two-header form otherwise.

**Note:** The "Focus for next week" section is read by the monthly-review skill when computing Planned vs Actual.

## Chat Output

After writing, confirm minimally:

```
Review written → periodic/weekly/2026-W08.md

Tasks: 5 completed.
Themes: knowledge management (6), writing process (4).
Projects: 3 active.
Threads: 3 open.
```

If the note was created — first line: `Created periodic/weekly/2026-W08.md + review.`
Adapt language of confirmation to match detected language.
