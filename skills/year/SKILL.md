---
name: year
description: "Generates a strategic yearly review in the yearly note: year in numbers with consistency and peak/dead months, intellectual diet breakdown by source type and category, multi-quarter theme trajectory (emergent vs abandoned vs core), project portfolio with completion rate and multi-year drag, synthesis ratio trend across quarters, year in one sentence, and one data-derived priority for next year. Creates the yearly note if it doesn't exist. INVOKE when the user wants a yearly review or year summary. Triggers: 'yearly review', 'year review', 'year summary', 'итоги года', 'годовой обзор', 'обзор года', 'что за год'."
---

# Yearly Review

Generates a comprehensive yearly review without asking questions. Chains data upward from quarterly and monthly reviews, recomputes where those don't exist, and writes a `[!yearly-review]-` block into the yearly note, then appends a minimal space for the user's own reflections.

## Language Detection

Before generating any content, detect the user's writing language. Read the 5 most recent daily notes (`periodic/daily/YYYY-MM-DD.md`). In non-frontmatter, non-wikilink, non-tag text, count Cyrillic vs Latin characters. If Cyrillic > 30% → write the entire review in Russian. Otherwise → English.

Apply to ALL section headers, metric labels, table column names, inference lines (→), characterization labels, and participation prompts. Callout types and wikilinks remain unchanged regardless of detected language.

## Yearly Note Format

**Path:** `periodic/yearly/YYYY.md`

**Frontmatter (exact from template):**
```yaml
---
tags:
  - periodic/year
reviewed: false
cssclasses:
  - hide-backlinks
created: YYYY-MM-DDTHH:mm:ssZ
updated: YYYY-MM-DDTHH:mm:ssZ
---

> [!success]- 🔻 history 🔻
> `$=await dv.view("templates/views/periodic", {type: "quarter"})`
```

Note: yearly notes have **no `up:` field** — they are the top of the hierarchy.

If the yearly note exists — find `[!yearly-review]-` and replace it. Otherwise create with template, then append after `[!success]-`.

## Execution Flow

```
User: "yearly review" / "итоги года" / "годовой обзор"
    |
1. Determine current year (YYYY)
    |
2. Find or create periodic/yearly/YYYY.md
    |
3. Detect language from last 5 daily notes
    |
4. Gather IN PARALLEL:
   a. Year in numbers — velocity across all 12 months
   b. Intellectual diet — source breakdown by type and category
   c. Theme trajectory — Q1 vs Q4 themes, emergent/abandoned/core;
      also read user-written sections below [!quarterly-review]- in each quarterly note
   d. Project portfolio — all year outcomes + multi-year drag
   e. Synthesis ratio — per quarter trend
   f. Previous yearly note — for year-over-year comparison
    |
5. For each section: collect data → derive one "→" inference from the specific pattern
    |
6. Generate review: numbers → diet → trajectory → projects →
   synthesis → year sentence → next year priority
    |
7. Write [!yearly-review]- callout into yearly note
    |
8. Append user participation section below the callout (outside it)
    |
9. Minimal chat confirmation
```

## Year in Numbers

Compute velocity for each of the 12 months, then aggregate.

**Per-month computation (all 12 months in parallel):**
```bash
# Notes created (run for each MM from 01 to 12):
obsidian search query="[created: YYYY-MM]" path=base/notes total
obsidian search query="[created: YYYY-MM]" path=base/additions total

# Tasks closed (run for each MM):
obsidian search query="✅ YYYY-MM" total

# Sources processed (run for each MM):
obsidian search query="[status: 🟩] [end: YYYY-MM]" path=sources total
```

**Aggregate:**
- Total for year
- Peak month: month with highest combined activity
- Dead months: months where notes=0 AND tasks=0 AND sources=0
- Consistency score: (12 - dead months) / 12 × 100%
  *Consistency = share of months with any activity. 100% = active every month. Lower = feast-or-famine pattern.*

**Year-over-year:** If `periodic/yearly/YYYY-1.md` exists and has a `[!yearly-review]-` block, extract its totals for comparison. Show delta with ↑/↓.

```markdown
> **Year in numbers:**
> - Notes: 187 (↑ from 134 last year)
> - Tasks closed: 412 (↓ from 489)
> - Sources processed: 43 (↑ from 31)
> - Peak month: October (notes: 28, tasks: 67, sources: 9)
> - Dead months: 2 (February, July)
> - Consistency: 83% (10 of 12 months active)
```

**→ Inference:** After showing numbers, derive one data-specific observation. Look for:
- All metrics ↑ vs last year → growth year; what structural change made this possible?
- One metric ↓ while others ↑ → something shifted (notes ↑ but tasks ↓ = more thinking, less doing)
- Dead months > 3 → sporadic pattern; the habit is fragile — what collapsed in those months?
- Consistency < 60% → the work is concentrated in bursts; useful to understand what sustains the active periods

