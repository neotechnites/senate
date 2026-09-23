"""Autonomous Kalshi Domain Cadence Daemon.

INVARIANT: IDLE IS A BUG.
Continuously runs tactical execution across registered strategy lanes:
0. PLACEMENT ENGINE DEFENSIVE FAST-PATH at the TOP of every cycle:
   fill-halt (any fill on our seats -> cancel family + auto-DISARM),
   hard-exit deadlines, 24h curfew exits, venue-truth reconcile.
0b. VENUE RECONCILE (harness/venue_reconciler, VR-6 2026-09-05): the
   active_orders mirror is reconciled to the venue in both directions and
   any ORPHAN venue order (no live plan row tracks it) is cancelled through
   the defensive gate -- before anything below may place.
   VR-0 (same day): it judges the SAME open-orders + fills read the sweep
   just made (one venue read per cycle), applies the plan's two-strike rule
   to the mirror, re-links a live order on a terminal row, and ends every
   cycle with a fixed-shape `reconcile: ...` summary plus an incident row
   for every orphan cancelled / uncancellable and every mass-vanish read.
0c. OBSERVABLE-CLASS SWEEP (harness/obs_sweep, OBS-9 2026-09-05): every live
   plan row (resting / pending / withdrawn_rearmed) is classified by the SAME
   informed-sweep function every entry gate uses (catalyst_review
   .reentry_class); an OBSERVABLE seat is cancelled through the defensive
   gate and its row exited under an 'observable-class' note, a terminal seat
   is held, an unknown one is named for the watcher and handed to the relay.
   Before today a resting observable seat was only ALARMED for a human to
   cancel by hand -- all 25 lifetime fills were sweeps of exactly that class.
   NOTE: the ~300s cycle interval is the REACTION FLOOR for these checks —
   a fill can go unanswered for up to one full cycle.  A tighter (sub-minute)
   defensive loop is known future work; never treat 5min as a safety property.
1. Syncs live venue orders & balances via authenticated API / oracle
2. Runs dynamic Census Scanner with live catalog diffing and 24h curfew gates
3. Checks resting order safety invariants and budget headroom
4. Reports the placement state machine (BLOCKER LEDGER) every cycle — WHY
   zero orders were placed, from the queryable `placement_state` table
5. OFFENSIVE RECONCILE: while placement_state == ARMED, reconciles the
   `deployment_plan` table to the venue through the full fail-closed gauntlet
   (software places orders — no human/Claude in the loop; arming is Ryan's
   single manual action: ./kalshi.py placement set --state ARMED ...)
6. Logs genuine cycle progress to `lane_runs` in `kalshi_domain.db`

WEEKLY: the watchdog/daemon owner must also re-run the verdict provenance
audit (`python3 harness/verdict_audit.py`) — see harness/verdict_audit.py.

======================================================================
LIVENESS IS NEVER BUFFERED (2026-08-18) — OBSERVABILITY ONLY
======================================================================
On 2026-08-18 this daemon (pid 26016) appeared to have stalled: no completed
cycle had reached state/daemon_20260818.log since 13:24:44Z, ~8 cycles' worth
of silence, process alive at ~0 % CPU with no children.  Because this daemon
carries the placement engine's FILL-HALT, "the daemon is hung" reads as "a real
fill is going unanswered", and it was investigated as an incident.

IT HAD NOT MISSED A SINGLE CYCLE.  `lane_runs` in kalshi_domain.db shows
cycle_52..cycle_62 completing on a metronomic ~5.4 min cadence right through
the supposed outage (13:30:09, 13:35:37, 13:41:02, 13:46:25, 13:51:47,
13:57:11, 14:02:39, 14:08:00, 14:13:24, 14:18:46, 14:24:09), and the fill-halt
for the 13:42:04Z fill fired normally at cycle 55 (13:46:25Z) with its
observed_fills row written.  The daemon was healthy; ITS LOG WAS LYING.

ROOT CAUSE: `print()` with stdout redirected to a FILE is BLOCK-buffered by
CPython (8 KiB), not line-buffered.  A cycle line here is ~700 bytes, so
completed cycles sat in the buffer and the operator-visible log only advanced
once every ~11 cycles — the better part of an hour of apparent silence per
flush.  The queue shield never had this problem because its emit() passes
flush=True.

THE FIX IS OBSERVABILITY ONLY.  Every line this daemon writes now goes through
log() with flush=True, and start() forces line buffering on stdout/stderr so a
redirect cannot re-introduce the lag.  NOTHING about control flow, cadence,
ordering, gating or any safety clause changes — the only difference is WHEN the
same bytes reach the file.  Belt and braces at the launcher: run with `-u`.
"""

