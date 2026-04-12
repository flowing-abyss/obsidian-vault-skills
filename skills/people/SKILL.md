---
name: people
description: 'Create notes for people and organizations. INVOKE when user wants to create a note for a person, author, company, or organization. Triggers: "create contact", "add person", "new creator", "company", "organization", "production", "author", "создай контакт", "добавь человека", "новый автор", "добавь компанию", "запиши контакт".'
---

# People

**Contact**
A contact note is a structured node representing a direct personal or professional relationship. It captures interaction history, shared context, and ongoing collaborations. Its primary purpose is to map your active network, linking individuals directly to your projects, meetings, and areas of responsibility.

**Creator**
A creator note represents an author, researcher, or public figure whose work you consume rather than interact with directly. It acts as an anchor for their intellectual output, aggregating associated source notes, methodologies, and core ideas to track their influence across your knowledge base.

**Production**
A production note represents a collective entity, platform, or publisher that produces, hosts, or distributes work. It acts as an umbrella node, grouping affiliated creators, contacts, and source materials to map the broader organizational or media ecosystem behind individual resources and ideas.

## Commands

| Action | Command |
| - | - |
| Create people note | `python3 ".claude/skills/people/scripts/people.py" create --title "Name" --tag contact/working [options]` |
| Update people note | `python3 ".claude/skills/people/scripts/people.py" update --title "Name" --tag contact/working [options]` |

Recommendation: direct editing in the note is the default way to update content. Use `update` mainly when you want to modify notes via script from any working directory.

## People Options

| Option | Explanation |
| - | - |
| `--title` | Required for `create` and `update` (note filename) |
| `--tag` | Single type-specific tag, required |
| `--alias` | Repeatable alias |
| `--description` | Short description |
| `--category`, `--meta`, `--problem` | Repeatable taxonomy links |
| `--relevant` | `true` or `false` |
| `--body` | Note body |

In `update`, only passed fields are changed. List fields replace the entire list.

## Required Body Block

Every people note must start with the tasks callout block. The script enforces this and always inserts it at the very beginning of the body if missing.

## Where To Get Names

> **Schema:** `Field` ➔ `Fast Command` ➔ `Fallback` (format: `obsidian search query="<Fallback>"`)

- `category` ➔ `rg --files -g "*.md" base/categories` ➔ `tag:system/category`
- `meta` ➔ `rg --files -g "*.md" base/_meta-notes` ➔ `tag:system/high/meta`
- `problem` ➔ `rg --files -g "*.md" base/_problems` ➔ `tag:system/high/problem`

Recommendation: request names only if the creation script returned an error or the user instructed to add links to these fields. In other cases, use default tools.

## Contact Tags

- `contact/working`
- `contact/client`
- `contact/personal`
- `contact/routine`

## Creator Tags

- `creator/writer`
- `creator/director`
- `creator/researcher`
- `creator/contentmaker`
- `creator/businessman`
- `creator/expert`
- `creator/musician`
- `creator/composer`
- `creator/actor`
- `creator/painter`
- `creator/photographer`
- `creator/cinematographer`

## Production Tags

- `production/channel`
- `production/podcast`
- `production/film_studio`
- `production/art_studio`
- `production/game_studio`
- `production/label`
- `production/band`
- `production/organization`
- `production/company`
- `production/platform`
- `production/website`
- `production/publisher`
- `production/journal`
