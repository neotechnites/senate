"""State models for Automotive Chassis Engineering Domain Pod."""
from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class DomainFact:
    key: str
    value: Dict[str, Any]
    source: str
    is_immutable: bool = False
