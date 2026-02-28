---
name: obsidian-tasks
description: 'Create and format GTD tasks with proper #task/ and #category/ tags. INVOKE when user wants to capture, create, or manage any task. Triggers: "add task", "create task", "todo", "inbox", "next action", "waiting for", "someday", "one-off", "idea", "добавь задачу", "запомни задачу", "нужно сделать", "создай таск", "поставь в очередь", "делегировал", "когда-нибудь", "следующее действие", "в инбокс".'
---

# Task Creator

Create tasks in the correct format for Obsidian GTD system.

## Task Format

```
- [ ] #task/TYPE #category/CATEGORY Description
```

## Task Types

Task type definitions are stored in `periodic/statuses/*.md` files (based on GTD methodology).

| Type | Use When |
|------|----------|
| `inbox` | Quick capture, not yet processed |
| `next_action` | Priority task to do immediately |
| `one-off` | Simple task, single action |
| `multistep` | Project with subtasks |
| `waiting_for` | Delegated or awaiting external action |
| `regular` | Recurring task |
| `idea` | Fleeting thought or inspiration |
| `reference` | Resource to study/read later |
| `someday` | Maybe/later, no specific timeframe |

## Categories

**CRITICAL:** Categories are dynamic and stored in `base/categories/*.md` files. Never hardcode category names.

### Finding Valid Categories

Before creating tasks, dynamically discover existing categories:

| Field      | Location           | Glob Pattern             |
| ---------- | ------------------ | ------------------------ |
| `category` | `base/categories/` | `base/categories/*.md`   |

### Workflow

1. **Discover existing categories** — use either:
   - `obsidian files folder=base/categories ext=md` (CLI, cross-platform)
   - Glob pattern: `base/categories/*.md` (Claude built-in Glob tool)
2. **Extract category tag** from filename (e.g., `artificial_intelligence.md` → `#category/artificial_intelligence`)
3. **Match by relevance** — choose the most appropriate existing category based on task context
4. **If no match exists** — omit category tag or ask user; NEVER invent categories
5. **Categories are human-only** — agent never creates categories

## Optional Prefixes

Add after category tag if needed:

- **Priority**: `#priority/a` (critical) to `#priority/e` (low)
- **Time**: `#time/quick`, `#time/moderate`, `#time/lengthy`, `#time/long`
- **Effort**: `#effort/easy`, `#effort/medium`, `#effort/hard`

## Date/Time Suffixes

Add at end of task:

- Due date: `📅 YYYY-MM-DD`
- Scheduled time: `⏰ HH:MM`
- Reminder: `💬` before description for tasks needing verbal action

## Examples

```markdown
- [ ] #task/inbox Разобраться с новым плагином
- [ ] #task/one-off #category/marketing Подготовить презентацию
- [ ] #task/next_action #category/development #priority/a Исправить баг в API
- [ ] #task/waiting_for #category/household Попросить починить кран 📅 2026-02-01
- [ ] #task/regular #category/health Тренировка в зале
- [ ] #task/reference #category/productivity Посмотреть видео про GTD | https://example.com
- [ ] #task/one-off #category/study 💬 Сдать документы на кафедру ⏰ 15:00 📅 2026-02-10
```

## Task Creation Workflow

1. **Discover categories**: Use `Glob base/categories/*.md` to list available categories
2. **Match category**: Choose most relevant category for the task context
3. **Determine type**: If unclear → use `inbox`
4. **Handle unknown category**: Ask user or omit category tag; never invent
5. For links/videos → prefer `reference` type
6. For ideas without action → use `idea`
