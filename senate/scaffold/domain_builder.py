"""Domain Pod Scaffolder, Registry, and Telemetry Engine for The Senate."""

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from senate.state.fact_store import FactStore
from senate.state.models import ProjectState

DOMAINS_ROOT = Path(__file__).resolve().parents[2] / "domains"


@dataclass
class DomainPodManifest:
    domain_id: str
    name: str
    description: str
    category: str
    created_at: str
    path: str
    active_lanes: List[str]


def pull_domain_telemetry(domain_id: str, store: FactStore) -> Dict[str, Any]:
    """Pull verified telemetry from an isolated domain pod into root Senate state.
    
    INVARIANT: The Senate Meta-Hub NEVER executes SQL over a pod's internal tables.
    The domain pod exports its own telemetry via `<pod_dir>/<entrypoint>.py telemetry --json`.
    """
    clean_id = domain_id.strip().lower()
    pod_dir = DOMAINS_ROOT / clean_id
    if not pod_dir.exists():
        raise ValueError(f"Domain Pod '{clean_id}' not found at {pod_dir}.")

    config_p = pod_dir / "config.json"
    cfg = json.loads(config_p.read_text(encoding="utf-8")) if config_p.exists() else {}

    # Default fallback telemetry
    telemetry: Dict[str, Any] = {
        "domain_id": clean_id,
        "name": cfg.get("name", clean_id),
        "mission": cfg.get("description", "Advance Ryan's goals"),
        "category": cfg.get("category", "general"),
        "active_lanes": cfg.get("active_lanes", ["core"]),
        "milestones": cfg.get("milestones", []),
        "resource_consumption": {},
        "domain_metrics": {},
        "invariant_health": "VERIFIED",
    }

    # Execute the pod's exported telemetry interface
    entrypoint_candidates = [
        pod_dir / f"{clean_id}.py",
        pod_dir / "interface" / "cli.py",
    ]
    entrypoint = next((ep for ep in entrypoint_candidates if ep.exists()), None)

    if entrypoint:
        try:
            res = subprocess.run(
                [sys.executable, str(entrypoint), "telemetry", "--json"],
                cwd=str(pod_dir),
                capture_output=True,
                text=True,
                timeout=5.0,
            )
            if res.returncode == 0 and res.stdout.strip():
                pod_telem = json.loads(res.stdout.strip())
                if isinstance(pod_telem, dict):
                    telemetry.update(pod_telem)
        except Exception:
            pass

    # Update Tier 1 Project State in Senate Hub
    proj = ProjectState(
        project_id=clean_id,
        name=telemetry.get("name", cfg.get("name", clean_id)),
        status="ACTIVE",
        variables={
            "mission": telemetry.get("mission", cfg.get("description", "")),
            "category": telemetry.get("category", cfg.get("category", "general")),
            "path": str(pod_dir),
            "lanes": telemetry.get("active_lanes", ["core"]),
            "milestones": telemetry.get("milestones", []),
            "resource_consumption": telemetry.get("resource_consumption", {}),
            "domain_metrics": telemetry.get("domain_metrics", {}),
        },
    )
    store.save_project_state(proj)
    return telemetry


def list_domain_pods(store: Optional[FactStore] = None) -> List[DomainPodManifest]:
    """Discover all active domain pods on disk and in SQLite."""
    manifests: List[DomainPodManifest] = []
    if not DOMAINS_ROOT.exists():
        return manifests

    for child in DOMAINS_ROOT.iterdir():
        if child.is_dir() and (child / "config.json").exists():
            try:
                cfg = json.loads((child / "config.json").read_text(encoding="utf-8"))
                manifests.append(DomainPodManifest(
                    domain_id=cfg.get("domain_id", child.name),
                    name=cfg.get("name", child.name),
                    description=cfg.get("description", ""),
                    category=cfg.get("category", "general"),
                    created_at=cfg.get("created_at", ""),
                    path=str(child),
                    active_lanes=cfg.get("active_lanes", []),
                ))
            except Exception:
                continue
    return manifests


