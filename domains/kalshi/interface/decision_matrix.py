"""Decision matrix and status renderer for Kalshi Domain Pod.

MT-1 (2026-09-09): THE WORD "P&L" IS NEVER PRINTED BESIDE A NUMBER THAT IS NOT
account_value - deposits + withdrawals.  The status printed "Cash: $966.10 |
Positions: $14.52 | P&L: $+14.52" and the Domain Head reported the positions
mark as the account's P&L (truth: -$1,619 on $2,600 deposited).  The money
line now spells the identity out in full and prints "Lifetime P&L: UNKNOWN
(<why>)" whenever the oracle fact carries None -- an unknown is reported as
unknown, never as a number that happens to be lying nearby.

MT-2 (2026-09-09): THE LAPTOP DB IS A MIRROR.  The Domain Head briefed Ryan
from the laptop copy (16 dead orders) as if it were the venue.  When this
renders anywhere but the VPS (hostname `senate`) the first line says so and
names the live host, so a status read off the mirror can never be quoted as
venue truth without the banner travelling with it.
"""

import socket
from datetime import datetime, timezone, timedelta
from typing import Optional

from domains.kalshi.state.fact_store import FactStore

# The VPS hostname.  Anything else is the laptop mirror (tests patch this).
VPS_HOSTNAME = "senate"
VPS_SSH = "ssh -i ~/.ssh/senate_vps_ed25519 ubuntu@129.146.115.241, /home/ubuntu/senate"
MIRROR_BANNER = ("⚠️ THIS DB IS THE LAPTOP MIRROR — live truth is the VPS "
                 f"({VPS_SSH}); order/seat lists below may be stale")


def _money_usd(x: Optional[float]) -> str:
    return "UNKNOWN" if x is None else f"${float(x):,.2f}"


def is_vps_host(hostname: Optional[str] = None) -> bool:
    """True only on the VPS; every other host renders the mirror banner."""
    h = hostname if hostname is not None else socket.gethostname()
    return str(h).split(".")[0] == VPS_HOSTNAME


DEPOSITS_LEDGER_SOURCE_PREFIX = "live /portfolio/deposits"


def deposits_are_ledger_sourced(v: dict) -> bool:
    """True only when the oracle fact's deposits came from the deposits ledger.

    The ONE predicate (M7) every renderer uses: lifetime_deposits_usd and
    lifetime_pnl_usd both present AND deposits_source begins with
    `live /portfolio/deposits`.  A pre-2026-09-09 fact (deposits == cash,
    no source) fails it; so does a fact whose deposits were read but rejected
    (H1: 0 rows on a funded account -> deposits None).
    """
    if not isinstance(v, dict):
        return False
    if v.get("lifetime_deposits_usd") is None or v.get("lifetime_pnl_usd") is None:
        return False
    return str(v.get("deposits_source") or "").startswith(DEPOSITS_LEDGER_SOURCE_PREFIX)


def render_money_lines(v: dict) -> str:
    """The money line from an oracle fact value (MT-1).

    `Account value $X = cash $C + positions (mark $M / cost $K) | Deposits $D
    | Lifetime P&L $P`, or with `Lifetime P&L: UNKNOWN (<pnl_note>)` when the
    fact carries None.  P&L is read from the fact, never recomputed here from
    cash and the mark.
    """
    cash = v.get("cash_usd")
    mark = v.get("open_positions_usd")
    cost = v.get("open_positions_cost_usd")
    account = v.get("account_value_usd")
    if account is None and cash is not None and mark is not None:
        account = round(float(cash) + float(mark), 2)
    deposits = v.get("lifetime_deposits_usd")
    pnl = v.get("lifetime_pnl_usd")
    note = v.get("pnl_note") or "deposits ledger not read; run './kalshi.py sync-oracle --live'"
    # MT-6 (2026-09-09): a fact written by the pre-MT-1 oracle carries
    # lifetime_deposits_usd == cash (the bug) and no deposits_source.  On the
    # VPS the old daemon kept writing such facts after this renderer shipped
    # and the status printed "Deposits $966.10 | Lifetime P&L $+14.52" again.
    # Deposits count ONLY when the fact says they came from the ledger.
    if not str(v.get("deposits_source") or "").startswith("live /portfolio/deposits"):
        if deposits is not None or pnl is not None:
            note = ("deposits not read from /portfolio/deposits (this oracle fact predates the "
                    "ledger read); run './kalshi.py sync-oracle --live'")
        deposits, pnl = None, None
    cost_txt = _money_usd(cost) if cost is not None else "unreadable"
    head = (f"Account value {_money_usd(account)} = cash {_money_usd(cash)} + positions "
            f"(mark {_money_usd(mark)} / cost {cost_txt})")
    if not deposits_are_ledger_sourced(v):
        if pnl is not None and deposits is not None:
            # a fact with numbers but no ledger provenance: the 09-09 shape
            note = (f"deposits not read from /portfolio/deposits "
                    f"(source: {v.get('deposits_source') or 'none'}); run './kalshi.py sync-oracle --live'")
            deposits = None
        return f"{head} | Deposits {_money_usd(deposits)} | Lifetime P&L: UNKNOWN ({note})"
    return f"{head} | Deposits {_money_usd(deposits)} | Lifetime P&L ${float(pnl):+,.2f}"


