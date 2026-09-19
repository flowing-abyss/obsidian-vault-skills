---
name: system-notes
description: 'Create structural system notes: meta-notes (thematic hubs), problems (research questions), and hierarchies (aggregators). INVOKE when user wants to create any structural knowledge note. Triggers: "create meta-note", "create problem", "create hierarchy", "system note", "structural note", "мета-заметка", "создай мету", "проблема", "иерархия", "структурная заметка", "узел иерархии". NEVER creates categories — human-only.'
---

# System Notes

**Category.** A high-level domain dashboard. Categories are created and edited only by the user. Never create, edit, rename or delete them.

**Meta-note.** A thematic hub or roadmap for in-depth research, anchored to a parent category.

**Problem.** A specific research question or conceptual challenge. Takes context and boundaries from its parent meta-note and category.

**Hierarchy.** A structural aggregator that sequences atomized notes into a linked narrative. Needs at least a parent category.

## Commands

Run from the vault root: `V="python3 .claude/_engine/vault.py"`

| Need | Command |
| - | - |
| Types and what each is for | `$V types system/high` |
| Fields, allowed values and their meaning | `$V schema system/high/problem` |
| Note names a link field accepts | `$V values system/high/problem meta --like "text"` |
| Create | `$V new system/high/problem --title "Title" --set key=value [--body-file FILE]` |
| Change metadata | `$V set "Title" key=value` (lists: `add`, `remove`) |
| Validate after a direct edit | `$V check "Title"` |

The engine reads the vault manifests, fills fixed values, defaults, `created` and `updated`, and takes the note body scaffold from the type's template. It refuses invalid input, writes nothing, and says what to fix. Correct the input. Never work around an error by writing frontmatter by hand.

- Repeat `--set key=value` to build a list. Link fields take plain note names.
- Pass only what you know. Skip a field instead of guessing a value.
- Edit the note body directly. A hook validates every edit; without hooks run `check`.

## The chain

`Category -> Meta -> Problem -> Hierarchy`. Always set `category`. A problem also needs `meta`. The engine refuses a write where the meta does not belong to the category or the problem to the meta; list valid names with `values system/high/problem meta --given category="name"`.

If no existing category fits, stop and ask the user. Do not pick a loose match and do not propose creating one yourself.
