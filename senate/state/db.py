"""SQLite database connection and schema management for The Senate."""

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

# SENATE_DB_PATH lets a test session (or any subprocess it spawns) redirect sovereign
# state to a temp file.  Receipt, 2026-09-09: senate/tests/test_cli_smoke.py builds and
# deletes real domain pods through FactStore() while spinup.py runs the whole suite at
# boot -- so BOOTING the head wrote to data/senate.db.  The Kalshi pod hit the same thing
# and had to move its boot check to pytest, because `unittest discover` skips conftest.
DEFAULT_DB_PATH = Path(os.environ.get("SENATE_DB_PATH")
                       or Path(__file__).resolve().parents[2] / "data" / "senate.db")

SCHEMA_SQL = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS facts (
    key TEXT PRIMARY KEY,
    domain TEXT NOT NULL,
    value JSON NOT NULL,
    source_artifact TEXT NOT NULL,
    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified_by TEXT NOT NULL,
    is_immutable INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_facts_domain ON facts(domain);

CREATE TABLE IF NOT EXISTS fact_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL,
    old_value JSON NOT NULL,
    new_value JSON NOT NULL,
    changed_by TEXT NOT NULL,
    source_artifact TEXT NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fact_history_key ON fact_history(key);

CREATE TABLE IF NOT EXISTS hypotheses (
    hypo_id TEXT PRIMARY KEY,
    domain TEXT NOT NULL,
    statement TEXT NOT NULL,
    status TEXT CHECK(status IN ('UNTESTED', 'TESTING', 'CONFIRMED', 'KILLED')) DEFAULT 'UNTESTED',
    kill_criterion JSON NOT NULL,
    acceptance_bar JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_hypo_status ON hypotheses(status);

CREATE TABLE IF NOT EXISTS trials_ledger (
    trial_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project TEXT NOT NULL,
    config_hash TEXT NOT NULL,
    description TEXT NOT NULL,
    count INTEGER DEFAULT 1,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_trials_project ON trials_ledger(project);

CREATE TABLE IF NOT EXISTS project_state (
    project_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    variables JSON NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS ideation_registry (
    idea_id TEXT PRIMARY KEY,
    domain TEXT NOT NULL,
    hypothesis TEXT NOT NULL,
    proposed_by_model TEXT NOT NULL,
    audited_by_adversary TEXT NOT NULL,
    adversary_status TEXT CHECK(adversary_status IN ('PROPOSED', 'ATTACKED', 'SURVIVED', 'KILLED')) DEFAULT 'PROPOSED',
    kill_test_spec JSON NOT NULL,
    status TEXT CHECK(status IN ('GRAVEYARD', 'INCUBATING', 'VALIDATED')) DEFAULT 'INCUBATING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mistake_invariants (
    mistake_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    incident_description TEXT NOT NULL,
    enforced_by_module TEXT NOT NULL,
    verification_test TEXT NOT NULL,
    status TEXT CHECK(status IN ('COMPILED_IMPOSSIBLE', 'REGRESSION_TESTED')) DEFAULT 'COMPILED_IMPOSSIBLE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mistakes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    receipt TEXT NOT NULL,
    loss_usd REAL DEFAULT 0.0,
    prevention TEXT NOT NULL,
    invariant_status TEXT CHECK(invariant_status IN ('COMPILED_IMPOSSIBLE', 'REGRESSION_TESTED', 'UNENFORCED')) DEFAULT 'UNENFORCED',
    status TEXT CHECK(status IN ('OPEN', 'MITIGATED')) DEFAULT 'OPEN',
    ratified_on TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_mistakes_status ON mistakes(status);

CREATE TABLE IF NOT EXISTS goals (
    goal_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    target_metric TEXT NOT NULL,
    current_value REAL DEFAULT 0.0,
    target_value REAL NOT NULL,
    unit TEXT DEFAULT '',
    ryan_hours_saved REAL DEFAULT 0.0,
    status TEXT CHECK(status IN ('ACTIVE', 'PAUSED', 'ACHIEVED', 'ABANDONED')) DEFAULT 'ACTIVE',
    associated_domains JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


class Database:
    """SQLite handle for the sovereign Senate state.

    M-RO (2026-09-09, ported from the Kalshi pod): `readonly=True` opens the file
    with sqlite `mode=ro` and SKIPS the schema script entirely.  A reader -- the
    UserPromptSubmit state-surface hook runs on every single turn -- must never be
    able to run a migration against the sovereign DB as a side effect of being
    asked what is true.
    """

    def __init__(self, db_path: Optional[Path] = None, readonly: bool = False):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.readonly = bool(readonly)
        if not self.readonly:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_db()

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        if self.readonly:
            uri = f"file:{self.db_path.as_posix()}?mode=ro"
            conn = sqlite3.connect(uri, timeout=30.0, uri=True)
        else:
            conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self.get_connection() as conn:
            conn.executescript(SCHEMA_SQL)
            conn.commit()

