---
name: obsidian-system-notes
description: 'Create structural system notes: meta-notes (thematic hubs), problems (research questions), and hierarchies (aggregators). INVOKE when user wants to create any structural knowledge note. Triggers: "create meta-note", "create problem", "create hierarchy", "system note", "structural note", "мета-заметка", "создай мета", "проблема", "иерархия", "структурная заметка", "узел иерархии". NEVER creates categories — human-only.'
---

# Obsidian System Notes

Create structural system notes that form the knowledge hierarchy: **meta-notes**, **problems**, and **hierarchies**.

**CRITICAL:** Never create categories — these are human-only.

## Note Types

| Type | Tag | Directory | Purpose |
|------|-----|-----------|---------|
| **Meta-note** | `system/high/meta` | `base/_meta-notes/` | Thematic hub or roadmap for a knowledge area |
| **Problem** | `system/high/problem` | `base/_problems/` | Specific research question within a meta-note |
| **Hierarchy** | `system/high/hierarchy` | `base/_hierarchy/` | Aggregator that groups related notes in the hierarchy |

## Hierarchy Chain

```
Category → Meta-note → Problem → Hierarchy
```

- **Category** — human-only. Agent NEVER creates these.
- **Meta-note** — must link to exactly one existing category.
- **Problem** — must link to exactly one existing meta-note AND use the same category as that meta-note.
- **Hierarchy** — can link to a category, a meta-note, or a problem. Always use the same category as its parent.

## Workflow Decision Tree

```
User wants a system note →
  └─ "organize a knowledge area / thematic hub" → Meta-note
  └─ "specific question / research problem" → Problem
  └─ "aggregate / group notes under a topic" → Hierarchy
```

## Naming Rules

Same rules as regular notes:

| Rule | Description |
|------|-------------|
| **Uniqueness** | Must be unique across the entire vault |
| **Case** | Lowercase only. Exception: proper nouns |
| **Structure** | Nouns or stable noun phrases only |
| **Forbidden** | No dates, numbers, questions, or pronouns |
| **Compatibility** | Filesystem-safe characters only |

## Finding Valid Links

Before creating any system note, discover existing notes dynamically:

| Field | Directory | Glob Pattern |
|-------|-----------|--------------|
| `category` | `base/categories/` | `base/categories/*.md` |
| `meta` | `base/_meta-notes/` | `base/_meta-notes/*.md` |
| `problem` | `base/_problems/` | `base/_problems/*.md` |

**Workflow:**
1. **Discover existing notes** — use either:
   - `obsidian files folder=base/categories ext=md` / `obsidian files folder=base/_meta-notes ext=md` / `obsidian files folder=base/_problems ext=md` (CLI, cross-platform)
   - Glob patterns from the table above (Claude built-in Glob tool)
2. **Match by relevance** — choose the most appropriate existing note
3. **If no match exists** — leave the field empty or ask the user; NEVER invent links
4. **Constraint:** Problem must use the same category as its parent meta-note

---

## Meta-note

Thematic hub that organizes a broad knowledge area under one category.

### Frontmatter Template

```yaml
---
tags:
  - system/high/meta
aliases:
category:
  - "[[category name]]"
relevant: false
created: 2025-08-10T23:25:33+07:00
updated: 2025-08-10T23:25:33+07:00
---
```

### Fields

- **category**: Link to one existing category from `base/categories/`
- **relevant**: `false` by default; user sets to `true` when actively working in this area
- **aliases**: empty by default

### Body

New meta-notes start with the stub marker `💤`. When creating, place it as the first line of body content:

```markdown
💤
```

### Example

Filename: `base/_meta-notes/machine learning.md`

```markdown
---
tags:
  - system/high/meta
aliases:
category:
  - "[[computer science]]"
relevant: false
created: 2025-08-10T23:25:33+07:00
updated: 2025-08-10T23:25:33+07:00
---

💤
```

---

## Problem

A specific research question anchored to a meta-note. Inherits the same category.

### Frontmatter Template

```yaml
---
tags:
  - system/high/problem
aliases:
category:
  - "[[category name]]"
meta:
  - "[[meta note name]]"
relevant: false
created: 2025-08-10T23:25:33+07:00
updated: 2025-08-10T23:25:33+07:00
---
```

### Fields

- **category**: Same category as the parent meta-note — required
- **meta**: Link to the parent meta-note — required
- **relevant**: `false` by default

### Body

```markdown
💤
```

### Example

Filename: `base/_problems/overfitting in neural networks.md`

```markdown
---
tags:
  - system/high/problem
aliases:
category:
  - "[[computer science]]"
meta:
  - "[[machine learning]]"
relevant: false
created: 2025-08-10T23:25:33+07:00
updated: 2025-08-10T23:25:33+07:00
---

💤
```

---

## Hierarchy

Aggregator note that groups related knowledge under a node in the hierarchy. Can attach to a category, meta-note, or problem.

### Frontmatter Template

```yaml
---
tags:
  - system/high/hierarchy
aliases:
category:
  - "[[category name]]"
meta:
  - "[[meta note name]]"
problem:
  - "[[problem name]]"
relevant: false
created: 2025-08-10T23:25:33+07:00
updated: 2025-08-10T23:25:33+07:00
---
```

### Fields

- **category**: Required — use the same category as the parent meta-note/problem
- **meta**: Optional — link to parent meta-note if applicable
- **problem**: Optional — link to parent problem if applicable
- **relevant**: `false` by default

### When to fill meta vs problem

| Hierarchy attaches to | Fill `meta` | Fill `problem` |
|-----------------------|-------------|----------------|
| Category only | — | — |
| Meta-note | Yes | — |
| Problem | Yes (same meta) | Yes |

### Body

```markdown
💤
```

### Example

Filename: `base/_hierarchy/regularization techniques.md`

```markdown
---
tags:
  - system/high/hierarchy
aliases:
category:
  - "[[computer science]]"
meta:
  - "[[machine learning]]"
problem:
  - "[[overfitting in neural networks]]"
relevant: false
created: 2025-08-10T23:25:33+07:00
updated: 2025-08-10T23:25:33+07:00
---

💤
```
