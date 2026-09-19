"""Notes of a type live in the folder its manifest names."""

from engine.findings import Finding

ID = "enforce_folder"
ORDER = 60
ABOUT = "The note is inside the folder set by enforce_folder."


def run(ctx):
    if ctx.schema is None or not isinstance(ctx.schema.enforce_folder, str):
        return []
    folder = ctx.schema.enforce_folder.rstrip("/") + "/"
    if ctx.path.startswith(folder):
        return []
    here = ctx.path.rsplit("/", 1)[0] if "/" in ctx.path else "the vault root"
    return [Finding(ID, f'This note belongs in "{folder}" but is in "{here}".', field="__location__",
                    severity="warning", hint=f'Move it to "{folder}{ctx.path.rsplit("/", 1)[-1]}".')]
