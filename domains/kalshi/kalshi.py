#!/usr/bin/env python3
"""Executable launcher for Kalshi Domain Pod CLI."""

import sys
from pathlib import Path

# Ensure root workspace is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from domains.kalshi.interface.cli import main

if __name__ == "__main__":
    sys.exit(main())
