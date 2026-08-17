import sys
from pathlib import Path
import unittest
from unittest.mock import MagicMock

# Import virgil wire from nestor-wt-lipv5
tools_dir = Path(__file__).resolve().parents[2] / "nestor-wt-lipv5" / "tools"
sys.path.insert(0, str(tools_dir))

from virgil import wire as WIRE
from domains.kalshi.harness.venue_client import KalshiVenueClient



class TestWireInvariantEnforcement(unittest.TestCase):
    def setUp(self):
        self.mock_auth = MagicMock()
        self.mock_auth.headers.return_value = {"KALSHI-ACCESS-KEY": "test", "KALSHI-ACCESS-SIGNATURE": "sig", "KALSHI-ACCESS-TIMESTAMP": "123"}
        self.client = WIRE.KalshiClient(self.mock_auth)

    def test_wire_rejects_single_order_exceeding_50_dollars(self):
        """CRITICAL: Wire layer rejects order costing > $50.00 without network call."""
        status, body = self.client.place_order(
            ticker="KXTEST-26",
            side="bid",
            price_dollars=0.60,
            count=100,  # $60.00
            coid="test-1",
        )
        self.assertEqual(status, 403)
        self.assertEqual(body.get("code"), "CAP_EXCEEDED")

    def test_wire_rejects_asymmetric_taker_death_trap_90c_plus(self):
        """CRITICAL: Wire layer rejects buying at >= 90c (e.g. 98c mirror pilot trap)."""
        status, body = self.client.place_order(
            ticker="KXTEMPAUSH-26AUG16-94",
            side="bid",
            price_dollars=0.98,
            count=50,  # $49.00 at 98c
            coid="test-2",
        )
        self.assertEqual(status, 403)
        self.assertEqual(body.get("code"), "ASYMMETRIC_TRAP_REJECTED")

    def test_wire_rejects_toxic_no_on_ballot_measures(self):
        """CRITICAL: Wire layer rejects selling cheap NO at <= 35c on state ballot/bond measures."""
        status, body = self.client.place_order(
            ticker="KXSTATEBALLOTMEASURE-KY-A1",
            side="ask",
            price_dollars=0.70,  # YES at 70c -> NO acquired at 30c (<=35c)
            count=100,
            coid="test-3",
        )
        self.assertEqual(status, 403)
        self.assertEqual(body.get("code"), "TOXIC_NO_BASE_RATE_BREACH")

    def test_venue_client_harness_rejects_breaches(self):
        """CRITICAL: VenueClient in domains/kalshi/ also enforces invariants."""
        vc = KalshiVenueClient()
        vc.api_key_id = "test"
        vc._private_key = MagicMock()

        # >$50 cap
        with self.assertRaises(ValueError) as ctx:
            vc.place_post_only_order(ticker="KXTEST", side="yes", price_cents=60, count=100, client_order_id="test")
        self.assertIn("exceeds $50.00", str(ctx.exception))

        # >=90c trap
        with self.assertRaises(ValueError) as ctx:
            vc.place_post_only_order(ticker="KXTEST", side="yes", price_cents=98, count=50, client_order_id="test")
        self.assertIn(">= 90c strictly prohibited", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
