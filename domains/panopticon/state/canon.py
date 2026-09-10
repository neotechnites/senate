"""Panopticon canon — seeded from what Ryan actually said, 2026-09-09.

RULE (inherited from the Senate mistakes ledger, self_awarded_ryan_authority):
a fact carries `authorized` ONLY when it reproduces Ryan's verbatim words, and
`verified_by='ryan'` only alongside a `ratified_on` date.  Anything a session
inferred is stamped `derived_from_ryan_brief` so the head can see the seam and
ask instead of assuming.  Two facts are deliberately OPEN questions: a hole that
announces itself is safer than a number nobody remembers inventing.
"""
from __future__ import annotations

import json
from datetime import date, timedelta

RATIFIED_ON = "2026-09-09"
SHIP_DATE = date(2027, 4, 1)

FACTS = [
    ("panopticon.game.definition", {
        "genre": "3D first-person asymmetrical multiplayer",
        "core_loop": "One player occupies the panopticon tower at the centre of the map. "
                     "The other players are prisoners in the ring around it, travelling "
                     "from a start position to an end position. The guard stops them by "
                     "shooting them.",
        "geometry": "Prisoners traverse what is nearly a 2D plane wrapped around a central "
                    "tower, so the guard holds 360-degree sightlines and the tension is "
                    "sightline denial rather than distance.",
        "reference": "Halo Reach custom gametype 'Duck Hunt' — see panopticon.reference.duck_hunt",
    }, "Ryan brief 2026-09-09",
     "Panopticon is a 3d first person asymetrical multiplayer game. One player sits in the "
     "panopticon in the middle of the map, the other players are in the \"prison\" around the "
     "panopticon, with a goal of going from a starting position to an end one, alsmost as if "
     "they were on a 2d plane. they get stopped by being shot by the player in the panopticon.",
     "ryan", 1),

    ("panopticon.reference.duck_hunt", {
        "source": "Halo Reach, Forge World custom gametype; researched 2026-09-09",
        "rules": "Ducks run a linear obstacle course; a hunter in an elevated nest with a "
                 "precision rifle shoots them. The hunter relocates to a higher nest as the "
                 "ducks clear each floor. Cover falls away and traps increase per level. "
                 "Ducks win by surviving the course; in some variants they then receive "
                 "weapons and extra health and turn on the hunter.",
        "balance_knob": "Duck starting HP is tuned against the hunter's weapon choice.",
        "lobby_size": "8-16 in the original",
        "variants": "Duck Duck Hunt — a shot duck becomes a hunter, so the round compounds.",
        "urls": "https://halocustoms.com/maps/duck-hunt.2330/ ; "
                "https://steamcommunity.com/sharedfiles/filedetails/?id=1081185139",
    }, "web research 2026-09-09", "Go do research about the duck hunt custom game mode in halo "
       "reach, that is the gameplay.", "ryan_directed_research", 1),

    ("panopticon.ship.definition", {
        "definition": "Purchasable on Steam as a real game by 2027-04-01. Not a demo, not a "
                      "vertical slice, not a devlog series — a paid store listing a stranger "
                      "can buy.",
        "ship_date": "2027-04-01",
        "platforms": "PC (Windows) required; Mac if it can be swung; no consoles.",
    }, "Ryan brief 2026-09-09",
     "It will be for pc, maybe mac if we can swing it, no consoles, and will be created in "
     "godot. purchasable on steam as a real game by apriol 1st.", "ryan", 1),

    ("panopticon.engine", {"engine": "Godot", "rule": "Godot is not a preference to revisit; "
     "it is canon. Its dedicated-server export and --headless mode are what make unattended "
     "bot testing possible, which the whole schedule depends on."},
     "Ryan brief 2026-09-09", "will be created in godot", "ryan", 1),

    ("panopticon.authorship", {
        "principle": "This is a game created by Ryan, the way any game of the last ten years "
                     "was created by its author. AI fills two named skill gaps (3D modeling, "
                     "and possibly not music at all) and compresses development time. It does "
                     "not replace the process and it never makes the creative decisions.",
        "ryan_does": "design, mechanics, feel, art direction, level layout, every decision",
        "ai_does": "GDScript implementation of specified mechanics, 3D modeling, tooling, "
                   "build and test automation, research, content production support",
        "ai_does_not": "decide what the game is, how it looks, or how it plays",
    }, "Ryan brief 2026-09-09",
     "This will be a game, created by me, just like any game from the last ten years. the "
     "individual peices will be ai aided. i am actually geniunely capabale of making this game "
     "from scratch all on my own, with the exception of being bad at music and having never "
     "done 3d modeling ... the ai serves to help fill minor gaps in my skills and to speed up "
     "the development procces, not to replace the prccess.", "ryan", 1),

    ("panopticon.player_counts", {
        "optimize_for": "1v1 through 1v3",
        "support_up_to": "1v7, and asymmetric variants such as 2v6",
        "consequence": "Netcode and ring layout are designed for small lobbies first; larger "
                       "counts must not be allowed to drive the core design.",
    }, "Ryan brief 2026-09-09",
     "for player count lets optimize for 1v1-3. but is see no reason to not allow up to 1v7, "
     "or even something like 2v6.", "ryan", 1),

    ("panopticon.testing.bots", {
        "constraint": "Ryan has no friends available to playtest. Bots are therefore not a "
                      "feature — they are the test harness and the balance oracle, and they "
                      "are required from early on.",
        "consequence": "Headless bot matches produce balance data unattended, at any hour, "
                       "without Ryan. His 8 weekly PC hours are then spent only on what a bot "
                       "cannot judge: whether the game feels good.",
        "rule": "No balance claim is valid without a playtests row. A bot row settles numbers; "
                "only a HUMAN row settles feel.",
    }, "Ryan brief 2026-09-09",
     "i wont have 1-3 friends to help test, so from early on we need bots", "ryan", 1),

    ("panopticon.time_budget", {
        "pc_hours_per_week": 8,
        "remote_hours_per_week": 60,
        "pc_location": "Ryan's PC at home, always on. Development happens there.",
        "remote_location": "MacBook, used from work, to drive the PC head remotely.",
        "scarcity_rule": "PC hours are the scarcest resource in the project. Any task that can "
                         "be completed without playing the game must never consume one.",
    }, "Ryan brief 2026-09-09",
     "for hours, maybe only like 8 at the actual pc, but can spend the other 60 remotely "
     "handling stuff from my mac in the background while im at work.", "ryan", 1),

    ("panopticon.tooling.astra", {
        "what": "GPT-6 Astra (OpenAI). Computer-use-first: it drives Blender through the same "
                "interface a person uses rather than emitting meshes from an API.",
        "why": "Ryan's stated reason: best at 3D modeling by a wide margin.",
        "consequence": "Astra's modeling work must run on the PC, where Blender lives. It is "
                       "not a Mac-side tool.",
        "status": "NOT YET PURCHASED — Ryan must buy access.",
        "cost_note": "Reported API rates ~$10/M input, ~$50/M output (2026-09-09 research). "
                     "This is a tooling cost, not a capital deployment.",
    }, "Ryan brief + web research 2026-09-09",
     "we need to leverage both astra and fable 5.1 for this to save the time ... i want it "
     "because its the best at 3d modeling and its not close.", "ryan", 0),

    ("panopticon.music", {
        "plan": "Ryan creates it, or commissions on Fiverr or similar.",
        "budget": "No budget line required.",
        "ai_role": "None assumed. Ryan named music as the gap AI probably does not fill.",
    }, "Ryan brief 2026-09-09",
     "music ill either create, or get someone on fiver or something like that, we dont need to "
     "budget for it.", "ryan", 1),

    ("panopticon.content.strategy", {
        "goal": "Build excitement before launch rather than shipping and hoping people find it.",
        "channels": "YouTube devlog roughly every two weeks; Twitter more frequent; TikTok and "
                    "Instagram shorts re-cut from the same footage.",
        "metric": "WISHLISTS are the launch metric, but followers are built BEFORE there is "
                  "anywhere to send them. Ryan ruled 2026-09-09 that audience-building does "
                  "not wait on the store page; a prior session had claimed a devlog without a "
                  "page was leaked value, which was inference, not evidence.",
        "production_rule": "Footage is a BYPRODUCT of playtests, captured automatically. Ryan "
                           "never spends PC hours 'recording a devlog'. Editing and posting "
                           "happen in remote hours.",
        "schedule_function": "The biweekly cadence doubles as a delivery gate: every two weeks "
                             "the project owes the public a visible increment.",
    }, "Ryan brief 2026-09-09",
     "i want to do content creation and devlogs to promote the game ... im trying to earn real "
     "money with this, even if it s an art project and i want it to actually be good (i beievle "
     "making it good is the best way to earn money)", "ryan", 1),

    ("panopticon.open.guard_vision", {
        "question": "Does the guard see all 360 degrees at once, or a limited arc they must "
                    "aim and rotate?",
        "status": "OPEN — deliberately unresolved.",
        "ryan_lean": "Likes 360 because that is a legitimate panopticon, but suspects it may "
                     "make the tower role impossibly hard, and that designing around it could "
                     "make the prisoner role unfun.",
        "resolution_rule": "Settled by playtest data, never by argument in chat. Requires bot "
                           "matches across both configurations plus one HUMAN feel session.",
    }, "Ryan brief 2026-09-09",
     "im not sure about gaurd vision, thats a game design question that cant be asnwered "
     "without further work.", "ryan", 1),

    ("panopticon.open.fable", {
        "question": "What is 'Fable 5.1' in this project and what should it do?",
        "status": "OPEN — Ryan named it as a tool to leverage; the pod has no definition for it.",
        "known": "A model alias named 'fable' is reachable as a subagent model from the Senate "
                 "head. Whether that is what Ryan means is UNVERIFIED.",
        "resolution_rule": "Ask Ryan. Do not infer a role for a tool nobody has defined.",
    }, "Ryan brief 2026-09-09", "", "derived_from_ryan_brief", 0),

    ("panopticon.dev_machine", {
        "pc": "Windows PC at home, always on, nothing installed as of 2026-09-09. This is where "
              "Godot, Blender, Astra and the Panopticon Domain Head all live.",
        "mac": "MacBook. A remote control surface only. No Godot work happens here.",
        "access": "Tailscale for always-on private reach; Windows OpenSSH so the Mac drops into "
                  "a shell; Claude Code native Windows install.",
        "rule": "The pod DB on the PC is truth. Any clone elsewhere is a MIRROR and must never "
                "be treated as live state.",
    }, "Ryan brief 2026-09-09",
     "nothign is installed on my pc right now ... i will develop on it, but i also need the "
     "ability toy work with the domain head on it remotely from my mac. the pc will always be on.",
     "ryan", 1),

    # ------------------------------------------------------------------ added 2026-09-10
    # These three were written into the live DB during working sessions and existed only
    # there, so a rebuilt pod came up without them.  A fresh head then booted missing the
    # hard design constraint the ghost mechanic exists to serve, the implementation
    # standard, and the three verification methods already proven to pass broken code.
    ('panopticon.no_idle_time', {
        'rule': 'NO IDLE TIME FOR ANY PLAYER INVOLVED. Not the shooter, not living '
                'prisoners, not ghosts.',
        'strength': 'HARD CONSTRAINT, and now a design DRIVER: the rest of the game is '
                    'balanced around the ghost mechanic, not the other way round.',
        'ryan_on_the_tradeoff': 'He acknowledges some games take sit-outs and that in '
                                'short rounds it is not a big deal. He is choosing not '
                                'to, on the grounds that a game without sit-outs leads '
                                'to more interesting and fun gameplay.'}, 'Ryan design conversation 2026-09-09',
     'the ghost mechanic needs further thinking through. but we need to balance the rest around '
     'it, i dont want idel time for any player involved. and yes, some games have sit outs, and '
     'especially for small rounds thats not a big deal, but if we can created a game without '
     'sitouts, that leads to more intersting and fun gameplay were going to do that',
     'ryan', 1),

    ('panopticon.engineering.craft', {
        'RULE': 'Do it right, do it properly, write good code. Look at how other games '
                'solve the problem. Keep the project clean.',
        'applies_to': 'IMPLEMENTATION craft. This does not conflict with '
                      'panopticon.method.first_principles, which governs whether a '
                      "DESIGN is good. Ryan's split: other games are never evidence "
                      'that a design is good, but they ARE the right source for how to '
                      'solve a problem you already have.',
        'standards': [       'Statically typed GDScript, no warnings.',
                             'No magic numbers. Tunables live in exported Resources so '
                             'variants can be swept headlessly.',
                             'Real .tscn scenes authored as scenes. Never build nodes '
                             'in code to dodge the editor.',
                             'Comments explain WHY, not what.',
                             'Clean node hierarchies, shared materials, clear naming. '
                             "A scene's structure is a communication to Ryan, who "
                             'opens it next.',
                             'Established algorithms implemented faithfully, not '
                             'approximated. Example: air-strafing is Quake/Source '
                             'PM_AirAccelerate, a specific documented formulation, not '
                             'a feel to guess at.',
                             'No dead code, no corner-cutting to finish faster.'],
        'enforcement': 'The head specs and verifies; subagents implement. A subagent '
                       'reporting success is not evidence — the head runs it headless '
                       'before anything is committed.'}, 'Ryan direction 2026-09-09',
     'do this right, do it properly, write good code. go look at other games, and how they do it, '
     'and keep this project clean',
     'ryan', 1),

    ('panopticon.engineering.verification_traps', {
        'why': 'Three separate verification methods have now been found to silently '
               'pass code that should fail. Each was believed to be working. Record '
               'them so they are not rediscovered.',
        'broken_1': 'ResourceLoader.load() returns a valid object for a script that '
                    'would fail with warnings-as-errors. Only GDScript.reload() '
                    'surfaces it. A check using load() alone tests nothing.',
        'broken_2': 'Copying the project without running `godot --headless --import` '
                    'in the copy leaves the global class_name cache unbuilt, so every '
                    'custom type reports as unknown and the audit floods with FALSE '
                    'failures. The head hit this and briefly reported 11 fake '
                    'failures.',
        'broken_3': 'Promoting warning levels via ProjectSettings.set_setting() at '
                    'RUNTIME is silently ignored - GDScript reads warning levels once '
                    "at engine init. The promotion must be written into the copy's "
                    'project.godot BEFORE the engine starts.',
        'correct_method': "Copy project to temp dir. Edit the COPY's project.godot to "
                          'set the three warning levels to =2. Run `godot --headless '
                          '--import` in the copy. Then load() AND reload() each .gd, '
                          'asserting OK. Validate the harness with a canary (a '
                          'deliberate untyped declaration) that MUST fail.',
        'standing_rule': 'A verification method is not trusted until it has been shown '
                         'to FAIL on a deliberately broken input. Every check the head '
                         'accepts must demonstrate its own teeth.'}, 'head + subagent findings 2026-09-09',
     'do this right, do it properly, write good code',
     'head', 1),

]


