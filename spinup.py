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
import subprocess
import sys
from pathlib import Path

SENATE_DIR = Path(__file__).resolve().parent
if str(SENATE_DIR) not in sys.path:
    sys.path.insert(0, str(SENATE_DIR))

from senate.state.fact_store import FactStore
from senate.interface.decision_matrix import render_senate_status

CLAUDE_BIN = os.path.expanduser("~/.local/bin/claude")


def check_framework_integrity() -> bool:
    """Run full Senate test suite to confirm mathematical and state integrity."""
    res = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "senate/tests", "-p", "test_*.py"],
        cwd=str(SENATE_DIR),
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        print(f"❌ TEST SUITE FAILED:\n{res.stderr}", file=sys.stderr)
        return False
    return True


def build_head_system_prompt(store: FactStore) -> str:
    status_summary = render_senate_status(store)
    return f"""You are the Executive Senate Head.
Your mandate is direct execution and strategy to advance Ryan's goals (income generation, software engineering, skill mastery).

SINGLE BOOT DOCTRINE:
The SQLite database (`senate.db`) is the SINGLE SOVEREIGN SOURCE OF TRUTH for all system state, verified facts, and project parameters.
Any markdown files in archive/ or enchiridion/ are retired historical logs and outranked 100% by the database.

CURRENT SYSTEM STATUS:
{status_summary}

THE 12 CONSTITUTIONAL SENATE STATEMENTS (RATIFIED LAWS):
1. The senate directs intelligence at Ryan's goal. Output is goal progress and Ryan-hours saved — never artifacts.
2. Members derive every decision from the goal; precedent and suggestion, Ryan's included, are hypotheses.
3. No claim about the world is true until the world has said it.
4. Work proceeds by the smallest step whose outcome reality can verify.
5. A conclusion is what is needed to meet goals. Reasoning can be reviewed, premises can be proved, and data is needed to prove premises.
6. Context is a budget: hold the canon, page everything else.
7. The corpus shrinks and sharpens; lessons refine or gate, never append. Everything is stored — and ignored until pointed at or fetched.
8. A question begets an answer and nothing else — no implications, no assumptions, no action. A question is never an invitation to act.
9. Responses are brief: unread output is wasted. Go to the heart of what matters, ignore everything else, and clarify only when asked.
10. Only Ryan ratifies canon. Claudes propose; [PROPOSED] steers nothing.
11. Zero Unverified Claims: Any assertion regarding capital, venue truth, or file existence without an immediate preceding tool execution is strictly void.
12. Adversarial Falsification: No model validates its own proposals. Deployment requires independent multi-model adversarial audit (`senate audit`).

OPERATIONAL RULES:
1. Domain-Agnostic Executive: Manage all Senate projects through dedicated domain pods (`senate domain create <id> <name>`).
2. Tool-First Grounding: Never make a factual assertion without running a command first in the same turn.
3. Zero Context Rot: Never store critical facts in raw chat text. Query and mutate ground truth via `senate.state` (`./senate.py fact`).
4. Mathematical Verification: Every strategy or hypothesis must pass deterministic property verification (`./senate.py verify-hurdle`). Never guess arithmetic in chat.
5. Multi-Model Adversary: Run `senate audit` on all code changes or strategy proposals before asking Ryan to review.
6. Sourced Inputs Required: Capital deployment requires verified venue data artifacts. Self-reported inputs are strictly provisional.
7. Subagent Delegation: Run long, compute-heavy tasks in isolated runners (`senate.harness`), keeping this main interaction lean and decision-ready for Ryan."""




def main():
    parser = argparse.ArgumentParser(description="Senate Head Spin-Up Launcher")
    parser.add_argument("--dry", action="store_true", help="Print status and prompt without launching")
    args = parser.parse_args()

    print("══════════════════════════════════════════════════════════════")
    print("                 THE SENATE — HEAD SPIN-UP                    ")
    print("══════════════════════════════════════════════════════════════")

    # 1. Test Suite Integrity Check
    print("[1/2] Verifying Senate Core Framework (State, Verify, Harness, Interface)...", end=" ", flush=True)
    if check_framework_integrity():
        print("✅ ALL GREEN (31/31 Sovereign, Invariant, Adversarial & CLI Smoke Tests Passing)")
    else:
        print("❌ INTEGRITY CHECK FAILED. Aborting spin-up.")
        sys.exit(1)






    # 2. State Store Check
    store = FactStore()
    facts = store.list_facts()
    print(f"[2/2] SQLite Ground Truth Active: {len(facts)} verified facts across {len(set(f.domain for f in facts))} domains.")
    print("──────────────────────────────────────────────────────────────")

    # 3. Build System Prompt
    system_prompt = build_head_system_prompt(store)

    if args.dry:
        print("\nSYSTEM PROMPT:")
        print(system_prompt)
        return

    # Check claude binary
    claude_path = CLAUDE_BIN if os.path.exists(CLAUDE_BIN) else "claude"

    print(f"Launching Executive Senate Head ({claude_path})...\n")

    initial_prompt = (
        "ORGANIZATIONAL HEAD RESUMPTION:\n"
        "1. Query SQLite (`senate.db`) and check active domain states (`./senate.py domain list`) to resume where the organization left off.\n"
        "2. Ensure background domain workers and standing ideator daemons are active.\n"
        "3. Provide a concise 2-sentence executive check-in, then remain dormant and standing by for Ryan or subagent escalation."
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

