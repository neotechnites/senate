"""Seed data for Kalshi Domain Pod extracted strictly from verified on-disk primary receipts.

INVARIANT: NO MONEY OR SEAT STATE ORIGINATES IN A SEED FILE.
Active seats and balances must originate from authentic venue receipts or live venue APIs.
"""

from pathlib import Path
from domains.kalshi.state.fact_store import FactStore
from domains.kalshi.state.models import Fact
from domains.kalshi.verify.caps import (LEGACY_CAPS_FACT_KEY, LIMITS_FACT_KEY,
                                        legacy_caps_alias_value, ryan_limits_value)
# FG-11 (2026-09-05): the rotation / horizon / payability doctrine is seeded
# as the RATIFIED facts, not as derived copies under other keys.
from domains.kalshi.state.ratify_facts_20260831 import FACTS as _RATIFIED_FACTS
# 2026-09-09: later ratifications overlay earlier ones, newest measurement
# wins (kalshi.model.realization re-measured at 0.43 on 228 seat-programs).
from domains.kalshi.state.ratify_facts_20260909 import FACTS as _RATIFIED_FACTS_0909
from domains.kalshi.state.ratify_mistakes_20260909 import ratify_mistakes
_RATIFIED_BY_KEY = {f.key: f for f in _RATIFIED_FACTS}
_RATIFIED_BY_KEY.update({f.key: f for f in _RATIFIED_FACTS_0909})

SOURCES_DIR = Path(__file__).resolve().parents[1] / "data" / "sources"

# FG-06 (2026-09-05): A SOURCE_ARTIFACT THAT DOES NOT EXIST IS NOT PROVENANCE.
#
# Six policy facts below (the five 2026-08-31 strategy facts and
# kalshi.armor.policy) cited data/sources/<name>_spec.json files that were
# never written -- `ls data/sources` has ten receipts and none of them.  The
# phantom path let each fact wear the same on-disk-receipt shape as the
# venue-mechanics facts above it, and one of them (kalshi.armor.policy) was
# additionally self-stamped immutable under a "sovereign" label, so the bar the
# engine actually enforces (duty_cycle.resolve_armor_policy, qualify.py) was
# uncorrectable through the API while its cited receipt was a file nobody could
# open.  This is mistake-ledger #2 (fabricated provenance) recurring.  Rules:
#   * a seed fact cites a file only if the file is on disk
#     (tests/test_facts_governance.py::test_seed_source_artifacts_exist);
#   * where no primary receipt exists, the artifact string says so and names
#     the thing the numbers were actually derived from -- the 2026-08-31
#     ratification session facts (state/ratify_facts_20260831.py) and, for
#     the armor bar, harness/duty_cycle.ARMOR_POLICY_DEFAULTS.  No receipt
#     file is invented to satisfy the check;
#   * only the five venue-mechanics facts may be immutable
#     (::test_only_venue_mechanics_immutable).
RATIFY_SESSION = "ryan-conversation-2026-08-31 ratification session (state/ratify_facts_20260831.py)"


