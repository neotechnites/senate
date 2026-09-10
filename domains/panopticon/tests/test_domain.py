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

    def test_the_pc_plan_does_not_budget_by_estimated_hours(self):
        """Ryan, 2026-09-09: 'i have never ever ever seen you estimate hours correctly.
        rip it out of your brain.'  block() stopped printing hours that day; the planner
        kept computing with them until 2026-09-10."""
        import inspect
        from domains.panopticon.verify import queue
        self.conn.execute("UPDATE tasks SET status='READY', blocked_by='' WHERE lane='PC_REQUIRED'")
        self.conn.commit()
        plan = queue.pc_session_plan(self.conn)
        self.assertTrue(plan)
        self.assertNotIn("hours", inspect.signature(queue.pc_session_plan).parameters)
        self.assertNotIn("estimate_hours", inspect.getsource(queue.pc_session_plan))

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
        self.assertIn("THE QUEUE IS THE WORK", p)
        self.assertIn("PLANNING FAILURE", p)


class TestTruthOwnership(unittest.TestCase):
    def test_before_bootstrap_this_host_holds_truth(self):
        b = hp.host_block(self.conn)
        self.assertIn("THIS DB IS TRUTH", b)
        self.assertNotIn("MIRROR", b)

    def test_after_bootstrap_the_mac_stays_authoritative(self):
        """Decision 26, Ryan verbatim: 'no we dont need to make that change, ill work with
        you here for now.'  The old rule declared this host a MIRROR once the PC was up,
        so the head's second line told it not to trust the only DB it can write."""
        self.conn.execute("UPDATE milestones SET status='DONE' WHERE name='pc_bootstrapped'")
        self.conn.commit()
        b = hp.host_block(self.conn)
        self.assertIn("AUTHORITATIVE", b)
        self.assertNotIn("MIRROR", b)


class TestStandingOrders(unittest.TestCase):
    """Ryan repeated orders he had already given because the boot prompt rendered the 8
    newest rulings out of 46 and everything older aged off the edge.  These pin the fix."""

    SEED_DAY = date(2026, 9, 9)

    def _decide(self, topic, ruling, pinned=0, superseded=None):
        self.conn.execute(
            "INSERT INTO decisions (decided_on, topic, ruling, rationale, evidence, "
            "pinned, superseded_by) VALUES (?,?,?,?,?,?,?)",
            (self.SEED_DAY.isoformat(), topic, ruling, "test", "ryan ruling",
             pinned, superseded))
        self.conn.commit()

    def test_a_pinned_ruling_renders_however_old_it_is(self):
        self._decide("ancient standing order", "NEVER do the forbidden thing.", pinned=1)
        for i in range(20):
            self._decide(f"newer ruling {i}", f"something else {i}")
        p = hp.build_head_prompt(self.conn)
        self.assertIn("STANDING ORDERS", p)
        self.assertIn("NEVER do the forbidden thing.", p,
                      "a pinned order aged out of the prompt — the original defect")

    def test_a_superseded_ruling_never_reaches_the_head(self):
        self._decide("withdrawn", "The head makes small changes itself.", superseded=999)
        p = hp.build_head_prompt(self.conn)
        self.assertNotIn("The head makes small changes itself.", p)

    def test_a_pinned_ruling_is_not_printed_twice(self):
        self._decide("pinned once", "EXACTLY ONE COPY OF THIS.", pinned=1)
        p = hp.build_head_prompt(self.conn)
        self.assertEqual(p.count("EXACTLY ONE COPY OF THIS."), 1)

    def test_the_prompt_carries_the_cost_rule_and_the_bots_correction(self):
        """Decision 45 (token discipline) and decision 36 (bots are not an oracle).  The
        prompt used to assert the opposite of 36 in its own prose: 'BOTS ARE THE ORACLE'."""
        p = hp.build_head_prompt(self.conn)
        self.assertIn("SPEND LIKE IT COSTS", p)
        self.assertIn("CHEAP model", p)
        self.assertNotIn("BOTS ARE THE ORACLE", p)
        self.assertIn("not an oracle", p)

    def test_the_verification_traps_are_rendered_not_filed(self):
        p = hp.build_head_prompt(self.conn)
        self.assertIn("VERIFICATION TRAPS", p)
        self.assertIn("EMPTY OUTPUT IS NOT A PASS", p)
        self.assertIn("reload()", p)


class TestInvariantsHaveTeeth(unittest.TestCase):
    """The pod's own standing rule, from panopticon.engineering.verification_traps:
    'A verification method is not trusted until it has been shown to FAIL on a
    deliberately broken input.'  verify/invariants.py was a stub that could not fail."""

    DAY = date(2026, 9, 9)

    def _check(self):
        from domains.panopticon.verify import invariants
        return invariants.check(self.conn, today=self.DAY)

    def test_a_clean_pod_passes(self):
        self.assertEqual(self._check(), [], "control: the seeded pod must be clean")

    def test_done_without_evidence_fails(self):
        self.conn.execute("UPDATE tasks SET status='DONE', evidence='' WHERE id=1")
        self.conn.commit()
        self.assertTrue(any("no evidence" in v for v in self._check()))

    def test_a_ruling_without_a_rationale_fails(self):
        self.conn.execute("INSERT INTO decisions (decided_on, topic, ruling, rationale) "
                          "VALUES ('2026-09-09','t','r','')")
        self.conn.commit()
        self.assertTrue(any("no rationale" in v for v in self._check()))

    def test_a_canon_fact_the_prompt_references_but_the_db_lacks_fails(self):
        self.conn.execute("DELETE FROM facts WHERE key=?", (hp.CANON_FACT_KEYS[0],))
        self.conn.commit()
        self.assertTrue(any(hp.CANON_FACT_KEYS[0] in v for v in self._check()))

    def test_a_pinned_but_superseded_ruling_fails(self):
        self.conn.execute("UPDATE decisions SET pinned=1, superseded_by=99 WHERE id=1")
        self.conn.commit()
        self.assertTrue(any("pinned AND superseded" in v for v in self._check()))

    def test_standing_orders_are_required_once_the_log_outgrows_the_window(self):
        for i in range(hp.DECISIONS_WINDOW + 2):
            self.conn.execute("INSERT INTO decisions (decided_on, topic, ruling, rationale) "
                              f"VALUES ('2026-09-09','filler {i}','r','why')")
        self.conn.commit()
        self.assertTrue(any("pinned standing orders" in v for v in self._check()),
                        "rulings can age out of the prompt with nothing pinned")

    def test_a_queue_nobody_has_touched_is_reported(self):
        """2026-09-10: a full day of shipped work, zero task rows created or moved."""
        from domains.panopticon.verify import invariants
        vs = invariants.check(self.conn, today=date(2026, 9, 20))
        self.assertTrue(any("untouched" in v for v in vs))
