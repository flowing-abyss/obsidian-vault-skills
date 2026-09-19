"""Two notes with one name make links ambiguous."""

from engine.findings import Finding

ID = "duplicate-name"
ORDER = 90
ABOUT = "No other note in the vault has the same file name."


def run(ctx):
    stem = ctx.path.rsplit("/", 1)[-1][:-3]
    others = [p for p in ctx.vault.paths_by_name(stem) if p != ctx.path and not ctx.vault.is_ignored(p)]
    if not others:
        return []
    return [Finding(ID, f'Another note has the same name: "{others[0]}".', severity="warning",
                    hint="Links by name become ambiguous. Pick a unique name.")]
