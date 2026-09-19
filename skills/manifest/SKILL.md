---
name: manifest
description: >
  Read, explain, design, and troubleshoot vault `manifest.md` schemas for Metadata Validator.
  INVOKE when the user needs to find which manifest and field types apply to a note, design a manifest for a new note type, or diagnose validation-panel errors.
  Triggers (EN): "manifest.md", "Metadata Validator", "which manifest applies", "field types for this note", "new note type manifest", "validator panel errors".
  Triggers (RU): "манифест заметки", "какой манифест применяется", "типы полей этой заметки", "манифест нового типа заметок", "ошибки панели валидатора".
  NOT for ordinary note creation, generic frontmatter/properties edits, or vault organization.
---

# Manifest

The source of truth is the concrete `templates/create/**/manifest.md` files. Read them before explaining or proposing metadata.

## How to work

1. Read the affected note's path and frontmatter, or the manifest named by the user.
2. Find its matching leaf manifest and read every `manifest.md` above it. For a new type, also read one or two sibling leaves.
3. Explain the effective fields and where each comes from. Do not infer a type from a property name: `url`, for example, appears as `text`, `list`, and `url`.
4. Propose the smallest change that follows the parent and siblings. Check which existing notes it would affect.

Return: matching manifest → parent chain → effective fields → problem or proposed change.

Treat `templates/` as architecture. On the first pass, inspect the relevant files, explain the proposed change, its consequences, and any safer alternative; do not edit. After one explicit follow-up approval, apply the agreed change without asking again unless its scope changes. Do not run bulk auto-fix unless the user asks.

## Inheritance

Folder nesting is the schema hierarchy. A child inherits its parent's fields, replaces a same-named field as a whole, and can remove one with `exclude`. An empty intermediate manifest only continues the chain.

```yaml
# abridged from templates/create/notes/manifest.md
name: ⭕ note
enforce_folder: base/notes
target:
  query: "#note"
fields:
  aliases:
    type: list
    required: true
```

```yaml
# templates/create/notes/basic/evergreen/manifest.md
name: 🌲 Evergreen
target:
  query: "#note/basic/evergreen AND -#note/discourse"
fields:
  icon:
    type: text
    required: true
    hidden: true
    fixed: 🌲
  color:
    type: text
    required: true
    hidden: true
    fixed: "#2a8a40"
```

The leaf inherits `aliases` and changes only its own fields. `target.query` uses tags or quoted paths with `AND`, `OR`, and `-` for exclusion. `enforce_folder` gives the destination for matching notes.

```yaml
target:
  query: '"base/contacts" OR #contact'
```

`exclude: [milestone]` removes an inherited field. When a child defines `formatting.property_order`, list the complete desired order.

```yaml
formatting:
  property_order: [tags, aliases, deck, cssclasses, icon, color, created, updated, sr-due, sr-interval, sr-ease]
```

## Fields by example

Only keys inside `fields` define properties on matched notes. Other recognized top-level keys configure the schema; unrelated keys such as `tags` describe the manifest note itself. The current manifests use all ten field types and the controls shown here:

```yaml
fields:
  description:
    type: text
    label: 🪪 Description
    required: true

  focus: { type: number, min: 0, max: 10 }

  status:
    type: select
    default: 📥
    options:
      - { value: 📥, label: "📥 Inbox" }
      - { value: 🟩, label: "🟩 Done" }

  tags:
    type: multiselect
    sort: alphabetical-desc
    strict: false
    options:
      source:
        # Minimal options.source.js example.
        js: 'return ["mark/approved", "mark/bookmark"].map(v => ({ value: v, label: v }))'

  aliases: { type: list, sort: alphabetical }
  published: { type: date }
  next: { type: link }

  creator:
    type: multilink
    validate_exists: false
    source:
      js: 'return dv.pages("#creator").map(p => ({ value: p.file.name, label: p.file.name }))'

  reviewed: { type: boolean, default: false }
  cover: { type: url }

  icon:
    type: text
    hidden: true
    fixed: 🧪
```

`options` lists allowed values. `options.source.js` builds choices dynamically for `select` and `multiselect`. In current manifests, field-level `source.js` builds valid targets for `multilink`. `strict: false` permits values outside current options; links must resolve unless `validate_exists: false`.

`required` requires the property. `default` fills an empty value; `fixed` overwrites it. `hidden` hides a field in the editor, `sort` orders lists, and `min`/`max` constrain numbers.

## Validation problems

Read the reported manifest, its parent chain, and a few affected notes.

- Many identical errors point to the schema or an unfinished migration; a few outliers usually point to note data.
- For choices, compare stored values with `options`. For links, check `source` and whether the target note exists.
- For missing fields, add a default only when the note type has a real default.
- Before changing `target.query` or `enforce_folder`, check which notes would start matching or moving.

Report the cause, affected paths, smallest safe fix, and migration consequences.
