#!/usr/bin/env python3
"""Dedicated Kalshi Domain Head Launcher.
100% focused on prediction market trading and capital generation.
Zero cross-domain noise.
"""

import os
import subprocess
import sys
from pathlib import Path

# Ensure root workspace in sys.path
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from domains.kalshi.interface.decision_matrix import render_kalshi_status
from domains.kalshi.state.fact_store import FactStore
from domains.kalshi.state.seed import seed_kalshi_database

POD_DIR = Path(__file__).resolve().parent
CLAUDE_BIN = os.path.expanduser("~/.local/bin/claude")


def check_domain_integrity() -> bool:
    """Run local Kalshi property test suite."""
    res = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(POD_DIR / "tests"), "-p", "test_*.py"],
        cwd=str(ROOT_DIR),
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        print(f"❌ DOMAIN TEST SUITE FAILED:\n{res.stderr}", file=sys.stderr)
        return False
    return True


def main():
    print("══════════════════════════════════════════════════════════════")
    print("             KALSHI DOMAIN HEAD — DEDICATED SPIN-UP           ")
    print("══════════════════════════════════════════════════════════════")

    # 1. Test Suite Integrity Check
    print("[1/2] Verifying Kalshi Invariants & Property Tests...", end=" ", flush=True)
    if check_domain_integrity():
        print("✅ ALL GREEN (24/24 Invariant, Payoff, Gate, Base-Rate & CLI Smoke Tests Passing)")
    else:
        print("❌ INTEGRITY CHECK FAILED. Aborting spin-up.")
        sys.exit(1)

    # 2. State Store Check & Seed
    store = FactStore()
    seed_kalshi_database(store)
    status_summary = render_kalshi_status(store)
    print("[2/2] Local SQLite FactStore Active.")
    print("──────────────────────────────────────────────────────────────")

    system_prompt = f"""You are the Dedicated Kalshi Domain Head for Ryan.
Your sole mandate is maximizing capital yield on Kalshi prediction markets for Ryan while preserving collateral.
Your workspace is `domains/kalshi/` and your database is `data/kalshi_domain.db`.

CURRENT KALSHI DOMAIN STATUS:
{status_summary}

KEY HARD INVARIANTS & CONSTITUTIONAL RULES:
1. Tool-First Grounding: You may NOT assert any claim regarding balances, positions, orders, or files without running a tool in that turn first.
2. Fundamental Base-Rate Side-Gate: Never quote NO at <=35c on measures with high historical pass rates (>65% YES). Quoting book geometry against fundamentals is prohibited.
3. Terminal Window Curfew: Never place or hold orders within 24h of window expiry (<24h).
4. Total Capital Risk Cap: Maximum capital budget is $250. Fills DO NOT open headroom. Total Capital = Positions + Resting Orders <= $250.
5. Mathematical Payoff Engine: Off-touch earning seats are NEVER canceled to hold cash. Run `./kalshi.py verify-payoff`.
6. Execution Gate: Never touch orders without the gate. All actions must route through `./kalshi.py order place` / `./kalshi.py order cancel`.
7. Zero Guessing: Query and mutate state strictly via `./kalshi.py` and SQLite.

First, run `./kalshi.py status` to verify current live ground truth with Ryan."""


    claude_path = CLAUDE_BIN if os.path.exists(CLAUDE_BIN) else "claude"

    if "--dry" in sys.argv:
        print("\nSYSTEM PROMPT:")
        print(system_prompt)
        return

    print(f"Launching Dedicated Kalshi Domain Head ({claude_path})...\n")
    initial_prompt = (
        "STANDING MANDATE EXECUTION:\n"
        "1. SEATS: Run `./kalshi.py status` and `./kalshi.py census` to evaluate live venue ground truth and 7-day family opportunities under depth >= 250 and 24h curfew.\n"
        "2. IDEATION: Run `senate ideate propose` on live tape hypotheses through the Gemini adversary; persist all kills and survivors to SQLite.\n"
        "3. FRAMEWORK: Verify that all 10 historical mistake invariants remain compiled as impossible.\n"
        "Present your verified findings and seat placement recommendations immediately."
    )
    cmd = [claude_path, "--system-prompt", system_prompt, initial_prompt]
    try:
        os.execvp(claude_path, cmd)
    except FileNotFoundError:
        print(f"❌ Error: Claude binary not found at '{claude_path}'.", file=sys.stderr)
        sys.exit(1)




if __name__ == "__main__":
    main()
