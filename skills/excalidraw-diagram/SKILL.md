---
name: excalidraw-diagram
description: 'Generate Excalidraw diagrams from text content. Three output modes: Obsidian (.md for plugin), Standard (.excalidraw for excalidraw.com), Animated (.excalidraw with animation order). INVOKE when user wants to create a visual diagram. Triggers: "Excalidraw", "draw diagram", "flowchart", "mind map", "visualize", "diagram", "standard excalidraw", "animated excalidraw", "animate", "нарисуй диаграмму", "визуализируй", "создай схему", "майнд мап", "блок-схема".'
---

# Excalidraw Diagram Generator

Create Excalidraw diagrams from text content with multiple output formats.

## Output Modes

Select the output mode based on the user's trigger words:

| Trigger Words | Output Mode | File Format | Purpose |
|---------------|-------------|-------------|---------|
| `Excalidraw`, `draw diagram`, `flowchart`, `mind map` | **Obsidian** (default) | `.md` | Open directly in Obsidian |
| `standard excalidraw` | **Standard** | `.excalidraw` | Open/edit/share on excalidraw.com |
| `animated excalidraw`, `animate` | **Animated** | `.excalidraw` | Drag to excalidraw-animate for animation |

## Workflow

1. **Detect output mode** from trigger words (see Output Modes table above)
2. Analyze content - identify concepts, relationships, hierarchy
3. Choose diagram type (see Diagram Types below)
4. Generate Excalidraw JSON (add animation order if Animated mode)
5. Output in correct format based on mode
6. **Automatically save to `files/` directory**
7. Notify user with file path and usage instructions

## Output Formats

### Mode 1: Obsidian Format (Default)

**Output must strictly follow this structure with no modifications:**

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

**Key points:**
- Frontmatter must include `tags: [excalidraw]`
- Warning message must be complete
- JSON must be wrapped in `%%` markers
- Do not use any frontmatter settings other than `excalidraw-plugin: parsed`
- **File extension**: `.md`

### Mode 2: Standard Excalidraw Format

Output a pure JSON file that can be opened on excalidraw.com:

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [...],
  "appState": {
    "gridSize": null,
    "viewBackgroundColor": "#ffffff"
  },
  "files": {}
}
```

**Key points:**
- `source` must be `https://excalidraw.com` (not the Obsidian plugin)
- Pure JSON, no Markdown wrapping
- **File extension**: `.excalidraw`

### Mode 3: Animated Excalidraw Format

Same as Standard format, but each element gets a `customData.animate` field to control animation order:

```json
{
  "id": "element-1",
  "type": "rectangle",
  "customData": {
    "animate": {
      "order": 1,
      "duration": 500
    }
  },
  "...other standard fields"
}
```

**Animation order rules:**
- `order`: Playback sequence (1, 2, 3...) — lower numbers appear first
- `duration`: Drawing duration for the element in milliseconds, default 500
- Elements with the same `order` appear simultaneously
- Recommended order: title → main framework → connectors → detail text

**Usage:**
1. Generate the `.excalidraw` file
2. Drag it to https://dai-shi.github.io/excalidraw-animate/
3. Click Animate to preview, then export as SVG or WebM

**File extension**: `.excalidraw`

---

## Diagram Types & Selection Guide

Choose the appropriate diagram type to maximize clarity and visual appeal.

| Type | Use Case | Approach |
|------|----------|----------|
| **Flowchart** | Step-by-step instructions, workflows, task execution order | Connect steps with arrows to show process flow |
| **Mind Map** | Concept exploration, topic classification, brainstorming | Radiate outward from a central concept |
| **Hierarchy** | Org structures, content tiers, system decomposition | Build top-down or left-to-right tree nodes |
| **Relationship** | Influence, dependency, and interaction between elements | Use connectors with arrows and labels |
| **Comparison** | Side-by-side analysis of two or more options | Two columns or table format with comparison dimensions |
| **Timeline** | Event progression, project milestones, model evolution | Use a time axis with key dates and events |
| **Matrix** | Two-dimensional classification, priority mapping | Create X and Y axes, place items on coordinate plane |
| **Freeform** | Scattered content, brainstorming, initial information gathering | No structural constraints, freely place blocks and arrows |

## Design Rules

### Text & Format
- **All text elements must use** `fontFamily: 5` (Excalifont handwriting font)
- **Double quote replacement**: `"` → `『』`
- **Parentheses replacement**: `()` → `「」`
- **Font size rules**:
  - Title: 24-28px
  - Subtitle: 18-20px
  - Body/description: 14-16px
- **Line height**: All text uses `lineHeight: 1.25`

### Layout & Design
- **Canvas range**: Keep all elements within 0-1200 x 0-800
- **Spacing**: Ensure adequate spacing between elements for a clean layout
- **Clear hierarchy**: Use different colors and shapes to distinguish information levels
- **Graphic elements**: Use rectangles, circles, arrows, etc. to organize information
- **No Emoji**: Do not use any Emoji symbols in diagram text — use simple shapes (circles, squares, arrows) or color coding instead

### Color Palette
- **Title**: `#1e40af` (deep blue)
- **Subtitle/connectors**: `#3b82f6` (bright blue)
- **Body text**: `#374151` (gray)
- **Emphasis/highlights**: `#f59e0b` (gold)
- **Other colors**: Use a harmonious color scheme, avoid too many colors

See [references/excalidraw-schema.md](references/excalidraw-schema.md) for all element types.

## JSON Structure

**Obsidian mode:**
```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://github.com/zsviczian/obsidian-excalidraw-plugin",
  "elements": [...],
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
  "elements": [...],
  "appState": { "gridSize": null, "viewBackgroundColor": "#ffffff" },
  "files": {}
}
```

## Required Fields for All Elements

**IMPORTANT**: Do NOT include `frameId`, `index`, `versionNonce`, `strokeStyle`, or `rawText` fields. These cause "Error: invalid file" on excalidraw.com v0.17.0+. Use `boundElements: null` (not `[]`), and `updated: 1` (not timestamps).

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

### Text-Specific Properties

Text elements (type: "text") require additional fields (do NOT include `rawText`):

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
  "id": "title-1",
  "type": "text",
  "customData": {
    "animate": {
      "order": 1,
      "duration": 500
    }
  },
  "...other fields"
}
```

---

## Implementation Notes

### Text Elements Handling
- The `## Text Elements` section in Markdown **must be left empty**, using only `%%` as delimiter
- The Obsidian Excalidraw plugin **auto-populates text elements** from the JSON data
- No need to manually list text content

### Coordinates & Layout
- **Coordinate system**: Origin (0,0) is at the top-left corner
- **Recommended range**: All elements within 0-1200 x 0-800 pixels
- **Element IDs**: Each element needs a unique `id` (string, e.g. "title", "box1")

### File Naming

Choose file extension based on output mode:

| Mode | Filename Format | Example |
|------|----------------|---------|
| Obsidian | `[topic].[type].md` | `business-model.relationship.md` |
| Standard | `[topic].[type].excalidraw` | `business-model.relationship.excalidraw` |
| Animated | `[topic].[type].animate.excalidraw` | `business-model.relationship.animate.excalidraw` |

### Auto-save

- **Save location**: `files/` directory in the vault root
- **Full path**: `files/[filename]`
- Use the Write tool to save the file automatically

### User Feedback

After generating, report to the user:
- Diagram has been generated
- Exact save location
- How to view it (mode-specific instructions)
- Design choices made (diagram type selected and why)
- Whether adjustments are needed
