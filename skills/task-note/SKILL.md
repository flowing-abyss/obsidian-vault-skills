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

## ABSOLUTE CONSTRAINTS — NEVER VIOLATE

1. NEVER edit structured fields (status, priority, dates, links, or any metadata)
   by writing to the file directly. The ONLY permitted method is task.py script.
2. NEVER use `grep` / `find` / `cat` / `ls` on `base/tasks` — they produce incorrect results.
3. NEVER load more than one task's full content without explicit user request.
4. If task.py is unavailable or returns an error — report it to the user and STOP.
   Do NOT attempt manual metadata editing as a fallback. Ever.

Violating these rules silently corrupts vault consistency and breaks backlinks.

---

CONTEXT OVERFLOW PREVENTION: Discovery pipelines return file paths only.
Never pipe discovery results to awk unless the user explicitly asks for full content.
Loading 20+ tasks at once will overflow the context window.

ONLY the pipelines below are permitted for reading base/tasks.

## READ / FIND — Decision Tree

**Single task needed?** → Use RETRIEVAL (returns full content)
**Multiple tasks needed?** → Use DISCOVERY (returns paths only — DO NOT load content unless user asks)

**Environment:**
→ Shell available (`rg`, `awk`, `xargs`) → use **Bash Pipeline**
→ No shell tools → use **Obsidian Fallback** (requires Obsidian to be open)

### RETRIEVAL — Single Task (full content)

By ID:
- Bash: `rg -l '^id:\s*"?<ID>"?\s*$' -g "*.md" base/tasks | xargs -I {} awk 'FNR==1{print "=== " FILENAME " ==="} {print}' "{}"`
- Fallback: `obsidian search query='/^id:\s*"?<ID>"?\s*$/'`

By Title:
- Bash: `rg --files -g "*.md" base/tasks | rg "<Title>" | xargs -I {} awk 'FNR==1{print "=== " FILENAME " ==="} {print}' "{}"`
- Fallback: `obsidian search query="file:<Title>" path=base/tasks`

### DISCOVERY — Multiple Tasks (paths only)

By Project:
- Bash: `rg -l "\[\[<Project>.*\]\]" -g "*.md" base/tasks`
- Fallback: `obsidian search query="[project:<Project>]" path=base/tasks`

By Milestone:
- Bash: `rg -l "\[\[<Milestone>.*\]\]" -g "*.md" base/tasks`
- Fallback: `obsidian search query="[milestone:<Milestone>]" path=base/tasks`

Get project milestones:
- Bash: `rg -l '  - task/milestone$' -g "*.md" base/tasks | xargs -I {} rg -l "\[\[<Project>.*\]\]" "{}"`
- Fallback: `obsidian search query="tag:task/milestone [project:<Project>]" path=base/tasks`

By Status:
- Bash: `rg -l '^status:\s*<Status>\s*$' -g "*.md" base/tasks`
- Fallback: `obsidian search query='[status:<Status>]' path=base/tasks`

By Priority:
- Bash: `rg -l '^priority:\s*<Priority>\s*$' -g "*.md" base/tasks`
- Fallback: `obsidian search query='[priority:<Priority>]' path=base/tasks`

By Project + Status:
- Bash: `rg -l "\[\[<Project>.*\]\]" -g "*.md" base/tasks | xargs -I {} rg -l '^status:\s*<Status>\s*$' "{}"`
- Fallback: `obsidian search query="[project:<Project>] [status:<Status>]" path=base/tasks`

By Project + Priority:
- Bash: `rg -l "\[\[<Project>.*\]\]" -g "*.md" base/tasks | xargs -I {} rg -l '^priority:\s*<Priority>\s*$' "{}"`
- Fallback: `obsidian search query="[project:<Project>] [priority:<Priority>]" path=base/tasks`

By Project + Status + Priority:
- Bash: `rg -l "\[\[<Project>.*\]\]" -g "*.md" base/tasks | xargs -I {} rg -l '^status:\s*<Status>\s*$' "{}" | xargs -I {} rg -l '^priority:\s*<Priority>\s*$' "{}"`
- Fallback: `obsidian search query="[project:<Project>] [status:<Status>] [priority:<Priority>]" path=base/tasks`

