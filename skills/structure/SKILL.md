---
name: structure
description: 'Reference for Obsidian vault directory layout, restricted directories, and the knowledge hierarchy (Category → Meta-note → Problem → Hierarchy). Can also run a script to get the real vault tree and analyze it. INVOKE when user asks about vault organization, where files live, which directories exist, or what can be modified, OR when user wants to see/analyze the actual vault structure. Triggers: "structure", "organization", "what folders", "where to put", "hierarchy", "directory", "DO NOT MODIFY", "analyze structure", "show structure", "куда положить", "какие папки", "структура хранилища", "где находится", "что можно изменять", "покажи структуру", "проанализируй структуру".'
---

# Obsidian Structure

Two modes:
1. **Reference** — static info about vault layout, hierarchy rules, restricted directories.
2. **Analyze** — run the bundled script to get the real vault tree, then audit it inline.

## DO NOT MODIFY

These directories and files are human-only. Never create, edit, or delete anything inside them:

- `base/categories/` — global category definitions
- `home/databases/` — global databases (e.g. contacts, sources, projects)
- `home/prefixes.md` - global prefix definitions for fast note creation
- `templates/` - note templates for various types (sources, contacts, projects, etc.)
- `classes/` - definitions of note classes and their metadata schemas
- `periodic/statuses/` - status definitions for inline tasks

## Directory Map

| Path | Contents | Agent creates here? |
| - | - | - |
| `base/notes/` | Knowledge notes | **YES — primary** |
| `base/_hierarchy/` | Hierarchical aggregator notes | Yes |
| `base/_meta-notes/` | Thematic hubs / roadmaps | Yes |
| `base/_problems/` | Specific research questions | Yes |
| `base/contacts/` | People notes | Yes |
| `base/creators/` | Creator / author profiles | Yes |
| `base/productions/` | Companies / organizations | Yes |
| `base/additions/` | Experiments, meetings, reports | Yes |
| `base/categories/` | Global directions | **NO** |
| `base/tasks/` | Projects tasks | Yes |
| `sources/` | Books, articles, videos, papers | Yes |
| `projects/` | Project management notes | Yes |
| `periodic/` | Daily / weekly / monthly / quarterly / yearly | Yes |
| `files/` | Images, PDFs, attachments | Yes (files only) |

## Knowledge Hierarchy

The vault organizes knowledge through a strict dependency chain:

```
Category → Meta-note → Problem → Hierarchy
```

- **Category** — the base unit. Human-only — agent never creates these.
	- **Meta-note** — must link to exactly one existing category.
		- **Problem** — must link to exactly one existing meta-note AND must use the **same category** as that meta-note.
- **Hierarchy** — can link to a category, a meta-note, or a problem. When linking to a meta-note or problem, always use the same category they belong to.

---

## Understanding and Advising on the Actual Vault Structure

When the user asks anything about their real vault — where to put a note, how to reorganize an area, what's missing, how something fits — first run the script to load the live structure into context:

```bash
python3 .claude/skills/obsidian-structure/scripts/structure.py
```

The script outputs the full vault tree. Use it to understand what actually exists before giving any advice. Do not annotate or score the output — it's context for you, not a report for the user.

### How to advise

After loading the structure, ask 1–2 targeted questions to understand the user's goal before making recommendations. Good guiding questions:

- "What are you trying to improve — navigation, coverage, naming, or something specific?"
- "Are you adding a new node or rethinking an existing one?"
- "Which area of the vault concerns you most?"

Then give concrete, context-aware advice grounded in the actual tree. Reference real node names from the script output.

### Structural principles to apply

Use these as a compass, not a rulebook. The user knows their context better than you.

**🗺️ Category** — the main dashboard and global entry point into a domain. A powerful container: it shows tables of sources, projects, people, and a Mermaid diagram of everything inside. Categories are classifiers — they're used to filter and query across the vault. They're stable and limited in number; even starting with just `work` and `study` is enough. The name should feel like a "department" — but the user decides what counts as a department for them. A specific technology (`python`, `js`) is a valid category if it's a major context the user lives in.

**🔎 Meta-note** — a thematic hub or roadmap for ongoing research inside a category. This is "I'm studying X" — it scopes a direction worth sustained attention. A meta-note is NOT a plan, a log, or a single resource. It's where the user tracks the landscape of a topic and links related problems and hierarchies. Must belong to a category.

**⚡ Problem** — a decomposed sub-problem of the meta-note's research. Think of it as breaking down a research challenge into tractable components: not "how to do X", but the concrete problems that need to be solved within the research. In the medical AI example: "AI diagnosis", "identification of symptoms", "patient information based on data" — each is a distinct sub-problem of the larger research. Must belong to both a category and a meta-note.

**🧬 Hierarchy** — an aggregator of atomic notes sharing a common attribute. This is where synthesis happens. Unlike categories/meta-notes/problems (which are classifiers for filtering sources and projects), hierarchies hold the actual knowledge: they collect wikilinks to notes by theme, attribute, or keyword. Can be nested freely — this is the safe zone for adding depth. A hierarchy can also implement a Discourse Graph structure. Must have at least a category in its metadata.

Nesting law (hard rule, not heuristic):
1. 🗺️ → children: 🔎, 🧬
2. 🔎 → children: ⚡, 🧬
3. ⚡ → children: 🧬
4. 🧬 → children: 🧬 only (no 🗺️/🔎/⚡ inside)

### Examples

R&D decomposition with problems:
```
🗺️ artificial intelligence
  └── 🔎 AI-powered medical decision support
        ├── ⚡ search for a patient in the database
        ├── ⚡ identification of symptoms
        ├── ⚡ AI diagnosis
        └── ⚡ AI treatment planning
```

Deep knowledge synthesis with nested hierarchies:
```
🗺️ history
  ├── 🔎 historiography
  │     ├── 🧬 analysis of historical processes
  │     └── 🧬 interpretation of historical processes
  └── 🔎 methodology of history
        └── 🧬 methods of historical research
              ├── 🧬 comparative analysis in history
              └── 🧬 archival research in history
```

In the second example, `historiography` is the meta-note (the hub), and the 🧬 nodes are aggregators of atomic notes pulled from dozens of sources — they're not section headers, they're note collections.
