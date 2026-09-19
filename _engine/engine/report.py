"""Plain text report for people and agents."""

from __future__ import annotations

MAX_FINDINGS = 15


def render(path: str, findings, schema_name: str = "") -> str:
    shown = [f for f in findings if f.severity != "info"]
    if not shown:
        return f"OK {path}" + (f" ({schema_name})" if schema_name else "")
    lines = [f"{path}" + (f" ({schema_name})" if schema_name else "")]
    for f in shown[:MAX_FINDINGS]:
        lines.append("  " + f.line().replace("\n", "\n    "))
    if len(shown) > MAX_FINDINGS:
        lines.append(f"  and {len(shown) - MAX_FINDINGS} more")
    if any(f.fixable for f in shown):
        lines.append(f'  Items marked fixable: run python3 .claude/_engine/vault.py fix "{path}"')
    manifests = sorted({f.manifest for f in shown if f.manifest})
    if manifests:
        lines.append(f"  Rules: {', '.join(manifests)}")
    return "\n".join(lines)
