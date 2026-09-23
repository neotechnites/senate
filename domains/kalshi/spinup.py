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
from domains.kalshi.interface.head_prompt import build_kalshi_head_prompt
from domains.kalshi.state.fact_store import FactStore
from domains.kalshi.state.seed import seed_kalshi_database

POD_DIR = Path(__file__).resolve().parent
CLAUDE_BIN = os.path.expanduser("~/.local/bin/claude")


_LAST_SUMMARY = ""


def res_summary() -> str:
    return _LAST_SUMMARY


def check_domain_integrity() -> bool:
    """Run local Kalshi property test suite."""
    global _LAST_SUMMARY
    # 2026-09-09: pytest, not unittest discover -- tests/conftest.py redirects
    # the DB path to a temp file for the whole run, so the integrity check can
    # never write into data/kalshi_domain.db (the laptop MIRROR must never be
    # mutated; unittest discover skipped conftest and touched it).
    res = subprocess.run(
        [sys.executable, "-m", "pytest", str(POD_DIR / "tests"), "-q", "-p", "no:cacheprovider"],
        cwd=str(POD_DIR),
        capture_output=True,
        text=True,
    )
    tail = [ln for ln in (res.stdout or "").splitlines() if "passed" in ln or "failed" in ln]
    _LAST_SUMMARY = tail[-1].strip(" =") if tail else ""
    if res.returncode != 0:
        print(f"❌ DOMAIN TEST SUITE FAILED:\n{(res.stdout or '')[-3000:]}\n{res.stderr[-2000:]}", file=sys.stderr)
        return False
    return True


def main():
    print("══════════════════════════════════════════════════════════════")
    print("             KALSHI DOMAIN HEAD — DEDICATED SPIN-UP           ")
    print("══════════════════════════════════════════════════════════════")

    # 1. Test Suite Integrity Check
    print("[1/2] Verifying Kalshi Invariants & Property Tests...", end=" ", flush=True)
    if check_domain_integrity():
        print("✅ ALL GREEN (" + (res_summary() or "pod suite") + ")")
    else:
        print("❌ INTEGRITY CHECK FAILED. Aborting spin-up.")
        sys.exit(1)

    # 2. State Store Check & Seed
    store = FactStore()
    seed_kalshi_database(store)
    status_summary = render_kalshi_status(store)
    print("[2/2] Local SQLite FactStore Active.")
    print("──────────────────────────────────────────────────────────────")

    # 2026-09-09 (Ryan): the prompt is BUILT FROM THE DATABASE -- ratified
    # facts, the open-mistake ledger and the deposits-based money line -- never
    # typed from memory.  See interface/head_prompt.py for the receipts.
    system_prompt = build_kalshi_head_prompt(store, status_summary)

    claude_path = CLAUDE_BIN if os.path.exists(CLAUDE_BIN) else "claude"

    if "--dry" in sys.argv:
        print("\nSYSTEM PROMPT:")
        print(system_prompt)
        return

    initial_prompt = (
        "ORGANIZATIONAL HEAD RESUMPTION:\n"
        "1. Ground on the VPS (live truth), not this mirror: `ssh -i ~/.ssh/senate_vps_ed25519 "
        "ubuntu@129.146.115.241 'cd /home/ubuntu/senate/domains/kalshi && ./kalshi.py status && "
        "./kalshi.py placement show && systemctl --user list-units \"kalshi*\" --no-legend'`.\n"
        "2. Read the latest memory file named in the prompt; check fills since it was written "
        "(`./kalshi.py position list` on the VPS) and the seeder/rotation journals.\n"
        "3. Brief Ryan in 2-3 sentences: account value vs deposits (or UNKNOWN), book N/20, fills "
        "since the last brief, anything blocked.  Name each number's provenance.  Then stay dormant."
    )
    cmd = [claude_path, "--system-prompt", system_prompt, initial_prompt]


    try:
        os.execvp(claude_path, cmd)


    except FileNotFoundError:
        print(f"❌ Error: Claude binary not found at '{claude_path}'.", file=sys.stderr)
        sys.exit(1)




if __name__ == "__main__":
    main()
