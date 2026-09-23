"""Invariant and boundary condition validator for Kalshi Domain Pod.

Enforces:
1. Maker-Only Rules (Market orders prohibited)
2. Spread Crossing Protection (Never cross the touch)
3. Exposure Limits: Single market cap (verify/caps.PER_MARKET_HARD_USD, the compiled hard ceiling; a fact may only tighten it) & Total portfolio risk cap (fact)
4. Terminal Window Curfew: Zero order entry within 24h of window expiry (anti-evacuation)
5. Measurement & Catalyst Clock Curfew: Zero order entry within 55h of scheduled print
6. Price-Zone Hazard Gate: <=35c requires elevated armor (>=600ct)
7. Fundamental Base-Rate Side-Gate: Zero quoting against asymmetric fundamental distributions
8. Feed Taxonomy: Max 1 seat per underlying catalyst/data stream
"""

from typing import Any, Dict, List, Optional, Set, Tuple

from domains.kalshi.state.fact_store import FactStore
from domains.kalshi.verify.base_rates import evaluate_fundamental_base_rate
from domains.kalshi.harness.positions import positions_exposure_usd
from domains.kalshi.verify.caps import PER_MARKET_HARD_USD, TOTAL_HARD_USD
from domains.kalshi.verify.qualify import (
    check_scheduled_measurement_clock,
    qualify_seat_candidate,
    resolve_feed_taxonomy,
)


