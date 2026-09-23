"""SQLite database management for Kalshi Domain Pod."""

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

# The live pod DB.  KALSHI_DOMAIN_DB_PATH is a TEST HOOK ONLY (2026-09-05):
# the test suite's conftest points every bare Database() — and every
# `kalshi.py` subprocess a test spawns — at a per-session temp file, because
# Database.__init__ runs the schema migrations on every open and a bare
# FactStore() in a test used to open, migrate and even seed the laptop's live
# data/kalshi_domain.db (it applied the per-market-cap migration from inside
# pytest on 2026-09-05).  Production never sets this variable.
DEFAULT_DB_PATH = Path(os.environ.get("KALSHI_DOMAIN_DB_PATH")
                       or Path(__file__).resolve().parents[1] / "data" / "kalshi_domain.db")

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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    venue_miss_count INTEGER NOT NULL DEFAULT 0
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

CREATE TABLE IF NOT EXISTS placement_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- ARMED: new deployments allowed.  DISARMED: NEW DEPLOYMENTS FROZEN, but
    -- seats we already hold keep their full shield (reactive cancel, atomic
    -- re-arm, hourly timer).  HALTED: global freeze, nothing places at all —
    -- for a SYSTEM-level fault only.  See FactStore.PLACEMENT_STATES.
    state TEXT NOT NULL CHECK(state IN ('ARMED', 'DISARMED', 'HALTED')),
    reason TEXT NOT NULL,
    set_by TEXT NOT NULL,
    set_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS deployment_plan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    side TEXT NOT NULL CHECK(side IN ('yes', 'no')),
    price_cents INTEGER NOT NULL CHECK(price_cents BETWEEN 1 AND 99),
    count INTEGER NOT NULL CHECK(count > 0),
    max_escrow_usd REAL NOT NULL,
    hard_exit_utc TEXT,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK(status IN ('pending', 'resting', 'filled', 'exited', 'cancelled',
                         'withdrawn_rearmed', 'stood_down')),
    order_id TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- DUTY-CYCLE LEDGER (queue-shield withdraw-and-rearm, 2026-08-17).
    -- 'withdrawn_rearmed' is the re-placeable exit: a seat the shield pulled on
    -- CANCEL-driven queue erosion, which the placement engine may re-place once
    -- protection rebuilds.  'exited'/'cancelled'/'filled' remain TERMINAL.
    --
    -- 'stood_down' (2026-08-17, stand-down lane) is the THIRD kind of exit and
    -- the whole point of that lane: the shield pulled us because the level was
    -- being CONSUMED by real aggressors rather than merely requoted, so
    -- re-placing would feed us straight back in with fresh armour.  It is NOT
    -- terminal (the seat is not dead forever) but it is NOT re-placeable
    -- either: the engine never selects it, and only an explicit
    -- re-qualification decision can return it to service.
    withdraw_reason TEXT,
    withdrawn_at TEXT,
    withdraw_shield_frac REAL,
    a0_baseline REAL,           -- reference rival depth ahead of us (first placement)
    a0_current REAL,            -- RE-BASELINED at the most recent placement instant
    last_placed_at TEXT,
    uptime_s REAL NOT NULL DEFAULT 0,
    downtime_s REAL NOT NULL DEFAULT 0,
    replace_count INTEGER NOT NULL DEFAULT 0,
    replaces_utc_date TEXT,
    replaces_today INTEGER NOT NULL DEFAULT 0,
    -- WHY the shield left, in contracts, so a stand-down is auditable after the
    -- fact instead of being a bare status change.  Cancel-driven erosion is
    -- rivals requoting (benign, re-place); trade-driven erosion is real
    -- aggressors consuming the level (~9x more toxic per event); unclassified
    -- is erosion seen while the trade feed was unhealthy, which FAILS CLOSED
    -- and is counted as trade-driven for the stand-down test.
    erosion_trade_ct REAL,
    erosion_cancel_ct REAL,
    erosion_unclassified_ct REAL,
    stood_down_at TEXT,
    -- PRICING RULE (price-at-the-placement-instant, 2026-08-18).
    --
    -- price_cents above is a SEED-TIME snapshot of a book.  A row does not place
    -- when it is seeded: it waits on the 300s cadence, on the 60-minute post-fill
    -- re-entry ban, on the daily cap, on DISARMED.  Ryan: "why are we choosing
    -- where it sits now, instead of when we can actually place it? ... how do you
    -- know where touch will be in 25 minutes?"
    --
    --   price_mode 'fixed'  (DEFAULT, and every row that existed before this
    --                        migration): price_cents/count are used verbatim.
    --                        Behaviour is bit-for-bit what it always was.
    --   price_mode 'derive': the LEVEL and the COUNT are computed at the
    --                        placement instant from the same fresh orderbook the
    --                        preflight already fetched (harness/price_derivation.py),
    --                        subject to the constraints below.  A derived row
    --                        NEVER falls back to the stale seed price: if no
    --                        level qualifies it places nothing and logs why.
    --                        price_cents/count are then overwritten with what was
    --                        actually placed, so the queue shield, the duty-cycle
    --                        ledger and the atomic replace all see the true seat.
    price_mode TEXT NOT NULL DEFAULT 'fixed' CHECK(price_mode IN ('fixed', 'derive')),
    max_capital_usd REAL,       -- budget the derived size is computed from
    band_lo_c INTEGER,          -- inclusive price band; NULL = the ENTRY floor,
                                -- price_derivation.ENTRY_BAND_LO_C (BAND-21: 21c)
    band_hi_c INTEGER,          -- inclusive price band; NULL = DEFAULT_BAND_HI_C 85
    min_armor_ct REAL,          -- rival depth required AT the chosen level
    max_seat_share REAL,        -- our_ct / (our_ct + rival_ct) ceiling
    -- VR-2 (2026-09-05): consecutive defensive cycles in which a resting
    -- row's order was ABSENT from the venue open-orders read.  The plan
    -- reconcile only writes terminal 'cancelled' at RECONCILE_MISS_STRIKES;
    -- a sighting resets it to 0.  One missing read used to be enough.
    venue_miss_count INTEGER NOT NULL DEFAULT 0,
    UNIQUE(ticker, side, price_cents, count)
);

