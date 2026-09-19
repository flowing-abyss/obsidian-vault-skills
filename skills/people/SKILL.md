---
name: people
description: 'Create notes for people and organizations. INVOKE when user wants to create a note for a person, author, company, or organization. Triggers: "create contact", "add person", "new creator", "company", "organization", "production", "author", "создай контакт", "добавь человека", "новый автор", "добавь компанию", "запиши контакт".'
---

# People

**Contact.** A direct personal or professional relationship. Captures interaction history, shared context and collaborations, and links the person to projects, meetings and areas of responsibility.

**Creator.** An author, researcher or public figure whose work you consume rather than interact with. Anchors their output: sources, methods and core ideas.

**Production.** A collective entity, platform or publisher that produces, hosts or distributes work. Groups affiliated creators, contacts and sources.

## Commands

Run from the vault root: `V="python3 .claude/_engine/vault.py"`

| Need | Command |
| - | - |
| Types and what each is for | `$V types contact` |
| Fields, allowed values and their meaning | `$V schema creator/writer` |
| Note names a link field accepts | `$V values creator/writer category --like "text"` |
| Create | `$V new creator/writer --title "Title" --set key=value [--body-file FILE]` |
| Change metadata | `$V set "Title" key=value` (lists: `add`, `remove`) |
| Validate after a direct edit | `$V check "Title"` |
| Same for the other two families | `$V types creator`, `$V types production` |

The engine reads the vault manifests, fills fixed values, defaults, `created` and `updated`, and takes the note body scaffold from the type's template. It refuses invalid input, writes nothing, and says what to fix. Correct the input. Never work around an error by writing frontmatter by hand.

- Repeat `--set key=value` to build a list. Link fields take plain note names.
- Pass only what you know. Skip a field instead of guessing a value.
- Edit the note body directly. A hook validates every edit; without hooks run `check`.

## Choosing values

- Contact, creator or production is decided by the relationship, not by fame: someone the user talks to is a contact even if they also publish.
- The title is the name as the user writes it. Put other spellings into `aliases`.
- No category fits: ask the user. If the user asked for the closest one, pick it and say which one you picked. Never invent a category.
- The tabs block at the top of the body comes from the template. Keep it when editing the body.
