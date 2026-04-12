---
name: project
description: 'Create and manage project notes. Two types: single and longform. INVOKE when user asks to create or update a project note. Triggers: "create project", "new project", "project note", "update project", "создай проект", "обнови проект", "longform", "chapters", "scenes".'
---

# Projects

A project is a finite unit of work with a clear objective and a deadline. It has a defined deliverable – a specific outcome that determines when the work is done. Unlike system notes (categories, meta-notes, problems, and hierarchies), a project always ends.

For project tasks, use the separate `task-note` skill, which creates standalone task notes linked to a project.

## Project Types

| Type | Meaning |
| - | - |
| `single` | Standard project: compact work in one project context |
| `longform` | Extended project with separate scenes/parts |

## Commands

| Action | Command |
| - | - |
| Create project | `python3 ".claude/skills/project/scripts/project.py" create --title "Title" [options]` |
| Update project | `python3 ".claude/skills/project/scripts/project.py" update --title "Title" [options]` |
| Create scene in longform project | `python3 ".claude/skills/project/scripts/project.py" create-scene --project "Project Title" --title "Scene Title" [options]` |
| Update scene in longform project | `python3 ".claude/skills/project/scripts/project.py" update-scene --project "Project Title" --title "Scene Title" [options]` |

Recommendation: direct editing in the note is the default way to update content. Use `update` or `update-scene` mainly when you want to modify notes via script from any working directory.

## Project Options

| Option | Explanation |
| - | - |
| `--title` | Project title for `create` and `update` |
| `--type single/longform` | Project type. Default: `single` |
| `--status` | Current project status (see Statuses table) |
| `--priority` | Project priority (see Priorities table) |
| `--category`, `--meta`, `--problem` | Repeatable list fields. Links must exist |
| `--creator`, `--production` | Repeatable list fields. Links must exist |
| `--url` | Repeatable field. Markdown link only: `[Name](https://...)` |
| `--start`, `--end` | Project dates |
| `--body` | Note body |

## Where To Get Names

> **Schema:** `Field` ➔ `Fast Command` ➔ `Fallback` (format: `obsidian search query="<Fallback>"`)

- `project` ➔ `rg -l "  - project/longform" -g "*.md" projects` ➔ `tag:project/longform`
- `category` ➔ `rg --files -g "*.md" base/categories` ➔ `tag:system/category`
- `meta` ➔ `rg --files -g "*.md" base/_meta-notes` ➔ `tag:system/high/meta`
- `problem` ➔ `rg --files -g "*.md" base/_problems` ➔ `tag:system/high/problem`
- `creator` ➔ `rg --files -g "*.md" base/creators base/contacts` ➔ `tag:creator OR tag:contact`
- `production` ➔ `rg --files -g "*.md" base/productions` ➔ `tag:production`

Recommendation: request names only if the creation script returned an error or the user instructed to add links to these fields. In other cases, use default tools.

## Scene Options

| Option | Explanation |
| - | - |
| `--title` | Scene title |
| `--project` | Longform project title |
| `--status` | Scene status. In `update-scene`, this is one of two updatable fields |
| `--body` | Scene body. In `update-scene`, this is one of two updatable fields |

## Statuses

| Status | Meaning |
| - | - |
| `⬛` | Abandoned |
| `🟥` | Todo |
| `🟦` | In Progress |
| `🟩` | Completed |
| `📢` | Published |

## Priorities

| Priority | Meaning |
| - | - |
| `🇦` | Critical & urgent |
| `🇧` | Important, not urgent |
| `🇨` | Normal |
| `🇩` | Delegated |
| `🇪` | Review or delete |

## Heading and Scene Statuses

| Status | Meaning |
| - | - |
| `⬛` | Abandoned |
| `🟥` | Todo / queue |
| `💡` | Idea |
| `🧠` | Brainstorming |
| `🔎` | Research |
| `🟦` | Work in progress |
| `📋` | Revising |
| `🖍` | Editing |
| `🟩` | Completed |
| `📦` | Preparation |
| `📢` | Distributed |

Example:

```markdown
# 🟦 Drafting
## 🔎 References
## 🟩 Final structure
```

The same heading statuses can be used inside longform scenes.
