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

# Dropped 2026-09-10 to pay for the STANDING ORDERS block without growing the prompt:
#   panopticon.time_budget   -- the schedule block and WORKING_DOCTRINE both state it
#   panopticon.dev_machine   -- OVERRIDDEN by decision 26; host_block now carries the truth
#   panopticon.tooling.astra -- not purchased; it is a RYAN_DECISION row in the queue
#   panopticon.content.strategy -- decision 41 defers all content/publishing work, and
#                               the devlog dates are already in the schedule block
#   panopticon.repo.location -- pinned decision 24 states the path, the remote and the
#                               never-use-gh rule in one line
# Added: panopticon.no_idle_time (the hard design constraint the ghost mechanic exists to
# serve) and panopticon.engineering.craft (what "do it right" actually means).
CANON_FACT_KEYS: List[str] = [
    "panopticon.game.definition",
    "panopticon.ship.definition",
    "panopticon.engine",
    "panopticon.authorship",
    "panopticon.player_counts",
    "panopticon.no_idle_time",
    "panopticon.testing.bots",
    "panopticon.engineering.craft",
    "panopticon.music",
    "panopticon.reference.duck_hunt",
]

# Rulings that must appear in EVERY boot prompt regardless of age.  Marked in the DB
# (decisions.pinned) rather than listed here, so Ryan's next standing order needs a
# `./panopticon.py decide --pin`, not a code edit.
PINNED_MIN = 8
DECISIONS_WINDOW = 6   # how many rulings the recency block renders

OPEN_QUESTION_KEYS = ["panopticon.open.guard_vision", "panopticon.open.fable"]

WORKING_DOCTRINE = """HOW THIS PROJECT IS BUILT (the constraint that designs everything):
~8 hours a week AT THE PC, ~60 remote from a Mac at work.  Remote hours FILL the queue,
PC hours DRAIN it.
- REMOTE (most of the work): GDScript, headless runs, tests, commits, asset review,
  research.  Ryan reviews a diff, not a game.
- PC (scarce): only what needs the machine and Ryan's eyes -- playing, judging feel,
  laying out geometry, reacting to art.  Anything doable without playing must never
  consume a PC hour.  Protecting those hours is your primary scheduling job.
- BOTS FILL THE SEATS RYAN HAS NO FRIENDS FOR.  They are opponents, not an oracle.
  Decision 36: the head does not run balance sweeps and does not report findings about
  whether a mechanic "works".  Ryan settles that by PLAYING it.
- FOOTAGE IS A BYPRODUCT.  Every PC session records; editing happens in remote hours."""

HEAD_DOCTRINE = """HEAD DOCTRINE:
1. GROUND from the pod DB before asserting: `./panopticon.py status`, `fact KEY`,
   `decisions`, `scope`, `schedule`.  Name each number's provenance.
2. RYAN IS THE AUTHOR.  He decides what the game is, how it looks and how it plays.  You
   implement, model, automate, research.  Never decide a creative question, never argue
   your own idea into canon, and never re-litigate a ruling -- read `decisions` first.
3. SPEND LIKE IT COSTS.  A small change must be SMALL IN COST, not reassigned to you
   (decisions 43, 45).  Brief an agent in a few lines: name the files, name the change,
   ONE verification command, a word cap on the report.  No consistency sweeps, no
   proving-the-proof, no re-briefing what the agent can read from disk.  Mechanical edits
   go to a CHEAP model.  If a two-line edit is costing five figures of tokens, stop.
4. THE QUEUE IS THE WORK.  Every unit of work is a `tasks` row before it starts and ends
   with `task-done --evidence`.  Work done outside the queue is invisible to the next
   session and did not happen.  `./panopticon.py next` is the standing list; an empty
   REMOTE queue with ship-blocking work open is a PLANNING FAILURE to escalate, never a
   rest.  Take the top REMOTE task THAT SERVES THE CURRENT OBJECTIVE (decision 41) -- a
   queue row older than the objective does not outrank it.
5. PROTECT THE PC HOURS.  A PC_REQUIRED task is READY only when its remote prerequisites
   are DONE.  Never surface a per-task hour estimate (decision 22).
6. DONE MEANS A BUILD THAT RAN.  Not a document, not a commit, not a passing unit test.
7. SCOPE ONLY SHRINKS.  A new ship-blocking feature displaces one by name.
8. HARD DATES ARE OTHER PEOPLE'S CLOCKS.  Say a breach plainly and immediately.
9. A question begets an answer and nothing else.  Answer it, then stop.
10. Escalate only for: a creative decision, a hard-date breach, a purchase, or evidence
   the core loop is not fun."""


