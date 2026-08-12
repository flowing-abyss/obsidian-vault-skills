---
name: flashcards
description: 'Create recall-first flashcard notes that also work as useful Obsidian knowledge notes, with validated Anki decks, one compact answer ending at the first blank line, optional extended explanations/tables/media, and footnote sources. INVOKE whenever the user wants flashcards, study cards, Anki material, spaced repetition, a knowledge deck, or wants to turn concepts into memorable atomic notes. Triggers: "create flashcard", "flashcards", "study cards", "Anki", "spaced repetition", "карточка", "создай флэшкарту", "карточки для повторения", "анки карточка", "флэшкарды", "колода знаний". Shows an example first and creates after confirmation.'
---

# Obsidian Flashcards

Create flashcards that are easy to grade during recall and remain valuable when opened as ordinary Obsidian notes. The mandatory answer stays small; explanations, tables, sources, and media live after the card boundary.

## Flashcard Template

All flashcards follow this structure:

### YAML Frontmatter

```yaml
---
tags:
  - note/specific/exact  # or note/specific/code
  - category/<category_name>  # e.g., category/computer_science
aliases: []  # or specific aliases for code/exact types
deck: obsidian::<deck_path>  # e.g., obsidian::computer_science::algorithms
created: 2026-02-08T15:30:00+07:00  # ISO 8601 with timezone
updated: 2026-02-08T15:30:00+07:00  # ISO 8601 with timezone
---
```

**Important metadata rules:**
- **Tags**: Must include note taxonomy (`note/specific/code` or `note/specific/exact`) and category tag (`category/<name>`)
- **Deck**: Format is `obsidian::<category>` or `obsidian::<category>::<subcategory>` (use `::` for hierarchy)
- **Aliases**: Can be empty `[]` or include specific terms for quick reference
- **Dates**: ISO 8601 format with timezone (generated automatically based on current time)

### Content Structure

```markdown
**One precise question or term**
—
The smallest sufficient answer.[^1]

## Подробнее

Optional explanation, decision table, example, callout, illustration, or audio.

[^1]: [Source title](https://example.com)
```

**CRITICAL content rules:**
- Add exactly one blank line between closing frontmatter and the card front.
- Use `—` (em dash) as separator after the title/term
- The first blank line after the answer ends the Anki back side. Everything below it is extended note content and is not part of the recall criterion.
- Do not put blank lines inside the mandatory answer. Keep it to one independently gradable idea.
- Bold the front as `**Question or term**`. Prefer a question when it makes the expected recall clearer.
- Cite claims with footnote markers in the relevant sentence. Put footnote definitions after a blank line; do not add a separate `Source: [^1]` label.
- Keep the card atomic, but allow the extended note to contain concise details, tables, callouts, examples, wikilinks, illustrations, or audio.
- ID field is added automatically by a separate plugin — do not include it manually

## Recall Design

Design the card around how the learner will decide whether recall succeeded:

1. **One cue, one grading target.** The front must make it clear what must be reproduced.
2. **Minimum sufficient answer.** Include only the information that must be remembered every time.
3. **Context independence.** The mandatory answer must make sense without opening Google or another note.
4. **Refined wording.** Remove qualifiers and examples that do not change the core claim.
5. **Split overload.** If it is unclear how many details must be recalled, create multiple cards instead of a list-heavy answer.
6. **Coverage over quotas.** For a deck, create as many cards as needed to cover distinct learning objectives; do not target an arbitrary count or duplicate ideas to enlarge the deck.

### Extended Note Content

After the first blank line, the flashcard becomes a normal knowledge note. Use this area to make the note useful without expanding the required recall:

- explain why the answer matters;
- add a small decision table when it reduces ambiguity;
- link prerequisite and neighboring concepts with wikilinks;
- add a callout for a practical test or common mistake;
- attach an illustration or audio example when perception is part of the concept;
- add authoritative sources as footnotes.

Media placement follows the learning goal:

- put media on the front when it is the stimulus to identify;
- keep it in the mandatory answer only when it is necessary feedback;
- otherwise place it in the extended note as optional reinforcement.

## Common Flashcard Types

### 1. Code Flashcard

**Tag**: `note/specific/code`
**Title format**: `(function_name) **function_name()**` (with parentheses)
**Use**: Programming functions, methods, syntax

Example:
```markdown
---
tags:
  - note/specific/code
  - category/js
aliases:
  - map
deck: obsidian::js
created: 2026-02-08T15:30:00+07:00
updated: 2026-02-08T15:30:00+07:00
---

**map()**
—
Creates a new array by applying a function to each element of the original array.

## Example

```js
const numbers = [1, 2, 3, 4];
const doubled = numbers.map(x => x * 2);
// [2, 4, 6, 8]
```
```

### 2. Exact Definition

**Tag**: `note/specific/exact`
**Use**: Precise terminology, formal definitions

Example:
```markdown
---
tags:
  - note/specific/exact
  - category/computer_science/algorithms
aliases: []
deck: obsidian::computer_science::algorithms
created: 2026-02-08T15:30:00+07:00
updated: 2026-02-08T15:30:00+07:00
---

**Quicksort**
—
A divide-and-conquer sorting algorithm that partitions elements around a selected pivot.

## Complexity

| Case | Time |
|---|---:|
| Average | `O(n log n)` |
| Worst | `O(n²)` |
```

## Category and Deck Validation

**CRITICAL:** Only use EXISTING categories and decks. Categories and decks are defined in the system.

### Validation Workflow

**Before creating ANY flashcard:**

