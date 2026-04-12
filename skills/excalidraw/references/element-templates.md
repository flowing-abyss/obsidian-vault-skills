# Element Templates

Copy-paste JSON templates for each element type. All templates use vault defaults:
- `fontFamily: 5` (Excalifont)
- `roughness: 1` (hand-drawn style)
- `opacity: 100`
- `boundElements: null` (never use `[]`)
- `updated: 1` (never use timestamps)
- **Forbidden fields** (omit always): `frameId`, `index`, `versionNonce`, `strokeStyle`, `rawText`

Colors reference:
- Title/stroke: `#1e40af` (deep blue)
- Subtitle/connector: `#3b82f6` (bright blue)
- Body text: `#374151` (gray)
- Emphasis: `#f59e0b` (gold)
- Background light blue: `#dbeafe`
- Background light gray: `#f3f4f6`
- Background light orange: `#fef3c7`
- Background light green: `#d1fae5`
- Background light purple: `#ede9fe`

---

## Free-Floating Text (no container)

Default for labels, titles, annotations. Use this more often than containers.

```json
{
  "type": "text",
  "id": "label1",
  "x": 100,
  "y": 100,
  "width": 200,
  "height": 25,
  "angle": 0,
  "strokeColor": "#1e40af",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "roughness": 1,
  "opacity": 100,
  "groupIds": [],
  "roundness": null,
  "seed": 11111,
  "version": 1,
  "isDeleted": false,
  "boundElements": null,
  "updated": 1,
  "link": null,
  "locked": false,
  "text": "Section Title",
  "originalText": "Section Title",
  "fontSize": 24,
  "fontFamily": 5,
  "textAlign": "left",
  "verticalAlign": "top",
  "containerId": null,
  "autoResize": true,
  "lineHeight": 1.25
}
```

Font size guide: Title 24-28px, Subtitle 18-20px, Body 14-16px

---

## Rectangle

For processes, actions, components — when shape carries meaning.

```json
{
  "type": "rectangle",
  "id": "rect1",
  "x": 100,
  "y": 100,
  "width": 180,
  "height": 80,
  "angle": 0,
  "strokeColor": "#1e40af",
  "backgroundColor": "#dbeafe",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "roughness": 1,
  "opacity": 100,
  "groupIds": [],
  "roundness": {"type": 3},
  "seed": 12345,
  "version": 1,
  "isDeleted": false,
  "boundElements": [{"id": "text1", "type": "text"}],
  "updated": 1,
  "link": null,
  "locked": false
}
```

---

## Text Inside Shape (bound to container)

Always pair with parent shape — add text id to parent's `boundElements`.

```json
{
  "type": "text",
  "id": "text1",
  "x": 110,
  "y": 128,
  "width": 160,
  "height": 25,
  "angle": 0,
  "strokeColor": "#1e40af",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "roughness": 1,
  "opacity": 100,
  "groupIds": [],
  "roundness": null,
  "seed": 22222,
  "version": 1,
  "isDeleted": false,
  "boundElements": null,
  "updated": 1,
  "link": null,
  "locked": false,
  "text": "Process",
  "originalText": "Process",
  "fontSize": 16,
  "fontFamily": 5,
  "textAlign": "center",
  "verticalAlign": "middle",
  "containerId": "rect1",
  "autoResize": true,
  "lineHeight": 1.25
}
```

Text `x` = shape `x` + padding (~10px). Text `y` = shape `y` + (height - fontSize) / 2.

---

## Ellipse

For start/end points, external systems, abstract states.

```json
{
  "type": "ellipse",
  "id": "ellipse1",
  "x": 100,
  "y": 100,
  "width": 120,
  "height": 60,
  "angle": 0,
  "strokeColor": "#10b981",
  "backgroundColor": "#d1fae5",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "roughness": 1,
  "opacity": 100,
  "groupIds": [],
  "roundness": {"type": 2},
  "seed": 33333,
  "version": 1,
  "isDeleted": false,
  "boundElements": [{"id": "text2", "type": "text"}],
  "updated": 1,
  "link": null,
  "locked": false
}
```

---

## Diamond (Decision)

For conditions, branching logic.

```json
{
  "type": "diamond",
  "id": "diamond1",
  "x": 100,
  "y": 100,
  "width": 150,
  "height": 100,
  "angle": 0,
  "strokeColor": "#f59e0b",
  "backgroundColor": "#fef3c7",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "roughness": 1,
  "opacity": 100,
  "groupIds": [],
  "roundness": {"type": 2},
  "seed": 44444,
  "version": 1,
  "isDeleted": false,
  "boundElements": [{"id": "text3", "type": "text"}],
  "updated": 1,
  "link": null,
  "locked": false
}
```