Write the inference in detected language. Skip if no clear pattern.

## Intellectual Diet

Breakdown of all sources completed (`end: YYYY-` + `status: 🟩`) by type and category.

### Source types

All valid source tags in this vault:
```
source/article/paper
source/article/resource
source/book
source/course
source/cinematic/movie
source/cinematic/series
source/cinematic/anime
source/podcast
source/video/recording
source/video/playlist
source/music/album
source/music/tracklist
source/game
```

```bash
# Get all sources completed this year, then count by tag:
obsidian search query="[status: 🟩] [end: YYYY]" path=sources
# From those files, count occurrences of each tag above.
# Or look up each type directly:
obsidian tag name="source/book" verbose
obsidian tag name="source/article/paper" verbose
obsidian tag name="source/article/resource" verbose
obsidian tag name="source/course" verbose
obsidian tag name="source/cinematic/movie" verbose
obsidian tag name="source/cinematic/series" verbose
obsidian tag name="source/cinematic/anime" verbose
obsidian tag name="source/podcast" verbose
obsidian tag name="source/video/recording" verbose
obsidian tag name="source/video/playlist" verbose
obsidian tag name="source/music/album" verbose
obsidian tag name="source/music/tracklist" verbose
obsidian tag name="source/game" verbose
# Cross-reference each result with the completed set for YYYY.
```

### Source categories
```bash
# Read completed sources from: obsidian search query="[status: 🟩] [end: YYYY]" path=sources
# Extract category: frontmatter field from each file → count by category, show top 5
```

```markdown
> **Intellectual diet:**
> - By type: 📚 books: 12 | 📄 articles/resources: 11 | 📑 papers: 7 | 🎬 video/recordings: 5 | 📺 video/playlists: 3 | 🎓 courses: 2 | 🎬 movies: 2 | 📡 podcasts: 1
> - Top categories: [[knowledge management]] (11), [[artificial intelligence]] (9), [[productivity]] (7), [[writing]] (5), [[health]] (3)
> - Dominant type: books (29% of total)
```

If one type > 60% of total — flag it: `⚠️ Heavy bias toward [type] — consider diversifying sources.`

**→ Inference:** After showing diet, derive one data-specific observation. Look for:
- Diet dominated by passive formats (articles, videos) vs active (books, courses, papers) → breadth vs depth signal
- Top categories in diet diverge from core themes in knowledge base → are you studying what you're actually thinking about?
- Very narrow category coverage (2–3 categories dominate) → potential echo chamber; what's being ignored?
- Diet is varied and matches theme trajectory → strong alignment between learning and thinking

Write the inference in detected language. Skip if no clear pattern.

## Multi-Quarter Theme Trajectory

Reveals what emerged, what faded, and what held throughout the year. Also surfaces what the user themselves identified as important through their quarterly focus statements.

