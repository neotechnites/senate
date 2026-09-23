"""Fact and Seat Store for Kalshi Domain Pod."""

import json
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from domains.kalshi.state.db import Database
from domains.kalshi.state.models import ActiveOrder, Fact, _utc_now_iso
from domains.kalshi.verify.caps import (LEGACY_CAPS_FACT_KEY, LIMITS_FACT_KEY,
                                        MAX_SEATS, PER_MARKET_HARD_USD,
                                        TOTAL_HARD_USD)

# Default reality as of 2026-08-17: the pod is placement-disarmed and every
# cycle must SAY so.  This row is auto-seeded so the state machine is never
# silently absent (the failure mode Ryan ruled against on 2026-08-17).
#
# FG-09 (2026-09-05) PAID-FOR LESSON: this reason string used to read
# "...+ Ryan standing authority $250/$50".  It was agent text (set_by is the
# framework, not Ryan), it was auto-inserted into EVERY fresh ledger, and it
# was read back on 2026-09-05 as if it were a Ryan instruction for $250 total
# / $50 per market -- the same day a $50 seat (KXKR-26SEPIDSALES-1.5) was
# seeded and swept.  Ryan's actual words are "never to have more than 25$ in
# any market".  A placement-state reason is a LEDGER NOTE, not a limits
# authority: it must never restate a dollar figure or speak in Ryan's name.
# The sizing numbers live in exactly one place (verify/caps.py, surfaced as
# fact `kalshi.limits`); anything that quotes them elsewhere can drift, and
# drift here already cost a fill.  tests/test_placement_state.py pins this.
DEFAULT_PLACEMENT_STATE = {
    "state": "DISARMED",
    "reason": (
        "framework default: DISARMED until a human arms "
        "(A56 verdict 2026-08-15; seat-qualification-20260817 package pending); "
        f"sizing limits live only in fact {LIMITS_FACT_KEY} / verify/caps.py, "
        "never in this reason"
    ),
    "set_by": "framework-default-20260817",
}


def _float_or_none(v: Any) -> Optional[float]:
    """FLAT-3: a fill's count parsed leniently; unparseable -> None, never 0."""
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _int_or_none(v: Any) -> Optional[int]:
    if v is None or v == "":
        return None
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


# --- FG-05 (2026-09-05): WHO MAY LOCK A FACT, AND WHO MAY SPEAK FOR RYAN ---
#
# PAID-FOR LESSON.  Until today set_fact refused only to overwrite a row that
# was ALREADY immutable.  Any process could insert is_immutable=True under any
# verified_by string, and the ON CONFLICT clause copied excluded.is_immutable,
# so a later write could lock a fact that had been mutable.  That is the
# exact mechanism by which a prior agent stamped `kalshi.exposure.caps` =
# $50/market, is_immutable=True, verified_by="ryan_sovereign_mandate" -- a
# label it awarded itself, on a number Ryan never gave -- and then every
# correction through the API was refused ("permanently locked"), the live
# VPS copy had to be moved by raw SQL, and harness/auto_seeder.py cited that
# fact as its authority for the $50 KXKR-26SEPIDSALES-1.5 seat that was
# seeded at 07:24Z and swept at 14:30Z the same day.  Ryan, verbatim:
# "never to have more than 25$ in any market".
#
# RULES, enforced here at the only write path:
#   (a) is_immutable=True is accepted ONLY from a venue-mechanics provenance
#       in IMMUTABLE_ALLOWLIST.  A human-authority label is never a reason
#       to lock: a ruling must stay correctable through the API (journaled
#       in fact_history), and the code layer (verify/caps.py) is what stops
#       a stored value from loosening.
#   (b) an existing row's is_immutable flag is never changed by an upsert
#       (dropped from ON CONFLICT ... DO UPDATE): a fact is locked at birth
#       by an allowlisted source or not at all.
#   (c) a fact stamped with Ryan's name (verified_by matching ^ryan, any
#       case) must carry his words: value["authorized"] holding a
#       YYYY-MM-DD date and a quoted span ('...' or "...").  No quote, no
#       date -> not his fact; stamp it as the session that relayed it.
IMMUTABLE_ALLOWLIST = frozenset({
    "venue_api_spec",
    "exchange_regulatory_rulebook",
    "settlement_api_spec",
    "audited_reward_receipts",
    "exchange_fee_specification",
})
_RYAN_PROVENANCE = re.compile(r"^ryan", re.IGNORECASE)
_AUTHORIZED_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_AUTHORIZED_QUOTE = re.compile(r"'[^']+'|\"[^\"]+\"")


def validate_fact_governance(fact: Fact) -> None:
    """Raise ValueError if `fact` may not be written as stamped (FG-05).
    Pure function; no store access.  See the receipt above."""
    by = str(fact.verified_by or "")
    if fact.is_immutable and by not in IMMUTABLE_ALLOWLIST:
        raise ValueError(
            f"FG-05: fact '{fact.key}' may not be stamped immutable by "
            f"verified_by='{by}'. Only venue-mechanics provenance may lock a fact "
            f"({', '.join(sorted(IMMUTABLE_ALLOWLIST))}); a policy or human-authority "
            f"fact stays mutable so it can be corrected through the API "
            f"(the $50 kalshi.exposure.caps lock, 2026-09-05).")
    if _RYAN_PROVENANCE.match(by):
        auth = fact.value.get("authorized") if isinstance(fact.value, dict) else None
        auth_s = auth if isinstance(auth, str) else ""
        if not (auth_s and _AUTHORIZED_DATE.search(auth_s) and _AUTHORIZED_QUOTE.search(auth_s)):
            raise ValueError(
                f"FG-05: ryan-attributed fact requires verbatim quote + date: "
                f"'{fact.key}' is stamped verified_by='{by}' but value['authorized'] "
                f"is {auth!r}. Put Ryan's words in quotes with the YYYY-MM-DD he said "
                f"them, or stamp the fact as the session that relayed it.")