import os
import time
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from domains.kalshi.state.fact_store import FactStore
from domains.kalshi.harness.venue_client import KalshiVenueClient
from domains.kalshi.harness.census_scanner import CensusScanner
from domains.kalshi.harness.oracle_sync import sync_kalshi_oracle
from domains.kalshi.harness import duty_cycle
from domains.kalshi.harness import hazard_gate
from domains.kalshi.harness.duty_cycle import seats_file_path
from domains.kalshi.harness.placement_engine import PlacementEngine


MIRROR_RECONCILE_GRACE_S = 600.0   # matches placement_engine.RECONCILE_GRACE_S
MIRROR_MASS_VANISH_MIN_RESTING = 3


def reconcile_order_mirror(store, client, now_utc=None, cancel_orphans=True,
                           snapshot=None) -> str:
    """THE MIRROR + ORPHAN RECONCILE, EVERY CYCLE.  VR-6 (2026-09-05): this is
    now a thin door onto harness/venue_reconciler.reconcile -- the ONE
    reconciler the daemon and `./kalshi.py sync-orders` share.  The name and
    the one-line return are kept so the cycle log and the VR-5 tests read the
    same; the behaviour (both mirror directions, 10-min grace, mass-vanish
    guard, fail closed on an unreadable venue) is unchanged, and it GAINS the
    actuator none of the three old reconcilers had: an untracked venue order
    (no pending / resting / withdrawn_rearmed / stood_down plan row names it,
    not one of our closes, older than the grace, not adoptable by an ARMED
    engine) is CANCELLED through the defensive gate.  KXUST10AM 01a069d1
    rested 17 h that way; the daemon now pulls it on the next cycle instead
    of waiting for a human to read the watcher.  The venue read carries the
    shared 429 retry, which the old body did not.

    VR-0 (2026-09-05): `snapshot` is the defensive sweep's own open-orders +
    fills read (PlacementEngine.last_venue_snapshot).  When it is fresh the
    reconciler judges THAT read -- one venue read per cycle, both ledgers
    judged against the same truth -- and reads fresh only when it is absent
    or stale.  The mirror now takes the plan's two-strike rule (a single
    missing read past the grace no longer retires it) and the line ends with
    the fixed-shape `reconcile: venue=.. plan_resting=.. mirror_resting=..
    orphans=.. ghosts=.. positions=..` summary the watcher greps."""
    from domains.kalshi.harness.venue_reconciler import reconcile
    return reconcile(store, client, now_utc=now_utc, mirror_venue=False,
                     cancel_orphans=cancel_orphans, snapshot=snapshot).line()


def placement_report(store: FactStore, opportunities: list) -> str:
    """BLOCKER LEDGER: state WHY zero orders were placed this cycle.

    Every cycle must report the placement state machine explicitly — never a
    bare zero. Source of truth is the `placement_state` table (queryable,
    append-only), not daemon memory. Ryan ruling 2026-08-17: the org only
    discovering its own placement-disarmed state under interrogation is a
    framework bug.
    """
    ps = store.get_placement_state()
    if ps["state"] == "HALTED":
        return (f"placement: HALTED — GLOBAL FREEZE, nothing places at all, not even "
                f"maintenance of a seat we already hold ({ps['reason']}) "
                f"[set_by {ps['set_by']} @ {ps['set_at']}]")
    if ps["state"] == "DISARMED":
        # SCOPE MATTERS (2026-08-18): DISARMED freezes NEW deployments only.
        # Existing seats keep their full shield, so the ledger must not imply
        # the pod is inert — but it must still say plainly that a fill-halt
        # fired, on which family, and that nothing new may be seated.
        return (f"placement: DISARMED — NEW DEPLOYMENTS FROZEN ({ps['reason']}) "
                f"[set_by {ps['set_by']} @ {ps['set_at']}] — already-held seats keep "
                f"their full shield (reactive cancel + atomic re-arm + hourly timer); "
                f"any filled family stays barred by the post-fill re-entry ban")

    # ARMED: explain what the screen did with the candidates.
    qualified = [o for o in opportunities if o.get("status") == "QUALIFIED"]
    if qualified:
        return (
            f"placement: ARMED, {len(qualified)} candidates passed screen, "
            f"pending approval/deployment"
        )
    blockers: dict = {}
    for o in opportunities:
        st = o.get("status") or "UNKNOWN"
        if st != "QUALIFIED":
            blockers[st] = blockers.get(st, 0) + 1
    if blockers:
        top = max(blockers.items(), key=lambda kv: kv[1])
        return (
            f"placement: ARMED, 0 candidates passed screen "
            f"(top blocker: {top[0]} x{top[1]} of {len(opportunities)})"
        )
    return "placement: ARMED, 0 candidates surfaced by census scan (empty screen input)"


