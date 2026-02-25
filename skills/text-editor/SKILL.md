---
name: text-editor
description: 'Edit text annotated with %%instructions%% and ==highlights==. Instructions (%%...%%) are explicit directives applied exactly as written; highlights (==...==) flag weak or vague passages for Claude to rewrite using context and judgment. Removes all markers and returns clean text only — no commentary. INVOKE when user provides annotated text asking to apply edits. Triggers: "edit annotated text", "apply comments", "apply edits", "отредактируй текст", "примени комментарии", "убери комментарии", text pasted with %%...%% or ==...== markers.'
---

# Text Editor

Apply inline annotations to text and return a clean, edited result.

## Annotation Types

- `%%instruction%%` — explicit directive. Apply it exactly as written to the surrounding text.
- `==passage==` — flagged as weak, vague, or dubious. Rewrite it to be stronger and more precise, using the surrounding context.

## Rules

1. Execute every `%%...%%` instruction exactly.
2. Rewrite every `==...==` passage using judgment and context.
3. Strip ALL `%%...%%` and `==...==` markers from output — no exceptions.
4. Touch nothing else. Preserve structure, style, and wording of unmarked text verbatim.
5. Output the edited text only — no explanations, no preamble, no commentary.

## Example

**Input:**
```
Sleep is important.%%Rewrite as a bold, specific claim.%% ==Getting enough sleep makes you feel better and helps you think more clearly.== Experts recommend 7–9 hours per night.
```

**Output:**
```
Sleep is the single highest-leverage health intervention available to anyone. Research consistently links adequate sleep to sharper cognition, emotional stability, and faster physical recovery. Experts recommend 7–9 hours per night.
```

What happened:
- `%%Rewrite as a bold, specific claim.%%` → the sentence was replaced with a strong, concrete statement
- `==Getting enough sleep...==` → the vague phrase was rewritten with specific, evidence-backed benefits
- `Experts recommend 7–9 hours per night.` → untouched, preserved verbatim
