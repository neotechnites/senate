"""Per-test pod DB. Booting the head runs this suite, so a test must never touch
domains/panopticon/data/panopticon.db — the Senate ledger already carries the receipt
for a boot gate that mutated sovereign state (test_suite_mutated_the_sovereign_db)."""
import os
import sys
import tempfile
from pathlib import Path

import pytest

# The pod suite is run from the pod directory (spinup.py's boot gate does exactly that),
# so the repo root is not on sys.path and `domains.panopticon...` will not import.
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

_TMP = Path(tempfile.mkdtemp(prefix="panopticon-tests-"))
os.environ["PANOPTICON_DB_PATH"] = str(_TMP / "session.db")
_n = {"i": 0}


@pytest.fixture(autouse=True)
def pod_db(monkeypatch):
    import domains.panopticon.state.db as db
    _n["i"] += 1
    path = _TMP / f"t{_n['i']:04d}.db"
    monkeypatch.setattr(db, "DEFAULT_DB_PATH", path, raising=True)
    monkeypatch.setenv("PANOPTICON_DB_PATH", str(path))
    yield db.Database(path)