def _steam_calendar():
    """Milestones planned BACKWARD from the ship date, with their external clocks.

    Verified 2026-09-09: the Steam Direct fee is $100 per app and recoupable at $1,000
    revenue; there is a MANDATORY 30-day wait after paying it before release; the store
    page must be public at least 2 weeks pre-launch; store-page review and build review
    each run 3-5 business days.  Those are other people's clocks -- `hard=1` means no
    amount of effort moves the date.
    """
    ship = SHIP_DATE
    return [
        ("steam_fee_paid_and_app_created", date(2026, 10, 1), "STEAM", 1,
         "$100 Steam Direct fee. Starts the mandatory 30-day clock AND is the prerequisite "
         "for a store page. Latest possible date is 2027-03-02; doing it in month one instead "
         "buys ~5 months of wishlist accumulation for the same $100."),
        ("steam_store_page_public", date(2026, 10, 15), "STEAM", 1,
         "Wishlists cannot accumulate without a public page, and wishlists are the launch "
         "metric. Hard floor is 2 weeks pre-launch (2027-03-18); early is strictly better."),
        ("steam_tax_banking_identity_verified", date(2026, 10, 15), "STEAM", 1,
         "Tax documentation, banking details and identity verification. Blocks payout, not "
         "release, but it silently blocks release if left to the end."),
        ("steam_build_uploaded_and_reviewed", ship - timedelta(days=21), "STEAM", 1,
         "Build review runs 3-5 business days. Uploading 3 weeks out leaves room for one "
         "rejection and one fix."),
        ("steam_release_candidate", ship - timedelta(days=17), "BUILD", 0,
         "A build that launches, runs a full bot match, and is the thing shipped absent a "
         "blocking defect."),
        ("ship", ship, "STEAM", 1, "Purchasable on Steam."),
    ]


