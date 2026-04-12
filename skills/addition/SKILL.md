---
name: additions
description: 'Create supplementary materials attached to existing notes: experiments, meetings, reports, logs, conspectuses, practice sessions, annotations, AI outputs, links collections. Two-step process: (1) create aggregator space, (2) create concrete addition in base/additions/. INVOKE when user wants to attach any supplementary material to an existing note. Triggers: "addition", "create addition", "experiment", "meeting notes", "report", "conspectus", "log", "practice", "annotations", "links", "link collection", "аддишн", "конспект", "встреча", "отчёт", "эксперимент", "практика", "аннотации", "ссылки", "добавь к заметке".'
---

# Obsidian Additions

Two-level system for attaching supplementary materials to notes.

## Architecture

### Level 1: Aggregator (Space)

Container note in `base/additions/` that groups additions by type. Tagged `mark/addition/aggregator`.

### Level 2: Concrete Additions

Individual additions inside the aggregator space. Live in `base/additions/` or subdirectories (e.g., `base/additions/conspectuses/`).

## Addition Types

| Emoji | Type | Tag (concrete) | Subdirectory |
|-------|------|-----------------|-------------|
| 💪 | practice | `mark/addition/practice` | `base/additions/` |
| 📁 | attachments | `mark/addition/attachments` | `base/additions/` |
| 🕵 | researches | `mark/addition/researches` | `base/additions/` |
| ⬜ | canvases | `mark/addition/canvases` | `base/additions/` |
| 🤖 | AI | `mark/addition/ai` | `base/additions/` |
| ➕ | other | `mark/addition/other` | `base/additions/` |
| 📓 | conspectuses | `mark/addition/conspectus` | `base/additions/conspectuses/` |
| 🖍 | annotations | `mark/addition/annotations` | `base/additions/` |
| ✅️ | tasks | `mark/addition/tasks` | `base/additions/` |
| 🚨 | reports | `mark/addition/report` | `base/additions/` |
| 🧪 | experiments | `mark/addition/experiment` | `base/additions/` |
| 🗣️ | meetings | `mark/addition/meeting` | `base/additions/` |
| 🔗 | links | `mark/addition/links` | `base/additions/` |

## Workflow 1: Create Aggregator Space

### Steps

1. **Identify parent note** — user specifies which note to attach addition to
2. **Verify the note exists** — use Glob to find it
3. **Choose addition type** — ask user which type from the table above
4. **Check for duplicates** — verify no aggregator with same name already exists in `base/additions/`
5. **Create aggregator file** in `base/additions/`
6. **Update parent note** — add wikilink to `addition` frontmatter property

### Aggregator Naming

```
<parent note title> - <addition type>
```

Examples:
- `Deep Learning - conspectuses.md`
- `Introduction to Statistics - practice.md`
- `My Project - experiments.md`

### Aggregator Frontmatter

```yaml
---
tags:
  - mark/addition/aggregator
---
```

### Update Parent Note's `addition` Property

Add a wikilink to the `addition` array in the parent note's frontmatter:

```yaml
addition:
  - "[[<aggregator name>|<emoji>]]"
```

Example — if parent note is `sources/Deep Learning.md` and type is `conspectuses`:

```yaml
addition:
  - "[[Deep Learning - conspectuses|📓]]"
```

**Rules:**
- If `addition` property doesn't exist — create it as a list with one item
- If `addition` property exists and is a list — append the new item
- If `addition` property exists but is empty — replace with a list containing the new item
- Preserve all existing items in the list

## Workflow 2: Create Concrete Addition

### Steps

1. **Identify target aggregator** — user specifies which aggregator or parent note
2. **Verify the aggregator exists** — use Glob in `base/additions/`
3. **Create addition file** based on type (see templates below)
4. **Add wikilink to the concrete addition** in the aggregator body as a list item (e.g., `- [[My Project (2025-08-10) - meeting]]`)

### Concrete Addition Naming

```
<parent note title> (<date>) - <addition type>
```

Date format: `YYYY-MM-DD`

Examples:
- `My Project (2025-08-10) - experiments.md`
- `My Project (2025-08-10) - meeting.md`
- `My Project (2025-08-10) - reports.md`

For conspectuses — use descriptive name instead of date:
- `introduction to computer architecture.md` (in `base/additions/conspectuses/`)

### Concrete Addition Templates

#### Experiment

```yaml
---
tags:
  - mark/addition/experiment
status: 🟥
project:
  - "[[<parent note>]]"
attribute:
input:
output:
description:
created: <ISO 8601>
updated: <ISO 8601>
---
```

#### Meeting

```yaml
---
tags:
  - mark/addition/meeting
status: 🟥
project:
  - "[[<parent note>]]"
created: <ISO 8601>
updated: <ISO 8601>
---
```

#### Report

```yaml
---
tags:
  - mark/addition/report
status: 🟥
project:
  - "[[<parent note>]]"
created: <ISO 8601>
updated: <ISO 8601>
---
```

#### Conspectus (Log)

```yaml
---
tags:
  - <source type tag from parent>
  - mark/log/conspectus
  - <category tags from parent>
aliases: []
status: 🟦
source:
  - "[[<parent note>]]"
next:
category:
creator:
url:
published:
start: <ISO 8601>
end:
total_hours: 0
updated: <ISO 8601>
---

> [!toc]+
> ```table-of-contents
> ```
```

**For conspectus notes:** copy `source type` and `category` tags from the parent source note.

#### Links

```yaml
---
tags:
  - mark/addition/aggregator
  - mark/addition/links
meta:
  - "[[<parent note>]]"
created: <ISO 8601>
updated: <ISO 8601>
---
```

Body: semantic groups using collapsed `[!abstract]-` callouts. Links live directly in the aggregator — no separate concrete additions needed for this type.

Example group:
```
> [!abstract]- 💬 Chat & Inference
> - [Groq](https://groq.com/) · fast inference
> - [OpenRouter](https://openrouter.ai/) · model aggregator
```

#### Generic Addition (practice, annotations, AI, researches, etc.)

```yaml
---
tags:
  - mark/addition/aggregator
---
```

Use the aggregator tag for generic containers. Body content is freeform.

## Important Rules

- **Always verify notes exist** before linking — use Glob
- **Never overwrite** existing `addition` entries — only append
- **Date format** for all timestamps: ISO 8601 with timezone (`YYYY-MM-DDTHH:mm:ssZ`)
- **Aggregator body** is freeform markdown — the user organizes content within it
- **Concrete additions** go in `base/additions/` or its subdirectories
- Conspectus notes specifically go in `base/additions/conspectuses/`