class FactStore:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    # --- Facts CRUD ---
    def set_fact(self, fact: Fact) -> None:
        validate_fact_governance(fact)   # FG-05: refuse before touching the DB
        with self.db.get_connection() as conn:
            cur = conn.execute("SELECT is_immutable, value, source_artifact FROM facts WHERE key = ?", (fact.key,))
            existing = cur.fetchone()
            if existing and existing["is_immutable"]:
                raise ValueError(f"CRITICAL: Cannot overwrite immutable fact '{fact.key}'. It is permanently locked.")

            val_str = json.dumps(fact.value) if not isinstance(fact.value, (str, int, float, bool)) else fact.value
            
            if existing:
                conn.execute(
                    """
                    INSERT INTO fact_history (key, old_value, new_value, changed_by, source_artifact)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (fact.key, existing["value"], val_str if isinstance(val_str, str) else json.dumps(val_str), fact.verified_by, fact.source_artifact),
                )

            conn.execute(
                """
                INSERT INTO facts (key, domain, value, source_artifact, verified_at, verified_by, is_immutable)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    domain = excluded.domain,
                    value = excluded.value,
                    source_artifact = excluded.source_artifact,
                    verified_at = excluded.verified_at,
                    verified_by = excluded.verified_by
                """,
                (
                    fact.key,
                    fact.domain,
                    val_str if isinstance(val_str, str) else json.dumps(val_str),
                    fact.source_artifact,
                    fact.verified_at,
                    fact.verified_by,
                    1 if fact.is_immutable else 0,
                ),
            )
            conn.commit()

    def get_fact(self, key: str) -> Optional[Fact]:
        with self.db.get_connection() as conn:
            cur = conn.execute("SELECT key, domain, value, source_artifact, verified_at, verified_by, is_immutable FROM facts WHERE key = ?", (key,))
            row = cur.fetchone()
            if not row:
                return None
            val = json.loads(row["value"]) if isinstance(row["value"], str) else row["value"]
            return Fact(
                key=row["key"],
                domain=row["domain"],
                value=val,
                source_artifact=row["source_artifact"],
                verified_at=row["verified_at"],
                verified_by=row["verified_by"],
                is_immutable=bool(row["is_immutable"]),
            )

    # --- Capital limits (ONE resolver; FG-01, 2026-09-05) ---
    def get_limits(self) -> Optional[Dict[str, Any]]:
        """Ryan's capital limits as every reader must see them.

        WHY ONE RESOLVER: until 2026-09-05 four readers (verify/invariants,
        placement_engine.resolve_escrow_cap + _max_open_orders, watch_stuck,
        watch.sh) each read `kalshi.exposure.caps` in their own way, with
        their own private fallbacks ($250 here, $125 there, 20 elsewhere),
        while that fact said $50/market, was immutable, and disagreed with
        both Ryan and the live VPS.  The KXKR $50 seat was seeded and swept
        under exactly that split.  Now: `kalshi.limits` is the authority;
        the legacy key is consulted only when it is absent (a DB the VPS
        migration has not yet reached); the per-market number is clamped
        to the compiled ceiling (a fact may only TIGHTEN it); and an
        unreadable total is returned as None so the caller FAILS CLOSED
        rather than inventing a budget.

        Returns None when neither fact is present — callers treat that as
        "cannot see the limits" and refuse, never as "no limits".
        """
        def _f(x):
            try:
                v = float(x)
            except (TypeError, ValueError):
                return None
            return v if v > 0 else None

        def _i(x):
            try:
                v = int(x)
            except (TypeError, ValueError):
                return None
            return v if v > 0 else None

        readings = []   # (source_key, per, total, seats, headroom, fact)
        lim = self.get_fact(LIMITS_FACT_KEY)
        if lim and isinstance(lim.value, dict) and "per_market_usd" in lim.value:
            v = lim.value
            readings.append((LIMITS_FACT_KEY, v.get("per_market_usd"), v.get("total_usd"),
                             v.get("max_seats"), v.get("replace_headroom_usd"), lim))
        leg = self.get_fact(LEGACY_CAPS_FACT_KEY)
        if leg and isinstance(leg.value, dict) and "max_per_market_usd" in leg.value:
            v = leg.value
            readings.append((LEGACY_CAPS_FACT_KEY, v.get("max_per_market_usd"),
                             v.get("max_total_portfolio_usd",
                                   v.get("max_autoseat_collateral_usd")),
                             v.get("max_open_orders"), None, leg))
        if not readings:
            return None
        # THE TIGHTER NUMBER WINS ACROSS BOTH KEYS.  kalshi.limits is the
        # authority, but while the legacy alias still exists a ruling written
        # to either key must bind: a $20 fact anywhere governs at $20.  An
        # unreadable per-market number reads as the ceiling; an unreadable
        # total/seat count reads as None (fail closed at the caller) UNLESS
        # the other key carries a readable one.
        source, fact = readings[0][0], readings[0][5]
        pers = [_f(r[1]) if _f(r[1]) is not None else PER_MARKET_HARD_USD for r in readings]
        per_f = min(pers + [PER_MARKET_HARD_USD])   # never looser than compiled
        # CAP-6 (2026-09-05): the total and the seat count are clamped to the
        # compiled ceilings exactly as the per-market number is.  Until today
        # a $1000 total in either fact resolved to $1000 here and was
        # installed by resolve_escrow_cap and the ExecutionGate unclamped;
        # only the seeder took min() against verify/caps.  Ryan 2026-08-20:
        # 20 x $25 in a $530 cap.  A fact may TIGHTEN either, never raise it;
        # an unreadable one still resolves to None (fail closed).
        totals = [t for t in (_f(r[2]) for r in readings) if t is not None]
        total_f: Optional[float] = min(min(totals), TOTAL_HARD_USD) if totals else None
        seat_vals = [n for n in (_i(r[3]) for r in readings) if n is not None]
        seats_i: Optional[int] = min(min(seat_vals), MAX_SEATS) if seat_vals else None
        heads = [h for h in (_f(r[4]) for r in readings) if h is not None]
        headroom_f: Optional[float] = heads[0] if heads else None
        return {
            "per_market_usd": per_f,
            "total_usd": total_f,
            "max_seats": seats_i,
            "replace_headroom_usd": headroom_f,
            "source": source,
            "verified_by": fact.verified_by,
            "is_immutable": bool(fact.is_immutable),
        }

    def list_facts(self) -> List[Fact]:
        with self.db.get_connection() as conn:
            cur = conn.execute("SELECT key, domain, value, source_artifact, verified_at, verified_by, is_immutable FROM facts ORDER BY key ASC")
            results = []
            for row in cur.fetchall():
                val = json.loads(row["value"]) if isinstance(row["value"], str) else row["value"]
                results.append(Fact(
                    key=row["key"],
                    domain=row["domain"],
                    value=val,
                    source_artifact=row["source_artifact"],
                    verified_at=row["verified_at"],
                    verified_by=row["verified_by"],
                    is_immutable=bool(row["is_immutable"]),
                ))
            return results

    # --- Placement State (order-placement arm/disarm ledger) ---
    #
    # THREE STATES, and the scope of each (2026-08-18).  Until this date there
    # were two, and DISARMED was a GLOBAL hammer: an automatic fill-halt in one
    # market froze every seat in the pod, because atomic_replace answered every
    # trip with CASH.  On 2026-08-18 a fill in KXGENERICBALLOTVOTEHUB disarmed
    # placement globally and left an unrelated KXCOMPANYLAYOFF seat able to exit
    # but never to re-arm — one erosion event away from being permanently ended
    # by news about a different market.  Ryan: "it shouldnt be global, becuase
    # now goog has no shield."  So scope is now explicit:
    #
    #   ARMED     new deployments allowed; existing seats maintained.
    #   DISARMED  NEW DEPLOYMENTS FROZEN — no market may be seated out of the
    #             deployment_plan until a human re-arms.  Existing seats keep
    #             their FULL shield: reactive cancel, atomic re-placement and
    #             the hourly preemptive timer all continue.  This is what an
    #             automatic fill-halt sets.  The filled market itself is stopped
    #             by its own scoped locks (terminal plan rows + the family-wide
    #             post-fill re-entry ban), NOT by this state.
    #   HALTED    GLOBAL FREEZE — nothing places, not even maintenance of a seat
    #             we already hold.  Cancels are never blocked by any state.
    #             For a SYSTEM-level fault (bad venue data, a broken invariant,
    #             a human pulling the plug), never for a market-level event: a
    #             fill in one market is information about that market only.
    PLACEMENT_STATES = ("ARMED", "DISARMED", "HALTED")

    def get_placement_state(self) -> Dict[str, Any]:
        """Current placement state. Append-only ledger; latest row wins.

        If the table is empty the default DISARMED row is written first, so a
        fresh database can never report an ambiguous/absent placement state.
        """
        with self.db.get_connection() as conn:
            row = conn.execute(
                "SELECT state, reason, set_by, set_at FROM placement_state ORDER BY id DESC LIMIT 1"
            ).fetchone()
            if row is None:
                conn.execute(
                    "INSERT INTO placement_state (state, reason, set_by) VALUES (?, ?, ?)",
                    (
                        DEFAULT_PLACEMENT_STATE["state"],
                        DEFAULT_PLACEMENT_STATE["reason"],
                        DEFAULT_PLACEMENT_STATE["set_by"],
                    ),
                )
                conn.commit()
                row = conn.execute(
                    "SELECT state, reason, set_by, set_at FROM placement_state ORDER BY id DESC LIMIT 1"
                ).fetchone()
            return dict(row)

    def set_placement_state(self, state: str, reason: str, set_by: str) -> Dict[str, Any]:
        """Flip the placement state machine. Appends (never overwrites) so the
        full arm/disarm history stays queryable.

        See PLACEMENT_STATES above for the SCOPE of each state — DISARMED
        freezes new deployments only; HALTED is the global freeze."""
        state = state.upper()
        if state not in self.PLACEMENT_STATES:
            raise ValueError(
                f"Invalid placement state '{state}': must be one of "
                f"{', '.join(self.PLACEMENT_STATES)}.")
        if not reason or not reason.strip():
            raise ValueError("A placement state flip requires a non-empty reason.")
        if not set_by or not set_by.strip():
            raise ValueError("A placement state flip requires set_by (who authorized it).")
        with self.db.get_connection() as conn:
            conn.execute(
                "INSERT INTO placement_state (state, reason, set_by) VALUES (?, ?, ?)",
                (state, reason.strip(), set_by.strip()),
            )
            conn.commit()
        return self.get_placement_state()

    def placement_state_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self.db.get_connection() as conn:
            rows = conn.execute(
                "SELECT state, reason, set_by, set_at FROM placement_state ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    # --- Active Orders ---
    def save_order(self, order: ActiveOrder) -> None:
        with self.db.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO active_orders (order_id, ticker, side, price, count, collateral_usd, status, lane, placed_at, updated_at, program_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(order_id) DO UPDATE SET
                    ticker = excluded.ticker,
                    side = excluded.side,
                    price = excluded.price,
                    count = excluded.count,
                    collateral_usd = excluded.collateral_usd,
                    status = excluded.status,
                    lane = excluded.lane,
                    updated_at = excluded.updated_at,
                    -- ATTRIBUTION-1: a later write that does not know the program
                    -- id (venue adoption, reconciler mirror) must NEVER erase one
                    -- we captured at placement.  COALESCE keeps the known value.
                    program_id = COALESCE(excluded.program_id, active_orders.program_id)
                """,
                (
                    order.order_id,
                    order.ticker,
                    order.side,
                    order.price,
                    order.count,
                    order.collateral_usd,
                    order.status,
                    order.lane,
                    order.placed_at,
                    order.updated_at,
                    order.program_id,
                ),
            )
            conn.commit()

    def list_active_orders(self) -> List[ActiveOrder]:
        with self.db.get_connection() as conn:
            cur = conn.execute("SELECT order_id, ticker, side, price, count, collateral_usd, status, lane, placed_at, updated_at FROM active_orders WHERE status = 'RESTING'")
            return [ActiveOrder(**dict(row)) for row in cur.fetchall()]

    def order_history(self, tickers: List[str]) -> List[ActiveOrder]:
        """Every mirror row for `tickers`, ANY status, oldest first.
        TENURE-1 (2026-09-11): rotation reads this to find where the CURRENT
        holding of a market began, so a re-seeded market is judged on its own
        tenure and not on the gap before it."""
        tks = [str(t) for t in tickers]
        if not tks:
            return []
        q = ",".join("?" * len(tks))
        with self.db.get_connection() as conn:
            cur = conn.execute(
                "SELECT order_id, ticker, side, price, count, collateral_usd, status, lane, "
                f"placed_at, updated_at FROM active_orders WHERE ticker IN ({q}) "
                "ORDER BY placed_at", tks)
            return [ActiveOrder(**dict(row)) for row in cur.fetchall()]

    def get_order(self, order_id: str) -> Optional[ActiveOrder]:
        """One mirror row by order id, ANY status (None if never written).
        VR-6 (2026-09-05): the venue reconciler reads this before an upsert
        so a row's existing lane and placed_at survive a sync-orders pass
        (cli.py used to overwrite 'deployment_plan' with 'general'), and so
        a FILLED receipt is never overwritten by a live listing."""
        with self.db.get_connection() as conn:
            row = conn.execute(
                "SELECT order_id, ticker, side, price, count, collateral_usd, status, "
                "lane, placed_at, updated_at FROM active_orders WHERE order_id = ?",
                (str(order_id),)).fetchone()
            return ActiveOrder(**dict(row)) if row else None

    def list_order_ids(self) -> List[str]:
        """Every order id the mirror has EVER held, any status.  CAP-2
        (2026-09-05): the defensive sweep matches venue fills against this
        so a fill on an order whose mirror was already reconciled to
        CANCELLED/GONE_FROM_VENUE (the orphan shape) is still recognised as
        ours."""
        with self.db.get_connection() as conn:
            cur = conn.execute("SELECT order_id FROM active_orders")
            return [str(row[0]) for row in cur.fetchall() if row[0]]

    def list_order_ids_by_lane(self, lane: str) -> List[str]:
        """Every mirror order id ever written under `lane`, any status.
        FLAT-7 (2026-09-05): the fills sweep asks this for lane='flatten' so
        a fill on one of our closes is read as the position LEAVING (stamp
        flattened_at) and never as a sweep to halt on or an orphan to
        re-mint as a 'filled' row."""
        with self.db.get_connection() as conn:
            cur = conn.execute("SELECT order_id FROM active_orders WHERE lane = ?", (str(lane),))
            return [str(row[0]) for row in cur.fetchall() if row[0]]

    def mark_order_status(self, order_id: str, status: str) -> None:
        with self.db.get_connection() as conn:
            conn.execute(
                "UPDATE active_orders SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE order_id = ?",
                (status, order_id),
            )
            conn.commit()

    def revive_order_status(self, order_id: str) -> bool:
        """VR-2 RE-LINK (2026-09-05).  The venue lists an order whose local
        mirror had already been retired to CANCELLED / GONE_FROM_VENUE by a
        reconcile that believed one missing open-orders read.  Venue truth
        wins in BOTH directions: put the mirror back to RESTING so the
        exposure gate (verify/invariants sums RESTING collateral) counts the
        live escrow again.  Guarded to those two cause-neutral / reconcile
        statuses — a FILLED mirror is a receipt and is never revived.
        Returns True iff a row actually moved."""
        with self.db.get_connection() as conn:
            cur = conn.execute(
                "UPDATE active_orders SET status = 'RESTING', venue_miss_count = 0, "
                "updated_at = CURRENT_TIMESTAMP "
                "WHERE order_id = ? AND status IN ('CANCELLED', 'GONE_FROM_VENUE')",
                (str(order_id),),
            )
            conn.commit()
            return cur.rowcount > 0

    # ------------------------------------------------------------------
    # VR-0 (2026-09-05): THE MIRROR'S TWO-STRIKE COUNTER.  The plan row has
    # had venue_miss_count since VR-2; the mirror retired on ONE miss.  The
    # reconciler now strikes a RESTING mirror the venue does not list and
    # retires it only on the second consecutive miss; a sighting resets it.
    # ------------------------------------------------------------------
    def bump_order_miss(self, order_id: str) -> int:
        """Add one strike to a RESTING mirror; return the new count (0 if the
        row is not RESTING -- a retired or filled row takes no strikes)."""
        with self.db.get_connection() as conn:
            conn.execute(
                "UPDATE active_orders SET venue_miss_count = venue_miss_count + 1, "
                "updated_at = CURRENT_TIMESTAMP WHERE order_id = ? AND status = 'RESTING'",
                (str(order_id),))
            row = conn.execute(
                "SELECT venue_miss_count FROM active_orders WHERE order_id = ? AND status = 'RESTING'",
                (str(order_id),)).fetchone()
            conn.commit()
            return int(row[0]) if row else 0

    def reset_order_miss(self, order_id: str) -> bool:
        """A sighting: the venue lists the order, so a prior miss was listing
        lag.  Returns True iff a non-zero count was cleared."""
        with self.db.get_connection() as conn:
            cur = conn.execute(
                "UPDATE active_orders SET venue_miss_count = 0, updated_at = CURRENT_TIMESTAMP "
                "WHERE order_id = ? AND venue_miss_count > 0", (str(order_id),))
            conn.commit()
            return cur.rowcount > 0

    def order_miss_counts(self) -> Dict[str, int]:
        """{order_id: venue_miss_count} for every RESTING mirror row."""
        with self.db.get_connection() as conn:
            cur = conn.execute(
                "SELECT order_id, venue_miss_count FROM active_orders WHERE status = 'RESTING'")
            return {str(r[0]): int(r[1] or 0) for r in cur.fetchall()}

    def restore_resting_order(self, order_id: str) -> bool:
        """VR-5 (2026-09-05): the reconciler's name for the revive.  When the
        venue lists an order whose mirror was retired to CANCELLED /
        GONE_FROM_VENUE on a missing read, put it back to RESTING so the
        exposure sums (verify/invariants total + per-market caps, the
        requalifier's 'book full' supply, the rotation engine) count the
        live escrow again.  clear_resting_order() is no longer a one-way
        door: this is its inverse.  Same guard as revive_order_status --
        a FILLED mirror is a receipt and never comes back."""
        return self.revive_order_status(order_id)

    def clear_resting_order(self, order_id: str) -> bool:
        """GHOST-ROW ANTIDOTE (ratified 2026-08-31, kalshi.ops.known_traps).

        Move a locally-RESTING active_orders row to GONE_FROM_VENUE — the
        cause-neutral retirement used when the venue no longer lists the order
        but we cannot prove WHY (fill vs cancel).  Guarded on status='RESTING'
        so it never overwrites a more precise terminal status (CANCELLED,
        FILLED) written by the path that actually knew the cause — the same
        guard pattern as the record_observed_fill fill-path fix.  Returns True
        iff a row actually moved.  Ghost RESTING rows inflate the exposure
        gate (verify/invariants sums RESTING collateral) and silently starve
        seeding; ~10 of them from Friday's cancel paths blocked a rotation.

        VR-5 (2026-09-05): ONLY THE RECONCILER CALLS THIS
        (harness/venue_reconciler.reconcile -- VR-6 made it the ONE
        reconciler for the daemon and sync-orders alike -- behind the
        10-min grace and the mass-vanish guard).  The queue shield used to call it too, on
        every 60s seat poll, on a SINGLE missing read, with no grace -- and
        because nothing restored RESTING when the order reappeared, one
        transient miss permanently dropped a live order out of every
        exposure sum (KXUST10AM 01a069d1: live 17h as an untracked orphan).
        The shield is now a pure reader of venue truth; see
        QueueShieldMonitor._hint_order_mirror_gone."""
        with self.db.get_connection() as conn:
            cur = conn.execute(
                "UPDATE active_orders SET status = 'GONE_FROM_VENUE', "
                "updated_at = CURRENT_TIMESTAMP "
                "WHERE order_id = ? AND status = 'RESTING'",
                (order_id,),
            )
            conn.commit()
            return cur.rowcount > 0

    # --- Deployment Plan (the placement engine's marching orders) ---
    #
    # THREE kinds of exit, and the difference between them is the whole
    # queue-shield/stand-down design:
    #
    #   'withdrawn_rearmed'  the shield pulled us on CANCEL-driven erosion —
    #                        rivals requoting.  Benign.  RE-PLACEABLE once
    #                        protection rebuilds (duty_cycle.replace_guard).
    #   'stood_down'         the shield pulled us because the level was being
    #                        CONSUMED by real aggressors, or because we could
    #                        not tell (trade feed unhealthy → fail closed).
    #                        NOT terminal, but NOT re-placeable: re-placing
    #                        feeds us back in with fresh armour.  Only an
    #                        explicit re-qualification returns it to service.
    #   TERMINAL_STATUSES    filled / exited / cancelled.  Never come back.
    #
    # REPLACEABLE_STATUSES is the query the placement engine actually runs, so
    # keeping 'stood_down' out of it is what makes the state mean anything.
    PLAN_STATUSES = ("pending", "resting", "filled", "exited", "cancelled",
                     "withdrawn_rearmed", "stood_down")
    TERMINAL_STATUSES = ("filled", "exited", "cancelled")
    REPLACEABLE_STATUSES = ("pending", "withdrawn_rearmed")
    # Non-terminal but non-re-placeable.  Named so that a future status cannot
    # be added to PLAN_STATUSES and silently become re-placeable by omission.
    FROZEN_STATUSES = ("stood_down",)
    # columns the duty-cycle ledger is allowed to write (whitelist, not **kwargs)
    PLAN_LEDGER_COLUMNS = (
        "withdraw_reason", "withdrawn_at", "withdraw_shield_frac",
        "a0_baseline", "a0_current", "last_placed_at",
        "uptime_s", "downtime_s", "replace_count",
        "replaces_utc_date", "replaces_today",
        "erosion_trade_ct", "erosion_cancel_ct", "erosion_unclassified_ct",
        "stood_down_at",
        "venue_miss_count",   # VR-2 (2026-09-05) two-strike reconcile
        # FLAT-3 (2026-09-05): what a fill ACTUALLY left and when it stopped
        # existing.  See Database.DEPLOYMENT_PLAN_ADDED_COLUMNS for the receipt.
        "filled_ct", "filled_cost_usd", "flattened_at", "flatten_order_id",
    )

    # --- PRICING RULE (price-at-the-placement-instant, 2026-08-18) ---
    #
    # 'fixed' is the DEFAULT and is the pre-existing behaviour exactly: the
    # pinned price_cents/count are used verbatim.  'derive' means the level and
    # the size are computed at the placement instant off the fresh book (see
    # harness/price_derivation.py), and the row NEVER falls back to its seed
    # price.  ALTER TABLE ADD COLUMN cannot carry a CHECK constraint onto an
    # existing table, so this tuple is the enforcement point for migrated DBs.
    PLAN_PRICE_MODES = ("fixed", "derive")
    PLAN_RULE_COLUMNS = ("price_mode", "max_capital_usd", "band_lo_c",
                         "band_hi_c", "min_armor_ct", "max_seat_share")

    @staticmethod
    def refuse_plan_row_above_cap(max_escrow_usd: Optional[float],
                                  max_capital_usd: Optional[float],
                                  what: str = "plan row") -> None:
        """THE $25 BOUND AT THE POINT OF INTENT (CAP-3, 2026-09-05).

        Ryan, verbatim: "never to have more than 25$ in any market".  Until
        today this store accepted ANY max_escrow_usd / max_capital_usd: the
        pilot seed carried $49.94 and $50.00 rows and re-upserted them on
        every `spinup.py` boot and `./kalshi.py seed`; the re-seed-over-
        terminal branch below flipped an exited/cancelled row back to
        'pending' with whatever number the caller sent; `price-rule
        --max-capital` was unbounded; and the engine's plan_cap was
        min(50, row) — so a $50 row flowed through a check that allowed $50.
        That is the exact shape of the $50 KXKR-26SEPIDSALES-1.5 seat that
        was seeded at 07:24Z and swept at 14:30Z (every one of the 25
        lifetime fills is an informed sweep of a dead ladder; a fill at $50
        loses ~2x).  The engine now clamps to the compiled ceiling too, but a
        row the system will never honour must not exist as intent: a
        $30 'pending' row is a standing lie about what the book will hold.
        Refuse it HERE, at write time, with the one compiled number.  Facts
        may only tighten this ceiling (verify/caps.py); nothing may loosen it.
        """
        for name, val in (("max_escrow_usd", max_escrow_usd),
                          ("max_capital_usd", max_capital_usd)):
            if val is None:
                continue
            if float(val) > PER_MARKET_HARD_USD + 0.005:
                raise ValueError(
                    f"{what} {name}=${float(val):.2f} exceeds the "
                    f"${PER_MARKET_HARD_USD:.2f}/market ceiling — Ryan: \"never to "
                    f"have more than 25$ in any market\" (CAP-3, 2026-09-05). "
                    f"Refused at write time; a row the engine will never place "
                    f"is not intent.")

    def upsert_deployment_plan(
        self,
        ticker: str,
        side: str,
        price_cents: int,
        count: int,
        max_escrow_usd: float,
        hard_exit_utc: Optional[str] = None,
        notes: Optional[str] = None,
        price_mode: str = "fixed",
        max_capital_usd: Optional[float] = None,
        band_lo_c: Optional[int] = None,
        band_hi_c: Optional[int] = None,
        min_armor_ct: Optional[float] = None,
        max_seat_share: Optional[float] = None,
        worst_ratio: Optional[float] = None,
        receipt_of_fill: bool = False,
    ) -> None:
        """Idempotent plan seeding: (ticker, side, price_cents, count) is UNIQUE, so
        re-seeding never duplicates a row nor resets an existing row's status.

        price_cents/count remain REQUIRED even for a 'derive' row: they stay the
        UNIQUE key and the audit record of what the seeding snapshot said, and
        the derivation logs the price it actually used against them.

        max_escrow_usd / max_capital_usd above the $25 compiled ceiling are
        REFUSED (CAP-3) — see refuse_plan_row_above_cap.  The single exception
        is `receipt_of_fill=True`: the engine's orphan-fill ledger
        (_mint_orphan_fill_row) records a fill that ALREADY HAPPENED on a
        non-plan order, and a receipt of money already at risk must never be
        refused for being too large — that is precisely when the per-market
        cap and the seeder most need to see it.  A receipt row is never
        left 'pending': the caller marks it 'filled' in the same breath, and
        even if it were, the engine's plan_cap = min($25, row) refuses it.
        """
        if str(price_mode).lower() not in self.PLAN_PRICE_MODES:
            raise ValueError(f"Invalid price_mode '{price_mode}'. "
                             f"Expected one of {self.PLAN_PRICE_MODES}.")
        if not receipt_of_fill:
            self.refuse_plan_row_above_cap(max_escrow_usd, max_capital_usd,
                                           what=f"deployment_plan {ticker} {side}")
        with self.db.get_connection() as conn:
            conn.execute(
                """INSERT OR IGNORE INTO deployment_plan
                   (ticker, side, price_cents, count, max_escrow_usd, hard_exit_utc, notes,
                    price_mode, max_capital_usd, band_lo_c, band_hi_c, min_armor_ct,
                    max_seat_share, worst_ratio)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (ticker, side.lower(), int(price_cents), int(count),
                 float(max_escrow_usd), hard_exit_utc, notes,
                 str(price_mode).lower(),
                 None if max_capital_usd is None else float(max_capital_usd),
                 None if band_lo_c is None else int(band_lo_c),
                 None if band_hi_c is None else int(band_hi_c),
                 None if min_armor_ct is None else float(min_armor_ct),
                 None if max_seat_share is None else float(max_seat_share),
                 None if worst_ratio is None else float(worst_ratio)),
            )
            # RE-SEED OVER A TERMINAL ROW (2026-09-04).  The UNIQUE key made a
            # re-seed of a market at the same (side, price, count) as an
            # EXITED/CANCELLED row a silent no-op: the seeder printed "SEEDED"
            # for KXKAOHSIUNGMAYOR / KXUPASSEMBLY / KXNEWTAIPEIMAYOR (rotated
            # out 09-03, re-qualified 09-04) and no row existed, so the book
            # sat at 16/20 and nothing reported why.  A terminal row is history,
            # not intent: revive it as a fresh pending row (old notes kept).
            # 'filled' is deliberately NOT revived — a fill is a receipt.
            cur = conn.execute(
                "SELECT id, status, notes FROM deployment_plan "
                "WHERE ticker = ? AND side = ? AND price_cents = ? AND count = ?",
                (ticker, side.lower(), int(price_cents), int(count)))
            row = cur.fetchone()
            if row is not None and row["status"] in ("exited", "cancelled"):
                conn.execute(
                    """UPDATE deployment_plan SET status = 'pending', order_id = NULL,
                       notes = ?, max_escrow_usd = ?, hard_exit_utc = ?, price_mode = ?,
                       max_capital_usd = ?, band_lo_c = ?, band_hi_c = ?, min_armor_ct = ?,
                       max_seat_share = ?, withdrawn_at = NULL, withdraw_reason = NULL,
                       withdraw_shield_frac = NULL, stood_down_at = NULL, last_placed_at = NULL,
                       a0_baseline = NULL, a0_current = NULL, updated_at = CURRENT_TIMESTAMP
                       WHERE id = ?""",
                    ((notes or "") + " | re-seeded over %s row: %s" % (
                        row["status"], str(row["notes"] or "")[:80]),
                     float(max_escrow_usd), hard_exit_utc, str(price_mode).lower(),
                     None if max_capital_usd is None else float(max_capital_usd),
                     None if band_lo_c is None else int(band_lo_c),
                     None if band_hi_c is None else int(band_hi_c),
                     None if min_armor_ct is None else float(min_armor_ct),
                     None if max_seat_share is None else float(max_seat_share),
                     row["id"]))
            conn.commit()

    def set_price_rule(
        self,
        plan_id: int,
        price_mode: str,
        max_capital_usd: Optional[float] = None,
        band_lo_c: Optional[int] = None,
        band_hi_c: Optional[int] = None,
        min_armor_ct: Optional[float] = None,
        max_seat_share: Optional[float] = None,
        note: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Convert an EXISTING plan row to (or back from) a pricing rule.

        Deliberately does NOT touch status: a pending row stays pending and the
        engine picks it up on its own.  Converting to 'derive' leaves the seed
        price_cents/count in place as the audit baseline; they are overwritten
        only when a derived placement actually happens.
        """
        mode = str(price_mode).lower()
        if mode not in self.PLAN_PRICE_MODES:
            raise ValueError(f"Invalid price_mode '{price_mode}'. "
                             f"Expected one of {self.PLAN_PRICE_MODES}.")
        # CAP-3 (2026-09-05): `./kalshi.py price-rule --max-capital` was
        # unbounded; a derive row's budget is what the engine sizes FROM.
        self.refuse_plan_row_above_cap(None, max_capital_usd,
                                       what=f"price rule for plan row {plan_id}")
        if mode == "derive":
            # Deferred import: harness/ depends on state/, never the reverse at
            # import time.  price_derivation owns the canonical band defaults.
            from domains.kalshi.harness.price_derivation import (DEFAULT_BAND_HI_C,
                                                                 DEFAULT_BAND_LO_C)
            if max_capital_usd is None or float(max_capital_usd) <= 0:
                raise ValueError("A 'derive' row needs a positive max_capital_usd — "
                                 "the size is recomputed from the budget, never "
                                 "from a stale contract count.")
            lo = DEFAULT_BAND_LO_C if band_lo_c is None else int(band_lo_c)
            hi = DEFAULT_BAND_HI_C if band_hi_c is None else int(band_hi_c)
            if not (1 <= lo <= hi <= 99):
                raise ValueError(f"Nonsensical band {lo}-{hi}c.")
            if max_seat_share is not None and not (0 < float(max_seat_share) <= 1):
                raise ValueError("max_seat_share must be in (0, 1].")
            band_lo_c, band_hi_c = lo, hi
        row = self.get_deployment_plan_row(plan_id)
        if row is None:
            raise ValueError(f"deployment_plan row {plan_id} does not exist.")
        sets = ["updated_at = CURRENT_TIMESTAMP", "price_mode = ?"]
        params: List[Any] = [mode]
        for col, val in (("max_capital_usd", max_capital_usd),
                         ("band_lo_c", band_lo_c),
                         ("band_hi_c", band_hi_c),
                         ("min_armor_ct", min_armor_ct),
                         ("max_seat_share", max_seat_share)):
            sets.append(f"{col} = ?")
            params.append(None if val is None else
                          (int(val) if col in ("band_lo_c", "band_hi_c") else float(val)))
        if note:
            sets.append("notes = ?")
            params.append(((row.get("notes") or "") + " | " + note).strip(" |"))
        params.append(plan_id)
        with self.db.get_connection() as conn:
            conn.execute(
                f"UPDATE deployment_plan SET {', '.join(sets)} WHERE id = ?", params)
            conn.commit()
        return self.get_deployment_plan_row(plan_id)

    def set_placed_price(self, plan_id: int, price_cents: int, count: int) -> bool:
        """Record what a DERIVED row actually placed at.

        Everything downstream of placement — the queue shield's level, A0
        re-baselining, the duty-cycle ledger, the atomic replace — reads
        price_cents/count off the plan row.  A derived seat that left those at
        their seed values would be shielded at a level it is not resting on, so
        the derived price becomes the row's price at the moment it is placed.

        Returns False (without raising) if the write would collide with the
        UNIQUE(ticker, side, price_cents, count) key — the row is still
        identified by its order_id and the caller logs the collision.
        """
        if not (1 <= int(price_cents) <= 99) or int(count) <= 0:
            raise ValueError(f"Refusing to record placed price {price_cents}c x{count}.")
        try:
            with self.db.get_connection() as conn:
                conn.execute(
                    "UPDATE deployment_plan SET price_cents = ?, count = ?, "
                    "updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (int(price_cents), int(count), plan_id),
                )
                conn.commit()
        except sqlite3.IntegrityError:
            return False
        return True

    PLAN_COLUMNS = (
        "id, ticker, side, price_cents, count, max_escrow_usd, hard_exit_utc, "
        "status, order_id, notes, created_at, updated_at, "
        "withdraw_reason, withdrawn_at, withdraw_shield_frac, a0_baseline, "
        "a0_current, last_placed_at, uptime_s, downtime_s, replace_count, "
        "replaces_utc_date, replaces_today, "
        "erosion_trade_ct, erosion_cancel_ct, erosion_unclassified_ct, "
        "stood_down_at, "
        "price_mode, max_capital_usd, band_lo_c, band_hi_c, min_armor_ct, "
        "max_seat_share, venue_miss_count, "
        "filled_ct, filled_cost_usd, flattened_at, flatten_order_id"
    )

    def list_deployment_plan(self, statuses: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        query = f"SELECT {self.PLAN_COLUMNS} FROM deployment_plan"
        params: List[Any] = []
        if statuses:
            query += f" WHERE status IN ({','.join('?' * len(statuses))})"
            params.extend(statuses)
        query += " ORDER BY id ASC"
        with self.db.get_connection() as conn:
            return [dict(r) for r in conn.execute(query, params).fetchall()]

    def update_deployment_plan(
        self,
        plan_id: int,
        status: Optional[str] = None,
        order_id: Optional[str] = None,
        notes: Optional[str] = None,
        ledger: Optional[Dict[str, Any]] = None,
    ) -> None:
        if status is not None and status not in self.PLAN_STATUSES:
            raise ValueError(f"Invalid deployment_plan status '{status}'.")
        sets, params = ["updated_at = CURRENT_TIMESTAMP"], []
        for col, val in (("status", status), ("order_id", order_id), ("notes", notes)):
            if val is not None:
                sets.append(f"{col} = ?")
                params.append(val)
        for col, val in (ledger or {}).items():
            if col not in self.PLAN_LEDGER_COLUMNS:
                raise ValueError(f"Column '{col}' is not a deployment_plan ledger column.")
            sets.append(f"{col} = ?")
            params.append(val)
        params.append(plan_id)
        with self.db.get_connection() as conn:
            conn.execute(f"UPDATE deployment_plan SET {', '.join(sets)} WHERE id = ?", params)
            conn.commit()

    def get_deployment_plan_row(self, plan_id: int) -> Optional[Dict[str, Any]]:
        with self.db.get_connection() as conn:
            row = conn.execute(
                f"SELECT {self.PLAN_COLUMNS} FROM deployment_plan WHERE id = ?", (plan_id,)
            ).fetchone()
            return dict(row) if row else None

    def find_plan_by_order_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Locate the plan row that owns a venue order id (the queue shield only
        knows order ids; the duty-cycle ledger is keyed on plan rows)."""
        with self.db.get_connection() as conn:
            row = conn.execute(
                f"SELECT {self.PLAN_COLUMNS} FROM deployment_plan WHERE order_id = ? "
                "ORDER BY id DESC LIMIT 1", (str(order_id),)
            ).fetchone()
            return dict(row) if row else None

    def record_observed_fill(self, fill_id: str, order_id: Optional[str], ticker: Optional[str],
                             observed_at: Optional[str] = None,
                             count_ct: Optional[float] = None,
                             price_cents: Optional[int] = None,
                             held_side: Optional[str] = None,
                             client_order_id: Optional[str] = None) -> bool:
        """Record a venue fill id; returns True only the FIRST time it is seen.

        observed_at is written explicitly when the caller has an injected clock,
        so the post-fill re-entry ban measures against the same clock the rest of
        the engine uses instead of SQLite's CURRENT_TIMESTAMP.

        FLAT-3 (2026-09-05): count_ct / price_cents / held_side / client_order_id
        are the venue fill's OWN numbers.  Before today the receipt discarded
        them, so after 25 informed sweeps the pod could not say from local
        state how many contracts it held in any ticker, at what cost, on which
        side -- and a flatten could not size itself.  Unparseable values are
        stored as NULL ("unrecorded"), never coerced to 0 ("flat")."""
        cnt = _float_or_none(count_ct)
        px = _int_or_none(price_cents)
        side = str(held_side).lower() if held_side in ("yes", "no", "YES", "NO") else None
        coid = None if client_order_id in (None, "") else str(client_order_id)
        with self.db.get_connection() as conn:
            if observed_at is None:
                cur = conn.execute(
                    "INSERT OR IGNORE INTO observed_fills "
                    "(fill_id, order_id, ticker, count_ct, price_cents, held_side, client_order_id) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (fill_id, order_id, ticker, cnt, px, side, coid),
                )
            else:
                cur = conn.execute(
                    "INSERT OR IGNORE INTO observed_fills "
                    "(fill_id, order_id, ticker, observed_at, count_ct, price_cents, held_side, "
                    "client_order_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (fill_id, order_id, ticker, observed_at, cnt, px, side, coid),
                )
            first_time = cur.rowcount > 0
            # GHOST COLLATERAL FIX (2026-08-26, merged from the VPS tree
            # 2026-08-31).  A fill removes the order from the venue, but nothing
            # here ever retired the active_orders row, so it stayed 'RESTING'
            # forever and verify/invariants kept summing its collateral as live
            # exposure.  MEASURED COST: $74.71 of phantom escrow on 2026-08-26
            # (3 dead rows) put the exposure gate at $546.97 against the $530
            # cap and locked a real seat out of the book for hours.  Every fill
            # minted a fresh ghost until this landed.  Same transaction as the
            # fill insert so the two can never disagree; gated on first_time so
            # a re-observed fill cannot retire a row legitimately re-placed
            # since; the status='RESTING' predicate is a no-op against any row
            # the shield already moved on.  The CANCEL-side twin of this fix is
            # clear_resting_order() above (kalshi-6b, 2026-08-31).
            if first_time and order_id:
                conn.execute(
                    "UPDATE active_orders SET status = 'FILLED', "
                    "updated_at = CURRENT_TIMESTAMP "
                    "WHERE order_id = ? AND status = 'RESTING'",
                    (str(order_id),),
                )
            conn.commit()
            return first_time

    def delete_observed_fill(self, fill_id: str) -> bool:
        """VR-3 (2026-09-05): retire a SYNTHETIC receipt (fill id `fp:<order>`,
        minted from the open-orders fill_count_fp signal) once the fills feed
        delivers the venue's own row for that order, so one sweep is counted
        once.  Only the synthetic prefix is deletable: a venue fill id is a
        paid-for receipt and stays."""
        if not str(fill_id).startswith("fp:"):
            return False
        with self.db.get_connection() as conn:
            cur = conn.execute("DELETE FROM observed_fills WHERE fill_id = ?", (str(fill_id),))
            conn.commit()
            return cur.rowcount > 0

    def list_observed_fills(self, ticker_prefix: Optional[str] = None) -> List[Dict[str, Any]]:
        """Observed fills, newest first.  ticker_prefix matches the series family."""
        query = ("SELECT fill_id, order_id, ticker, observed_at, count_ct, price_cents, "
                 "held_side, client_order_id FROM observed_fills")
        params: List[Any] = []
        if ticker_prefix:
            query += " WHERE ticker LIKE ?"
            params.append(f"{ticker_prefix}%")
        query += " ORDER BY observed_at DESC"
        with self.db.get_connection() as conn:
            return [dict(r) for r in conn.execute(query, params).fetchall()]

    # --- FLAT-3 (2026-09-05): the position a fill left, and its end -------
    #
    # PAID-FOR LESSON.  25 lifetime fills, every one an informed sweep of a
    # dead ladder; every one left an open position; not one was ever
    # flattened (KXSNOWCRABCATCH from 09-03 is still open, a $50 KXKR seat
    # joined it today).  The ledger had a 'filled' status and nothing after
    # it: no count of what was filled, no record of the position ending, so
    # (a) a partial fill was booked as the whole order, (b) the per-market
    # cap held the ticker "full" forever, even after settlement, and (c) the
    # only position number in the pod was the venue's aggregate mark.  The
    # plan row stays 'filled' -- it is the receipt of the sweep, and the
    # post-fill family ban keys off observed_fills, not off this -- but it
    # now says how much was filled and, once the position is gone, when.
    #
    # SIZING RULE.  A flatten is sized from the venue's LIVE position
    # (KalshiVenueClient.fetch_position), never from these columns: they are
    # the local record, the venue is the truth, and over-selling a position
    # is an acquire wearing a close's exemptions.

    def list_open_positions(self) -> List[Dict[str, Any]]:
        """'filled' plan rows whose position has not been flattened/settled,
        i.e. the pod's local view of what it still HOLDS, per ticker."""
        with self.db.get_connection() as conn:
            rows = conn.execute(
                f"SELECT {self.PLAN_COLUMNS} FROM deployment_plan "
                "WHERE status = 'filled' AND flattened_at IS NULL ORDER BY id ASC"
            ).fetchall()
            return [dict(r) for r in rows]

    def mark_plan_flattened(self, ticker: str, at_iso: str,
                            flatten_order_id: Optional[str] = None,
                            note: Optional[str] = None) -> int:
        """Stamp every un-flattened 'filled' row of `ticker` as flattened at
        `at_iso` (position sold or settled).  Idempotent: rows already stamped
        are left alone so the first flatten time survives.  Returns the number
        of rows stamped.  Status is NOT changed -- 'filled' is the receipt."""
        with self.db.get_connection() as conn:
            cur = conn.execute(
                "UPDATE deployment_plan SET flattened_at = ?, flatten_order_id = ?, "
                "notes = COALESCE(notes, '') || ?, updated_at = CURRENT_TIMESTAMP "
                "WHERE ticker = ? AND status = 'filled' AND flattened_at IS NULL",
                (str(at_iso), None if flatten_order_id is None else str(flatten_order_id),
                 f" | [{at_iso}] position FLATTENED"
                 + (f" via {flatten_order_id}" if flatten_order_id else "")
                 + (f": {note}" if note else ""),
                 str(ticker)))
            conn.commit()
            return int(cur.rowcount or 0)

    def record_incident(self, mistake_id: str, name: str, description: str,
                        enforced_by: str, verification_test: str,
                        status: str = "COMPILED_IMPOSSIBLE") -> None:
        """Mistakes-style incident row (idempotent on mistake_id).

        status: COMPILED_IMPOSSIBLE when code makes the mistake impossible;
        REGRESSION_TESTED when the guard is a prompt rule + lint regex (M6).
        """
        if status not in ("COMPILED_IMPOSSIBLE", "REGRESSION_TESTED"):
            raise ValueError(f"mistake_invariants.status must be COMPILED_IMPOSSIBLE or "
                             f"REGRESSION_TESTED, got {status!r}")
        with self.db.get_connection() as conn:
            conn.execute(
                """INSERT OR IGNORE INTO mistake_invariants
                   (mistake_id, name, incident_description, enforced_by_module, verification_test, status)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (mistake_id, name, description, enforced_by, verification_test, status),
            )
            conn.commit()

    # MT-8 (2026-09-09): the ledger row is the lesson, and the lesson MOVES.
    # record_mistake was INSERT OR IGNORE on `name`, so the FIRST ratify won
    # forever: a mistake whose guard was later compiled into code kept the
    # prevention text from the day it was still a prompt rule, and re-running
    # the ratify script silently changed nothing.  A ledger that cannot be
    # corrected is a ledger that lies.  This is now an UPSERT -- but a
    # RATCHET, never a rewrite of history:
    #   receipt / prevention  -- always refreshed (that is the point)
    #   prevention_effort_h   -- refreshed only when a value is supplied
    #   loss_usd              -- monotone: a paid loss never shrinks
    #   status                -- monotone up the ladder OPEN < MITIGATED <
    #                            IMPOSSIBLE, so a caller relying on the
    #                            "MITIGATED" default can never DOWNGRADE a
    #                            mistake that code has since made impossible
    # Still idempotent on `name` (UNIQUE): a ratify path may run on every boot
    # and the ledger never grows a duplicate.
    _STATUS_RANK = {"OPEN": 1, "MITIGATED": 2, "IMPOSSIBLE": 3}

    def record_mistake(self, name: str, receipt: str, prevention: str,
                       loss_usd: float = 0.0, status: str = "MITIGATED",
                       prevention_effort_h: Optional[float] = None) -> None:
        """MT-4 (2026-09-09): one paid-for lesson in the mistakes ledger.

        Writes the LIVE VPS column set (id, name, loss_usd, status, receipt,
        prevention, prevention_effort_h, updated_at) and nothing else.
        Upserts on `name` (MT-8): re-running a ratify script CORRECTS the
        lesson text in place instead of being ignored, while loss_usd and
        status only ever ratchet upward.
        """
        if status not in self._STATUS_RANK:
            raise ValueError("mistakes.status must be one of %s, got %r"
                             % (sorted(self._STATUS_RANK), status))
        with self.db.get_connection() as conn:
            conn.execute(
                """INSERT INTO mistakes
                   (name, loss_usd, status, receipt, prevention, prevention_effort_h, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(name) DO UPDATE SET
                     receipt   = excluded.receipt,
                     prevention = excluded.prevention,
                     prevention_effort_h =
                       coalesce(excluded.prevention_effort_h, mistakes.prevention_effort_h),
                     loss_usd  = max(coalesce(mistakes.loss_usd, 0.0),
                                     coalesce(excluded.loss_usd, 0.0)),
                     status    = CASE WHEN
                       (CASE excluded.status WHEN 'IMPOSSIBLE' THEN 3
                                             WHEN 'MITIGATED'  THEN 2 ELSE 1 END) >=
                       (CASE mistakes.status WHEN 'IMPOSSIBLE' THEN 3
                                             WHEN 'MITIGATED'  THEN 2 ELSE 1 END)
                       THEN excluded.status ELSE mistakes.status END,
                     updated_at = excluded.updated_at""",
                (str(name), float(loss_usd), str(status), str(receipt), str(prevention),
                 None if prevention_effort_h is None else float(prevention_effort_h),
                 _utc_now_iso()),
            )
            conn.commit()

    def list_mistakes(self) -> List[Dict[str, Any]]:
        with self.db.get_connection() as conn:
            cur = conn.execute(
                "SELECT id, name, loss_usd, status, receipt, prevention, prevention_effort_h, "
                "updated_at FROM mistakes ORDER BY id")
            return [dict(r) for r in cur.fetchall()]

    def get_mistake(self, name: str) -> Optional[Dict[str, Any]]:
        with self.db.get_connection() as conn:
            row = conn.execute(
                "SELECT id, name, loss_usd, status, receipt, prevention, prevention_effort_h, "
                "updated_at FROM mistakes WHERE name = ?", (str(name),)).fetchone()
            return dict(row) if row else None

