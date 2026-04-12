---
description: Edit text annotated with %%instructions%% and ==highlights==
---

Apply inline annotations to the text provided in $ARGUMENTS and return a clean, edited result.

## Annotation Types

- `%%instruction%%` — explicit directive. Apply it exactly as written to the surrounding text.
- `==passage==` — flagged as weak, vague, or dubious. Rewrite it to be stronger and more precise, using the surrounding context.

## Rules

1. Execute every `%%...%%` instruction exactly.
2. Rewrite every `==...==` passage using judgment and context.
3. Strip ALL `%%...%%` and `==...==` markers from output — no exceptions.
4. Touch nothing else. Preserve structure, style, and wording of unmarked text verbatim.
5. Output the edited text only — no explanations, no preamble, no commentary.
