"""End-to-End CLI Smoke Tests for Kalshi Domain Pod.

Verifies that ALL CLI subcommands execute without ImportErrors, syntax errors, or schema crashes.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

POD_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
for p in [str(REPO_ROOT), str(POD_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

import contextlib
import io

from domains.kalshi.interface.cli import main as kalshi_main
from domains.kalshi.state.db import Database
from domains.kalshi.state.fact_store import FactStore
from domains.kalshi.state.seed import seed_kalshi_database


class _StubVenue:
    """A credentialed venue whose ledgers the CLI must consult (CAP-5)."""

    def __init__(self, orders=None, positions=None, balance=None, balance_error=None):
        self.has_credentials = True
        self.orders = list(orders or [])
        self.positions = list(positions or [])
        self.balance = balance or {"balance": 50000, "portfolio_value": 0, "lifetime_deposits": 50000}
        self.balance_error = balance_error
        self.calls = []
        # FLAT-7: the reads and the one write a flatten needs
        self.books = {}
        self.closes = []

    def fetch_balance(self):
        self.calls.append("balance")
        if self.balance_error:
            raise RuntimeError(self.balance_error)
        return dict(self.balance)

    def fetch_open_orders(self):
        self.calls.append("orders")
        return list(self.orders)

    def fetch_positions(self):
        self.calls.append("positions")
        return list(self.positions)

    def fetch_public_orderbook(self, ticker):
        self.calls.append("book")
        return self.books[ticker]

    def cancel_order(self, order_id):
        # VR-6: sync-orders cancels orphan orders through the reconciler
        self.calls.append("cancel")
        self.orders = [o for o in self.orders if str(o.get("order_id")) != str(order_id)]
        return {"order": {"order_id": order_id, "status": "canceled"}}

    def place_post_only_close(self, ticker, held_side, sell_price_cents, count, client_order_id):
        self.calls.append("close")
        rec = {"ticker": ticker, "held_side": held_side, "sell_price_cents": sell_price_cents,
               "count": count, "client_order_id": client_order_id}
        self.closes.append(rec)
        return {"order": {"order_id": f"close-{len(self.closes)}", "status": "resting"}}


class TestOrderPlaceLiveConsultsTheVenue(unittest.TestCase):
    """CAP-5 (2026-09-05): `order place --live` used to gate on stale local
    state only — no oracle sync, no open-orders read — so a hand-typed $25
    order on a ticker where the engine already held a $25 seat or an
    un-flattened position passed the gate whenever the mirror row was not
    RESTING.  Ryan: "never to have more than 25$ in any market"."""

    TICKER = "KXTEST-26"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = FactStore(Database(Path(self.tmp.name) / "cli_cap5.db"))
        seed_kalshi_database(self.store)
        self.assertEqual(self.store.list_active_orders(), [])  # local ledger EMPTY

    def tearDown(self):
        self.tmp.cleanup()

    def _place(self, client, ticker=None, count=100):
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            rc = kalshi_main(["order", "place", "--ticker", ticker or self.TICKER, "--side", "no",
                              "--price-cents", "20", "--count", str(count), "--live"],
                             store=self.store, client=client)
        return rc, err.getvalue()

    def test_same_ticker_venue_order_refuses_with_empty_local_ledger(self):
        client = _StubVenue(orders=[{"order_id": "o-engine", "ticker": self.TICKER, "side": "no",
                                     "no_price": 20, "remaining_count": 125}])  # $25 live
        rc, err = self._place(client)
        self.assertEqual(rc, 1, err)
        self.assertIn("per-market cap", err)
        self.assertIn("$25.00 already in", err)
        # CAP-6 (2026-09-05): the oracle sync now reads positions too (cost
        # basis), so the venue is asked balance, positions, orders, positions.
        # The pin is the INTENT: balance first, both ledgers before the gate.
        self.assertEqual(client.calls[0], "balance")
        self.assertEqual(client.calls[:4], ["balance", "positions", "orders", "positions"])

    def test_same_ticker_venue_position_refuses(self):
        client = _StubVenue(positions=[{"ticker": self.TICKER, "position": 125,
                                        "market_exposure": 2500}])
        rc, err = self._place(client)
        self.assertEqual(rc, 1, err)
        self.assertIn("per-market cap", err)

    def test_venue_resting_total_counts_toward_the_portfolio_cap(self):
        total_cap = float(self.store.get_limits()["total_usd"])
        # $26 x N live orders on OTHER tickers so the venue total sits just
        # under the cap while the local mirror shows $0.
        n = int(total_cap // 26)
        orders = [{"order_id": f"o{i}", "ticker": f"KXOTHER-{i}", "side": "yes",
                   "yes_price": 26, "remaining_count": 100} for i in range(n)]
        client = _StubVenue(orders=orders)
        rc, err = self._place(client)  # +$20 pushes venue total over the cap
        self.assertEqual(rc, 1, err)
        self.assertIn("Total portfolio exposure", err)

    def test_oracle_sync_failure_refuses(self):
        client = _StubVenue(balance_error="HTTP 500")
        rc, err = self._place(client)
        self.assertEqual(rc, 1, err)
        self.assertIn("Oracle sync failed", err)
        self.assertNotIn("orders", client.calls)

    def test_fresh_positions_mark_is_used_not_the_stale_fact(self):
        from domains.kalshi.state.models import Fact
        self.store.set_fact(Fact(key="kalshi.oracle.balance", domain="kalshi",
                                 value={"cash_usd": 500.0, "open_positions_usd": 0.0},
                                 source_artifact="stale", verified_at="2026-09-01T00:00:00+00:00",
                                 verified_by="test", is_immutable=False))
        total_cap = float(self.store.get_limits()["total_usd"])
        client = _StubVenue(balance={"balance": 1000, "portfolio_value": int(total_cap * 100),
                                     "lifetime_deposits": 50000})
        rc, err = self._place(client)
        self.assertEqual(rc, 1, err)
        self.assertIn("Total portfolio exposure", err)
        fact = self.store.get_fact("kalshi.oracle.balance")
        self.assertEqual(fact.value["open_positions_usd"], total_cap)


class TestPositionCommands(unittest.TestCase):
    """FLAT-7 (2026-09-05): the CLI gains `position list` and
    `position flatten`.  Until today it could place and cancel but never
    sell, so every one of the 25 informed-sweep fills left a position nobody
    could close from here."""

    TICKER = "KXTEST-26"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = FactStore(Database(Path(self.tmp.name) / "cli_flat7.db"))
        seed_kalshi_database(self.store)
        self.client = _StubVenue(positions=[{"ticker": self.TICKER, "position": 100,
                                             "market_exposure": 2200}])
        self.client.books = {self.TICKER: {"orderbook": {"yes": [[22, 400]], "no": [[70, 300]]}}}

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, argv, client=None):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = kalshi_main(argv, store=self.store, client=client or self.client)
        return rc, out.getvalue(), err.getvalue()

    def test_position_list(self):
        rc, out, err = self._run(["position", "list"])
        self.assertEqual(rc, 0, err)
        self.assertIn(self.TICKER, out)
        self.assertIn("100ct YES held", out)
        self.assertIn("$22.00", out)

    def test_position_list_fails_closed_when_unreadable(self):
        client = _StubVenue()
        def boom():
            raise RuntimeError("HTTP Error 503")
        client.fetch_positions = boom
        rc, out, err = self._run(["position", "list"], client=client)
        self.assertEqual(rc, 1)
        self.assertIn("fail closed", err)

    def test_position_flatten_dry_run_places_nothing(self):
        rc, out, err = self._run(["position", "flatten", "--ticker", self.TICKER])
        self.assertEqual(rc, 0, err)
        self.assertNotIn("close", self.client.calls)
        self.assertEqual(self.client.closes, [])
        self.assertIn("gate APPROVED", out)
        self.assertIn("@ 30c", out)          # best YES ask = 100 - 70
        self.assertIn("Dry-run passed", out)
        self.assertEqual(self.store.list_active_orders(), [])

    def _verify_ledger(self):
        """FLAT-10: a full-size live close is trusted only after a 1ct probe
        fill has shown the position shrink.  Stamp the ledger verified."""
        from domains.kalshi.harness.placement_engine import write_positions_schema
        write_positions_schema(self.store, {"close_semantics_verified": True,
                                            "verdict": "close_reduces_position"},
                               "2026-09-05T00:00:00+00:00", by="test")

    def test_position_flatten_live_places_one_close_and_mirrors_it(self):
        self._verify_ledger()
        rc, out, err = self._run(["position", "flatten", "--ticker", self.TICKER, "--live"])
        self.assertEqual(rc, 0, err)
        self.assertIn("FLAT-10 close semantics: VERIFIED", out)
        self.assertEqual(len(self.client.closes), 1)
        c = self.client.closes[0]
        self.assertEqual((c["held_side"], c["sell_price_cents"], c["count"]), ("yes", 30, 100))
        self.assertTrue(c["client_order_id"].startswith("kfl-"))
        mirror = self.store.list_active_orders()
        self.assertEqual(len(mirror), 1)
        self.assertEqual((mirror[0].lane, mirror[0].collateral_usd, mirror[0].ticker),
                         ("flatten", 0.0, self.TICKER))
        self.assertIn("Live close placed", out)

    # --- FLAT-10 (2026-09-05): the close path is probed before it is trusted ---

    def test_position_flatten_live_full_size_refused_until_probe_verified(self):
        rc, out, err = self._run(["position", "flatten", "--ticker", self.TICKER, "--live"])
        self.assertEqual(rc, 1)
        self.assertIn("FLAT-10", err)
        self.assertIn("--count 1 --live", err)
        self.assertEqual(self.client.closes, [])
        self.assertEqual(self.store.list_active_orders(), [])
        self.assertIn("UNVERIFIED", out)

    def test_position_flatten_probe_count_1_live_places_and_records(self):
        rc, out, err = self._run(["position", "flatten", "--ticker", self.TICKER,
                                  "--count", "1", "--live"])
        self.assertEqual(rc, 0, err)
        self.assertEqual(len(self.client.closes), 1)
        self.assertEqual(self.client.closes[0]["count"], 1)
        self.assertIn("FLAT-10 PROBE order", out)
        ledger = self.store.get_fact("kalshi.ops.positions_schema").value
        self.assertEqual(ledger["verdict"], "probe_placed")
        self.assertIs(ledger["close_semantics_verified"], False)
        self.assertEqual(ledger["probe"]["held_before"], 100)
        self.assertEqual(ledger["count_key"], "position")

    def test_position_list_prints_raw_rows_and_pins_the_schema(self):
        rc, out, err = self._run(["position", "list"])
        self.assertEqual(rc, 0, err)
        self.assertIn(f"raw {self.TICKER}:", out)
        self.assertIn('"position": 100', out)
        self.assertIn("count_key='position' exposure_key='market_exposure'", out)
        self.assertIn("close semantics: UNVERIFIED", out)
        ledger = self.store.get_fact("kalshi.ops.positions_schema").value
        self.assertEqual((ledger["count_key"], ledger["exposure_key"]), ("position", "market_exposure"))
        self.assertIsNotNone(ledger["schema_pinned_at"])
        self.assertIs(ledger["close_semantics_verified"], False)  # a listing never verifies

    def test_position_flatten_refuses_when_flat_or_without_credentials(self):
        flat = _StubVenue(positions=[])
        flat.books = dict(self.client.books)
        rc, out, err = self._run(["position", "flatten", "--ticker", self.TICKER, "--live"], client=flat)
        self.assertEqual(rc, 1)
        self.assertIn("FLAT", err)
        self.assertEqual(flat.closes, [])
        # a bare, credential-less client cannot read the position: refuse, never guess
        rc, out, err = self._run(["position", "flatten", "--ticker", self.TICKER],
                                 client=KalshiVenueClientNoCreds())
        self.assertEqual(rc, 1)
        self.assertIn("fail closed", err)


class TestSyncOrdersIsTheReconciler(unittest.TestCase):
    """VR-6 (2026-09-05): `sync-orders` calls harness/venue_reconciler --
    the same function the cadence daemon runs every cycle -- in mirror mode.
    It used to be a third reconciler of its own that overwrote the engine's
    'deployment_plan' lane with 'general' and could not cancel an orphan."""

    TICKER = "KXTEST-26"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = FactStore(Database(Path(self.tmp.name) / "cli_vr6.db"))
        seed_kalshi_database(self.store)
        self.store.set_placement_state("DISARMED", "test", "test")

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, argv, client):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = kalshi_main(argv, store=self.store, client=client)
        return rc, out.getvalue(), err.getvalue()

    def _mirror(self, oid):
        with self.store.db.get_connection() as conn:
            row = conn.execute("SELECT status, lane FROM active_orders WHERE order_id=?", (oid,)).fetchone()
        return None if row is None else (row[0], row[1])

    def test_sync_orders_prints_the_reconciler_count_line_and_cancels_the_orphan(self):
        from domains.kalshi.state.models import ActiveOrder
        # an engine-owned seat: plan row + mirror in lane 'deployment_plan'
        self.store.upsert_deployment_plan(ticker=self.TICKER, side="no", price_cents=20,
                                          count=100, max_escrow_usd=20.0)
        row = self.store.list_deployment_plan()[-1]
        self.store.update_deployment_plan(row["id"], status="resting", order_id="o-eng")
        self.store.save_order(ActiveOrder(
            order_id="o-eng", ticker=self.TICKER, side="no", price=0.20, count=100,
            collateral_usd=20.0, status="RESTING", lane="deployment_plan",
            placed_at="2026-09-05T00:00:00+00:00", updated_at="2026-09-05T00:00:00+00:00"))
        client = _StubVenue(orders=[
            {"order_id": "o-eng", "ticker": self.TICKER, "outcome_side": "no", "no_price": 20,
             "remaining_count": 100, "created_time": "2026-09-05T00:00:00Z"},
            {"order_id": "01a069d1", "ticker": "KXUST10AM-26SEP", "outcome_side": "no", "no_price": 20,
             "remaining_count": 125, "created_time": "2026-09-04T00:00:00Z"},
        ])
        rc, out, err = self._run(["sync-orders"], client)
        self.assertEqual(rc, 0, err)
        self.assertIn("VenueReconcile:", out)
        self.assertIn("2 venue order(s) mirrored RESTING (1 lane(s) preserved)", out)
        self.assertIn("1 ORPHAN order(s) CANCELLED on venue", out)
        self.assertIn("KXUST10AM-26SEP 01a069d1", out)
        self.assertEqual(client.calls.count("cancel"), 1)
        self.assertEqual(self._mirror("o-eng"), ("RESTING", "deployment_plan"), "lane preserved")
        self.assertEqual(self._mirror("01a069d1"), ("CANCELLED", "general"))

    def test_no_cancel_orphans_reports_only(self):
        client = _StubVenue(orders=[
            {"order_id": "01a069d1", "ticker": "KXUST10AM-26SEP", "outcome_side": "no", "no_price": 20,
             "remaining_count": 125, "created_time": "2026-09-04T00:00:00Z"}])
        rc, out, err = self._run(["sync-seats", "--no-cancel-orphans"], client)
        self.assertEqual(rc, 0, err)
        self.assertIn("cancel disabled", out)
        self.assertNotIn("cancel", client.calls)
        self.assertEqual(self._mirror("01a069d1"), ("RESTING", "general"))

    def test_unreadable_venue_fails_closed_rc_1(self):
        client = _StubVenue()
        client.fetch_open_orders = lambda: (_ for _ in ()).throw(RuntimeError("HTTP Error 503"))
        rc, out, err = self._run(["sync-orders"], client)
        self.assertEqual(rc, 1)
        self.assertIn("fail closed", err)


def KalshiVenueClientNoCreds():
    from domains.kalshi.harness.venue_client import KalshiVenueClient
    return KalshiVenueClient(api_key_id="", private_key_path="/nonexistent/key.pem")


class _EmptyBookVenue:
    """An EMPTY venue: no orders, no positions, a funded balance and Ryan's
    13 deposits.  Every method the order/oracle paths call, and nothing else --
    an unstubbed call raises AttributeError rather than reaching the network."""
    has_credentials = True

    def fetch_balance(self):
        return {"balance": 96610, "portfolio_value": 0}

    def fetch_open_orders(self):
        return []

    def fetch_positions(self):
        return []

    def fetch_deposits(self):
        return [{"amount_dollars": "200.00", "status": "applied"} for _ in range(13)]

    def fetch_withdrawals(self):
        return []

    def venue_committed_usd(self, ticker):
        return {"ok": True, "ticker": ticker, "orders_usd": 0.0, "position_usd": 0.0,
                "total_usd": 0.0, "n_orders": 0, "position_ct": 0.0, "detail": "stub: flat"}

    def cancel_order(self, *a, **k):
        return {"ok": True}


class TestKalshiCLISmoke(unittest.TestCase):
    def test_cli_main_status(self):
        """Verify kalshi status runs with code 0."""
        rc = kalshi_main(["status"])
        self.assertEqual(rc, 0)

    def test_cli_main_seed(self):
        """Verify kalshi seed runs with code 0."""
        rc = kalshi_main(["seed"])
        self.assertEqual(rc, 0)

    def test_cli_main_telemetry(self):
        """Verify kalshi telemetry outputs valid JSON."""
        rc = kalshi_main(["telemetry"])
        self.assertEqual(rc, 0)

    def test_cli_main_order_place_and_cancel_dry_run(self):
        """Verify order placement and cancellation execution through gate."""
        # 2026-09-05: the suite no longer runs against the live laptop DB
        # (conftest points a bare FactStore() at a temp file), so the caps
        # fact the gate fails closed on must be seeded here, not inherited.
        self.assertEqual(kalshi_main(["seed"]), 0)
        # MT-8 (2026-09-09): this test used the REAL venue client, so its
        # verdict moved with Ryan's live book -- it passed at a 10-seat book
        # and failed at 19 ($455.03 resting + $74.82 positions + $20 proposed
        # > the $530 cap), which is the gate working, not a code defect.  A
        # unit test may not depend on live account state: the venue is stubbed
        # to an EMPTY book so the assertion is about the gate's logic.
        client = _EmptyBookVenue()
        rc_place = kalshi_main(["order", "place", "--ticker", "KXTEST-26", "--side", "no",
                                "--price-cents", "20", "--count", "100"], client=client)
        self.assertEqual(rc_place, 0)

        rc_cancel = kalshi_main(["order", "cancel", "--order-id", "ord_test_123"], client=client)
        self.assertEqual(rc_cancel, 0)

    def test_cli_main_seed_book_smoke(self):
        """Verify kalshi seed-book runs with code 0."""
        rc = kalshi_main(["seed-book", "--target", "0"])
        self.assertEqual(rc, 0)

    def test_cli_subprocess_invocation(self):
        """Verify ./kalshi.py executable runs in its own process without import errors."""
        res = subprocess.run(
            [sys.executable, str(POD_DIR / "kalshi.py"), "status"],
            cwd=str(POD_DIR),
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"kalshi.py status failed: {res.stderr}")
        self.assertIn("KALSHI DOMAIN POD", res.stdout)

    def test_cli_subprocess_telemetry(self):
        """Verify ./kalshi.py telemetry outputs valid domain telemetry JSON."""
        res = subprocess.run(
            [sys.executable, str(POD_DIR / "kalshi.py"), "telemetry"],
            cwd=str(POD_DIR),
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"kalshi.py telemetry failed: {res.stderr}")
        data = json.loads(res.stdout)
        self.assertEqual(data["domain_id"], "kalshi")
        self.assertIn("resource_consumption", data)
        self.assertIn("domain_metrics", data)


if __name__ == "__main__":
    unittest.main()
