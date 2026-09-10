#!/usr/bin/env python3
"""Steward Domain Head launcher. The prompt is BUILT FROM THE POD DB, never typed."""
import os
import re
import subprocess
import sys
from pathlib import Path

POD_DIR = Path(__file__).resolve().parent
REPO_ROOT = POD_DIR.parents[1]
for p in (str(REPO_ROOT), str(POD_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from domains.steward.state.db import Database                    # noqa: E402
from domains.steward.state.canon import seed as seed_canon       # noqa: E402
from domains.steward.interface.head_prompt import (              # noqa: E402
    build_head_prompt, canon_line_count, CANON_MAX_LINES)

CLAUDE_BIN = os.path.expanduser("~/.local/bin/claude")

INITIAL = (
    "STEWARD HEAD RESUMPTION:\n"
    "1. GROUND first: `./steward.py status`. Assert nothing you have not read.\n"
    "2. Brief Ryan in 2-3 sentences: how many obligations are captured, how many are "
    "overdue, how many completions he has actually reported, and whether a message has "
    "ever reached his phone. Name each number's provenance.\n"
    "3. Say plainly what is blocking the first real receipt (Telegram channel unwired, "
    "host not provisioned, backlog empty -- whichever is true).\n"
    "4. Then go dormant. Escalate only for a decision that is genuinely his."
)


def main():
    print("══════════════════════════════════════════════════════════════")
    print("              STEWARD DOMAIN HEAD SPIN-UP")
    print("══════════════════════════════════════════════════════════════")

    res = subprocess.run([sys.executable, "-m", "pytest", "tests", "-q",
                          "-p", "no:cacheprovider"],
                         cwd=str(POD_DIR), capture_output=True, text=True)
    if res.returncode != 0:
        print(f"❌ POD TESTS FAILED — aborting.\n{(res.stdout or '')[-2500:]}",
              file=sys.stderr)
        sys.exit(1)
    m = re.search(r"(\d+)\s+passed", res.stdout or "")
    print(f"✅ {m.group(1) if m else '?'} pod tests passed (isolated DB).")

    db = Database()
    with db.get_connection() as conn:
        seed_canon(conn)                      # canon re-asserts itself every boot
        prompt = build_head_prompt(conn)
    print(f"   Prompt built from {db.db_path.name}: canon "
          f"{canon_line_count(prompt)}/{CANON_MAX_LINES} lines.")

    if "--dry" in sys.argv:
        print("\nSYSTEM PROMPT:\n" + prompt)
        return

    claude = CLAUDE_BIN if os.path.exists(CLAUDE_BIN) else "claude"
    print(f"Launching Steward Domain Head ({claude})...\n")
    os.execvp(claude, [claude, "--system-prompt", prompt, INITIAL])


if __name__ == "__main__":
    main()
