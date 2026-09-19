---
name: proofread
description: 'Proofread an existing note in place, correcting only spelling, grammar, punctuation, typography, and serious clarity errors while preserving voice and formatting. INVOKE only when the user explicitly asks to proofread or correct errors in prose, or invokes /proofread or $proofread with a note path. Triggers: "proofread", "proofread this note", "correct spelling and punctuation", "вычитай заметку", "исправь ошибки в тексте", "проверь орфографию", "проверь пунктуацию". NOT for rewriting, humanizing, translating, or changing ideas.'
---

# Proofread a note

Use the note path supplied by the user. When invoked manually, use `$ARGUMENTS` as the path.

Correct spelling, grammar, punctuation, typography, and serious stylistic problems that hinder comprehension. Preserve the original style, intonation, tone, authorial voice, formatting, layout, and terminology. Change nothing unless necessary. Keep word choices, metaphors, idioms, speech patterns, and rhythm unless an error makes a change essential.

## Language conventions

For Russian:

- Use the em dash (`—`).
- Use «guillemets» for quotations and „лапки“ for nested quotations.
- Use the ellipsis character (`…`) rather than three periods.

For English:

- Replace em dashes (`—`) with en dashes (`–`).
- Use double quotation marks (`"`) for quotations and direct speech.

For any language:

- Do not add quotation marks around metaphors, similes, or stylistic comparisons.
- Keep brands, anglicisms, proper names, and specialized terms exactly as written unless they contain an error.

## Workflow

1. Read the file at the supplied path.
2. Apply only the necessary corrections.
3. Write the corrected content back to the same file.
4. Report briefly what changed and why.
