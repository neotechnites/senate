"""Canon for the Steward pod — Ryan's rulings, re-asserted on every boot.

Every row below carries `authorized`: Ryan's VERBATIM words from the session dated in
`ratified_on`.  A fact with an empty `authorized` field did not come from Ryan and does
not steer this pod (Senate mistake #9, capital_limits_inferred_from_non_ryan_text: a
session once inferred a limit from non-Ryan text and it became binding).  If you are a
future Domain Head reading this: you may PROPOSE canon, you may not ratify it.
"""
from __future__ import annotations

import json
import sqlite3

RYAN_2026_09_09 = "2026-09-09"

CANON = [
    {
        "key": "steward.purpose",
        "value": {
            "goal": "Ryan's obligation backlog gets CLOSED.",
            "output": "obligations closed and Ryan-hours saved, never artifacts",
            "anti_goal": "a clean schema over a rotting backlog",
        },
        "authorized": ("i have a laundry list, a huge one, of tasks i need to complete "
                       "to keep my life from falling apart, and i do a terrible job of "
                       "them. this domains goal will be to manage all of those things, "
                       "and serve as a manager to get me to do that ones it cant do "
                       "itself."),
        "source": "ryan_session_2026-09-09",
    },
    {
        "key": "steward.interface.conversation_not_digest",
        "value": {
            "interface": "one persistent conversation",
            "forbidden": "scheduled digest, daily reminder feed, per-task alarm",
            "silence_is_valid": True,
        },
        "authorized": ("no, not a daily digest, its an open conversation with my "
                       "manager, sometimes they tell me what i need to do, give me a "
                       "heads up the night before, tell me what else needs to get done "
                       "etc. if i wanted daily reminders i would use daily reminders."),
        "source": "ryan_session_2026-09-09",
    },
    {
        "key": "steward.store.pod_owns_the_list",
        "value": {
            "store": "this pod's SQLite, sovereign",
            "forbidden": "making Ryan maintain a list in a third-party app",
            "tools": "the manager may drive any tool it likes, invisibly",
        },
        "authorized": ("and no, im not putting the list in jack shit, im talking to an "
                       "ai that can use whatever tools it wants to. that is the entire "
                       "whole point of this"),
        "source": "ryan_session_2026-09-09",
    },
    {
        "key": "steward.oracle.ryan_reports_completion",
        "value": {
            "oracle": "Ryan",
            "rule": "an obligation advances ONLY on a completion Ryan reported",
            "no_receipt_apparatus": True,
        },
        "authorized": ("youre right it needs to prove the stuff it does, but only i "
                       "need to tell it when ive done somehting. im not going to lie "
                       "to it."),
        "source": "ryan_session_2026-09-09",
    },
    {
        "key": "steward.tone.annoying_within_limits",
        "value": {
            "rule": "persistent enough to move him, never enough to get muted",
            "measured_basis": ("Pop-Eleches 2011 AIDS 25(6) N=431: weekly SMS +13pp "
                               "adherence, daily SMS zero effect; Wohllebe 2021 "
                               "N=17,500: ~2.5pp abandonment per extra msg/week"),
            "enforced_by": "verify/attention.py",
        },
        "authorized": ("and it needs to be annoying enough to get me to do it, but not "
                       "so annoying i ignore it and never work with it again."),
        "source": "ryan_session_2026-09-09",
    },
    {
        "key": "steward.host.not_kalshis_vps",
        "value": {
            "forbidden_host": "the Kalshi VPS (129.146.115.241)",
            "intended_host": "a second Oracle Always Free instance, this pod's own",
            "status": "PENDING -- Ryan to confirm free-tier headroom in OCI console",
        },
        "authorized": ("it shoudl not be using the vps that kalshi does. thats kalshis. "
                       "... the answer is a vps only if i can create a second one in "
                       "oracle thats free and can support this"),
        "source": "ryan_session_2026-09-09",
    },
    {
        "key": "steward.seeding.ryan_types_it_in",
        "value": {
            "rule": "Ryan supplies the backlog; the manager transcribes and files it",
            "measured_basis": ("research 2026-09-09: no machine-readable dataset of "
                               "home or vehicle maintenance intervals exists on "
                               "GitHub, Kaggle, HuggingFace or data.gov; every "
                               "product in the category ships empty"),
        },
        "authorized": ("fine that i need to type everthing in, i expect to have to do "
                       "that."),
        "source": "ryan_session_2026-09-09",
    },
]


def seed(conn: sqlite3.Connection) -> int:
    """Re-assert canon.  Returns rows written.  Idempotent."""
    n = 0
    for row in CANON:
        conn.execute(
            "INSERT INTO facts (key, value, source, authorized, ratified_on, "
            "verified_by, is_immutable) VALUES (?,?,?,?,?,?,1) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value, "
            "authorized=excluded.authorized, ratified_on=excluded.ratified_on",
            (row["key"], json.dumps(row["value"]), row["source"],
             row["authorized"], RYAN_2026_09_09, "ryan_verbatim"),
        )
        n += 1
    return n
