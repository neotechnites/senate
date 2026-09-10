"""The Steward Domain Head's system prompt — BUILT FROM THE POD DB, never typed.

If a number appears in this prompt it was read out of steward.db this boot.  A head
that reasons from memory instead of from the DB is the failure this file exists to
prevent (Senate mistake #2, goal_progress_self_marked).
"""
from __future__ import annotations

import json
import sqlite3
from datetime import date
from typing import List

import sys
from pathlib import Path

POD_DIR = Path(__file__).resolve().parents[1]
if str(POD_DIR.parents[1]) not in sys.path:
    sys.path.insert(0, str(POD_DIR.parents[1]))

from domains.steward.verify import attention, recurrence  # noqa: E402

CANON_MAX_LINES = 40


def _canon_block(conn: sqlite3.Connection) -> str:
    rows = conn.execute(
        "SELECT key, value, authorized FROM facts ORDER BY key"
    ).fetchall()
    if not rows:
        return "  (NO CANON. This pod has no Ryan rulings. Do not act; ask him.)"
    out = []
    for r in rows:
        val = json.loads(r["value"])
        head = (val.get("rule") or val.get("goal") or val.get("interface")
                or val.get("store") or val.get("oracle") or val.get("forbidden_host")
                or next((str(v) for v in val.values() if isinstance(v, str) and v), ""))
        out.append(f'  - {r["key"]}: {head}')
        if r["authorized"]:
            quote = r["authorized"]
            if len(quote) > 300:
                quote = quote[:297] + "..."
            out.append(f'    RYAN VERBATIM: "{quote}"')
        else:
            out.append("    [NOT RYAN-AUTHORIZED -- does not steer]")
    return "\n".join(out)


def _backlog_block(conn: sqlite3.Connection) -> str:
    rows = conn.execute(
        "SELECT * FROM obligations WHERE status='OPEN' ORDER BY next_due_at"
    ).fetchall()
    if not rows:
        return ("  (EMPTY. Nothing is in the backlog yet. The first job is to get it "
                "out of Ryan's head and into this table -- he ruled he expects to type "
                "it in. Until it is populated this pod does nothing for him.)")
    buckets = {recurrence.OVERDUE: [], recurrence.DUE_SOON: [],
               recurrence.FUTURE: [], recurrence.UNSCHEDULED: []}
    for r in rows:
        state, days = recurrence.due_state(r["next_due_at"] or "")
        src = "measured" if r["interval_source"] else "SELF-MARKED"
        when = f"{days:+d}d" if days is not None else "no date"
        buckets[state].append(
            f'  [{r["id"]}] {r["title"]} ({r["kind"]}/{r["domain"]}) {when}'
            + (f' | every {r["interval_days"]}d [{src}]' if r["interval_days"] else "")
            + (f' | BLOCKED: {r["blocked_on"]}' if r["blocked_on"] else "")
        )
    out = []
    for label in (recurrence.OVERDUE, recurrence.DUE_SOON, recurrence.FUTURE,
                  recurrence.UNSCHEDULED):
        if buckets[label]:
            out.append(f"  == {label} ({len(buckets[label])}) ==")
            out.extend(buckets[label][:15])
            if len(buckets[label]) > 15:
                out.append(f"  ... and {len(buckets[label]) - 15} more")
    return "\n".join(out)


def _conversation_block(conn: sqlite3.Connection) -> str:
    rows = conn.execute(
        "SELECT at, direction, text FROM conversation ORDER BY at DESC LIMIT 8"
    ).fetchall()
    if not rows:
        return "  (Never spoken to Ryan. No message has ever reached his phone.)"
    out = []
    for r in reversed(rows):
        who = "MANAGER" if r["direction"] == "TO_RYAN" else "RYAN"
        txt = r["text"][:200]
        out.append(f'  {str(r["at"])[:16]} {who}: {txt}')
    return "\n".join(out)


def _attention_block(conn: sqlite3.Connection) -> str:
    allowed, reason = attention.may_speak_at_all(conn)
    woke = conn.execute("SELECT COUNT(*) c FROM wake_log").fetchone()["c"]
    spoke = conn.execute("SELECT COUNT(*) c FROM wake_log WHERE spoke=1").fetchone()["c"]
    verdict = "MAY SPEAK" if allowed else "MUST STAY SILENT"
    line1 = f"  {verdict} -- {reason}"
    if not woke:
        return line1 + "\n  Wakes logged: 0 (this manager has never run)"
    rate = 100.0 * spoke / woke
    return (line1 + f"\n  Wakes logged: {woke} | spoke on {spoke} of them "
                    f"({rate:.0f}% talk rate)")


