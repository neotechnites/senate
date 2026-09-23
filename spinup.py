#!/usr/bin/env python3
"""spinup.py — Dedicated Senate Head launcher.

1. Runs pre-flight verification across the Senate Core Framework (State, Verify, Harness, Interface).
2. Reads active project states and ground-truth facts from SQLite FactStore.
3. Launches the Executive Senate Head with autonomous subagent delegation and zero-context-rot tools.

Usage:
    ./spinup.sh              -> Verifies and launches interactive Senate Head session
    python3 spinup.py --dry  -> Prints verification and prompt payload without launching
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

SENATE_DIR = Path(__file__).resolve().parent
if str(SENATE_DIR) not in sys.path:
    sys.path.insert(0, str(SENATE_DIR))

from senate.state.fact_store import FactStore
from senate.interface.head_prompt import (build_senate_head_prompt, canon_line_count,
                                          CANON_MAX_LINES)

CLAUDE_BIN = os.path.expanduser("~/.local/bin/claude")


def check_framework_integrity() -> bool:
    """Run the full Senate suite to confirm state and mathematical integrity.

    PYTEST, not `unittest discover` (2026-09-09): unittest skips senate/tests/conftest.py,
    which redirects DEFAULT_DB_PATH to a temp file.  Without it this boot gate ran
    test_cli_smoke's domain create/delete lifecycle against the REAL data/senate.db --
    booting the head mutated sovereign state.  Ledger: test_suite_mutated_the_sovereign_db.
    """
    res = subprocess.run(
        [sys.executable, "-m", "pytest", "senate/tests", "-q", "-p", "no:cacheprovider"],
        cwd=str(SENATE_DIR),
        capture_output=True,
        text=True,
    )
    out = res.stdout or ""
    if res.returncode != 0:
        print(f"❌ TEST SUITE FAILED:\n{out[-3000:]}\n{res.stderr[-1500:]}", file=sys.stderr)
        return None
    m = re.search(r"(\d+)\s+passed", out)
    return int(m.group(1)) if m else 0


def build_head_system_prompt(store: FactStore) -> str:
    """The head's system prompt, BUILT FROM THE DATABASE.

    This function used to be a hand-typed f-string: 14 "ratified" statements recited as
    prose while data/senate.db held 3 facts and no mistakes ledger, plus a status block
    whose "117.0 Ryan-hours saved" was a seed value from 2026-08-17 that nothing had
    touched and no trial row backed.  The head recited canon it had never read and
    reported its own marks as progress.  Everything now comes from senate/interface/
    head_prompt.py, which reads facts, goals, caps and the mistakes ledger out of SQLite.
    Ledger: head_prompt_typed_from_memory, goal_progress_self_marked, fact_written_but_never_read.
    """
    return build_senate_head_prompt(store)


def main():
    parser = argparse.ArgumentParser(description="Senate Head Spin-Up Launcher")
    parser.add_argument("--dry", action="store_true", help="Print status and prompt without launching")
    args = parser.parse_args()

    print("══════════════════════════════════════════════════════════════")
    print("                 THE SENATE — HEAD SPIN-UP                    ")
    print("══════════════════════════════════════════════════════════════")

    # 1. Test Suite Integrity Check
    print("[1/2] Verifying Senate Core Framework (State, Verify, Harness, Interface)...", end=" ", flush=True)
    # The count is READ FROM PYTEST, never printed as a literal. This banner used to
    # assert "31/31 ... Passing" whatever the suite actually did.
    n_passed = check_framework_integrity()
    if n_passed is None:
        print("❌ INTEGRITY CHECK FAILED. Aborting spin-up.")
        sys.exit(1)
    print(f"✅ {n_passed} tests passed (pytest, isolated DB).")






    # 2. State Store Check
    store = FactStore()
    facts = store.list_facts()
    print(f"[2/2] SQLite Ground Truth Active: {len(facts)} verified facts across {len(set(f.domain for f in facts))} domains.")
    print("──────────────────────────────────────────────────────────────")

    # 3. Build System Prompt
    system_prompt = build_head_system_prompt(store)

    n_canon = canon_line_count(system_prompt)
    print(f"      Prompt built from the DB: canon {n_canon}/{CANON_MAX_LINES} lines "
          "(statement 6 — context is a budget).")

    if args.dry:
        print("\nSYSTEM PROMPT:")
        print(system_prompt)
        return

    # Check claude binary
    claude_path = CLAUDE_BIN if os.path.exists(CLAUDE_BIN) else "claude"

    print(f"Launching Executive Senate Head ({claude_path})...\n")

    initial_prompt = (
        "ORGANIZATIONAL HEAD RESUMPTION:\n"
        "1. GROUND from SQLite before asserting anything: `./senate.py domain list`, the open "
        "rows of the `mistakes` table, and the goals block already in your prompt.\n"
        "2. Read the HANDOFF file named in your prompt.\n"
        "3. Brief Ryan in 2-3 sentences, NAMING each number's provenance (measured / modelled "
        "/ self-marked) and what is blocked. Then remain dormant, standing by for Ryan or a "
        "subagent escalation."
    )

    cmd = [
        claude_path,
        "--system-prompt", system_prompt,
        initial_prompt,
    ]

    try:
        os.execvp(claude_path, cmd)

    except FileNotFoundError:
        print(f"❌ Error: Claude binary not found at '{claude_path}'.", file=sys.stderr)
        print(f"To launch manually, run in this directory:\n  claude --system-prompt \"{system_prompt}\"", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

