---
name: obsidian-people
description: 'Create notes for people and organizations in three directories: contacts (base/contacts/), creators (base/creators/), productions (base/productions/). INVOKE when user wants to create a note for a person, author, company, or organization. Triggers: "create contact", "add person", "new creator", "company", "organization", "production", "author", "создай контакт", "добавь человека", "новый автор", "добавь компанию", "запиши контакт". NOT for regular notes or projects.'
---

# Obsidian People Notes

Create notes for people, creators, and organizations. Three types with identical structure but different tags and directories.

## Filename Convention

**IMPORTANT:** Use Title Case for names — capitalize the first letter of each word.

- Correct: `John Smith.md`, `Андрей Иванов.md`, `Apple Inc.md`
- Incorrect: `john smith.md`, `андрей иванов.md`, `apple inc.md`

## Note Types

### Contact (`base/contacts/`)
Personal and professional connections.

**Tags:** `contact/working`, `contact/client`, `contact/personal`, `contact/routine`

### Creator (`base/creators/`)
Individual content creators, artists, and experts.

**Tags:** `creator/writer`, `creator/director`, `creator/researcher`, `creator/contentmaker`, `creator/businessman`, `creator/expert`, `creator/musician`, `creator/composer`, `creator/actor`, `creator/painter`, `creator/photographer`, `creator/cinematographer`

### Production (`base/productions/`)
Companies, organizations, channels, studios.

**Tags:** `production/channel`, `production/podcast`, `production/film_studio`, `production/art_studio`, `production/game_studio`, `production/label`, `production/band`, `production/organization`, `production/company`, `production/platform`, `production/publisher`, `production/journal`

## Linking Rules

**CRITICAL:** Only link to EXISTING notes. Use the `obsidian-structure` skill to understand the vault hierarchy.

### Finding Valid Links

Before creating a people note, dynamically discover existing system notes:

| Field      | Location             | Glob Pattern               |
| ---------- | -------------------- | -------------------------- |
| `category` | `base/categories/`   | `base/categories/*.md`     |
| `meta`     | `base/_meta-notes/`  | `base/_meta-notes/*.md`    |
| `problem`  | `base/_problems/`    | `base/_problems/*.md`      |

### Workflow

1. **Discover existing notes** — use either:
   - `obsidian files folder=base/categories ext=md` / `obsidian files folder=base/_meta-notes ext=md` (CLI, cross-platform)
   - Glob patterns from the table above (Claude built-in Glob tool)
2. **Match by relevance** — choose the most appropriate existing note based on the person's domain/field
3. **If no match exists** — leave the field empty or ask user; NEVER create system notes
4. **Categories are human-only** — agent never creates categories
5. **Meta and problem are optional** — only fill if directly relevant to the person

## Shared Frontmatter Template

```yaml
---
tags:
  - <type/subtype>
aliases:
description:
category:
  - "[[category name]]"
meta:
  - "[[meta note name]]"
problem:
  - "[[problem name]]"
relevant: false
created: 2025-08-10T23:25:33+07:00
updated: 2025-08-10T23:25:33+07:00
---
```

## Required Body Structure

Every people note MUST include this task management section verbatim:

```markdown
> [!todo]- tasks (`$=dv.pages().file.tasks.where(t => !t.completed).where(t => dv.func.contains(t.outlinks, dv.current().file.link)).length`)
> > [!info]+ mentions
> > ```dataviewjs
> > dv.taskList(dv.pages().file.tasks
> >  .where(t => !t.completed)
> >  .where(t => !t.text.includes("#task/waiting_for"))
> >  .where(t => dv.func.contains(t.outlinks, dv.current().file.link))
> >  .groupBy(t => ""))
> > ```
>
> > [!check]+ delegated
> > ```dataviewjs
> > dv.taskList(dv.pages().file.tasks
> >  .where(t => !t.completed)
> >  .where(t => t.text.includes("#task/waiting_for"))
> >  .where(t => dv.func.contains(t.outlinks, dv.current().file.link))
> >  .groupBy(t => ""))
> > ```
```

## Examples

### Contact Example

Filename: `base/contacts/John Smith.md`

```yaml
---
tags:
  - contact/working
aliases:
  - John
description: Senior developer at TechCorp
category:
  - "[[<existing category>]]"  # Find via: Glob base/categories/*.md
meta:
  - "[[<existing meta-note>]]"  # Find via: Glob base/_meta-notes/*.md
relevant: false
created: 2025-08-10T23:25:33+07:00
updated: 2025-08-10T23:25:33+07:00
---

> [!todo]- tasks (`$=dv.pages().file.tasks...`)
[... task sections ...]
```

### Creator Example

Filename: `base/creators/Jane Doe.md`

```yaml
---
tags:
  - creator/writer
aliases:
description: Science fiction author
category:  # Optional — leave empty if no relevant category exists
meta:  # Optional — leave empty if no relevant meta-note exists
relevant: false
created: 2025-08-10T23:25:33+07:00
updated: 2025-08-10T23:25:33+07:00
---

> [!todo]- tasks (`$=dv.pages().file.tasks...`)
[... task sections ...]
```

### Production Example

Filename: `base/productions/Acme Studios.md`

```yaml
---
tags:
  - production/film_studio
aliases:
  - ACME
description: Independent film production company
category:
  - "[[<existing category>]]"
meta:
problem:  # Optional — only if directly relevant
relevant: false
created: 2025-08-10T23:25:33+07:00
updated: 2025-08-10T23:25:33+07:00
---

> [!todo]- tasks (`$=dv.pages().file.tasks...`)
[... task sections ...]
```