def _derived_from(*ratified_keys: str) -> str:
    """Provenance string for a policy fact with no primary receipt on disk."""
    return (f"derived from ratified fact(s) {', '.join(ratified_keys)} -- {RATIFY_SESSION}; "
            "no primary receipt on disk (FG-06 2026-09-05)")

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
    # FG-01 (2026-09-05): THE LIMITS RYAN GAVE, IN HIS WORDS, MUTABLE.
    #
    # This slot used to seed `kalshi.exposure.caps` at $50/market and $250
    # total, `is_immutable=True`, `verified_by="ryan_sovereign_mandate"` — a
    # label an agent awarded itself, citing an agent-authored JSON with no
    # quote and no date.  Ryan said neither number.  Because it was
    # immutable, FactStore.set_fact refused every later correction (the live
    # VPS copy had to be moved to $25 by raw SQL), so the seed, the tests and
    # the VPS all disagreed, and harness/auto_seeder.py cited the fact as
    # the authority for the $50 KXKR-26SEPIDSALES-1.5 seat that was swept
    # the same day.  Rules, paid for:
    #   * a fact that carries Ryan's authority carries his quote and its
    #     date, and is stamped "ryan" — never a self-awarded "sovereign"
    #     label (the same rule the five 2026-08-31 policy facts below
    #     were re-stamped under);
    #   * policy facts stay MUTABLE so a ruling can be corrected through
    #     the API and journaled in fact_history — the code layer
    #     (verify/caps.py) is what stops a stored value from loosening;
    #   * one authority.  kalshi.exposure.caps is a READ-ALIAS built from
    #     the same numbers for readers not yet moved to get_limits().
    Fact(
        key=LIMITS_FACT_KEY,
        domain="kalshi",
        value=ryan_limits_value(),
        source_artifact=str(SOURCES_DIR / "capital_exposure_mandate.json"),
        verified_by="ryan",
        is_immutable=False,
    ),
    Fact(
        key=LEGACY_CAPS_FACT_KEY,
        domain="kalshi",
        value=legacy_caps_alias_value(),
        source_artifact=str(SOURCES_DIR / "capital_exposure_mandate.json"),
        verified_by="alias-of-kalshi.limits (FG-01 seed 2026-09-05)",
        is_immutable=False,
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
    Fact(
        key="kalshi.fill_zone.hazard",
        domain="kalshi",
        value={
            "hazard_threshold_cents": 35,
            "fill_rate_le_35": 0.0036,
            "fill_rate_gt_35": 0.0,
            "sample_size_gt_35": 833,
            "description": "Prices <= 35c carry 0.36% fill rate; prices > 35c carry 0.0% fill rate across 833 placements.",
        },
        source_artifact=_derived_from("kalshi.fill_zone.price"),
        # PROVENANCE CORRECTED 2026-09-01 (kalshi-6b re-review): these five
        # strategy-policy facts were seeded 2026-08-31 by an unattributed
        # session with is_immutable=True and self-asserted authority labels —
        # the exact anti-pattern the kalshi.exposure.caps correction banned.
        # Policy facts stay MUTABLE so rulings can evolve (e.g. the $1.03
        # rotation buffer); only venue-mechanics facts may be immutable.
        verified_by="unattributed-session-20260831 (re-reviewed kalshi-6b 2026-09-01)",
        is_immutable=False,
    ),
    # FG-11 (2026-09-05): THE DUPLICATE KEYS ARE GONE.  Two derived COPIES of
    # the ratified doctrine used to sit here -- kalshi.measurement_clock.curfew
    # (a copy of kalshi.hold_horizon) and kalshi.rotation.thresholds (a copy
    # of kalshi.lip.payability + kalshi.model.realization) -- and only
    # verify/qualify.py read them, while every process that actually holds,
    # rotates, seeds or screens a seat hardcoded the same numbers.  Two keys
    # for one horizon meant a ruling could land in one and be read from the
    # other.  The seed now carries the RATIFIED facts themselves (imported
    # from the ratification script so they cannot drift from it) and every
    # consumer reads them through harness/policy_facts.resolve_rotation_policy.
    # A live DB that still holds the old copies is left alone (the seed never
    # deletes); the resolver consults them only when the ratified key is
    # absent.
    _RATIFIED_BY_KEY["kalshi.hold_horizon"],
    _RATIFIED_BY_KEY["kalshi.lip.payability"],
    _RATIFIED_BY_KEY["kalshi.model.realization"],
    Fact(
        key="kalshi.feed_taxonomy.rules",
        domain="kalshi",
        value={
            "max_seats_per_underlying_feed": 1,
            "description": "Max 1 seat per underlying data stream to prevent correlated basket hits across multiple markets.",
        },
        source_artifact=_derived_from("kalshi.feeds.one_feed_one_line", "kalshi.feeds.taxonomy"),
        # was self-stamped "sovereign_mandate" — no receipt exists for that label
        verified_by="unattributed-session-20260831 (re-reviewed kalshi-6b 2026-09-01)",
        is_immutable=False,
    ),
    # FG-07 (2026-09-05): this row said fill_halt_scope="FAMILY_ONLY" and
    # "global freeze scoped" while the engine halts by FEED
    # (placement_engine.feed_scope: NFLXAPP filled 09:58Z 2026-09-04, LYFTAPP
    # -- same "App" feed -- 12:12Z the same day) and freezes in FULL (Ryan
    # 2026-09-04: "placement being disarmed has absolutely not stopped
    # placements").  Nothing read the fact; it only told future agents to
    # rebuild the family-scoped halt and the seeder bypass that paid for those
    # fills.  Rewritten to the enforced rule; the old values are kept under
    # "superseded"; placement_engine.freeze_fact_divergence now reads it.
    Fact(
        key="kalshi.ban_policy.rules",
        domain="kalshi",
        value={
            "mode": "RECEIPTS_ONLY",
            "fill_halt_scope": "FEED",
            "freeze_scope": "FULL",
            "seeder_may_place_through_freeze": False,
            "description": (
                "A fill halts by FEED (every family on the filled seat's feed per "
                "kalshi.feeds.taxonomy: cancel resting, retire plan rows, durable "
                "receipts-only ban) and FREEZES ALL new deployments (DISARMED = no "
                "new market by any path, seeder included) until a human re-arms."
            ),
            "authorized": (
                "Ryan 2026-09-04: 'placement being disarmed has absolutely not "
                "stopped placements'"
            ),
            "superseded": {
                "as_of": "2026-09-04",
                "old_fill_halt_scope": "FAMILY_ONLY",
                "old_description": (
                    "Fills trigger family-specific halt; global freeze scoped to "
                    "avoid draining portfolio across Sunday rollover."
                ),
                "why": (
                    "family-only halt let LYFTAPP fill 2h after NFLXAPP on the same "
                    "feed; the scoped freeze let 18 seats seed while DISARMED, three "
                    "of which filled (2026-09-03/04)"
                ),
            },
        },
        source_artifact=_derived_from("kalshi.bans.policy", "kalshi.fill_response.scoped_freeze"),
        # was self-stamped "ryan_sovereign_mandate" — only a fact Ryan states in
        # conversation, quoted verbatim with its date, may carry that label;
        # it now carries his 2026-09-04 quote (FG-07) and stays MUTABLE.
        verified_by="ryan",
        is_immutable=False,
    ),
    # FG-05 (2026-09-05): this row was seeded `verified_by="ryan_sovereign_mandate"`,
    # `is_immutable=True` -- the same self-awarded label and lock that made the
    # $50 caps fact uncorrectable.  FactStore.set_fact now refuses that shape
    # outright (only venue-mechanics provenance may lock; a ryan-stamped fact
    # must carry his quote and its date).  The gate itself IS Ryan's ruling --
    # kalshi.armor.role_ruling, 2026-08-31: 'the wall does stop the print' --
    # so it keeps his name, with that quote, and stays MUTABLE like every
    # policy fact (the numbers are operating constants from
    # harness/duty_cycle.ARMOR_POLICY_DEFAULTS, correctable through the API and
    # journaled in fact_history; nothing here loosens the gate).
    Fact(
        key="kalshi.armor.policy",
        domain="kalshi",
        value={
            "abs_min_ct": 200.0,
            "burst_mult": 5.0,
            "status": "HARD_GATE",
            "description": "Hard gate: min 200ct wall thickness required for all resting seats.",
            "authorized": ("Ryan 2026-08-31: 'the wall does stop the print' -- armor stays "
                           "a full gate (kalshi.armor.role_ruling); numbers are the pod's "
                           "operating constants, not a quoted figure"),
        },
        # FG-06: the cited armor_policy_spec.json never existed; the ruling is
        # kalshi.armor.role_ruling and the numbers are duty_cycle.ARMOR_POLICY_DEFAULTS.
        source_artifact=(f"{RATIFY_SESSION} kalshi.armor.role_ruling; numbers: "
                         "harness/duty_cycle.ARMOR_POLICY_DEFAULTS (FG-06 2026-09-05)"),
        verified_by="ryan",
        is_immutable=False,
    ),
    # FLAT-9 (2026-09-05): WHAT THE POD DOES WITH A POSITION A SWEEP LEFT IT.
    #
    # 25 lifetime fills, every one an informed sweep, and NOT ONE position was
    # ever flattened: the fill-halt DISARMed, cancelled the feed and returned
    # -- the position itself was abandoned at that instant (KXSNOWCRABCATCH
    # from 09-03 is still open; a $50 KXKR seat was swept today).  FLAT-7 gave
    # the pod ONE flatten path (PlacementEngine.flatten_position: post-only,
    # reduce-only, sized from the venue's live position).  This fact decides
    # whether the fill-halt calls it automatically.
    #
    # DEFAULT OFF.  A sweep is information ("$137 lesson: a fill is
    # information -- stand down first"); an automatic close placed into the
    # same re-rating book is a second decision Ryan has not ratified.  A
    # missing fact reads as OFF (placement_engine.FLATTEN_POLICY_DEFAULTS).
    # Policy facts stay MUTABLE (FG-01 doctrine above): flip
    # auto_on_fill_halt through the API, journaled in fact_history.
    #   mode           'post_only_touch' -> join the best ask of the held side
    #                  (flatten_position take=False); 'post_only_inside' ->
    #                  one tick above the best bid (take=True, STILL post-only)
    #   allow_taker    False.  No taker path exists in the engine; a True here
    #                  is logged and ignored, never honoured.
    #   requote_max_per_day  ceiling for a future requote loop on a resting
    #                  close; nothing consumes it yet (a resting close is
    #                  spared by the fill-halt, FLAT-7, and never chased).
    Fact(
        key="kalshi.flatten.policy",
        domain="kalshi",
        value={
            "auto_on_fill_halt": False,
            "mode": "post_only_touch",
            "allow_taker": False,
            "requote_max_per_day": 6,
            "description": ("Fill-halt auto-flatten hook (FLAT-9). OFF until Ryan ratifies "
                            "an automatic close; the manual path is "
                            "`kalshi.py position flatten --ticker T --live`."),
            "authorized": ("Ryan 2026-09-05: 'never to have more than 25$ in any market' "
                           "-- an open position is exposure the limit counts; the hook's "
                           "default is the pod's own conservative choice, not a quoted ruling"),
        },
        source_artifact="FLAT-9 2026-09-05 (placement_engine fill-halt auto-flatten hook)",
        verified_by="pod",
        is_immutable=False,
    ),
    # FLAT-10 (2026-09-05): THE CLOSE PATH IS A HYPOTHESIS UNTIL THE VENUE
    # CONFIRMS IT.  fetch_positions returned market_positions raw for the life
    # of the pod and no code ever parsed a field from it, so the signed count
    # key (position_fp vs position), its units, and whether an `ask` while
    # long YES is NETTED as a close (zero new collateral) or OPENED as a NO
    # position were asserted by comments only.  The pod already paid for
    # trusting docs once: the V2 cancel path returned 404 live and broke the
    # defensive path.  This fact is the ledger of the two-step probe:
    #   step 1 (read-only)  `kalshi.py position list` pins count_key /
    #                       exposure_key from a live row (schema_pinned_at);
    #   step 2 (Ryan-gated) `kalshi.py position flatten --ticker T --count 1
    #                       --live` places the ONE-contract probe; its fill
    #                       re-reads the position and stamps
    #                       close_semantics_verified True only when the
    #                       position SHRANK on the held side (never flipped).
    # Until close_semantics_verified is True the engine caps every live
    # flatten at the 1ct probe and the FLAT-9 auto hook places nothing.
    # MUTABLE (FG-01): the engine writes it; seed only creates it when absent.
    Fact(
        key="kalshi.ops.positions_schema",
        domain="kalshi",
        value={
            "count_key": None,
            "exposure_key": None,
            "schema_pinned_at": None,
            "close_semantics_verified": False,
            "verdict": "unverified",
            "probe": None,
            "description": ("FLAT-10 positions-schema / close-semantics probe ledger. "
                            "Live flatten capped at 1 contract until verified."),
            "authorized": ("pod doctrine (venue_client.cancel_order receipt): a docs-derived "
                           "endpoint or field is a hypothesis until one live read confirms it"),
        },
        source_artifact="FLAT-10 2026-09-05 (positions schema + close semantics probe)",
        verified_by="pod",
        is_immutable=False,
    ),
]


