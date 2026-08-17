# HARDENING BUILD — 2026-08-16

Build lane against `mistake-ledger-20260816.md` §S1 / §S4, plus two `seats.py` ports.
**Nothing deployed. Nothing restarted. No byte written to the VPS.** All VPS access was `scp` read
into a temp dir that the gate then `chmod -R a-w`s.

**Suite: 268 passed, 3 skipped, EXIT CODE 0** (was 241 passed / 3 skipped = 244; now 271 collected).
`+27 tests`, `+0 regressions`. Verified by exit code, not by grep.

---

## 1. WHAT WAS BUILT

| # | Item | File | Tests |
|---|---|---|---:|
| 1 | S1-pragmatic deploy gate | `nestor-wt-lipv5/tools/lipseats/deploy_gate.sh` (new, 230 lines) | run end-to-end, both verdicts |
| 2 | S4 code-seal manifest | `nestor-wt-lipv5/tools/lipseats/seal_check.py` (`manifest generate` / `manifest verify`) | +12 |
| 2b | Baseline ratchet (enabler for #1) | same file (`--baseline`) | +5 |
| 3 | GAP GUARD port | `nestor-wt-lipv5/tools/lipseats/autoseat.py` | +10 |
| 4 | WS fill-detection spec | §5 below — **spec only, not implemented** | — |

Also new: `nestor-wt-lipv5/tools/lipseats/seal-baseline.example.json` (inactive by design),
`nestor-wt-lipv5/tools/lipseats/code-manifest.json` (the live manifest, cut 2026-08-16 00:38 MDT).

---

## 2. S1-PRAGMATIC — `deploy_gate.sh`

Replaces the ad-hoc `pytest && scp && ssh restart` chains (mistake #11). The chain's defect is not
that it is ugly — it is that `&&` is invisible: a skipped step, a `|| true`, or a grep that matched
the word "passed" inside a traceback all read as a green deploy.

Five steps, **every one gated on `$?`, never on output text**:

1. Full lipseats suite. `set -e` is deliberately disarmed around the call so the exit code can be
   *read* rather than abort the script.
2. S4 manifest generated from the tree the suite just ran, then self-verified. The suite exit code
   is written **into** the manifest, and `manifest verify` refuses anything but `0` — a hash set cut
   from a red suite can never certify a deploy downstream.
3. `scp` the VPS `protocol/seals.jsonl` + `enchiridion/work/*.md` into a temp dir, `chmod -R a-w`,
   run the S8 chain check against the copy. Copied rather than checked in place because ledger item
   10c is a confident finding read off a non-authoritative replica; this audits the authoritative
   bytes while being structurally unable to write them. **An unreachable VPS is a FAIL, not a pass.**
4. `scp -p` the five VPS trading modules, `manifest verify` against them, print the deploy delta.
5. On green: **print** the exact scp / install / verify / restart commands. It never runs the restart.

No `--force`. Flags: `--no-vps` (local half), `--require-vps-code-match` (makes step 4 fatal — the
post-install proof that the box holds the tested bytes).

**End-to-end results, run today against the live VPS:**

| run | verdict | exit |
|---|---|---:|
| `deploy_gate.sh --no-vps` | GREEN, staged commands printed | 0 |
| `deploy_gate.sh` (no baseline) | RED at step 3 — 10 live seal violations | **1** |
| `SEAL_BASELINE=…example.json deploy_gate.sh` | GREEN, 10 defects reprinted as `BASELINED — STILL BROKEN` | 0 |

Only step 5's restart was not executed, as instructed.

### 2b. Why a baseline exists (read this before approving)

The VPS chain is dirty *today* (§4). A gate that is red on every single run is the exact death S8's
own kill condition names: it gets bypassed, and a bypassed gate is worse than none. So `seal_check`
gained `--baseline`: known defects are accepted **with a written reason** and anything new blocks.

Three properties stop it becoming a laundry chute:
- Waived violations are **reprinted in full every run** under `BASELINED — accepted, STILL BROKEN`.
- A baseline entry with no `reason` is a hard load error (exit 2). *An accepted defect with no stated
  reason is just a hidden one.*
- A baseline entry whose defect got fixed becomes a `STALE_BASELINE` **failure**, so the file cannot
  accumulate cover for defects that no longer exist — nor silently pre-authorize their return.

**The baseline is shipped INACTIVE**, as `seal-baseline.example.json`. The gate looks for
`seal-baseline.json` / `$SEAL_BASELINE`; with no such file **every violation blocks**. Activating it
is a decision to deploy over 10 known-broken seal records, and that is your call, not the build's.

---

## 3. S4 — CODE-SEAL MANIFEST

`seal_check.py` now carries both halves: `check_chain` audits the artifact people **read**,
`manifest` audits the artifact that **trades**. Gemini's Round-2 line, made executable.

```
seal_check.py manifest generate --root nestor-wt-lipv5/tools --out code-manifest.json --suite-exit 0
seal_check.py manifest verify   --manifest code-manifest.json [--root /other/tree]
```

Tracked set (`DEFAULT_CODE_FILES`, relative to `tools/` so one manifest verifies here and on the VPS):
`lipseats/autoseat.py`, `lipseats/rung1.py`, `lipseats/speedgate.py`, `virgil/wire.py`,
`virgil/lip_score.py`.

Records per file: `sha256`, `bytes`, `mtime_epoch`; per manifest: `version`, `root`,
`generated_epoch`/`generated_mt`, `suite_exit`.

Five verify codes, all exit-1:
- `CODE_DRIFT` — sha on disk ≠ manifest (prints old→new size and mtime).
- `CODE_MISSING` — manifest names a file that is gone.
- `CODE_UNMANIFESTED` — a tracked module present on disk with **no manifest entry**. This closes the
  obvious attack: delete the awkward entry and verify goes green over a set someone shrank.
- `MANIFEST_SUITE_RED` — `suite_exit` is not 0 (or is absent).
- `MALFORMED_MANIFEST`.

`generate` **raises** if a tracked module is missing, rather than emitting a partial manifest.
The drift report prints the no-git warning explicitly, because that is the fact that makes it matter.

### Not implemented, as instructed — autoseat startup log-and-page on verify failure

The hook already exists in shape: `Autoseat._run_gate` / `_write_gate_manifest` run a pre-flight and
`halt()` on failure, and `ntfy_fn` is already wired for paging. The addition would be, in `preflight`
before the first cycle:

1. `seal_check.load_manifest(cfg["code_manifest"])`, then
   `verify_manifest(man, os.path.dirname(__file__) + "/..")`.
2. On any violation: `self.log("code_manifest_drift", violations=[v.as_dict() for v in vs])`, then
   `self.ntfy("autoseat REFUSING START — code drift: <file> <old8>→<new8>")`, then
   `self.halt("code_not_sealed", file=…)`. autoseat is already fail-closed on a halt file, so a
   restart with the halt present is a no-op cycle — the failure mode is "does not trade", not
   "trades wrong".
3. Config key `code_manifest` (path), plus a compiled refusal to start when the key is absent —
   otherwise deleting one config line disables the entire control.

**The stated kill condition, honestly:** this halt is cleared by hand exactly like `autoseat_halt.json`
is today. If legitimate hotfixes make hand-clearing routine, the control is dead and should be
deleted rather than kept as decoration. Recommend shipping the manifest as a *deploy-gate* check
first (done), and only moving it into startup once a month of gate runs shows the false-positive rate
is genuinely zero.

---

## 4. SEAL_CHECK / MANIFEST FINDINGS ON CURRENT LIVE DATA

Pulled read-only from `ubuntu@129.146.115.241:/home/ubuntu/senate`, 2026-08-16 00:37 MDT.
`seals.jsonl` = 22 lines; `enchiridion/work/` = 13 files.

**Seal chain: 10 violations, all real, none a sync artifact.**

| code | n | detail |
|---|---:|---|
| `DOUBLE_SEAL` | 1 | `reg-autoseat-v2-2026-08-13.md` — sealed 17:16:09 `d101eb06`, re-sealed **+65s** `c3dc2e8e`. The doc on disk matches the FIRST seal, so nothing is currently laundered; the *record* is the defect. |
| `SEALED_FILE_MISSING` | 2 | `protocol/reg-autoseat-2026-08-13.md`, `protocol/reg-rung1-2026-08-13-ballot.md` — seal `file` is a bare filename resolving to `protocol/`, while the docs live (and are separately sealed) in `enchiridion/work/`. A path-spelling defect, not missing policy. |
| `SEALED_FILE_MISSING` | 7 | the `registrations/…` ids 08-10 → 08-12. **Confirmed today: `/home/ubuntu/senate/protocol/registrations/` does not exist on the VPS at all.** The ledger called these "sealed-but-missing" from the local checkout; they are missing on the authoritative box too. |

**Code manifest vs the VPS: exactly ONE drift, and it is the pending deploy.**

```
CODE_DRIFT  lipseats/autoseat.py
    on disk 5fdcab6a != manifest 3074eccc  (99344 -> 94308 bytes)
```

`rung1.py`, `speedgate.py`, `wire.py`, `lip_score.py` are **byte-identical** between the local tree
and the VPS. The autoseat delta is 94,308 bytes on the VPS = exactly this repo's pre-edit size, i.e.
the gap-guard change and nothing else. **There is no unexplained VPS drift today.** That is the first
time that sentence has been checkable rather than assumed.

---

## 5. PORT — GAP GUARD (implemented)

Ported as **code**, not as prose — ledger item 9's specific complaint about the round-trip port.

`autoseat.py` gained module-level `next_level_behind(ladder, price)` and
`gap_check(ladder, price, max_gap_c, require_backstop=False)`, straight from
`virgil/seats.py:344-383`, with the two `SEATS_*` env knobs replaced by explicit arguments so the
bound is **config-validated** rather than whatever the service happened to be started with.

The cited measurement, in the comment at the call site and at the constant:
> MEASURED 2026-08-05: we held long YES at 23c while 1,450 contracts were bid at 2c — we were the
> only bid. A price 20c above the next real level is not JOINING a touch, it IS the market, and when
> the touch leaves there is nothing under us.

**Call site:** `Autoseat.discover`, per candidate **side**, immediately after the join price is
computed and the band / pair-sum checks pass, before sizing. Refusal:
`candidate_refused reason=gap_guard` with `side`, `price`, `next_rival`, `gap_c`, `bound_c`,
`require_backstop`.

**Config:** `gap_max_c` default **5.0** (`DEFAULT_GAP_MAX_C`, = seats.py's `MAX_GAP_C`), **only-tighten**
— `load_config` raises `ConfigError` on anything above 5.0 or ≤ 0. `gap_require_backstop` default
**false**: an empty ladder behind us is **allowed**, seats.py's own reasoning being that "quiet
low-flow books legitimately show one level and refusing them refuses the universe". Setting it true
refuses that case too.

One deliberate divergence, documented in the docstring: `PHANTOM_TICKS` (1c/99c) are **not** filtered
out of the backstop, matching seats.py. It could only matter below ~6c, which the price band already
excludes, and diverging would invent semantics the 2026-08-05 measurement never tested.

**10 tests** (`GapGuardTests`): pure-function behaviour incl. the 23c/2c incident book reproduced
exactly (gap 21.0c, refused); bound inclusivity at 5c pass / 6c fail; empty-ladder allowed and the
backstop flag flipping it; both-sides-gapped book refused with per-side receipts; single-level book
still seats; the standard 26c-over-25c fixture **seats unchanged with no gap refusal logged**; a
0.5c bound refusing the NO side while the one-level YES side survives (proves the call site reads the
*config*, not the constant); only-tighten config matrix; shipped defaults pinned; and a refused book
still feeding the sweep ledger — refusing to *seat* must never blind the storm breaker.

---

## 6. SPEC ONLY — WEBSOCKET FILL DETECTION FOR AUTOSEAT

**What seats.py has.** `virgil/ws.py` (420 lines) + `tests/test_ws.py` (308) provide the feed;
`seats.py` adds `start_ws` / `stop_ws` / `ws_service` / `_ws_key` / `_ws_remember` / `_ws_ours` /
`_ws_health` and three constants: `WS_STALE_S=120` (no proof of life this long → degraded),
`WS_MIN_CHECK_S=5` (a burst of fills is ONE adjudication, not one REST round trip per fill),
`WS_SEEN_MAX=4000` (bounded dedupe). Gated **default OFF** by `SEATS_WS_FILLS=1`; off, it must not
import ws, not open a socket, and behave byte-identically to the pre-feature path.

**The contract, from `TestWsDegradation` (6 tests) — this is the whole design in one paragraph.**
The socket is a *doorbell, never a source of truth*. `ws_service` decides nothing from the payload:
no position, no P&L, no grace counter, no blacklist. It drains, dedupes, logs `ws_fill_seen`, and —
if a fill is ours — calls the **existing** `check_fills()`, which recomputes everything from the REST
orders and positions endpoints. One writer, and it reads the exchange. Hence the four degradation
guarantees the tests pin: a quiet socket logs `ws_degraded` **edge-triggered** (once, then
`ws_recovered`); `alive_flag=False` is degraded; a dead socket **still gets the fill by poll** —
evict, blacklist and book identically; and a drain that raises logs `ws_drain_failed` and never
breaks the cycle, with the poll carrying it. Plus replay safety: a reconnect re-delivering a fill
logs `ws_fill_repeat` and rings nothing twice.

**What porting would take.** ~6–8h. `ws.py` is already tool-agnostic and would be imported, not
copied (the fix for item 9, applied for once). The autoseat-side work: (a) `ws_fills_enabled()`
equivalent as a config key rather than an env var, defaulting off; (b) `ws_service` translated to
autoseat's coid space — `owns()` / `EXIT_COID_PREFIX`, since autoseat must ring on **seat** fills and
also on **exit** fills, which seats.py handles through its roundtrip record; (c) a call at the top of
`cycle()` plus a between-cycle service tick, autoseat having no event loop today; (d) the `halted()`
short-circuit and the `WS_MIN_CHECK_S` floor, both non-negotiable on a shared account; (e) porting
the degradation suite verbatim — those six tests **are** the spec.

**What the lag costs, honestly.** Measured on the 08-15 incident
(`fill-forensics-20260815.md:335-339`), against a 900s cycle: fills at 04:25 / 05:30 / 14:09 / 17:51
were logged at 04:25:59 / 05:40:12 / 14:19:37 / **19:00:34** — 1, 10, 10.6 and **69 minutes**. Three
of four sit inside one poll period; the outlier does **not**, which means the 69 minutes was a
stalled or skipped cycle, not poll granularity. That matters for the decision: a socket would have
caught the outlier (`ws_service` triggers `check_fills` directly), but a stalled cycle loop is a
different bug and deserves its own watchdog, which is cheaper than a websocket.

**Versus the round-trip exit's value.** The exit is what the lag delays. Measured (n=3,011 positions,
11 exit policies): resting the reducing quote at the rival touch until it fills scores **+3.26c/ct**
(sd 8.75, 92.8% completed) vs hold-to-settlement **+2.64c/ct** (sd 33.53, worst −98c). At the current
compiled size — one seat, $50, ~192 contracts at 26c — the mean edge is **+0.62c × 192 ≈ $1.19 per
completed round trip**, and the real prize is the variance: sd 33.53 → 8.75, worst case −98c/ct
(≈ −$188 on 192 contracts) → −$16.8. Faster detection does not change either number; it only shortens
the window in which we hold inventory *without* a working exit and repeg from a stale touch.

**Recommendation: DO NOT PORT YET.** At `max_seats=1` the expected saving is a fraction of $1.19 per
fill, on ~4 fills/month, against 6–8h and a new always-on network dependency on a box with no git and
no CI. The cheap 80% is (i) a cycle watchdog that pages when no `cycle_start` has been logged in
`2 × cycle_s` — which is what actually failed on 08-15 — and (ii) shortening `cycle_s` on a market
carrying inventory. Revisit the socket when `max_seats > 1` is sealed, at which point the per-fill
saving scales and the fixed cost does not.

---

## 7. STAGED DEPLOY — FOR YOUR REVIEW

Nothing below has been run. Reproduce the gate yourself first:

```bash
cd /Users/ryanwhitehead/Documents/senate/nestor-wt-lipv5/tools/lipseats
./deploy_gate.sh                 # expect RED: 10 live seal violations (§4)
SEAL_BASELINE="$PWD/seal-baseline.example.json" ./deploy_gate.sh   # expect GREEN
```

Decisions I need from you, in order:

1. **Activate the baseline?** `cp seal-baseline.example.json seal-baseline.json` accepts the 10
   defects in §4 with reasons on record. Without it the gate is permanently red and will be bypassed.
   The alternative — fixing the chain first (delete the 7 phantom `registrations/` seals, correct the
   2 bare-filename paths, add a `supersedes` field for the double-seal) — is the better answer and is
   maybe 1h of work on the VPS. **I did not touch the chain.**
2. **Ship the gap guard?** It is a pure subtraction: it can only refuse candidates, never place one.
   Blast radius at `max_seats=1` is one seat.
3. Then run the printed step-1 scp block, the step-2 `manifest verify` proof, and only then step 3's
   restart. The gate prints all of them verbatim on a green run.

Files:
- `/Users/ryanwhitehead/Documents/senate/nestor-wt-lipv5/tools/lipseats/deploy_gate.sh`
- `/Users/ryanwhitehead/Documents/senate/nestor-wt-lipv5/tools/lipseats/seal_check.py`
- `/Users/ryanwhitehead/Documents/senate/nestor-wt-lipv5/tools/lipseats/seal-baseline.example.json`
- `/Users/ryanwhitehead/Documents/senate/nestor-wt-lipv5/tools/lipseats/code-manifest.json`
- `/Users/ryanwhitehead/Documents/senate/nestor-wt-lipv5/tools/lipseats/autoseat.py`
- `/Users/ryanwhitehead/Documents/senate/nestor-wt-lipv5/tools/lipseats/tests/test_autoseat.py`
- `/Users/ryanwhitehead/Documents/senate/nestor-wt-lipv5/tools/lipseats/tests/test_seal_check.py`

*Read-only against the VPS throughout. No service restarted, no seal appended, no chain repaired.*