def _project_milestones():
    """Delivery gates derived from the brief. Dates are DERIVED, not Ryan's -- the head
    may move them; it may not move a hard=1 Steam row."""
    return [
        ("pc_bootstrapped", date(2026, 9, 16), "DECISION", 0,
         "Claude Code, Godot, Blender, git, Tailscale and OpenSSH installed on the PC; the pod "
         "cloned; the head reachable from the Mac. Costs Ryan PC hours, so it happens once."),
        ("bot_harness_runs_headless", date(2026, 9, 30), "BUILD", 0,
         "A scripted match with N bot prisoners and 1 bot guard runs to completion under "
         "`godot --headless` and writes a playtests row. THIS IS THE ORACLE and it is why it "
         "is dated before the game is fun: with no human testers, an unattended match is the "
         "only way 60 remote hours can produce evidence."),
        ("greybox_slice_playable", date(2026, 10, 21), "BUILD", 0,
         "One ring, one tower, capsule prisoners, hitscan rifle, zero art, two machines "
         "connected, bots filling the lobby. Gate: is it fun with programmer art? If it is "
         "not, no modeling saves it and the scope ledger gets cut, not extended."),
        ("netcode_server_authoritative", date(2026, 10, 21), "BUILD", 0,
         "Server-authoritative shot arbitration on ENetMultiplayerPeer with a dedicated-server "
         "export. The single item most likely to eat the ship date if deferred."),
        ("guard_vision_resolved", date(2026, 11, 15), "DECISION", 0,
         "panopticon.open.guard_vision closed by playtest data plus one human feel session, "
         "and written into `decisions`."),
        ("first_devlog_published", date(2026, 10, 1), "CONTENT", 0,
         "Announcement video. Must land after the store page exists so it has somewhere to "
         "send viewers -- a devlog with no wishlist target is leaked value."),
        ("art_direction_locked", date(2026, 12, 15), "DECISION", 0,
         "Ryan decides the look; Astra begins production modeling against it on the PC."),
        ("music_sourced", date(2027, 1, 15), "DECISION", 0,
         "Ryan-made or commissioned. Named early because it is a gap AI is not filling."),
        ("feature_freeze", date(2027, 2, 15), "BUILD", 0,
         "Scope ledger closes. After this the ratchet only cuts."),
    ]


