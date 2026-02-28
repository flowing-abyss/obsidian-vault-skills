---
name: obsidian-cli
description: Interact with Obsidian vaults using the Obsidian CLI to read, create, search, and manage notes, tasks, properties, and more. Also supports plugin and theme development with commands to reload plugins, run JavaScript, capture errors, take screenshots, and inspect the DOM. Use when the user asks to interact with their Obsidian vault, manage notes, search vault content, perform vault operations from the command line, or develop and debug Obsidian plugins and themes.
---

# Obsidian CLI

Use the `obsidian` CLI to interact with a running Obsidian instance. Requires Obsidian to be open.

**REQUIRES:** Obsidian 1.12+ with CLI enabled: Settings → General → Command line interface.

## PATH Setup

On macOS, Obsidian adds itself to `.zprofile` when you enable the CLI:
```bash
export PATH="$PATH:/Applications/Obsidian.app/Contents/MacOS"
```

In Claude Code Bash tool sessions (non-login shell), source it explicitly or use the full path:
```bash
# Option A: set PATH inline
export PATH="/Applications/Obsidian.app/Contents/MacOS:$PATH" && obsidian <command>

# Option B: full path
/Applications/Obsidian.app/Contents/MacOS/Obsidian <command>
```

For brevity, all examples below assume `obsidian` is in PATH.

## Syntax

**Parameters** take a value with `=`. Quote values with spaces:
```bash
obsidian create name="My Note" content="Hello world"
```

**Flags** are boolean switches with no value:
```bash
obsidian create name="My Note" silent overwrite
```

For multiline content use `\n` for newline and `\t` for tab.

## File Targeting

Many commands accept `file` or `path` to target a file. Without either, the active file is used.

- `file=<name>` — resolves like a wikilink (name only, no path or extension needed)
- `path=<path>` — exact path from vault root, e.g. `folder/note.md`

## Vault Targeting

Commands target the most recently focused vault by default. Use `vault=<name>` as the first parameter to target a specific vault:
```bash
obsidian vault="My Vault" search query="test"
```

## Command Reference

### File Operations
```bash
obsidian files folder=<path> ext=md          # list files (replaces: Glob *.md)
obsidian files folder=base/categories ext=md # list categories
obsidian folders folder=<path>               # list subdirectories
obsidian read file="My Note"                 # read file contents
obsidian read path="folder/note.md"          # read by exact path
obsidian create name="New Note" content="# Hello" template="Template" silent
obsidian append path="folder/note.md" content="New line"
obsidian prepend file="My Note" content="New line"
obsidian move path="old/note.md" to="new/folder"
obsidian rename file="My Note" name="New Name"
obsidian delete path="folder/note.md"
obsidian delete path="folder/note.md" permanent  # skip trash
```

### Search
```bash
obsidian search query="search term" limit=10          # file paths with matches
obsidian search query="text" path=base/notes limit=10 # scoped to folder
obsidian search:context query="text" path=base/notes  # grep-style with matching lines
obsidian search query="#task/inbox" path=periodic/daily  # find inbox tasks
```

### Properties (Frontmatter)
```bash
obsidian properties path=folder/note.md             # read all properties of a file
obsidian property:read name="status" file="My Note" # read single property
obsidian property:set name="status" value="🟦" file="My Note"
obsidian property:set name="updated" value="2026-02-28" type=date file="My Note"
obsidian property:set name="tags" value="note/basic/primary" type=list file="My Note"
obsidian property:remove name="draft" file="My Note"
```

### Tags
```bash
obsidian tags                           # all tags in vault
obsidian tags sort=count counts         # sorted by frequency with counts
obsidian tags file="My Note"            # tags for a specific file
obsidian tag name="category/pkm" verbose # files using this tag
```

### Tasks
```bash
obsidian tasks todo format=json               # all open tasks in vault, with metadata
obsidian tasks done format=json               # all completed tasks in vault
obsidian task ref="path/to/note.md:42" toggle # toggle a specific task

# Tasks in a folder — use search with Obsidian task operators (path= in tasks needs a file):
obsidian search:context query="task-todo:#task/inbox" path=periodic/daily   # open inbox tasks
obsidian search:context query="task-done:#task/inbox" path=periodic/daily   # completed inbox tasks
obsidian search query="- [ ]" path=periodic/daily       # open tasks (any, without tag filter)
```

### Links & Graph
```bash
obsidian backlinks file="My Note"              # notes linking to this note
obsidian links file="My Note"                  # outgoing links from this note
obsidian unresolved                            # broken links in vault
obsidian orphans                               # notes with no incoming links
obsidian deadends                              # notes with no outgoing links
obsidian outline file="My Note" format=md      # headings structure
```

### Recently Modified Files
```bash
obsidian recents                              # recently opened files (replaces: Glob sort by mtime)
```

**DO NOT use `base:query` or other `base:*` commands** — they require Obsidian UI rendering and return `[]` from CLI. Use `obsidian search` with `[property: value]` syntax instead.

### Cross-Platform Date Calculations (replaces bash date / python3)
Use `obsidian eval` with JavaScript instead of OS-specific commands:

