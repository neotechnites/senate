#!/usr/bin/env python3
"""Dedicated Domain Head Launcher for Automotive Chassis Engineering.
Context is 100% focused on automotive. Zero cross-domain noise.
"""
import os
import sys
from pathlib import Path

POD_DIR = Path(__file__).resolve().parent
CLAUDE_BIN = os.path.expanduser("~/.local/bin/claude")

SYSTEM_PROMPT = """You are the Dedicated Domain Head for Automotive Chassis Engineering (automotive).
MANDATE: CAD stress-strain and aerodynamic simulation engine

OPERATING RULES:
1. Complete Domain Focus: You operate in pure isolation for this project.
2. Invariants: All code and proposals must pass tests in `tests/test_domain.py`.
3. High Leverage: Direct all intelligence at advancing milestones for Ryan.
"""

def main():
    print("══════════════════════════════════════════════════════════════")
    print("             AUTOMOTIVE CHASSIS ENGINEERING DOMAIN HEAD SPIN-UP")
    print("══════════════════════════════════════════════════════════════")
    claude_path = CLAUDE_BIN if os.path.exists(CLAUDE_BIN) else "claude"
    cmd = [claude_path, "--system-prompt", SYSTEM_PROMPT]
    os.execvp(claude_path, cmd)

if __name__ == "__main__":
    main()