# ==========================================================================
# EARN-1 (2026-09-10): THE STATUS SURFACE MUST STATE WHAT WE EARNED.
#
# THE FAILURE.  On 2026-09-09/10 the Domain Head ran a monitor tick every
# fifteen minutes for nineteen hours and reported, every single time, the seat
# count and the escrow and "no fills".  Not once did it report the RATE.  Ryan
# had to come and ask "how much have we earned over the last 12 hours?" -- and
# the answer was $5.68, an $11.36/day pace against a $30+/day target.  A book
# at 20/20 seats with $497 resting reads like success on this surface while
# earning a third of target, because the surface never showed earnings.
# "No fills" is the absence of one specific failure, not evidence of working.
#
# THE FIX.  The accrual rate is now a FIRST-CLASS LINE on the status block,
# next to cash and escrow.  Every tick that prints seats now prints what those
# seats produced.  It cannot be reported without the other.
#
# PROVENANCE.  This is the VENUE-ESTIMATE feed (/v1/incentives/.../estimates,
# reward_centicents, written to /tmp/accrual_log.jsonl by the accrual poller).
# Ratified facts kalshi.rewards.realization_accuracy (0.1%) and
# kalshi.k1.credit_realization (ratio 1.0006) make it gospel: it realizes 1:1.
# NO MODEL RATIO IS APPLIED TO IT, ever.
#
# MEASUREMENT.  Per ratified kalshi.model.realization.measurement_rule the feed
# "freezes 3-6h and credits retroactively, so short windows manufacture fake
# rates in both directions".  So: marginal steps WITHIN each program (a program
# entering the feed is a baseline, not a gain; leaving is not a loss), POSITIVE
# only, and the headline window is 24h -- long enough to survive a freeze.
# The 12h figure is shown beside it so a fresh regime is visible early.
ACCRUAL_LOG_PATH = "/tmp/accrual_log.jsonl"
CENTICENTS_PER_USD = 10000.0


def accrual_window_usd(hours: float, path: str = ACCRUAL_LOG_PATH):
    """Venue-estimate accrual over the last `hours`, or None if unreadable.

    Returns (usd, n_paying_programs).  Never raises: a status block that dies
    because a log is missing is worse than one that says UNAVAILABLE.
    """
    import json as _json
    from collections import defaultdict as _dd
    # NEVER a bare `except: return None` here.  The first version of this
    # function used `io.open` in a module that does not import `io`, and the
    # blanket handler turned that NameError into a bland "UNAVAILABLE" -- the
    # identical swallow-the-reason bug WIRE-1 fixed on the venue client the
    # same day.  The reason is returned to the caller and printed.
    try:
        series = _dd(list)
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = _json.loads(line)
                except Exception:
                    continue
                ts = d.get("ts")
                est = d.get("est")
                if not ts or not isinstance(est, dict):
                    continue
                try:
                    t = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
                except Exception:
                    continue
                for pid, cc in est.items():
                    try:
                        series[pid].append((t, float(cc)))
                    except (TypeError, ValueError):
                        continue
        if not series:
            return None
        newest = max(t for pts in series.values() for t, _ in pts)
        cut = newest - timedelta(hours=float(hours))
        total = 0.0
        paying = set()
        for pid, pts in series.items():
            pts.sort()
            for (t0, v0), (t1, v1) in zip(pts, pts[1:]):
                if v1 > v0 and t1 >= cut:
                    total += (v1 - v0) / CENTICENTS_PER_USD
                    paying.add(pid)
        return (total, len(paying))
    except Exception as exc:                                  # noqa: BLE001
        return ("ERROR", "%s: %s" % (type(exc).__name__, str(exc)[:120]))


