---
name: vault-check
description: 'Health check of the whole vault: invalid metadata, broken links, notes in the wrong folder, manifests and templates that drifted apart. Read only by default. INVOKE when the user asks to check, validate, audit or clean up the vault, or asks whether everything is in order. Triggers: "check the vault", "validate the vault", "audit", "vault health", "is everything ok", "find broken links", "проверь хранилище", "провалидируй хранилище", "аудит", "всё ли в порядке", "найди битые ссылки", "проверь структуру". NOT for creating notes or for one note the user is editing now.'
---

# Vault check

`vault` below stands for `python3 .claude/_engine/vault.py`, run from the vault root. Every command here only reads.

| Need | Command |
| - | - |
| Overview first, always | `vault audit --summary` |
| Real problems only | `vault audit --errors` |
| One rule in detail | `vault audit --rule link-exists --limit 100` |
| One area | `vault audit --folder sources/` |
| Broken links inside note bodies | `vault audit --summary --links --limit 100` |
| What each rule means and its severity | `vault checks` |
| One note | `vault check "note name"` |

## What the sections mean

- **Manifests**: broken YAML, keys the engine does not know, an `enforce_folder` that does not exist. These affect every note of the type, so report them first.
- **Sources**: a JavaScript source in a manifest the engine cannot answer. That field is checked only in part.
- **Templates**: a `template.md` whose properties differ from its manifest. New notes made by hand in Obsidian start out incomplete.
- **Notes**: findings per note. Errors are wrong data. Warnings are usually old notes that predate a rule.
- **Broken links in note bodies**: often planned notes that were never written. Not always a mistake.

## How to work

1. Run the overview. Do not print the full audit into the conversation; it is long. Narrow with `--rule`, `--folder`, `--errors`.
2. Report in the user's language: what is wrong, how many, the few worst examples, and what you suggest. Group by cause, not by file. Many identical findings point at a manifest or an unfinished migration, not at the notes.
3. Change nothing until the user says what to fix. Then:
   - mechanical items marked `fixable`: `vault fix "note"`;
   - a wrong value: `vault set "note" key=value`;
   - manifests, templates and categories are protected zones. Propose the exact edit and wait for approval.
4. After fixes, run the same audit command again and report the difference.
