---
name: quarterly-review
description: "Generates a strategic quarterly review in the quarterly note: 3-month velocity trend, planned vs actual (from previous quarterly/monthly intent), theme drift across months, source-to-note synthesis ratio, project outcomes (completed/frozen/started), and one strategic question. Creates the quarterly note if it doesn't exist. INVOKE when the user wants a quarterly review or quarter summary. Triggers: 'quarterly review', 'quarter summary', 'итоги квартала', 'квартальный обзор', 'обзор квартала', 'что за квартал'."
---

# Quarterly Review

Generates a strategic quarterly review without asking questions. Aggregates 3 months of vault data and writes a `[!quarterly-review]-` block into the quarterly note, then appends a minimal space for the user's own reflections.

## Language Detection

Before generating any content, detect the user's writing language. Read the 5 most recent daily notes (`periodic/daily/YYYY-MM-DD.md`). In non-frontmatter, non-wikilink, non-tag text, count Cyrillic vs Latin characters. If Cyrillic > 30% → write the entire review in Russian. Otherwise → English.

Apply to ALL section headers, metric labels, table column names, inference lines (→), and participation prompts. Callout types and wikilinks remain unchanged regardless of detected language.

## Quarterly Note Format

**Path:** `periodic/quarterly/YYYY-QN.md`

**Compute quarter months and parent year** (cross-platform, using `obsidian eval`):
```bash
obsidian eval code="const d=new Date();const q=Math.ceil((d.getMonth()+1)/3);const m1=(q-1)*3+1;const months=[0,1,2].map(i=>d.getFullYear()+'-'+String(m1+i).padStart(2,'0'));d.getFullYear()+'-Q'+q+' '+months.join(' ')"
# example output: 2026-Q1 2026-01 2026-02 2026-03
```

**Frontmatter (exact from template):**
```yaml
---
tags:
  - periodic/quarter
up:
  - "[[periodic/yearly/YYYY|YYYY]]"
created: YYYY-MM-DDTHH:mm:ssZ
updated: YYYY-MM-DDTHH:mm:ssZ
reviewed: false
cssclasses:
  - hide-backlinks
---

> [!success]- 🔻 history 🔻
> `$=await dv.view("templates/views/periodic", {type: "month"})`
```

If the quarterly note exists — find `[!quarterly-review]-` and replace it. Otherwise create with template, then append the review block after `[!success]-`.

## Execution Flow

```
User: "quarterly review" / "итоги квартала" / "квартальный обзор"
    |
1. Compute current quarter (YYYY-QN) and its 3 months (MM1, MM2, MM3)
    |
2. Find or create periodic/quarterly/YYYY-QN.md
    |
3. Detect language from last 5 daily notes
    |
4. Gather IN PARALLEL:
   a. Velocity — count notes/tasks/sources per month, all 3 months
   b. Planned vs actual — read user-written sections from monthly notes + previous quarterly
   c. Theme drift — wikilink frequency per month, compare Month1 vs Month3
   d. Synthesis ratio — total sources processed vs notes created in quarter
   e. Project outcomes — completed/frozen/started projects this quarter
    |
5. For each section: collect data → derive one "→" inference from the specific pattern
    |
6. Write [!quarterly-review]- callout into quarterly note
    |
7. Append user participation section below the callout (outside it)
    |
8. Minimal chat confirmation
```

## Velocity Trend

Compute the same three metrics as monthly-review, but independently for each of the 3 months. Show as a trend, not just totals.

### Per-month computation (repeat for MM1, MM2, MM3)

**Notes created:**
```bash
obsidian search query="[created: YYYY-MM]" path=base/notes total
obsidian search query="[created: YYYY-MM]" path=base/additions total
```

**Tasks closed:**
```bash
obsidian search query="✅ YYYY-MM" total
```

**Sources processed:**
```bash
obsidian search query="[status: 🟩] [end: YYYY-MM]" path=sources total
```

Format as a trend table. Use ↑ / ↓ / → arrows to indicate direction Month1→Month3 (↑ = grew >20%, ↓ = dropped >20%, → = stable within 20%):

```markdown
> **Velocity trend:**
>
> |               | Jan | Feb | Mar | Trend |
> |---|---|---|---|---|
> | Notes created | 8   | 14  | 19  | ↑     |
> | Tasks closed  | 31  | 22  | 18  | ↓     |
> | Sources       | 3   | 6   | 2   | →     |
> | **Total**     | 42  | 42  | 39  |       |
```

**→ Inference:** After the table, derive one data-specific observation. Look for:
- Notes ↑ and tasks ↓ → shifting from execution to thinking — intentional focus change or execution fatigue?
- All metrics ↓ → burnout signal, seasonal slowdown, or deliberate deceleration?
- Sources ↑ but notes → → reading more without producing more — synthesis is lagging
- Strong Month1, weak Month3 → lost momentum through the quarter; what happened?
- Consistent across all 3 months → stable productive rhythm — unusual and worth noting

Write the inference in detected language. Skip if no clear pattern.

## Planned vs Actual

Look for stated intentions to compare against what actually happened.

### Where to look (in priority order)

