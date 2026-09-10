#!/usr/bin/env python3
"""Panopticon Domain Head launcher. The prompt is BUILT FROM THE POD DB, never typed."""
import os
import subprocess
import sys
from pathlib import Path

POD_DIR = Path(__file__).resolve().parent
REPO_ROOT = POD_DIR.parents[1]
for p in (str(REPO_ROOT), str(POD_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from domains.panopticon.state.db import Database                  # noqa: E402
from domains.panopticon.state.canon import seed as seed_canon     # noqa: E402
from domains.panopticon.interface.head_prompt import (            # noqa: E402
    build_head_prompt, canon_line_count, CANON_MAX_LINES)

CLAUDE_BIN = os.path.expanduser("~/.local/bin/claude")

INITIAL = (
    "PANOPTICON HEAD RESUMPTION:\n"
    "1. GROUND first: `./panopticon.py status`. Do not assert anything you have not read.\n"
    "2. Brief Ryan in 2-3 sentences: days left, the next gate, what is actually playable "
    "(a build that ran, per verify/oracle.py), and what is blocked on him.\n"
    "3. Then go dormant. Escalate only for a creative decision, a hard-date breach, a "
    "purchase, or evidence the core loop is not fun."
)


def main():
    print("══════════════════════════════════════════════════════════════")
    print("             PANOPTICON DOMAIN HEAD SPIN-UP")
    print("══════════════════════════════════════════════════════════════")

    res = subprocess.run([sys.executable, "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider"],
                         cwd=str(POD_DIR), capture_output=True, text=True)
    if res.returncode != 0:
        print(f"❌ POD TESTS FAILED — aborting.\n{(res.stdout or '')[-2500:]}", file=sys.stderr)
        sys.exit(1)
    import re
    m = re.search(r"(\d+)\s+passed", res.stdout or "")
    print(f"✅ {m.group(1) if m else '?'} pod tests passed (isolated DB).")

    db = Database()
    with db.get_connection() as conn:
        seed_canon(conn)                        # canon re-asserts itself every boot
        prompt = build_head_prompt(conn)
    print(f"   Prompt built from {db.db_path.name}: canon "
          f"{canon_line_count(prompt)}/{CANON_MAX_LINES} lines.")

    if "--dry" in sys.argv:
        print("\nSYSTEM PROMPT:\n" + prompt)
        return

    claude = CLAUDE_BIN if os.path.exists(CLAUDE_BIN) else "claude"
    print(f"Launching Panopticon Domain Head ({claude})...\n")
    os.execvp(claude, [claude, "--system-prompt", prompt, INITIAL])


if __name__ == "__main__":
    main()
