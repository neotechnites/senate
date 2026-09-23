"""Unit and property tests for Fundamental Base Rates, 24h Curfew, and Total Budget Gates."""

import sys
import tempfile
import unittest
from pathlib import Path

POD_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
for p in [str(REPO_ROOT), str(POD_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from domains.kalshi.harness.gate import ActionType, ExecutionGate
from domains.kalshi.harness.census_scanner import CensusScanner
# the hermetic census harness (temp DB + stubbed venue) lives with the gate tests
from domains.kalshi.tests.test_census_gates import (DEEP_BOOK,
                                                    CensusGateTestBase,
                                                    _hours_from_now)
from domains.kalshi.state.db import Database
from domains.kalshi.state.fact_store import FactStore
from domains.kalshi.state.models import ActiveOrder, Fact
from domains.kalshi.state.seed import seed_kalshi_database
from domains.kalshi.verify.base_rates import evaluate_fundamental_base_rate
from domains.kalshi.verify.invariants import InvariantEngine


class TestBaseRatesCurfewAndBudget(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_safety.db"
        self.db = Database(self.db_path)
        self.store = FactStore(self.db)
        seed_kalshi_database(self.store)
        self.gate = ExecutionGate(self.store)
        self.engine = InvariantEngine(self.store)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_fundamental_base_rate_rejects_toxic_no_on_ballots(self):
        """CRITICAL: Proves selling cheap NO on high-probability state ballot bond/fund measures is REJECTED."""
        # Proposal: Sell NO @ 22c on 911 emergency fund amendment
        is_safe, violation, rule = evaluate_fundamental_base_rate(
            ticker="KXSTATEBALLOTMEASURE-GA-A2",
            side="no",
            price=0.22,
            market_title="Will Amendment 2 pass?",
            market_subtitle="9-1-1 Fund Amendment",
        )
        self.assertFalse(is_safe)
        self.assertIn("Fundamental Base-Rate Breach", violation)
        self.assertIn("76%", violation)

        # Gate execution must FAIL CLOSED
        proposal = {
            "ticker": "KXSTATEBALLOTMEASURE-GA-A2",
            "side": "no",
            "price": 0.22,
            "count": 100,
            "notional_usd": 22.00,
            "title": "Will Amendment 2 pass?",
            "subtitle": "9-1-1 Fund Amendment",
        }
        res = self.gate.execute_action(ActionType.DEPLOY_SEAT, proposal)
        self.assertFalse(res.is_executed)
        self.assertTrue(any("Fundamental Base-Rate Breach" in v for v in res.violations))

    def test_terminal_window_curfew_rejects_sub_24h_entry(self):
        """CRITICAL: Proves order entry inside 24h of window expiry is strictly REJECTED (anti-evacuation)."""
        proposal = {
            "ticker": "KXFEDFUNDSYEAR-26-HOLD",
            "side": "yes",
            "price": 0.20,
            "count": 100,
            "notional_usd": 20.00,
            "hours_to_window_expiry": 12.5,  # < 24h
        }
        valid, violations, _ = self.engine.validate_order_proposal(proposal)
        self.assertFalse(valid)
        self.assertTrue(any("Terminal window curfew breached" in v for v in violations))

        # At >= 24h margin -> Pass
        proposal["hours_to_window_expiry"] = 36.0
        valid2, violations2, _ = self.engine.validate_order_proposal(proposal)
        self.assertTrue(valid2)

    def test_total_portfolio_budget_cap_includes_positions_and_resting(self):
        """CRITICAL: Proves fills into positions DO NOT create headroom; total capital <= $530 is enforced.

        FG-01 (2026-09-05): was written against a $250 total the seed carried
        without Ryan's authority; his cap is $530 (20 seats x $25 + $30 replace
        headroom, 2026-08-20), so the numbers below are rescaled to it."""
        # 1. Simulate $437.27 locked in positions in oracle balance
        self.store.set_fact(Fact(
            key="kalshi.oracle.balance",
            domain="kalshi",
            value={
                "cash_usd": 850.00,
                "open_positions_usd": 437.27,
                "lifetime_deposits_usd": 1000.00,
                "timestamp": "2026-08-15T12:00:00Z",
            },
            source_artifact="live_test",
            is_immutable=False,
        ))

        # 2. Add 2 resting orders totaling $49.72 collateral
        self.store.save_order(ActiveOrder(
            order_id="ord1", ticker="T1", side="yes", price=0.22, count=113, collateral_usd=24.86, status="RESTING", lane="autoseat"
        ))
        self.store.save_order(ActiveOrder(
            order_id="ord2", ticker="T2", side="yes", price=0.22, count=113, collateral_usd=24.86, status="RESTING", lane="autoseat"
        ))

        # Total currently deployed = $437.27 (positions) + $49.72 (resting) = $486.99
        # Attempting to deploy another $49.94 (Total = $536.93 > $530 cap) MUST BE REJECTED!
        over_proposal = {
            "ticker": "KXFEDFUNDSYEAR-26-HOLD",
            "side": "yes",
            "price": 0.22,
            "count": 227,
            "notional_usd": 49.94,
        }
        valid, violations, _ = self.engine.validate_order_proposal(over_proposal)
        self.assertFalse(valid)
        self.assertTrue(any("exceeds total portfolio budget of $530.00" in v for v in violations), violations)

class TestMultiFamilyCensusScan(CensusGateTestBase):
    """The discovery sweep must return ONE representative per family, so that a
    single large slate drop cannot crowd every other family out of the census
    window, and each representative must carry a real verdict.

    THIS TEST USED TO HIT THE LIVE VENUE.  It built a bare CensusScanner(), which
    defaults to the production kalshi_domain.db and a real KalshiVenueClient, so
    it synced the live catalog over the network, WROTE the live domain DB, and
    then asserted that three hard-coded families (KXFEDFUNDSYEAR, KXUSCPIYEAR,
    KXSTATEBALLOTMEASURE) were among the results.  That asserts the venue's
    inventory on the day the test runs, not the scanner's behaviour: the sweep
    takes the 250 newest families, the live catalog grew past that tonight, and
    KXFEDFUNDSYEAR aged out — so the test went red without a line of scanner code
    being wrong.  It is now hermetic (temp DB, stubbed client, seeded families),
    which is also what keeps it from writing production state.
    """

    FAMILIES = ("KXFEDFUNDSYEAR", "KXUSCPIYEAR", "KXSTATEBALLOTMEASURE",
                "KXNFLGAME", "KXMLBGAME", "KXBTCD")

    def _slate(self):
        """One event per family, plus a SECOND market inside one family — the
        crowding case the per-family grouping exists to defeat."""
        events = []
        for fam in self.FAMILIES:
            events.append(self.event(
                f"{fam}-26AUG21",
                [{"ticker": f"{fam}-26AUG21-A",
                  "expected_expiration_time": _hours_from_now(90),
                  "status": "active"}],
                title=f"{fam} stub"))
        events.append(self.event(
            "KXNFLGAME-26AUG22",
            [{"ticker": f"KXNFLGAME-26AUG22-{i}",
              "expected_expiration_time": _hours_from_now(90),
              "status": "active"} for i in range(40)],
            title="KXNFLGAME slate drop"))
        return events

    def test_every_family_gets_exactly_one_classified_representative(self):
        events = self._slate()
        books = {m["ticker"]: DEEP_BOOK
                 for ev in events for m in ev["markets"]}
        scanner, _ = self.make_scanner(events, books=books)
        opps = scanner.scan_family_opportunities()

        families = [o["family"] for o in opps]
        for fam in self.FAMILIES:
            self.assertIn(fam, families)
        self.assertEqual(sorted(families), sorted(set(families)),
                         "the sweep must return ONE row per family")
        self.assertGreaterEqual(len(opps), 5)

    def test_a_slate_drop_cannot_crowd_out_the_other_families(self):
        """40 markets in one family must not displace the other five."""
        events = self._slate()
        books = {m["ticker"]: DEEP_BOOK
                 for ev in events for m in ev["markets"]}
        scanner, _ = self.make_scanner(events, books=books)
        families = {o["family"] for o in scanner.scan_family_opportunities()}
        self.assertTrue(set(self.FAMILIES) <= families)

    def test_each_representative_carries_a_verdict_and_a_reason(self):
        events = self._slate()
        books = {m["ticker"]: DEEP_BOOK
                 for ev in events for m in ev["markets"]}
        scanner, _ = self.make_scanner(events, books=books)
        for o in scanner.scan_family_opportunities():
            self.assertTrue(o["status"], f"no verdict on {o['ticker']}")
            self.assertTrue(o["reason"], f"no reason on {o['ticker']}")
            self.assertIn("curfew", o["gates"])

    def test_ballot_families_are_still_yes_only(self):
        """The base-rate side gate survives the multi-family path: a BALLOT
        family is never recommended NO."""
        events = self._slate()
        books = {m["ticker"]: DEEP_BOOK
                 for ev in events for m in ev["markets"]}
        scanner, _ = self.make_scanner(events, books=books)
        ballot = next(o for o in scanner.scan_family_opportunities()
                      if o["family"] == "KXSTATEBALLOTMEASURE")
        self.assertNotIn("no", ballot["recommended_sides"])


if __name__ == "__main__":
    unittest.main()
