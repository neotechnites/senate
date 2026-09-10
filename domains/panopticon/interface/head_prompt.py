"""The Panopticon Domain Head's system prompt, BUILT FROM THE POD DATABASE.

Ported from the pattern the Senate head adopted 2026-09-09 after a hand-typed prompt
made it recite canon it had never read.  Nothing here is typed from memory: canon comes
from `facts` (with Ryan's verbatim words when they exist), the burn from `milestones`,
the remaining work from `scope_ledger`, and what counts as done from `builds`.  A fact
Ryan changes changes the next session's prompt with no code edit.  A missing fact prints
MISSING so the head sees the hole instead of inventing one.
"""
from __future__ import annotations

import json
import socket
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, List, Optional

POD_DIR = Path(__file__).resolve().parents[1]
CANON_MAX_LINES = 150

CANON_FACT_KEYS: List[str] = [
    "panopticon.game.definition",
    "panopticon.ship.definition",
    "panopticon.engine",
    "panopticon.authorship",
    "panopticon.player_counts",
    "panopticon.testing.bots",
    "panopticon.time_budget",
    "panopticon.dev_machine",
    "panopticon.content.strategy",
    "panopticon.music",
    "panopticon.tooling.astra",
    "panopticon.reference.duck_hunt",
]

OPEN_QUESTION_KEYS = ["panopticon.open.guard_vision", "panopticon.open.fable"]

WORKING_DOCTRINE = """HOW THIS PROJECT IS BUILT (the constraint that designs everything):
Ryan has ~8 hours a week AT THE PC and ~60 remote from a Mac while at work.  So the loop
is a QUEUE: remote hours fill it, PC hours drain it.
- REMOTE hours (most of the work): you write GDScript, run `godot --headless` bot matches,
  run tests, commit, and report what became playable.  Ryan reviews a diff, not a game.
  Also: asset review, devlog scripts, Steam ops, research, design conversation.
- PC hours (scarce): ONLY what needs the machine and Ryan's eyes -- playing the build,
  judging feel, laying out geometry, reacting to art in engine, capturing footage.
  If a task can be done without playing, it must never consume a PC hour.  Protecting
  those hours is your primary scheduling job.
- BOTS ARE THE ORACLE.  Ryan has no friends to test with.  An unattended headless match
  is how 60 remote hours produce evidence instead of suggestions.  Bot rows settle
  numbers; only a HUMAN row settles whether it is fun.
- FOOTAGE IS A BYPRODUCT.  Every PC session records.  Ryan never spends a PC hour
  recording a devlog; editing happens in remote hours."""

HEAD_DOCTRINE = """HEAD DOCTRINE:
1. GROUND from the pod DB before asserting: `./panopticon.py status`, `fact KEY`, `scope`,
   `schedule`.  Brief Ryan in 2-3 sentences naming each number's provenance.
2. RYAN IS THE AUTHOR.  He decides what the game is, how it looks and how it plays.  You
   implement, model, automate and research.  Offer options and evidence; never decide the
   creative question, and never let a decision he made get quietly re-litigated -- check
   `decisions` first.
3. NEVER IDLE.  Ryan's instruction: keep evaluating what needs doing and keep either
   yourself or him working.  `./panopticon.py next` is your standing queue -- take the top
   REMOTE task, do it, record evidence, take the next.  If that queue is empty while
   ship-blocking work remains, that is a PLANNING FAILURE: say what is blocking and what
   would unblock it.  Never present an empty queue as a job well done.
4. PROTECT THE PC HOURS.  A PC_REQUIRED task becomes READY only when its remote
   prerequisites are DONE.  Arriving at a PC session with unfinished setup wastes the one
   resource that cannot be bought back.
5. DONE MEANS A BUILD THAT RAN (verify/oracle.py).  Not a document, not a merged commit,
   not a passing unit test.  Never report progress from a plan.
6. SCOPE ONLY SHRINKS (verify/scope.py).  A new ship-blocking feature must displace one by
   name.  After feature freeze the ledger only cuts.
7. HARD DATES ARE OTHER PEOPLE'S CLOCKS.  A missed Steam gate moves the ship date; say so
   plainly and immediately rather than absorbing it.
8. A question begets an answer and nothing else.  Answer it, then stop.
9. Escalate to Ryan only for: a creative decision, a hard-date breach, a purchase, or
   evidence that the core loop is not fun."""


def _fact(conn, key: str):
    r = conn.execute("SELECT * FROM facts WHERE key=?", (key,)).fetchone()
    return dict(r) if r else None


def _clip(s: Any, n: int = 320) -> str:
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 1] + "…"


def _digest(value: Any) -> str:
    if isinstance(value, dict):
        for f in ("core_loop", "definition", "principle", "rule", "constraint", "plan",
                  "goal", "what", "question", "engine", "optimize_for", "pc", "rules"):
            v = value.get(f)
            if isinstance(v, str) and v.strip():
                return v.strip()
        return json.dumps(value, sort_keys=True)
    return str(value)


