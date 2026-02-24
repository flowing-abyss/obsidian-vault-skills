---
name: discourse-graph
description: 'Advisory assistant for building discourse graphs — structured argumentation (questions, claims, evidence, synthesis) within Obsidian hierarchy notes. Searches vault for relevant notes, suggests node types, validates structure. Does NOT auto-generate content. INVOKE when user wants structured research argumentation. Triggers: "discourse graph", "discourse node", "discourse", "structured argumentation", "research graph", "дискурс граф", "граф аргументации", "структурированная аргументация".'
---

# Discourse Graph

Advisory assistant for building discourse graphs — structured argumentation trees adapted from the [Discourse Graph Extension](https://oasis-lab.gitbook.io/roamresearch-discourse-graph-extension/) for Obsidian.

**Role:** Guide the user through discourse graph construction. Search for relevant existing notes, suggest node types and hierarchy placement, help validate argumentation structure. Do NOT auto-generate note content or create notes without explicit user request.

## Node Types

| Tag | Purpose |
|-----|---------|
| `note/discourse/question` | Central research question or hypothesis that drives inquiry |
| `note/discourse/context` | Background information needed to understand the question or claim |
| `note/discourse/observation` | Raw fact, pattern, or notable phenomenon not yet fully interpreted |
| `note/discourse/claim` | Falsifiable assertion, thesis, or proposed answer to a question |
| `note/discourse/evidence` | Data, experiments, sources, or logic supporting/refuting a claim |
| `note/discourse/synthesis` | Integration, conclusion, or resolution across multiple branches |

## Valid Parent-Child Relations

| Parent | Valid Children |
|--------|---------------|
| question | context, claim, synthesis, observation |
| claim | evidence, observation, synthesis |
| synthesis | claim, observation, question |
| context | Typically leaf node |
| observation | Typically leaf node |
| evidence | Typically leaf node |

Key principle: every claim must be supported by evidence.

## Structure

### Container: Hierarchy Note

Discourse graphs live in `base/_hierarchy/` with the `mark/discourse` tag.

```yaml
---
tags:
  - system/high/hierarchy
  - category/<existing_category>
aliases: []
category:
  - "[[<category name>]]"
meta:
  - "[[<meta-note name>]]"  # optional
problem:  # optional
relevant: false
created: YYYY-MM-DDTHH:mm:ss+TZ:TZ
updated: YYYY-MM-DDTHH:mm:ss+TZ:TZ
---
```

### Body: Hierarchical List of Wikilinks

Plain wikilinks in a nested bulleted list. No emojis or type labels — Obsidian renders visual styling automatically based on the discourse tags inside each linked note.

```markdown
- [[note A]]
	- [[note B]]
	- [[note C]]
		- [[note D]]
```

### Discourse Node Notes

Each node is a separate note in `base/notes/`. Follow standard `obsidian-notes` naming rules. Discourse type is determined solely by the tag in frontmatter.

```yaml
---
tags:
  - note/discourse/<type>
  - category/<existing_category>
aliases: []
created: YYYY-MM-DDTHH:mm:ss+TZ:TZ
updated: YYYY-MM-DDTHH:mm:ss+TZ:TZ
---
```

Where `<type>` is one of: `question`, `context`, `observation`, `claim`, `evidence`, `synthesis`.

## Advisory Workflow

### When the user wants to build or extend a discourse graph:

1. **Understand the topic** — ask the user about the research question or area of interest
2. **Search for existing notes** — use Grep/Glob to find relevant notes already in the vault that could serve as discourse nodes
3. **Suggest node types** — for each relevant note or idea, suggest which discourse type fits and where it belongs in the hierarchy
4. **Validate structure** — check parent-child relations, identify gaps (e.g. claims without evidence, questions without context)
5. **Create only on request** — when the user confirms, create the hierarchy note and/or individual node notes

### When searching for relevant notes:

- Search `base/notes/` for notes matching the topic by content and tags
- Search `sources/` for reference material that could serve as evidence
- Check existing hierarchy notes in `base/_hierarchy/` for related structures
- Look for notes already tagged with `note/discourse/*` that might connect to the current graph

### Guiding questions to help the user:

- "What is the core question you are investigating?"
- "What background context is needed to understand this problem?"
- "What claims or positions exist on this topic?"
- "What evidence supports or refutes each claim?"
- "Are there observations that don't yet fit into a claim?"
- "Can any branches be synthesized into a broader conclusion?"

## Example

### Hierarchy note: `base/_hierarchy/information destruction in black holes.md`

```markdown
- [[information destruction in black holes]]
	- [[black hole in general relativity]]
	- [[unitarity principle in quantum mechanics]]
	- [[Hawking claim on information destruction]]
		- [[thermal nature of Hawking radiation]]
		- [[absence of source information in thermal radiation]]
		- [[information loss paradox]]
	- [[quantum prohibition of information destruction]]
		- [[unitary evolution of quantum systems]]
	- [[resolving the information paradox]]
		- [[holographic principle AdS-CFT]]
			- [[information preservation on event horizon]]
			- [[AdS-CFT correspondence bridging gravity and quantum theory]]
		- [[firewall hypothesis]]
			- [[monogamy of entanglement contradiction]]
		- [[soft hair on black holes]]
			- [[information encoding by quantum fluctuations]]
	- [[consensus on the information paradox]]
		- [[physicists leaning toward information preservation]]
		- [[experimental verification of information preservation]]
```