def _fact(conn, key: str):
    r = conn.execute("SELECT * FROM facts WHERE key=?", (key,)).fetchone()
    return dict(r) if r else None


def _clip(s: Any, n: int = 260) -> str:
    """Clip to a SENTENCE where one ends in range, otherwise to a word.

    A ruling cut mid-word ("no isolated-copy re-verification, no '…") costs the same
    tokens as a whole sentence and carries less, which is the worst trade in the prompt.
    """
    s = " ".join(str(s).split())
    if len(s) <= n:
        return s
    head = s[:n]
    cut = max(head.rfind(". "), head.rfind(".\n"))
    if cut >= int(n * 0.55):
        return head[: cut + 1]
    cut = head.rfind(" ")
    return (head[:cut] if cut > 0 else head) + "…"


def _norm(s: str) -> str:
    return "".join(c for c in str(s).lower() if c.isalnum())


def _echoes(digest: str, verbatim: str) -> bool:
    """True when the head's summary is a restatement of Ryan's own sentence.

    Word overlap rather than substring: the paraphrases differ by a word or two ("do it
    right" vs "do this right") while carrying nothing new, and a substring test misses
    every one of them.
    """
    dw = {w for w in (_norm(x) for x in digest.split()) if len(w) > 3}
    vw = {w for w in (_norm(x) for x in verbatim.split()) if len(w) > 3}
    if len(dw) < 4 or not vw:
        return False
    return len(dw & vw) / len(dw) >= 0.7


def _digest(value: Any) -> str:
    if isinstance(value, dict):
        # Ordered by how much of the fact the field carries.  Before 2026-09-10 this list
        # missed RULE/CORRECTION/FORMAT/purpose, so four of the twelve canon entries fell
        # through to json.dumps and rendered ~400 characters of escaped JSON each — the
        # single largest block of unreadable text in the prompt.
        picked = []
        for f in ("RULE", "CORRECTION", "core_loop", "definition", "principle", "rule",
                  "FORMAT", "constraint", "purpose", "plan", "goal", "what", "IS",
                  "question", "engine", "optimize_for", "support_up_to", "pc", "rules",
                  "strength"):
            v = value.get(f)
            if isinstance(v, str) and v.strip():
                picked.append(v.strip())
                # A one-clause field on its own can misrepresent the fact.
                # panopticon.player_counts rendered as "1v1 through 1v3" (optimize_for)
                # while the scope ledger said "1v1 to 1v7", and the prompt read as a
                # contradiction; the missing half was in the very next field.
                if len(" / ".join(picked)) >= 70 or len(picked) == 2:
                    break
        if picked:
            return " / ".join(picked)
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
            # Where the digest is just a tidied-up copy of Ryan's own sentence, print HIS
            # words and drop the paraphrase.  Printing both doubled the cost of several
            # canon entries to say the same thing twice.
            if _echoes(head, f["authorized"]):
                head = 'RYAN: "' + _clip(f["authorized"], 200) + '"'
            else:
                head += ' || RYAN: "' + _clip(f["authorized"], 130) + '"'
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


def standing_orders_block(conn) -> str:
    """The rulings a fresh head must never rediscover the hard way.

    WHY THIS EXISTS.  `decisions` held 46 rulings and the prompt rendered the 8 newest.
    Everything older fell off the edge, so Ryan kept re-issuing orders he had already
    given -- bots are not an oracle, never use the gh CLI, never estimate hours, do not
    kill a process you did not start.  Recency is the wrong filter for a standing order,
    so these are marked `pinned` in the DB and are ALWAYS rendered, in full sentences,
    ahead of the recency window.
    """
    rows = conn.execute(
        "SELECT * FROM decisions WHERE pinned=1 AND superseded_by IS NULL ORDER BY id"
    ).fetchall()
    if not rows:
        live = conn.execute(
            "SELECT count(*) n FROM decisions WHERE superseded_by IS NULL").fetchone()["n"]
        if live > DECISIONS_WINDOW:
            return (f"STANDING ORDERS: NONE PINNED, and {live} live rulings do not fit the "
                    f"{DECISIONS_WINDOW}-row recency window — orders Ryan gave once are "
                    "invisible to you. This is a DEFECT: `./panopticon.py check` fails.")
        return ("STANDING ORDERS: none pinned yet — every ruling still fits the recency "
                "block below. Pin one with `./panopticon.py decide ... --pin`.")
    lines = ["STANDING ORDERS (pinned in `decisions` — Ryan gave each of these once and "
             "should not have to again. Full text: `./panopticon.py decisions --pinned`):"]
    for r in rows:
        lines.append(f"- [{r['id']}] {r['topic']}: {_clip(r['ruling'], 170)}")
    return "\n".join(lines)