# FG-10 (2026-09-05): THE SEED WRITES NO DEPLOYMENT-PLAN ROWS.  NONE.
#
# Until today this file carried PILOT_DEPLOYMENT_PLAN -- the two 2026-08-17
# pilot seats (KXGENERICBALLOTVOTEHUB-26AUG21-T6.8 at $49.94 and
# KXVOTEPRIMARY-GOVFLNOMR26JFISJFIS-14 at $50.00) -- and upserted them as
# 'pending' intent on EVERY seed_kalshi_database call: spinup.py boots,
# `./kalshi.py seed`, every test DB.  That is the paid-for lesson three ways:
#
#   1. They were $50 rows.  Ryan's limit, verbatim: "never to have more than
#      25$ in any market".  The engine's plan_cap was min(50, row), so a $50
#      row flowed through a check that allowed $50 -- the exact shape of the
#      $50 KXKR seat seeded 07:24Z and swept 14:30Z today.  Only the
#      KXVOTEPRIMARY family fill-ban and the 26AUG21 expiry kept these two
#      off the venue; any new host or test that ARMed with them present sized
#      at $50.  Resizing them to $25 (the first patch today) fixed the number
#      and left the mechanism: a seed that manufactures intent.
#   2. They were DEAD.  The pilot expired 2026-08-21 and the FL seat's hard
#      exit was 2026-08-18T12:00Z; 19 days later every boot still re-stamped
#      them 'pending', and the re-seed-over-terminal branch (2026-09-04)
#      would have revived them from 'exited' on the next boot.
#   3. Intent is not seed data.  This file's own invariant says NO MONEY OR
#      SEAT STATE ORIGINATES IN A SEED FILE.  A pending plan row IS seat
#      state -- the placement engine turns it into an order the moment a
#      human ARMs.  Live intent enters through the seeder (harness/
#      auto_seeder.py) or an explicit `./kalshi.py plan` action, each bounded
#      by FactStore.refuse_plan_row_above_cap at write time.
#
# The placement-engine tests that used the pilot rows as fixtures now create
# their own (tests/test_placement_engine.py PILOT_TEST_PLAN, both <= $25).
# Nothing here may grow a deployment_plan row again; test_oracle_and_seats
# asserts the plan is empty after seeding.


def seed_kalshi_database(store: FactStore) -> None:
    """Idempotently seed the Kalshi Domain FactStore with verified platform laws.

    Zero money state, active seats, or deployment-plan intent is created here
    (FG-10, 2026-09-05).  Facts only.
    """
    for f in INITIAL_KALSHI_FACTS:
        if not store.get_fact(f.key):
            store.set_fact(f)
    # FG-10: no deployment_plan rows are seeded -- see the receipt above.
    # MT-4 (2026-09-09): the mistakes ledger is ratified on every boot,
    # idempotently (`mistakes` INSERT OR IGNORE on name -- the live VPS shape;
    # `mistake_invariants` on mistake_id).  Zero money state.
    # MT-5: the ledger must never block a boot (the VPS daemon seeds on start).
    try:
        ratify_mistakes(store)
    except Exception as exc:  # noqa: BLE001 -- reported, never fatal
        print(f"⚠️  mistakes ledger ratification skipped: {exc}")
