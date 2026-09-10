# PANOPTICON — Engineering Framework and Work Breakdown
### 2026-09-09 · head plan, awaiting Ryan's review · 204 days to ship

**Objective of this document.** Not to build the game. To establish that the framework can
produce the game, and to decompose the eleven ship-blocking features into ordered work with
lanes, dependencies and estimates — so that ~233 remaining PC hours get spent on the right
things in the right sequence.

**The rule that governs every choice below:** this is a clean Godot project of the kind a
competent human would build. Nothing here is shaped by what the head can or cannot run today.

---

## PART 1 — FRAMEWORK

### 1.1 Repository

Separate private GitHub repo, `panopticon`, distinct from the Senate pod. The pod is the head's
state; the game is the product; they version independently. Godot project sits at repo root,
which is the convention and keeps CI paths trivial.

### 1.2 Godot version

Pinned at bootstrap to the then-current stable, recorded as a fact, and identical on both
machines. A `.godot-version` file in the repo so CI and both machines agree. **Not guessed
now** — it gets read off the machine at bootstrap and written down.

A version mismatch between machines silently rewrites `project.godot` and can one-way upgrade
scene formats. This is the single most likely way to corrupt a two-machine Godot project.

### 1.3 Git hygiene — must exist in the first commit, not retrofitted

| | |
|---|---|
| **Ignore** | `.godot/` (import cache + editor state), `export/`, `.DS_Store`, `Thumbs.db` |
| **Commit** | `*.import` and `*.uid` sidecars, `project.godot`, `export_presets.cfg` |
| **`.gitattributes`** | `* text=auto eol=lf` plus explicit binary markers — without this, CRLF churn rewrites every file each time it crosses machines |
| **Git LFS** | `.blend`, `.wav`, `.ogg`, large textures. Decided now; migrating later rewrites history |
| **Path convention** | all-lowercase. macOS and Windows are case-insensitive, exported builds are not — mismatched casing works on both dev machines and breaks only for players |

### 1.4 Project layout

```
/scenes      .tscn, grouped by domain — ring/ tower/ player/ ui/
/scripts     .gd mirroring scenes, plus systems/ for non-node logic
/resources   .tres — including the match rule configs
/assets      models, textures, audio, fonts
/addons      third-party: test framework, Steam integration
/tests       headless suite
/tools       harness scripts, CI helpers, ingest
```

### 1.5 Testing and CI — the thing that makes remote work honest

GdUnit4 for tests; it runs headless and returns real exit codes.

GitHub Actions on every push: headless import, script validation, test suite, Windows export.

This is not ceremony. The pod's rule is that *done means a build that ran*. CI is what makes
that enforceable instead of aspirational — and it is what lets the head work without an editor
without handing Ryan unverified code to debug on scarce PC hours.

### 1.6 Netcode

Godot's high-level multiplayer, with the transport behind an interface:

- **ENetMultiplayerPeer** for development, headless runs and CI — no Steam dependency, so the
  bot harness never needs Steam running.
- **SteamMultiplayerPeer** for shipping — free relay, NAT traversal, no IP exposure, no servers
  to rent.

Server-authoritative on a **player-hosted listen server**. Authority is bound to a stable peer
and **never to the tower role**, because the tower rotates constantly.

### 1.7 Match rules as data — what makes pick-then-sweep real

A `MatchRules` Resource. Every deferred design decision is a field on it: shooter win condition,
TTK, prisoner lives, ghost variant and speed, round structure, guard vision, cover rules, reload
duration and its escalation curve, player counts, the eye behaviour.

The headless runner takes a rules file per match. Building an alternative costs a `.tres`, not a
rewrite. **If any of these are hard-coded, the sweep becomes impossible retroactively and the
whole method Ryan chose dies quietly.** This is the highest-leverage decision in the framework.

### 1.8 Bot harness

A headless scene that runs N matches from a rules file and emits JSON; a `tools/` ingest writes
`playtests` rows. Bots are behaviour trees over a navmesh — standard game AI, offline, free per
match, thousands of runs unattended.

### 1.9 The two-machine workflow

| | Mac (≈60h/wk) | PC (≈8h/wk, scarce) |
|---|---|---|
| **Does** | code, tests, headless runs, CI, review, ingest | editor work, geometry, art, feel, footage |
| **Never** | judges feel, lays out geometry | anything that could have been done remotely |

Sync is git and only git. **Never both edit the same scene at once** — Godot scene merges are
genuinely bad. The head reaches the PC over Tailscale SSH for headless runs.

---

## PART 2 — WORK BREAKDOWN

Five phases. Each phase's exit criterion is a thing that *ran*, never a document.

### Setup — blocks literally everything
Repo, version pin, git hygiene, layout, CI, test framework, the MatchRules resource.
**Exit:** CI green on an empty project and a Windows export artifact exists.

### Core loop — greybox
Shared movement controller, ring greybox, tower room, hitscan + reload + tracer, round state
machine, match state machine with the race-for-the-tower opener and seat handover.
**Exit:** one human can play a full match against nothing and the loop resolves correctly.

### Bots and harness — the oracle
Navmesh, bot prisoner, bot shooter, headless runner, JSON emit, playtests ingest, sweep driver.
**Exit:** `bot_harness_runs_headless` — an unattended match writes a real playtests row.

### Netcode
Authority model, transport interface, ENet dev path, state sync, lobby, Steam transport.
**Exit:** `netcode_server_authoritative` — two machines play one match.

### Content and ship
Models and animation, one finished ring, menus/settings/keybinds, sound, music, Steam build.
**Exit:** a stranger can buy it.

### Sequencing note that matters

Bots are scheduled **before** netcode, against the instinct to get multiplayer working early. The reason
is the pod's own economics: bots are the oracle, Ryan has nobody to test with, and a headless
sweep converts 60 remote hours into evidence. Netcode produces no evidence about whether the
game is fun. Building the oracle first means every subsequent decision is measured rather than
argued.

### The one thing this plan cannot buy

`greybox_slice_playable` (2026-10-21) exists so Ryan can answer the only question no amount of
remote work touches: **is it fun?** Everything in P0–P2 is in service of putting that question
in front of him early enough that the answer still leaves time to act on it.
