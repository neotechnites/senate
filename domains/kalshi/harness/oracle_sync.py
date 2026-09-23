"""Authentic Oracle balance synchronization for Kalshi Domain Pod.

INVARIANT: ZERO HAND-AUTHORED / DROP-FILE INGESTION.
Money state originates strictly from the live authenticated Kalshi Venue API (`live_client.fetch_balance()`).
No local drop-files or intermediate human-editable files are permitted.

MT-1 (2026-09-09): LIFETIME P&L IS account_value - deposits + withdrawals, OR IT IS
UNKNOWN.  The status printed "Cash: $966.10 | Positions: $14.52 | P&L: $+14.52" and
the Domain Head reported +$14.52 as the account's P&L; truth was $2,600 deposited
(13 deposits), account value ~$981, lifetime P&L ~-$1,619.  The cause was one line
here: `deposits_usd = raw_bal.get("lifetime_deposits", cents_bal)` -- the balance
endpoint has no such key, so deposits defaulted to the cash balance and "P&L"
collapsed to the positions mark.  Deposits now come ONLY from the paged
/portfolio/deposits ledger (venue_client.fetch_deposits); when that ledger cannot
be read the fact carries lifetime_pnl_usd=None with a pnl_note saying why, and every
renderer prints UNKNOWN.  No key on the balance response may ever stand in for it.
"""

from datetime import datetime, timezone
from typing import Any, List, Optional, Tuple

from domains.kalshi.harness.positions import positions_cost_total_usd
from domains.kalshi.harness.venue_client import (KalshiVenueClient,
                                                 call_with_rate_limit_retry,
                                                 rate_limit_note)
from domains.kalshi.state.fact_store import FactStore
from domains.kalshi.state.models import Fact


LEDGER_AMOUNT_KEYS = ("amount_dollars", "amount_cents", "amount")

# M5 (2026-09-09): a deposit row that never landed (pending / failed /
# cancelled / reversed) is not a deposit.  A row with NO status key is
# counted (the reference oracle.py read 13 rows with no status filter and
# reconciled to Ryan's $2,600); a row WITH a status outside this set is
# skipped and the skip is reported in deposits_source.
# MT-7 (2026-09-09, live read): Kalshi's own status for a landed deposit is
# "applied" -- the guard above, written from a guessed vocabulary, skipped all
# 13 of Ryan's deposits and printed "Deposits=UNKNOWN (13 skipped: applied)".
# The venue's word is the authority; a status vocabulary invented in this file
# is a hypothesis until a live row confirms it.
LEDGER_ACCEPTED_STATUSES = frozenset(
    {"applied", "completed", "complete", "settled", "succeeded", "success",
     "successful", "confirmed", "credited", "approved", "done"})


def ledger_amount_usd(row: Any) -> float:
    """Dollar amount of one deposit/withdrawal row, from the FIRST present key.

    `amount_dollars` is a dollar figure whether string or number (strings
    since the 2026-08 API migration); `amount_cents` and bare `amount` are
    CENTS whether string or number (M5: a string "260000" under amount_cents
    is $2,600, not $260,000).  A row with none of the keys is UNREADABLE and
    raises -- a silent 0 would understate deposits and overstate P&L, the
    one direction that is forbidden.
    """
    if not isinstance(row, dict):
        raise ValueError(f"ledger row is not a mapping: {row!r}")
    for k in LEDGER_AMOUNT_KEYS:
        v = row.get(k)
        if v is None:
            continue
        if k.endswith("_dollars"):
            return float(v)
        return float(v) / 100.0
    raise ValueError(f"ledger row carries none of {LEDGER_AMOUNT_KEYS}: {row!r}")


def ledger_row_accepted(row: Any) -> bool:
    """False only for a row whose `status` is present and not a landed state."""
    st = row.get("status") if isinstance(row, dict) else None
    if st is None or str(st).strip() == "":
        return True
    return str(st).strip().lower() in LEDGER_ACCEPTED_STATUSES


def ledger_total_usd(rows: Any) -> Tuple[float, int, List[str]]:
    """(total_usd, n_counted, skipped_statuses) over a deposits/withdrawals page set."""
    total = 0.0
    counted = 0
    skipped: List[str] = []
    for r in list(rows or []):
        if not ledger_row_accepted(r):
            skipped.append(str(r.get("status")))
            continue
        total += ledger_amount_usd(r)
        counted += 1
    return round(total, 2), counted, skipped


