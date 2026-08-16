"""Schema and input/output validation for The Senate Tool Harness."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class ToolExecutionResult:
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration_s: float
    timed_out: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    executed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def is_success(self) -> bool:
        return self.exit_code == 0 and not self.timed_out

    def to_dict(self) -> Dict[str, Any]:
        return {
            "command": self.command,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration_s": self.duration_s,
            "timed_out": self.timed_out,
            "is_success": self.is_success,
            "metadata": self.metadata,
            "executed_at": self.executed_at,
        }
