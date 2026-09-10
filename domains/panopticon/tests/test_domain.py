"""Panopticon pod invariants — the gates, not the game."""
import json
import unittest
from contextlib import ExitStack
from datetime import date

import pytest

from domains.panopticon.interface import head_prompt as hp
from domains.panopticon.state.canon import seed
from domains.panopticon.state.db import Database
from domains.panopticon.verify import oracle, schedule, scope


@pytest.fixture(autouse=True)
def _c(pod_db, request):
    """A seeded pod DB plus one live connection per test.

    ExitStack, not `get_connection().__enter__()`: the bare form drops the last
    reference to the generator, Python finalises it, and the `finally: conn.close()`
    fires immediately -- every test then hit "Cannot operate on a closed database".
    """
    request.cls.db = pod_db
    with pod_db.get_connection() as conn:
        seed(conn)
    stack = ExitStack()
    request.cls.conn = stack.enter_context(pod_db.get_connection())
    yield
    stack.close()


class TestScopeRatchet(unittest.TestCase):
    def test_ship_blocking_addition_must_displace(self):
        with self.assertRaises(scope.ScopeViolation):
            scope.add_feature(self.conn, "Destructible cover", "SHIP_BLOCKING",
                              today=date(2026, 11, 1))

    def test_displacement_cuts_the_displaced_feature(self):
        scope.add_feature(self.conn, "Destructible cover", "SHIP_BLOCKING",
                          displaced="Sound effects", today=date(2026, 11, 1))
        row = self.conn.execute(
            "SELECT status FROM scope_ledger WHERE feature='Sound effects'").fetchone()
        self.assertEqual(row["status"], "CUT")

    def test_a_cut_feature_cannot_pay_twice(self):
        scope.add_feature(self.conn, "A", "SHIP_BLOCKING", displaced="Sound effects",
                          today=date(2026, 11, 1))
        with self.assertRaises(scope.ScopeViolation):
            scope.add_feature(self.conn, "B", "SHIP_BLOCKING", displaced="Sound effects",
                              today=date(2026, 11, 1))

    def test_displacing_something_that_does_not_exist_is_refused(self):
        with self.assertRaises(scope.ScopeViolation):
            scope.add_feature(self.conn, "A", "SHIP_BLOCKING", displaced="Nonexistent",
                              today=date(2026, 11, 1))

    def test_wanted_and_stretch_add_freely_before_freeze(self):
        scope.add_feature(self.conn, "Spectator mode", "WANTED", today=date(2026, 11, 1))
        scope.add_feature(self.conn, "Hats", "STRETCH", today=date(2026, 11, 1))

    def test_nothing_is_added_after_feature_freeze(self):
        after = date(2027, 3, 1)
        self.assertTrue(scope.is_frozen(self.conn, after))
        for tier in ("SHIP_BLOCKING", "WANTED", "STRETCH"):
            with self.assertRaises(scope.ScopeViolation):
                scope.add_feature(self.conn, f"late-{tier}", tier,
                                  displaced="Sound effects", today=after)

    def test_a_cut_feature_keeps_its_row_so_it_cannot_silently_return(self):
        scope.cut_feature(self.conn, "Music", "no composer", today=date(2026, 12, 1))
        row = self.conn.execute(
            "SELECT status, cut_on, notes FROM scope_ledger WHERE feature='Music'").fetchone()
        self.assertEqual(row["status"], "CUT")
        self.assertEqual(row["cut_on"], "2026-12-01")
        self.assertIn("no composer", row["notes"])


class TestOracle(unittest.TestCase):
    def test_nothing_is_done_without_a_build_that_ran(self):
        ok, why = oracle.can_claim_done(self.conn, "Sound effects")
        self.assertFalse(ok)
        self.assertIn("headless bot match", why)
        with self.assertRaises(ValueError):
            oracle.mark_done(self.conn, "Sound effects")

    def test_a_build_that_did_not_launch_does_not_count(self):
        self.conn.execute("INSERT INTO builds (tag, built_on, commit_sha, platform, launched, "
                          "headless_match_passed) VALUES ('v0','2026-10-01','abc','windows',0,1)")
        self.conn.commit()
        self.assertFalse(oracle.can_claim_done(self.conn, "x")[0])

    def test_a_build_that_launched_and_passed_a_match_unlocks_done(self):
        self.conn.execute("INSERT INTO builds (tag, built_on, commit_sha, platform, launched, "
                          "headless_match_passed) VALUES ('v1','2026-10-01','abc','windows',1,1)")
        self.conn.commit()
        why = oracle.mark_done(self.conn, "Sound effects")
        self.assertIn("v1", why)
        row = self.conn.execute(
            "SELECT status FROM scope_ledger WHERE feature='Sound effects'").fetchone()
        self.assertEqual(row["status"], "DONE")

    def test_balance_evidence_is_empty_until_matches_exist(self):
        ev = oracle.balance_evidence(self.conn, 1, 3)
        self.assertEqual(ev["matches"], 0)
        self.assertIsNone(ev["guard_win_rate"])

    def test_human_sessions_are_counted_separately(self):
        for kind in ("BOT", "BOT", "HUMAN"):
            self.conn.execute(
                "INSERT INTO playtests (played_on, kind, build_tag, guards, prisoners, matches, "
                "guard_wins) VALUES ('2026-10-02',?,'v1',1,3,10,6)", (kind,))
        self.conn.commit()
        ev = oracle.balance_evidence(self.conn, 1, 3)
        self.assertEqual(ev["sessions"], 3)
        self.assertEqual(ev["human_sessions"], 1)
        self.assertEqual(ev["guard_win_rate"], 0.6)


