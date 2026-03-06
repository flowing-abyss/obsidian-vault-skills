---
name: excalidraw-diagram
description: 'Generate Excalidraw diagrams from text content. Three output modes: Obsidian (.md for plugin), Standard (.excalidraw for excalidraw.com), Animated (.excalidraw with animation order). INVOKE when user wants to create a visual diagram. Triggers: "Excalidraw", "draw diagram", "flowchart", "mind map", "visualize", "diagram", "standard excalidraw", "animated excalidraw", "animate", "нарисуй диаграмму", "визуализируй", "создай схему", "майнд мап", "блок-схема".'
---

# Excalidraw Diagram Generator

Create Excalidraw diagrams from text content with multiple output formats.

---

## Core Philosophy

**Diagrams should ARGUE, not DISPLAY.**

A diagram is not formatted text. It's a visual argument that shows relationships, causality, and flow that words alone can't express. The shape should BE the meaning.

**Isomorphism Test**: If you removed all text, would the structure alone communicate the concept? If not, redesign.

**Education Test**: Could someone learn something concrete from this diagram, or does it just label boxes?

---

## Step 0: Depth Assessment (Do This First)

Before designing, determine what the diagram needs:

**Simple/Conceptual** — use when:
- Explaining a mental model or philosophy
- The concept IS the abstraction
- Audience doesn't need technical specifics

**Comprehensive/Technical** — use when:
- Diagramming a real system, protocol, or architecture
- The diagram will teach or explain
- Multiple technologies integrate

For technical diagrams: look up actual specs, real event names, API formats — then use them. Real terminology > generic placeholders.

---

## Design Process

**Step 1: Understand Deeply**
For each concept ask: What does it DO? What relationships exist? What's the core transformation?

**Step 2: Map Concepts to Patterns**

| If the concept... | Use this pattern |
|---|---|
| Spawns multiple outputs | Fan-out (arrows radiating from center) |
| Combines inputs into one | Convergence (funnel, arrows merging) |
| Has hierarchy/nesting | Tree (lines + free-floating text, no boxes) |
| Is a sequence of steps | Timeline (line + dots + free-floating labels) |
| Loops or improves | Spiral/Cycle (arrow returning to start) |
| Is abstract state/context | Cloud (overlapping ellipses) |
| Transforms input to output | Assembly Line (before → process → after) |
| Compares two things | Side-by-side (parallel with contrast) |
| Separates into phases | Gap/Break (visual separation between sections) |

**Step 3: Ensure Variety**
Each major concept must use a different visual pattern. No uniform card grids.

**Step 4: Sketch the Flow**
Mentally trace how the eye moves. There should be a clear visual story.

**Step 5: Generate JSON**
Only now create the Excalidraw elements. For large diagrams — see Large Diagram Strategy.

---

## Visual Pattern Library

### Fan-Out (One-to-Many)
Central element with arrows radiating to multiple targets. For: sources, root causes, hubs.

### Convergence (Many-to-One)
Multiple inputs merging to single output. For: aggregation, funnels, synthesis.

### Tree (Hierarchy)
Use `line` elements for trunk and branches + free-floating text labels. No boxes needed.
```
  label
  ├── label
  │   └── label
  └── label
```

### Timeline
Vertical/horizontal line + small dots (10-20px ellipses) at intervals + free-floating labels beside each dot.

### Spiral/Cycle
Elements in sequence with arrow returning to start. For: feedback loops, iteration.

### Cloud (Abstract State)
Overlapping ellipses with varied sizes. For: context, memory, mental states.

### Assembly Line
Input → Process → Output with clear before/after. For: transformations, conversion.

### Side-by-Side
Two parallel structures with visual contrast. For: before/after, options, trade-offs.

---

## Container vs Free-Floating Text

**Default to free-floating text. Add a container only when it serves a purpose.**

| Use a Container When... | Use Free-Floating Text When... |
|---|---|
| It's the focal point of a section | It's a label or description |
| Arrows need to connect to it | It describes something nearby |
| The shape carries meaning (decision diamond, etc.) | It's a title, subtitle, or annotation |
| It represents a distinct "thing" in the system | Typography alone creates hierarchy |

**Target: <30% of text elements inside containers.**

Use font size and color to create visual hierarchy without boxes — a 24px title doesn't need a rectangle around it.

---

## Large Diagram Strategy