**To extract IDs from discovery results**, pipe to:
```bash
| xargs -I {} rg --no-line-number -o '^id:\s*"?(.+?)"?\s*$' -r '$1' "{}"
```

## CREATE / UPDATE

### Forbidden actions

- NEVER edit status, priority, dates, links, or any metadata field directly in the file.
- NEVER use `sed`, `awk`, or any text replacement on task frontmatter.
- The ONLY permitted method to mutate structured fields is `task.py`.

### Checklist before every UPDATE

Before running any update, confirm:
- [ ] I am using task.py — not direct file editing
- [ ] I have the task ID or exact title
- [ ] I am only changing fields the user explicitly requested

### Updating a task

→ Changing note body or free-form content → edit the file directly
→ Changing any structured field (status, priority, dates, links, metadata) → ONLY via script:

```bash
python3 ".claude/skills/task-note/scripts/task.py" update (--id OVN-5 | --title "Title") [options]
```

### Creating a task

```bash
python3 ".claude/skills/task-note/scripts/task.py" create --title "Title" --project "ProjectName" [options]
```

Script validates all field values and returns an error if a value is invalid.

**If the script returns an error:** report it to the user verbatim. Do NOT attempt workarounds.

### Renaming a task

ONLY via Obsidian CLI (preserves vault backlinks):
```bash
obsidian rename path="<current_file_path>" name="<new_title_without_extension>"
```

NEVER use shell `mv` — breaks vault backlinks.
NEVER use script `--title` for renaming — it is a lookup parameter, not a rename.

### Options

| Option | Notes |
|-|-|
| `--id` | One of two lookup options for `update` |
| `--title` | Required for `create`; can also be used for `update` lookup instead of `--id` |
| `--project` | Required for create |
| `--tag` | `task/default` or `task/milestone` |
| `--status` | See statuses below |
| `--priority` | See priorities below |
| `--description` | Short description |
| `--attribute` | Repeatable plain-text label |
| `--milestone`, `--related`, `--blocked-by` | Repeatable links |
| `--category`, `--meta`, `--problem` | Repeatable; inherited from project — omit unless overriding |
| `--creator`, `--production` | Repeatable links |
| `--url` | Repeatable; format: `[Name](https://...)` |
| `--start`, `--end` | YYYY-MM-DD |
| `--body` | Note body |

`update`: only passed fields change. List fields replace entire list.
If both `--start` and `--end` are passed, validation checks the new pair only.
If only one of them is passed, validation checks it against the persisted opposite date.

### Tags

| Value | Meaning |
|-|-|
| `task/default` | Normal task |
| `task/milestone` | Milestone task that can be used in other tasks' `milestone` field |

### Statuses

| Value | Meaning |
|-|-|
| `⬛` | Abandoned / Duplicated |
| `📥` | Inbox |
| `🟥` | ToDo |
| `🟦` | In Progress |
| `❄` | Hold / Blocked |
| `🟩` | Done |
| `📢` | Published |

### Priorities

| Value | Meaning |
|-|-|
| `🇦` | Critical & urgent |
| `🇧` | Important, not urgent |
| `🇨` | Normal |
| `🇩` | Delegated |
| `🇪` | Review or delete |

## Resolve Field Names

Run only if create script returns an error or user specifies explicit links.

- `project`
  - Bash: `rg -l "  - project/" -g "*.md" projects`
  - Fallback: `obsidian search query="tag:project"`
- `category`
  - Bash: `rg --files -g "*.md" base/categories`
  - Fallback: `obsidian search query="tag:system/category"`
- `meta`
  - Bash: `rg --files -g "*.md" base/_meta-notes`
  - Fallback: `obsidian search query="tag:system/high/meta"`
- `problem`
  - Bash: `rg --files -g "*.md" base/_problems`
  - Fallback: `obsidian search query="tag:system/high/problem"`
- `creator`
  - Bash: `rg --files -g "*.md" base/creators base/contacts`
  - Fallback: `obsidian search query="tag:creator OR tag:contact"`
- `production`
  - Bash: `rg --files -g "*.md" base/productions`
  - Fallback: `obsidian search query="tag:production"`
- `milestone`
  - Bash: `rg -l0 "  - task/milestone" -g "*.md" base/tasks | xargs -0 rg -l "<project>"`
  - Fallback: `obsidian search query="tag:task/milestone [project:<project>]"`
