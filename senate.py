#!/usr/bin/env python3
"""Executable launcher for The Senate Core Framework CLI."""

import sys
from pathlib import Path

# Ensure root workspace is in sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from senate.interface.cli import main

if __name__ == "__main__":
    sys.exit(main())