class TestSchedule(unittest.TestCase):
    def test_ship_date_is_canon(self):
        self.assertEqual(schedule.SHIP, date(2027, 4, 1))

    def test_pc_hours_are_the_scarce_budget(self):
        self.assertEqual(schedule.days_left(date(2026, 9, 9)), 204)
        self.assertAlmostEqual(schedule.pc_hours_left(date(2026, 9, 9)), 233.1, places=1)

    def test_hard_steam_gates_exist_and_precede_ship(self):
        ms = {m["name"]: m for m in schedule.milestones(self.conn, date(2026, 9, 9))}
        for name in ("steam_fee_paid_and_app_created", "steam_store_page_public",
                     "steam_build_uploaded_and_reviewed"):
            self.assertTrue(ms[name]["hard"], f"{name} must be a hard external gate")
            self.assertLess(ms[name]["due"], date(2027, 4, 1))

    def test_fee_precedes_release_by_at_least_the_mandatory_thirty_days(self):
        ms = {m["name"]: m for m in schedule.milestones(self.conn, date(2026, 9, 9))}
        gap = (date(2027, 4, 1) - ms["steam_fee_paid_and_app_created"]["due"]).days
        self.assertGreaterEqual(gap, 30)

    def test_store_page_precedes_launch_by_at_least_two_weeks(self):
        ms = {m["name"]: m for m in schedule.milestones(self.conn, date(2026, 9, 9))}
        self.assertGreaterEqual((date(2027, 4, 1) - ms["steam_store_page_public"]["due"]).days, 14)

    def test_an_overdue_open_milestone_is_a_breach(self):
        brs = schedule.breaches(self.conn, date(2027, 1, 1))
        self.assertTrue(any(b["name"] == "pc_bootstrapped" for b in brs))


class TestCanonAndPrompt(unittest.TestCase):
    def test_ryan_verbatim_words_are_stored_not_paraphrased(self):
        r = self.conn.execute(
            "SELECT authorized FROM facts WHERE key='panopticon.game.definition'").fetchone()
        self.assertIn("panopticon in the middle of the map", r["authorized"])

    def test_only_ryan_quoted_facts_claim_ryan(self):
        for r in self.conn.execute("SELECT key, authorized, verified_by, ratified_on FROM facts"):
            if r["verified_by"] == "ryan":
                self.assertTrue(r["authorized"].strip(),
                                f"{r['key']} claims ryan with no verbatim quote")
                self.assertTrue(r["ratified_on"].strip(), f"{r['key']} has no ratified_on")

    def test_prompt_is_built_from_the_db(self):
        before = hp.build_head_prompt(self.conn)
        self.assertIn("panopticon in the middle of the map", before)
        self.conn.execute("UPDATE facts SET value=?, authorized='SENTINEL' "
                          "WHERE key='panopticon.game.definition'",
                          (json.dumps({"core_loop": "SENTINEL LOOP"}),))
        self.conn.commit()
        after = hp.build_head_prompt(self.conn)
        self.assertIn("SENTINEL LOOP", after)
        self.assertNotIn("panopticon in the middle of the map", after)

    def test_missing_fact_prints_missing(self):
        self.assertIn("MISSING FROM DB", hp.canon_block(self.conn, ["panopticon.not.a.fact"]))

    def test_open_questions_are_not_answered_by_the_prompt(self):
        block = hp.open_questions_block(self.conn)
        self.assertIn("guard_vision", block)
        self.assertIn("resolve by", block)

    def test_canon_stays_within_budget(self):
        p = hp.build_head_prompt(self.conn)
        self.assertLessEqual(hp.canon_line_count(p), hp.CANON_MAX_LINES)

    def test_bots_are_canon_because_there_are_no_testers(self):
        r = self.conn.execute(
            "SELECT value FROM facts WHERE key='panopticon.testing.bots'").fetchone()
        self.assertIn("no friends", json.loads(r["value"])["constraint"])

    def test_seed_is_idempotent(self):
        with self.db.get_connection() as c:
            seed(c); seed(c)
            n = c.execute("SELECT count(*) n FROM facts").fetchone()["n"]
            k = c.execute("SELECT count(DISTINCT key) n FROM facts").fetchone()["n"]
        self.assertEqual(n, k)


