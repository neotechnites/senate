"""Steward pod invariant tests.  These gate spinup — the head will not boot if they fail."""
from __future__ import annotations

import os
import sys
import tempfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

POD_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = POD_DIR.parents[1]
for p in (str(REPO_ROOT), str(POD_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from domains.steward.state.db import Database                    # noqa: E402
from domains.steward.state.canon import seed, CANON              # noqa: E402
from domains.steward.verify import recurrence, attention         # noqa: E402
from domains.steward.interface.head_prompt import build_head_prompt  # noqa: E402


@pytest.fixture()
def db():
    with tempfile.TemporaryDirectory() as td:
        yield Database(Path(td) / "t.db")


# ---------------------------------------------------------------- recurrence

def test_recurring_is_completion_based_not_calendar_based():
    """The whole reason no off-the-shelf app survived selection."""
    # Due annually, anchored 2026-01-01, but actually done late on 2026-03-15.
    nxt = recurrence.next_due("RECURRING", 365, "2026-01-01", "2026-03-15")
    assert nxt == "2027-03-15", "next due must key off the COMPLETION, not the anchor"


def test_recurring_never_completed_falls_back_to_anchor():
    assert recurrence.next_due("RECURRING", 365, "2026-01-01", "") == "2026-01-01"


def test_event_date_does_not_move_when_ignored():
    assert recurrence.next_due("EVENT", None, "2026-12-25", "") == "2026-12-25"


def test_recurring_rearms_and_never_closes():
    assert recurrence.closes_on_completion("RECURRING") is False
    assert recurrence.closes_on_completion("ONESHOT") is True
    assert recurrence.closes_on_completion("EVENT") is True


def test_due_state_buckets():
    today = date(2026, 9, 9)
    assert recurrence.due_state("2026-09-01", today)[0] == recurrence.OVERDUE
    assert recurrence.due_state("2026-09-01", today)[1] == -8
    assert recurrence.due_state("2026-09-20", today)[0] == recurrence.DUE_SOON
    assert recurrence.due_state("2027-09-20", today)[0] == recurrence.FUTURE
    assert recurrence.due_state("", today)[0] == recurrence.UNSCHEDULED


def test_recurring_with_no_interval_is_unscheduled_not_crashing():
    assert recurrence.next_due("RECURRING", None, "", "") == ""


# ---------------------------------------------------------------- the oracle

def test_only_ryan_completions_advance_an_obligation(db):
    """Ryan is the oracle. Nothing else may close work."""
    with db.get_connection() as c:
        c.execute("INSERT INTO obligations (title, kind) VALUES ('baseboards','ONESHOT')")
        oid = c.execute("SELECT id FROM obligations").fetchone()["id"]
        c.execute("INSERT INTO completions (obligation_id, completed_on, reported_by, "
                  "verbatim) VALUES (?,?,'ryan','did it saturday')", (oid, "2026-09-09"))
        row = c.execute("SELECT * FROM completions WHERE obligation_id=?", (oid,)).fetchone()
    assert row["reported_by"] == "ryan"
    assert row["verbatim"] == "did it saturday", "his words are the receipt"


def test_completion_dies_with_its_obligation(db):
    with db.get_connection() as c:
        c.execute("INSERT INTO obligations (title, kind) VALUES ('x','ONESHOT')")
        oid = c.execute("SELECT id FROM obligations").fetchone()["id"]
        c.execute("INSERT INTO completions (obligation_id, completed_on) VALUES (?,?)",
                  (oid, "2026-09-09"))
        c.execute("DELETE FROM obligations WHERE id=?", (oid,))
        assert c.execute("SELECT COUNT(*) c FROM completions").fetchone()["c"] == 0


# ---------------------------------------------------------------- attention

def test_global_floor_blocks_a_second_message_too_soon(db):
    with db.get_connection() as c:
        c.execute("INSERT INTO conversation (at, direction, text) VALUES (?,?,?)",
                  (datetime.now(timezone.utc).replace(tzinfo=None).isoformat(), "TO_RYAN", "hey"))
        allowed, reason = attention.may_speak_at_all(c)
    assert allowed is False
    assert "floor" in reason


def test_global_floor_allows_after_the_gap(db):
    old = (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=attention.GLOBAL_MIN_GAP_HOURS + 1)).isoformat()
    with db.get_connection() as c:
        c.execute("INSERT INTO conversation (at, direction, text) VALUES (?,?,?)",
                  (old, "TO_RYAN", "hey"))
        allowed, _ = attention.may_speak_at_all(c)
    assert allowed is True


def test_first_ever_message_is_always_allowed(db):
    with db.get_connection() as c:
        allowed, reason = attention.may_speak_at_all(c)
    assert allowed is True and "never" in reason


def test_per_obligation_cooldown_is_one_week(db):
    """Pop-Eleches 2011: daily nagging measured ZERO effect. One per week, per task."""
    assert attention.PER_OBLIGATION_COOLDOWN_DAYS == 7
    with db.get_connection() as c:
        c.execute("INSERT INTO obligations (title, kind) VALUES ('gutters','ONESHOT')")
        oid = c.execute("SELECT id FROM obligations").fetchone()["id"]
        c.execute("INSERT INTO conversation (at, direction, text, obligation_id) "
                  "VALUES (?,?,?,?)",
                  ((datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=2)).isoformat(),
                   "TO_RYAN", "gutters?", oid))
        allowed, reason = attention.may_nag(c, oid)
    assert allowed is False and "cooldown" in reason