def render_accrual_line(path: str = ACCRUAL_LOG_PATH) -> str:
    """The one line that says whether the book is doing its job."""
    d1 = accrual_window_usd(24.0, path)
    h12 = accrual_window_usd(12.0, path)
    if d1 is None:
        return ("UNAVAILABLE (%s holds no usable estimate rows -- the accrual "
                "poller is the only record of what we earn; check "
                "kalshi-poller.service)" % path)
    if d1[0] == "ERROR":
        return ("UNAVAILABLE (%s -- reading %s; the accrual poller is the only "
                "record of what we earn)" % (d1[1], path))
    usd, progs = d1
    part = ""
    if h12 is not None and h12[0] != "ERROR":
        part = "  |  last 12h ${:,.2f}".format(h12[0])
    return ("${:,.2f}/24h across {} paying programs{}  [VENUE-ESTIMATE, "
            "realizes 1:1]".format(usd, progs, part))


# ==========================================================================
# DUTY-1 (2026-09-10): THE STATUS SURFACE MUST STATE HOW MUCH OF THE BOOK IS
# ACTUALLY ON THE VENUE.  Same house rule as EARN-1 above: a number the pod
# reports every tick must be the number the tape would give.
#
# THE FAILURE.  `deployment_plan.uptime_s / (uptime_s + downtime_s)` summed
# over all 474 plan rows read 88.98 % (7,195.2 h up / 891.2 h down).  The tape
# — every order's [placed_at, terminal) interval against 20 seats x
# wall-minutes, 2026-08-19 -> 2026-09-10, 23 day-clusters — says 64.69 %
# (band 62.6-64.7 %).  Twenty-four points.  A third of the capital earns
# nothing and the instrument called it a 89 % duty cycle, because downtime_s
# stopped accruing at terminal status, never accrued for the 66 rows seeded
# and never placed, and never accrued for seed -> first-placement latency.
# Every uptime claim this pod has made came off that number.
#
# THE FIX is in harness/duty_cycle.py (_open_downtime / book_duty); this line
# is how it becomes visible.  It sits next to EARNED because they are the two
# halves of one sentence: what the seats produced, and how many seat-minutes
# were on the venue to produce it.  A duty line without the earnings line is
# an efficiency claim about nothing; the earnings line without the duty line
# is the 09-09 failure again, a rate with no denominator.
#
# PROVENANCE.  This is the LEDGER, corrected — not an independent replay of
# the tape.  It is labelled [PLAN-LEDGER] so nobody mistakes it for the
# order-interval measurement in scratchpad/duty_cycle_uptime.md.  The two
# should now agree; if they ever diverge again the label is what makes the
# divergence a question instead of a headline.
# ==========================================================================

def render_duty_line(store: FactStore) -> str:
    """What fraction of the book's plan-row seat-time was actually on venue."""
    try:
        from domains.kalshi.harness.duty_cycle import DutyCycleLedger
        d = DutyCycleLedger(store).book_duty()
    except Exception as exc:                                  # noqa: BLE001
        # Never a bare swallow (EARN-1's rule): the reason is printed.
        return ("UNAVAILABLE (%s: %s -- the duty cycle is the denominator of "
                "the EARNED line above)" % (type(exc).__name__, str(exc)[:120]))
    if d["duty"] is None:
        return ("no accrued seat-time yet across %d plan row(s)  [PLAN-LEDGER]"
                % d["rows"])
    tail = ""
    if d["never_placed_rows"]:
        tail += ("  |  %d row(s) seeded and NEVER placed"
                 % d["never_placed_rows"])
    if d["unreadable_clocks"]:
        tail += ("  |  %d unreadable clock(s) counted as neither"
                 % d["unreadable_clocks"])
    return ("{:.1f}% of plan seat-time ON VENUE ({:,.0f}h up / {:,.0f}h down "
            "across {} rows, break-even {:.1f}%){}  [PLAN-LEDGER, all statuses]"
            .format(d["duty"] * 100.0, d["uptime_s"] / 3600.0,
                    d["downtime_s"] / 3600.0, d["rows"],
                    d["breakeven_duty"] * 100.0, tail))


