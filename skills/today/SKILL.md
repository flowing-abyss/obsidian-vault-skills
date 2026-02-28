---
name: today
description: "Proactive daily briefing system. Creates today's daily note if missing, writes a briefing block with seed idea, relevant vault links, project connections, and open threads directly into the note — without asking questions. INVOKE when user wants to start their day or get unstuck. Triggers: 'today', 'start my day', 'daily', 'unstuck', 'kick me', 'feed', 'project feed', 'briefing', 'что писать', 'начни день', 'дай идею', 'чем заниматься'. NOT for regular note creation or task management."
---

# Today

Proactive daily briefing system. Doesn't ask — acts. Scans the vault,
generates ideas, finds useful materials, and writes everything directly
into the daily note.

## Philosophy

The old approach (ask questions, wait for user to respond) doesn't work.
The user stalls on self-generation. Asking more questions just adds another
thing to stall on.

**New approach:** Do the work. Write a ready-made briefing into the daily note
with ideas, links, and connections. The user opens the note and sees material
to react to — not a blank page and not a question hanging in the air.

**Principle:** AI is a scout, not an interrogator. It goes ahead, finds what's
useful, lays it out, and gets out of the way. The user's job is to react,
edit, develop — not to generate from zero.

## Daily Note Format

**Path:** `periodic/daily/YYYY-MM-DD.md`

**Frontmatter:**
```yaml
---
tags:
  - periodic/day
up:
  - "[[periodic/weekly/YYYY-WWW|YYYY-WWW]]"
created: YYYY-MM-DDTHH:mm:ss+HH:MM
updated: YYYY-MM-DDTHH:mm:ss+HH:MM
reviewed: false
cssclasses:
  - hide-backlinks
---
```

**Week computation:** ISO 8601 week number. Use `obsidian eval` (cross-platform):
```bash
# Current week
obsidian eval code="(function(){const d=new Date();const dt=new Date(Date.UTC(d.getFullYear(),d.getMonth(),d.getDate()));const day=dt.getUTCDay()||7;dt.setUTCDate(dt.getUTCDate()+4-day);const y=dt.getUTCFullYear();const ys=new Date(Date.UTC(y,0,1));const w=Math.ceil(((dt-ys)/86400000+1)/7);return y+'-W'+String(w).padStart(2,'0')})()"

# Specific date (e.g. 2026-02-10)
obsidian eval code="(function(){const d=new Date('2026-02-10');const dt=new Date(Date.UTC(d.getFullYear(),d.getMonth(),d.getDate()));const day=dt.getUTCDay()||7;dt.setUTCDate(dt.getUTCDate()+4-day);const y=dt.getUTCFullYear();const ys=new Date(Date.UTC(y,0,1));const w=Math.ceil(((dt-ys)/86400000+1)/7);return y+'-W'+String(w).padStart(2,'0')})()"
```

## Execution Flow

```
User: "today" / "start my day" / "kick me" / "feed" / "briefing"
    |
1. Get today's date (YYYY-MM-DD)
    |
2. Check: does periodic/daily/YYYY-MM-DD.md exist?
   - NO  -> create it with frontmatter
   - YES -> read its content
    |
3. INBOX MIGRATION — collect all #task/inbox from past daily notes:
   a. Grep for "#task/inbox" in periodic/daily/*.md (exclude today)
   b. Collect all matching task lines (full line, preserving formatting)
   c. DELETE those lines from source notes (Edit tool)
   d. Hold collected tasks for briefing callout (Inbox section)
    |
4. Gather context (ALL of this, in parallel where possible):
   a. Read last 3-5 daily notes
   b. Find active projects (status 🟥 or 🟦), read their content
   c. Read 5-10 recently modified vault notes (base/, sources/)
   d. Find 2-3 old notes (30+ days) connected to recent themes
   e. Search for open tasks and stated intentions in recent entries (obsidian search)
   f. Read current week's weekly note (periodic/weekly/YYYY-WWW.md) if it exists —
      specifically text BELOW the [!weekly-review]- callout (user's stated weekly focus).
      This tells you what the user committed to this week. Use it to align the seed
      and materials with their actual declared intention.
    |
5. Generate briefing content:
   a. SEED — one sharp idea/thought/connection based on vault context
   b. MATERIALS — relevant vault links organized by usefulness
   c. PROJECT FEED — connections for active projects
   d. THREADS — unfinished business from recent days
    |
6. WRITE the briefing directly into the daily note (append after existing content)
    |
7. Brief confirmation in chat (1-2 lines max)
```