# REARM-SWEEP (2026-09-10).  How often, BETWEEN full cycles, the engine's
# existing re-placement attempt is made over 'withdrawn_rearmed' rows -- and,
# since the same day, over never-yet-offered 'pending' rows
# (PlacementEngine.run_pending_sweep, cause 9).  ONE cadence, two statuses,
# each through the same gauntlet at its own armor phase.
#
# THE MEASUREMENT (scratchpad/duty_cycle_uptime.md, 23 day-clusters).  A
# reactive shield trip cancels first (fast_cancel=True deliberately does not
# honour the anti-thrash block), so a refused trip CASHES: the seat is empty,
# the row sits 'withdrawn_rearmed', and NOTHING re-places it until this
# daemon's next wake.  1,834 shield-cash episodes over the window show that as
# a hard floor at exactly 300 s — 123 episodes in [300,330) s, FIVE in the
# whole of [60,300) s in 23 days — with a median of 493 s and p25 362 s.  The
# floor is `interval_seconds` and nothing else.
#
# 30 s is chosen against what the sweep actually costs, not against the floor:
# a pass that finds no locally-eligible row makes ZERO venue calls (see
# PlacementEngine.run_rearm_sweep), and a pass that does find one costs the
# same three reads a normal cycle already spends.  So the cadence is set by how
# quickly we want to notice a row becoming eligible, and 30 s is one tenth of
# the dwell floor it is waiting on — fine-grained enough that the sweep is
# never the binding delay, coarse enough that a book of eligible rows cannot
# spend more venue budget than the ordinary cycle would.
#
# HONEST CEILING: this cannot pull a cash episode below MIN_DWELL_SEC, because
# the cadence re-placement path is governed by replace_guard clause 1 and this
# sweep relaxes NOTHING.  When this comment was written that ceiling was 300 s
# and the expected effect was 493 s -> ~315 s on the median episode.
# UPDATED 2026-09-10 (DWELL-DERIVED): MIN_DWELL_SEC was derived from the tape
# and set to 60 s, so the ceiling is now 60 s and the expected effect on the
# median episode is 493 s -> ~90 s (this 30 s cadence plus the 60 s floor).
# 30 s is HALF the floor it waits on, so the sweep is still never the binding
# delay; it was one tenth of the old floor.
REARM_SWEEP_INTERVAL_SEC = int(os.environ.get("KALSHI_REARM_SWEEP_SEC", "30"))