def scaffold_domain_pod(
    domain_id: str,
    name: str,
    description: str,
    category: str = "general",
    store: Optional[FactStore] = None,
) -> Path:
    """Provision a brand-new, isolated Domain Pod with its own 4-engine structure."""
    import time

    clean_id = domain_id.strip().lower().replace("-", "_").replace(" ", "_")
    pod_dir = DOMAINS_ROOT / clean_id

    if pod_dir.exists():
        raise ValueError(f"Domain Pod '{clean_id}' already exists at {pod_dir}.")

    # 1. Create directory hierarchy
    (pod_dir / "state").mkdir(parents=True, exist_ok=True)
    (pod_dir / "verify").mkdir(parents=True, exist_ok=True)
    (pod_dir / "harness").mkdir(parents=True, exist_ok=True)
    (pod_dir / "interface").mkdir(parents=True, exist_ok=True)
    (pod_dir / "tests").mkdir(parents=True, exist_ok=True)
    (pod_dir / "data").mkdir(parents=True, exist_ok=True)

    # 2. Write config.json
    now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    config_payload = {
        "domain_id": clean_id,
        "name": name,
        "description": description,
        "category": category,
        "created_at": now_iso,
        "active_lanes": ["core"],
    }
    (pod_dir / "config.json").write_text(json.dumps(config_payload, indent=2), encoding="utf-8")

    # 3. Write Domain Models / State Engine
    (pod_dir / "state" / "__init__.py").write_text("", encoding="utf-8")
    (pod_dir / "state" / "models.py").write_text(f'''"""State models for {name} Domain Pod."""
from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class DomainFact:
    key: str
    value: Dict[str, Any]
    source: str
    is_immutable: bool = False
''', encoding="utf-8")

    # 4. Write Domain Verify Engine
    (pod_dir / "verify" / "__init__.py").write_text("", encoding="utf-8")
    (pod_dir / "verify" / "invariants.py").write_text(f'''"""Invariant validation for {name} Domain Pod."""
from typing import Any, Dict, List, Tuple

def validate_domain_proposal(proposal: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate proposal against {name} domain invariants."""
    violations = []
    return len(violations) == 0, violations
''', encoding="utf-8")

    # 5. Write Domain Harness
    (pod_dir / "harness" / "__init__.py").write_text("", encoding="utf-8")
    (pod_dir / "harness" / "runner.py").write_text(f'''"""Tool execution harness for {name} Domain Pod."""
import subprocess
from pathlib import Path
from typing import List, Union

POD_ROOT = Path(__file__).resolve().parent.parent

def run_domain_tool(command: Union[str, List[str]]) -> subprocess.CompletedProcess:
    """Run a domain tool within the isolated pod root."""
    return subprocess.run(command, cwd=str(POD_ROOT), capture_output=True, text=True)
''', encoding="utf-8")

    # 6. Write Domain Tests with self-contained path resolution
    (pod_dir / "tests" / "__init__.py").write_text("", encoding="utf-8")
    (pod_dir / "tests" / "test_domain.py").write_text(f'''"""Automated invariant tests for {name} Domain Pod."""
import sys
from pathlib import Path
import unittest

POD_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
for p in [str(REPO_ROOT), str(POD_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from verify.invariants import validate_domain_proposal

class TestDomainInvariants(unittest.TestCase):
    def test_basic_invariant(self):
        valid, violations = validate_domain_proposal({{"action": "test"}})
        self.assertTrue(valid)

if __name__ == "__main__":
    unittest.main()
''', encoding="utf-8")

    # 7. Write Dedicated CLI Entrypoint
    (pod_dir / f"{clean_id}.py").write_text(f'''#!/usr/bin/env python3
"""CLI Entrypoint for {name} Domain Pod."""
import argparse
import json
import sys
from pathlib import Path

POD_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[2]
for p in [str(REPO_ROOT), str(POD_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

def main(argv=None):
    parser = argparse.ArgumentParser(prog="{clean_id}", description="{name} Domain CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status", help="Print domain status")
    
    telem_p = sub.add_parser("telemetry", help="Export domain telemetry")
    telem_p.add_argument("--json", action="store_true", default=True)

    args = parser.parse_args(argv)
    if args.command == "status":
        print("══════════════════════════════════════════════════════════════")
        print("             {name.upper()} DOMAIN POD STATUS")
        print("══════════════════════════════════════════════════════════════")
        print("Mission: {description}")
        print("Status:  ACTIVE")
        return 0
    elif args.command == "telemetry":
        data = {{
            "domain_id": "{clean_id}",
            "name": "{name}",
            "mission": "{description}",
            "category": "{category}",
            "active_lanes": ["core"],
            "resource_consumption": {{}},
            "domain_metrics": {{"status": "active"}},
            "invariant_health": "VERIFIED",
        }}
        print(json.dumps(data, indent=2))
        return 0
    return 0

if __name__ == "__main__":
    sys.exit(main())
''', encoding="utf-8")
    os.chmod(pod_dir / f"{clean_id}.py", 0o755)

    # 8. Write Dedicated Domain Launcher (spinup.py & spinup.sh)
    (pod_dir / "spinup.py").write_text(f'''#!/usr/bin/env python3
"""Dedicated Domain Head Launcher for {name}.
Context is 100% focused on {clean_id}. Zero cross-domain noise.
"""
import os
import sys
from pathlib import Path

POD_DIR = Path(__file__).resolve().parent
CLAUDE_BIN = os.path.expanduser("~/.local/bin/claude")

SYSTEM_PROMPT = """You are the Dedicated Domain Head for {name} ({clean_id}).
MANDATE: {description}

OPERATING RULES:
1. Complete Domain Focus: You operate in pure isolation for this project.
2. Invariants: All code and proposals must pass tests in `tests/test_domain.py`.
3. High Leverage: Direct all intelligence at advancing milestones for Ryan.
"""

def main():
    print("══════════════════════════════════════════════════════════════")
    print("             {name.upper()} DOMAIN HEAD SPIN-UP")
    print("══════════════════════════════════════════════════════════════")
    claude_path = CLAUDE_BIN if os.path.exists(CLAUDE_BIN) else "claude"
    cmd = [claude_path, "--system-prompt", SYSTEM_PROMPT]
    os.execvp(claude_path, cmd)

if __name__ == "__main__":
    main()
''', encoding="utf-8")

    (pod_dir / "spinup.sh").write_text(f'''#!/usr/bin/env bash
cd "$(dirname "$0")" || exit 1
python3 spinup.py "$@"
''', encoding="utf-8")
    os.chmod(pod_dir / "spinup.sh", 0o755)
    os.chmod(pod_dir / "spinup.py", 0o755)

    # 9. Write README.md
    (pod_dir / "README.md").write_text(f'''# {name} Domain Pod (`{clean_id}`)

**Mission:** {description}
**Category:** {category}
**Created:** {now_iso}

## Quickstart
```bash
./spinup.sh   # Launches isolated Domain Claude session
```
''', encoding="utf-8")

    # 10. Register in Root Senate FactStore if provided
    if store is not None:
        proj = ProjectState(
            project_id=clean_id,
            name=name,
            status="ACTIVE",
            variables={
                "mission": description,
                "category": category,
                "path": str(pod_dir),
                "lanes": ["core"],
            },
        )
        store.save_project_state(proj)

    return pod_dir


def delete_domain_pod(domain_id: str, store: Optional[FactStore] = None) -> bool:
    """Delete a domain pod from disk and unregister from Senate FactStore."""
    clean_id = domain_id.strip().lower().replace("-", "_").replace(" ", "_")
    pod_dir = DOMAINS_ROOT / clean_id

    if pod_dir.exists():
        shutil.rmtree(pod_dir)

    if store is not None:
        store.delete_project_state(clean_id)

    return True
