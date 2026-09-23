"""Seed facts and sovereign truths for The Senate State Engine (Tier 1 Meta-Hub).

INVARIANT: The Senate Meta-Hub only stores executive sovereign laws and global standards.
Domain-specific platform facts live strictly inside their own domain pod database.
"""

from typing import List
from senate.state.fact_store import FactStore
from senate.state.models import Fact, ProjectState, Goal
from senate.state.mistake_enforcer import seed_mistakes_into_db
from senate.state.ratify_mistakes_20260909 import ratify_mistakes


INITIAL_FACTS: List[Fact] = [
    # Senate Sovereign Constitution & Operating Laws
    Fact(
        key="senate.constitution.statements",
        domain="senate",
        value={
            "statement_1_goal": "The senate directs intelligence at Ryan's goal. Output is goal progress and Ryan-hours saved — never artifacts.",
            "statement_2_hypotheses": "Members derive every decision from the goal; precedent and suggestion, Ryan's included, are hypotheses.",
            "statement_3_reality": "No claim about the world is true until the world has said it.",
            "statement_4_verification": "Work proceeds by the smallest step whose outcome reality can verify.",
            "statement_5_premises": "A conclusion is what is needed to meet goals. Reasoning can be reviewed, premises can be proved, and data is needed to prove premises.",
            "statement_6_context": "Context is a budget: hold the canon, page everything else.",
            "statement_7_corpus": "The corpus shrinks and sharpens; lessons refine or gate, never append. Everything is stored — and ignored until pointed at or fetched.",
            "statement_8_questions": "A question begets an answer and nothing else — no implications, no assumptions, no action. A question is never an invitation to act.",
            "statement_9_brevity": "Responses are brief: unread output is wasted. Go to the heart of what matters, ignore everything else, clarify only when asked.",
            "statement_10_ratification": "Only Ryan ratifies canon. Claudes propose; [PROPOSED] steers nothing.",
            "statement_11_tool_first": "Zero Unverified Claims: Any assertion regarding capital, venue truth, or file existence without an immediate preceding tool execution is strictly void.",
            "statement_12_adversary": "Adversarial Falsification: No model validates its own proposals. Deployment requires independent multi-model adversarial audit.",
            "statement_13_history_first": "History Answers Strategy Questions: Live money is only ever permitted to measure unrecorded execution parameters (fills, slippage, queue churn). Any strategy verdict that ignored available historical tape is strictly invalid and forbidden from live funding.",
            "statement_14_regime_clustering": "Statistical Power Requires Regime Clustering: All t-statistics and win-rates must be clustered at the regime level (e.g. daily/weather cluster), never at the intra-day trigger level. Single-regime sample mining is treated as N=1 and rejected.",
        },
        source_artifact="SENATE STATEMENTS.md",
        verified_by="ryan_sovereign_ratification",
        is_immutable=True,
    ),


    # Statistical / Multiple-Testing Standards (Global Sovereign Law)
    Fact(
        key="statistics.multiple_testing.standards",
        domain="statistics",
        value={
            "euler_mascheroni": 0.5772156649015329,
            "fwer_alpha": 0.05,
            "reference": "Bailey & Lopez de Prado (AMS 2014)",
            "rule": "Unreported N = infinity = auto-reject. Minimum t-hurdle priced via Bonferroni.",
        },
        source_artifact="statistics_specification",
        verified_by="math_proof",
        is_immutable=True,
    ),
    # Sovereign Risk Mandate
    Fact(
        key="sovereign.risk.caps",
        domain="sovereign",
        value={
            "max_single_deployment_usd": 50.00,
            "max_total_portfolio_risk_usd": 300.00,
            "max_daily_loss_usd": 100.00,
            "description": "Ryan's sovereign risk mandate: max $50 single deployment, max $300 portfolio risk.",
        },
        # 2026-09-09: this row previously carried verified_by="ryan_sovereign_mandate"
        # -- self-awarded by a prior session, with no verbatim quote and no date, for a
        # $50 figure that Ryan's own repeated ruling ("never more than $25 in any
        # market") contradicts.  The binding number is compiled in senate/verify/caps.py
        # and this fact can now only TIGHTEN it.  See mistakes ledger:
        # immutable_fact_outranked_a_ryan_ruling / self_awarded_ryan_authority.
        source_artifact="sovereign_mandate:ryan_risk_limits",
        verified_by="unattributed_prior_session:20260817",
        is_immutable=True,
    ),
]

INITIAL_PROJECTS: List[ProjectState] = [
    ProjectState(
        project_id="kalshi",
        name="Kalshi Prediction Markets",
        status="ACTIVE",
        variables={
            "category": "capital_generation",
            "mission": "Autonomous prediction market trading and market making engine.",
            "path": "domains/kalshi",
            "lanes": [
                "autoseat_lip",
                "crypto_scalp",
                "mlb_xvenue",
                "weather_ensemble",
                "dutchbook_arb",
                "deribit_implied",
                "earnings_nlp",
            ],
        },
    )
]

INITIAL_GOALS: List[Goal] = [
    Goal(
        goal_id="goal_capital_autonomy",
        title="Autonomous Capital Generation",
        category="CAPITAL_GENERATION",
        target_metric="Daily Net P&L",
        target_value=100.0,
        current_value=0.0,
        unit="USD/day",
        ryan_hours_saved=42.0,
        status="ACTIVE",
        associated_domains=["kalshi"],
    ),
    Goal(
        goal_id="goal_physical_engineering",
        title="Automotive Chassis & Physical Simulation",
        category="PHYSICAL_ENGINEERING",
        target_metric="FEA Stress & Aero Solves",
        target_value=10.0,
        current_value=1.0,
        unit="Simulations",
        ryan_hours_saved=15.0,
        status="ACTIVE",
        associated_domains=["automotive"],
    ),
    Goal(
        goal_id="goal_sovereign_framework",
        title="Senate Multi-Agent Sovereign Operating System",
        category="SOFTWARE_MASTERY",
        target_metric="Zero-Context-Rot Subagent Autonomy",
        target_value=100.0,
        current_value=95.0,
        unit="Percent",
        ryan_hours_saved=60.0,
        status="ACTIVE",
        associated_domains=["senate"],
    ),
]


def seed_database(store: FactStore) -> None:
    """Populate FactStore with verified foundational facts idempotently.

    2026-09-09: the mistakes ledger is re-ratified on EVERY boot (ported from the
    Kalshi pod, whose seed calls ratify_mistakes unconditionally).  A lesson that
    is written once and never re-asserted rots out of the prompt the first time
    the DB is rebuilt -- which is exactly how this head came to recite 14 laws it
    had never read.
    """
    for fact in INITIAL_FACTS:
        store.set_fact(fact, allow_sovereign_override=True)
    for proj in INITIAL_PROJECTS:
        if not store.get_project_state(proj.project_id):
            store.save_project_state(proj)
    for goal in INITIAL_GOALS:
        if not store.get_goal(goal.goal_id):
            store.save_goal(goal)
    with store.db.get_connection() as conn:
        seed_mistakes_into_db(conn)      # legacy mistake_invariants table
        ratify_mistakes(conn)            # the dated, receipted mistakes ledger