class InvariantEngine:
    def __init__(self, facts: Optional[FactStore] = None):
        self.facts = facts or FactStore()

    def validate_order_proposal(
        self,
        proposal: Dict[str, Any],
        active_feed_ids: Optional[Set[str]] = None,
    ) -> Tuple[bool, List[str], List[str]]:
        """Validate order against Kalshi compiled invariants."""
        violations: List[str] = []
        passes: List[str] = []

        # 1. Maker-only check
        order_type = str(proposal.get("order_type", "limit")).lower()
        if order_type == "market":
            violations.append("Invariant Breach: Market/Taker orders are forbidden. Must be post-only maker.")
        else:
            passes.append("Maker-only rule satisfied.")

        # 2. Spread crossing check
        price = float(proposal.get("price", 0.0))
        touch_px = proposal.get("touch_price")
        if touch_px is not None:
            touch_float = float(touch_px)
            if price > touch_float:
                violations.append(f"Invariant Breach: Price ${price:.2f} crosses touch ${touch_float:.2f}.")
            else:
                passes.append(f"Price ${price:.2f} does not cross touch.")

        # 3. Terminal Window Curfew (>= 24h to window expiry)
        hours_to_close = proposal.get("hours_to_window_expiry")
        if hours_to_close is not None:
            if float(hours_to_close) < 24.0:
                violations.append(
                    f"Invariant Breach: Terminal window curfew breached ({float(hours_to_close):.1f}h < 24.0h to close). "
                    f"High book evacuation and adverse selection fill risk."
                )
            else:
                passes.append(f"Terminal window margin satisfied ({float(hours_to_close):.1f}h >= 24.0h).")

        # 4. Measurement & Catalyst Clock Curfew (>= 55h hold horizon)
        hours_to_print = proposal.get("hours_to_scheduled_print")
        ticker = str(proposal.get("ticker", ""))
        mkt_title = str(proposal.get("title", ""))
        # FG-11 (2026-09-05): the horizon from fact kalshi.hold_horizon, not a
        # literal — this gate and the qualifier must agree with the engine.
        from domains.kalshi.harness import policy_facts as _policy
        _hold_h = _policy.resolve_hold_horizon(self.facts)
        clock_ok, clock_msg = check_scheduled_measurement_clock(
            ticker=ticker,
            title=mkt_title,
            hours_to_scheduled_print=hours_to_print,
            hold_horizon_hours=_hold_h,
        )
        if not clock_ok and clock_msg:
            violations.append(f"Invariant Breach: {clock_msg}")
        else:
            passes.append(f"Measurement clock curfew satisfied (>= {_hold_h:.0f}h to scheduled data release).")

        # 5. Price-Zone Hazard Gate (<=35c carries 0.36% fill rate)
        price_cents = int(round(price * 100)) if price <= 1.0 else int(price)
        wall_depth = float(proposal.get("wall_contracts", 0.0))
        if 0 < price_cents <= 35 and wall_depth > 0 and wall_depth < 600.0:
            violations.append(
                f"Invariant Breach: Price {price_cents}c is in <=35c fill hazard zone; "
                f"requires elevated armor >= 600ct (found {wall_depth:.0f}ct)."
            )
        elif price_cents >= 90:
            violations.append(f"Invariant Breach: Price {price_cents}c >= 90c asymmetric taker trap.")

        # 6. Fundamental Base-Rate Side-Gate Check
        side = str(proposal.get("side", "yes"))
        mkt_sub = str(proposal.get("subtitle", ""))
        is_safe_rate, rate_violation, _ = evaluate_fundamental_base_rate(
            ticker=ticker,
            side=side,
            price=price,
            market_title=mkt_title,
            market_subtitle=mkt_sub,
        )
        if not is_safe_rate and rate_violation:
            violations.append(rate_violation)
        else:
            passes.append("Fundamental base-rate side check passed.")

        # 7. Feed Taxonomy & Basket Dedup
        feed_id = resolve_feed_taxonomy(ticker, mkt_title)
        if active_feed_ids and feed_id in active_feed_ids:
            violations.append(
                f"Invariant Breach: Feed '{feed_id}' is already occupied by a resting seat. "
                f"Basket concentration prohibited."
            )
        else:
            passes.append(f"Feed taxonomy '{feed_id}' unique.")

        # 8. Capital Exposure Caps (Single Market & Total Portfolio Cap)
        notional_usd = float(proposal.get("notional_usd", 0.0))
        # ONE RESOLVER (FG-01, 2026-09-05).  This block used to read
        # `kalshi.exposure.caps` directly, with a private $250 fallback for
        # the total, while that fact said $50/market, was immutable, and
        # disagreed with Ryan ($25/market; 20 x $25 in a $530 cap) and with
        # the live VPS.  FactStore.get_limits() is now the only way in:
        # `kalshi.limits` first, the legacy key only as a fallback, the
        # per-market number clamped to the compiled ceiling, and NO private
        # total default — an unreadable total fails closed.
        limits = self.facts.get_limits()
        if limits is None:
            violations.append(
                "Invariant Breach: Capital limits fact 'kalshi.limits' (or legacy "
                "'kalshi.exposure.caps') is missing or unverified. Fails closed.")
        elif limits.get("total_usd") is None:
            violations.append(
                f"Invariant Breach: total portfolio cap unreadable in "
                f"'{limits.get('source')}'. Fails closed.")
        else:
            # COMPILED CEILING WINS (2026-09-05).  The fact may only TIGHTEN the
            # per-market cap, never loosen it.  The live `kalshi.exposure.caps`
            # fact was self-stamped immutable at $50 by a prior agent and
            # set_fact refuses immutables, so the stored value could not be
            # corrected through the API; meanwhile this line trusted it and a
            # second $25 seat could stack on a $25 resting order or open
            # position in the same ticker.  Ryan: "never to have more than 25$
            # in any market".  get_limits() applies min() against the ceiling;
            # re-applied here so this gate cannot be loosened by a resolver bug.
            max_per_mkt = min(float(limits["per_market_usd"]), PER_MARKET_HARD_USD)
            # CAP-6 (2026-09-05): the TOTAL is clamped to the compiled ceiling
            # for the same reason — a fact of $1000 installed $1000 here while
            # only the seeder clamped to Ryan's $530 (2026-08-20).
            max_total_cap = min(float(limits["total_usd"]), TOTAL_HARD_USD)

            # PER-MARKET CAP COUNTS WHAT IS ALREADY IN THE MARKET (2026-09-05).
            # This used to test the proposal alone, so a second $25 seat, or a
            # seat on top of an open position from a fill, passed as "$25 within
            # limit".  Ryan: "never more than $25 in any market" — orders AND
            # positions, per ticker.  Existing = same-ticker RESTING mirror rows
            # + cost basis of same-ticker FILLED plan rows (the open position).
            same_mkt = 0.0
            replacing = str(proposal.get("replacing_order_id") or "")
            try:
                for o in self.facts.list_active_orders():
                    if (str(getattr(o, "ticker", "")) == str(ticker)
                            and str(getattr(o, "status", "")).upper() == "RESTING"
                            and str(getattr(o, "order_id", "")) != replacing):
                        same_mkt += float(getattr(o, "collateral_usd", 0.0) or 0.0)
                for r in self.facts.list_deployment_plan(statuses=["filled"]):
                    if str(r.get("ticker")) != str(ticker):
                        continue
                    # FLAT-3 (2026-09-05): a 'filled' row is the RECEIPT of a
                    # sweep and stays 'filled' forever; the POSITION it left
                    # ends when it is sold or settles, and that end is stamped
                    # in flattened_at.  Before today this loop summed every
                    # filled row for the ticker until the end of time, so a
                    # ticker once swept (KXSNOWCRABCATCH, 09-03) could never
                    # be re-seated even after the venue showed it flat.  A
                    # row with NO flattened_at still counts at its full
                    # max_escrow_usd (the order size, not the filled size):
                    # over-counting a live position is the safe direction,
                    # and the venue max() below is the truth anyway.
                    if r.get("flattened_at"):
                        continue
                    same_mkt += float(r.get("max_escrow_usd") or 0.0)
            except Exception as exc:  # fail closed: unknown exposure is not zero exposure
                violations.append(f"Invariant Breach: same-market exposure unreadable ({str(exc)[:60]}) — fails closed.")
            # VENUE TRUTH WINS WHEN IT IS LARGER (CAP-2, 2026-09-05).  The
            # local view above cannot see an orphan order (mirror already
            # CANCELLED/GONE_FROM_VENUE, order still live) or a position from
            # a non-plan fill.  The placement engine reads the venue's open
            # orders and positions for the ticker and sends the number here;
            # the gate takes the larger of the two ledgers, never the smaller.
            try:
                venue_same = float(proposal.get("same_ticker_venue_usd") or 0.0)
            except (TypeError, ValueError):
                venue_same = max_per_mkt  # unreadable -> full
            same_mkt = max(same_mkt, venue_same)
            # VR-4 (2026-09-05): A THIRD LEDGER -- THE VENUE'S OWN POSITIONS
            # MIRROR.  `same_ticker_venue_usd` above only exists when the
            # CALLER read the venue and remembered to pass it; the local
            # view only sees 'filled' plan rows, and a fill on an order no
            # plan row named never made one (KXSNOWCRABCATCH, 09-03).  The
            # placement engine now writes fact `kalshi.venue.positions`
            # {by_ticker: {ticker: cost_usd}} on EVERY successful positions
            # read (offensive, defensive and flatten paths), so this gate
            # has a per-ticker position number that does not depend on the
            # proposal.  Larger ledger wins; an unreadable entry counts as
            # the full cap (unknown exposure is not zero exposure).  A stale
            # mirror can only over-count -- the safe direction -- and the
            # engine refreshes it before every placement cycle.
            try:
                pos_fact = self.facts.get_fact("kalshi.venue.positions")
                if pos_fact and isinstance(pos_fact.value, dict):
                    by_tk = pos_fact.value.get("by_ticker") or {}
                    if str(ticker) in by_tk:
                        try:
                            same_mkt = max(same_mkt, float(by_tk[str(ticker)]))
                        except (TypeError, ValueError):
                            same_mkt = max(same_mkt, max_per_mkt)
            except Exception as exc:  # fail closed
                violations.append(f"Invariant Breach: venue positions mirror unreadable ({str(exc)[:60]}) — fails closed.")
            if notional_usd + same_mkt > max_per_mkt:
                violations.append(f"Invariant Breach: Allocation ${notional_usd:.2f} + ${same_mkt:.2f} already in {ticker} exceeds per-market cap of ${max_per_mkt:.2f}.")
            else:
                passes.append(f"Single market allocation ${notional_usd:.2f} (+${same_mkt:.2f} existing) is within limit.")

            # Compute total deployed capital (Positions + Resting Orders + Proposed Order)
            active_orders = self.facts.list_active_orders()
            resting_collateral = sum(o.collateral_usd for o in active_orders)
            # VENUE TRUTH IN THE TOTAL CAP TOO (CAP-5, 2026-09-05).  The sum
            # above is the LOCAL mirror; the two orphan orders minted by the
            # premature "gone from venue" reconcile on 2026-09-05 rested live
            # for hours with mirror rows already GONE_FROM_VENUE, i.e. $0
            # here.  A placer that has read the venue's open orders sends
            # their total as `venue_resting_usd`; the gate takes the larger
            # ledger, never the smaller.  An unreadable number counts as the
            # whole cap (unknown exposure is not zero exposure).
            venue_resting = 0.0
            if proposal.get("venue_resting_usd") is not None:
                try:
                    venue_resting = float(proposal.get("venue_resting_usd"))
                except (TypeError, ValueError):
                    venue_resting = max_total_cap
            resting_collateral = max(resting_collateral, venue_resting)

            # POSITIONS AT COST (CAP-6, 2026-09-05).  This read
            # `open_positions_usd` alone — the venue's MARK — and every fill
            # on this book is an adverse sweep, so the mark sits below what
            # was paid and the total cap loosened by exactly the loss.  Now
            # the LARGEST readable of the oracle's cost basis, its mark and
            # the engine's per-ticker mirror (harness/positions.py).
            positions_val, _pos_detail = positions_exposure_usd(self.facts)

            total_deployed = resting_collateral + positions_val + notional_usd
            if total_deployed > max_total_cap:
                violations.append(
                    f"Invariant Breach: Total portfolio exposure ${total_deployed:.2f} "
                    f"(Positions ${positions_val:.2f} + Resting ${resting_collateral:.2f} + Proposed ${notional_usd:.2f}) "
                    f"exceeds total portfolio budget of ${max_total_cap:.2f}."
                )
            else:
                passes.append(f"Total portfolio exposure ${total_deployed:.2f} <= ${max_total_cap:.2f}.")

        is_valid = len(violations) == 0
        return is_valid, violations, passes