For complex diagrams, build JSON **one section at a time** — never generate everything in one pass.

1. **Create base file** with JSON wrapper + first section
2. **Add one section per edit** — think layout, spacing, cross-section connections
3. **Use descriptive string IDs** (`"trigger_rect"`, `"arrow_fan_left"`)
4. **Namespace seeds by section** (section 1 → seeds 100xxx, section 2 → 200xxx)
5. **After all sections**: review cross-section bindings, balance spacing, fix alignment

---

## Output Modes

Select based on trigger words:

| Trigger Words | Output Mode | File Format | Purpose |
|---|---|---|---|
| `Excalidraw`, `draw diagram`, `flowchart`, `mind map` | **Obsidian** (default) | `.md` | Open directly in Obsidian |
| `standard excalidraw` | **Standard** | `.excalidraw` | Open/edit/share on excalidraw.com |
| `animated excalidraw`, `animate` | **Animated** | `.excalidraw` | Drag to excalidraw-animate |

---

## Workflow

1. Detect output mode from trigger words
2. **Step 0**: Assess depth (Simple vs Comprehensive)
3. Run Design Process (Steps 1-5)
4. Output in correct format
5. Auto-save to `files/` directory
6. Notify user with file path and usage instructions

---

## Output Formats

### Mode 1: Obsidian Format (Default)

```markdown
---
excalidraw-plugin: parsed
tags: [excalidraw]
---
==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠== You can decompress Drawing data with the command palette: 'Decompress current Excalidraw file'. For more info check in plugin settings under 'Saving'

# Excalidraw Data

## Text Elements
%%
## Drawing
\`\`\`json
{complete JSON data}
\`\`\`
%%
```

- Frontmatter must include `tags: [excalidraw]`
- JSON must be wrapped in `%%` markers
- File extension: `.md`

### Mode 2: Standard Excalidraw Format

Pure JSON, no Markdown wrapping:

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [],
  "appState": { "gridSize": null, "viewBackgroundColor": "#ffffff" },
  "files": {}
}
```

File extension: `.excalidraw`

### Mode 3: Animated Excalidraw Format

Same as Standard, but each element gets a `customData.animate` field:

```json
{
  "id": "element-1",
  "type": "rectangle",
  "customData": { "animate": { "order": 1, "duration": 500 } }
}
```

- `order`: Playback sequence — lower numbers appear first
- `duration`: Drawing duration in ms (default 500)
- Same `order` = appear simultaneously
- Recommended order: title → main framework → connectors → detail text
- Usage: drag to https://dai-shi.github.io/excalidraw-animate/
- File extension: `.excalidraw`

---

## Diagram Types & Selection Guide

| Type | Use Case | Approach |
|---|---|---|
| **Flowchart** | Workflows, task execution order | Connect steps with arrows |
| **Mind Map** | Concept exploration, brainstorming | Radiate outward from center |
| **Hierarchy** | Org structures, system decomposition | Top-down or left-right tree |
| **Relationship** | Influence, dependency, interaction | Connectors with arrows and labels |
| **Comparison** | Side-by-side analysis | Two columns or table format |
| **Timeline** | Event progression, milestones | Time axis with key dates |
| **Matrix** | Two-dimensional classification | X and Y axes |
| **Freeform** | Brainstorming, initial info gathering | No structural constraints |

---

## Design Rules

### Shape Meaning

| Concept Type | Shape | Why |
|---|---|---|
| Labels, descriptions, details | **none** (free-floating text) | Typography creates hierarchy |
| Section titles, annotations | **none** (free-floating text) | Font size/weight is enough |
| Timeline markers | small `ellipse` (10-20px) | Visual anchor, not container |
| Start, trigger, input | `ellipse` | Soft, origin-like |
| End, output, result | `ellipse` | Completion, destination |
| Decision, condition | `diamond` | Classic decision symbol |
| Process, action, step | `rectangle` | Contained action |
| Abstract state, context | overlapping `ellipse` | Fuzzy, cloud-like |
| Hierarchy node | lines + text (no boxes) | Structure through lines |

### Text & Format
- **All text must use** `fontFamily: 5` (Excalifont)
- **Double quote replacement**: `"` → `『』`
- **Parentheses replacement**: `()` → `「」`
- **Font sizes**: Title 24-28px, Subtitle 18-20px, Body 14-16px
- **Line height**: `lineHeight: 1.25`

