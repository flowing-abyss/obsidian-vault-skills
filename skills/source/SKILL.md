---
name: source
description: 'Create source tracking notes for books, articles, videos, papers, courses, films, podcasts, and other reference materials. INVOKE when user wants to track any content source. Triggers: "track book", "add source", "new book", "article", "video", "paper", "course", "film", "podcast", "добавь книгу", "запиши источник", "читаю книгу", "смотрю курс", "добавь статью", "добавь видео", "источник". Handles status, ratings, and scientificity levels.'
---

# Sources

A source note is a structured container for knowledge extracted from an external resource, such as a book, paper, or video. It anchors highlights, quotes, and first interpretations, and gives projects and knowledge notes a reliable reference point.

## Commands

Run from the vault root: `V="python3 .claude/_engine/vault.py"`

| Need | Command |
| - | - |
| Types and what each is for | `$V types source` |
| Fields, allowed values and their meaning | `$V schema source/book` |
| Note names a link field accepts | `$V values source/book creator --like "text"` |
| Create | `$V new source/book --title "Title" --set key=value [--body-file FILE]` |
| Change metadata | `$V set "Title" key=value` (lists: `add`, `remove`) |
| Validate after a direct edit | `$V check "Title"` |

The engine reads the vault manifests, fills fixed values, defaults, `created` and `updated`, and takes the note body scaffold from the type's template. It refuses invalid input, writes nothing, and says what to fix. Correct the input. Never work around an error by writing frontmatter by hand.

- Repeat `--set key=value` to build a list. Link fields take plain note names.
- Pass only what you know. Skip a field instead of guessing a value.
- Edit the note body directly. A hook validates every edit; without hooks run `check`.

## Choosing values

- Pick the most specific type from `types source`. The parent type `source` alone is reported as incomplete.
- `status`, `rating` and `scientificity` each come with a meaning per value in `schema`. Set `rating` and `scientificity` only when the user gave a judgment or the source makes it evident.
- `creator` and `production` may name notes that do not exist yet. Create those through the `people` skill when the user wants them.
- In `schema`, "key must exist, may be empty" means exactly that: leave the value empty when you do not know it.
- No category fits: ask the user. If the user asked for the closest one, pick it and say which one you picked. Never invent a category.
- `meta` must belong to one of the note's categories, and `problem` to one of its metas. A write that breaks this is refused. Use `values ... --given category="name"` to list what fits.
