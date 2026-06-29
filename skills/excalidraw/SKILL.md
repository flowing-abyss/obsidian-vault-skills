---
name: diagram
description: 'Generate Obsidian Excalidraw diagrams from text content as vault-native .md files for the Obsidian Excalidraw plugin. INVOKE when user wants to create a visual diagram. Triggers: "Excalidraw", "draw diagram", "flowchart", "mind map", "visualize", "diagram", "нарисуй диаграмму", "визуализируй", "создай схему", "майнд мап", "блок-схема".'
---

# Excalidraw Diagram Generator

Create vault-native Obsidian Excalidraw diagrams from text content.

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
3. **Use stable 8-character element IDs** for Obsidian compatibility (e.g. `"TTitle01"`, `"ArrowA01"`, `"BoxPlan1"`)
4. **Namespace seeds by section** (section 1 → seeds 100xxx, section 2 → 200xxx)
5. **After all sections**: review cross-section bindings, balance spacing, fix alignment

---

## Output Mode

Always create an Obsidian Excalidraw Markdown file (`.md`) for the vault's Excalidraw plugin. No other output formats are supported by this skill.

---

## Workflow

1. **Step 0**: Assess depth (Simple vs Comprehensive)
2. Run Design Process (Steps 1-5)
3. Create an Obsidian Excalidraw Markdown file using the vault template format
4. Auto-save to `files/` directory
5. Open the created file in Obsidian
6. Take a screenshot of the rendered diagram to the operating system temp directory and visually inspect it
7. Fix visible layout problems and repeat screenshot if needed
8. Notify user with file path, screenshot path, diagram type, and visual patterns used

---

## Output Format

### Obsidian Format

```markdown
---
tags:
  - mark/excalidraw
excalidraw-plugin: parsed
---

# Excalidraw Data
## Text Elements
%%
## Drawing
\`\`\`json
{complete JSON data}
\`\`\`
%%
```

- Frontmatter must include `tags: [mark/excalidraw]`
- Prefer the vault YAML-list style:
  ```yaml
  tags:
    - mark/excalidraw
  ```
- Frontmatter must include `excalidraw-plugin: parsed`
- JSON must be wrapped in `%%` markers
- File extension: `.md`
- Match the vault default template at `templates/excalidraw/templates/excalidraw_template.md`

### Canonical Wrapper

When creating a new drawing, copy `templates/excalidraw/templates/excalidraw_template.md` as the wrapper and replace only:
- `elements`
- `files` when embedded files are needed
- `appState.scrollX`, `appState.scrollY`, and `appState.zoom` when you need a better initial viewport

Keep the template's frontmatter, headings, `%%` wrappers, `source`, and app defaults intact.

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