### Layout
- **Canvas range**: Keep all elements within 0-1200 x 0-800
- **No Emoji** in diagram text — use shapes or color coding instead
- **Roughness**: `roughness: 1` (hand-drawn style)
- **Stroke width**: 1 for subtle lines, 2 for standard shapes, 3 for emphasis
- **Opacity**: `opacity: 100` for all elements

### Color Palette
- **Title**: `#1e40af` (deep blue)
- **Subtitle/connectors**: `#3b82f6` (bright blue)
- **Body text**: `#374151` (gray)
- **Emphasis/highlights**: `#f59e0b` (gold)
- Colors encode meaning, not decoration — be consistent

---

## JSON Structure

**Obsidian mode:**
```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://github.com/zsviczian/obsidian-excalidraw-plugin",
  "elements": [],
  "appState": { "gridSize": null, "viewBackgroundColor": "#ffffff" },
  "files": {}
}
```

**Standard / Animated mode:**
```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [],
  "appState": { "gridSize": null, "viewBackgroundColor": "#ffffff" },
  "files": {}
}
```

## Required Fields for All Elements

**IMPORTANT**: Do NOT include `frameId`, `index`, `versionNonce`, `strokeStyle`, or `rawText`. These cause "Error: invalid file" on excalidraw.com v0.17.0+. Use `boundElements: null` (not `[]`), and `updated: 1`.

```json
{
  "id": "unique-id",
  "type": "rectangle|text|arrow|ellipse|diamond",
  "x": 100, "y": 100,
  "width": 200, "height": 50,
  "angle": 0,
  "strokeColor": "#1e1e1e",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "roughness": 1,
  "opacity": 100,
  "groupIds": [],
  "roundness": {"type": 3},
  "seed": 123456789,
  "version": 1,
  "isDeleted": false,
  "boundElements": null,
  "updated": 1,
  "link": null,
  "locked": false
}
```

### Text-Specific Properties (do NOT include `rawText`)

```json
{
  "text": "Display text",
  "fontSize": 20,
  "fontFamily": 5,
  "textAlign": "center",
  "verticalAlign": "middle",
  "containerId": null,
  "originalText": "Display text",
  "autoResize": true,
  "lineHeight": 1.25
}
```

### Animated Mode Additional Field

```json
{
  "customData": { "animate": { "order": 1, "duration": 500 } }
}
```

---

## Implementation Notes

### Text Elements Handling
- The `## Text Elements` section in Markdown **must be left empty** — Obsidian Excalidraw plugin auto-populates it

### Coordinates & Layout
- Origin (0,0) is top-left
- All elements within 0-1200 x 0-800 pixels
- Each element needs a unique `id` (string)

### File Naming

| Mode | Format | Example |
|---|---|---|
| Obsidian | `[topic].[type].md` | `business-model.relationship.md` |
| Standard | `[topic].[type].excalidraw` | `business-model.relationship.excalidraw` |
| Animated | `[topic].[type].animate.excalidraw` | `business-model.relationship.animate.excalidraw` |

### Auto-save
- Save to `files/` directory in vault root
- Full path: `files/[filename]`

### User Feedback

After generating, report:
- Diagram generated + exact save location
- How to view it (mode-specific)
- Diagram type chosen and why
- Visual patterns used and why

---

## Quality Checklist

### Conceptual
- [ ] Isomorphism: visual structure mirrors the concept's behavior?
- [ ] Argument: does the diagram SHOW something text couldn't?
- [ ] Variety: each major concept uses a different visual pattern?
- [ ] No uniform card grids or equal boxes?

### Container Discipline
- [ ] Free-floating text used by default?
- [ ] Tree/timeline uses lines + text rather than boxes?
- [ ] <30% of text elements inside containers?

### Structural
- [ ] Every relationship has an arrow or line
- [ ] Clear visual path for the eye to follow
- [ ] Important elements are larger/more isolated

### Technical
- [ ] Text clean: `text` contains only readable words (no quotes/parens)
- [ ] fontFamily: 5 on all text
- [ ] roughness: 1 on all elements
- [ ] opacity: 100 on all elements
- [ ] No forbidden fields: frameId, versionNonce, strokeStyle, rawText
- [ ] boundElements: null (not [])

See [references/excalidraw-schema.md](references/excalidraw-schema.md) for all element types.
