"""Agent adapters. Each one turns an agent's hook payload into engine calls.

The engine itself knows nothing about agents. Agents without hooks run
`vault.py check PATH` after an edit and read the same output.
"""

from __future__ import annotations

import sys


def run_hook(agent: str, event: str, vault_root=None) -> int:
    try:
        if agent == "claude-code":
            from . import claude_code

            return claude_code.run(event, vault_root)
        print(f'Unknown agent "{agent}". Known: claude-code.', file=sys.stderr)
        return 0
    except Exception as exc:  # a broken hook must never block the agent
        print(f"vault engine hook failed: {exc}", file=sys.stderr)
        return 0
