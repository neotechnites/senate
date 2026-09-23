"""Dynamic Multi-Family Market Census & Venue Catalog Tracker for Kalshi.

ELIMINATES SYNTHETIC FICTION:
1. Fetches authentic open events WITH nested markets from Kalshi API (with rate-limiting protection).
2. Maintains `venue_catalog` in SQLite to track mint timestamps, close times, expected expiry, and batch drops.
3. Evaluates real qualification, ALL GATES FAIL CLOSED:
   - 24h terminal curfew keyed on expected_expiration_time (close_time fallback; parse failure disqualifies)
   - LIP program join: a live row in /trade-api/v2/incentive_programs is REQUIRED for seat inventory
   - touch-depth floor: top-of-book depth >= 250 contracts on each side to be quoted
   - fundamental base-rate side gate; families with no rule coverage are FLAGGED, never silently passed
4. Persists per-market gate outcomes (gates_json / verdict) into venue_catalog for auditable census output.
"""

import json
import logging
import sqlite3
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from domains.kalshi.harness.venue_client import (KalshiVenueClient,
                                                 call_with_rate_limit_retry,
                                                 is_rate_limited,
                                                 rate_limit_note)
from domains.kalshi.state.fact_store import FactStore
from domains.kalshi.verify.base_rates import evaluate_fundamental_base_rate, find_base_rate_rule

REPO_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = REPO_ROOT / "domains" / "kalshi" / "data" / "kalshi_domain.db"

LOG = logging.getLogger(__name__)

# Touch-depth floor: contracts resting at best bid on the quoted side (top-of-book ONLY, never summed).
DEPTH_FLOOR_CONTRACTS = 250

# ---------------------------------------------------------------------------
# /events pagination (mistake: census_events_unpaginated).
#
# The scanner used to issue exactly ONE /events request per status with
# limit=100 and no cursor, so a scan could never see more than ~300 events no
# matter how long it ran.  venue_catalog held 36,237 rows while only 801 had
# ever been scored — the other 35,436 had never been evaluated because the
# fetch never walked past page 1.  Coverage only: nothing below changes a gate
# or a verdict, it only stops the board being truncated at the door.
# ---------------------------------------------------------------------------
EVENTS_PATH = "/trade-api/v2/events"
EVENTS_STATUSES = ("open", "unopened", "initialized")
EVENTS_PAGE_LIMIT = 100        # venue page size per request
EVENTS_MAX_PAGES = 500         # HARD CAP per status: a runaway cursor can never spin forever
EVENTS_PAGE_SLEEP_SEC = 0.15   # 429 rate limit protection (unchanged from the single-shot code)
EVENTS_PAGE_TIMEOUT_SEC = 8
EVENTS_PROGRESS_EVERY = 10     # log a progress line every N pages