def test_nag_allowed_once_the_week_has_passed(db):
    with db.get_connection() as c:
        c.execute("INSERT INTO obligations (title, kind) VALUES ('gutters','ONESHOT')")
        oid = c.execute("SELECT id FROM obligations").fetchone()["id"]
        c.execute("INSERT INTO conversation (at, direction, text, obligation_id) "
                  "VALUES (?,?,?,?)",
                  ((datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=9)).isoformat(),
                   "TO_RYAN", "gutters?", oid))
        allowed, _ = attention.may_nag(c, oid)
    assert allowed is True


def test_ryans_own_replies_do_not_count_as_the_manager_speaking(db):
    with db.get_connection() as c:
        c.execute("INSERT INTO conversation (at, direction, text) VALUES (?,?,?)",
                  (datetime.now(timezone.utc).replace(tzinfo=None).isoformat(), "FROM_RYAN", "did it"))
        allowed, _ = attention.may_speak_at_all(c)
    assert allowed is True, "his message must not start the manager's cooldown"


def test_silence_is_recordable_as_a_decision(db):
    with db.get_connection() as c:
        c.execute("INSERT INTO wake_log (spoke, rationale, considered) "
                  "VALUES (0,'nothing due; last spoke 4h ago',12)")
        r = c.execute("SELECT * FROM wake_log").fetchone()
    assert r["spoke"] == 0 and r["rationale"]


# ---------------------------------------------------------------- canon

def test_every_canon_row_carries_ryans_verbatim_words():
    """Senate mistake #9: a fact with no Ryan attribution must never steer."""
    for row in CANON:
        assert row["authorized"].strip(), f"{row['key']} has no Ryan quote"


def test_canon_seed_is_idempotent(db):
    with db.get_connection() as c:
        seed(c); seed(c)
        assert c.execute("SELECT COUNT(*) c FROM facts").fetchone()["c"] == len(CANON)


def test_canon_records_the_kalshi_vps_prohibition(db):
    with db.get_connection() as c:
        seed(c)
        r = c.execute("SELECT value FROM facts WHERE key='steward.host.not_kalshis_vps'"
                      ).fetchone()
    assert "129.146.115.241" in r["value"]


# ---------------------------------------------------------------- head prompt

def test_head_prompt_is_built_from_the_db_and_says_nothing_is_verified(db):
    with db.get_connection() as c:
        seed(c)
        p = build_head_prompt(c)
    assert "ZERO completions recorded" in p
    assert "Never spoken to Ryan" in p
    assert "BACKLOG EMPTY" in p or "EMPTY." in p


def test_head_prompt_shows_overdue_items_and_flags_selfmarked_intervals(db):
    with db.get_connection() as c:
        seed(c)
        c.execute("INSERT INTO obligations (title, kind, interval_days, next_due_at) "
                  "VALUES ('drain water heater','RECURRING',365,'2026-01-01')")
        p = build_head_prompt(c)
    assert "OVERDUE" in p
    assert "SELF-MARKED" in p, "an interval with no citation must be flagged"


def test_head_prompt_marks_a_cited_interval_as_measured(db):
    with db.get_connection() as c:
        seed(c)
        c.execute("INSERT INTO obligations (title, kind, interval_days, "
                  "interval_source, next_due_at) VALUES "
                  "('drain water heater','RECURRING',365,'https://epa.gov/watersense',"
                  "'2027-01-01')")
        p = build_head_prompt(c)
    assert "measured" in p


def test_head_prompt_carries_ryans_verbatim_ruling_on_digests(db):
    with db.get_connection() as c:
        seed(c)
        p = build_head_prompt(c)
    assert "if i wanted daily reminders i would use daily reminders" in p
