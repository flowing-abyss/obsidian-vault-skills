---
name: task-note
description: >
  Manage project task notes in Obsidian vault.
  INVOKE when user wants to: create, read, find, update a task.
  Triggers (EN): "create task", "add task to project", "find task", "update task", "take task".
  Triggers (RU): "создай задачу", "найди задачу", "обнови задачу", "читай задачу", "бери задачу".
  NOT for inline tasks — use task-inline skill instead.
---

# Task Notes

A task note is a standalone note in `base/tasks` linked to a project. Its id (`PREFIX-NUMBER`) is computed from the project, it inherits category, meta and problem from the project, and `related` links are kept two way.

## Constraints

1. Change task metadata only through `vault.py set`, `add`, `remove`. Never write task frontmatter by hand and never use `sed` or `awk` on it. The id counter and the two way links depend on it.
2. Never set `id` yourself.
3. Find tasks only with `vault.py find`. It prints paths, not content. Do not read more than one task in full unless the user asks; many tasks overflow the context.
4. If a command returns an error, fix the input or report the error to the user. Do not fall back to manual editing.

## Commands

Run from the vault root: `V="python3 .claude/_engine/vault.py"`

| Need | Command |
| - | - |
| Fields, allowed values and their meaning | `$V schema task/default` (milestones: `task/milestone`) |
| Find tasks | `$V find "#task AND project=[[Project]] AND status=🟦" --show id,status,priority` |
| Find one task by id | `$V find "id=OV-12"`, then read that one file |
| Milestones of a project | `$V values task/default milestone --given project="Project"` |
| Create | `$V new task/default --title "Title" --set project="Project" [--set key=value] [--body-file FILE]` |
| Change metadata | `$V set OV-12 status=🟩` (a task id, a title or a path all work; lists: `add`, `remove`) |
| Rename | `obsidian rename path="<path>" name="<new title>"` (never `mv`: it breaks backlinks). Needs Obsidian running with this vault. If it fails, tell the user. |

`find` queries combine `#tag`, `key=value`, `key=` (empty), `key<value`, `AND`, `OR`, `-` (not).

The engine reads the vault manifests, fills fixed values, defaults, `created` and `updated`, and takes the note body scaffold from the type's template. It refuses invalid input, writes nothing, and says what to fix. Correct the input. Never work around an error by writing frontmatter by hand.

- Repeat `--set key=value` to build a list. Link fields take plain note names.
- Pass only what you know. Skip a field instead of guessing a value.
- Edit the note body directly. A hook validates every edit; without hooks run `check`.

## Choosing values

- `project` is required. Without it there is no id and the engine refuses the task.
- `status` and `priority` have defaults. Set them only when the user said so. Meanings are in `schema`.
- `blockedBy` means this task cannot start before the other one ends; the engine warns when dates contradict it.
- Change only the fields the user asked to change.