class KalshiCadenceDaemon:
    def __init__(self, interval_seconds: int = 300, max_cycles: Optional[int] = None):
        self.interval = interval_seconds
        # NOT a constructor parameter, deliberately: test_daemon_log_flush pins
        # this signature as the daemon's construction contract, and the sweep
        # cadence is a policy number with an env override, not a caller's
        # business.  Read through getattr in the loop so a fixture that builds
        # the daemon with __new__ (that same test file) still works.
        self.rearm_interval = max(0, int(REARM_SWEEP_INTERVAL_SEC))
        self.max_cycles = max_cycles
        self.store = FactStore()
        # ONE ARMOR BAR FOR EVERY PROCESS (2026-08-18).  Installed from the
        # shared fact before anything can decide a placement, and printed in the
        # boot banner below so this daemon's number and the queue shield's are
        # comparable at a glance.  See duty_cycle.resolve_armor_policy for the
        # GOOG incident that made two processes disagree.
        self.armor_policy = duty_cycle.resolve_armor_policy(self.store)
        self.replacement_policy = duty_cycle.resolve_replacement_policy(self.store)
        # ONE HAZARD GATE FOR EVERY PROCESS (2026-08-18), by the same mechanism
        # and for the same reason: the queue shield and this daemon both decide
        # whether a seat may exist, and they must not be able to answer that two
        # ways.  Installed from the shared fact kalshi.hazard.policy before
        # anything can decide a placement, and printed in the boot banner below
        # so this daemon's numbers and the shield's are a one-line diff.
        self.hazard_policy = hazard_gate.resolve_hazard_policy(self.store)
        self.client = KalshiVenueClient()
        self.scanner = CensusScanner(self.client)
        from domains.kalshi.harness.auto_seeder import AutoSeeder
        self.seeder = AutoSeeder(store=self.store, client=self.client)
        self.engine = PlacementEngine(
            store=self.store,
            client=self.client,
            program_index_loader=self.scanner.load_live_program_index,
            hazard_gate=hazard_gate.HazardGate(client=self.client),
            # PRODUCTION ONLY: re-baseline the queue shield's pre-registered A0
            # on every (re-)placement.  Passed explicitly here and nowhere else,
            # so no test can overwrite the live pre-registration file.
            seats_file=seats_file_path(),
        )
        # OBS-9 (2026-09-05): the observable-class sweep shares the engine's
        # gate (defensive CANCEL_ORDER fast-path) and duty-cycle ledger, so
        # an eviction is accounted exactly like a hard-exit / curfew-exit.
        from domains.kalshi.harness.obs_sweep import ObsSweep
        self.obs_sweep = ObsSweep(store=self.store, client=self.client,
                                  gate=self.engine.gate, ledger=self.engine.ledger)

    # ------------------------------------------------------------------
    # LIVENESS IS NEVER BUFFERED (2026-08-18).  print() to a redirected file is
    # block-buffered by CPython, which made a healthy daemon look stalled for an
    # hour at a time and cost an incident investigation.  Every line this daemon
    # emits goes through here, and every one is flushed.
    # ------------------------------------------------------------------
    def log(self, message: str, error: bool = False) -> None:
        stream = sys.stderr if error else sys.stdout
        try:
            print(message, file=stream, flush=True)
        except Exception:
            pass

    @staticmethod
    def _configure_streams() -> None:
        """Force line buffering even when stdout/stderr are redirected files."""
        for stream in (sys.stdout, sys.stderr):
            try:
                stream.reconfigure(line_buffering=True)  # type: ignore[union-attr]
            except Exception:
                pass

    def sleep_with_rearm_sweeps(self, seconds: float) -> int:
        """The inter-cycle wait, with the REARM-SWEEP running inside it.

        This REPLACES `time.sleep(self.interval)` and is the whole of the
        change: the cycle itself is untouched, nothing is placed by a new path,
        and with rearm_interval == 0 it is exactly the old sleep.  Returns the
        number of sweeps that produced an action, so a caller (and the test)
        can see whether the wait did any work.

        A sweep that raises can never end the daemon: run_rearm_sweep already
        returns its error as a line, and the belt-and-braces guard here means
        even an unexpected failure costs one sweep, not the loop.

        PENDING-SWEEP (2026-09-10): the same tick also runs
        PlacementEngine.run_pending_sweep, which offers each brand-new
        'pending' row to the gauntlet ONCE.  That closes cause 9 (seed -> first
        placement, 396 seat-min/day) for rows the systemd-timer seeder writes
        out of band; the in-cycle seeder is already covered by run_cycle step
        2d'.  It is the same gauntlet at the ENTRY armor phase, it costs zero
        venue calls when no un-offered row exists, and it seats nothing under a
        freeze."""
        deadline = time.time() + float(seconds)
        acted = 0
        every = max(0, int(getattr(self, "rearm_interval", REARM_SWEEP_INTERVAL_SEC)))
        if every <= 0:
            time.sleep(max(0.0, deadline - time.time()))
            return acted
        while True:
            remaining = deadline - time.time()
            if remaining <= 0:
                break
            time.sleep(min(float(every), remaining))
            if time.time() >= deadline:
                break
            lines: list = []
            # TWO SWEEPS, ONE TICK.  run_rearm_sweep owns 'withdrawn_rearmed'
            # (cause 1, the 300 s cash floor); run_pending_sweep owns brand-new
            # 'pending' rows the systemd-timer seeder wrote out-of-band (cause
            # 9, seed -> first placement).  Both return [] with ZERO venue calls
            # when nothing is locally eligible, and neither is a new placement
            # path: each is _run_offensive restricted to one status.
            for _name in ("run_rearm_sweep", "run_pending_sweep"):
                try:
                    got = getattr(self.engine, _name)()
                except Exception as exc:                      # noqa: BLE001
                    got = [f"{_name}: ERROR {str(exc)[:160]} "
                           f"(the daemon survives; next sweep retries)"]
                # A non-list (a test double, a future return shape) is ignored
                # rather than joined: a 30 s loop that can kill the daemon would
                # be a worse bug than the one this fixes.
                if isinstance(got, list):
                    lines.extend(str(x) for x in got)
            if lines:
                acted += 1
                self.log(f"[{datetime.now(timezone.utc).isoformat()}] "
                         f"rearm-sweep: {'; '.join(lines)}")
        return acted

    def run_cycle(self, cycle_num: int) -> dict:
        ts = datetime.now(timezone.utc).isoformat()
        results = {
            "cycle": cycle_num,
            "timestamp": ts,
            "actions_taken": [],
        }

        # 0. PLACEMENT ENGINE DEFENSIVE FAST-PATH — always FIRST, before any
        # scan or sync: fill-halt, hard-exit, curfew-exit, venue reconcile.
        # (~300s interval == reaction floor; tighter loop is future work.)
        results["actions_taken"].extend(self.engine.run_defensive())

        # 0b. VENUE RECONCILE — the sync-orders antidote, EVERY cycle
        # (ratified 2026-08-31), now the ONE reconciler (VR-6, 2026-09-05:
        # harness/venue_reconciler).  Moved HERE from the end of the cycle:
        # it used to run after two offensive passes and the seeder had
        # already placed against a stale mirror, and it could not cancel
        # the orphan it was looking at.  Right after the defensive sweep
        # (whose RE-LINK has just revived any terminal row with a live
        # order) and BEFORE anything places: the mirror the caps, the
        # seeder's shortfall and the rotation engine sum is venue-true for
        # the rest of this cycle, and an untracked seat is pulled before the
        # book is judged.  Every write inside still fails closed.
        if self.client.has_credentials:
            results["actions_taken"].append(
                reconcile_order_mirror(
                    self.store, self.client,
                    # VR-0: the sweep's read, not a second one (None -> fresh read)
                    snapshot=getattr(self.engine, "last_venue_snapshot", None)))

        # 0c. OBSERVABLE-CLASS SWEEP (OBS-9, 2026-09-05) -- after the reconcile
        # (the plan is venue-true) and BEFORE anything may place or re-place.
        # Receipt: every entry path met the informed-sweep gate by today, but a
        # seat ALREADY RESTING on an observable market met nothing except a
        # watcher alarm and a prompt line asking a human to cancel it by hand;
        # 16 of 19 resting seats on 2026-09-04 were that class, and all 25
        # lifetime fills were informed sweeps of it.  The sweep evicts an
        # observable seat mechanically (defensive gate + venue cancel + row
        # exited 'observable-class' so the seeder bans the family 24h), holds
        # a terminal seat, and defers an unknown one to the relay -- it never
        # cancels a seat on no evidence.  Fails closed on every read.
        try:
            _snap = getattr(self.engine, "last_venue_snapshot", None)
            _live = ({str(o.get("order_id") or "") for o in _snap.live_orders()}
                     if _snap is not None else None)
            results["actions_taken"].extend(self.obs_sweep.run_pass(live_order_ids=_live))
        except Exception as exc:
            results["actions_taken"].append(
                f"obs-sweep: ERROR {str(exc)[:120]} (fails closed -- no seat evicted "
                f"or held on an error)")

        # 1. Sync live oracle balance if credentials exist
        if self.client.has_credentials:
            ok, msg, _ = sync_kalshi_oracle(self.store, live_client=self.client)
            results["actions_taken"].append(f"Oracle Sync: {msg}")
        else:
            results["actions_taken"].append("Oracle Sync: Local/Dry mode (no live keys)")

        # 1b. OFFENSIVE RECONCILE + REQUALIFIER — BEFORE the census scan and
        # the seeder (2026-09-03).  Measured on 2026-09-02 evening: the census
        # diff (300-1,000 new listings) plus the seeder's in-cycle screen
        # (~8 min) stretched cycles to 10-25 min, so withdrawn seats waited
        # that long to re-enter and the book sagged 20 -> 15 between passes.
        # Re-entry is cheap and is what the book needs most when it is short;
        # discovery can run after it.  Every check inside still fails closed.
        results["actions_taken"].extend(self.engine.run_offensive())
        # 1c. AUTO-REQUALIFIER (2026-09-01): the codified return path from a
        # stand-down — strict measurable conditions (cooling, fresh hazard
        # verdict, wall rebuilt to >=80% of baseline), capped, attributed.
        try:
            from domains.kalshi.harness.requalifier import run_pass as _requal
            from domains.kalshi.harness.hazard_gate import HazardGate as _HG
            results["actions_taken"].extend(
                _requal(self.store, self.client,
                        self.engine.ledger, _HG(client=self.client)))
        except Exception as exc:
            results["actions_taken"].append(
                f"requalifier: ERROR {str(exc)[:120]} (fails closed — no "
                f"stood-down row returns on an error)")

        # 2. Run Dynamic Multi-Family Census Scanner with live catalog sync
        catalog_sync = self.scanner.sync_venue_catalog()
        new_cnt = catalog_sync.get("new_listings", 0)
        opps = self.scanner.scan_family_opportunities(min_hours_to_close=24.0)
        qualified = [o for o in opps if o["status"] == "QUALIFIED"]
        results["actions_taken"].append(
            f"Census Scan (Dynamic): {len(qualified)}/{len(opps)} opportunities qualified ({new_cnt} new listings discovered)"
        )

        # 2b. BLOCKER LEDGER — explicit placement state machine, every cycle.
        results["actions_taken"].append(placement_report(self.store, opps))

        # 2c. AUTO-SEEDER — maintain TARGET seats automatically when ARMED
        ps = self.store.get_placement_state()
        if ps.get("state") == "ARMED":
            results["actions_taken"].extend(self.seeder.seed_book_shortfall(target_seats=20))

        # 2d'. OFFENSIVE RECONCILE, second pass — rows the seeder just wrote
        # place in the same cycle instead of waiting a full census round.
        results["actions_taken"].extend(self.engine.run_offensive())

        # 3. Check active orders vs portfolio budget (the resolved total cap;
        #    verify/caps.TOTAL_HARD_USD = Ryan's $530 is the ceiling)
        orders = self.store.list_active_orders()
        total_collateral = sum(o.collateral_usd for o in orders)
        # The cap is PRINTED FROM THE RESOLVED POLICY, never a literal.  This
        # line read "(limit $250.00)" as a hardcoded string while the engine was
        # actually enforcing 125 and the fact said 300 — three numbers, none of
        # which agreed, and the log asserted a fourth.  A status line that
        # states a limit it does not use is worse than one that says nothing.
        from domains.kalshi.harness.placement_engine import (
            TOTAL_ESCROW_CAP_USD as _cap, TOTAL_ESCROW_CAP_SOURCE as _cap_src)
        results["actions_taken"].append(
            f"Risk Check: {len(orders)} active orders, ${total_collateral:.2f} "
            f"resting collateral (limit ${_cap:.2f} via {_cap_src})")

        # 4. Log to SQLite lane_runs
        with self.store.db.get_connection() as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS lane_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lane TEXT NOT NULL,
                    trigger TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )"""
            )
            conn.execute(
                "INSERT INTO lane_runs (lane, trigger, outcome) VALUES (?, ?, ?)",
                ("kalshi_cadence_daemon", f"cycle_{cycle_num}", f"Completed: {'; '.join(results['actions_taken'])}")
            )
            conn.commit()

        return results

    def start(self):
        # BEFORE the banner: a banner that sits in an 8 KiB buffer is exactly
        # the failure this daemon was misdiagnosed for.  This is the ONLY
        # behavioural change in start() — the loop below is untouched.
        self._configure_streams()
        self.log("══════════════════════════════════════════════════════════════")
        self.log("         KALSHI DOMAIN — AUTONOMOUS CADENCE DAEMON            ")
        self.log("══════════════════════════════════════════════════════════════")
        self.log(f"Interval: {self.interval}s | Rule: IDLE IS A BUG (Dynamic Catalog Diffing)")
        self.log(duty_cycle.armor_banner(self.armor_policy))
        self.log(hazard_gate.hazard_banner(self.hazard_policy))
        self.log("Running continuous multi-lane scanner & risk validation in background...")
        self.log("══════════════════════════════════════════════════════════════")

        cycle = 1
        try:
            while True:
                res = self.run_cycle(cycle)
                self.log(f"[{res['timestamp']}] Cycle {cycle} complete: "
                         f"{'; '.join(res['actions_taken'])}")
                if self.max_cycles and cycle >= self.max_cycles:
                    break
                cycle += 1
                self.sleep_with_rearm_sweeps(self.interval)
        except KeyboardInterrupt:
            self.log("\nKalshi Cadence Daemon stopped cleanly.")
