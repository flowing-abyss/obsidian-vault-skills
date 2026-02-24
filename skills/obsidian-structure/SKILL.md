---
name: obsidian-structure
description: 'Reference for Obsidian vault directory layout, restricted directories, and the knowledge hierarchy (Category → Meta-note → Problem → Hierarchy). INVOKE when user asks about vault organization, where files live, which directories exist, or what can be modified. Triggers: "structure", "organization", "what folders", "where to put", "hierarchy", "directory", "DO NOT MODIFY", "куда положить", "какие папки", "структура хранилища", "где находится", "что можно изменять".'
---

# Obsidian Structure

Provides knowledge about the Obsidian vault directory structure, hierarchical organization, and modification restrictions.

## DO NOT MODIFY

These directories and files are human-only. Never create, edit, or delete anything inside them:

- `base/categories/` — global category definitions
- `home/databases/`
- `home/prefixes.md`
- `templates/`
- `classes/`
- `periodic/statuses/`

## Directory Map

| Path                | Contents                                      | Agent creates here? |
| ------------------- | --------------------------------------------- | ------------------- |
| `base/notes/`       | Knowledge notes                               | **YES — primary**   |
| `base/_hierarchy/`  | Hierarchical aggregator notes                 | Yes                 |
| `base/_meta-notes/` | Thematic hubs / roadmaps                      | Yes                 |
| `base/_problems/`   | Specific research questions                   | Yes                 |
| `base/contacts/`    | People notes                                  | Yes                 |
| `base/creators/`    | Creator / author profiles                     | Yes                 |
| `base/productions/` | Companies / organizations                     | Yes                 |
| `base/additions/`   | Experiments, meetings, reports                | Yes                 |
| `base/categories/`  | Global directions                             | **NO**              |
| `sources/`          | Books, articles, videos, papers               | Yes                 |
| `projects/`         | Project management notes                      | Yes                 |
| `periodic/`         | Daily / weekly / monthly / quarterly / yearly | Yes                 |
| `files/`            | Images, PDFs, attachments                     | Yes (files only)    |

## Knowledge Hierarchy

The vault organizes knowledge through a strict dependency chain:

```
Category → Meta-note → Problem → Hierarchy
```

- **Category** — the base unit. Human-only — agent never creates these.
	- **Meta-note** — must link to exactly one existing category.
		- **Problem** — must link to exactly one existing meta-note AND must use the **same category** as that meta-note.
- **Hierarchy** — can link to a category, a meta-note, or a problem. When linking to a meta-note or problem, always use the same category they belong to.
