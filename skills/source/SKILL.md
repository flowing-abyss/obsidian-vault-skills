---
name: sources
description: 'Create source tracking notes for books, articles, videos, papers, courses, films, podcasts, and other reference materials. INVOKE when user wants to track any content source. Triggers: "track book", "add source", "new book", "article", "video", "paper", "course", "film", "podcast", "добавь книгу", "запиши источник", "читаю книгу", "смотрю курс", "добавь статью", "добавь видео", "источник". Handles status, ratings, and scientificity levels.'
---

# Sources

A source-note is a structured container for knowledge extracted from an external resource, such as a book, paper, or video. It serves as an anchor for highlights, quotes, and your initial interpretations. Its primary purpose is to distill outside information into accessible insights, providing a reliable reference point that fuels ongoing projects and feeds the knowledge base.

## Commands

| Action | Command |
| - | - |
| Create source | `python3 ".claude/skills/source/scripts/source.py" create --title "Title" [options]` |
| Update source | `python3 ".claude/skills/source/scripts/source.py" update --title "Title" [options]` |

Recommendation: direct editing in the note is the default way to update content. Use `update` mainly when you want to modify notes via script from any working directory.

## Source Options

| Option | Explanation |
| - | - |
| `--title` | Required for `create` and `update` |
| `--tag` | Single source type tag (required in `create`) |
| `--alias` | Repeatable alias |
| `--status` | Source status |
| `--rating` | Subjective rating |
| `--scientificity` | Evidence-quality level |
| `--category`, `--meta`, `--problem` | Repeatable taxonomy links |
| `--creator`, `--production` | Repeatable links |
| `--start`, `--end` | Source dates (YYYY-MM-DD) |
| `--body` | Note body |

In `update`, only passed fields are changed. List fields replace the entire list.

## Where To Get Names

> **Schema:** `Field` ➔ `Fast Command` ➔ `Fallback` (format: `obsidian search query="<Fallback>"`)

- `category` ➔ `rg --files -g "*.md" base/categories` ➔ `tag:system/category`
- `meta` ➔ `rg --files -g "*.md" base/_meta-notes` ➔ `tag:system/high/meta`
- `problem` ➔ `rg --files -g "*.md" base/_problems` ➔ `tag:system/high/problem`
- `creator` ➔ `rg --files -g "*.md" base/creators base/contacts` ➔ `tag:creator OR tag:contact`
- `production` ➔ `rg --files -g "*.md" base/productions` ➔ `tag:production`

Recommendation: request names only if the creation script returned an error or the user instructed to add links to these fields. In other cases, use default tools.

## Statuses

| Status | Meaning |
| - | - |
| `⬛` | Abandoned |
| `🟥` | ToDo |
| `🟦` | In Progress |
| `⚛️` | Atomizing |
| `🟩` | Done |

## Ratings

| Rating | Meaning |
| - | - |
| `🌕` | Excellent |
| `🌔` | Very Good |
| `🌓` | Good |
| `🌒` | Weak |
| `🌑` | Poor |

## Scientificity

| Level | Meaning |
| - | - |
| `🅰️` | Primary research |
| `🅱️` | Secondary research |
| `👓` | Expert/industry |
| `📢` | Popular science |
| `💬` | Opinion/unverified |

## Tags

- `source/article/paper`
- `source/article/resource`
- `source/book`
- `source/course`
- `source/cinematic/movie`
- `source/cinematic/series`
- `source/cinematic/anime`
- `source/podcast`
- `source/video/recording`
- `source/video/playlist`
- `source/music/album`
- `source/music/tracklist`
- `source/game`