### Data source (priority order)
1. **Quarterly reviews** — if `periodic/quarterly/YYYY-Q1.md` through `YYYY-Q4.md` exist and have `[!quarterly-review]-` blocks, extract their "Theme Drift" sections
2. **User-written quarterly sections** — read text BELOW the `[!quarterly-review]-` callout in each quarterly note (user's "Focus for next quarter" and "My conclusions"). Surface any stated intentions that connect to theme patterns.
3. **Fallback** — grep wikilinks in daily notes for Q1 (`YYYY-01` to `YYYY-03`) and Q4 (`YYYY-10` to `YYYY-12`), count frequency per meta-note

### Classification
- **Emergent:** appeared in Q3 or Q4, absent in Q1 and Q2 (new focus area this year)
- **Abandoned:** prominent in Q1/Q2, absent in Q3/Q4 (lost momentum)
- **Core:** present in all 4 quarters (sustained intellectual interest)
- **Seasonal:** appears in exactly one quarter

```markdown
> **Theme trajectory:**
> - Emergent: [[machine learning]] (appeared Q3, dominant Q4), [[writing systems]] (Q4 only)
> - Abandoned: [[linux administration]] (Q1 top, gone by Q3), [[economics]] (Q1–Q2 only)
> - Core (all year): [[knowledge management]], [[learning]], [[productivity]]
> - Seasonal: [[health]] (Q1 only)
```

**→ Inference:** After showing trajectory, derive one data-specific observation. Look for:
- Many abandoned vs few core → intellectually nomadic year; broad exploration without depth
- Strong emergent theme in Q4 → discovered something important late; worth making it explicit next year
- Core theme with no completed projects → consistent interest but no shipping; what's the gap?
- User's quarterly focus statements align with actual theme data → intentional direction held all year

Write the inference in detected language. Skip if no clear pattern.

## Project Portfolio

Full year view of project activity and execution rate.

### Completed this year
```bash
obsidian search query="tag:#project [status: 🟩]"
obsidian search query="tag:#project [status: 📢]"
# Filter: keep only files where updated: frontmatter falls within YYYY
```

### Frozen this year
```bash
obsidian search query="tag:#project [status: ❄]"
# Filter: keep only files where updated: frontmatter falls within YYYY
```

### Started this year
```bash
obsidian search query="tag:#project [status: 🟦]"   # in progress
obsidian search query="tag:#project [status: 🟥]"   # todo
# Filter: keep only files where created: frontmatter falls within YYYY
```

### Multi-year drag
```bash
obsidian search query="tag:#project [status: 🟦]"   # in progress
obsidian search query="tag:#project [status: 🟥]"   # todo
# Filter: keep only files where created: predates YYYY (from previous years)
```

**Completion rate** = completed / (completed + frozen + multi-year drag) × 100%
*Of all projects that reached any resolution this year (completed or frozen) plus those carried from before, what share actually finished?*

```markdown
> **Project portfolio:**
> - Completed (5): [[Blog Series Part 1]] 📢, [[Home Lab Setup]] 🟩, [[Reading Tracker v2]] 🟩, [[Podcast Outline]] 📢, [[Note Sync Script]] 🟩
> - Frozen (3): [[Course Notes App]] ❄️, [[Spanish Learning Plan]] ❄️, [[Video Essay Draft]] ❄️
> - Started (8): ...
> - Multi-year drag (2): [[Archive Reorganization]] 🟦 (from 2024), [[API Integration]] 🟥 (from 2023)
> - Completion rate: 42% (5 completed / 12 resolvable)
```

If completion rate < 30%: `⚠️ Low completion rate — starting is easy, finishing is the bottleneck.`
If multi-year drag > 2 projects: `⚠️ N projects carried from previous years — consider archiving or resetting.`

**→ Inference:** After listing portfolio, derive one data-specific observation. Look for:
- High frozen count → projects are being started optimistically but scope or motivation doesn't hold
- Multi-year drag accumulating year over year → the system isn't clearing historical commitments
- Started count >> Completed count → are projects being designed too large? Or is scope expanding after start?
- Completion rate > 60% → strong execution year; what specifically worked that could be repeated?

Write the inference in detected language.

## Synthesis Ratio Trend

Shows whether synthesis efficiency improved or declined across the year.

Compute ratio (notes created / sources processed) for each quarter:

```markdown
> **Synthesis ratio:**
>
> | Q1  | Q2  | Q3  | Q4  | Year |
> |-----|-----|-----|-----|------|
> | 1.4 | 2.1 | 3.2 | 1.8 | 2.1  |
>
> *Scale: >2.0 = strong synthesis, 1.0–2.0 = balanced, 0.5–1.0 = consuming > creating, <0.5 = synthesis gap*
> Peak: Q3. Trend: ↑ Q1→Q3, ↓ Q3→Q4.
> Year average: 2.1 (balanced).
```

**→ Inference:** After showing trend, derive one data-specific observation. Look for:
- Synthesis dropping consistently Q1→Q4 → reading appetite grew faster than processing capacity
- Synthesis high in low-activity months → when less is happening, more gets processed
- Consistently low (<1.0) all year → systematic habit gap; each new source needs a note before the next one opens
- Peak synthesis quarter matches high project completion quarter → synthesis and shipping are connected

Write the inference in detected language.

## The Year in One Sentence

A single factual characterization derived from the dominant pattern — not inspirational, not motivational. Just accurate.

Derive from the data:

| Dominant pattern | Sentence type |
|---|---|
| Synthesis ratio < 1 across most quarters | "Год потребления: больше читал, чем создавал" |
| Completion rate < 30% | "Год незавершённого: много стартов, мало финишей" |
| One theme > 40% of all mentions | "Год одной темы: всё вращалось вокруг [X]" |
| Consistency < 50% | "Год рывков: продуктивные месяцы чередовались с провалами" |
| Many emergent themes, few core | "Год разброса: много новых направлений без фокуса" |
| Completion rate > 60%, synthesis > 2 | "Год зрелости: высокий выхлоп и завершение начатого" |
| Velocity ↑ YoY and synthesis ↑ | "Год роста: по всем метрикам лучше, чем предыдущий" |

```markdown
> **Year in one sentence:**
> Год одной темой: knowledge management занял 38% всех упоминаний — это либо глубина, либо туннельное зрение.
```

Write the label and characterization in detected language. One sentence. Name the exact metric or number that triggered the characterization. Do not soften or inflate — be accurate.

## Priority for Next Year

One concrete direction derived from the year's weakest or most significant signal. Not a wish — a logical next step from the data. Also check user-written quarterly sections for any stated intentions about next year.

Priority logic (pick the highest-priority applicable rule):

1. **Completion rate < 30%** → "Не начинать новые проекты пока не закроешь [N stuck projects]"
2. **Multi-year drag > 2** → "Первым делом: решить судьбу [oldest stuck project]"
3. **Synthesis ratio < 1 for 3+ quarters** → "Добавить шаг синтеза между чтением и следующим источником"
4. **Dead months > 3** → "Снизить объём в пиковые месяцы, чтобы не выгорать в мёртвые"
5. **Intellectual diet heavily biased (>60% one type)** → "Расширить диету: добавить [underrepresented source type]"
6. **Theme abandoned mid-year with no notes** → "[[Abandoned theme]] требует либо закрытия, либо осознанного возврата"
7. **Emergent theme dominant in Q4** → "[[Emergent theme]] оказался неожиданно важным — стоит сделать его явным приоритетом"

```markdown
> **Priority for next year:**
> Коэффициент синтеза падал 3 квартала подряд — добавить промежуточный шаг между обработкой источника и следующим чтением. Например: заметка до открытия нового источника.
```

One actionable sentence in detected language, with the specific number or fact that justifies it.

## Output Format

```markdown
> [!yearly-review]- Yearly review — YYYY
> **Year in numbers:**
> - Notes: N (↑/↓ from last year)
> - Tasks closed: N
> - Sources processed: N
> - Peak month: Month (notes: N, tasks: N, sources: N)
> - Dead months: N (Month, Month)
> - Consistency: N% (N of 12 months active)
> → [inference about year pattern — only if clear]
>
> **Intellectual diet:**
> - By type: 📚 books: N | 📄 articles: N | 🎬 video: N | ...
> - Top categories: [[cat]] (N), [[cat]] (N)
> → [inference about diet composition — only if clear]
>
> **Theme trajectory:**
> - Emergent: [[theme]] (appeared QN)
> - Abandoned: [[theme]] (gone by QN)
> - Core: [[theme]], [[theme]]
> → [inference about intellectual arc of the year — only if clear]
>
> **Project portfolio:**
> - Completed (N): [[Project]] 📢, [[Project]] 🟩
> - Frozen (N): [[Project]] ❄️
> - Started (N): N projects
> - Multi-year drag (N): [[Project]] (from YYYY)
> - Completion rate: N%
> → [inference about execution capacity — only if clear]
>
> **Synthesis ratio:**
>
> | Q1 | Q2 | Q3 | Q4 | Year |
> |----|----|----|----|----|
> | N  | N  | N  | N  | N  |
>
> *Scale: >2.0 = strong, 1.0–2.0 = balanced, 0.5–1.0 = consuming, <0.5 = gap*
> → [inference about synthesis trend — only if clear]
>
> **Year in one sentence:**
> [Characterization label]: [one sentence in detected language]
>
> **Priority for next year:**
> [One actionable sentence]
```

**Rules:**
- Write into note — never just output to chat
- Collapsed by default (`-` suffix)
- Callout title includes year: `[!yearly-review]- Yearly review — 2026`
- All labels translated to detected language
- Skip sections with no content
- Skip "→" inference lines where no clear pattern exists — never write generic lines
- Every reference = `[[wikilink]]`
- Flags (`⚠️`) only for patterns that cross clear thresholds — don't flag minor deviations

## User Participation Sections

After the `[!yearly-review]-` callout, appended **outside it** (in the note body), with a horizontal rule separator.

The yearly note is the top of the hierarchy — there is no higher-level review to feed. This section is for the user's personal synthesis: what the year actually meant, what they want to carry forward.

**Default form (always):**
```markdown
---
**Мои выводы за год / My reflections on the year:**

**Намерение на следующий год / My intention for [YYYY+1]:**
```

**Extended form (when review data shows a specific strong signal):**
```markdown
---
*[One direct question from the review's most significant finding — e.g., "[[X theme]] оказался заброшен к Q3 без единой заметки — это завершено или просто забыто?" / "[[X theme]] was abandoned by Q3 without a single note — resolved or forgotten?"]*

**Мои выводы за год / My reflections on the year:**

**Намерение на следующий год / My intention for [YYYY+1]:**
```

Write the italic question in detected language. Use extended form only when the signal is unambiguous.

Unlike lower-level review notes, this is not read by a higher-level review. This section exists purely for the user — a space for personal synthesis at the highest level of the review system.

## Chat Output

```
Review written → periodic/yearly/2026.md

Notes: 187 (↑ from 134). Tasks: 412. Sources: 43.
Diet: articles dominant (42%). Top: knowledge management, AI.
Themes: knowledge management core all year; linux abandoned Q3.
Projects: 5/12 completed (42%). 2 multi-year drag.
Synthesis: avg 2.1, peak Q3.
Year: [characterization in 1 line]. Priority: [priority in 1 line].
```

If note was created — first line: `Created periodic/yearly/2026.md + review.`
Adapt language of confirmation to match detected language.
