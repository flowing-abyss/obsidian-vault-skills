---
name: system-notes
description: 'Create structural system notes: meta-notes (thematic hubs), problems (research questions), and hierarchies (aggregators). INVOKE when user wants to create any structural knowledge note. Triggers: "create meta-note", "create problem", "create hierarchy", "system note", "structural note", "мета-заметка", "создай мету", "проблема", "иерархия", "структурная заметка", "узел иерархии". NEVER creates categories — human-only.'
---

# System Notes

**Category**
A category serves as a high-level domain dashboard and structural container. It provides a macroscopic overview of a broad area, utilizing filtered tables and visual diagrams to map and navigate all underlying knowledge within that scope. Categories are created *manually* by the user.

**Meta-note**
A meta-note acts as a thematic hub or dynamic roadmap for in-depth research. It structures complex topics and guides exploration within a specific domain, always anchored to a parent category.

**Problem**
A problem note isolates a specific research question or conceptual challenge. It drives focused investigation on a targeted issue, drawing essential context and strict boundaries from its parent meta-note and category.

**Hierarchy**
A hierarchy note is a structural aggregator that compiles and sequences atomized notes. It transforms isolated pieces of information into a cohesive, logically linked narrative, requiring at least a parent category to maintain system order.

## Commands

| Action | Command |
| - | - |
| Create system note | `python3 ".claude/skills/system-note/scripts/system_note.py" create --title "Title" --tag system/high/meta --category "Category" [options]` |
| Update system note | `python3 ".claude/skills/system-note/scripts/system_note.py" update --title "Title" --tag system/high/meta [options]` |

Recommendation: direct editing in the note is the default way to update content. Use `update` mainly when you want to modify notes via script from any working directory.

## Options

| Option | Explanation |
| - | - |
| `--title` | Required for `create` and `update` |
| `--tag` | Required: `system/high/meta`, `system/high/problem`, `system/high/hierarchy` |
| `--category` | Required in `create`; required logically for all system notes |
| `--meta` | Required for `problem`; optional for `hierarchy` |
| `--problem` | Optional for `hierarchy` |
| `--alias` | Repeatable alias |
| `--relevant` | `true` or `false` |
| `--body` | Note body |

In `update`, only passed fields are changed. List fields replace the entire list.

## Relations

Category is required for every system note.

| Kind | Required links | Constraints |
| - | - | - |
| `meta` | `category` | Category must exist |
| `problem` | `category`, `meta` | Meta must exist and belong to the same category |
| `hierarchy` | `category` | Optional `meta` must be from same category; optional `problem` must be from same category; if both set, problem must belong to the selected meta |

This enforces the chain `Category -> Meta -> Problem -> Hierarchy`.

## Where To Get Names

> **Schema:** `Field` ➔ `Fast Command` ➔ `Fallback` (format: `obsidian search query="<Fallback>"`)

- `category` ➔ `rg --files -g "*.md" base/categories` ➔ `tag:system/category`
- `meta` ➔ `rg --files -g "*.md" base/_meta-notes` ➔ `tag:system/high/meta`
- `problem` ➔ `rg --files -g "*.md" base/_problems` ➔ `tag:system/high/problem`

Recommendation: request names only if the creation script returned an error or the user instructed to add links to these fields. In other cases, use default tools.
