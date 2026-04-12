#!/usr/bin/env python3
"""
Script to change deck and category tags in Obsidian notes.

Usage:
    python3 change-deck.py [old_deck] [new_deck] [relative_path]

Examples:
    python3 change-deck.py "computer_science" "computer_science/basics"
    python3 change-deck.py "python" "python/advanced" base/notes
    python3 change-deck.py "math" "math/calculus" .
"""
import sys
import re
from pathlib import Path


def has_deck(file_path, deck_name):
    """Check if a markdown file has the specified deck"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract frontmatter
        frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if not frontmatter_match:
            return False

        frontmatter = frontmatter_match.group(1)

        # Check for deck property: deck: obsidian::deck_name
        deck_pattern = rf"^\s*deck:\s*obsidian::{re.escape(deck_name)}\s*$"
        if not re.search(deck_pattern, frontmatter, re.MULTILINE):
            return False

        # Check for category tag in tags section: category/deck_name
        category_tag = f"category/{deck_name}"

        # Pattern 1: tags as a list (with - prefix)
        tags_list_pattern = r"^\s*tags:\s*\n((?:\s*-\s+.+\n)*)"
        tags_match = re.search(tags_list_pattern, frontmatter, re.MULTILINE)
        if tags_match:
            tags_section = tags_match.group(1)
            tag_line_pattern = rf"^\s*-\s+{re.escape(category_tag)}\s*$"
            if re.search(tag_line_pattern, tags_section, re.MULTILINE):
                return True

        # Pattern 2: tags as inline array
        tags_inline_pattern = r"^\s*tags:\s*\[([^\]]+)\]"
        tags_inline_match = re.search(tags_inline_pattern, frontmatter, re.MULTILINE)
        if tags_inline_match:
            tags_content = tags_inline_match.group(1)
            tags_list = [t.strip() for t in tags_content.split(",")]
            if category_tag in tags_list:
                return True

        return False
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False


def change_deck_in_file(file_path, old_deck, new_deck):
    """Change deck and category tag in a markdown file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract frontmatter
        frontmatter_match = re.match(
            r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL
        )
        if not frontmatter_match:
            return False, "No frontmatter found"

        frontmatter = frontmatter_match.group(1)
        rest_content = frontmatter_match.group(2)

        # Replace deck property
        old_deck_property = f"obsidian::{old_deck}"
        new_deck_property = f"obsidian::{new_deck.replace('/', '::')}"

        deck_pattern = rf"(^\s*deck:\s*)obsidian::{re.escape(old_deck)}(\s*)$"
        frontmatter = re.sub(
            deck_pattern, rf"\1{new_deck_property}\2", frontmatter, flags=re.MULTILINE
        )

        # Replace category tag
        old_category_tag = f"category/{old_deck}"
        new_category_tag = f"category/{new_deck}"

        # Replace in list format
        tag_line_pattern = rf"(^\s*-\s+){re.escape(old_category_tag)}(\s*)$"
        frontmatter = re.sub(
            tag_line_pattern,
            rf"\1{new_category_tag}\2",
            frontmatter,
            flags=re.MULTILINE,
        )

        # Replace in inline array format
        def replace_in_array(match):
            tags_content = match.group(1)
            tags_list = [t.strip() for t in tags_content.split(",")]
            tags_list = [
                new_category_tag if t == old_category_tag else t for t in tags_list
            ]
            return f"tags: [{', '.join(tags_list)}]"

        frontmatter = re.sub(
            r"^\s*tags:\s*\[([^\]]+)\]",
            replace_in_array,
            frontmatter,
            flags=re.MULTILINE,
        )

        # Write back
        new_content = f"---\n{frontmatter}\n---\n{rest_content}"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        return True, "Success"
    except Exception as e:
        return False, str(e)


def find_notes_with_deck(search_path, deck_name):
    """Find all markdown files with the specified deck"""
    notes_with_deck = []

    for md_file in search_path.rglob("*.md"):
        if has_deck(md_file, deck_name):
            notes_with_deck.append(md_file)

    return notes_with_deck


def main():
    # Get script directory
    script_dir = Path(__file__).parent.absolute()

    # Parse command line arguments
    if len(sys.argv) < 3:
        print("Usage: python3 change-deck.py [old_deck] [new_deck] [relative_path]")
        print("\nExamples:")
        print('  python3 change-deck.py "computer_science" "computer_science/basics"')
        print('  python3 change-deck.py "python" "python/advanced" base/notes')
        print('  python3 change-deck.py "math" "math/calculus" .')
        sys.exit(1)

    old_deck = sys.argv[1]
    new_deck = sys.argv[2]
    relative_path = sys.argv[3] if len(sys.argv) > 3 else "."

    # Resolve the search path
    search_path = (script_dir / relative_path).resolve()

    if not search_path.exists():
        print(
            f"Error: Path '{relative_path}' does not exist (resolved to {search_path})"
        )
        sys.exit(1)

    if not search_path.is_dir():
        print(f"Error: Path '{relative_path}' is not a directory")
        sys.exit(1)

    print(f"Searching for notes with deck '{old_deck}' in '{relative_path}'...")
    notes_with_deck = find_notes_with_deck(search_path, old_deck)

    if not notes_with_deck:
        print(f"No notes found with deck '{old_deck}'.")
        return

    print(f"\nFound {len(notes_with_deck)} notes with deck '{old_deck}':")
    for note in notes_with_deck:
        try:
            relative_to_search = note.relative_to(search_path)
            print(f"  - {relative_to_search}")
        except ValueError:
            print(f"  - {note}")

    # Confirm changes
    print(f"\nThis will change:")
    print(f"  - Tag: category/{old_deck} -> category/{new_deck}")
    print(f"  - Deck: obsidian::{old_deck} -> obsidian::{new_deck.replace('/', '::')}")
    response = input(
        f"\nDo you want to change these {len(notes_with_deck)} notes? (yes/no): "
    )

    if response.lower() in ["yes", "y"]:
        changed_count = 0
        for note in notes_with_deck:
            success, message = change_deck_in_file(note, old_deck, new_deck)
            if success:
                try:
                    relative_to_search = note.relative_to(search_path)
                    print(f"Changed: {relative_to_search}")
                except ValueError:
                    print(f"Changed: {note}")
                changed_count += 1
            else:
                try:
                    relative_to_search = note.relative_to(search_path)
                    print(f"Error changing {relative_to_search}: {message}")
                except ValueError:
                    print(f"Error changing {note}: {message}")

        print(f"\nSuccessfully changed {changed_count} notes.")
    else:
        print("Changes cancelled.")


if __name__ == "__main__":
    main()