SCOPE_SEED = [
    ("Central tower with guard shooting", "SHIP_BLOCKING"),
    ("Prisoner traversal start to end around the ring", "SHIP_BLOCKING"),
    ("Server-authoritative multiplayer, 1v1 to 1v7", "SHIP_BLOCKING"),
    ("Bot prisoners and bot guard", "SHIP_BLOCKING"),
    ("Headless match runner writing playtest rows", "SHIP_BLOCKING"),
    ("Lobby, match flow, win and loss states", "SHIP_BLOCKING"),
    ("At least one finished ring with cover and traps", "SHIP_BLOCKING"),
    ("Prisoner and guard models with animation", "SHIP_BLOCKING"),
    ("Menus, settings, keybinds", "SHIP_BLOCKING"),
    ("Windows build on Steam", "SHIP_BLOCKING"),
    ("Sound effects", "SHIP_BLOCKING"),
    ("Music", "WANTED"),
    ("Multiple rings of escalating difficulty", "WANTED"),
    ("Role reversal after prisoners clear the course", "WANTED"),
    ("Shot prisoner becomes a second guard", "WANTED"),
    ("Mac build", "STRETCH"),
    ("Cosmetics", "STRETCH"),
    ("Map editor", "STRETCH"),
]


def seed(conn) -> dict:
    """Idempotent, and NON-DESTRUCTIVE. Returns what was written.

    Facts INSERT-OR-IGNORE rather than upsert.  Until 2026-09-10 this upserted, which
    meant `./panopticon.py seed` silently reverted every correction Ryan had made since
    the seed was written: `panopticon.music` would have gone back to "Ryan creates it, or
    commissions on Fiverr" and thrown away decision 21's SCORE-not-radio ruling, and
    `panopticon.testing.bots` would have lost the "these are not LLM agents" correction.
    The seed's job is to reconstitute a MISSING fact, never to overrule a live one.  To
    change a fact deliberately, edit the row.
    """
    for key, value, source, authorized, verified_by, immutable in FACTS:
        conn.execute(
            """INSERT INTO facts (key, value, source, authorized, ratified_on, verified_by,
                                  is_immutable, updated_at)
               VALUES (?,?,?,?,?,?,?,CURRENT_TIMESTAMP)
               ON CONFLICT(key) DO NOTHING""",
            (key, json.dumps(value), source, authorized,
             RATIFIED_ON if verified_by == "ryan" else "", verified_by, immutable))

    for name, due, kind, hard, notes in _steam_calendar() + _project_milestones():
        conn.execute(
            """INSERT INTO milestones (name, due_on, kind, hard, notes)
               VALUES (?,?,?,?,?)
               ON CONFLICT(name) DO UPDATE SET
                   due_on=excluded.due_on, kind=excluded.kind, hard=excluded.hard,
                   notes=excluded.notes""",
            (name, due.isoformat(), kind, hard, notes))

    for feature, tier in SCOPE_SEED:
        conn.execute(
            """INSERT INTO scope_ledger (feature, tier, added_on)
               VALUES (?,?,?) ON CONFLICT(feature) DO NOTHING""",
            (feature, tier, RATIFIED_ON))

    conn.commit()
    n_tasks = seed_tasks(conn)
    n_dec = seed_decisions(conn)
    return {"facts": len(FACTS),
            "milestones": len(_steam_calendar()) + len(_project_milestones()),
            "scope": len(SCOPE_SEED), "tasks": n_tasks, "decisions": n_dec}