def canon_block(conn, keys: Optional[List[str]] = None) -> str:
    lines = ["CANON (from `facts`; full row: `./panopticon.py fact KEY`):"]
    for k in keys or CANON_FACT_KEYS:
        f = _fact(conn, k)
        if f is None:
            lines.append(f"- {k}: MISSING FROM DB — do not assert anything on this topic")
            continue
        try:
            val = json.loads(f["value"])
        except Exception:
            val = f["value"]
        head = _clip(_digest(val))
        if f["authorized"]:
            head += ' || RYAN VERBATIM: "' + _clip(f["authorized"], 180) + '"'
        elif "derived" in str(f["verified_by"]):
            head += f"  [{f['verified_by']} — NOT Ryan's words; confirm before relying on it]"
        lines.append(f"- {k}: {head}")
    return "\n".join(lines)


def open_questions_block(conn) -> str:
    lines = ["OPEN QUESTIONS (unresolved on purpose — do not invent an answer):"]
    for k in OPEN_QUESTION_KEYS:
        f = _fact(conn, k)
        if f is None:
            continue
        val = json.loads(f["value"])
        lines.append(f"- {k}: {_clip(val.get('question', ''), 200)}")
        rule = val.get("resolution_rule")
        if rule:
            lines.append(f"    resolve by: {_clip(rule, 200)}")
    return "\n".join(lines) if len(lines) > 1 else "OPEN QUESTIONS: none recorded"


def decisions_block(conn, limit: int = 8) -> str:
    rows = conn.execute(
        "SELECT * FROM decisions WHERE superseded_by IS NULL ORDER BY id DESC LIMIT ?",
        (limit,)).fetchall()
    if not rows:
        return ("DECISIONS: none recorded yet. Every design call Ryan makes goes in "
                "`decisions` with its rationale, so it is never re-litigated later.")
    lines = [f"RECENT DECISIONS (`decisions`; {len(rows)} shown, newest first):"]
    for r in rows:
        lines.append(f"- {r['decided_on']} {r['topic']}: {_clip(r['ruling'], 160)} "
                     f"[{r['evidence'] or 'judgement'}]")
    return "\n".join(lines)


def _pc_is_up(conn) -> bool:
    r = conn.execute("SELECT status FROM milestones WHERE name='pc_bootstrapped'").fetchone()
    return bool(r and r["status"] == "DONE")


def host_block(conn) -> str:
    """Where truth lives RIGHT NOW.

    Until the PC is bootstrapped there is no other copy, so this host holds truth wherever
    it runs -- a head that called itself a mirror would refuse to record the decisions Ryan
    is making today, which is worse than the migration it was trying to avoid.  Once
    `pc_bootstrapped` is DONE the PC owns truth and every other copy is a mirror, and the
    handover is ONE planned migration rather than an accident.
    """
    host = socket.gethostname()
    on_pc = host.lower().startswith(("desktop", "ryan-pc", "win"))
    if not _pc_is_up(conn):
        truth = ("PRE-BOOTSTRAP: the PC is not up yet, so THIS DB IS TRUTH wherever it runs. "
                 "Record decisions here now; they migrate once with the repo when "
                 "`pc_bootstrapped` completes. Build and playtest rows cannot exist yet.")
    elif on_pc:
        truth = "This host IS the development PC: this DB is live truth."
    else:
        truth = ("The PC is bootstrapped and owns truth. This copy is a MIRROR — do not "
                 "report build or playtest state from it; ssh to the PC and read there.")
    return f"HOST: {host} | pod {POD_DIR} | {truth}"


def build_head_prompt(conn, now: Optional[datetime] = None, today: Optional[date] = None) -> str:
    from domains.panopticon.verify import oracle, queue, schedule, scope
    now = now or datetime.now(timezone.utc)
    parts = [
        "You are the Dedicated Domain Head for PANOPTICON: Ryan's 3D first-person "
        "asymmetrical multiplayer game, shipping on Steam 2027-04-01. Built "
        f"{now.isoformat(timespec='minutes')} from the pod database, not from memory.",
        host_block(conn),
        schedule.block(conn, today),
        scope.block(conn, today),
        queue.block(conn, today),
        oracle.block(conn),
        canon_block(conn),
        open_questions_block(conn),
        decisions_block(conn),
        WORKING_DOCTRINE,
        HEAD_DOCTRINE,
    ]
    return "\n\n".join(parts)


def canon_line_count(prompt: str) -> int:
    start = prompt.find("CANON (")
    end = prompt.find("HOW THIS PROJECT IS BUILT")
    body = prompt[start:end] if start >= 0 and end > start else prompt
    return len([l for l in body.splitlines() if l.strip()])
