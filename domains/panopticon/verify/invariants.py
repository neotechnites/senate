"""Pod invariants — the rules that must FAIL, not merely be stated in a prompt.

WHY THIS FILE HAS TEETH NOW.  It used to be a stub that returned "no violations" for any
input.  A check that cannot fail is worse than no check: the head ran it, saw a pass, and
believed something had been verified.  That is the same class of mistake recorded in
`panopticon.engineering.verification_traps` ("a verification method is not trusted until
it has been shown to FAIL on a deliberately broken input").

Every rule below traces to a ruling in `decisions` or a fact in `facts`.  Nothing here is
invented: if Ryan never said it, it is not enforced.
"""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional, Tuple


def check(conn, today: Optional[date] = None) -> List[str]:
    """Return a list of violation strings. Empty list = the pod is honest right now."""
    from domains.panopticon.interface import head_prompt as hp
    from domains.panopticon.verify import queue

    today = today or date.today()
    v: List[str] = []

    # -- Decision 2 / the head prompt's STANDING ORDERS mechanism ---------------------
    # 46 rulings, 8 rendered by recency, so standing orders aged out and Ryan re-issued
    # them.  If the pin count collapses, that regression is back and nothing else here
    # would notice.
    pinned = conn.execute(
        "SELECT count(*) n FROM decisions WHERE pinned=1 AND superseded_by IS NULL"
    ).fetchone()["n"]
    live = conn.execute(
        "SELECT count(*) n FROM decisions WHERE superseded_by IS NULL").fetchone()["n"]
    # Only bites once the log outgrows the recency window.  A young pod whose every
    # ruling still renders has no aging-out problem to solve.
    if live > hp.DECISIONS_WINDOW and pinned < hp.PINNED_MIN:
        v.append(f"only {pinned} live pinned standing orders (min {hp.PINNED_MIN}) — "
                 "rulings Ryan gave once are aging out of the boot prompt again")

    bad_pin = conn.execute(
        "SELECT id, topic FROM decisions WHERE pinned=1 AND superseded_by IS NOT NULL"
    ).fetchall()
    for r in bad_pin:
        v.append(f"decision {r['id']} ({r['topic']}) is pinned AND superseded — "
                 "a withdrawn ruling must not be a standing order")

    # -- Decision 5 / "DONE MEANS A BUILD THAT RAN" -----------------------------------
    n = conn.execute("SELECT count(*) n FROM tasks WHERE status='DONE' "
                     "AND trim(evidence)=''").fetchone()["n"]
    if n:
        v.append(f"{n} task(s) marked DONE with no evidence — done means something ran")

    # -- Every ruling carries its reason, or February-Ryan re-litigates it ------------
    n = conn.execute("SELECT count(*) n FROM decisions WHERE trim(rationale)=''").fetchone()["n"]
    if n:
        v.append(f"{n} decision(s) recorded with no rationale")

    # -- The prompt must not print MISSING at Ryan ------------------------------------
    for key in list(hp.CANON_FACT_KEYS) + list(hp.OPEN_QUESTION_KEYS) + [
            "panopticon.engineering.verification_traps"]:
        if conn.execute("SELECT 1 FROM facts WHERE key=?", (key,)).fetchone() is None:
            v.append(f"boot prompt references fact {key}, which is not in the DB")

    # -- Decision 2 / Ryan: "constantly evaluating what needs to get done" -------------
    # Work that never became a task row is invisible to the next session.
    last = queue.last_movement(conn)
    if last:
        try:
            days = (today - date.fromisoformat(last)).days
        except ValueError:
            days = 0
        if days >= 2:
            v.append(f"work queue untouched for {days}d (last movement {last}) — either "
                     "nothing is happening or work is happening off the queue")

    # -- Decision 2 again: an idle head with open work is an escalation ----------------
    if queue.head_is_idle(conn):
        v.append("no REMOTE task the head can start while non-EXTERNAL work is open — "
                 "planning failure, not a rest")

    return v


def validate_domain_proposal(proposal: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate a proposal against Panopticon domain invariants.

    UNIMPLEMENTED SCAFFOLD, kept only because domain_builder generates it.  No pod code
    calls it and no rule has ever been written into it, so its clean return is an absence
    of checks rather than a verification.  The real gate is check() above; use that.
    """
    return True, []
