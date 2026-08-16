"""Unified CLI interface for The Senate Core Framework."""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from senate.interface.decision_matrix import render_senate_status
from senate.state.fact_store import FactStore
from senate.state.models import Fact, Trial
from senate.state.seeds import seed_database
from senate.verify.payoff import evaluate_order_payoff
from senate.verify.statistics import price_n_hurdle


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="senate",
        description="The Senate Core Framework CLI — Deterministic AI Orchestration",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # senate status
    subparsers.add_parser("status", help="Print clean, high-density system status matrix")

    # senate seed
    subparsers.add_parser("seed", help="Initialize and seed the FactStore with ground-truth constants")

    # senate fact
    fact_parser = subparsers.add_parser("fact", help="Inspect and manage ground-truth facts")
    fact_sub = fact_parser.add_subparsers(dest="fact_cmd", required=True)

    fact_list = fact_sub.add_parser("list", help="List all verified facts")
    fact_list.add_argument("--domain", help="Filter facts by domain")

    fact_get = fact_sub.add_parser("get", help="Get a single fact by key")
    fact_get.add_argument("key", help="Fact key (e.g. kalshi.lip.discount_factor)")

    fact_set = fact_sub.add_parser("set", help="Set or update a fact")
    fact_set.add_argument("key", help="Fact key")
    fact_set.add_argument("domain", help="Fact domain")
    fact_set.add_argument("value", help="JSON value string or scalar")
    fact_set.add_argument("source", help="Source artifact citation")
    # senate domain
    domain_p = subparsers.add_parser("domain", help="Manage and scaffold isolated Domain Pods")
    domain_sub = domain_p.add_subparsers(dest="domain_cmd", required=True)

    domain_list_p = domain_sub.add_parser("list", help="List all provisioned domain pods")

    domain_create_p = domain_sub.add_parser("create", help="Scaffold a new isolated domain pod")
    domain_create_p.add_argument("domain_id", help="Unique identifier (e.g. automotive, jujitsu)")
    domain_create_p.add_argument("name", help="Human-readable name (e.g. 'Automotive Chassis')")
    domain_create_p.add_argument("--desc", default="Dedicated domain pod", help="Domain mission/description")
    domain_create_p.add_argument("--category", default="general", help="Category (e.g. physical, software, financial)")

    domain_status_p = domain_sub.add_parser("status", help="Get status of a specific domain pod")
    domain_status_p.add_argument("domain_id", help="Domain identifier")

    domain_sync_p = domain_sub.add_parser("sync", help="Pull verified telemetry from domain pod into Senate Hub")
    domain_sync_p.add_argument("domain_id", help="Domain identifier")

    domain_delete_p = domain_sub.add_parser("delete", help="Delete a domain pod from disk and unregister from Senate")
    domain_delete_p.add_argument("domain_id", help="Domain identifier")

    # senate audit (Multi-Model Adversarial Audit)

    audit_p = subparsers.add_parser("audit", help="Run independent multi-model adversarial audit on a proposal")
    audit_p.add_argument("proposal", help="Proposal text or path to proposal file")
    audit_p.add_argument("--invariants", nargs="*", default=[], help="List of enforced invariants")
    audit_p.add_argument("--provider", default="cli", help="Auditor provider (cli, google, openai, anthropic)")
    audit_p.add_argument("--model", help="Auditor model name")

    # senate trials
    trials_parser = subparsers.add_parser("trials", help="Multiple-testing ledger and N-pricing")
    trials_sub = trials_parser.add_subparsers(dest="trials_cmd", required=True)


    trials_log = trials_sub.add_parser("log", help="Log a trial to the ledger")
    trials_log.add_argument("project", help="Project identifier (e.g. nestor)")
    trials_log.add_argument("description", help="Configuration description")
    trials_log.add_argument("--count", type=int, default=1, help="Number of trials / variants tested")

    trials_sub.add_parser("summary", help="Show global and per-project N counts with statistical hurdles")

    # senate sync-oracle
    sync_p = subparsers.add_parser("sync-oracle", help="Sync live venue balance from oracle JSON artifact")

    sync_p.add_argument("--file", help="Path to authentic oracle truth_latest.json")
    sync_p.add_argument("--max-age", type=float, default=24.0, help="Max age in hours before marking stale (default 24h)")

    # senate verify-payoff
    payoff_p = subparsers.add_parser("verify-payoff", help="Compute deterministic EV(Hold) vs EV(Recycle)")

    payoff_p.add_argument("--source-file", help="Path to authentic venue JSON record (order and book snapshot)")
    payoff_p.add_argument("--ticker", help="Current position ticker")
    payoff_p.add_argument("--dist", type=int, help="Distance in ticks from touch (0=at touch)")
    payoff_p.add_argument("--reward", type=float, help="Base daily reward USD at touch")
    payoff_p.add_argument("--cand-ticker", help="Alternative candidate ticker")
    payoff_p.add_argument("--cand-dist", type=int, default=0, help="Candidate distance in ticks from touch")
    payoff_p.add_argument("--cand-reward", type=float, default=0.0, help="Candidate base daily reward USD")
    payoff_p.add_argument("--hurdle", type=float, default=1.5, help="Recycle hurdle multiplier (default 1.5x)")

    # senate verify-hurdle
    hurdle_p = subparsers.add_parser("verify-hurdle", help="Calculate Bonferroni and Deflated Sharpe hurdles for N trials")
    hurdle_p.add_argument("--n", type=int, required=True, help="Total trial count N")
    hurdle_p.add_argument("--alpha", type=float, default=0.05, help="Family-wise error rate alpha")
    hurdle_p.add_argument("--obs", type=int, default=0, help="Observation count for Sharpe conversion")

    # senate ideate
    ideate_p = subparsers.add_parser("ideate", help="Standing multi-model ideation organ (Claude + Gemini dialectic)")
    ideate_sub = ideate_p.add_subparsers(dest="ideate_cmd", required=True)
    ideate_propose = ideate_sub.add_parser("propose", help="Propose a hypothesis and run multi-model adversarial audit")
    ideate_propose.add_argument("domain", help="Domain identifier (e.g. kalshi)")
    ideate_propose.add_argument("hypothesis", help="Hypothesis statement")
    ideate_propose.add_argument("--kill-test", default="{}", help="JSON kill test specification")
    ideate_propose.add_argument("--model", default="claude-3-7-sonnet", help="Proposing model name")

    ideate_list = ideate_sub.add_parser("list", help="List registered ideas, survivors, and graveyard")
    ideate_list.add_argument("--domain", help="Filter by domain")
    ideate_list.add_argument("--status", choices=["GRAVEYARD", "VALIDATED", "INCUBATING"], help="Filter by status")

    # senate mistakes
    mistakes_p = subparsers.add_parser("mistakes", help="Mistake-to-impossibility ledger and verification")
    mistakes_sub = mistakes_p.add_subparsers(dest="mistakes_cmd", required=True)
    mistakes_sub.add_parser("list", help="List all 10 compiled mistake invariants")
    mistakes_sub.add_parser("seed", help="Seed mistake invariants into SQLite database")

    # senate daemon (Continuous Autonomous Cadence)
    daemon_p = subparsers.add_parser("daemon", help="Run continuous autonomous cadence loop (Idle is a bug)")
    daemon_p.add_argument("--interval", type=int, default=300, help="Cycle interval in seconds (default 300s)")
    daemon_p.add_argument("--cycles", type=int, help="Optional max cycle count")

    args = parser.parse_args(argv)


    store = FactStore()

    if args.command == "status":
        print(render_senate_status(store))
        return 0

    elif args.command == "seed":
        seed_database(store)
        facts = store.list_facts()
        print(f"✅ FactStore seeded successfully. {len(facts)} ground-truth facts active in SQLite.")
        return 0

    elif args.command == "fact":
        if args.fact_cmd == "list":
            facts = store.list_facts(domain=args.domain)
            print(f"Found {len(facts)} fact(s):")
            for f in facts:
                print(f"  • [{f.domain}] {f.key}: {json.dumps(f.value)} (source: {f.source_artifact})")
            return 0
        elif args.fact_cmd == "get":
            fact = store.get_fact(args.key)
            if not fact:
                print(f"❌ Fact not found: {args.key}", file=sys.stderr)
                return 1
            print(json.dumps(fact.to_dict(), indent=2))
            return 0
        elif args.fact_cmd == "set":
            try:
                parsed_val = json.loads(args.value)
            except Exception:
                parsed_val = args.value
            fact = Fact(
                key=args.key,
                domain=args.domain,
                value=parsed_val,
                source_artifact=args.source,
                is_immutable=args.immutable,
            )
            try:
                store.set_fact(fact)
                print(f"✅ Fact saved: {args.key}")
                return 0
            except ValueError as e:
                print(f"❌ ERROR: {e}", file=sys.stderr)
                return 1

    elif args.command == "domain":
        from senate.scaffold.domain_builder import list_domain_pods, scaffold_domain_pod

        if args.domain_cmd == "list":
            pods = list_domain_pods(store)
            print("══════════════════════════════════════════════════════════════")
            print("                   SENATE DOMAIN PODS                         ")
            print("══════════════════════════════════════════════════════════════")
            if not pods:
                print("  (No domain pods provisioned. Create one via 'senate domain create <id> <name>')")
            else:
                for p in pods:
                    print(f"  • [{p.category.upper()}] {p.name} ({p.domain_id})")
                    print(f"    Path: {p.path} | Active Lanes: {', '.join(p.active_lanes)}")
                    print(f"    Mission: {p.description}")
            print("══════════════════════════════════════════════════════════════")
            return 0

        elif args.domain_cmd == "create":
            try:
                pod_path = scaffold_domain_pod(
                    domain_id=args.domain_id,
                    name=args.name,
                    description=args.desc,
                    category=args.category,
                    store=store,
                )
                print(f"✅ Domain Pod '{args.name}' provisioned successfully at: {pod_path}")
                print(f"To launch dedicated Domain Head:")
                print(f"  cd {pod_path} && ./spinup.sh")
                return 0
            except ValueError as e:
                print(f"❌ ERROR: {e}", file=sys.stderr)
                return 1

        elif args.domain_cmd == "status":
            pods = {p.domain_id: p for p in list_domain_pods(store)}
            if args.domain_id not in pods:
                print(f"❌ Domain pod '{args.domain_id}' not found.", file=sys.stderr)
                return 1
            pod = pods[args.domain_id]
            print(f"Domain ID:     {pod.domain_id}")
            print(f"Name:          {pod.name}")
            print(f"Category:      {pod.category}")
            print(f"Mission:       {pod.description}")
            print(f"Location:      {pod.path}")
            print(f"Active Lanes:  {', '.join(pod.active_lanes)}")
            return 0

        elif args.domain_cmd == "sync":
            from senate.scaffold.domain_builder import pull_domain_telemetry
            try:
                telemetry = pull_domain_telemetry(args.domain_id, store)
                print("══════════════════════════════════════════════════════════════")
                print(f"       PULLED TELEMETRY: {telemetry['name'].upper()}         ")
                print("══════════════════════════════════════════════════════════════")
                print(f"Domain ID:            {telemetry['domain_id']}")
                print(f"Mission:              {telemetry['mission']}")
                print(f"Category:             {telemetry['category'].upper()}")
                
                dm = telemetry.get("domain_metrics", {})
                rc = telemetry.get("resource_consumption", {})
                if "active_orders_count" in dm:
                    print(f"Active Open Orders:   {dm['active_orders_count']}")
                if "resting_collateral_usd" in rc:
                    print(f"Resting Collateral:   ${rc['resting_collateral_usd']:.2f}")
                if "oracle_balance" in dm:
                    ob = dm["oracle_balance"]
                    print(f"Verified Oracle Cash: ${ob.get('cash_usd', 0.0):.2f} | P&L: ${ob.get('lifetime_pnl_usd', 0.0):+.2f}")
                if "trials_count" in dm:
                    print(f"Domain Trials (N):    {dm['trials_count']}")
                print(f"State updated in Senate Hub.")
                print("══════════════════════════════════════════════════════════════")
                return 0
            except ValueError as e:
                print(f"❌ ERROR: {e}", file=sys.stderr)
                return 1

        elif args.domain_cmd == "delete":
            from senate.scaffold.domain_builder import delete_domain_pod
            delete_domain_pod(args.domain_id, store)
            print(f"✅ Domain pod '{args.domain_id}' deleted and unregistered from Senate Hub.")
            return 0

    elif args.command == "audit":

        from senate.models.adversary import MultiModelAdversary
        from senate.models.gateway import ModelGateway, ModelProvider

        proposal_text = args.proposal
        if Path(proposal_text).exists():
            proposal_text = Path(proposal_text).read_text(encoding="utf-8")

        prov = ModelProvider(args.provider) if args.provider in [p.value for p in ModelProvider] else ModelProvider.CLI
        adversary = MultiModelAdversary(ModelGateway(default_provider=prov))
        
        print("══════════════════════════════════════════════════════════════")
        print("           MULTI-MODEL ADVERSARIAL AUDIT                      ")
        print("══════════════════════════════════════════════════════════════")
        print(f"Auditor Provider: {prov.value} | Model: {args.model or 'default'}")
        print("Evaluating proposal against domain invariants...")
        
        result = adversary.audit_proposal(
            proposal_description=proposal_text,
            invariants_list=args.invariants,
            auditor_provider=prov,
            auditor_model=args.model,
        )

        status_tag = "✅ APPROVED" if result.is_approved else "❌ REJECTED"
        print(f"Audit Result:      {status_tag} (Risk Score: {result.risk_score}/10)")
        if result.violations:
            print("Violations Located:")
            for v in result.violations:
                print(f"  • {v}")
        print(f"Critique:          {result.critique}")
        print("══════════════════════════════════════════════════════════════")
        return 0 if result.is_approved else 1

    elif args.command == "sync-oracle":

        from senate.state.oracle import sync_oracle_fact
        file_p = Path(args.file) if args.file else None
        ok, msg, fact = sync_oracle_fact(store, file_p, max_age_hours=args.max_age)
        if ok:
            print(f"✅ Oracle synced: {msg}")
            return 0
        else:
            print(f"❌ Oracle sync failed (fails closed): {msg}", file=sys.stderr)
            return 1

    elif args.command == "trials":

        if args.trials_cmd == "log":
            import hashlib
            desc_hash = hashlib.sha256(args.description.strip().encode("utf-8")).hexdigest()[:16]
            trial = Trial(
                project=args.project,
                config_hash=f"sha256_{desc_hash}",
                description=args.description.strip(),
                count=args.count,
            )
            tid = store.log_trial(trial)
            per, tot = store.get_trial_counts(args.project)
            print(f"✅ Logged trial #{tid} for project '{args.project}'. Total project N={per.get(args.project, 0)}, Global N={tot}.")
            return 0
        elif args.trials_cmd == "summary":
            per, tot = store.get_trial_counts()
            hurdle = price_n_hurdle(tot if tot > 0 else 1)
            print("══════════════════════════════════════════════════════════════")
            print("                 SENATE STATISTICAL LEDGER                    ")
            print("══════════════════════════════════════════════════════════════")
            print(f"Global Trial Count N = {tot}")
            print(f"Expected Max Noise Sharpe @ N={tot or 1}: {hurdle['expected_noise_sharpe']:.2f}")
            print(f"Required Bonferroni Hurdle |t| >= {hurdle['required_t_stat']:.2f}")
            print("──────────────────────────────────────────────────────────────")
            for proj, cnt in per.items():
                print(f"  • {proj.ljust(25)} N = {cnt}")
            print("══════════════════════════════════════════════════════════════")
            return 0

    elif args.command == "verify-payoff":
        from senate.verify.payoff import evaluate_order_payoff_from_venue_record

        if args.source_file:
            source_p = Path(args.source_file)
            if not source_p.exists():
                print(f"❌ Source artifact not found: {args.source_file}", file=sys.stderr)
                return 1
            try:
                payload = json.loads(source_p.read_text(encoding="utf-8"))
                order_rec = payload.get("order", {})
                book_rec = payload.get("book", {})
                cand_recs = payload.get("candidates", [])
                decision = evaluate_order_payoff_from_venue_record(
                    order_record=order_rec,
                    market_book=book_rec,
                    candidate_books=cand_recs,
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
        print("             DETERMINISTIC ECONOMIC PAYOFF VERIFICATION       ")
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


    elif args.command == "verify-hurdle":
        res = price_n_hurdle(args.n, args.alpha, args.obs)
        print(json.dumps(res, indent=2))
        return 0

    elif args.command == "ideate":
        from senate.models.ideation_engine import StandingIdeator
        ideator = StandingIdeator(store.db)

        if args.ideate_cmd == "propose":
            try:
                kill_spec = json.loads(args.kill_test)
            except Exception:
                kill_spec = {"raw": args.kill_test}

            rec = ideator.submit_and_audit_idea(
                domain=args.domain,
                hypothesis=args.hypothesis,
                kill_test_spec=kill_spec,
                proposing_model=args.model,
            )
            icon = "✅ SURVIVED" if rec.adversary_status == "SURVIVED" else "❌ KILLED (GRAVEYARD)"
            print("══════════════════════════════════════════════════════════════")
            print(f"      STANDING IDEATION ORGAN — ADVERSARIAL VERDICT           ")
            print("══════════════════════════════════════════════════════════════")
            print(f"Idea ID:          {rec.idea_id}")
            print(f"Domain:           {rec.domain.upper()}")
            print(f"Hypothesis:       {rec.hypothesis}")
            print(f"Proposing Model:  {rec.proposed_by_model}")
            print(f"Auditor:          {rec.audited_by_adversary}")
            print(f"Verdict:          {icon}")
            print(f"Status:           {rec.status}")
            print("══════════════════════════════════════════════════════════════")
            return 0

        elif args.ideate_cmd == "list":
            ideas = ideator.list_ideas(domain=args.domain, status=args.status)
            print("══════════════════════════════════════════════════════════════")
            print("                SENATE IDEATION & GRAVEYARD REGISTRY          ")
            print("══════════════════════════════════════════════════════════════")
            if not ideas:
                print("  (No ideas recorded matching criteria)")
            else:
                for i in ideas:
                    status_icon = "✅" if i["status"] == "VALIDATED" else "🪦"
                    print(f"  • {status_icon} [{i['status']}] {i['hypothesis']} ({i['idea_id']})")
                    print(f"    Domain: {i['domain']} | Proposed by: {i['proposed_by_model']} | Auditor: {i['audited_by_adversary']}")
            print("══════════════════════════════════════════════════════════════")
            return 0

    elif args.command == "mistakes":
        from senate.state.mistake_enforcer import HISTORICAL_MISTAKES, seed_mistakes_into_db
        if args.mistakes_cmd == "seed":
            with store.db.get_connection() as conn:
                count = seed_mistakes_into_db(conn)
            print(f"✅ Seeded {count} historical mistake invariants into SQLite.")
            return 0

        elif args.mistakes_cmd == "list":
            print("══════════════════════════════════════════════════════════════")
            print("             SENATE COMPILED MISTAKE INVARIANTS               ")
            print("══════════════════════════════════════════════════════════════")
            for m in HISTORICAL_MISTAKES:
                print(f"  • 🔒 [{m.status}] {m.name} ({m.mistake_id})")
                print(f"    Incident: {m.incident_description}")
                print(f"    Enforcer: {m.enforced_by_module} -> {m.test_function}()")
            print("══════════════════════════════════════════════════════════════")
            return 0

    elif args.command == "daemon":
        from senate.harness.daemon import SenateCadenceDaemon
        daemon = SenateCadenceDaemon(interval_seconds=args.interval, max_cycles=args.cycles)
        daemon.start()
        return 0

    return 0





if __name__ == "__main__":
    sys.exit(main())
