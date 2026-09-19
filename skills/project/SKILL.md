---
name: project
description: 'Create and manage project notes. Two types: single and longform. INVOKE when user asks to create or update a project note. Triggers: "create project", "new project", "project note", "update project", "создай проект", "обнови проект", "longform", "chapters", "scenes".'
---

# Projects

A project is a finite unit of work with a clear objective, a deliverable that defines "done", and an end. System notes (categories, meta-notes, problems, hierarchies) never end; a project always does.

For project tasks use the `task-note` skill.

## Commands

Run from the vault root: `V="python3 .claude/_engine/vault.py"`

| Need | Command |
| - | - |
| Types and what each is for | `$V types project` |
| Fields, allowed values and their meaning | `$V schema project/single` |
| Note names a link field accepts | `$V values project/single category --like "text"` |
| Create | `$V new project/single --title "Title" --set key=value [--body-file FILE]` |
| Change metadata | `$V set "Title" key=value` (lists: `add`, `remove`) |
| Validate after a direct edit | `$V check "Title"` |
| Add a scene to a longform project | `$V new mark/scene --title "Scene" --set up="Project Title" --set status=🟥` |

The engine reads the vault manifests, fills fixed values, defaults, `created` and `updated`, and takes the note body scaffold from the type's template. It refuses invalid input, writes nothing, and says what to fix. Correct the input. Never work around an error by writing frontmatter by hand.

- Repeat `--set key=value` to build a list. Link fields take plain note names.
- Pass only what you know. Skip a field instead of guessing a value.
- Edit the note body directly. A hook validates every edit; without hooks run `check`.

## Choosing values

- No category fits: ask the user. If the user asked for the closest one, pick it and say which one you picked. Never invent a category.
- Set `priority`, `start` and `end` only when the user gave them.

## Choosing a type

`types project` describes each. In short: `single` for compact work in one note, `longform` for a long work split into scenes, `short` for one short published piece.

A longform project is placed in its own folder `projects/<Title>/<Title>.md`. A scene is placed in that folder and added to the project's scene list. Both are done by the engine; do not move files or edit the `longform` block by hand.

## Heading and scene statuses

Headings inside a project body and longform scenes carry a status emoji:

`⬛` abandoned, `🟥` todo, `💡` idea, `🧠` brainstorming, `🔎` research, `🟦` in progress, `📋` revising, `🖍` editing, `🟩` completed, `📦` preparation, `📢` distributed.

```markdown
# 🟦 Drafting
## 🔎 References
## 🟩 Final structure
```