def render_kalshi_status(store: FactStore) -> str:
    """Render a clean, high-density status summary for Kalshi Domain Pod (<20 lines)."""
    facts = store.list_facts()
    orders = store.list_active_orders()
    
    # Oracle balance check
    bal_fact = store.get_fact("kalshi.oracle.balance")
    if not bal_fact or not isinstance(bal_fact.value, dict):
        money_str = "UNAVAILABLE (oracle fact missing; run './kalshi.py sync-oracle')"
    else:
        v = bal_fact.value
        cash = v.get("cash_usd")
        pos = v.get("open_positions_usd")
        ts_str = v.get("timestamp", "UNKNOWN")
        
        if cash is None or pos is None:
            money_str = "UNAVAILABLE (corrupt oracle fact format)"
        else:
            is_stale = True
            try:
                record_dt = datetime.fromisoformat(str(ts_str).replace("Z", "+00:00"))
                age_hours = (datetime.now(timezone.utc) - record_dt).total_seconds() / 3600.0
                is_stale = age_hours > 24.0
            except Exception:
                is_stale = True

            status_tag = "⚠️ STALE" if is_stale else "✅ FRESH"
            money_str = f"{status_tag} (as of {ts_str}) — {render_money_lines(v)}"

    escrow = sum(float(o.collateral_usd or 0.0) for o in orders)
    lines = []
    if not is_vps_host():
        lines.append(MIRROR_BANNER)
    lines += [
        "══════════════════════════════════════════════════════════════",
        "              KALSHI DOMAIN POD — SYSTEM STATUS               ",
        "══════════════════════════════════════════════════════════════",
        f"Live Venue Truth:            {money_str}",
        # EARN-1 HARDENING (2026-09-16).  EARN-1 put the rate on its own line and said "it
        # cannot be reported without the other".  It could: on 2026-09-16 a monitor tick
        # read `./kalshi.py status | grep -E "Live Venue|Resting escrow"` for a week, which
        # matches the escrow line and DROPS the EARNED line, and ~40 consecutive reports to
        # Ryan carried seats and escrow and no rate.  A separate line is droppable by any
        # grep.  So the rate is now WELDED onto the escrow line itself: escrow is the
        # denominator, and it can no longer be read without its numerator.  The standalone
        # EARNED line stays, for the reader who wants it broken out.
        f"Resting escrow:              ${escrow:,.2f} across {len(orders)} seats"
        f"  →  EARNING {render_accrual_line()}",
        f"EARNED (the point):          {render_accrual_line()}",
        f"DUTY (the denominator):      {render_duty_line(store)}",
        f"Verified Ground-Truth Facts: {len(facts)} active entries in SQLite",
        "──────────────────────────────────────────────────────────────",
        f"ACTIVE OPEN ORDERS ({len(orders)}):",
    ]

    if not orders:
        lines.append("  (No resting orders recorded)")
    else:
        for o in orders:
            lines.append(f"  • [{o.lane.upper()}] {o.ticker} — {o.count} {o.side.upper()} @ {int(o.price*100)}c (${o.collateral_usd:.2f}) [order: {o.order_id[:8]}]")


    lines.extend([
        "──────────────────────────────────────────────────────────────",
        "KEY INVARIANTS ENFORCED:",
        "  1. 50% Distance Decay & 15% Churn Haircut Compiled",
        "  2. Non-zero Yielding Seats NEVER Canceled to Cash",
        "  3. Sourced Venue Snapshots Required for Money Actions",
        "══════════════════════════════════════════════════════════════",
    ])
    return "\n".join(lines)