1. **User-written sections from monthly notes** — read text BELOW the `[!monthly-review]-` callout in each of the 3 monthly notes (`periodic/monthly/YYYY-MM1.md`, `YYYY-MM2.md`, `YYYY-MM3.md`). These are the "Focus for next month" entries the user wrote after each monthly review.

2. **Previous quarterly note** (`periodic/quarterly/YYYY-QN-1.md`) — text BELOW the `[!quarterly-review]-` callout (user's quarterly focus and conclusions from last quarter).

3. **Yearly note** (`periodic/yearly/YYYY.md`) — any goals or intentions stated at the top level.

Extract: stated goals, themes flagged as priorities, projects mentioned as upcoming.

Cross-reference with quarter's actual data (themes that grew, projects completed).

```markdown
> **Planned vs Actual:**
> - Planned: focus on [[writing process]], finish [[Long-form Essay Collection]]
> - Actual: [[learning systems]] dominated (18 refs), [[Long-form Essay Collection]] still 🟦
> - Unplanned: [[productivity systems]] emerged mid-quarter (0 → 11 refs)
```

If no prior intentions found anywhere — write:
```markdown
> **Planned vs Actual:** No prior intentions recorded. To use this section next quarter: write your focus below after this review.
```

**→ Inference:** Was the drift from plan intentional (genuine reprioritization) or reactive (distraction, external events)? A large gap between planned and actual with no explanation in user notes is a signal worth examining.

Write the inference in detected language. Skip this "→" if no stated focus existed.

## Theme Drift

Shows how attention shifted across the 3 months. Reveals what gained momentum and what faded.

### Process
For each of the 3 months, aggregate wikilinks from daily notes (`periodic/daily/YYYY-MM-*.md`) pointing to `base/_meta-notes/` and `base/notes/`. Take top 5 per month.

Show as a drift table — what was top in Month1 vs Month3:

```markdown
> **Theme drift:**
> - Gained momentum: [[learning systems]] (M1: 3 → M3: 14), [[writing process]] (M1: 0 → M3: 9)
> - Faded: [[productivity systems]] (M1: 12 → M3: 2), [[linux administration]] (M1: 8 → M3: 0)
> - Consistent: [[knowledge management]] (M1: 7, M2: 9, M3: 8)
```

**→ Inference:** After listing drift, derive one data-specific observation. Look for:
- A theme gained momentum but no project in that area was started or completed → growing intellectual interest, no output yet
- A faded theme had an active project → project may have stalled when interest shifted
- No consistent themes across all 3 months → intellectually nomadic quarter; lots of exploration, no depth
- A consistent theme with high mentions but no completed project → sustained attention without shipping

Write the inference in detected language. Skip if no clear pattern.

## Synthesis Ratio

A PKM-specific metric: how much was consumed vs how much was synthesized into the knowledge base.

```
Sources processed in quarter = sum of monthly source counts
Notes created in quarter     = sum of monthly note counts (base/notes only, not additions)
Ratio = notes / sources
```

**Scale (inline, always show with the number):**
- Ratio > 2.0 → **strong synthesis**: each source generates 2+ notes — reading actively builds the knowledge base
- Ratio 1.0–2.0 → **balanced**: healthy equilibrium between input and output
- Ratio 0.5–1.0 → **consumption-heavy**: reading more than synthesizing — inputs are accumulating unprocessed
- Ratio < 0.5 → **synthesis gap**: significant backlog of unprocessed material

```markdown
> **Synthesis ratio:**
> - Sources processed: 14 | Notes created: 31 | Ratio: 2.2 (strong synthesis)
> - *Scale: >2.0 = strong, 1.0–2.0 = balanced, 0.5–1.0 = consuming, <0.5 = gap*
```

**→ Inference:** After showing ratio, derive one data-specific observation. Look for:
- Ratio dropped compared to previous quarter → more sources added without synthesis steps? Or fewer notes written?
- Ratio very high (>4.0) → unusually productive synthesis; what drove it?
- Ratio < 0.5 three quarters in a row → systematic synthesis gap; a habit change is needed, not a one-time fix

Write the inference in detected language.

If sources = 0 — skip ratio, write: `Sources processed: 0 — no external inputs this quarter.`

## Project Outcomes

What happened to projects during the quarter.

### Completed
```bash
obsidian search query="[status: 🟩]" path=projects
obsidian search query="[status: 📢]" path=projects
# Filter: keep only files where updated: frontmatter falls within the quarter
```

### Frozen this quarter
```bash
obsidian search query="[status: ❄]" path=projects
# Filter: keep only files where updated: frontmatter falls within the quarter
```

### Started this quarter
```bash
obsidian search query="[status: 🟦]" path=projects
obsidian search query="[status: 🟥]" path=projects
# Filter: keep only files where created: frontmatter falls within the quarter
```

### Still stuck (carried from previous quarter)
```bash
obsidian search query="[status: 🟦]" path=projects
obsidian search query="[status: 🟥]" path=projects
# Filter: created: predates the quarter start AND updated: is 30+ days before today
```

```markdown
> **Project outcomes:**
> - Completed (2): [[Personal Blog Relaunch]] 📢, [[Home Lab v2]] 🟩
> - Frozen (1): [[Course Outline Draft]] ❄️
> - Started (3): [[Reading System Overhaul]], [[Note Linking Automation]], [[Weekly Podcast]]
> - Still stuck (2): [[Archive Migration]] 🟦 (91 days), [[API Docs Rewrite]] 🟥 (47 days)
```

**→ Inference:** After listing outcomes, derive one data-specific observation. Look for:
- Started > Completed → the backlog is growing; starting is much easier than finishing
- Frozen projects outnumber completed → optimistic starts meeting unsustainable scope
- Stuck projects lasting 90+ days → need a decision: clear next action or archive
- All stuck projects share a category or type → there may be a systemic obstacle in that area

Write the inference in detected language.

## Strategic Question

Generate **exactly 1** sharp strategic inference from the quarter's data. Not a question — a statement that surfaces the biggest tension, gap, or contradiction found in the review. Grounded in the specific numbers.

Look for the biggest gap, contradiction, or momentum signal:

| Pattern | Strategic inference type |
|---|---|
| Tasks ↓ but notes ↑ | "Shifting from execution to thinking — intentional?" |
| Top theme ≠ any completed project | "Attention ≠ output — where does the effort actually go?" |
| High synthesis ratio but no completed projects | "Thinking fast, shipping slow" |
| Planned focus ≠ actual dominant theme | "Quarter drifted — new priority or loss of focus?" |
| Many started, few completed | "Starting is easy — what makes finishing hard?" |
| Theme consistent all 3 months but no new notes | "Deep engagement or just repeated visiting?" |

```markdown
> **Strategic question:**
> [[writing process]] dominated 30% of all quarter mentions, but no project in this area was completed — is thinking about writing replacing the act of writing?
```

Write in detected language, casual register. One sentence, specific, grounded in actual numbers from the review.

## Output Format

```markdown
> [!quarterly-review]- Quarterly review — YYYY-QN
> **Velocity trend:**
>
> |               | MM1 | MM2 | MM3 | Trend |
> |---|---|---|---|---|
> | Notes created | N   | N   | N   | ↑/↓/→ |
> | Tasks closed  | N   | N   | N   | ↑/↓/→ |
> | Sources       | N   | N   | N   | ↑/↓/→ |
> → [inference about trend direction — only if clear pattern]
>
> **Planned vs Actual:**
> - Planned: ...
> - Actual: ...
> → [inference about gap — only if stated focus existed]
>
> **Theme drift:**
> - Gained: [[theme]] (M1: N → M3: N)
> - Faded: [[theme]] (M1: N → M3: N)
> - Consistent: [[theme]]
> → [inference about intellectual trajectory — only if clear pattern]
>
> **Synthesis ratio:**
> - Sources: N | Notes: N | Ratio: N.N (label)
> - *Scale: >2.0 = strong, 1.0–2.0 = balanced, 0.5–1.0 = consuming, <0.5 = gap*
> → [inference about synthesis habit]
>
> **Project outcomes:**
> - Completed (N): ...
> - Frozen (N): ...
> - Started (N): ...
> - Still stuck (N): ...
> → [inference about execution pattern — only if clear pattern]
>
> **Strategic question:**
> [One sharp sentence in detected language]
```

**Rules:**
- Write into note — never just output to chat
- Collapsed by default (`-` suffix on callout)
- Callout title includes quarter: `[!quarterly-review]- Quarterly review — 2026-Q1`
- All labels translated to detected language
- Skip sections with no content — don't write empty headers
- Skip "→" inference lines where no clear pattern exists — never write generic lines
- Every reference = `[[wikilink]]`
- Strategic question must be a statement, not an interrogative — thought-provoking without being a direct question

## User Participation Sections

After the `[!quarterly-review]-` callout, appended **outside it** (in the note body), with a horizontal rule separator:

**Default form (always):**
```markdown
---
**Мои выводы / My conclusions:**

**Фокус на следующий квартал / Focus for next quarter:**
```

**Extended form (when review data shows a specific sharp pattern):**
```markdown
---
*[One direct question from the review's most significant finding — e.g., "Если [[writing process]] занял 30% квартала без результата — что конкретно нужно изменить в следующем?" / "If [[writing process]] dominated the quarter without output — what specifically needs to change next quarter?"]*

**Мои выводы / My conclusions:**

**Фокус на следующий квартал / Focus for next quarter:**
```

Write the italic question in detected language. Use extended form only when a pattern is unambiguous.

**Note:** The "Focus for next quarter" section is read by the yearly-review skill when computing theme trajectory and priorities.

## Chat Output

```
Review written → periodic/quarterly/2026-Q1.md

Velocity: ↑ notes (8→19), ↓ tasks (31→18), → sources.
Theme drift: learning systems gained, productivity faded.
Synthesis: 2.2 (strong).
Projects: 2 completed, 1 frozen, 3 started, 2 stuck.
```

If note was created — first line: `Created periodic/quarterly/2026-Q1.md + review.`
Adapt language of confirmation to match detected language.