## Inbox Migration

Every run, collect ALL unchecked `#task/inbox` tasks from past daily notes
and move them to today's note. This is the GTD "process inbox" step — automated.

### Process

1. **Find inbox tasks:**
```bash
obsidian search:context query="task-todo:#task/inbox" path=periodic/daily  # open inbox tasks only
```

2. **Filter:**
   - Only from daily notes BEFORE today (not from today's note itself)
   - Only unchecked tasks (`- [ ]`), skip completed (`- [x]`)
   - Preserve the FULL task line (tags, categories, priorities, dates, links, subtasks)

3. **Collect task lines** from each source file. Example task formats:
```markdown
- [ ] #task/inbox Add Espanso script to Gists
- [ ] #task/inbox #category/public Record video about X
- [ ] #task/inbox #priority/a Urgent task 📅 2026-02-15
```

4. **Delete from source notes:**
   - Use Edit tool to remove each collected task line from its source file
   - If a task has subtasks (indented lines below it), move those too
   - If removing a task leaves trailing blank lines, clean them up
   - After deletion, check if the source note is now empty (only frontmatter,
     no text, no tasks, only whitespace after `---`). If so — DELETE the file entirely

5. **Include in briefing callout:**
   - Inbox tasks go INSIDE the briefing callout as the first section (`**Inbox:**`)
   - Each task line prefixed with `> ` to be part of the callout
   - Subtasks prefixed with `> ` + their original indentation
   - Preserve original formatting (tags, priorities, dates, links)

### Subtask handling

Some inbox tasks have subtasks (indented lines). Move the entire block.
Inside the callout it looks like:
```markdown
> - [ ] #task/inbox #task/multistep #category/public Record video
> 	- [ ] ⤵️ Prepare outline
> 	- [ ] ⤵️ Record audio
```
All indented lines following a `#task/inbox` line belong to that task.
Each line gets `> ` prefix to stay inside the callout.

### Edge cases

- **No inbox tasks found** — skip this step silently, don't mention it
- **Tasks already in today's note** — don't duplicate; if a task with identical
  text already exists in today, skip it
- **Multiple tasks from same file** — remove all of them, do a single edit per file
- **Empty note after deletion** — if a past daily note has ONLY frontmatter left
  (no text, no tasks, no content — just YAML between `---` and whitespace),
  delete the file with `rm`. "Empty" = nothing meaningful after the closing `---`
- **Never delete today's note** — only past daily notes get cleaned up

---

## Context Gathering

Use `obsidian` CLI and built-in tools (Glob, Read, Grep) directly. Gather broadly — the more
context, the better the briefing.

### Recent daily notes
```bash
obsidian files folder=periodic/daily ext=md   # list all daily notes
```
Read the most recent 3-5 entries (newest by name, since names are YYYY-MM-DD). Extract:
- Unfinished thoughts, trailing sentences
- Recurring themes across entries
- Stated intentions ("need to", "want to", "planning to")
- What the user was thinking about / working on

### Active projects
```bash
# Via CLI search — use [property: value] syntax for frontmatter:
obsidian search query="[status: 🟦]" path=projects
obsidian search query="[status: 🟥]" path=projects
```
For each active project:
1. Read the project index file (the one with `status:` in frontmatter)
2. Extract: title, description, `category`/`meta`/`problem` links, existing [[wikilinks]]
3. Build a keyword/topic profile from the project content
4. Collect all wikilinks already present -> KNOWN connections (skip these)

### Recent vault activity
```bash
obsidian recents   # recently opened files (cross-platform, replaces Glob sort by mtime)
```
Also use Glob for broader scoping:
```
Glob: base/notes/**/*.md   -> 5-10 newest by modification time
Glob: sources/**/*.md      -> 3-5 newest by modification time
Glob: base/additions/**/*.md -> 3-5 newest by modification time
```
Read titles and first ~50 lines to understand what's being worked on.

### Old notes for resurrection
```
Find notes 30+ days old whose topics intersect with recent daily themes or active projects.
```

### Open threads
```bash
# Open tasks in daily notes — use task-todo:/task-done: operators:
obsidian search:context query="task-todo:#task/inbox" path=periodic/daily   # open inbox tasks only
obsidian search query="- [ ]" path=periodic/daily                          # any open task (no tag)
```

## Briefing Structure

The briefing is written directly into the daily note as a collapsible callout.
Appended AFTER any existing content in the note.

### Format

```markdown
> [!briefing]- Briefing
> **Inbox:**
> - [ ] #task/inbox Add Espanso script to Gists
> - [ ] #task/inbox #category/public Record video about X
>
> **Seed:** [One provocative idea/thought/connection — see Seed Generation below]
>
> **Materials:**
> - [[note title]] — [why it's relevant today, 5-10 words]
> - [[source title]] — [what's useful in it]
> - [[old note]] — [why it's worth revisiting]
>
> **Projects:**
> - [[Project A]] 🟦: see [[note X]] — [how it helps]
> - [[Project B]] 🟥: see [[note Y]], [[source Z]] — [connection]
>
> **Threads:**
> - [open task or stated intention] — [[periodic/daily/YYYY-MM-DD|date]]
```

### Rules

1. **Always write into the note** — never just output to chat
2. **Callout block** — use `> [!briefing]-` (collapsed by default, `-` suffix)
3. **Append, don't overwrite** — add after existing content with a blank line separator
4. **If briefing already exists** in today's note — don't duplicate. Either update it or skip
5. **Each section optional** — skip sections with no content (don't write empty headers)
6. **Minimum viable briefing** — at least a Seed + one other section
7. **Every reference = direct wikilink** — NEVER use vague references like "in the entry from 05.02", "in some note", "recently in the journal". Always use concrete `[[wikilinks]]`:
   - Daily note → `[[periodic/daily/2026-02-05|entry 05.02]]`
   - Regular note → `[[note title]]`
   - Source → `[[source title]]`
   - Project → `[[project title]]`
   - If you reference an idea, quote, or task — link directly to the note where it lives

## Seed Generation

The seed is the core of the briefing — one sharp thought that gives the user
something to react to. NOT a question. A statement, idea, or connection.

### Seed Types (pick the strongest match)

**1. Synthesis** — connect two vault notes the user hasn't connected
```
[[Note A]] talks about X. [[Note B]] describes Y.
Both are instances of the same pattern: [pattern]. This could mean [implication].
```

**2. Contradiction** — surface a tension between notes or between note and behavior
```
In [[note]] you wrote "[quote]". But your last 5 journal entries show [opposite behavior].
Either the principle is wrong or you're not applying it.
```

**3. Idea extension** — take a recent thought and push it further
```
Your idea about [X] from [[periodic/daily/2026-02-05|05.02]] has an unexplored implication:
if [X] is true, then [Y] should also follow. That would mean [Z].
```

**4. Resource highlight** — surface a forgotten source with a specific useful insight
```
In [[source title]], [author] argues [specific point] — directly applicable to
what you've been writing about [topic] in [[periodic/daily/2026-02-08|08.02]].
```

**5. Project insight** — generate a concrete idea for an active project
```
For [[project]]: section [X] could be strengthened by approaching it from
the angle of [concept from vault note]. Specifically: [concrete suggestion].
```

**6. Pattern recognition** — identify a recurring pattern across recent activity
```
Looking at the last week: you keep returning to [theme] from different angles
([[note1]], [[note2]], journal entries). There's an unwritten note here about [concept].
```

### Seed Meta-rules

- **Specific** — quote notes, cite exact ideas, reference real vault content
- **Assertive** — state something, don't ask. Give the user something to agree with, challenge, or develop
- **Concise** — 2-4 sentences max
- **Grounded** — must come from actual vault content, not generic advice
- **One seed only** — don't scatter across multiple ideas
- **Weekly-aware** — if the user wrote a weekly focus in the weekly note (step 4f), prefer seed types that connect to or extend that focus. Don't ignore stated intention — either support it or surface a productive tension with it.

## Materials Section

Find 2-5 vault notes the user should look at today. Each with a reason.

### Selection criteria (in priority order)
1. **Directly relevant to active project** — note matches project themes but isn't linked
2. **Connected to recent journal themes** — user has been thinking about this topic
3. **Forgotten resource** — source note not touched in 30+ days, relevant to current work
4. **Contradiction or challenge** — note that contradicts recent thinking (worth addressing)
5. **Unfinished addition** — experiment/report/log that was started but not developed

### What NOT to include
- Notes already linked in today's entry or recent entries
- Notes the user is actively editing (they already know about them)
- Weak matches just to fill space — better to have 2 strong links than 5 weak ones

## Project Feed Section

For each active project (🟥/🟦), find vault notes that could help but aren't linked.

### Matching strategies (priority order)
1. **Shared hierarchy** — note and project share `category`/`meta`/`problem`
2. **Keyword match** — note title/content contains project's key terms
3. **Cross-project pollination** — note used in project A, relevant to project B
4. **Source match** — source covers topic discussed in project, not referenced

### Rules
- Max 2-3 connections per project
- Each must explain WHY it's useful (not just "related")
- Skip projects with no matches — don't force it
- Exclude notes already wikilinked in the project

## Threads Section

Collect unfinished business from recent daily notes:
- Open tasks (`- [ ]`) with dates
- Stated intentions ("need to", "want to") not yet acted on
- Thoughts that trailed off

Keep to 2-3 most important threads. Don't dump the entire backlog.

## Anti-patterns

- Outputting the briefing to chat instead of writing to the note
- Asking questions instead of giving material
- Generic advice or inspiration ("set your intention for the day")
- Overwhelming the note with 10+ links
- Including notes the user is already actively working with
- Writing seeds based on general knowledge instead of vault content
- Duplicating a briefing that already exists in today's note
- Soft, coaching language ("consider exploring...", "you might want to...")
- **Vague references without wikilinks** — never write "in the entry from 05.02" or "in a recent note". Always `[[periodic/daily/2026-02-05|05.02]]` or `[[note title]]`

## Output to Chat

After writing into the note, confirm in chat. Keep it minimal:

```
Briefing written to periodic/daily/2026-02-11.md

Inbox: 3 tasks moved (from 2026-02-09, 2026-02-08).
Seed: connection between [[X]] and [[Y]].
3 materials, 2 project links, 1 open thread.
```

If the note didn't exist — mention it was created:

```
Created periodic/daily/2026-02-11.md with briefing.

Inbox: 1 task moved (from 2026-02-09).
Seed: your idea about [X] has an unexplored angle.
4 materials, 1 project link, 2 threads.
```

If no inbox tasks were found, omit the "Inbox:" line entirely.

## Language

Detect writing language from the 5 most recent daily notes: count Cyrillic vs Latin characters in non-frontmatter, non-wikilink, non-tag text. If Cyrillic > 30% → write in Russian. Otherwise → English.

Match the user's register — casual journal, casual briefing. The briefing reads like something a trusted colleague left on the desk, not a formal report.

## Resources

- **Seed and feed patterns:** See references/prompts.md
