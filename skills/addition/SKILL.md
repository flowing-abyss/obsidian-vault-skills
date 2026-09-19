---
name: additions
description: 'Create supplementary materials attached to existing notes: experiments, meetings, reports, logs, conspectuses, practice sessions, annotations, AI outputs, links collections. Two-step process: (1) create aggregator space, (2) create concrete addition in base/additions/. INVOKE when user wants to attach any supplementary material to an existing note. Triggers: "addition", "create addition", "experiment", "meeting notes", "report", "conspectus", "log", "practice", "annotations", "links", "link collection", "аддишн", "конспект", "встреча", "отчёт", "эксперимент", "практика", "аннотации", "ссылки", "добавь к заметке".'
---

# Obsidian Additions

Supplementary material attached to an existing note, on two levels.

- **Aggregator.** A container note that groups the additions of one kind for one parent note. The parent links to it from its `addition` property.
- **Concrete addition.** One experiment, meeting, report, conspectus and so on. The aggregator lists it in its body.

## Commands

`vault` below stands for `python3 .claude/_engine/vault.py`, run from the vault root.

| Need | Command |
| - | - |
| Addition types and what each is for | `vault types mark/addition` and `vault types mark/log` |
| Fields, allowed values and their meaning | `vault schema mark/addition/experiment` |
| Create an aggregator | `vault new mark/addition/aggregator --title "<parent> - <kind>"` |
| Link it from the parent | see the block below |
| Create a concrete addition | `vault new mark/addition/meeting --title "<parent> (YYYY-MM-DD) - meeting" --set project="<parent>"` |
| Create a conspectus | `vault new mark/log/conspectus --title "descriptive name" --set source="<source note>"` |

```bash
vault add "<parent>" addition="[[<parent> - <kind>|<emoji>]]"
```

The engine picks the folder, fills fixed values, defaults and timestamps, and refuses invalid input without writing. Fix the input it names. Never write frontmatter by hand to get around an error.

## Workflow

1. Find the parent note and confirm it exists: `vault find "..."` or `vault check "<parent>"`.
2. Pick the type from `vault types mark/addition`. Ask the user when two types fit.
3. Look for an existing aggregator before creating one: `vault find "#mark/addition/aggregator" --limit 200` and match the parent title.
4. Create the aggregator, then link it from the parent with `add`. `add` appends and keeps every existing entry.
5. Create the concrete addition and add `- [[its title]]` to the aggregator body.

## Naming

- Aggregator: `<parent note title> - <kind in plural>`, for example `Deep Learning - conspectuses`.
- Concrete addition: `<parent note title> (YYYY-MM-DD) - <kind>`, for example `My Project (2025-08-10) - meeting`.
- Conspectus: a descriptive lowercase name instead of a date, for example `introduction to computer architecture`.
- The emoji in the parent's `addition` link is the icon of the addition type, shown by `vault types`.

## Special cases

- **Conspectus.** Also copy the parent source's type tag and `category/...` tags: `--set tags=mark/log/conspectus --set tags=<source type> --set tags=category/<name>`. Start the body with a table of contents callout.
- **Links collection.** Links live directly in the aggregator body, grouped in collapsed callouts. No concrete additions are needed.

```markdown
> [!abstract]- 💬 Chat & Inference
> - [Groq](https://groq.com/) · fast inference
> - [OpenRouter](https://openrouter.ai/) · model aggregator
```

- The aggregator body is freeform. The user organizes it.
