---
name: editor
description: 'Apply surgical edits to text marked with %%instructions%% and ==highlights==, remove the markers, and preserve all unmarked text verbatim. INVOKE only when the user explicitly asks to apply inline annotations and supplies these markers, or invokes /editor or $editor. Triggers: "apply inline annotations", "edit annotated text", "примени аннотации", "обработай выделения", "выполни встроенные инструкции". NOT for general rewriting, proofreading, humanizing, or unannotated text.'
---

# Edit annotated text

Apply inline annotations to the text supplied by the user. When invoked manually, use `$ARGUMENTS` as the annotated text.

## Annotation types

- `%%instruction%%` — an explicit directive. Apply it exactly as written to the surrounding text.
- `==passage==` — a passage flagged as weak, vague, or dubious. Rewrite it to be stronger and more precise using the surrounding context.

## Rules

1. Execute every `%%...%%` instruction exactly.
2. Rewrite every `==...==` passage using judgment and context.
3. Remove all `%%...%%` and `==...==` markers from the result.
4. Preserve the structure, style, and wording of all unmarked text verbatim.
5. Return only the edited text, without explanations, preamble, or commentary.
