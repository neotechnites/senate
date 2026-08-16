"""Senate Interface module."""

from senate.interface.cli import main
from senate.interface.decision_matrix import render_senate_status

__all__ = ["main", "render_senate_status"]
