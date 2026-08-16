"""Data models for The Senate state management layer."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import json


@dataclass
class Fact:
    key: str
    domain: str
    value: Any
    source_artifact: str
    verified_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    verified_by: str = "operator"
    is_immutable: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "domain": self.domain,
            "value": self.value,
            "source_artifact": self.source_artifact,
            "verified_at": self.verified_at,
            "verified_by": self.verified_by,
            "is_immutable": self.is_immutable,
        }

    @classmethod
    def from_row(cls, row: tuple) -> "Fact":
        val = row[2]
        if isinstance(val, str):
            try:
                val = json.loads(val)
            except Exception:
                pass
        return cls(
            key=row[0],
            domain=row[1],
            value=val,
            source_artifact=row[3],
            verified_at=row[4],
            verified_by=row[5],
            is_immutable=bool(row[6]),
        )


@dataclass
class Hypothesis:
    hypo_id: str
    domain: str
    statement: str
    status: str  # UNTESTED, TESTING, CONFIRMED, KILLED
    kill_criterion: Dict[str, Any]
    acceptance_bar: Dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hypo_id": self.hypo_id,
            "domain": self.domain,
            "statement": self.statement,
            "status": self.status,
            "kill_criterion": self.kill_criterion,
            "acceptance_bar": self.acceptance_bar,
            "created_at": self.created_at,
            "notes": self.notes,
        }


@dataclass
class Trial:
    project: str
    config_hash: str
    description: str
    count: int = 1
    trial_id: Optional[int] = None
    logged_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ProjectState:
    project_id: str
    name: str
    status: str  # ACTIVE, PAUSED, COMPLETED, ARCHIVED
    variables: Dict[str, Any] = field(default_factory=dict)
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
