---
name: note
description: 'Create regular knowledge notes in base/notes/. INVOKE whenever user wants to capture or document a concept, topic, or idea. Triggers: "create note", "new note", "note about", "write down", "document this", "запиши", "создай заметку", "новая заметка", "сохрани", "запомни", "заметка про". NOT for projects, sources, people, system notes, or flashcards.'
---

# Obsidian Notes

Create regular knowledge notes in `base/notes/` — the primary location for knowledge capture.

**Syntax validation:** Use the `markdown` skill for markdown syntax rules (wikilinks, callouts, footnotes, LaTeX, mermaid, etc.)

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

## Creating the note

`vault` below stands for `python3 .claude/_engine/vault.py`, run from the vault root.

| Need | Command |
| - | - |
| Note types and what each is for | `vault types note` |
| Fields and allowed values | `vault schema note/basic/primary` |
| Existing categories | `vault find "#system/category" --limit 100` |
| Create | `vault new note/basic/primary --title "spaced repetition" --body-file FILE` |
| Add a category tag | `--set tags=note/basic/primary --set tags=category/<name>` |

The engine fills `aliases`, `icon`, `color`, `created` and `updated`, refuses a name that is already taken, and refuses invalid values without writing. Edit the body directly afterwards; a hook validates each edit.

**Categories are human-owned.** Use only a category that exists. The tag is `category/<file name>` with spaces replaced by `_`. If none fits, leave the tag out or ask. If the user asked for the closest one, pick it and say which one you picked. Never invent one.

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
The Zettelkasten method is a knowledge management system based on networked atomic notes[^1].

Each note should contain one idea and link to related notes, forming a network of knowledge.

> [!quote]
> "A Zettelkasten is a personal tool for thinking and writing that creates an interconnected web of thought." — Sönke Ahrens

[^1]: [Introduction to the Zettelkasten Method](https://zettelkasten.de/introduction/)
```
