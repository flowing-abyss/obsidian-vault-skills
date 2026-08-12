---
name: note
description: 'Create regular knowledge notes in base/notes/. INVOKE whenever user wants to capture or document a concept, topic, or idea. Triggers: "create note", "new note", "note about", "write down", "document this", "запиши", "создай заметку", "новая заметка", "сохрани", "запомни", "заметка про". NOT for projects, sources, people, system notes, or flashcards.'
---

# Obsidian Notes

Create regular knowledge notes in `base/notes/` — the primary location for knowledge capture.

**Syntax validation:** Use `obsidian-markdown` skill for markdown syntax rules (wikilinks, callouts, footnotes, LaTeX, mermaid, etc.)

## Filename Rules

**CRITICAL:** Follow all naming conventions strictly.

| Rule | Description |
|-|-|
| **Uniqueness** | Each filename must be unique across the entire vault |
| **Specificity** | Avoid abstractions; use precise, concrete terms |
| **Case** | Lowercase only. Exception: proper nouns (e.g., `Zettelkasten`, `Python`) |
| **Structure** | Nouns or stable noun phrases only |
| **Forbidden** | No dates, numbers, questions, or pronouns |
| **Compatibility** | Use only filesystem-safe characters |

### Examples

| Correct | Incorrect | Reason |
|-|-|-|
| `spaced repetition.md` | `Spaced Repetition.md` | Lowercase (not a proper noun) |
| `Zettelkasten method.md` | `zettelkasten method.md` | Zettelkasten is a proper noun (Luhmann's system) |
| `Python decorator.md` | `python decorator.md` | Python is a proper noun |
| `knowledge graph.md` | `how does knowledge graph work.md` | No questions |
| `sorting algorithm.md` | `my sorting algorithm.md` | No pronouns |
| `binary search.md` | `binary search 1.md` | No numbers |

## Category Validation

**CRITICAL:** Only use EXISTING categories. Categories are human-created and managed.

### Finding Valid Categories

Before assigning a category tag, discover existing categories:

| Field | Location | Glob Pattern |
|-|-|-|
| `category` | `base/categories/` | `base/categories/*.md` |

### Workflow

1. **Discover existing categories** — use either:
   - `obsidian files folder=base/categories ext=md` (CLI, cross-platform)
   - Glob pattern: `base/categories/*.md` (Claude built-in Glob tool)
2. **Match by relevance** — choose the most appropriate existing category for the note's topic
3. **If no match exists** — omit the category tag or ask user; NEVER invent categories
4. **Category tag format** — `category/<folder_name>` where `<folder_name>` matches the category note filename (without `.md`)

## Frontmatter Template

```yaml
---
tags:
  - note/basic/primary
  - category/<existing_category>  # Optional — only if relevant category exists
aliases: []
created: 2025-08-10T23:25:33+07:00
updated: 2025-08-10T23:25:33+07:00
---
```

### Frontmatter Rules

- **Date format:** ISO 8601 with timezone offset (`YYYY-MM-DDTHH:mm:ssZ`)
- **Required tag:** One of the note type tags (see below)
- **Optional tag:** `category/<name>` — only if category exists (replace spaces with `_` in category name)

### Tag Taxonomy

Fetch current valid note type tags from manifests:
```bash
obsidian eval code="app.vault.getMarkdownFiles().filter(f=>f.path.startsWith('templates/create/notes')&&f.basename==='manifest').map(f=>{const m=(app.metadataCache.getFileCache(f)?.frontmatter?.target?.query||'').match(/#([\w/-]+)/);return m&&m[1].includes('/')?m[1]:null}).filter(Boolean).sort().join(', ')"
```

Additionally: `category/<name>` — assign to existing category (validate first!).

## Content Principles

- **Self-contained:** Note should be understandable without extra context
- **Atomic:** One idea per note
- **Source references:** Use footnotes for URLs and citations

### Visual Emphasis

In this vault, `**bold**` renders **red** and `*italic*` renders *green*, so both create strong color contrast. Treat them as semantic signals, not decoration:

- Keep plain text as the default. Emphasize only what materially helps the reader find the main conclusion, distinction, warning, or action.
- Use bold for the strongest focal point, usually no more than one short fragment in a compact paragraph or list item. Do not bold whole paragraphs or restyle headings inside their text.
- Use italics for a local nuance, contrast, term, or brief aside. Do not alternate bold and italics merely to create rhythm.
- Avoid combined `***bold italic***`, underlining, and several competing colored fragments in the same sentence unless the notation itself requires them.
- Before saving, scan the note at a glance. If several accents compete for attention, remove formatting until the intended reading hierarchy is immediately clear.

Overloaded: `**Threshold detects the signal**, *Strength controls the amount*, **change them carefully**.`

Balanced: `Threshold detects the signal; Strength controls the amount. **Change one parameter at a time.**`

## Example Note

Filename: `base/notes/zettelkasten method.md`

```markdown
---
tags:
  - note/basic/primary
  - category/productivity  # Only if base/categories/productivity.md exists!
aliases: []
created: 2025-08-10T23:25:33+07:00
updated: 2025-08-10T23:25:33+07:00
---

The Zettelkasten method is a knowledge management system based on networked atomic notes[^1].

Each note should contain one idea and link to related notes, forming a network of knowledge.

> [!quote]
> "A Zettelkasten is a personal tool for thinking and writing that creates an interconnected web of thought." — Sönke Ahrens

[^1]: [Introduction to the Zettelkasten Method](https://zettelkasten.de/introduction/)
```
