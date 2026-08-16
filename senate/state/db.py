"""SQLite database connection and schema management for The Senate."""

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "senate.db"

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
"""


class Database:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
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

