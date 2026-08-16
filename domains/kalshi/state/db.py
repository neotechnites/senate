"""SQLite database management for Kalshi Domain Pod."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "kalshi_domain.db"

SCHEMA_SQL = """
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA busy_timeout = 5000;

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

CREATE TABLE IF NOT EXISTS active_orders (
    order_id TEXT PRIMARY KEY,
    ticker TEXT NOT NULL,
    side TEXT NOT NULL,
    price REAL NOT NULL,
    count INTEGER NOT NULL,
    collateral_usd REAL NOT NULL,
    status TEXT NOT NULL,
    lane TEXT NOT NULL,
    placed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_orders_ticker ON active_orders(ticker);
CREATE INDEX IF NOT EXISTS idx_orders_status ON active_orders(status);


CREATE TABLE IF NOT EXISTS seat_accruals (
    id TEXT PRIMARY KEY,
    ticker TEXT NOT NULL,
    seat_hours REAL NOT NULL,
    escrow_usd REAL NOT NULL,
    realized_credit_usd REAL NOT NULL,
    hourly_rate_usd REAL NOT NULL,
    effective_daily_per_100_usd REAL NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

    def _init_db(self) -> None:
        with self.get_connection() as conn:
            conn.executescript(SCHEMA_SQL)
            conn.commit()

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(
            str(self.db_path),
            timeout=10.0,
        )
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