1. **Read `home/prefixes.md`** to discover available decks:
   - Categories section: flashcard categories with deck paths
   - Code section: programming language decks
   - Look for patterns like `computer_science – cs` or `js – js`

2. **Validate category exists** using Glob:
   - Use `base/categories/*.md` to list available categories
   - Match the category from prefixes.md to existing category files

3. **Extract deck path** from prefixes.md:
   - For simple prefix: `computer_science – cs` → deck is `obsidian::computer_science`
   - For subcategory: `computer_science,algorithms – cs_a` → deck is `obsidian::computer_science::algorithms`
   - For code: `js – js` → deck is `obsidian::js`

4. **If category/deck doesn't exist**:
   - Do NOT create flashcard
   - Ask user to clarify category or suggest existing alternatives
   - List available categories/decks from prefixes.md

### Category Tag Format

- `category/<category_name>` — where `<category_name>` matches the category folder in `base/categories/`
- For subcategories: `category/<main>/<sub>` — e.g., `category/computer_science/algorithms`

## Workflow

### Creating a Single Flashcard

1. **Validate category and deck FIRST**:
   - Read `home/prefixes.md` to get available decks
   - Use Glob to verify category exists in `base/categories/`
   - If category doesn't exist, stop and ask user

2. **Gather information from user**:
   - What is the flashcard about? (topic/concept)
   - What type of flashcard? (basic, code, exact)
   - What category/deck? (suggest from available in prefixes.md)
   - What is the content/definition?

3. **Generate example flashcard** with:
   - Proper filename (lowercase, noun phrases, no dates/numbers)
   - Correct frontmatter based on type with VALIDATED category and deck
   - Exactly one blank line after frontmatter
   - A single recall cue, `—`, and a compact mandatory answer ending at the first blank line
   - Optional extended note content after that boundary
   - Footnote sources and useful media where appropriate
   - Current timestamp in ISO 8601 with timezone

4. **Show example to user** and ask: "Is this correct? Should I create this flashcard?"

5. **Create note** in `base/notes/` if user confirms

### Creating Multiple Flashcards

1. **Validate category and deck FIRST** (same as single flashcard)
2. **Confirm topic and type** with user
3. **Ask for flashcard data** in structured format
4. **Build a learning-objective map** and split it into independently gradable cards; do not impose a fixed card count
5. **Generate examples for all flashcards** with validated metadata
6. **Show examples and ask for confirmation**
7. **Create all flashcards** if user confirms

## Quality Gate

Before creating each card, verify:

- the front asks for one thing;
- the mandatory back can be graded as recalled/not recalled without guessing a list length;
- the first blank line appears only after the mandatory answer;
- the mandatory answer is understandable without the extended note;
- extended details do not silently add new required recall criteria;
- tables are used for decisions or comparisons, not decoration;
- sources are footnotes with a blank line before their definitions;
- media improves recognition or understanding and is not merely ornamental;
- filename, category tag, and deck are valid and unique.

## Filename Rules

- **Lowercase** (except proper nouns)
- **Noun phrases** (no questions, no pronouns)
- **No dates or numbers** in filename
- **Filesystem-safe** characters only
- **Unique** across vault

Good examples:
- `binary search.md`
- `js map().md`
- `quicksort.md`

Bad examples:
- `What is binary search.md` (question)
- `2024-01-15 binary search.md` (date)
- `binary-search-algorithm-1.md` (number)

## Deck Migration Utility

The `change-deck.py` script (included in this skill) helps reorganize flashcards by changing deck and category tags in bulk.

### Usage

From the Obsidian vault root:
```bash
python3 .claude/skills/obsidian-flashcards/change-deck.py [old_deck] [new_deck] [relative_path]
```

**Examples**:
```bash
# Change all computer_science cards to computer_science/basics
python3 .claude/skills/obsidian-flashcards/change-deck.py "computer_science" "computer_science/basics"

# Change within specific directory
python3 .claude/skills/obsidian-flashcards/change-deck.py "python" "python/advanced" base/notes

# Search from current directory
python3 .claude/skills/obsidian-flashcards/change-deck.py "math" "math/calculus" .
```

### What it does

1. Finds all notes with `deck: obsidian::<old_deck>` and `category/<old_deck>` tag
2. Changes tag: `category/<old_deck>` → `category/<new_deck>`
3. Changes deck: `obsidian::<old_deck>` → `obsidian::<new_deck>` (replaces `/` with `::`)
4. Confirms before making changes
5. Reports changed files

### When to use

- Reorganizing flashcard hierarchy (e.g., `js` → `js/basics`, `js/advanced`)
- Splitting large decks into subcategories
- Moving cards between categories
- Renaming deck paths

## Available Decks Reference

Check `home/prefixes.md` for the current list of available decks. Common examples:

**Categories (flashcards):**
- `computer_science` → `obsidian::computer_science`
- `computer_science,algorithms` → `obsidian::computer_science::algorithms`
- `english` → `obsidian::english`
- `artificial_intelligence,deep_learning,basics` → `obsidian::artificial_intelligence::deep_learning::basics`

**Code (programming languages):**
- `js` → `obsidian::js`
- `python` → `obsidian::python`
- `sql` → `obsidian::sql`

**Note:** This is just an example. ALWAYS read `home/prefixes.md` before creating flashcards to get the current accurate list.

## Tips

- **Always validate first** — read `home/prefixes.md` and check `base/categories/` before creating flashcards
- **Keep recall atomic** — one grading target per card; move nuance below the first blank line
- **Use hierarchical decks** for better organization (`category::subcategory`)
- **Code flashcards** should include working examples
- **Exact definitions** are for formal terminology