# LIP program join (mistake: census_no_program_join). A market with no LIVE incentive
# program earns $0 credit while carrying full adverse selection, so it is NOT seat inventory.
INCENTIVE_PROGRAMS_PATH = "/trade-api/v2/incentive_programs"
PROGRAM_PAGE_LIMIT = 1000
# ---- WHY THE EARLY STOP IS GONE (2026-09-14) -----------------------------
#
# THE FAILURE.  2026-09-13T04:00:01Z the pod cashed 34 seats in the same
# second, every one of them with cash_reason "no live LIP program for this
# market — not seat inventory" (queue_shield_run.log).  The programs had not
# ended.  Five of those markets — KXCOBUILDPERMITS-27JAN27-T36000,
# KXWVPOP-26DEC31-T1766147, KXNHMAPLE-27JUN30-T160000,
# KXCABUILDPERMITS-27JAN27-T115000, KXSDCATTLE-27JAN31-T3550000 — still have
# LIVE programs a day later.  The book was liquidated against a SHORT READ.
#
# THE BUG.  fetch_incentive_programs stopped paging after PROGRAM_STALE_PAGES=3
# consecutive pages carrying no still-open window, on the premise (in the old
# docstring) that the feed is ordered start_date DESCENDING so every open
# program sits near the top.  That premise is false for the programs we most
# want: a LONG-RUNNING program STARTED WEEKS AGO and is still open, so it sorts
# BELOW thousands of short programs that started yesterday and have already
# closed.  Three stale pages is roughly 3,000 rows of recent-but-closed
# programs, and the reader quit there every single time.
#
# THE MEASUREMENT (scratchpad probe_index.py, VPS, 2026-09-14 ~16:0xZ, same
# feed, same instant, two readers):
#     as shipped (stale stop = 3):  11 pages, 11,000 rows ->  1,440 live
#     early stop disabled:          40 pages, 40,000 rows ->  2,928 live
#     LIVE PROGRAMS THE SHIPPED READ MISSED: 1,513  (52 % of the board)
# Missed families included KXYTVIEWSW 108, KXHEADLINE 95, KXYTVIEWSHIGH 82,
# KXVENUEPERFORM 35, KXDWTSRANK 32, KXMLBPLAYOFFS 30, KXTRUMPMENTION 29.
# Election-shaped live markets: 1 by the shipped read, 16 by the full read.
#
# WHAT IT COST.  Both halves of the 2026-09-13/14 outage.  The book was cashed
# against the short read, and then could not rebuild because the seeder was
# screening half a board — which is what made a rich venue look like a board
# with no seatable supply for eighteen hours.
#
# THE RULE NOW: page until the venue's cursor is exhausted, or until
# PROGRAM_MAX_PAGES.  A run that hits the cap with a cursor still live is
# TRUNCATED and says so in the result, because a silent short read of this feed
# is a liquidation order.  The old docstring called a short read "the safe
# direction"; it is the opposite — it reads as "your program ended".
# SIZED FROM A FULL READ, NOT FROM A GUESS (2026-09-15).  The comment here used
# to say "the whole feed is ~40k and growing"; it had grown past the 120-page cap
# and every read was coming back TRUNCATED -- found by the rearm-filter
# diagnostic printing "ok=True truncated=True n=3118" at 15:3xZ.  So I paged it
# to exhaustion once, at the same 0.5s cadence the scanner uses:
#
#     25 pages   25,000 rows   2,255 live    19s
#     50 pages   50,000 rows   3,120 live    37s
#     75 pages   75,000 rows   3,122 live    56s
#    125 pages  125,000 rows   3,122 live    92s
#    DONE      212 pages  211,876 rows  3,122 live  cursor_left=False  155s
#
# TWO THINGS THAT MATTER.  The feed is 212 pages, so 120 could never finish it.
# And the LIVE rows are concentrated at the front: 3,120 of 3,122 by page 50,
# all of them by page 75, nothing after.  That is why the 120-page truncation
# was costing only ~4 live programs (daemon reads showed n=3,117/3,118 against
# a true 3,122) rather than the 1,513 the 2026-09-13 early-stop lost -- small,
# but never zero, and one of those four can be a held seat's program.
#
# 300 pages is the measured 212 with ~40% headroom for a feed that is still
# growing.  The COST GOES DOWN, not up: today is 120 pages (~90s) every 300s of
# cache TTL, a ~30% duty cycle on this endpoint; 300 pages finishing in ~155s
# against a 900s TTL is ~17%.  A complete read, less traffic, and no TRUNCATED
# deferrals.  The price is that a newly-listed program can take up to 15 min to
# appear; seats live ~55h, so that is not a constraint that binds.
PROGRAM_MAX_PAGES = 300        # 300k rows; measured full feed 2026-09-15 = 212 pages
PROGRAM_PAGE_SLEEP_SEC = 0.5   # measured: 0.15s between pages trips the venue's 429 limiter
PROGRAM_PAGE_RETRIES = 3       # transient 429/timeout retries per page before failing closed
PROGRAM_STALE_PAGES = 0        # 0 = NEVER stop early; see the receipt above
PROGRAM_CACHE_TTL_SEC = 900.0  # one full read per ~15 min; see the sizing receipt above
VERDICT_NO_PROGRAM = "DISQUALIFIED_NO_PROGRAM"

# Sentinel stored in hours_to_close when NO expiry timestamp parses.
# Negative so any curfew comparison fails closed (also for readers of the old schema).
PARSE_FAILED_HOURS = -1.0
PARSE_FAILED_FIELD = "PARSE_FAILED"

# Columns added for auditable gate outcomes (ALTER TABLE keeps live DB backward-compatible).
_CATALOG_EXTRA_COLUMNS = [
    ("expected_expiration_ts", "TEXT"),
    ("expiry_field", "TEXT"),
    ("verdict", "TEXT"),
    ("verdict_ts", "TEXT"),
    ("gates_json", "TEXT"),
]


def _parse_iso_ts(ts_str: Optional[str]) -> Optional[datetime]:
    """Parse an ISO-8601 timestamp defensively. Returns None on ANY failure (caller must fail closed)."""
    if not ts_str or not isinstance(ts_str, str):
        return None
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def _select_expiry(expected_raw: Optional[str], close_raw: Optional[str]) -> Tuple[Optional[datetime], str]:
    """Curfew must gate on expected_expiration_time when present; close_time only as fallback.

    Returns (expiry_dt, field_used). (None, PARSE_FAILED_FIELD) when neither parses — FAIL CLOSED.
    """
    expected_dt = _parse_iso_ts(expected_raw)
    if expected_dt is not None:
        return expected_dt, "expected_expiration_time"
    close_dt = _parse_iso_ts(close_raw)
    if close_dt is not None:
        return close_dt, "close_time"
    return None, PARSE_FAILED_FIELD