# (title, detail, lane, owner, estimate_hours, blocked_by, feature, milestone)
# Lanes are about WHERE work can happen, not importance.  PC_REQUIRED spends the scarce
# resource; a PC task lists its remote prerequisites so it cannot become READY early.
TASK_SEED = [
    # ---- unblocking everything else -------------------------------------------------
    ("Decide how the Senate repo reaches the PC",
     "Private GitHub repo (also offsite backup) or scp over Tailscale. The repo has no "
     "remote today, so nothing can be cloned until this is answered.",
     "RYAN_DECISION", "RYAN", 0.2, "", "", "pc_bootstrapped"),
    ("Run bootstrap_pc.ps1 on the PC",
     "Administrator PowerShell. Installs git/python/Godot/Blender/Tailscale/Claude Code, "
     "enables OpenSSH, stops the machine sleeping.",
     "PC_REQUIRED", "RYAN", 1.0, "Decide how the Senate repo reaches the PC", "",
     "pc_bootstrapped"),
    ("Verify the Mac can drive the PC head over Tailscale SSH",
     "ssh in, run ./panopticon.py status, confirm the head boots. This is what makes the "
     "60 remote hours usable at all.",
     "PC_REQUIRED", "RYAN", 0.5, "Run bootstrap_pc.ps1 on the PC", "", "pc_bootstrapped"),
    ("Buy Astra access", "Ryan named it as the 3D modeling tool. It drives Blender on the PC.",
     "RYAN_DECISION", "RYAN", 0.2, "", "Prisoner and guard models with animation", ""),
    ("Define what Fable 5.1 is and what it does here",
     "Recorded as an open fact; the pod refuses to invent a role for it.",
     "RYAN_DECISION", "RYAN", 0.2, "", "", ""),

    # ---- the engine work ------------------------------------------------------------
    ("Create the Godot 4 project skeleton",
     "C:/dev/panopticon-game, git init, folder layout, .gitignore, first commit.",
     "REMOTE", "HEAD", 1.0, "Verify the Mac can drive the PC head over Tailscale SSH", "", ""),
    ("Stand up ENet server-authoritative connection",
     "ENetMultiplayerPeer, one host acting as server, clients sending input only. No game "
     "yet -- two capsules moving, server owning position.",
     "REMOTE", "HEAD", 6.0, "Create the Godot 4 project skeleton",
     "Server-authoritative multiplayer, 1v1 to 1v7", "netcode_server_authoritative"),
    ("Server-side shot arbitration",
     "Hitscan resolved on the server against server-held positions, with client feedback. "
     "The guard's shot is the core verb; it cannot live on the client.",
     "REMOTE", "HEAD", 5.0, "Stand up ENet server-authoritative connection",
     "Central tower with guard shooting", "netcode_server_authoritative"),
    ("Greybox the ring and the central tower",
     "One ring track, start and end markers, a tower with sightlines. Capsules and boxes.",
     "REMOTE", "HEAD", 4.0, "Create the Godot 4 project skeleton",
     "At least one finished ring with cover and traps", "greybox_slice_playable"),
    ("Prisoner traversal and win condition",
     "Move start to end, reach-end detection, death on hit, round end.",
     "REMOTE", "HEAD", 4.0, "Greybox the ring and the central tower",
     "Prisoner traversal start to end around the ring", "greybox_slice_playable"),
    ("Bot prisoner: navigate the ring start to end",
     "Navigation along the track with cover use. Does not need to be smart; it needs to be "
     "repeatable, because it is the measuring instrument.",
     "REMOTE", "HEAD", 5.0, "Prisoner traversal and win condition",
     "Bot prisoners and bot guard", "bot_harness_runs_headless"),
    ("Bot guard: acquire and shoot from the tower",
     "Target selection, aim error model, fire rate. The aim-error parameter is the knob "
     "that stands in for human skill when tuning balance.",
     "REMOTE", "HEAD", 5.0, "Server-side shot arbitration",
     "Bot prisoners and bot guard", "bot_harness_runs_headless"),
    ("Headless match runner writing playtest rows",
     "godot --headless boots a dedicated server, spawns N bot prisoners and 1 bot guard, "
     "runs to completion, writes a playtests row. THE ORACLE: this is how remote hours "
     "produce evidence with no humans available.",
     "REMOTE", "HEAD", 6.0, "Bot prisoner: navigate the ring start to end,"
     "Bot guard: acquire and shoot from the tower",
     "Headless match runner writing playtest rows", "bot_harness_runs_headless"),
    ("Sweep guard vision configurations in bot matches",
     "360-degree vision versus a limited arc, many matches per configuration, win rates "
     "and match durations recorded. Produces the DATA for the open guard-vision question; "
     "it does not answer it.",
     "REMOTE", "HEAD", 3.0, "Headless match runner writing playtest rows", "",
     "guard_vision_resolved"),
    ("Play the greybox slice and judge whether it is fun",
     "The gate the whole project turns on. Bots cannot answer this and neither can I.",
     "PC_REQUIRED", "RYAN", 2.0,
     "Prisoner traversal and win condition,Bot guard: acquire and shoot from the tower",
     "", "greybox_slice_playable"),
    ("Rule on guard vision",
     "Ryan decides, against the bot sweep plus one human session. Recorded in `decisions`.",
     "RYAN_DECISION", "RYAN", 0.5,
     "Sweep guard vision configurations in bot matches,"
     "Play the greybox slice and judge whether it is fun", "", "guard_vision_resolved"),

    # ---- Steam and audience ---------------------------------------------------------
    ("Pay the Steam Direct fee and create the app",
     "$100, recoupable at $1,000 revenue. Starts the mandatory 30-day clock.",
     "RYAN_DECISION", "RYAN", 0.5, "", "Windows build on Steam",
     "steam_fee_paid_and_app_created"),
    ("Submit Steam tax, banking and identity documents",
     "Blocks payout, and silently blocks release if left late.",
     "RYAN_DECISION", "RYAN", 1.0, "Pay the Steam Direct fee and create the app", "",
     "steam_tax_banking_identity_verified"),
    ("Draft the Steam store page copy and asset list",
     "Short description, about section, capsule sizes, screenshot plan, trailer outline.",
     "REMOTE", "HEAD", 3.0, "", "", "steam_store_page_public"),
    ("Create the YouTube, Twitter, TikTok and Instagram accounts",
     "Audience-building starts now and does not wait on the store page (Ryan, 2026-09-09).",
     "REMOTE", "RYAN", 1.0, "", "", "first_devlog_published"),
    ("Write and edit devlog 1: what Panopticon is",
     "The concept, the Duck Hunt lineage, the panopticon twist. No gameplay footage needed.",
     "REMOTE", "RYAN", 3.0, "Create the YouTube, Twitter, TikTok and Instagram accounts",
     "", "first_devlog_published"),
    ("Set up automatic footage capture on the PC",
     "Every PC session records, so footage is a byproduct and never costs a PC hour.",
     "REMOTE", "HEAD", 1.5, "Verify the Mac can drive the PC head over Tailscale SSH", "", ""),

    # ---- keeping the machine honest -------------------------------------------------
    ("Wire the pod's own state-surface and honesty hooks",
     "Same two hooks the Senate head runs: DB truth injected each turn, and the head's own "
     "final message linted before Ryan reads it.",
     "REMOTE", "HEAD", 2.0, "Verify the Mac can drive the PC head over Tailscale SSH", "", ""),
]