---

## Arrow

For connections between shapes. Use `startBinding`/`endBinding` to snap to shapes.

```json
{
  "type": "arrow",
  "id": "arrow1",
  "x": 282,
  "y": 140,
  "width": 118,
  "height": 0,
  "angle": 0,
  "strokeColor": "#3b82f6",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "roughness": 1,
  "opacity": 100,
  "groupIds": [],
  "roundness": {"type": 2},
  "seed": 55555,
  "version": 1,
  "isDeleted": false,
  "boundElements": null,
  "updated": 1,
  "link": null,
  "locked": false,
  "points": [[0, 0], [118, 0]],
  "startBinding": {"elementId": "rect1", "focus": 0, "gap": 5},
  "endBinding": {"elementId": "rect2", "focus": 0, "gap": 5},
  "startArrowhead": null,
  "endArrowhead": "arrow"
}
```

For curves: add midpoint in `points`, e.g. `[[0,0],[60,-40],[118,0]]`.
For bidirectional: set `startArrowhead: "arrow"`.
For unconnected arrow: omit `startBinding`/`endBinding` entirely.

---

## Line (Structural, Not Arrow)

For timelines, tree trunks, dividers. Does NOT have arrowheads.

```json
{
  "type": "line",
  "id": "line1",
  "x": 100,
  "y": 100,
  "width": 0,
  "height": 200,
  "angle": 0,
  "strokeColor": "#374151",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "roughness": 1,
  "opacity": 100,
  "groupIds": [],
  "roundness": {"type": 2},
  "seed": 66666,
  "version": 1,
  "isDeleted": false,
  "boundElements": null,
  "updated": 1,
  "link": null,
  "locked": false,
  "points": [[0, 0], [0, 200]]
}
```

For horizontal: `points: [[0,0],[200,0]]`, `width: 200, height: 0`.
For dashed divider: add `"strokeStyle": "dashed"` (exception — allowed on lines).

---

## Timeline Marker Dot

Small filled circle for timeline/tree anchors. Place beside free-floating text labels.

```json
{
  "type": "ellipse",
  "id": "dot1",
  "x": 94,
  "y": 94,
  "width": 12,
  "height": 12,
  "angle": 0,
  "strokeColor": "#3b82f6",
  "backgroundColor": "#3b82f6",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "roughness": 1,
  "opacity": 100,
  "groupIds": [],
  "roundness": null,
  "seed": 77777,
  "version": 1,
  "isDeleted": false,
  "boundElements": null,
  "updated": 1,
  "link": null,
  "locked": false
}
```

Size: 10-20px. Center it on the timeline line: `x = line_x - 6` (for 12px dot).

---

## Container + Bound Text Pair (Full Example)

The most common pattern — copy both elements together.

```json
{
  "type": "rectangle",
  "id": "box_A",
  "x": 200, "y": 150,
  "width": 160, "height": 70,
  "angle": 0,
  "strokeColor": "#1e40af",
  "backgroundColor": "#dbeafe",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "roughness": 1,
  "opacity": 100,
  "groupIds": [],
  "roundness": {"type": 3},
  "seed": 100001,
  "version": 1,
  "isDeleted": false,
  "boundElements": [{"id": "text_A", "type": "text"}],
  "updated": 1,
  "link": null,
  "locked": false
},
{
  "type": "text",
  "id": "text_A",
  "x": 210, "y": 173,
  "width": 140, "height": 25,
  "angle": 0,
  "strokeColor": "#1e40af",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "roughness": 1,
  "opacity": 100,
  "groupIds": [],
  "roundness": null,
  "seed": 100002,
  "version": 1,
  "isDeleted": false,
  "boundElements": null,
  "updated": 1,
  "link": null,
  "locked": false,
  "text": "Label",
  "originalText": "Label",
  "fontSize": 16,
  "fontFamily": 5,
  "textAlign": "center",
  "verticalAlign": "middle",
  "containerId": "box_A",
  "autoResize": true,
  "lineHeight": 1.25
}
```

---

## Seed Strategy for Large Diagrams

Namespace seeds by section to avoid collisions:

| Section | Seed Range | Example IDs |
|---|---|---|
| Section 1 | 100001–109999 | `"seed": 100001` |
| Section 2 | 200001–209999 | `"seed": 200001` |
| Section 3 | 300001–309999 | `"seed": 300001` |

Use descriptive string IDs: `"trigger_rect"`, `"arrow_fan_left"`, `"timeline_dot_3"`.
