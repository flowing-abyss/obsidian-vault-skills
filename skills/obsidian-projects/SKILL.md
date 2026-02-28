---
name: obsidian-projects
description: 'Create and manage project notes in projects/ with status tracking, priorities, and task management. Two types: single (one file) and longform (folder + scenes). INVOKE when user wants to start, create, or manage a project. Triggers: "create project", "new project", "project note", "track project", "создай проект", "новый проект", "веду проект", "запусти проект", "проектная заметка", "longform", "chapters", "scenes". NOT for regular notes or tasks.'
---

# Obsidian Projects

Create project management notes in `projects/` directory. Two project types:

| Type | Tag | Structure | Use case |
|------|-----|-----------|----------|
| **Single** | `project/single` | `projects/name.md` | Simple projects, one-file scope |
| **Longform** | `project/longform` | `projects/name/name.md` + scenes | Complex projects with multiple parts/chapters |

**Default behavior:** Always create **Single** project unless user explicitly requests longform/multi-part/chapters/scenes.

**Triggers for Longform:**
- "longform project", "multi-part", "chapters", "scenes"
- "book", "novel", "series", "course", "curriculum"
- "create folder structure", "separate files for each part"

---

# Single Projects

## Frontmatter Template

```yaml
---
tags:
  - project/single
aliases:
status: 🟥
priority: 🇨
cover:
created: 2025-08-10T23:25:33+07:00
updated: 2025-08-10T23:25:33+07:00
start:
end:
category:
  - "[[category name]]"
meta:
  - "[[meta note name]]"
problem:
  - "[[problem name]]"
creator:
production:
url:
---
```

## Frontmatter Fields

- **status**: ⬛ (abandoned), 🟥 (planned), 🟦 (in progress), 🟩 (completed, not published), 📢 (published)
- **priority**: 🇦 (critical & urgent), 🇧 (important, not urgent), 🇨 (normal), 🇩 (delegated), 🇪 (review or delete)
- **dates**: ISO 8601 format with timezone
- **category/meta/problem**: optional hierarchy links (see Linking Rules below)
- **creator/production**: optional people links — **MUST use existing notes**, never create new ones
- **url**: optional external link

## Linking Rules

**CRITICAL:** Only link to EXISTING notes. Use the `obsidian-structure` skill to understand the vault hierarchy.

### Finding Valid Links

Before creating a project note, dynamically discover existing system notes:

| Field      | Location             | Glob Pattern               |
| ---------- | -------------------- | -------------------------- |
| `category` | `base/categories/`   | `base/categories/*.md`     |
| `meta`     | `base/_meta-notes/`  | `base/_meta-notes/*.md`    |
| `problem`  | `base/_problems/`    | `base/_problems/*.md`      |

### Workflow

1. **Discover existing notes** — use either:
   - `obsidian files folder=base/categories ext=md` / `obsidian files folder=base/_meta-notes ext=md` (CLI, cross-platform)
   - Glob patterns from the table above (Claude built-in Glob tool)
2. **Match by relevance** — choose the most appropriate existing note based on the project's domain/field
3. **If no match exists** — leave the field empty or ask user; NEVER create system notes
4. **Categories are human-only** — agent never creates categories
5. **Meta and problem are optional** — only fill if directly relevant to the project

## Heading Statuses

Headings inside project notes can have statuses to track progress of individual sections. Format: `# Status Heading Name`

| Status | Name | Description |
|--------|------|-------------|
| ⬛ | abandoned | Section abandoned or archived; no longer relevant |
| 🟥 | todo/queue | Just created; planned direction with nothing else yet |
| 💡 | idea | Few sentences or simple diagram explaining the approach |
| 🧠 | brainstorming | Expanding initial idea; adding details or related ideas |
| 🔎 | research | Need additional research; have sources/notes to process |
| 🟦 | wip | Actively developing; found the right direction |
| 📋 | revising | Done with content; reviewing, proofreading, or restructuring |
| 🖍 | editing | Full editing pass; fixing errors; ready for feedback/critique |
| 🟩 | completed | Fully done and edited; pending distribution |
| 📦 | preparation | Adapting to platform/journal/service rules; ready to compile |
| 📢 | distributed | Published, presented, contributed |

**When to use:** Apply these statuses when user asks to plan a project structure, track section progress, or explicitly requests heading statuses.

**Typical flow:** 🟥 → 💡 → 🧠 → 🔎 → 🟦 → 📋 → 🖍 → 🟩 → 📦 → 📢

## Required Body Structure

Every project note MUST include these sections verbatim:

```markdown
> [!toc]- Table of contents
> ```table-of-contents
> ```

> [!todo]- Tasks
> ```tasks
> path includes {{query.file.path}}
> group by heading
> hide task count
> ```

# Description
```

## Example Single Project

Filename: `projects/Website Redesign.md`