The JSON below shows the scene structure. For actual files, use the vault template as the source of truth and preserve its full `appState`.

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://github.com/zsviczian/obsidian-excalidraw-plugin/releases/tag/2.24.2",
  "elements": [],
  "appState": {
    "theme": "dark",
    "gridSize": null,
    "viewBackgroundColor": "#ffffff",
    "currentItemFontFamily": 5
  },
  "files": {}
}
```

## Required Fields for All Elements

Use the current Obsidian Excalidraw plugin shape format. Keep generated JSON minimal and consistent. Omit fields unless they are needed by the element, binding, or style.

`boundElements` rules:
- For newly generated elements, use `boundElements: null` for elements with no bindings.
- Use a non-empty array for shapes that own bound text or connected arrows.
- Do not generate empty `boundElements: []` in new elements.
- When editing existing plugin-emitted drawings, treat `boundElements: []` as valid and preserve it unless you are updating that element's bindings.

```json
{
  "id": "BoxPlan1",
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

### Text-Specific Properties

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

### Arrow Binding

```json
{
  "type": "arrow",
  "startBinding": { "elementId": "source-shape-id", "focus": 0, "gap": 5 },
  "endBinding": { "elementId": "target-shape-id", "focus": 0, "gap": 5 },
  "startArrowhead": null,
  "endArrowhead": "arrow"
}
```

- `startBinding.elementId` and `endBinding.elementId` must point to existing element ids.
- If an arrow is bound to a shape, add the arrow id to that shape's `boundElements`.
- For unbound visual arrows, omit `startBinding` and `endBinding` entirely.

When a shape has both bound text and connected arrows, merge all entries in one `boundElements` array:

```json
{
  "id": "source_box",
  "type": "rectangle",
  "boundElements": [
    { "id": "source_text", "type": "text" },
    { "id": "arrow_to_target", "type": "arrow" }
  ]
}
```

---

## Implementation Notes

### Text Elements Handling
- For newly generated files, leave `## Text Elements` empty; the Obsidian Excalidraw plugin can populate it after opening/saving.
- When editing existing drawings, preserve populated `# Text Elements`, `## Text Elements`, and `## Embedded Files` sections unless the edit explicitly requires rewriting the full drawing file.
- Never copy lines from `# Text Elements` or `## Text Elements` into the `## Drawing` JSON as text elements.
- Obsidian Excalidraw's Markdown text index parses element block IDs as exactly 8 characters. When generating or renaming elements manually, every element `id` should be exactly 8 characters, especially text elements and any element referenced by bindings or links.
- Do not use short descriptive IDs like `"tTitle"`, `"goal"`, or `"plan"`. They can make the plugin concatenate `## Text Elements` metadata into visible canvas text on reload.
- Do not use long descriptive IDs either when creating vault-native Obsidian drawings directly. The plugin may rewrite long IDs, which can break manually-authored bindings if every reference is not updated consistently.
- After any manual ID repair, reopen the file in Excalidraw view and verify via API or screenshot that no text element contains `^`, `## Text Elements`, or other Markdown metadata.

### Safe File Editing
- Do not manually edit an Excalidraw `.md` file on disk while the same file is open in Excalidraw view. The plugin can autosave the open canvas and overwrite or re-import manual file changes.
- `workspace:close` closes the active Obsidian tab/leaf, not the entire workspace.
- Before rewriting an existing Excalidraw file directly, focus that file and close its active tab if it may be open:
  ```bash
  obsidian open path="files/[filename].md"
  sleep 1
  obsidian command id=workspace:close
  ```
- After direct file edits are complete, always reopen the file and run the normal screenshot verification pipeline:
  ```bash
  obsidian open path="files/[filename].md"
  sleep 1
  obsidian command id=obsidian-excalidraw-plugin:excalidraw-open-on-current
  sleep 2
  screenshot_path="${TMPDIR:-/tmp}/obsidian-excalidraw-[filename].png"
  obsidian dev:screenshot path="$screenshot_path"
  ```
- For newly created files that have not been opened yet, direct creation in `files/` is safe; only open them after the file is fully written.

### Prevent Visible IDs
- Never include Obsidian block IDs like `^abc123` in JSON `text` or `originalText`.
- Plugin-generated lines ending in `^id` inside `# Text Elements` or `## Text Elements` are Markdown metadata, not diagram labels.
- Preserve plugin-generated `^id` metadata when editing existing files, but keep it out of the drawing JSON.
- If a visible ID problem appears after editing/creating new elements, inspect the element IDs first. Short IDs in text elements are a known cause because the Obsidian Excalidraw parser expects 8-character IDs in the `## Text Elements` section.
- If visible IDs appear in a screenshot, diagnose before accepting the image:
  - IDs with a leading caret, like `^abc123`, usually mean Markdown metadata is visible or was accidentally copied into JSON text.
  - Bare random strings without a caret may be accidental Excalidraw element ids or other debug/metadata text copied into JSON text.
  - If the screenshot shows Markdown text sections, force Excalidraw view again.
  - If the IDs are inside the canvas itself, inspect JSON `text` and `originalText` fields and remove the accidental ID text.

### Compressed Drawings
- This skill creates parsed JSON drawings only.
- Existing `compressed-json` Excalidraw files are out of scope for direct editing unless they are first decompressed by the Excalidraw plugin.

### Obsidian Verification
After saving the diagram, open it in Obsidian and take a screenshot:

```bash
obsidian open path="files/[filename].md"
sleep 1
obsidian command id=obsidian-excalidraw-plugin:excalidraw-open-on-current
sleep 2
screenshot_path="${TMPDIR:-/tmp}/obsidian-excalidraw-[filename].png"
obsidian dev:screenshot path="$screenshot_path"
```

Use the operating system temp directory for screenshots; do not store routine verification screenshots in the vault.

Inspect the screenshot for visible problems:
- screenshot is for the created file, not a previous tab
- Excalidraw canvas or toolbar is visible, not raw Markdown
- no visible metadata IDs such as `^abc123` or accidental element-id strings
- blank or non-rendered canvas
- clipped content
- overlapping text or arrows
- unreadably small text
- arrows pointing to the wrong target
- unbalanced whitespace

If the screenshot is not for the target file, wait briefly and repeat `obsidian dev:screenshot`. If the screenshot reveals a layout issue, edit the diagram and repeat the screenshot.

### Coordinates & Layout
- Origin (0,0) is top-left
- All elements within 0-1200 x 0-800 pixels
- Each element needs a unique `id` string.
- For Obsidian Excalidraw `.md` files, use exactly 8 characters for every generated element ID.

### File Naming

| Mode | Format | Example |
|---|---|---|
| Obsidian | `[topic].[type].md` | `business-model.relationship.md` |

### Auto-save
- Save to `files/` directory in vault root
- Full path: `files/[filename].md`

### User Feedback

After generating, report:
- Diagram generated + exact save location
- Screenshot path used for visual verification
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
- [ ] Text clean and readable
- [ ] fontFamily: 5 on all text
- [ ] roughness: 1 on all elements
- [ ] opacity: 100 on all elements
- [ ] `boundElements` is either null or a non-empty array
- [ ] Existing plugin-emitted `boundElements: []` preserved unless actively rebinding that element
- [ ] Every generated element `id` is exactly 8 characters
- [ ] Arrow bindings point to existing element ids
- [ ] No JSON `text`, `rawText`, or `originalText` contains `^id` or `## Text Elements` metadata
- [ ] File opened via `obsidian open path="files/[filename].md"`
- [ ] Screenshot taken to OS tmp via `obsidian dev:screenshot path="$screenshot_path"`

See [references/excalidraw-schema.md](references/excalidraw-schema.md) for all element types.