def ledger_source_note(endpoint: str, n_rows: int, skipped: List[str]) -> str:
    note = f"live /portfolio/{endpoint} ({n_rows} rows"
    if skipped:
        note += f", {len(skipped)} skipped: {', '.join(sorted(set(skipped)))}"
    return note + ")"


def sync_kalshi_oracle(
    store: FactStore,
    live_client: Optional[KalshiVenueClient] = None,
    max_age_hours: float = 24.0,
    sleep_fn: Any = None,
) -> Tuple[bool, str, Optional[Fact]]:
    """Synchronize live venue balance directly from authenticated Kalshi API into FactStore."""
    if live_client is None:
        return False, "No live venue balance fetched; configure KALSHI_API_KEY and run './kalshi.py sync-oracle --live'", None

    try:
        # A 429 from our own research lanes is contention, not a broken balance
        # endpoint: retry it promptly in-cycle, and if it survives the retries
        # say RATE-LIMITED rather than reporting it as a venue fetch failure.
        # The oracle still fails closed — a stale balance is never invented.
        kw = {} if sleep_fn is None else {"sleep_fn": sleep_fn}
        res = call_with_rate_limit_retry(live_client.fetch_balance, **kw)
        if not res["ok"]:
            return False, f"Live venue API balance fetch failed ({rate_limit_note(res)})", None
        raw_bal = res["value"]
        if not isinstance(raw_bal, dict) or "balance" not in raw_bal:
            return False, f"Live venue balance returned unexpected schema: {raw_bal}", None
        
        # Kalshi Trade API returns balance in integer cents
        cents_bal = float(raw_bal.get("balance", 0))
        # 2026-08-15 DEFECT FIX: open positions were read from a "payout" key
        # that does not exist in this response (always 0.0), so the pod
        # reported Positions: $0.00 while $199.69 of filled positions sat on
        # the book through the 08-15 incident.  The venue's mark of all open
        # positions is `portfolio_value` (cents).
        payouts_cents = float(raw_bal.get("portfolio_value",
                                          raw_bal.get("payout", 0)) or 0)
        cash_usd = round(cents_bal / 100.0, 2)
        open_pos_usd = round(payouts_cents / 100.0, 2)
        # MT-1: account value is cash + the venue's own mark of open positions.
        account_value_usd = round(cash_usd + open_pos_usd, 2)

        now_iso = datetime.now(timezone.utc).isoformat()

        # CAP-6 (2026-09-05): POSITIONS AT COST, BESIDE THE MARK.  Every
        # total-cap reader took `open_positions_usd` above — the venue's
        # `portfolio_value`, i.e. the MARK — as "positions".  All 25 lifetime
        # fills are adverse sweeps (price re-rates against us at the fill),
        # so on this book a position is always marked BELOW what was paid:
        # a $25 position marked $5 counted as $5 and freed $20 of room under
        # the total.  The positions feed reports the cost basis
        # (`market_exposure`, cents); it is written here as
        # `open_positions_cost_usd` and the readers take the larger of the
        # two (harness/positions.positions_exposure_usd).  The mark stays
        # for P&L.  A client without the endpoint, or a failed read, leaves
        # the cost None with a reason — the balance sync itself still
        # stands, and the engine's own positions read fails closed
        # independently before any placement.
        open_pos_cost_usd = None
        cost_note = "venue client exposes no fetch_positions"
        cost_unreadable = []
        fetch_pos = getattr(live_client, "fetch_positions", None)
        if callable(fetch_pos):
            try:
                pres = call_with_rate_limit_retry(fetch_pos, **kw)
                if pres["ok"]:
                    rows = list(pres["value"] or [])
                    open_pos_cost_usd, cost_unreadable = positions_cost_total_usd(rows)
                    cost_note = f"live positions feed ({len(rows)} row(s))"
                else:
                    cost_note = f"positions fetch failed ({rate_limit_note(pres)})"
            except Exception as pexc:  # noqa: BLE001
                cost_note = f"positions fetch failed: {pexc}"

        # MT-1 (2026-09-09): DEPOSITS FROM THE DEPOSITS LEDGER OR NOT AT ALL.
        # The balance response is never consulted for deposits (it has no
        # such field; the old fallback to cash balance is the mistake this
        # block exists to make impossible).  A client without the endpoint,
        # or a failed read, leaves deposits and P&L None with the reason,
        # and the sync still stands: cash and the mark are true regardless.
        deposits_usd = None
        withdrawals_usd = None
        lifetime_pnl = None
        pnl_note = None
        deposits_source = "none (deposits ledger not read)"
        fetch_dep = getattr(live_client, "fetch_deposits", None)
        if not callable(fetch_dep):
            pnl_note = "venue client exposes no fetch_deposits; deposits never derived from balance"
        else:
            try:
                dres = call_with_rate_limit_retry(fetch_dep, **kw)
                if not dres["ok"]:
                    pnl_note = f"deposits fetch failed ({rate_limit_note(dres)})"
                else:
                    drows = list(dres["value"] or [])
                    dep_total, dep_n, dep_skipped = ledger_total_usd(drows)
                    deposits_source = ledger_source_note("deposits", len(drows), dep_skipped)
                    # H1 (2026-09-09): ZERO DEPOSIT ROWS ON A FUNDED ACCOUNT IS
                    # UNKNOWN, NEVER $0.  A $0 deposits figure prints lifetime
                    # P&L = +account value (+$980.62 on 2026-09-09), the same
                    # lie as the cash-balance fallback with a different sign.
                    # This account has 13 deposits; an empty ledger means the
                    # read is wrong (auth scope, key rename, empty envelope).
                    if dep_n == 0:
                        pnl_note = ("deposits endpoint returned 0 rows on a funded account"
                                    + (f" ({len(dep_skipped)} skipped: "
                                       f"{', '.join(sorted(set(dep_skipped)))})" if dep_skipped else ""))
                    else:
                        deposits_usd = dep_total
                        withdrawals_usd = 0.0
                        fetch_wd = getattr(live_client, "fetch_withdrawals", None)
                        if callable(fetch_wd):
                            wres = call_with_rate_limit_retry(fetch_wd, **kw)
                            if wres["ok"]:
                                withdrawals_usd, _wn, _ws = ledger_total_usd(list(wres["value"] or []))
                            else:
                                pnl_note = f"withdrawals fetch failed ({rate_limit_note(wres)})"
                        if pnl_note is None:
                            lifetime_pnl = round(account_value_usd - deposits_usd + withdrawals_usd, 2)
            except Exception as dexc:  # noqa: BLE001
                pnl_note = f"deposits fetch failed: {dexc}"
        if lifetime_pnl is None:
            deposits_usd = None
            withdrawals_usd = None

        fact_value = {
            "cash_usd": cash_usd,
            "account_value_usd": account_value_usd,
            "open_positions_usd": open_pos_usd,
            "open_positions_cost_usd": open_pos_cost_usd,
            "open_positions_cost_source": cost_note,
            "positions_cost_unreadable": cost_unreadable,
            "lifetime_deposits_usd": deposits_usd,
            "lifetime_withdrawals_usd": withdrawals_usd,
            "lifetime_pnl_usd": lifetime_pnl,
            "pnl_note": pnl_note,
            "deposits_source": deposits_source,
            "timestamp": now_iso,
            "is_stale": False,
            "source_type": "live_kalshi_api_authenticated",
            "raw_response": raw_bal,
        }

        fact = Fact(
            key="kalshi.oracle.balance",
            domain="kalshi",
            value=fact_value,
            source_artifact="live_kalshi_api:/trade-api/v2/portfolio/balance",
            verified_at=now_iso,
            verified_by="venue_api_authenticated",
            is_immutable=False,
        )

        store.set_fact(fact)
        cost_txt = (f" (cost ${open_pos_cost_usd:.2f})" if open_pos_cost_usd is not None
                    else f" (cost unreadable: {cost_note})")
        if lifetime_pnl is None:
            money_txt = f"Deposits=UNKNOWN | Lifetime P&L=UNKNOWN ({pnl_note})"
        else:
            money_txt = f"Deposits=${deposits_usd:.2f} | Lifetime P&L=${lifetime_pnl:.2f}"
        msg = (f"Synced: Account=${account_value_usd:.2f} (cash ${cash_usd:.2f} + positions "
               f"mark ${open_pos_usd:.2f}{cost_txt}) | {money_txt} [FRESH]")
        return True, msg, fact
    except Exception as e:
        return False, f"Live venue API balance fetch failed: {e}", None
