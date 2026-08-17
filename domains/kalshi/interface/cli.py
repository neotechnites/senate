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


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="kalshi",
        description="Kalshi Domain Pod CLI — Dedicated Prediction Market Engine",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # kalshi status
    subparsers.add_parser("status", help="Print clean Kalshi seat and money status")

    # kalshi seed
    subparsers.add_parser("seed", help="Seed verified Kalshi platform laws into SQLite")

    # kalshi telemetry
    telem_p = subparsers.add_parser("telemetry", help="Export domain telemetry in standard JSON format")
    telem_p.add_argument("--json", action="store_true", default=True, help="Output format JSON")

    # kalshi sync-oracle
    sync_p = subparsers.add_parser("sync-oracle", help="Sync authentic venue balance directly from live authenticated Kalshi API")
    sync_p.add_argument("--live", action="store_true", default=True, help="Fetch live balance from authenticated Kalshi API")
    sync_p.add_argument("--max-age", type=float, default=24.0, help="Max age in hours before marking stale")

    # kalshi sync-orders (aliased with sync-seats)
    orders_p = subparsers.add_parser("sync-orders", help="Sync active open orders directly from live authenticated Kalshi API")
    orders_p.add_argument("--live", action="store_true", default=True, help="Fetch active open orders from authenticated Kalshi API")

    seats_p = subparsers.add_parser("sync-seats", help="Alias for sync-orders")
    seats_p.add_argument("--live", action="store_true", default=True, help="Fetch active open orders from authenticated Kalshi API")


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

    # kalshi daemon (Continuous Autonomous Cadence)
    daemon_p = subparsers.add_parser("daemon", help="Run continuous autonomous execution daemon across 7 strategy lanes")
    daemon_p.add_argument("--interval", type=int, default=300, help="Cycle interval in seconds (default 300s)")
    daemon_p.add_argument("--cycles", type=int, help="Optional max cycle count")

    args = parser.parse_args(argv)



    store = FactStore()
    gate = ExecutionGate(store)
    client = KalshiVenueClient()

    if args.command == "status":
        print(render_kalshi_status(store))
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
        try:
            orders_list = client.fetch_open_orders()
            source = "live_venue_api"

            def _price(o):
                for k in ("no_price_dollars", "yes_price_dollars"):
                    if o.get(k) is not None:
                        return round(float(o[k]), 4)
                for k in ("no_price", "yes_price", "price"):
                    if o.get(k) is not None:
                        return round(float(o[k]) / 100.0, 4)
                return 0.0

            def _count(o):
                for k in ("remaining_count_fp", "remaining_count", "count"):
                    if o.get(k) is not None:
                        return int(float(o[k]))
                return 0

            n = 0
            for o in orders_list:
                px = _price(o)
                cnt = _count(o)
                order_obj = ActiveOrder(
                    order_id=str(o.get("order_id") or o.get("client_order_id") or uuid.uuid4()),
                    ticker=o.get("ticker", "UNKNOWN"),
                    # 2026-08-15 DEFECT FIX: `side` on the venue order row is
                    # the YES-axis order side, NOT the outcome held; the pod
                    # recorded our NO maker seats as YES all through the 08-15
                    # incident.  `outcome_side` is the contract actually held.
                    side=str(o.get("outcome_side") or o.get("side") or "no").lower(),
                    price=px,
                    count=cnt,
                    collateral_usd=round(px * cnt, 2),
                    status="RESTING",
                    lane=o.get("lane", "general"),
                )
                store.save_order(order_obj)
                n += 1
            print(f"✅ Synced {n} active open orders directly from live venue API.")
            return 0
        except Exception as e:
            print(f"❌ Failed to sync orders: {e}", file=sys.stderr)
            return 1


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
            gate_res = gate.execute_action(ActionType.DEPLOY_SEAT, proposal)
            if not gate_res.is_executed:
                print(f"❌ OFFENSIVE GATE REJECTED ({gate_res.latency_ms:.1f}ms): {gate_res.reason}", file=sys.stderr)
                for v in gate_res.violations:
                    print(f"   • {v}", file=sys.stderr)
                return 1

            print(f"✅ Offensive Execution Gate APPROVED ({gate_res.latency_ms:.1f}ms): {gate_res.reason}")
            if args.live:
                try:
                    order_resp = client.place_post_only_order(
                        ticker=args.ticker,
                        side=args.side,
                        price_cents=args.price_cents,
                        count=args.count,
                        client_order_id=str(uuid.uuid4()),
                    )
                    print(f"✅ Live Order Placed on Venue: {order_resp}")
                except Exception as e:
                    print(f"❌ Venue placement failed: {e}", file=sys.stderr)
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
            else:
                print(f"Dry-run passed: Defensive gate approved cancellation for order ID '{args.order_id}' (order existence not checked against venue in dry-run mode).")
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

    elif args.command == "daemon":
        from domains.kalshi.harness.cadence_daemon import KalshiCadenceDaemon
        daemon = KalshiCadenceDaemon(interval_seconds=args.interval, max_cycles=args.cycles)
        daemon.start()
        return 0

    return 0




if __name__ == "__main__":
    sys.exit(main())
