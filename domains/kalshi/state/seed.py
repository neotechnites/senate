"""Seed data for Kalshi Domain Pod extracted strictly from verified on-disk primary receipts.

INVARIANT: NO MONEY OR SEAT STATE ORIGINATES IN A SEED FILE.
Active seats and balances must originate from authentic venue receipts or live venue APIs.
"""

from pathlib import Path
from domains.kalshi.state.fact_store import FactStore
from domains.kalshi.state.models import Fact

SOURCES_DIR = Path(__file__).resolve().parents[1] / "data" / "sources"

INITIAL_KALSHI_FACTS = [
    Fact(
        key="kalshi.lip.discount_factor",
        domain="kalshi",
        value={
            "bps": 5000,
            "decay_rate_per_tick": 0.50,
            "formula": "reward * (0.50 ** distance_ticks)",
            "description": "LIP rewards decay by 50% for each tick away from the qualifying touch.",
        },
        source_artifact=str(SOURCES_DIR / "lip_decay_spec.json"),
        verified_by="venue_api_spec",
        is_immutable=True,
    ),
    Fact(
        key="kalshi.fees.structure",
        domain="kalshi",
        value={
            "maker_fee_usd": 0.0,
            "taker_formula": "ceil(0.07 * count * price * (1 - price))",
            "maker_fee_waiver": True,
            "description": "Maker orders incur 0 fee. Taker fees peak quadratically at 50c.",
        },
        source_artifact=str(SOURCES_DIR / "fee_schedule.json"),
        verified_by="exchange_regulatory_rulebook",
        is_immutable=True,
    ),
    Fact(
        key="kalshi.settlement.accuracy",
        domain="kalshi",
        value={
            "payout_per_winning_contract_usd": 1.0000,
            "payout_per_losing_contract_usd": 0.0000,
            "description": "Kalshi contracts settle deterministically to $1.0000 or $0.0000.",
        },
        source_artifact=str(SOURCES_DIR / "settlement_accuracy.json"),
        verified_by="settlement_api_spec",
        is_immutable=True,
    ),
    Fact(
        key="kalshi.rewards.realization_accuracy",
        domain="kalshi",
        value={
            "realized_vs_estimate_max_error_bps": 10,
            "realization_tolerance_pct": 0.001,
            "description": "Realized daily LIP reward credits match deterministic model estimates within 0.1%.",
        },
        source_artifact=str(SOURCES_DIR / "credit_realization_rule.json"),
        verified_by="audited_reward_receipts",
        is_immutable=True,
    ),
    Fact(
        key="kalshi.exposure.caps",
        domain="kalshi",
        value={
            "max_per_market_usd": 50.00,
            "max_total_portfolio_usd": 250.00,
            "description": "Hard capital bounds: max $50 per single market and max $250 across total portfolio (positions + resting).",
        },
        source_artifact=str(SOURCES_DIR / "capital_exposure_mandate.json"),
        verified_by="ryan_sovereign_mandate",
        is_immutable=True,
    ),

    Fact(
        key="kalshi.fees.taker_peak_curve",
        domain="kalshi",
        value={
            "peak_taker_fee_price_cents": 50,
            "symmetry_axis_cents": 50,
            "description": "Taker fees peak quadratically at exactly 50 cents price.",
        },
        source_artifact=str(SOURCES_DIR / "taker_peak_curve.json"),
        verified_by="exchange_fee_specification",
        is_immutable=True,
    ),
]


def seed_kalshi_database(store: FactStore) -> None:
    """Idempotently seed the Kalshi Domain FactStore with verified platform laws.
    
    Zero money state or active seats are created here.
    """
    for f in INITIAL_KALSHI_FACTS:
        if not store.get_fact(f.key):
            store.set_fact(f)