```yaml
---
tags:
  - project/single
aliases:
status: 🟦
priority: 🇦
created: 2025-08-10T23:25:33+07:00
updated: 2025-08-10T23:25:33+07:00
start: 2025-08-01T00:00:00+07:00
end:
category:
  - "[[web development]]"
url: https://example.com
---

> [!toc]- Table of contents
> ```table-of-contents
> ```

> [!todo]- Tasks
> ```tasks
> path includes {{query.file.path}}
> group by heading
> hide task count
> ```

# Description

Complete redesign of company website with modern UI/UX.

# 🟩 Design Phase

## 📢 Wireframes

Low-fidelity mockups for all main pages.

## 🟩 Visual Design

Final UI designs with brand colors and typography.

# 🟦 Development Phase

## 🟦 Frontend

- [ ] Implement responsive layouts
- [ ] Add animations and transitions

## 🔎 Backend Integration

Need to research best API approach for new features.

# 🟥 Testing & Launch

## 🟥 QA Testing

Planned comprehensive testing before launch.

## 💡 Launch Strategy

Soft launch to beta users, then full rollout.
```

---

# Longform Projects

For complex projects with multiple parts, chapters, or scenes. Creates a folder structure.

## Folder Structure

```
projects/
└── Project Name/
    ├── Project Name.md    # Index file (main project note)
    ├── Chapter 1.md       # Scene files
    ├── Chapter 2.md
    └── ...
```

## Longform Frontmatter Template

```yaml
---
tags:
  - project/longform
aliases: []
status: 🟥
priority: 🇨
cover:
longform:
  format: scenes
  title: Project Name
  workflow: Default Workflow
  sceneFolder: /
  scenes: []
  sceneTemplate: templates/create/projects/longform scene template.md
  ignoredFiles: []
created: 2025-08-10T23:25:33+07:00
updated: 2025-08-10T23:25:33+07:00
start:
end:
category:
  - "[[category name]]"
meta:
  - "[[meta note name]]"
problem:
  - "[[problem name]]"
creator:
production:
url:
---
```

## Longform-specific Fields

- **longform.format**: `scenes` (standard format)
- **longform.title**: Project title for Longform plugin
- **longform.workflow**: `Default Workflow`
- **longform.sceneFolder**: `/` (scenes in same folder as index)
- **longform.scenes**: Array of scene filenames (managed by plugin)
- **longform.sceneTemplate**: Path to scene template
- **longform.ignoredFiles**: Files to exclude from project

## Required Body Structure (Longform)

Longform projects have an additional callout for scene tasks:

```markdown
> [!toc]- Table of contents
> ```table-of-contents
> ```

> [!todo]- Tasks
> ```tasks
> path includes {{query.file.path}}
> group by heading
> hide task count
> ```

> [!todo]- Scene tasks
> ```tasks
> path includes {{query.file.folder}}
> path does not include {{query.file.path}}
> group by backlink
> hide task count
> ```

# Description
```

## Scene Template

Scenes are separate files in the project folder with `mark/scene` tag:

```yaml
---
tags:
  - mark/scene
up:
  - "[[project name]]"
status: 🟥
created: 2025-08-10T23:25:33+07:00
updated: 2025-08-10T23:25:33+07:00
---
```

- **up**: Link to parent project (index file)
- **status**: Uses heading statuses (⬛, 🟥, 💡, 🧠, 🔎, 🟦, 📋, 🖍, 🟩, 📦, 📢)

## Example Longform Project

Folder: `projects/My Novel/`

Index file: `projects/My Novel/My Novel.md`

```yaml
---
tags:
  - project/longform
aliases: []
status: 🟦
priority: 🇧
longform:
  format: scenes
  title: My Novel
  workflow: Default Workflow
  sceneFolder: /
  scenes:
    - chapter 1
    - chapter 2
    - chapter 3
  sceneTemplate: templates/create/projects/longform scene template.md
  ignoredFiles: []
created: 2025-08-10T23:25:33+07:00
updated: 2025-08-10T23:25:33+07:00
start: 2025-08-01T00:00:00+07:00
category:
  - "[[writing]]"
---

> [!toc]- Table of contents
> ```table-of-contents
> ```

> [!todo]- Tasks
> ```tasks
> path includes {{query.file.path}}
> group by heading
> hide task count
> ```

> [!todo]- Scene tasks
> ```tasks
> path includes {{query.file.folder}}
> path does not include {{query.file.path}}
> group by backlink
> hide task count
> ```

# Description

A novel about...

# 🟦 Plot Outline

## 🟩 Act 1

Setup and introduction of characters.

## 🟦 Act 2

Rising action and conflict.

## 🔎 Act 3

Need to research satisfying endings.
```

Scene file: `projects/My Novel/Chapter 1.md`

```yaml
---
tags:
  - mark/scene
up:
  - "[[My Novel]]"
status: 🟩
created: 2025-08-10T23:25:33+07:00
updated: 2025-08-10T23:25:33+07:00
---

Chapter content goes here...
```