CREATE INDEX IF NOT EXISTS idx_plan_status ON deployment_plan(status);

CREATE TABLE IF NOT EXISTS observed_fills (
    fill_id TEXT PRIMARY KEY,
    order_id TEXT,
    ticker TEXT,
    observed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- FLAT-3 (2026-09-05): A FILL LEFT NO POSITION RECORD.  Twenty-five
    -- lifetime fills, every one an informed sweep, and this table kept only
    -- the fill id / order id / ticker -- not how many contracts, at what
    -- price, on which side.  The only position number anywhere in the pod
    -- was the venue's aggregate `portfolio_value` mark, so a flatten could
    -- not even be SIZED from local state (KXSNOWCRABCATCH, 09-03, still
    -- open).  These are the venue fill's own numbers, nullable so an
    -- on-disk row predating the column reads as "unrecorded", never as 0.
    count_ct REAL,
    price_cents INTEGER,
    held_side TEXT,
    client_order_id TEXT
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

-- MT-4 (2026-09-09): THE MISTAKES LEDGER.  One row per paid-for lesson: what
-- happened (receipt), what it cost, and what now makes it physically
-- impossible (prevention = the module + test names).  mistake_invariants
-- above is the enforcement index; this is the narrative ledger the Domain
-- Head reads on boot (interface/head_prompt.py).  THIS IS THE LIVE VPS
-- SHAPE, COLUMN FOR COLUMN -- the table already exists on the VPS and the
-- mirror with exactly these columns; a differing shape here would make
-- every writer fail on the live DB ("no column named ...").  Never add a
-- column.  Rows are ratified idempotently (INSERT OR IGNORE on `name`)
-- from state/ratify_mistakes_*.py; nothing here is ever edited by hand.
CREATE TABLE IF NOT EXISTS mistakes (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    loss_usd REAL,
    status TEXT CHECK(status IN ('IMPOSSIBLE', 'MITIGATED', 'OPEN')),
    receipt TEXT,
    prevention TEXT,
    prevention_effort_h REAL,
    updated_at TEXT
);"""



class Database:
    def __init__(self, db_path: Optional[Path] = None, readonly: bool = False):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        # M4 (2026-09-09): a READER never opens the mirror as a writer.  The
        # per-turn hooks (harness/state_surface.py) opened the DB through
        # this constructor, which runs the schema script and every migration
        # on each prompt -- a write on the laptop mirror from a path that only
        # reads.  readonly=True opens sqlite's `file:<path>?mode=ro` URI,
        # skips schema creation and migration entirely, and any write
        # through it fails with sqlite3.OperationalError.  A missing file is
        # an error too (mode=ro never creates one).
        self.readonly = bool(readonly)
        if self.readonly:
            with self.get_connection() as conn:
                conn.execute("SELECT 1")
            return
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with self.get_connection() as conn:
            conn.executescript(SCHEMA_SQL)
            conn.commit()
        self._migrate()

    # --- migrations -----------------------------------------------------
    # CREATE TABLE IF NOT EXISTS cannot widen a CHECK constraint or add a
    # column to a database that already exists on disk (the live pod DB does).
    # These migrations are idempotent and run on every open.

    DEPLOYMENT_PLAN_ADDED_COLUMNS = (
        # ATTRIBUTION-1 (2026-09-16).  THE POD COULD NOT SAY WHICH SEAT EARNED WHAT.
        #
        # The venue's accrual feed (/v1/incentives/.../estimates) is keyed by
        # PROGRAM ID.  The seeder reads the live program index to qualify every
        # candidate -- program_id is in its hand at that instant -- and then threw
        # it away.  The only ticker<->program_id map was a live API read that
        # returns CURRENTLY-LIVE programs only, so the mapping for a program the
        # venue has since retired is gone forever.
        #
        # MEASURED 2026-09-16: /tmp/accrual_log.jsonl holds 407 distinct
        # program_ids; a live index read resolves 42.  365 of 407 -- 90% of every
        # dollar this pod has ever earned -- is permanently unattributable to a
        # ticker.  Fingerprint recovery (matching each program's gain total and
        # gain window against a ticker's latched total and resting window) was
        # tried and scored 11 of 20 correct against the live-mapped control: not
        # usable.
        #
        # WHAT IT COST.  Every per-seat economic question is unanswerable without
        # it.  The size-elasticity study on 2026-09-16 could not run its own
        # stated experiment -- within-ticker, within-tick, $25 vs $50 -- and fell
        # back to a cross-sectional regression whose size variation is generated
        # entirely by PRICE, biasing the coefficient by a known sign.  We do not
        # know what a seat earns.  We know what the book earns.
        #
        # Written once at placement, never rolled forward.  A row that re-places
        # into a NEW program overwrites it, because that is a different program
        # and the accrual belongs to the new id.
        ("program_id", "TEXT"),
        # FALSIFIABILITY-1 (2026-09-16).  THE GATE THAT KILLS MOST, PROVES LEAST.
        #
        # `worst_ratio` = the largest single print on this market divided by the
        # wall we would rest behind (seat_screen.py:1029).  The tape stage
        # refuses anything at or above MAX_WORST_RATIO = 0.80, and on the
        # 2026-09-16 board that one bar killed 36 of 46 tape rejects carrying
        # $27.68/day of modelled est_day -- the largest tape-stage killer.
        #
        # Its entire written receipt is "VOTEHUB was 1.24": n = 1, one market,
        # one day.  And the number was computed, used to refuse, and DISCARDED
        # -- not on deployment_plan, active_orders, observed_fills or
        # market_index.  So the threshold could never be tested against our own
        # fills, at 0.80 or at any other value, no matter how much tape accrued.
        # A gate that destroys supply and cannot be checked is not a risk
        # control; it is a belief with a number on it.
        #
        # Persisting it at seed time costs one column and makes the bar
        # falsifiable: fills per seat-day for seats placed at worst_ratio in
        # [0.0,0.2), [0.2,0.4) ... becomes a query the moment enough seats
        # carry it.  NULL on every historical row and on any row seeded from a
        # path that never measured the tape -- absence stays absence.
        ("worst_ratio", "REAL"),
        ("withdraw_reason", "TEXT"),
        ("withdrawn_at", "TEXT"),
        ("withdraw_shield_frac", "REAL"),
        ("a0_baseline", "REAL"),
        ("a0_current", "REAL"),
        ("last_placed_at", "TEXT"),
        ("uptime_s", "REAL NOT NULL DEFAULT 0"),
        ("downtime_s", "REAL NOT NULL DEFAULT 0"),
        ("replace_count", "INTEGER NOT NULL DEFAULT 0"),
        ("replaces_utc_date", "TEXT"),
        ("replaces_today", "INTEGER NOT NULL DEFAULT 0"),
        ("erosion_trade_ct", "REAL"),
        ("erosion_cancel_ct", "REAL"),
        ("erosion_unclassified_ct", "REAL"),
        ("stood_down_at", "TEXT"),
        # PRICING RULE (2026-08-18).  Added nullable / defaulted so an existing
        # on-disk row keeps its EXACT behaviour: price_mode defaults to 'fixed',
        # which is the pinned-price path unchanged.  ALTER TABLE ADD COLUMN
        # cannot carry the CHECK constraint the fresh schema has, so
        # FactStore.PLAN_PRICE_MODES enforces the domain in code on every write.
        ("price_mode", "TEXT NOT NULL DEFAULT 'fixed'"),
        ("max_capital_usd", "REAL"),
        ("band_lo_c", "INTEGER"),
        ("band_hi_c", "INTEGER"),
        ("min_armor_ct", "REAL"),
        ("max_seat_share", "REAL"),
        # VR-2 (2026-09-05): two-strike venue reconcile, see placement_engine.
        ("venue_miss_count", "INTEGER NOT NULL DEFAULT 0"),
        # FLAT-3 (2026-09-05): A 'filled' ROW WAS TERMINAL FOREVER AND WAS
        # COUNTED AS EXPOSURE AT THE ORDER SIZE.  The status CHECK has no
        # flattened/settled state, so verify/invariants summed every filled
        # row's max_escrow_usd for the ticker until the end of time: the
        # KXSNOWCRABCATCH position from 09-03 would block re-seating that
        # ticker even after it settled or was sold.  And a partial fill was
        # booked as the whole order.  Rather than widen the CHECK (a table
        # rebuild on the live DB), a filled row now carries what was ACTUALLY
        # filled and WHEN the position stopped existing.  flattened_at set =
        # the position is gone (sold or settled); the row stays 'filled' as
        # the receipt of the sweep and the post-fill family ban still stands.
        ("filled_ct", "REAL"),
        ("filled_cost_usd", "REAL"),
        ("flattened_at", "TEXT"),
        ("flatten_order_id", "TEXT"),
    )

    # FLAT-3 (2026-09-05): see the observed_fills DDL above.
    OBSERVED_FILLS_ADDED_COLUMNS = (
        ("count_ct", "REAL"),
        ("price_cents", "INTEGER"),
        ("held_side", "TEXT"),
        ("client_order_id", "TEXT"),
    )
    # VR-0 (2026-09-05): THE MIRROR FOLLOWS THE SAME TWO-STRIKE RULE AS THE
    # PLAN.  deployment_plan gained venue_miss_count under VR-2 so a single
    # missing open-orders read past the grace could not retire a seat; the
    # active_orders mirror kept retiring on ONE miss (RESTING ->
    # GONE_FROM_VENUE), which is how the exposure sums the caps rely on
    # stopped counting a live escrow while the plan row still said
    # 'resting'.  One ledger, one rule: the mirror now carries its own
    # strike count.  Added nullable-defaulted so an on-disk table keeps
    # every existing row unchanged.
    ACTIVE_ORDERS_ADDED_COLUMNS = (
        # ATTRIBUTION-1 (2026-09-16), mirror side.  See the deployment_plan
        # receipt above: the order mirror is what carries [placed_at, terminal)
        # intervals, so per-seat accrual rate = program gain over that interval.
        ("program_id", "TEXT"),
        ("venue_miss_count", "INTEGER NOT NULL DEFAULT 0"),
    )

    def _migrate(self) -> None:
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name='deployment_plan'"
            ).fetchone()
            ddl = (row["sql"] if row else "") or ""

            # 1. widen the status CHECK to admit the re-placeable withdrawal
            #    state and the non-re-placeable stand-down state.  The sentinel
            #    is the NEWEST status, so a DB migrated by an earlier build
            #    (which already knows 'withdrawn_rearmed') is still rebuilt.
            if "stood_down" not in ddl:
                cols = [r["name"] for r in conn.execute("PRAGMA table_info(deployment_plan)")]
                keep = [c for c in cols if c != "id"]
                conn.execute("PRAGMA foreign_keys=OFF")
                conn.execute("ALTER TABLE deployment_plan RENAME TO deployment_plan_legacy")
                start = SCHEMA_SQL.index("CREATE TABLE IF NOT EXISTS deployment_plan (")
                end = SCHEMA_SQL.index(");", start) + 2
                conn.execute(SCHEMA_SQL[start:end])
                collist = ", ".join(["id"] + keep)
                conn.execute(
                    f"INSERT INTO deployment_plan ({collist}) "
                    f"SELECT {collist} FROM deployment_plan_legacy"
                )
                conn.execute("DROP TABLE deployment_plan_legacy")
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_plan_status ON deployment_plan(status)"
                )
                conn.commit()

            # 1b. widen the placement_state CHECK to admit HALTED (2026-08-18).
            #     DISARMED was split: it now freezes NEW deployments only, and
            #     HALTED is the explicit global freeze.  An on-disk table
            #     predating this rejects the new value outright, so rebuild it —
            #     append-only ledger, so every historical row is carried over.
            row = conn.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name='placement_state'"
            ).fetchone()
            ps_ddl = (row["sql"] if row else "") or ""
            if ps_ddl and "HALTED" not in ps_ddl:
                conn.execute("PRAGMA foreign_keys=OFF")
                conn.execute("ALTER TABLE placement_state RENAME TO placement_state_legacy")
                start = SCHEMA_SQL.index("CREATE TABLE IF NOT EXISTS placement_state (")
                end = SCHEMA_SQL.index(");", start) + 2
                conn.execute(SCHEMA_SQL[start:end])
                conn.execute(
                    "INSERT INTO placement_state (id, state, reason, set_by, set_at) "
                    "SELECT id, state, reason, set_by, set_at FROM placement_state_legacy"
                )
                conn.execute("DROP TABLE placement_state_legacy")
                conn.commit()

            # 2. add any duty-cycle column the on-disk table is missing.
            have = {r["name"] for r in conn.execute("PRAGMA table_info(deployment_plan)")}
            for name, decl in self.DEPLOYMENT_PLAN_ADDED_COLUMNS:
                if name not in have:
                    conn.execute(f"ALTER TABLE deployment_plan ADD COLUMN {name} {decl}")
            # 2b. FLAT-3 (2026-09-05): the fill receipt gains count/price/side.
            have_f = {r["name"] for r in conn.execute("PRAGMA table_info(observed_fills)")}
            for name, decl in self.OBSERVED_FILLS_ADDED_COLUMNS:
                if name not in have_f:
                    conn.execute(f"ALTER TABLE observed_fills ADD COLUMN {name} {decl}")
            # 2c. VR-0 (2026-09-05): the mirror's own two-strike counter.
            have_o = {r["name"] for r in conn.execute("PRAGMA table_info(active_orders)")}
            for name, decl in self.ACTIVE_ORDERS_ADDED_COLUMNS:
                if name not in have_o:
                    conn.execute(f"ALTER TABLE active_orders ADD COLUMN {name} {decl}")
            conn.commit()

            # 3. PER-MARKET CAP FACT: tighten a loose immutable copy (2026-09-05).
            #    `kalshi.exposure.caps` was seeded at max_per_market_usd=50 and
            #    stamped is_immutable by a prior agent; FactStore.set_fact
            #    refuses immutables, so the live value could not be corrected
            #    through the API while Ryan's limit was, verbatim, "never to
            #    have more than 25$ in any market".  The code layer already
            #    clamps (verify/caps.PER_MARKET_HARD_USD; invariants take
            #    min(fact, ceiling)); this makes the STORED number tell the
            #    truth too, so no reader of the fact is misled.  Direct UPDATE
            #    is deliberate — the only path past the immutable lock — and it
            #    only ever TIGHTENS: a stored value <= the ceiling is untouched.
            #    Idempotent; journaled to fact_history like any other change.
            self._tighten_per_market_cap_fact(conn)

    PER_MARKET_CAP_FACT_KEY = "kalshi.exposure.caps"
    # FG-01 (2026-09-05): the authority is now `kalshi.limits`; both keys are
    # tightened, each in its own field name.
    PER_MARKET_CAP_FIELDS = (
        ("kalshi.exposure.caps", "max_per_market_usd"),
        ("kalshi.limits", "per_market_usd"),
    )

    @staticmethod
    def _tighten_per_market_cap_fact(conn: sqlite3.Connection) -> bool:
        """Clamp the stored per-market cap down to the compiled ceiling, in
        both the authoritative `kalshi.limits` and the legacy alias.
        Returns True when at least one row was rewritten."""
        from domains.kalshi.verify.caps import PER_MARKET_HARD_USD
        changed = False
        for key, field in Database.PER_MARKET_CAP_FIELDS:
            row = conn.execute(
                "SELECT value, source_artifact FROM facts WHERE key = ?", (key,),
            ).fetchone()
            if not row:
                continue
            try:
                val = json.loads(row["value"]) if isinstance(row["value"], str) else row["value"]
            except (TypeError, ValueError):
                continue
            if not isinstance(val, dict):
                continue
            try:
                stored = float(val.get(field))
            except (TypeError, ValueError):
                continue
            if stored <= PER_MARKET_HARD_USD + 1e-9:
                continue
            new_val = dict(val)
            new_val[field] = PER_MARKET_HARD_USD
            if key == Database.PER_MARKET_CAP_FACT_KEY:
                new_val["description"] = (
                    f"Hard capital bounds: max ${PER_MARKET_HARD_USD:.0f} per single market "
                    f"(orders + positions, per ticker; Ryan 2026-09-05 'never to have more "
                    f"than 25$ in any market') and max "
                    f"${float(val.get('max_total_portfolio_usd', 0) or 0):.0f} across total "
                    f"portfolio (positions + resting)."
                )
            new_str = json.dumps(new_val)
            conn.execute(
                "INSERT INTO fact_history (key, old_value, new_value, changed_by, source_artifact) "
                "VALUES (?, ?, ?, ?, ?)",
                (key, row["value"], new_str,
                 "db-migration-20260905-per-market-cap-25", row["source_artifact"] or ""),
            )
            conn.execute(
                "UPDATE facts SET value = ?, verified_by = ?, verified_at = CURRENT_TIMESTAMP "
                "WHERE key = ?",
                # FG-05: a migration is not Ryan; it may not write his name.
                (new_str, "db-migration-20260905 (clamp to verify/caps.PER_MARKET_HARD_USD)", key),
            )
            changed = True
        if changed:
            conn.commit()
        return changed

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        if getattr(self, "readonly", False):
            conn = sqlite3.connect(
                f"file:{self.db_path}?mode=ro", uri=True, timeout=10.0)
        else:
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=10.0,
            )
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
