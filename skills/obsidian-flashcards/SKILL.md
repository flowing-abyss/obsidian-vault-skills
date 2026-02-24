---
name: obsidian-flashcards
description: 'Create flashcard notes for Anki integration with proper deck paths, category tags, and content structure (no empty lines). INVOKE when user wants to create study cards or flashcards for spaced repetition. Triggers: "create flashcard", "flashcards", "study cards", "Anki", "spaced repetition", "карточка", "создай флэшкарту", "карточки для повторения", "анки карточка", "флэшкарды". Shows example first, creates on confirmation.'
---

# Obsidian Flashcards

Create flashcard notes with correct metadata structure and content formatting for Anki integration.

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
**Title** or **Term**
—
Content / Definition / Explanation
[Optional: Code blocks, quotes, lists, etc.]
```

**CRITICAL content rules:**
- **NO EMPTY LINES** — Plugin limitation requires no blank lines in flashcard body
- Use `—` (em dash) as separator after the title/term
- Title should be bolded with `**Title**`
- Keep content atomic (one concept per flashcard)
- ID field is added automatically by a separate plugin — do not include it manually

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
A divide-and-conquer sorting algorithm that selects a pivot element and partitions the array around it.
Average time complexity: O(n log n)
Worst case: O(n²)
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
   - Content with `—` separator and NO EMPTY LINES
   - Current timestamp in ISO 8601 with timezone

4. **Show example to user** and ask: "Is this correct? Should I create this flashcard?"

5. **Create note** in `base/notes/` if user confirms

### Creating Multiple Flashcards

1. **Validate category and deck FIRST** (same as single flashcard)
2. **Confirm topic and type** with user
3. **Ask for flashcard data** in structured format
4. **Generate examples for all flashcards** with validated metadata
5. **Show examples and ask for confirmation**
6. **Create all flashcards** if user confirms

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
- **Keep flashcards atomic** — one concept per card
- **Use hierarchical decks** for better organization (`category::subcategory`)
- **Code flashcards** should include working examples
- **Exact definitions** are for formal terminology
