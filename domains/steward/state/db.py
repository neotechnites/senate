"""SQLite state for the Steward Domain Pod — the pod's single source of truth.

WHY THE SCHEMA LOOKS LIKE THIS.  Steward is not Kalshi and not Panopticon.  Kalshi's
oracle is a venue that answers in dollars.  Panopticon's oracle is a build that ran.
Steward's oracle is RYAN — he is the only thing on earth that knows whether the
baseboards are in.  He ruled on 2026-09-09: "only i need to tell it when ive done
somehting. im not going to lie to it."  So there is no receipt-hunting apparatus here;
there is a `completions` table that records HIS word, with the date he said it and the
words he used.  A completion nobody reported does not exist.

The failure mode this schema exists to make visible is not losing money and not missing
a ship date.  It is: a large backlog quietly rotting while a bot cheerfully reports
green.  So:

  facts         -- canon Ryan ruled on.  `authorized` holds his verbatim words.
                   Nothing without a Ryan quote steers this pod.
  obligations   -- the backlog.  ONESHOT (baseboards), RECURRING (drain the water
                   heater), EVENT (a dated thing he must attend).  RECURRING never
                   closes; it re-arms.  See verify/recurrence.py.
  completions   -- the ONLY way an obligation advances.  Ryan's word, dated, verbatim.
  conversation  -- every line in both directions.  This pod's interface is a
                   conversation, not a reminder feed (Ryan, 2026-09-09: "if i wanted
                   daily reminders i would use daily reminders").  The manager cannot
                   judge whether to speak without knowing what it already said.
  wake_log      -- every heartbeat, INCLUDING the ones where it chose silence.
                   Silence is a decision with a rationale, not an absence.  A manager
                   that speaks on every wake is an alarm clock.
  vendors       -- the plumber, the mechanic.  Some obligations are closed by hiring,
                   and the manager is expected to do that legwork itself.

INTERVAL PROVENANCE.  `obligations.interval_source` holds a citation URL, never drafted
prose.  Research 2026-09-09 found no machine-readable dataset of home or vehicle
maintenance intervals anywhere; every number here is transcribed from a named authority
(EPA WaterSense, an owner's manual) or is Ryan's own judgement.  An interval with an
empty `interval_source` is SELF-MARKED and must be reported that way.
"""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

POD_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = Path(os.environ.get("STEWARD_DB_PATH")
                       or POD_DIR / "data" / "steward.db")

SCHEMA_SQL = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS facts (
    key TEXT PRIMARY KEY,
    value JSON NOT NULL,
    source TEXT NOT NULL,
    authorized TEXT DEFAULT '',        -- Ryan's verbatim words when they exist
    ratified_on TEXT DEFAULT '',
    verified_by TEXT NOT NULL,
    is_immutable INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS obligations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    detail TEXT DEFAULT '',
    kind TEXT CHECK(kind IN ('ONESHOT','RECURRING','EVENT')) NOT NULL,
    domain TEXT NOT NULL DEFAULT 'HOUSE',   -- HOUSE | VEHICLE | ADMIN | HEALTH | EVENT
    asset TEXT DEFAULT '',                  -- 'living room', 'water heater', the truck
    interval_days INTEGER,                  -- RECURRING only
    interval_source TEXT DEFAULT '',        -- citation URL; empty => SELF-MARKED
    anchor_date TEXT DEFAULT '',            -- EVENT date, or first-due for RECURRING
    last_completed_at TEXT DEFAULT '',
    next_due_at TEXT DEFAULT '',            -- computed; verify/recurrence.py
    status TEXT CHECK(status IN ('OPEN','CLOSED','DROPPED')) DEFAULT 'OPEN',
    effort_hours REAL DEFAULT 0.0,          -- MODELLED estimate, never measured
    season TEXT DEFAULT '',                 -- e.g. 'SPRING,FALL' when weather-bound
    blocked_on TEXT DEFAULT '',             -- a part, a quote, a person, a decision
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    obligation_id INTEGER NOT NULL REFERENCES obligations(id) ON DELETE CASCADE,
    completed_on TEXT NOT NULL,
    reported_by TEXT NOT NULL DEFAULT 'ryan',   -- ONLY 'ryan' is a valid receipt
    verbatim TEXT DEFAULT '',                   -- what he actually said
    notes TEXT DEFAULT '',
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS conversation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    direction TEXT CHECK(direction IN ('TO_RYAN','FROM_RYAN')) NOT NULL,
    channel TEXT NOT NULL DEFAULT 'telegram',
    text TEXT NOT NULL,
    wake_id INTEGER REFERENCES wake_log(id),
    obligation_id INTEGER REFERENCES obligations(id)
);

CREATE TABLE IF NOT EXISTS wake_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    woke_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    spoke INTEGER DEFAULT 0,               -- 0 is a normal, healthy outcome
    rationale TEXT NOT NULL,               -- why it spoke, or why it held its tongue
    considered INTEGER DEFAULT 0,          -- how many obligations it weighed
    chose TEXT DEFAULT ''                  -- which obligation, if any
);

CREATE TABLE IF NOT EXISTS vendors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    trade TEXT NOT NULL,
    phone TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    last_used_on TEXT DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_oblig_due ON obligations(status, next_due_at);
CREATE INDEX IF NOT EXISTS idx_conv_at ON conversation(at DESC);
CREATE INDEX IF NOT EXISTS idx_wake_at ON wake_log(woke_at DESC);
"""


class Database:
    """Isolated pod database.  The Senate hub never SQLs this file; it shells
    `steward.py telemetry --json`."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _init_schema(self) -> None:
        with self.get_connection() as conn:
            conn.executescript(SCHEMA_SQL)

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
