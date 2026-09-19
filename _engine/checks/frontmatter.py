"""The note must have frontmatter that parses."""

from engine.findings import Finding

ID = "frontmatter"
ORDER = 0
ABOUT = "Frontmatter exists and is valid YAML."


def run(ctx):
    note = ctx.note
    if not note.has_frontmatter:
        return [Finding(ID, "The note has no frontmatter.", severity="warning",
                        hint='Start the file with a "---" block that holds the properties.')]
    if note.error:
        return [Finding(ID, f"Frontmatter is not valid YAML: {note.error}.",
                        hint="Fix the YAML first. Other checks are skipped until it parses.")]
    return []