```bash
# Current date YYYY-MM-DD
obsidian eval code="new Date().toISOString().slice(0,10)"

# Current week ISO 8601 (replaces: date +%G-W%V)
obsidian eval code="(function(){const d=new Date();const dt=new Date(Date.UTC(d.getFullYear(),d.getMonth(),d.getDate()));const day=dt.getUTCDay()||7;dt.setUTCDate(dt.getUTCDate()+4-day);const y=dt.getUTCFullYear();const ys=new Date(Date.UTC(y,0,1));const w=Math.ceil(((dt-ys)/86400000+1)/7);return y+'-W'+String(w).padStart(2,'0')})()"

# Parent month of current week (replaces: date -j macOS-specific)
obsidian eval code="const d=new Date();d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')"

# Current quarter + months (replaces: python3 quarter script)
obsidian eval code="const d=new Date();const q=Math.ceil((d.getMonth()+1)/3);const m1=(q-1)*3+1;const months=[0,1,2].map(i=>d.getFullYear()+'-'+String(m1+i).padStart(2,'0'));d.getFullYear()+'-Q'+q+' '+months.join(' ')"

# Days since a date
obsidian eval code="Math.floor((Date.now()-new Date('2026-01-01'))/86400000)"
```

**Note:** `eval` uses JavaScript without `return` keyword — the last expression is the result.

### Daily Notes
```bash
obsidian daily:path                           # expected path for today's daily note
obsidian daily:read                           # read today's daily note
obsidian daily:append content="- [ ] New task"
obsidian daily:prepend content="New content"
```

### Vault Info
```bash
obsidian vault                                # vault info
obsidian vaults                               # list all known vaults
obsidian version                              # Obsidian version
```

## Common Patterns for Skills

### Listing available categories (replaces: Glob base/categories/*.md)
```bash
obsidian files folder=base/categories ext=md
obsidian files folder=base/_meta-notes ext=md
obsidian files folder=base/_problems ext=md
```

### Finding active projects (replaces: Grep "status: 🟦" in projects/)
```bash
# Use [property: value] syntax for frontmatter property search:
obsidian search query="[status: 🟦]" path=projects
obsidian search query="[status: 🟩]" path=projects
obsidian search query="[status: 🟥]" path=projects
```

### Finding inbox tasks across daily notes (replaces: Grep #task/inbox)
```bash
# Use task-todo:/task-done: operators to filter by checkbox status:
obsidian search:context query="task-todo:#task/inbox" path=periodic/daily   # open only
obsidian search:context query="task-done:#task/inbox" path=periodic/daily   # completed only
obsidian search:context query="#task/inbox" path=periodic/daily             # all (open + done)
```

### Reading recently modified notes (replaces: Glob sorted by mtime)
```bash
obsidian recents
```

### Updating a property after creating a note (replaces: Edit YAML manually)
```bash
obsidian property:set name="addition" value="[[My Addition|➕]]" type=list file="Parent Note"
```


### Counting notes/tasks/sources by date (replaces: Grep "YYYY-MM-" in frontmatter)
```bash
# Notes created this month (works as partial date match in [property: value] syntax):
obsidian search query="[created: 2026-02]" path=base/notes total
obsidian search query="[created: 2026-02]" path=base/additions total

# Multiple property filters combined with space (AND logic):
obsidian search query="[status: 🟩] [end: 2026-02]" path=sources total

# Tasks completed this month (text search for ✅ date marker):
obsidian search query="✅ 2026-02" total

# Projects by status (replaces: Grep "status: 🟦" in projects/):
obsidian search query="[status: 🟦]" path=projects
obsidian search query="[status: 🟥]" path=projects
obsidian search query="[status: 🟩]" path=projects
```

**IMPORTANT:** `[property: value]` syntax supports partial matching:
- `[created: 2026-02]` — finds all files with `created:` starting with `2026-02`
- `[status: 🟩] [end: 2026]` — two property conditions combined (space = AND)
- `property: value` (without brackets) → **error** "Operator not recognized"
- `#tag [property: value]` combined → **returns 0** (not supported)

### Getting files by tag (replaces: Grep "#source/book" in sources/)
```bash
obsidian tag name="source/book" verbose      # all files with this tag + count
obsidian tag name="source/article/paper" verbose
obsidian tags sort=count counts              # all vault tags sorted by frequency
```

## Plugin Development

After making code changes to a plugin or theme, follow this workflow:

1. **Reload** the plugin to pick up changes:
   ```bash
   obsidian plugin:reload id=my-plugin
   ```
2. **Check for errors** — if errors appear, fix and repeat from step 1:
   ```bash
   obsidian dev:errors
   ```
3. **Verify visually** with a screenshot or DOM inspection:
   ```bash
   obsidian dev:screenshot path=screenshot.png
   obsidian dev:dom selector=".workspace-leaf" text
   ```
4. **Check console output** for warnings or unexpected logs:
   ```bash
   obsidian dev:console level=error
   ```

### Additional developer commands

Run JavaScript in the app context:
```bash
obsidian eval code="app.vault.getFiles().length"
```

Inspect CSS values:
```bash
obsidian dev:css selector=".workspace-leaf" prop=background-color
```

Toggle mobile emulation:
```bash
obsidian dev:mobile on
```