def verification_block(conn) -> str:
    """Three verification methods have silently passed code that should have failed.
    Each cost a session to rediscover, so the traps are rendered, not filed."""
    f = _fact(conn, "panopticon.engineering.verification_traps")
    if f is None:
        return ("VERIFICATION TRAPS: fact MISSING FROM DB — assume no check you run has "
                "been shown to have teeth.")
    v = json.loads(f["value"])
    lines = ["VERIFICATION TRAPS (`fact panopticon.engineering.verification_traps`):"]
    for k in ("broken_1", "broken_2", "broken_3"):
        if v.get(k):
            lines.append(f"- {_clip(v[k], 170)}")
    lines.append("- EMPTY OUTPUT IS NOT A PASS. A command that printed nothing has not "
                 "told you it succeeded; check the exit code and assert on real output.")
    if v.get("standing_rule"):
        lines.append(f"RULE: {_clip(v['standing_rule'], 170)}")
    return "\n".join(lines)


def decisions_block(conn, limit: int = DECISIONS_WINDOW) -> str:
    """The RECENCY window. Pinned rulings are excluded — they are already rendered above
    as STANDING ORDERS, and printing them twice buys nothing but tokens."""
    rows = conn.execute(
        "SELECT * FROM decisions WHERE superseded_by IS NULL AND COALESCE(pinned,0)=0 "
        "ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    if not rows:
        return ("DECISIONS: none recorded yet. Every design call Ryan makes goes in "
                "`decisions` with its rationale, so it is never re-litigated later.")
    total = conn.execute(
        "SELECT count(*) n FROM decisions WHERE superseded_by IS NULL").fetchone()["n"]
    lines = [f"RECENT DECISIONS ({len(rows)} of {total} live, newest first — the other "
             f"{total - len(rows)} are not optional: `./panopticon.py decisions`):"]
    for r in rows:
        lines.append(f"- [{r['id']}] {r['decided_on']} {r['topic']}: {_clip(r['ruling'], 160)}")
    return "\n".join(lines)


def _pc_is_up(conn) -> bool:
    r = conn.execute("SELECT status FROM milestones WHERE name='pc_bootstrapped'").fetchone()
    return bool(r and r["status"] == "DONE")


def host_block(conn) -> str:
    """Where truth lives RIGHT NOW.

    CORRECTED 2026-09-10.  This used to declare any non-PC host a MIRROR once
    `pc_bootstrapped` was DONE, which meant a head booting on the Mac -- where every
    session actually happens -- read "do not report state from this DB" as its second
    line.  Decision 26 reversed that on 2026-09-09: Ryan, verbatim, 'no we dont need to
    make that change, ill work with you here for now.'  The Mac is authoritative for the
    pod DB and both repos; the PC is a build, test and play target reached over Tailscale
    SSH.  One writable DB, no split brain.
    """
    host = socket.gethostname()
    on_pc = host.lower().startswith(("desktop", "ryan-pc", "win"))
    if not _pc_is_up(conn):
        truth = ("PRE-BOOTSTRAP: the PC is not up yet, so THIS DB IS TRUTH wherever it runs. "
                 "Record decisions here now. Build and playtest rows cannot exist yet.")
    elif on_pc:
        truth = ("You are ON THE PC, which is a BUILD/TEST/PLAY TARGET ONLY (decision 26). "
                 "The pod DB is authoritative on the MAC — no Domain Head state is written "
                 "here. Build, run and play; report back to the Mac.")
    else:
        truth = ("THIS MAC IS AUTHORITATIVE for the pod DB and both repos (decision 26). "
                 "The PC is a build, test and play target reached over Tailscale SSH. "
                 "Record everything here; there is no second writable copy.")
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
        standing_orders_block(conn),
        canon_block(conn),
        open_questions_block(conn),
        decisions_block(conn),
        verification_block(conn),
        WORKING_DOCTRINE,
        HEAD_DOCTRINE,
    ]
    return "\n\n".join(parts)


def canon_line_count(prompt: str) -> int:
    start = prompt.find("CANON (")
    end = prompt.find("OPEN QUESTIONS")
    body = prompt[start:end] if start >= 0 and end > start else prompt
    return len([l for l in body.splitlines() if l.strip()])
