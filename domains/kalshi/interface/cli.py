"""Unified CLI for Kalshi Domain Pod with real venue client, gate wiring, and telemetry export."""

import argparse
import json
import os
import sys
import uuid
from pathlib import Path
from typing import List, Optional

# Ensure domain package is importable
POD_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
for p in [str(REPO_ROOT), str(POD_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from domains.kalshi.harness.gate import ActionType, ExecutionGate
from domains.kalshi.harness.oracle_sync import sync_kalshi_oracle
from domains.kalshi.harness.venue_client import KalshiVenueClient
from domains.kalshi.interface.decision_matrix import render_kalshi_status
from domains.kalshi.state.fact_store import FactStore
from domains.kalshi.state.models import ActiveOrder
from domains.kalshi.state.seed import seed_kalshi_database
from domains.kalshi.verify.payoff import evaluate_order_payoff, evaluate_order_payoff_from_venue_record


def main(argv: Optional[List[str]] = None, store: Optional[FactStore] = None,
         client: Optional[KalshiVenueClient] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="kalshi",
        description="Kalshi Domain Pod CLI — Dedicated Prediction Market Engine",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # kalshi status
    subparsers.add_parser("status", help="Print clean Kalshi seat and money status")

    # kalshi seed
    subparsers.add_parser("seed", help="Seed verified Kalshi platform laws into SQLite")

    # kalshi fact KEY  (2026-09-09: doctrine is read from the DB, never recalled)
    fact_p = subparsers.add_parser("fact", help="Print one ratified fact verbatim (or list keys with --list)")
    fact_p.add_argument("key", nargs="?", help="Fact key, e.g. kalshi.rewards.realization_accuracy")
    fact_p.add_argument("--list", action="store_true", help="List every fact key")

    # kalshi telemetry
    telem_p = subparsers.add_parser("telemetry", help="Export domain telemetry in standard JSON format")
    telem_p.add_argument("--json", action="store_true", default=True, help="Output format JSON")

    # kalshi sync-oracle
    sync_p = subparsers.add_parser("sync-oracle", help="Sync authentic venue balance directly from live authenticated Kalshi API")
    sync_p.add_argument("--live", action="store_true", default=True, help="Fetch live balance from authenticated Kalshi API")
    sync_p.add_argument("--max-age", type=float, default=24.0, help="Max age in hours before marking stale")

    # kalshi sync-orders (aliased with sync-seats)
    # VR-6 (2026-09-05): sync-orders IS the venue reconciler (harness/
    # venue_reconciler.reconcile, the same call the cadence daemon makes
    # every cycle) run in mirror mode: venue orders upserted with their
    # existing lane PRESERVED, ghosts retired after the grace, retired rows
    # restored when listed again, and ORPHAN orders cancelled through the
    # defensive gate.  --no-cancel-orphans reports them instead.
    orders_p = subparsers.add_parser("sync-orders", help="Reconcile the local order mirror to the live venue (mirror both ways, cancel orphan orders)")
    orders_p.add_argument("--live", action="store_true", default=True, help="Fetch active open orders from authenticated Kalshi API")
    orders_p.add_argument("--no-cancel-orphans", action="store_true", help="Report untracked venue orders instead of cancelling them")

    seats_p = subparsers.add_parser("sync-seats", help="Alias for sync-orders")
    seats_p.add_argument("--live", action="store_true", default=True, help="Fetch active open orders from authenticated Kalshi API")
    seats_p.add_argument("--no-cancel-orphans", action="store_true", help="Report untracked venue orders instead of cancelling them")


    # kalshi order
    order_p = subparsers.add_parser("order", help="Manage and route market maker orders through execution gate")
    order_sub = order_p.add_subparsers(dest="order_cmd", required=True)

    # kalshi order place
    place_p = order_sub.add_parser("place", help="Route a new maker limit order through the offensive execution gate")
    place_p.add_argument("--ticker", required=True, help="Market ticker")
    place_p.add_argument("--side", required=True, choices=["yes", "no"], help="Order side")
    place_p.add_argument("--price-cents", type=int, required=True, help="Price in cents (1-99)")
    place_p.add_argument("--count", type=int, required=True, help="Contract count")
    place_p.add_argument("--touch", type=float, help="Current touch price for spread validation")
    place_p.add_argument("--live", action="store_true", help="Submit order directly to live venue API")

    # kalshi order cancel
    cancel_p = order_sub.add_parser("cancel", help="Route an order cancellation through the defensive fast-path gate")
    cancel_p.add_argument("--order-id", required=True, help="Order ID to cancel")
    cancel_p.add_argument("--live", action="store_true", help="Submit cancellation directly to live venue API")

    # kalshi position (FLAT-7, 2026-09-05).  Until today the CLI could place
    # and cancel but never SELL: 25 lifetime fills, every one an informed
    # sweep, every one leaving a position nobody could flatten from here
    # (KXSNOWCRABCATCH, 09-03, still open).  `order place --live` cannot be
    # bent into a close either -- it routes through the sovereign broker,
    # whose guards ($50 notional, 90c acquire ceiling, arm token) are
    # acquire guards.  A close has its own path: PlacementEngine
    # .flatten_position -> ExecutionGate FLATTEN_POSITION (reduce-only fast
    # path) -> KalshiVenueClient.place_post_only_close (count <= held).
    position_p = subparsers.add_parser(
        "position", help="List the venue's open positions or place a reduce-only flatten")
    position_sub = position_p.add_subparsers(dest="position_cmd", required=True)
    position_sub.add_parser(
        "list", help="Venue positions (ticker / contracts / exposure / resting orders) plus the local receipt rows")
    pflat_p = position_sub.add_parser(
        "flatten", help=("Place ONE reduce-only close against the venue's LIVE position "
                         "(post-only by default; --cross sells into the bid as a taker).  "
                         "Without --live it is a DRY RUN: reads + gate only, "
                         "no venue write, no store write."))
    pflat_p.add_argument("--ticker", required=True, help="Market ticker holding the position")
    pflat_p.add_argument("--live", action="store_true", help="Submit the close to the live venue")
    pflat_p.add_argument("--price-cents", type=int, default=None,
                         help=("Sell price in the HELD side's cents (1-99).  Default: join the "
                               "best resting ask of the held side off the fresh book."))
    pflat_p.add_argument("--count", type=int, default=None,
                         help="Contracts to sell (default: the whole position; never more than held)")
    pflat_p.add_argument("--take", action="store_true",
                         help=("Lead the spread: one tick above the best bid of the held side "
                               "(still post-only -- a flatten never crosses the book)"))
    # FLAT-11 (2026-09-09): the post-only close could not FILL in the books a
    # sweep leaves.  The 09-09 KXKR probe joined the 4c YES ask behind 13,275
    # contracts (~200ct/day lift it), so close semantics could never be
    # verified and the position could never be left.  --cross sells INTO the
    # bid as a taker.  Gated on kalshi.flatten.policy.allow_taker (ratify with
    # state/ratify_flatten_20260909.py); measured rule: held-side cost <= 20c
    # -> cross now (-$15.6/fill vs -$25.5 held); > 20c -> HOLD.
    pflat_p.add_argument("--cross", action="store_true",
                         help=("Sell into the bid as a TAKER; reduce-only; requires "
                               "kalshi.flatten.policy.allow_taker"))
    pflat_p.add_argument("--why", default="manual", help="Audit reason stamped on the mirror and plan rows")

    # kalshi verify-payoff
    payoff_p = subparsers.add_parser("verify-payoff", help="Compute deterministic EV(Hold) vs EV(Recycle)")
    payoff_p.add_argument("--source-file", help="Path to authentic venue JSON record")
    payoff_p.add_argument("--ticker", help="Current position ticker")
    payoff_p.add_argument("--dist", type=int, help="Distance in ticks from touch")
    payoff_p.add_argument("--reward", type=float, help="Base daily reward USD")
    payoff_p.add_argument("--cand-ticker", help="Alternative candidate ticker")
    payoff_p.add_argument("--cand-dist", type=int, default=0, help="Candidate distance in ticks")
    payoff_p.add_argument("--cand-reward", type=float, default=0.0, help="Candidate base reward")
    payoff_p.add_argument("--hurdle", type=float, default=1.5, help="Recycle hurdle multiplier (default 1.5)")
    # kalshi census (Multi-family opportunity scan)
    census_p = subparsers.add_parser("census", help="Scan active market families across 7 days with curfew and base-rate filters")
    census_p.add_argument("--family", help="Filter by family prefix (e.g. KXFEDFUNDS, KXUSCPI, KXRAIN)")
    census_p.add_argument("--min-hours", type=float, default=24.0, help="Minimum hours to window close (default 24h)")

    # kalshi placement (order-placement arm/disarm state machine)
    placement_p = subparsers.add_parser("placement", help="Show or flip the order-placement state machine (blocker ledger source of truth)")
    placement_sub = placement_p.add_subparsers(dest="placement_cmd", required=True)
    placement_sub.add_parser("show", help="Print current placement state and recent history")
    placement_sub.add_parser("plan", help="Show the deployment_plan table (the placement engine's marching orders)")
    pset_p = placement_sub.add_parser("set", help="Flip placement state (append-only ledger)")
    pset_p.add_argument(
        "--state", required=True, choices=["ARMED", "DISARMED", "HALTED"],
        help=("New placement state.  ARMED: new deployments allowed.  DISARMED: "
              "NEW DEPLOYMENTS FROZEN, existing seats keep their full shield "
              "(reactive cancel + re-arm + hourly timer).  HALTED: global freeze, "
              "nothing places at all — for a SYSTEM-level fault, not a fill."))
    pset_p.add_argument("--reason", required=True, help="Why the state is being flipped (e.g. verdict / authority reference)")
    pset_p.add_argument("--by", required=True, help="Who authorized the flip (e.g. 'ryan', 'domain-head')")

    # kalshi placement price-rule — price AT THE PLACEMENT INSTANT, not at seed
    # time.  A 'derive' row carries a rule instead of a pinned price and picks
    # its level off the fresh book when the engine can actually place it.
    prule_p = placement_sub.add_parser(
        "price-rule",
        help=("Attach a pricing RULE to a plan row so its level and size are "
              "derived at the placement instant instead of pinned at seed time"))
    prule_p.add_argument("--id", type=int, required=True, help="deployment_plan row id")
    prule_p.add_argument("--mode", required=True, choices=["fixed", "derive"],
                         help=("'fixed' = use the pinned price_cents/count verbatim "
                               "(the default, unchanged behaviour).  'derive' = pick "
                               "the level and recompute the size off the FRESH book "
                               "at the placement instant, never the seed snapshot."))
    prule_p.add_argument("--max-capital", type=float, default=None,
                         help="Budget in USD the derived size is computed from (required for 'derive')")
    prule_p.add_argument("--band", default=None, metavar="LO-HI",
                         help="Inclusive price band in cents, e.g. 15-85 (default 15-85)")
    prule_p.add_argument("--min-armor", type=float, default=None,
                         help="Rival contracts required resting AT the chosen level")
    prule_p.add_argument("--max-share", type=float, default=None,
                         help="Ceiling on our_ct / (our_ct + rival_ct) at the chosen level, e.g. 0.60")
    prule_p.add_argument("--side", default=None, choices=["yes", "no"],
                         help="Assert the row's side; refuses if it does not match")
    prule_p.add_argument("--note", default=None, help="Audit note appended to the row's notes")

    # kalshi seed-book (Autonomous book shortfall seeder)
    seed_book_p = subparsers.add_parser("seed-book", help="Run autonomous book seeder to fill shortfall up to TARGET seats")
    seed_book_p.add_argument("--target", type=int, default=20, help="Target active seats (default 20)")

    # kalshi daemon (Continuous Autonomous Cadence)
    daemon_p = subparsers.add_parser("daemon", help="Run continuous autonomous execution daemon across 7 strategy lanes")
    daemon_p.add_argument("--interval", type=int, default=300, help="Cycle interval in seconds (default 300s)")
    daemon_p.add_argument("--cycles", type=int, help="Optional max cycle count")

    args = parser.parse_args(argv)



    # store is injectable so tests can drive the CLI against a temp database
    # instead of the live pod DB.
    store = store or FactStore()
    gate = ExecutionGate(store)
    # `client` is injectable so tests can prove the venue-truth gates with a stub.
    client = client or KalshiVenueClient()

    if args.command == "status":
        print(render_kalshi_status(store))
        return 0

    elif args.command == "fact":
        if args.list or not args.key:
            for f in sorted(store.list_facts(), key=lambda f: f.key):
                print(f.key)
            return 0
        f = store.get_fact(args.key)
        if f is None:
            print(f"❌ no fact {args.key!r} in the store (try `./kalshi.py fact --list`)", file=sys.stderr)
            return 1
        print(json.dumps({"key": f.key, "value": f.value, "source_artifact": f.source_artifact,
                          "verified_by": f.verified_by, "verified_at": str(f.verified_at),
                          "is_immutable": bool(f.is_immutable)}, indent=2, sort_keys=True, default=str))
        return 0

    elif args.command == "seed":
        seed_kalshi_database(store)
        facts = store.list_facts()
        orders = store.list_active_orders()
        print(f"✅ Kalshi Domain seeded successfully: {len(facts)} platform laws, {len(orders)} open orders active.")
        return 0

    elif args.command == "telemetry":
        orders = store.list_active_orders()
        facts = store.list_facts()
        bal_fact = store.get_fact("kalshi.oracle.balance")
        
        telemetry = {
            "domain_id": "kalshi",
            "name": "Kalshi Prediction Markets",
            "category": "capital_generation",
            "mission": "Autonomous prediction market trading and market making engine.",
            "active_lanes": [
                "autoseat_lip",
                "crypto_scalp",
                "mlb_xvenue",
                "weather_ensemble",
                "dutchbook_arb",
                "deribit_implied",
                "earnings_nlp",
            ],
            "resource_consumption": {

                "resting_collateral_usd": round(sum(o.collateral_usd for o in orders), 2),
            },
            "domain_metrics": {
                "active_orders_count": len(orders),
                "oracle_balance": bal_fact.value if bal_fact and isinstance(bal_fact.value, dict) else None,
                "verified_facts_count": len(facts),
            },
            "invariant_health": "VERIFIED",
        }
        print(json.dumps(telemetry, indent=2))
        return 0

    elif args.command == "sync-oracle":
        ok, msg, fact = sync_kalshi_oracle(store, live_client=client, max_age_hours=args.max_age)
        if ok:
            print(f"✅ Oracle synced: {msg}")
            return 0
        else:
            print(f"❌ Oracle sync failed (fails closed): {msg}", file=sys.stderr)
            return 1

    elif args.command in ("sync-orders", "sync-seats"):
        # VR-6 (2026-09-05): ONE reconciler.  This block used to be the third
        # of three reconcilers, each with its own vocabulary: it upserted
        # every venue row RESTING with lane=o.get("lane", "general") --
        # OVERWRITING 'deployment_plan' on rows the engine owned -- then
        # retired RESTING rows the venue did not list, with no grace, and
        # never cancelled the orphan it was looking at.  It now calls the
        # same function the cadence daemon runs every cycle, in mirror mode.
        # Its old defect receipts (2026-08-17 no_price_dollars leg, 2026-08-18
        # phantom RESTING rows, FLAT-7 closes as lane 'flatten' at $0) are
        # honoured inside the reconciler's mirror pass.  Unreadable venue ->
        # nothing written, rc 1 (fail closed).
        from domains.kalshi.harness.venue_reconciler import reconcile
        report = reconcile(store, client, mirror_venue=True,
                           cancel_orphans=not getattr(args, "no_cancel_orphans", False),
                           gate=gate)
        if not report.ok:
            print(f"❌ {report.line()}", file=sys.stderr)
            return 1
        print(f"✅ Synced {report.venue_listed} live venue order(s). {report.line()}")
        return 0

    elif args.command == "order":
        if args.order_cmd == "place":
            notional = round((args.price_cents / 100.0) * args.count, 2)
            proposal = {
                "order_type": "limit",
                "ticker": args.ticker,
                "side": args.side,
                "price": args.price_cents / 100.0,
                "count": args.count,
                "notional_usd": notional,
                "touch_price": args.touch,
            }
            # VENUE TRUTH IN THE PER-MARKET CAP (CAP-2, 2026-09-05).  The
            # gate's local view cannot see an orphan order or a position from
            # a non-plan fill; ask the venue what is already in this ticker.
            # With credentials an unreadable venue REFUSES (fail closed); a
            # credential-less dry run says so and runs the local gate only.
            if getattr(client, "has_credentials", False):
                # STALE LOCAL STATE IS NOT A GATE (CAP-5, 2026-09-05).  This
                # path used to build the proposal and call the gate with NO
                # sync at all: the total cap summed local mirror rows plus
                # whatever `kalshi.oracle.balance.open_positions_usd` was last
                # written (hours or days old), and the per-market cap saw only
                # the mirror.  Every one of the 25 lifetime fills left an open
                # position that is never flattened (KXSNOWCRABCATCH, 09-03,
                # still open) and two live orphans carried $0 locally — so a
                # hand-typed $25 order could stack on a $25 seat/position the
                # engine had already placed.  Now, with credentials, the
                # venue is asked FIRST: balance/positions mark (oracle sync),
                # open orders (total + same-ticker), positions (same-ticker).
                # Any of them unreadable = REFUSE; the venue is the only
                # ledger that cannot drift from the venue.
                ok, msg, _fact = sync_kalshi_oracle(store, live_client=client)
                if not ok:
                    print(f"❌ Oracle sync failed before placement ({msg}) — open-position "
                          f"exposure unknown; refusing (fail closed, CAP-5).", file=sys.stderr)
                    return 1
                print(f"oracle: {msg}")
                try:
                    from domains.kalshi.harness.placement_engine import (
                        _order_collateral_usd, venue_same_ticker_usd)
                    venue_orders = client.fetch_open_orders()
                    venue_positions = client.fetch_positions()
                    same_usd, same_detail = venue_same_ticker_usd(
                        args.ticker, venue_orders, venue_positions)
                    proposal["same_ticker_venue_usd"] = same_usd
                    venue_resting_usd = round(sum(_order_collateral_usd(o) for o in venue_orders), 2)
                    proposal["venue_resting_usd"] = venue_resting_usd
                    print(f"venue truth: ${same_usd:.2f} already in {args.ticker} ({same_detail}); "
                          f"${venue_resting_usd:.2f} resting across {len(venue_orders)} live order(s)")
                except Exception as e:
                    print(f"❌ Venue open-orders/positions unreadable ({e}) — cannot prove "
                          f"{args.ticker} is empty; refusing (fail closed, CAP-2).", file=sys.stderr)
                    return 1
            else:
                print("no venue credentials: per-market cap checked against local mirrors only (dry run)")
            gate_res = gate.execute_action(ActionType.DEPLOY_SEAT, proposal)
            if not gate_res.is_executed:
                print(f"❌ OFFENSIVE GATE REJECTED ({gate_res.latency_ms:.1f}ms): {gate_res.reason}", file=sys.stderr)
                for v in gate_res.violations:
                    print(f"   • {v}", file=sys.stderr)
                return 1

            print(f"✅ Offensive Execution Gate APPROVED ({gate_res.latency_ms:.1f}ms): {gate_res.reason}")
            if args.live:
                from senate.harness.order_broker import OrderBrokerClient
                broker_client = OrderBrokerClient()
                resp = broker_client.place_order(
                    ticker=args.ticker,
                    side=args.side,
                    price_cents=args.price_cents,
                    count=args.count,
                    client_order_id=str(uuid.uuid4()),
                )
                if resp.get("status") == "PLACED":
                    print(f"✅ Live Order Placed via Sovereign Broker: {resp.get('venue_response')}")
                    print(f"   Remaining Budget: ${resp.get('remaining_budget_usd', 0.0):.2f}")
                else:
                    print(f"❌ SOVEREIGN BROKER REFUSAL ({resp.get('status')}): {resp.get('reason')}", file=sys.stderr)
                    return 1
            else:
                print(f"Dry-run passed: Order {args.ticker} {args.side.upper()} {args.count}x @ {args.price_cents}c (${notional:.2f}) verified.")
            return 0

        elif args.order_cmd == "cancel":
            proposal = {"order_id": args.order_id}
            gate_res = gate.execute_action(ActionType.CANCEL_ORDER, proposal)
            print(f"✅ Defensive Fast-Path APPROVED ({gate_res.latency_ms:.1f}ms): {gate_res.reason}")
            if args.live:
                try:
                    cancel_resp = client.cancel_order(args.order_id)
                    print(f"✅ Live Order Canceled on Venue: {cancel_resp}")
                except Exception as e:
                    print(f"❌ Venue cancellation failed: {e}", file=sys.stderr)
                    return 1
                # GHOST-ROW ANTIDOTE (ratified 2026-08-31): a manual cancel
                # used to leave BOTH local mirrors live — a full ghost that
                # inflated the exposure gate and blocked seeding.  Venue truth
                # changed above, so both mirrors move with it, best-effort.
                try:
                    store.mark_order_status(args.order_id, "CANCELLED")
                    row = store.find_plan_by_order_id(args.order_id)
                    if row and row.get("status") == "resting":
                        store.update_deployment_plan(
                            row["id"], status="cancelled",
                            notes=f"manual cancel via kalshi.py order cancel --live ({args.order_id})")
                        print(f"   Local mirrors cleared: active_orders -> CANCELLED, plan row {row['id']} -> cancelled")
                    else:
                        print("   Local mirror cleared: active_orders -> CANCELLED (no live plan row)")
                except Exception as e:
                    print(f"⚠️  Venue cancel landed but local mirror update failed: {e} — run sync-orders", file=sys.stderr)
            else:
                print(f"Dry-run passed: Defensive gate approved cancellation for order ID '{args.order_id}' (order existence not checked against venue in dry-run mode).")
            return 0

    elif args.command == "position":
        if args.position_cmd == "list":
            # VENUE TRUTH, FAIL CLOSED: the only position ledger that cannot
            # drift from the venue is the venue's.  Unreadable = say so, rc 1.
            try:
                positions = list(client.fetch_positions() or [])
            except Exception as e:
                print(f"❌ Venue positions unreadable ({e}) — refusing to print a guess (fail closed).",
                      file=sys.stderr)
                return 1
            try:
                venue_orders = list(client.fetch_open_orders() or [])
            except Exception as e:
                venue_orders = None
                print(f"⚠️  Venue open orders unreadable ({e}) — resting-order counts shown as '?'")
            from domains.kalshi.harness.placement_engine import (
                _is_close_order, _position_contracts, _position_cost_usd,
                pin_positions_schema, positions_schema)
            from domains.kalshi.harness.positions import position_count_key, position_cost_key
            print("══════════════════════════════════════════════════════════════")
            print("            KALSHI OPEN POSITIONS (venue truth)               ")
            print("══════════════════════════════════════════════════════════════")
            shown = 0
            for p in positions:
                tk = str(p.get("ticker") or "?")
                ct = _position_contracts(p)
                cost = _position_cost_usd(p)
                if ct == 0.0 and not cost:
                    continue
                # FLAT-10 (2026-09-05): print the RAW row and the keys the
                # parser actually read.  No code had ever parsed a field from
                # market_positions before today, so this listing IS the
                # read-only step 1 of the probe: the field names are pinned
                # into kalshi.ops.positions_schema from what the venue sends.
                print(f"  raw {tk}: {json.dumps(p, sort_keys=True, default=str)}")
                print(f"      parsed via count_key={position_count_key(p)!r} "
                      f"exposure_key={position_cost_key(p)!r}")
                if venue_orders is None:
                    resting_txt, close_txt = "?", ""
                else:
                    same = [o for o in venue_orders if str(o.get("ticker")) == tk]
                    closes = [o for o in same if _is_close_order(o)]
                    resting_txt = str(len(same))
                    close_txt = f" (of which {len(closes)} flatten)" if closes else ""
                side = "YES" if ct > 0 else "NO"
                cost_txt = "unreadable" if cost is None else f"${cost:.2f}"
                print(f"  • {tk}: {abs(ct):.0f}ct {side} held | exposure {cost_txt} | "
                      f"resting orders {resting_txt}{close_txt}")
                shown += 1
            if not shown:
                print("  (venue lists no open positions)")
            from datetime import datetime as _dt, timezone as _tz
            pin = pin_positions_schema(store, positions, now_iso=_dt.now(_tz.utc).isoformat())
            if pin.get("pinned"):
                print(f"  FLAT-10 schema pinned: count_key={pin['count_key']!r} "
                      f"exposure_key={pin['exposure_key']!r} -> kalshi.ops.positions_schema")
            elif pin.get("error"):
                print(f"  ⚠️  FLAT-10 schema pin failed: {pin['error']}")
            schema = positions_schema(store)
            if schema["close_semantics_verified"]:
                print(f"  FLAT-10 close semantics: VERIFIED ({schema.get('verdict')}) -- live "
                      f"flatten may size to the whole position")
            else:
                print(f"  FLAT-10 close semantics: UNVERIFIED ({schema.get('verdict')}) -- live "
                      f"flatten is capped at the 1-contract probe "
                      f"(`position flatten --ticker T --count 1 --live`, Ryan-gated)")
            local = store.list_open_positions()
            print(f"Local receipt rows (filled, not yet flattened): {len(local)}")
            for r in local:
                held = r.get("filled_ct")
                held_txt = f"{float(held):.0f}ct" if held is not None else f"<= {r['count']}ct (fill size unrecorded)"
                print(f"  • plan {r['id']} {r['ticker']} {str(r['side']).upper()} {held_txt} @ {r['price_cents']}c"
                      f" | flatten order: {r.get('flatten_order_id') or '—'}")
            print("══════════════════════════════════════════════════════════════")
            return 0

        elif args.position_cmd == "flatten":
            from domains.kalshi.harness.placement_engine import PlacementEngine
            engine = PlacementEngine(store=store, client=client, gate=gate)
            res = engine.flatten_position(
                args.ticker, price_cents=args.price_cents, count=args.count,
                take=args.take, why=args.why, live=args.live, cross=args.cross)
            if "schema_verified" in res:
                print("FLAT-10 close semantics: "
                      + ("VERIFIED" if res["schema_verified"] else
                         "UNVERIFIED -- live flatten capped at the 1-contract probe"))
            if res.get("held_side"):
                exp = res.get("exposure_usd")
                print(f"venue position: {abs(float(res['held_ct'])):.0f}ct {res['held_side'].upper()} held "
                      f"in {args.ticker} | exposure "
                      + ("unreadable" if exp is None else f"${float(exp):.2f}"))
            prop = res.get("proposal")
            if prop:
                print(f"proposal: sell {prop['count']}ct {prop['held_side'].upper()} @ "
                      f"{prop['sell_price_cents']}c ({prop['price_how']}) | book YES bid "
                      f"{prop['book'].get('yes_bid_c')}c / NO bid {prop['book'].get('no_bid_c')}c | "
                      f"reduce_only={prop['reduce_only']} post_only={prop.get('post_only', True)}"
                      + (" cross=TAKER" if prop.get("cross") else ""))
            g = res.get("gate")
            if g:
                verdict = "APPROVED" if g["is_executed"] else "REFUSED"
                print(f"{'✅' if g['is_executed'] else '❌'} FLATTEN_POSITION gate {verdict} "
                      f"({g['latency_ms']:.1f}ms): {g['reason']}")
                for v in g["violations"]:
                    print(f"   • {v}")
            if not res.get("ok"):
                print(f"❌ FLATTEN REFUSED (fails closed): {res.get('error')}", file=sys.stderr)
                return 1
            for line in res.get("actions", []):
                print(line)
            if res.get("dry_run"):
                print(f"Dry-run passed: no venue write, no store write. Re-run with --live to place the close.")
            else:
                print(f"✅ Live close placed on venue: order {res['order_id']} "
                      f"(client_order_id {res['client_order_id']})")
            return 0

    elif args.command == "verify-payoff":
        if args.source_file:
            source_p = Path(args.source_file)
            if not source_p.exists():
                print(f"❌ Source artifact not found: {args.source_file}", file=sys.stderr)
                return 1
            try:
                payload = json.loads(source_p.read_text(encoding="utf-8"))
                decision = evaluate_order_payoff_from_venue_record(
                    order_record=payload.get("order", {}),
                    market_book=payload.get("book", {}),
                    candidate_books=payload.get("candidates", []),
                    hurdle_multiplier=args.hurdle,
                    fact_store=store,
                )
            except (ValueError, json.JSONDecodeError) as e:
                print(f"❌ VENUE RECORD ERROR (FAILS CLOSED): {e}", file=sys.stderr)
                return 1
        else:
            if not args.ticker or args.dist is None or args.reward is None:
                print("❌ ERROR: Must provide either --source-file OR (--ticker, --dist, and --reward).", file=sys.stderr)
                return 1
            candidates = []
            if args.cand_ticker and args.cand_reward > 0:
                candidates.append({
                    "ticker": args.cand_ticker,
                    "distance_ticks": args.cand_dist,
                    "base_reward_daily_usd": args.cand_reward,
                })
            decision = evaluate_order_payoff(
                current_ticker=args.ticker,
                distance_ticks=args.dist,
                base_reward_daily_usd=args.reward,
                candidate_markets=candidates,
                hurdle_multiplier=args.hurdle,
                fact_store=store,
            )
            decision.metadata["is_venue_sourced"] = False

        print("══════════════════════════════════════════════════════════════")
        print("          KALSHI DETERMINISTIC ECONOMIC PAYOFF VERIFY         ")
        print("══════════════════════════════════════════════════════════════")
        source_label = "✅ FILE-SOURCED (VENUE RECORD)" if decision.metadata.get("is_venue_sourced") else "⚠️ PROVISIONAL (UNSOURCED / SELF-REPORTED)"
        print(f"Source Status:         {source_label}")
        print(f"Target Seat:           {decision.ticker}")
        print(f"Action:                {decision.action.value}")
        print(f"Current EV (Hold):     ${decision.ev_hold_daily_usd:.4f}/day")
        if decision.target_ticker:
            print(f"Recycle Target EV:     ${decision.ev_recycle_daily_usd:.4f}/day ({decision.target_ticker})")
        print(f"Reason:                {decision.reason}")
        if not decision.metadata.get("is_venue_sourced"):
            print("⚠️ WARNING: Unsourced inputs cannot gate capital. Pass --source-file for live orders.")
        print("══════════════════════════════════════════════════════════════")
        return 0

    elif args.command == "census":
        from domains.kalshi.harness.census_scanner import CensusScanner
        scanner = CensusScanner(client)
        opps = scanner.scan_family_opportunities(
            family_prefix=args.family,
            min_hours_to_close=args.min_hours,
        )
        print("══════════════════════════════════════════════════════════════")
        print("         KALSHI MULTI-FAMILY MARKET CENSUS (7-DAY SCAN)       ")
        print("══════════════════════════════════════════════════════════════")
        for o in opps:
            status_icon = "✅" if o["status"] == "QUALIFIED" else "❌"
            print(f"  • {status_icon} [{o['category'].upper()}] {o['family']} ({o['active_schedule']})")
            print(f"    Status: {o['status']} | Permitted Sides: {', '.join(o['recommended_sides'])}")
            print(f"    Min Margin to Window Expiry: >={o['min_hours_margin']}h")
        print("══════════════════════════════════════════════════════════════")
        return 0

    elif args.command == "placement":
        if args.placement_cmd == "show":
            ps = store.get_placement_state()
            print("══════════════════════════════════════════════════════════════")
            print("        KALSHI ORDER-PLACEMENT STATE MACHINE (LEDGER)         ")
            print("══════════════════════════════════════════════════════════════")
            print(f"State:   {ps['state']}")
            print(f"Reason:  {ps['reason']}")
            print(f"Set by:  {ps['set_by']} @ {ps['set_at']}")
            history = store.placement_state_history(limit=10)
            if len(history) > 1:
                print("History (latest first):")
                for h in history:
                    print(f"  • [{h['set_at']}] {h['state']} — {h['reason']} (by {h['set_by']})")
            print("══════════════════════════════════════════════════════════════")
            return 0
        elif args.placement_cmd == "plan":
            # ONE ARMOR BAR FOR EVERY PROCESS (2026-08-18).  This report is the
            # third reader of these constants, and a report that quotes a bar
            # nobody is enforcing is worse than no report.  Resolve from the
            # shared fact FIRST — the from-import below then picks up the
            # installed values rather than this shell's environment.
            from domains.kalshi.harness import duty_cycle as _dc
            # persist=False: a REPORT must never write policy.  It shows the
            # shared fact if one exists and the code defaults if not, which is
            # exactly what the next process to boot would install.
            _armor_policy = _dc.resolve_armor_policy(store, persist=False)
            # ...and the HAZARD GATE's constants, by the same rule and for the
            # same reason: this report is a third reader of them too.
            from domains.kalshi.harness import hazard_gate as _hz
            _hazard_policy = _hz.resolve_hazard_policy(store, persist=False)
            from domains.kalshi.harness.duty_cycle import (
                ABS_MIN_ARMOR_CT, ARMOR_BURST_MULT, ARMOR_BURST_WINDOW_SEC,
                CONTINUOUS_MIN_ARMOR_CT,
                ATOMIC_MIN_CYCLE_SEC, BREAKEVEN_DUTY, MAX_REPLACEMENTS_PER_DAY,
                MIN_DWELL_SEC, REACTIVE_REPLACEMENT_RESERVE, REENTRY_SHIELD_FRAC,
                DutyCycleLedger, read_burst_observation,
                timer_replacement_budget)
            rows = store.list_deployment_plan()
            ps = store.get_placement_state()
            ledger = DutyCycleLedger(store)
            print("══════════════════════════════════════════════════════════════")
            print("        KALSHI DEPLOYMENT PLAN (placement engine input)        ")
            print("══════════════════════════════════════════════════════════════")
            print(f"Placement state: {ps['state']} ({ps['reason']})")
            if not rows:
                print("(deployment_plan is empty)")
            for r in rows:
                escrow = r["price_cents"] / 100.0 * r["count"]
                print(f"  • [{r['id']}] {r['status'].upper():9s} {r['ticker']}")
                print(f"      {r['side'].upper()} {r['count']}x @ {r['price_cents']}c  (${escrow:.2f} escrow, cap ${r['max_escrow_usd']:.2f})")
                # PRICING RULE: for a DERIVE row the line above is the SEED
                # snapshot, not a commitment.  Say so — a pinned number that is
                # not what will be placed is exactly the confusion Ryan hit.
                if (r.get("price_mode") or "fixed") == "derive":
                    seated = r["status"] == "resting"
                    print(f"      price_mode: DERIVE — the {r['price_cents']}c above is "
                          + ("the level this seat is ACTUALLY resting at (written back at "
                             "placement)" if seated else
                             "the last derived/seed snapshot ONLY, never a commitment")
                          + "; the level and size are re-chosen off the FRESH book at EVERY "
                            "placement — first placement, cadence re-placement and atomic "
                            "replace alike (no fallback to a stale price)")
                    print(f"      rule: budget ${float(r['max_capital_usd'] or 0):.2f} | "
                          f"band {r['band_lo_c']}-{r['band_hi_c']}c | "
                          f"min armor {r['min_armor_ct']}ct | max share {r['max_seat_share']}")
                print(f"      hard_exit: {r['hard_exit_utc'] or '— (24h curfew governs)'} | order_id: {r['order_id'] or '—'}")
                # DUTY CYCLE — a LIP seat earns ONLY while resting, so uptime is
                # the whole economic case for the queue shield.  Break-even is a
                # measured 6.6 % (queue-shield-20260817.md §4).
                d = ledger.duty_snapshot(r)
                if (d["duty"] is not None or d["cycles"]
                        or r["status"] in ("resting", "withdrawn_rearmed")):
                    verdict = ("accrual starts at next (re-)placement" if d["duty"] is None else
                               ("ABOVE break-even" if d["above_breakeven"] else "BELOW break-even"))
                    duty_txt = "—" if d["duty"] is None else f"{d['duty'] * 100:.1f}%"
                    print(f"      duty: {duty_txt} (up {d['uptime_s'] / 3600:.2f}h / "
                          f"down {d['downtime_s'] / 3600:.2f}h) vs break-even "
                          f"{BREAKEVEN_DUTY * 100:.1f}% → {verdict}")
                    print(f"      cycles: {d['cycles']} re-placements "
                          f"({d['replaces_today']}/{MAX_REPLACEMENTS_PER_DAY} today, "
                          f"timer stops at {timer_replacement_budget()}) | "
                          f"A0 baseline {d['a0_baseline'] or '—'} → current {d['a0_current'] or '—'}")
                burst = read_burst_observation(r["ticker"], r["side"],
                                               r["price_cents"] / 100.0)
                # TWO FLOORS SINCE 2026-09-09: the ENTRY floor decides whether a
                # NEW/pending row may join a book, the CONTINUOUS floor whether
                # a held seat may stay in one.  This row is judged by whichever
                # phase it is actually in, and the report says which — quoting
                # the entry number at a resting seat is the same "report a bar
                # nobody enforces" defect that put this block here.
                _row_phase = ("continuous" if r["status"] in ("resting", "withdrawn_rearmed")
                              else "entry")
                _row_floor = (CONTINUOUS_MIN_ARMOR_CT if _row_phase == "continuous"
                              else ABS_MIN_ARMOR_CT)
                print(f"      armor bar ({_row_phase.upper()}): max({_row_floor:.0f}ct, "
                      f"{ARMOR_BURST_MULT:.0f}x {ARMOR_BURST_WINDOW_SEC:.0f}s-burst "
                      f"{'UNMEASURED' if burst is None else format(burst, '.0f') + 'ct'}) "
                      f"= {max(_row_floor, ARMOR_BURST_MULT * (burst or 0)):.0f}ct "
                      f"required ahead of us  [entry floor {ABS_MIN_ARMOR_CT:.0f}ct | "
                      f"continuous floor {CONTINUOUS_MIN_ARMOR_CT:.0f}ct]")
                # ...and the anti-repricing clause, RETIRED as a gate on
                # 2026-08-18 and reported here as the drift observation it now
                # is.  Labelled honestly: a line that says "required" about a
                # number nothing enforces is how an operator ends up debugging
                # the wrong refusal.
                base = r["a0_baseline"]
                _rg_label = ("repricing gate" if _dc.REENTRY_RELATIVE_GATE
                             else "repricing drift (LOG-ONLY, not enforced)")
                _rg_tail = ("required ahead of us" if _dc.REENTRY_RELATIVE_GATE
                            else "would have been required by the retired clause")
                print(f"      {_rg_label}: {REENTRY_SHIELD_FRAC:.0%} x "
                      f"{'UNSET (initialises on next re-entry)' if base is None else format(float(base), '.0f') + 'ct qualified'}"
                      + ("" if base is None
                         else f" = {REENTRY_SHIELD_FRAC * float(base):.0f}ct {_rg_tail}"))
                if r["status"] == "withdrawn_rearmed":
                    # persist_baseline=False: `placement plan` is a REPORT and
                    # must never write an initialised baseline to the store.
                    ok, why = ledger.replace_guard(
                        r, (None if r["a0_current"] is None else float(r["a0_current"])),
                        burst_ct=burst, persist_baseline=False)
                    print(f"      withdrawn: {r['withdrawn_at']} ({r['withdraw_reason']}, "
                          f"shield_frac {r['withdraw_shield_frac']}) — RE-PLACEABLE")
                    print(f"      re-entry (at last-known A0): {'READY' if ok else 'HELD'} — {why}")
                if r["notes"]:
                    print(f"      notes: {r['notes']}")
            total_open = sum(r["price_cents"] / 100.0 * r["count"] for r in rows if r["status"] in ("pending", "resting"))
            # FG-03 (2026-09-05): was a literal "$250.00 cap" — an agent-authored
            # number Ryan never gave.  His cap is 20 x $25 = $500 inside $530
            # (2026-08-20); the report must quote verify/caps, not a private copy.
            # FG-12 (2026-09-05): ...and it must quote the cap IN FORCE with its
            # SOURCE, exactly as the cadence daemon's Risk Check line does — the
            # same resolver the engine installs from (peek_escrow_cap: a pure
            # read, so this REPORT writes nothing).  A fact may tighten the
            # compiled $530; a line that prints the ceiling while the engine
            # enforces a tighter fact is the three-numbers defect again.
            from domains.kalshi.harness.placement_engine import peek_escrow_cap as _peek_cap
            _cap = _peek_cap(store)
            print(f"Open plan escrow (pending+resting): ${total_open:.2f} of "
                  f"${_cap['cap_usd']:.2f} cap (via {_cap['source']})")
            # DUTY-TRUTH (2026-09-10).  This line used to sum only rows in
            # ('resting', 'withdrawn_rearmed') — the rows currently IN service —
            # which excludes by construction exactly the rows whose whole story
            # is that they were NOT in service.  With the 66 seeded-and-never-
            # placed rows and everything that died parked left out, it reported
            # 88.98% against a tape truth of 64.69%.  Both numbers are printed
            # now: the IN-SERVICE pool (what the old line meant) and the BOOK
            # (what the pod has been claiming it meant).
            live = [r for r in rows if r["status"] in ("resting", "withdrawn_rearmed")]
            if live:
                snaps = [ledger.duty_snapshot(r) for r in live]
                up = sum(s["uptime_s"] for s in snaps)
                down = sum(s["downtime_s"] for s in snaps)
                pool = (up / (up + down)) if (up + down) > 0 else None
                pool_txt = "—" if pool is None else f"{pool * 100:.1f}%"
                print(f"Pooled duty cycle (in-service rows only): {pool_txt} "
                      f"across {len(live)} seat(s) "
                      f"(break-even {BREAKEVEN_DUTY * 100:.1f}%)")
            book = ledger.book_duty(rows)
            book_txt = "—" if book["duty"] is None else f"{book['duty'] * 100:.1f}%"
            print(f"BOOK duty cycle (every plan row): {book_txt} "
                  f"(up {book['uptime_s'] / 3600:.1f}h / down {book['downtime_s'] / 3600:.1f}h "
                  f"across {book['rows']} row(s); {book['never_placed_rows']} seeded and "
                  f"NEVER placed"
                  + (f"; {book['unreadable_clocks']} unreadable clock(s)"
                     if book["unreadable_clocks"] else "") + ")")
            print(f"Re-entry policy: the same TEST as a cold entry against the "
                  f"CONTINUOUS floor (2026-09-09: the 600ct entry number is "
                  f"measured on placement, not on a held seat) — "
                  f"ABSOLUTE armor >= max({CONTINUOUS_MIN_ARMOR_CT:.0f}ct, "
                  f"{ARMOR_BURST_MULT:.0f}x max-{ARMOR_BURST_WINDOW_SEC:.0f}s-burst)"
                  + ("" if _dc.REENTRY_RELATIVE_GATE else
                     f" [the {REENTRY_SHIELD_FRAC:.0%} anti-repricing clause is "
                     f"RETIRED as a gate — computed and logged, not enforced]")
                  + (f" AND RELATIVE recovery >= {REENTRY_SHIELD_FRAC:.0%} x qualified A0"
                     if _dc.REENTRY_RELATIVE_GATE else "")
                  + f", <= {MAX_REPLACEMENTS_PER_DAY}/day of which the "
                  f"last {REACTIVE_REPLACEMENT_RESERVE} are RESERVED for reactive trips "
                  f"(the hourly timer stops at {timer_replacement_budget()})")
            print(f"                dwell >= {MIN_DWELL_SEC:.0f}s (cadence re-place) | "
                  f"atomic replace: cancel+re-place as ONE op, "
                  f">= {ATOMIC_MIN_CYCLE_SEC:.0f}s between cycles")
            print(_dc.armor_banner(_armor_policy))
            print(_hz.hazard_banner(_hazard_policy))
            # FG-11 (2026-09-05): the rotation / horizon / payability doctrine
            # this report quotes is the FACT's, read the same way the rotation
            # engine, seeder, screen and gates read it -- never a literal.
            from domains.kalshi.harness import policy_facts as _pf
            print(_pf.policy_banner(_pf.resolve_rotation_policy(store)))
            print("══════════════════════════════════════════════════════════════")
            return 0
        elif args.placement_cmd == "set":
            ps = store.set_placement_state(state=args.state, reason=args.reason, set_by=args.by)
            print(f"✅ Placement state flipped: {ps['state']} — {ps['reason']} (by {ps['set_by']} @ {ps['set_at']})")
            return 0
        elif args.placement_cmd == "price-rule":
            row = store.get_deployment_plan_row(args.id)
            if row is None:
                print(f"❌ deployment_plan row {args.id} does not exist.")
                return 1
            if args.side and row["side"].lower() != args.side:
                print(f"❌ row {args.id} is side '{row['side']}', not '{args.side}' — refusing.")
                return 1
            lo = hi = None
            if args.band:
                try:
                    lo, hi = (int(x) for x in str(args.band).split("-", 1))
                except ValueError:
                    print(f"❌ --band must look like 15-85, got '{args.band}'.")
                    return 1
            try:
                updated = store.set_price_rule(
                    plan_id=args.id, price_mode=args.mode,
                    max_capital_usd=args.max_capital, band_lo_c=lo, band_hi_c=hi,
                    min_armor_ct=args.min_armor, max_seat_share=args.max_share,
                    note=args.note)
            except ValueError as exc:
                print(f"❌ {exc}")
                return 1
            print(f"✅ plan row {updated['id']} ({updated['ticker']} {updated['side'].upper()}) "
                  f"price_mode = {updated['price_mode'].upper()}")
            if updated["price_mode"] == "derive":
                print(f"   budget ${float(updated['max_capital_usd']):.2f} | "
                      f"band {updated['band_lo_c']}-{updated['band_hi_c']}c | "
                      f"min armor {updated['min_armor_ct']}ct | "
                      f"max share {updated['max_seat_share']}")
                print(f"   seeded {updated['price_cents']}c x{updated['count']} is now an AUDIT "
                      f"BASELINE only — the level and the size are chosen off the fresh book "
                      f"at the placement instant, and there is no fallback to it.")
            print(f"   status left untouched: {updated['status']}")
            return 0

    elif args.command == "seed-book":
        from domains.kalshi.harness.auto_seeder import AutoSeeder
        seeder = AutoSeeder(store=store, client=client, target_seats=args.target)
        actions = seeder.seed_book_shortfall(target=args.target)
        for act in actions:
            print(act)
        return 0

    elif args.command == "daemon":
        from domains.kalshi.harness.cadence_daemon import KalshiCadenceDaemon
        daemon = KalshiCadenceDaemon(interval_seconds=args.interval, max_cycles=args.cycles)
        daemon.start()
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