class TestWorkQueue(unittest.TestCase):
    """Ryan, 2026-09-09: 'i want it constantly evaluating what needs to get done and hacing
    either me or it working on it.' These pin the mechanism that makes that true."""

    def test_seeded_queue_has_work_in_every_lane(self):
        from domains.panopticon.verify import queue
        b = queue.burn(self.conn)
        for lane in ("REMOTE", "PC_REQUIRED", "RYAN_DECISION"):
            self.assertGreater(b.get(lane, 0), 0, f"no open {lane} work seeded")

    def test_head_always_has_something_it_can_start_alone(self):
        from domains.panopticon.verify import queue
        self.assertTrue(queue.next_remote(self.conn),
                        "the head has no unattended work — that is a planning failure")
        self.assertFalse(queue.head_is_idle(self.conn))

    def test_a_pc_task_is_not_ready_while_remote_prerequisites_are_open(self):
        """The mechanism that protects the 233 remaining PC hours."""
        from domains.panopticon.verify import queue
        plan = [t["title"] for t in queue.pc_session_plan(self.conn)]
        self.assertNotIn("Play the greybox slice and judge whether it is fun", plan)

    def test_clearing_a_blocker_promotes_the_dependent_task(self):
        from domains.panopticon.verify import queue
        self.conn.execute("UPDATE tasks SET status='DONE' WHERE title=?",
                          ("Decide how the Senate repo reaches the PC",))
        self.conn.commit()
        plan = [t["title"] for t in queue.pc_session_plan(self.conn)]
        self.assertIn("Run bootstrap_pc.ps1 on the PC", plan)

    def test_a_typo_blocker_blocks_rather_than_silently_unblocking(self):
        from domains.panopticon.verify import queue
        self.conn.execute("INSERT INTO tasks (title, lane, owner, blocked_by, created_on) "
                          "VALUES ('typo task','REMOTE','HEAD','No Such Task','2026-09-09')")
        self.conn.commit()
        queue.refresh(self.conn)
        row = self.conn.execute("SELECT status FROM tasks WHERE title='typo task'").fetchone()
        self.assertEqual(row["status"], "BLOCKED")

    def test_idle_head_with_open_work_is_detected(self):
        from domains.panopticon.verify import queue
        self.conn.execute("UPDATE tasks SET blocked_by='Buy Astra access' WHERE lane='REMOTE'")
        self.conn.commit()
        self.assertTrue(queue.head_is_idle(self.conn),
                        "an idle head with open work must be detectable, not silent")

    def test_pc_session_respects_the_hour_budget(self):
        from domains.panopticon.verify import queue
        self.conn.execute("UPDATE tasks SET status='READY', blocked_by='' WHERE lane='PC_REQUIRED'")
        self.conn.commit()
        plan = queue.pc_session_plan(self.conn, hours=1.0)
        self.assertLessEqual(sum(t["estimate_hours"] for t in plan), 1.0)

    def test_ryans_corrections_are_recorded_as_decisions(self):
        topics = [r["topic"] for r in self.conn.execute("SELECT topic FROM decisions")]
        self.assertIn("content: audience before store page", topics)
        self.assertIn("the pod tracks tasks, not just gates", topics)

    def test_audience_building_does_not_wait_on_the_store_page(self):
        r = self.conn.execute(
            "SELECT value FROM facts WHERE key='panopticon.content.strategy'").fetchone()
        self.assertIn("does not wait on the store page", json.loads(r["value"])["metric"])

    def test_queue_reaches_the_head_prompt(self):
        p = hp.build_head_prompt(self.conn)
        self.assertIn("WORK QUEUE", p)
        self.assertIn("NEVER IDLE", p)


class TestTruthOwnership(unittest.TestCase):
    def test_before_bootstrap_this_host_holds_truth(self):
        b = hp.host_block(self.conn)
        self.assertIn("THIS DB IS TRUTH", b)
        self.assertNotIn("MIRROR", b)

    def test_after_bootstrap_a_non_pc_host_is_a_mirror(self):
        self.conn.execute("UPDATE milestones SET status='DONE' WHERE name='pc_bootstrapped'")
        self.conn.commit()
        self.assertIn("MIRROR", hp.host_block(self.conn))