class CensusScanner:
    """Dynamic venue catalog tracker and opportunity census engine."""

    def __init__(self, client: Optional[KalshiVenueClient] = None, db_path: Optional[Path] = None):
        self.client = client or KalshiVenueClient()
        self.db_path = db_path or DB_PATH
        self.last_fetch_stats: Dict[str, Any] = {}
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        # 30s busy timeout: the cadence daemon shares this DB and holds brief write locks.
        return sqlite3.connect(str(self.db_path), timeout=30.0)

    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS venue_catalog (
                    ticker TEXT PRIMARY KEY,
                    event_ticker TEXT,
                    title TEXT,
                    category TEXT,
                    status TEXT,
                    open_ts TEXT,
                    close_ts TEXT,
                    hours_to_close REAL,
                    first_seen_ts TEXT,
                    last_seen_ts TEXT,
                    is_new_listing INTEGER DEFAULT 0
                )"""
            )
            # Auditability columns (idempotent; safe on the live DB the daemon is reading).
            existing_cols = {row[1] for row in conn.execute("PRAGMA table_info(venue_catalog)")}
            for col_name, col_type in _CATALOG_EXTRA_COLUMNS:
                if col_name not in existing_cols:
                    conn.execute(f"ALTER TABLE venue_catalog ADD COLUMN {col_name} {col_type}")
            # Ensure core prediction families are registered
            core_seeds = [
                ("KXFEDFUNDSYEAR-37JAN01", "KXFEDFUNDSYEAR", "Federal Funds Rate Year-End", "macro_rates", "open", 120.0),
                ("KXUSCPIYEAR-37FEB01", "KXUSCPIYEAR", "US CPI Inflation Year-End", "macro_inflation", "open", 96.0),
                ("KXSTATEBALLOTMEASURE-26NOV", "KXSTATEBALLOTMEASURE", "State Ballot Measures General", "politics_ballot", "open", 168.0),
                ("KXNOMGDPGROWTH-37JAN28", "KXNOMGDPGROWTH", "Nominal GDP Growth", "macro_gdp", "open", 144.0),
            ]
            now_iso = datetime.now(timezone.utc).isoformat()
            for tk, ev_tk, title, cat, status, hrs in core_seeds:
                conn.execute(
                    """INSERT OR IGNORE INTO venue_catalog
                    (ticker, event_ticker, title, category, status, close_ts, hours_to_close, first_seen_ts, last_seen_ts, is_new_listing)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)""",
                    (tk, ev_tk, title, cat, status, "2026-12-31T00:00:00Z", hrs, now_iso, now_iso)
                )
            conn.commit()

    def _fetch_events_page(self, status: str, limit: int, series_ticker: Optional[str],
                           cursor: Optional[str]) -> Dict[str, Any]:
        """One /events page. Raises on transport/HTTP error so the 429 retry can classify it."""
        params = [("status", status), ("limit", str(limit)), ("with_nested_markets", "true")]
        if series_ticker:
            params.append(("series_ticker", series_ticker))
        if cursor:
            params.append(("cursor", cursor))
        url = f"{self.client.base_url}{EVENTS_PATH}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": "SenateArchitect/2.0"})
        with urllib.request.urlopen(req, context=self.client._ssl_ctx,
                                    timeout=EVENTS_PAGE_TIMEOUT_SEC) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def fetch_live_events(self, limit: int = EVENTS_PAGE_LIMIT,
                          series_ticker: Optional[str] = None,
                          max_pages: int = EVENTS_MAX_PAGES,
                          on_progress: Optional[Callable[[Dict[str, Any]], None]] = None,
                          ) -> List[Dict[str, Any]]:
        """Walk the FULL open/pre-open event set WITH nested markets, cursor-paginated.

        with_nested_markets=true is mandatory: without it the events endpoint returns no
        `markets` key and every synthesized row previously fell through to a fictitious
        constant hours-to-expiry (mistake: census_curfew_hardcoded_72h).
        series_ticker targets a single family so family scans see its FULL market slate
        instead of whatever fits in the first generic page.

        PAGINATION (mistake: census_events_unpaginated).  Each status is walked with the
        venue's own `cursor` until it stops handing one back.  Guards, all of which stop
        the walk EARLY and therefore never manufacture rows:
          * `max_pages` per status — a hard cap so a cursor that never terminates
            (or one the venue keeps echoing) cannot spin forever;
          * a repeated cursor breaks the loop — the venue is looping us;
          * an empty page breaks the loop;
          * a page that errors out after the 429 retry budget ENDS that status'
            walk (a short read is a short read; it is never treated as "the board
            ends here" by anything downstream — sync only ever upserts what it saw).
        The deliberate inter-page sleep and the shared 429 retry are preserved.

        Per-status page/event counts and any short-read errors land in
        `self.last_fetch_stats` and are logged at INFO; `on_progress` (if given) is
        called with the same dict after every page.
        """
        all_events: List[Dict[str, Any]] = []
        page_limit = max(1, min(int(limit), EVENTS_PAGE_LIMIT))
        page_cap = max(1, int(max_pages))
        stats: Dict[str, Any] = {
            "series_ticker": series_ticker, "page_limit": page_limit, "max_pages": page_cap,
            "pages_total": 0, "events_total": 0, "by_status": {}, "errors": [],
            "rate_limited": False, "truncated_statuses": [],
        }
        self.last_fetch_stats = stats

        for st in EVENTS_STATUSES:
            cursor: Optional[str] = None
            seen_cursors = set()
            pages = 0
            got = 0
            truncated = False
            for _ in range(page_cap):
                fetched = call_with_rate_limit_retry(
                    self._fetch_events_page, st, page_limit, series_ticker, cursor)
                if not fetched["ok"]:
                    note = rate_limit_note(fetched)
                    stats["errors"].append(f"{st} page {pages + 1}: {note[:160]}")
                    stats["rate_limited"] = stats["rate_limited"] or bool(fetched["rate_limited"])
                    truncated = True
                    break
                data = fetched["value"]
                if not isinstance(data, dict):
                    stats["errors"].append(f"{st} page {pages + 1}: unparseable /events payload")
                    truncated = True
                    break
                evs = data.get("events") or []
                for e in evs:
                    if isinstance(e, dict):
                        e["_fetch_status"] = st
                        all_events.append(e)
                        got += 1
                pages += 1
                stats["pages_total"] += 1
                stats["events_total"] = len(all_events)
                if on_progress is not None or (pages % EVENTS_PROGRESS_EVERY == 0):
                    LOG.info("census /events %s: page %d, %d events this status, %d total",
                             st, pages, got, len(all_events))
                    if on_progress is not None:
                        on_progress(dict(stats, status=st, status_pages=pages, status_events=got))
                next_cursor = data.get("cursor") or data.get("next_cursor")
                if not next_cursor or not evs:
                    break
                if next_cursor in seen_cursors:
                    # The venue handed back a cursor we have already walked: stop
                    # rather than loop forever on the same page.
                    stats["errors"].append(f"{st}: repeated cursor after page {pages}")
                    break
                seen_cursors.add(next_cursor)
                cursor = next_cursor
                time.sleep(EVENTS_PAGE_SLEEP_SEC)  # 429 rate limit protection
            else:
                # Loop ran the whole page budget without breaking -> more board remains.
                truncated = True
                stats["errors"].append(f"{st}: hit max_pages={page_cap} cap")
            if truncated:
                stats["truncated_statuses"].append(st)
            stats["by_status"][st] = {"pages": pages, "events": got, "truncated": truncated}
            LOG.info("census /events %s complete: %d pages, %d events (truncated=%s)",
                     st, pages, got, truncated)
            time.sleep(EVENTS_PAGE_SLEEP_SEC)  # 429 rate limit protection

        LOG.info("census /events sweep: %d pages, %d events across %s",
                 stats["pages_total"], stats["events_total"], list(EVENTS_STATUSES))
        return all_events

    def sync_venue_catalog(self, series_ticker: Optional[str] = None,
                           max_pages: int = EVENTS_MAX_PAGES) -> Dict[str, Any]:
        """Sync live open events into SQLite venue_catalog and detect new listings.

        Markets with no parseable expiry timestamp are stored with the PARSE_FAILED
        sentinel (negative hours) so every downstream curfew comparison fails closed.
        Events without nested markets are SKIPPED — rows are never synthesized.

        The event fetch is cursor-paginated, so a sync now walks the WHOLE board
        rather than the first ~300 events; `max_pages` bounds it per status.
        """
        events = self.fetch_live_events(limit=EVENTS_PAGE_LIMIT, series_ticker=series_ticker,
                                        max_pages=max_pages)
        fetch_stats = dict(self.last_fetch_stats or {})
        now_ts = datetime.now(timezone.utc).isoformat()
        now_epoch = time.time()

        new_listings_count = 0
        updated_count = 0
        skipped_no_markets = 0
        parse_failures = 0

        with self._connect() as conn:
            for ev in events:
                event_ticker = ev.get("event_ticker", "")
                title = ev.get("title", "")
                category = ev.get("category", "general")

                markets = ev.get("markets") or []
                if not markets:
                    # FAIL CLOSED: never synthesize a market row from event scraps.
                    skipped_no_markets += 1
                    continue

                for m in markets:
                    ticker = m.get("ticker", event_ticker)
                    close_raw = m.get("close_time") or ""
                    expected_raw = m.get("expected_expiration_time") or ""
                    open_raw = m.get("open_time") or ""
                    market_title = m.get("title") or title

                    expiry_dt, expiry_field = _select_expiry(expected_raw, close_raw)
                    if expiry_dt is None:
                        # FAIL CLOSED: no passing constant. Negative sentinel disqualifies under any curfew.
                        hours_to_expiry = PARSE_FAILED_HOURS
                        parse_failures += 1
                    else:
                        hours_to_expiry = max(0.0, (expiry_dt.timestamp() - now_epoch) / 3600.0)

                    # Check if exists
                    cur = conn.execute("SELECT first_seen_ts FROM venue_catalog WHERE ticker = ?", (ticker,))
                    row = cur.fetchone()
                    if row is None:
                        is_new = 1
                        new_listings_count += 1
                        first_seen = now_ts
                    else:
                        is_new = 0
                        first_seen = row[0]
                        updated_count += 1

                    conn.execute(
                        """INSERT OR REPLACE INTO venue_catalog
                        (ticker, event_ticker, title, category, status, open_ts, close_ts,
                         expected_expiration_ts, expiry_field, hours_to_close,
                         first_seen_ts, last_seen_ts, is_new_listing)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (ticker, event_ticker, market_title, category, "open", open_raw, close_raw,
                         expected_raw, expiry_field, round(hours_to_expiry, 1),
                         first_seen, now_ts, is_new)
                    )
            conn.commit()

        return {
            "events_fetched": len(events),
            "new_listings": new_listings_count,
            "catalog_updated": updated_count,
            "skipped_no_markets": skipped_no_markets,
            "expiry_parse_failures": parse_failures,
            "sync_ts": now_ts,
            # Coverage receipt: how much of the board this sync actually walked.
            "pages_fetched": fetch_stats.get("pages_total", 0),
            "fetch_truncated": bool(fetch_stats.get("truncated_statuses")),
            "fetch_stats": fetch_stats,
        }

    # ------------------------------------------------------------------
    # Gate: LIP program join (live /trade-api/v2/incentive_programs)
    # ------------------------------------------------------------------

    def fetch_incentive_programs(self) -> Dict[str, Any]:
        """Cursor-paginated pull of the keyless LIP feed.

        Returns {"ok": bool, "programs": [...], "pages": int, "error": str|None}.
        FAIL CLOSED: ok=False on ANY page error, unparseable body, or an empty
        payload — the caller must then disqualify every market, never pass through.

        Pages until the venue's cursor is exhausted (or PROGRAM_MAX_PAGES). The
        result carries truncated=True when the cap was hit with a cursor still
        live, because a silent short read of THIS feed reads downstream as "your
        program ended" and cashes held seats — see the 2026-09-14 receipt at
        PROGRAM_STALE_PAGES. Setting PROGRAM_STALE_PAGES > 0 restores the old
        early stop for tests; 0 disables it.
        """
        programs: List[Dict[str, Any]] = []
        cursor = None
        pages = 0
        stale_pages = 0
        now_epoch = time.time()
        for _ in range(PROGRAM_MAX_PAGES):
            query = f"limit={PROGRAM_PAGE_LIMIT}"
            if cursor:
                query += f"&cursor={urllib.parse.quote(cursor)}"
            url = f"{self.client.base_url}{INCENTIVE_PROGRAMS_PATH}?{query}"
            req = urllib.request.Request(url, headers={"User-Agent": "SenateArchitect/2.0"})
            body = None
            last_error = None
            last_rate_limited = False
            for attempt in range(PROGRAM_PAGE_RETRIES):
                try:
                    with urllib.request.urlopen(req, context=self.client._ssl_ctx, timeout=10) as resp:
                        body = json.loads(resp.read().decode("utf-8"))
                    break
                except Exception as exc:
                    last_error = str(exc)[:200]
                    last_rate_limited = is_rate_limited(exc)
                    time.sleep(PROGRAM_PAGE_SLEEP_SEC * (2 ** attempt))  # 429 backoff
            if body is None:
                # A short read of the program feed is NOT "no programs" — fail closed.
                # But SAY which kind of short read it was: rate-limit contention
                # from our own research lanes reads identically to a broken feed
                # unless we label it, and an unlabelled 429 silently disqualifies
                # every market for a whole cycle (the row-61 failure mode).
                if last_rate_limited:
                    last_error = (f"rate-limited, retried {PROGRAM_PAGE_RETRIES - 1} "
                                  f"times: {last_error}")
                return {"ok": False, "programs": [], "pages": pages, "error": last_error,
                        "rate_limited": last_rate_limited}
            if not isinstance(body, dict):
                return {"ok": False, "programs": [], "pages": pages,
                        "error": "unparseable incentive_programs payload"}
            page = body.get("incentive_programs")
            if page is None:
                page = body.get("liquidity_incentive_programs") or body.get("programs")
            if page is None:
                return {"ok": False, "programs": [], "pages": pages,
                        "error": "unrecognized incentive_programs shape"}
            pages += 1
            rows = [p for p in page if isinstance(p, dict)]
            programs.extend(rows)
            cursor = body.get("next_cursor") or body.get("cursor")
            if not cursor or not page:
                break
            open_on_page = any(
                (_parse_iso_ts(p.get("end_date")) or datetime.fromtimestamp(0, timezone.utc)).timestamp() > now_epoch
                for p in rows
            )
            stale_pages = 0 if open_on_page else stale_pages + 1
            if PROGRAM_STALE_PAGES and stale_pages >= PROGRAM_STALE_PAGES:
                break  # only when explicitly re-enabled (tests); see the receipt above
            time.sleep(PROGRAM_PAGE_SLEEP_SEC)  # 429 rate limit protection
        if not programs:
            return {"ok": False, "programs": [], "pages": pages,
                    "error": "incentive_programs feed returned zero rows"}
        # TRUNCATION IS NEVER SILENT.  We ran out of page budget while the venue
        # still had a cursor, so rows below this point were never read and any
        # market whose program lives down there will look dead to every caller.
        truncated = bool(cursor) and pages >= PROGRAM_MAX_PAGES
        return {"ok": True, "programs": programs, "pages": pages, "error": None,
                "truncated": truncated}

    def load_live_program_index(self, now_epoch: Optional[float] = None,
                                force: bool = False) -> Dict[str, Any]:
        """Index of market_ticker -> live LIP program row, TTL-cached per scanner instance.

        Live == the program row parses AND start_date <= now < end_date. Rows that do
        not parse are DROPPED (a program we cannot read is a program we cannot bank on).
        Returns {"ok": bool, "by_ticker": {...}, "programs_total": n, "live_total": n, "error": ...};
        ok=False means the feed failed and EVERY market must be disqualified.
        """
        now_epoch = time.time() if now_epoch is None else now_epoch
        cached = getattr(self, "_program_cache", None)
        if cached and not force and (time.time() - cached["fetched_at"]) < PROGRAM_CACHE_TTL_SEC:
            feed = cached["feed"]
        else:
            feed = self.fetch_incentive_programs()
            self._program_cache = {"fetched_at": time.time(), "feed": feed}
        if not feed["ok"]:
            # FAIL CLOSED: no index at all, so no market can join a program.
            return {"ok": False, "by_ticker": {}, "programs_total": 0, "live_total": 0,
                    "error": feed.get("error") or "incentive_programs feed unavailable"}

        by_ticker: Dict[str, Dict[str, Any]] = {}
        for p in feed["programs"]:
            ticker = p.get("market_ticker") or p.get("ticker")
            if not ticker:
                continue
            start_dt = _parse_iso_ts(p.get("start_date"))
            end_dt = _parse_iso_ts(p.get("end_date"))
            if start_dt is None or end_dt is None:
                continue  # unreadable window is never live
            if not (start_dt.timestamp() <= now_epoch < end_dt.timestamp()):
                continue
            by_ticker[str(ticker)] = {
                "program_id": p.get("id"),
                "start_date": p.get("start_date"),
                "end_date": p.get("end_date"),
                "period_reward": p.get("period_reward"),
                "target_size_fp": p.get("target_size_fp"),
                # THE LIP DISTANCE DECAY.  This field was being dropped here,
                # so price_derivation never saw the venue's real discount factor
                # and silently fell back to its 0.50 default.  The default
                # happens to equal today's 5000bps, so the bug was invisible —
                # until the venue changes a program's decay and we price a deep
                # level off an assumption.  Carry it through.
                "discount_factor_bps": p.get("discount_factor_bps"),
                "incentive_type": p.get("incentive_type"),
                "hours_remaining": round((end_dt.timestamp() - now_epoch) / 3600.0, 1),
            }
        return {"ok": True, "by_ticker": by_ticker, "programs_total": len(feed["programs"]),
                "live_total": len(by_ticker), "error": None,
                # Carried so a caller deciding "this market has no program" can
                # tell "the feed says no" from "we never read that far".
                "truncated": bool(feed.get("truncated"))}

    # ------------------------------------------------------------------
    # Gate: touch depth (top-of-book, NEVER summed across levels)
    # ------------------------------------------------------------------

    @staticmethod
    def _touch_depth_from_book(levels: Optional[List[Any]]) -> int:
        """Contracts resting at the single best price level (top-of-book ONLY, never summed).

        Handles both venue book shapes: legacy integer cents ([price_cents, count])
        and fp dollar strings (["0.4900", "1007.00"]). Empty/malformed -> 0 (fail closed).
        """
        best_price = None
        best_qty = 0
        for lvl in levels or []:
            try:
                price, qty = float(lvl[0]), float(lvl[1])
            except Exception:
                continue  # malformed level carries no depth
            if best_price is None or price > best_price:
                best_price, best_qty = price, qty
        return int(best_qty)

    def measure_touch_depth(self, ticker: str) -> Dict[str, Any]:
        """Fetch the public orderbook and report top-of-book depth per side.

        Any fetch/shape failure returns ok=False with zero depth — FAIL CLOSED.
        Prefers the legacy `orderbook` key; falls back to the venue's newer
        `orderbook_fp` (yes_dollars/no_dollars) shape.
        """
        # A 429 here disqualifies the market for the whole cycle exactly as a
        # broken book would.  Retry the rate limit in-cycle, then fail closed
        # with a diagnosis that names it.
        fetched = call_with_rate_limit_retry(self.client.fetch_public_orderbook, ticker)
        if not fetched["ok"]:
            return {"ok": False, "yes": 0, "no": 0,
                    "error": rate_limit_note(fetched)[:200],
                    "rate_limited": bool(fetched["rate_limited"])}
        try:
            body = fetched["value"]
            book = body.get("orderbook") or {}
            yes_levels, no_levels = book.get("yes"), book.get("no")
            if not (yes_levels or no_levels):
                fp = body.get("orderbook_fp") or {}
                yes_levels, no_levels = fp.get("yes_dollars"), fp.get("no_dollars")
            if "orderbook" not in body and "orderbook_fp" not in body:
                return {"ok": False, "yes": 0, "no": 0, "error": "unrecognized orderbook shape"}
            return {
                "ok": True,
                "yes": self._touch_depth_from_book(yes_levels),
                "no": self._touch_depth_from_book(no_levels),
            }
        except Exception as exc:
            return {"ok": False, "yes": 0, "no": 0, "error": str(exc)[:200]}

    # ------------------------------------------------------------------
    # Census scan
    # ------------------------------------------------------------------

    def scan_family_opportunities(
        self,
        family_prefix: Optional[str] = None,
        min_hours_to_close: float = 24.0,
    ) -> List[Dict[str, Any]]:
        """Scan active catalog through the full fail-closed gate chain and persist verdicts.

        Gate order (cheap first): expiry parse -> 24h curfew (expected_expiration_time)
        -> speed exclusion -> LIP program join (live /incentive_programs)
        -> touch-depth floor (orderbook fetch) -> base-rate side gate.
        Every verdict + measured values is written back to venue_catalog (gates_json).
        """
        # 1. Sync live events if possible (family scans target the series for a full slate)
        series = family_prefix.upper().split("-")[0] if family_prefix else None
        self.sync_venue_catalog(series_ticker=series)

        # 2. Query catalog (read fully, then release the connection before network calls)
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            params = []
            if family_prefix:
                # Family scan: every market in the family, newest first.
                query = ("SELECT * FROM venue_catalog WHERE status = 'open' "
                         "AND (ticker LIKE ? OR event_ticker LIKE ?) "
                         "ORDER BY first_seen_ts DESC LIMIT 250")
                params.extend([f"%{family_prefix.upper()}%", f"%{family_prefix.upper()}%"])
            else:
                # Discovery sweep: one representative (newest) row PER family so a large
                # slate drop cannot crowd every other family out of the census window.
                query = ("SELECT *, MAX(first_seen_ts) FROM venue_catalog WHERE status = 'open' "
                         "GROUP BY CASE WHEN instr(ticker, '-') > 0 "
                         "THEN substr(ticker, 1, instr(ticker, '-') - 1) ELSE ticker END "
                         "ORDER BY first_seen_ts DESC LIMIT 250")
            rows = [dict(r) for r in conn.execute(query, params).fetchall()]

        results = []
        verdict_writes = []
        seen_families = set()
        now_epoch = time.time()
        program_index: Optional[Dict[str, Any]] = None  # loaded lazily, once per scan

        for r in rows:
            ticker = r["ticker"]
            base_family = ticker.split("-")[0] if "-" in ticker else ticker
            if base_family in seen_families and not family_prefix:
                continue
            seen_families.add(base_family)

            category = r["category"] or "general"
            title = r["title"] or ""
            is_new = bool(r["is_new_listing"])

            # --- Gate 1: expiry parse + field selection (recomputed live, never trusted from sync) ---
            expiry_dt, expiry_field = _select_expiry(r.get("expected_expiration_ts"), r.get("close_ts"))
            gates: Dict[str, Any] = {}
            if expiry_dt is None:
                hours_left = PARSE_FAILED_HOURS
                gates["curfew"] = {"pass": False, "expiry_field": expiry_field,
                                   "error": "no parseable expiry timestamp"}
                status = "DISQUALIFIED_PARSE"
                reason = "No parseable expected_expiration_time/close_time — FAIL CLOSED, no default constant."
            else:
                hours_left = max(0.0, (expiry_dt.timestamp() - now_epoch) / 3600.0)
                curfew_pass = hours_left >= min_hours_to_close
                gates["curfew"] = {"pass": curfew_pass, "expiry_field": expiry_field,
                                   "hours_to_expiry": round(hours_left, 1),
                                   "min_hours_required": min_hours_to_close}
                if not curfew_pass:
                    status = "DISQUALIFIED_CURFEW"
                    reason = f"{expiry_field} in {hours_left:.1f}h (< {min_hours_to_close}h curfew)."
                elif "TEMP" in ticker or "SPEED" in category.upper():
                    gates["speed"] = {"pass": False}
                    status = "DISQUALIFIED_SPEED"
                    reason = "Sub-minute weather/fast asset disqualified from maker seats."
                else:
                    gates["speed"] = {"pass": True}
                    status = None
                    reason = None

            recommended_sides = ["yes"] if "BALLOT" in ticker else ["maker_both"]

            # --- Gate 2: LIP program join (only reached if curfew/speed passed) ---
            # A market with no LIVE incentive program is NOT seat inventory: quoting it
            # earns $0 credit while carrying full adverse-selection risk.
            if status is None:
                if program_index is None:
                    program_index = self.load_live_program_index(now_epoch)
                program = program_index["by_ticker"].get(ticker) if program_index["ok"] else None
                gates["program"] = {
                    "pass": program is not None,
                    "feed_ok": program_index["ok"],
                    "live_programs": program_index["live_total"],
                    "source_endpoint": INCENTIVE_PROGRAMS_PATH,
                    "program": program,
                }
                if not program_index["ok"]:
                    gates["program"]["error"] = program_index.get("error")
                if program is None:
                    status = VERDICT_NO_PROGRAM
                    if not program_index["ok"]:
                        reason = (f"incentive_programs feed unavailable "
                                  f"({program_index.get('error')}) — FAIL CLOSED, "
                                  f"no market may qualify without a verified live LIP program.")
                    else:
                        reason = (f"No live LIP program for {ticker} in {INCENTIVE_PROGRAMS_PATH} "
                                  f"({program_index['live_total']} live programs venue-wide) — "
                                  f"unsubsidized book, not seat inventory.")
                    recommended_sides = []

            # --- Gate 3: touch-depth floor (only reached if curfew/speed/program passed) ---
            if status is None:
                quote_sides = ["yes", "no"] if recommended_sides == ["maker_both"] else list(recommended_sides)
                depth = self.measure_touch_depth(ticker)
                depth_by_side = {s: depth.get(s, 0) for s in quote_sides}
                passing_sides = [s for s in quote_sides
                                 if depth["ok"] and depth_by_side[s] >= DEPTH_FLOOR_CONTRACTS]
                gates["depth"] = {
                    "pass": bool(passing_sides),
                    "floor_contracts": DEPTH_FLOOR_CONTRACTS,
                    "touch_depth": depth_by_side,
                    "book_ok": depth["ok"],
                }
                if not depth["ok"]:
                    gates["depth"]["error"] = depth.get("error", "orderbook unavailable")
                time.sleep(0.12)  # 429 rate limit protection
                if not passing_sides:
                    status = "DISQUALIFIED_DEPTH"
                    reason = (f"Touch depth {depth_by_side} below {DEPTH_FLOOR_CONTRACTS}-contract "
                              f"top-of-book floor on every quotable side (book_ok={depth['ok']}).")
                else:
                    # --- Gate 4: fundamental base-rate side gate ---
                    coverage = find_base_rate_rule(ticker, market_title=title)
                    safe_sides = []
                    prohibited = {}
                    for side in passing_sides:
                        # Worst-case cheap quote price: if a rule prohibits this side at any
                        # price <= max_contra_price, the census must not recommend it.
                        is_safe, violation, _rule = evaluate_fundamental_base_rate(
                            ticker=ticker, side=side, price=0.01, market_title=title,
                        )
                        if is_safe:
                            safe_sides.append(side)
                        else:
                            prohibited[side] = violation
                    gates["base_rate"] = {
                        "pass": bool(safe_sides) and coverage is not None,
                        "rule": coverage[0] if coverage else None,
                        "covered": coverage is not None,
                        "prohibited_sides": prohibited,
                        "safe_sides": safe_sides,
                    }
                    if not safe_sides:
                        status = "DISQUALIFIED_BASE_RATE"
                        reason = f"All quotable sides prohibited by base-rate rules: {list(prohibited)}."
                    elif coverage is None:
                        # Flagged, NEVER silently passed as QUALIFIED.
                        status = "FLAGGED_NO_BASERATE_RULE"
                        reason = (f"Curfew ({hours_left:.1f}h via {expiry_field}) and depth passed, "
                                  f"but NO base-rate rule covers family {base_family} — flagged, not qualified.")
                        recommended_sides = safe_sides
                    else:
                        status = "QUALIFIED"
                        prog_end = (gates.get("program", {}).get("program") or {}).get("end_date")
                        reason = (f"Margin {hours_left:.1f}h via {expiry_field} >= {min_hours_to_close}h; "
                                  f"live LIP program until {prog_end}; "
                                  f"touch depth {depth_by_side} >= {DEPTH_FLOOR_CONTRACTS}; "
                                  f"base-rate rule {coverage[0]} permits sides {safe_sides}.")
                        recommended_sides = safe_sides

            verdict_ts = datetime.now(timezone.utc).isoformat()
            verdict_writes.append((status, verdict_ts, json.dumps(gates), expiry_field,
                                   round(hours_left, 1), ticker))

            cand = {
                "family": base_family,
                "ticker": ticker,
                "event_ticker": r["event_ticker"],
                "title": title,
                "category": category,
                "active_schedule": "live_catalog_7d",
                "hours_to_close": round(hours_left, 1),
                "min_hours_margin": round(hours_left, 1),
                "expiry_field": expiry_field,
                "status": status,
                "reason": reason,
                "gates": gates,
                "is_new_listing": is_new,
                "first_seen_ts": r["first_seen_ts"],
                "fetch_timestamp": r["last_seen_ts"],
                "source_endpoint": "/trade-api/v2/events?with_nested_markets=true",
                "recommended_sides": recommended_sides,
            }
            results.append(cand)

        # 3. Persist per-market gate outcomes for auditable census output
        if verdict_writes:
            with self._connect() as conn:
                conn.executemany(
                    """UPDATE venue_catalog
                       SET verdict = ?, verdict_ts = ?, gates_json = ?,
                           expiry_field = ?, hours_to_close = ?
                       WHERE ticker = ?""",
                    verdict_writes,
                )
                conn.commit()

        # Fallback if catalog is completely empty (offline/first run).
        # FAIL CLOSED: offline seeds carry zero venue evidence and can never be QUALIFIED.
        if not results:
            fallback_families = [
                {"family": "KXFEDFUNDSYEAR", "category": "macro_rates", "days": "7d", "hours": 120.0},
                {"family": "KXUSCPIYEAR", "category": "macro_inflation", "days": "7d", "hours": 96.0},
                {"family": "KXNOMGDPGROWTH", "category": "macro_gdp", "days": "7d", "hours": 144.0},
            ]
            for f in fallback_families:
                results.append({
                    "family": f["family"],
                    "ticker": f["family"],
                    "category": f["category"],
                    "active_schedule": f["days"],
                    "hours_to_close": f["hours"],
                    "min_hours_margin": f["hours"],
                    "expiry_field": "offline_seed",
                    "status": "DISQUALIFIED_OFFLINE",
                    "reason": "Offline fallback seed: no live catalog evidence — FAIL CLOSED.",
                    "gates": {"curfew": {"pass": False, "error": "offline fallback"}},
                    "is_new_listing": False,
                    "fetch_timestamp": datetime.now(timezone.utc).isoformat(),
                    "source_endpoint": "fallback_seed",
                    "recommended_sides": [],
                })

        return results
