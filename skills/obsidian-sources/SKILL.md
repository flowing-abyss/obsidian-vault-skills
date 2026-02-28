---
name: obsidian-sources
description: 'Create source tracking notes in sources/ for books, articles, videos, papers, courses, films, podcasts, and other reference materials. INVOKE when user wants to track any content source. Triggers: "track book", "add source", "new book", "article", "video", "paper", "course", "film", "podcast", "добавь книгу", "запиши источник", "читаю книгу", "смотрю курс", "добавь статью", "добавь видео", "источник". Handles status, ratings, and scientificity levels.'
---

# Obsidian Sources

Create source notes in `sources/` directory for books, articles, videos, papers, and other reference materials.

## Frontmatter Template

```yaml
---
tags:
aliases:
status:
rating:
scientificity:
created: 2025-08-10T23:25:33+07:00
updated: 2025-08-10T23:25:33+07:00
start: 2025-08-10T23:25:33+07:00
end:
category:
meta:
problem:
creator:
production:
---
```

## Frontmatter Fields

### Required Fields

- **tags**: Source-specific tags (see Available Tags section)
- **status**: ⬛ (abandoned), 🟥 (planned), 🟦 (in progress), ⚛️ (atomizing), 🟩 (completed)
- **created/updated**: ISO 8601 with timezone
- **start**: When started consuming the source

### Optional Fields

- **rating**: Moon phase rating set by user (🌕/🌔/🌓/🌒/🌑) — only set after consuming the source
- **scientificity**: Research quality level (🅰️/🅱️/👓/📢/💬)
- **end**: When finished consuming the source
- **category/meta/problem**: Hierarchy links (see Linking Rules below)
- **creator**: Link to existing creator note in `base/creators/`
- **production**: Link to existing production note in `base/productions/`

## Linking Rules

**CRITICAL:** Only link to EXISTING notes. Use the `obsidian-structure` skill to understand the vault hierarchy.

### Finding Valid Links

Before creating a source note, dynamically discover existing system notes:

| Field      | Location             | Glob Pattern               |
| ---------- | -------------------- | -------------------------- |
| `category` | `base/categories/`   | `base/categories/*.md`     |
| `meta`     | `base/_meta-notes/`  | `base/_meta-notes/*.md`    |
| `problem`  | `base/_problems/`    | `base/_problems/*.md`      |

### Workflow

1. **Discover existing notes** — use either:
   - `obsidian files folder=base/categories ext=md` / `obsidian files folder=base/_meta-notes ext=md` (CLI, cross-platform)
   - Glob patterns from the table above (Claude built-in Glob tool)
2. **Match by relevance** — choose the most appropriate existing note based on the source's topic/domain
3. **If no match exists** — leave the field empty or ask user; NEVER create system notes
4. **Categories are human-only** — agent never creates categories
5. **Meta and problem are optional** — only fill if directly relevant to the source

## Status Values

- ⬛ — Abandoned
- 🟥 — Planned
- 🟦 — In progress
- ⚛️ — Atomizing (being broken down into independent atomic notes)
- 🟩 — Completed

## Rating Values (Moon Phases)

Rating is set by the user after consuming the source:

- 🌕 — Outstanding quality in all aspects
- 🌔 — Almost perfect, minor flaws
- 🌓 — Decent level, pros outweigh cons
- 🌒 — Below average, cons outweigh pros
- 🌑 — Very low quality

## Scientificity Values

- 🅰️ — Primary Research (original, peer-reviewed, highest quality)
- 🅱️ — Secondary Research (analytical, review, or replicative studies)
- 👓 — Expert / Industry (expert materials or industry data)
- 📢 — Popular Science / Journalism (simplified, general information)
- 💬 — Unverified / Opinion (subjective sources without quality control)

## Available Tags

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

## Examples

**Note**: Wikilinks in examples below are illustrative. When creating actual source notes, only link to notes that exist in the vault. Leave fields empty if the referenced note doesn't exist yet.

### Book

Filename: `sources/Thinking, Fast and Slow.md`

```yaml
---
tags:
  - source/book
aliases:
status: 🟩
rating: 🌕
scientificity: 🅰️
created: 2025-08-10T23:25:33+07:00
updated: 2025-08-15T18:30:00+07:00
start: 2025-08-10T23:25:33+07:00
end: 2025-08-15T18:30:00+07:00
category:
  - "[[psychology]]"
  - "[[behavioral economics]]"
creator:
  - "[[Daniel Kahneman]]"
production:
  - "[[Farrar, Straus and Giroux]]"
---

# Summary

Explores two systems of thinking: fast intuitive thinking (System 1) and slow deliberate thinking (System 2).

## Key Concepts

- Cognitive biases
- Heuristics
- Prospect theory
```

### Paper

Filename: `sources/Attention Is All You Need.md`

```yaml
---
tags:
  - source/article/paper
aliases:
status: 🟩
rating: 🌕
scientificity: 🅰️
created: 2025-08-10T23:25:33+07:00
updated: 2025-08-10T23:25:33+07:00
start: 2025-08-10T23:25:33+07:00
end: 2025-08-10T23:25:33+07:00
category:
  - "[[machine learning]]"
creator:
  - "[[Ashish Vaswani]]"
  - "[[Noam Shazeer]]"
  - "[[Niki Parmar]]"
---

# Abstract

Introduces the Transformer architecture for sequence-to-sequence tasks.

## Key Innovation

Self-attention mechanism replacing recurrent layers.
```

### Course

Filename: `sources/Introduction to Quantum Computing.md`

```yaml
---
tags:
  - source/course
aliases:
status: 🟦
rating:
scientificity: 👓
created: 2025-08-10T23:25:33+07:00
updated: 2025-08-10T23:25:33+07:00
start: 2025-08-10T23:25:33+07:00
end:
category:
  - "[[quantum computing]]"
creator:
  - "[[John Preskill]]"
production:
  - "[[Caltech]]"
---

# Course Notes

Introduction to quantum mechanics and quantum computation fundamentals.
```

### Movie

Filename: `sources/Interstellar.md`

```yaml
---
tags:
  - source/cinematic/movie
aliases:
status: 🟥
rating:
scientificity:
created: 2025-08-10T23:25:33+07:00
updated: 2025-08-10T23:25:33+07:00
start:
end:
category:
  - "[[physics]]"
creator:
  - "[[Christopher Nolan]]"
production:
  - "[[Paramount Pictures]]"
---
```

### Planned Source

Filename: `sources/Gödel, Escher, Bach.md`

```yaml
---
tags:
  - source/book
aliases:
  - GEB
status: 🟥
rating:
scientificity: 📢
created: 2025-08-10T23:25:33+07:00
updated: 2025-08-10T23:25:33+07:00
start:
end:
category:
  - "[[mathematics]]"
  - "[[philosophy]]"
creator:
  - "[[Douglas Hofstadter]]"
---
```
