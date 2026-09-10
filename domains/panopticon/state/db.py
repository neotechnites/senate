"""SQLite state for the Panopticon Domain Pod — the pod's single source of truth.

WHY THE SCHEMA LOOKS LIKE THIS.  Panopticon is not Kalshi.  Kalshi's oracle is a venue
that answers in dollars; a game has no such oracle, and the failure mode of a dated
creative project is not losing money, it is arriving at 2027-04-01 with a pile of
artifacts and nothing playable.  So the tables here exist to make that specific failure
visible early:

  facts          -- canon Ryan ruled on. Nothing else steers.
  decisions      -- every design call with its date and rationale, so February-Ryan
                    knows why January-Ryan cut something and does not re-litigate it.
  scope_ledger   -- the ratchet. Scope may only SHRINK as the date approaches
                    (verify/scope.py). A feature added late must displace one.
  builds         -- a tagged build that LAUNCHED. "Done" is a build, never a document.
  playtests      -- bot and human sessions. With no friends to test, headless bot
                    matches are the balance oracle; human sessions judge feel.
  milestones     -- dated gates, including the Steam ones, planned backward from ship.
  content        -- devlogs/posts and the wishlist count they are meant to move.
  tasks          -- the work queue, split by WHERE it can happen. A REMOTE task the
                    head can start right now; a PC_REQUIRED task spends one of Ryan's
                    ~233 remaining PC hours and may only become READY once every
                    remote prerequisite is finished (verify/queue.py).
"""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

POD_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = Path(os.environ.get("PANOPTICON_DB_PATH")
                       or POD_DIR / "data" / "panopticon.db")

SCHEMA_SQL = """
PRAGMA journal_mode = WAL;

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

CREATE TABLE IF NOT EXISTS decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decided_on TEXT NOT NULL,
    topic TEXT NOT NULL,
    ruling TEXT NOT NULL,
    rationale TEXT NOT NULL,
    evidence TEXT DEFAULT '',          -- playtest id, build tag, or 'judgement'
    decided_by TEXT NOT NULL DEFAULT 'ryan',
    superseded_by INTEGER,
    -- A STANDING ORDER: rendered in every boot prompt, forever, never rotated out by a
    -- newer ruling.  Ryan had to repeat several of these because the prompt only ever
    -- showed the 8 newest decisions and everything older fell off the edge.
    pinned INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS scope_ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feature TEXT NOT NULL UNIQUE,
    tier TEXT CHECK(tier IN ('SHIP_BLOCKING','WANTED','STRETCH')) NOT NULL,
    status TEXT CHECK(status IN ('PLANNED','IN_PROGRESS','DONE','CUT')) DEFAULT 'PLANNED',
    added_on TEXT NOT NULL,
    cut_on TEXT DEFAULT '',
    displaced TEXT DEFAULT '',         -- what a late addition pushed out
    notes TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS builds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag TEXT NOT NULL UNIQUE,
    built_on TEXT NOT NULL,
    commit_sha TEXT NOT NULL,
    platform TEXT NOT NULL,
    launched INTEGER DEFAULT 0,        -- did it actually start?
    headless_match_passed INTEGER DEFAULT 0,
    notes TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS playtests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    played_on TEXT NOT NULL,
    kind TEXT CHECK(kind IN ('BOT','HUMAN','MIXED')) NOT NULL,
    build_tag TEXT NOT NULL,
    guards INTEGER NOT NULL,
    prisoners INTEGER NOT NULL,
    matches INTEGER DEFAULT 1,
    guard_wins INTEGER DEFAULT 0,
    prisoner_wins INTEGER DEFAULT 0,
    seconds_median REAL DEFAULT 0.0,
    verdict TEXT DEFAULT '',           -- what it settled; '' = nothing settled
    footage_path TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS milestones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    due_on TEXT NOT NULL,
    kind TEXT CHECK(kind IN ('BUILD','STEAM','CONTENT','DECISION')) NOT NULL,
    hard INTEGER DEFAULT 0,            -- 1 = an external clock owns this date
    status TEXT CHECK(status IN ('OPEN','DONE','MISSED')) DEFAULT 'OPEN',
    evidence TEXT DEFAULT '',
    notes TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL UNIQUE,
    detail TEXT DEFAULT '',
    -- WHERE the work can physically happen. This is the whole point of the table:
    -- PC_REQUIRED spends Ryan's scarcest resource, REMOTE does not.
    lane TEXT CHECK(lane IN ('REMOTE','PC_REQUIRED','RYAN_DECISION','EXTERNAL')) NOT NULL,
    owner TEXT CHECK(owner IN ('HEAD','RYAN')) NOT NULL,
    status TEXT CHECK(status IN ('BACKLOG','READY','IN_PROGRESS','BLOCKED','DONE','CUT'))
        DEFAULT 'BACKLOG',
    feature TEXT DEFAULT '',           -- scope_ledger.feature this serves
    milestone TEXT DEFAULT '',         -- milestones.name this serves
    estimate_hours REAL DEFAULT 1.0,
    blocked_by TEXT DEFAULT '',        -- comma-separated task titles
    created_on TEXT NOT NULL,
    started_on TEXT DEFAULT '',
    done_on TEXT DEFAULT '',
    evidence TEXT DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status, lane);

CREATE TABLE IF NOT EXISTS content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    published_on TEXT NOT NULL,
    channel TEXT NOT NULL,             -- youtube | twitter | tiktok | instagram
    title TEXT NOT NULL,
    url TEXT DEFAULT '',
    source_playtest INTEGER,           -- footage came from this session
    wishlists_after INTEGER            -- measured, not estimated
);
"""


# Columns added after the pod already had a live DB.  CREATE TABLE IF NOT EXISTS cannot
# add them, and this pod's DB is real state that must not be rebuilt to gain a column.
_ADDED_COLUMNS = (("decisions", "pinned", "INTEGER DEFAULT 0"),)


def _migrate(conn) -> None:
    for table, col, decl in _ADDED_COLUMNS:
        have = {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}
        if col not in have:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {decl}")


class Database:
    """Pod-local SQLite handle.  readonly=True opens sqlite mode=ro and skips the
    schema script entirely, so a hook that only reads can never migrate the pod."""

    def __init__(self, db_path: Optional[Path] = None, readonly: bool = False):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.readonly = bool(readonly)
        if not self.readonly:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with self.get_connection() as conn:
                conn.executescript(SCHEMA_SQL)
                _migrate(conn)
                conn.commit()

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        if self.readonly:
            conn = sqlite3.connect(f"file:{self.db_path.as_posix()}?mode=ro",
                                   timeout=30.0, uri=True)
        else:
            conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
