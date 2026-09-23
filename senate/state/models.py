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


@dataclass
class Goal:
    goal_id: str
    title: str
    category: str
    target_metric: str
    target_value: float
    current_value: float = 0.0
    unit: str = ""
    ryan_hours_saved: float = 0.0
    status: str = "ACTIVE"  # ACTIVE, PAUSED, ACHIEVED, ABANDONED
    associated_domains: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "title": self.title,
            "category": self.category,
            "target_metric": self.target_metric,
            "current_value": self.current_value,
            "target_value": self.target_value,
            "unit": self.unit,
            "ryan_hours_saved": self.ryan_hours_saved,
            "status": self.status,
            "associated_domains": self.associated_domains,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_row(cls, row: tuple) -> "Goal":
        domains = row[9]
        if isinstance(domains, str):
            try:
                domains = json.loads(domains)
            except Exception:
                domains = [domains]
        return cls(
            goal_id=row[0],
            title=row[1],
            category=row[2],
            target_metric=row[3],
            current_value=float(row[4] or 0.0),
            target_value=float(row[5] or 0.0),
            unit=str(row[6] or ""),
            ryan_hours_saved=float(row[7] or 0.0),
            status=str(row[8] or "ACTIVE"),
            associated_domains=list(domains or []),
            created_at=str(row[10]),
            updated_at=str(row[11]),
        )