def _completion_block(conn: sqlite3.Connection) -> str:
    n = conn.execute("SELECT COUNT(*) c FROM completions").fetchone()["c"]
    closed = conn.execute(
        "SELECT COUNT(*) c FROM obligations WHERE status='CLOSED'").fetchone()["c"]
    if n == 0:
        return ("  ZERO completions recorded. Nothing has been closed. Any claim of "
                "progress from this pod is SELF-MARKED and must be reported as such.")
    last = conn.execute(
        "SELECT o.title, c.completed_on, c.verbatim FROM completions c "
        "JOIN obligations o ON o.id=c.obligation_id "
        "ORDER BY c.completed_on DESC LIMIT 3").fetchall()
    out = [f"  {n} completions reported by Ryan | {closed} obligations CLOSED"]
    for r in last:
        out.append(f'    {r["completed_on"]} {r["title"]}'
                   + (f' -- "{r["verbatim"][:80]}"' if r["verbatim"] else ""))
    return "\n".join(out)


def canon_line_count(prompt: str) -> int:
    return sum(1 for ln in prompt.splitlines() if ln.strip().startswith("- steward."))


def build_head_prompt(conn: sqlite3.Connection) -> str:
    return f"""You are the STEWARD DOMAIN HEAD — Ryan's manager for everything that keeps
his life from falling apart: the house, the vehicles, recurring maintenance, events.
Built {date.today().isoformat()} from steward.db, not from memory.

YOUR OUTPUT IS OBLIGATIONS CLOSED AND RYAN-HOURS SAVED. Never artifacts. A clean
schema over a rotting backlog is total failure. If nothing on the list moved this
month, say so plainly.

RYAN'S CANON (verbatim; only he ratifies — you may propose, never ratify):
{_canon_block(conn)}

THE BACKLOG (read from obligations this boot):
{_backlog_block(conn)}

COMPLETIONS — THE ONLY RECEIPT THAT EXISTS:
{_completion_block(conn)}

THE CONVERSATION SO FAR (last 8 lines):
{_conversation_block(conn)}

INTERRUPTION BUDGET (verify/attention.py enforces the floor; judgement is yours):
{_attention_block(conn)}

HOW YOU BEHAVE:
1. You are a MANAGER IN A CONVERSATION, not a reminder feed. Ryan ruled: "if i wanted
   daily reminders i would use daily reminders." Sometimes you give him a heads-up the
   night before. Sometimes you ask how the thing he started went. Sometimes you say
   nothing for two days. Vary what you say and when — varying the form of a repeated
   message is the one intervention measured to slow habituation.
2. SILENCE IS A DECISION. On every wake you may choose not to speak, and that choice is
   logged with its rationale in wake_log. A manager who speaks on every wake is an
   alarm clock, and alarm clocks get muted.
3. ONLY RYAN CLOSES AN OBLIGATION. You never mark work done. You never infer completion
   from silence, from a calendar, or from your own suggestion. He said: "im not going
   to lie to it." Believe him, and record his words in completions.verbatim.
4. NEVER MAKE HIM MAINTAIN A LIST. He does not open this pod to file tasks. He talks to
   you; you file. Drive whatever tools you need — invisibly.
5. DO THE LEGWORK YOURSELF FIRST. Find the part, get the quote, read the manual, call
   the vendor. Interrupt him only for the fraction that genuinely needs his hands or
   his decision. Every question you could have answered yourself is a Ryan-hour wasted,
   which is the opposite of your purpose.
6. AN INTERVAL WITHOUT A CITATION IS SELF-MARKED. obligations.interval_source holds a
   URL or it holds nothing. Store the number and the citation, never copyrighted prose.
   Seven common household tasks (gutters, caulking, roof, sump pump, generator, dryer
   vent, garage door) have NO authoritative interval anywhere — for those, Ryan's
   judgement is the source and you say so.
7. NAME EVERY NUMBER'S PROVENANCE: measured (a receipt, a citation, a completion row),
   modelled (you computed it — give the basis), self-marked (someone typed it with no
   backing). A self-marked number is never reported as progress.
8. A QUESTION FROM RYAN BEGETS AN ANSWER AND NOTHING ELSE. Answer it, then stop.
9. Be brief. Unread output is wasted.

CURRENT STATE OF THE BUILD: the conversation channel (Telegram) is NOT yet wired, and
the host is NOT yet provisioned. Until a real message reaches Ryan's actual phone and
his reply lands in `conversation`, this pod has produced nothing. That round trip is
the first receipt — everything before it is scaffolding.
"""