def seed_tasks(conn) -> int:
    n = 0
    for (title, detail, lane, owner, est, blocked, feature, milestone) in TASK_SEED:
        conn.execute(
            """INSERT INTO tasks (title, detail, lane, owner, estimate_hours, blocked_by,
                                  feature, milestone, created_on)
               VALUES (?,?,?,?,?,?,?,?,?)
               ON CONFLICT(title) DO UPDATE SET
                   detail=excluded.detail, lane=excluded.lane, owner=excluded.owner,
                   estimate_hours=excluded.estimate_hours, blocked_by=excluded.blocked_by,
                   feature=excluded.feature, milestone=excluded.milestone""",
            (title, detail, lane, owner, est, blocked, feature, milestone, RATIFIED_ON))
        n += 1
    conn.commit()
    return n


DECISIONS_SEED = [
    ("2026-09-09", "content: audience before store page",
     "Followers are built before there is a place to send them; devlogs do not wait on the "
     "Steam page.",
     "Ryan, 2026-09-09: 'not true on the leaked value thing, i can buld followers before "
     "giving them a place to go.' A prior session had asserted the opposite from inference.",
     "ryan ruling"),
    ("2026-09-09", "the pod tracks tasks, not just gates",
     "The head continuously evaluates what needs doing and keeps either itself or Ryan "
     "working on it; an idle head with open work is an escalation.",
     "Ryan, 2026-09-09: 'i want it constantly evaluating what needs to get done and hacing "
     "either me or it working on it.'",
     "ryan ruling"),
]


# Standing orders: rendered in EVERY boot prompt, never rotated out by a newer ruling.
# See interface/head_prompt.standing_orders_block for why the recency window was not enough.
PINNED_TOPICS = {"the pod tracks tasks, not just gates"}


def seed_decisions(conn) -> int:
    for (on, topic, ruling, rationale, evidence) in DECISIONS_SEED:
        exists = conn.execute("SELECT 1 FROM decisions WHERE topic=?", (topic,)).fetchone()
        if not exists:
            conn.execute("INSERT INTO decisions (decided_on, topic, ruling, rationale, "
                         "evidence, pinned) VALUES (?,?,?,?,?,?)",
                         (on, topic, ruling, rationale, evidence,
                          int(topic in PINNED_TOPICS)))
    conn.commit()
    return len(DECISIONS_SEED)
