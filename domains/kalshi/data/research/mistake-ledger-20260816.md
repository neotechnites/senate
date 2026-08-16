# MISTAKE LEDGER — 2026-08-16

Lane 3. Every known loss and process mistake, converted (or not) into a framework impossibility.
Adversarial partner: Gemini 2.5 Pro, 2 rounds, transcript condensed in §4.

**Verdict up front: IMPOSSIBLE 0 / MITIGATED 2 / OPEN 8.** Not one of the ten mistakes is closed
by a mechanism that runs. The org has written ~13,000 lines of Python controls and put the
enforcing half of them in `archive/`.

---

## 0. THE STRUCTURAL FINDING

Everything below is downstream of three facts established today against the live VPS:

1. **CI runs `cargo` only.** `nestor-wt-lipv5/.github/workflows/ci.yml` runs fmt/clippy/test/build
   for the Rust crates. There is no pytest job anywhere in the repo. Every Python control —
   `lipseats/tests/` (2,857 lines), `lip_maker_v4` (~4,500), `lip_v5/tests/` (22 files),
   `domains/kalshi/tests/` (5 files) — runs only when a human types `pytest`.
2. **Zero `.py` files are sealed.** `protocol/seals.jsonl` on the VPS holds 20 seals, all markdown
   registrations. `enforce_gate.py`, `autoseat.py`, `wire.py` are unsealed. The gate verifies the
   *policy* and never the *code that enforces the policy*.
3. **`/home/ubuntu/senate` on the VPS is not a git repository** (`fatal: not a git repository`).
   An edit to `enforce_gate.py` or `autoseat.py` leaves no trace but mtime. There is no
   after-the-fact detection, let alone prevention.

Gemini's Round-2 formulation, which is the thesis of this document:

> "The artifact people audit (prose) and the artifact that trades (code) are dangerously decoupled."

The one genuinely compiled control found: `autoseat.py` hard-codes `HARD_MAX_SEATS = 1` (L154),
`$250` total / `$50` per-market ceilings, and raises `ConfigError` at load if a config tries to
weaken `fill_suspend_count` / `fill_suspend_window_s` (L318-334). A config file **cannot** loosen a
reg floor; the service refuses to start. That pattern is correct and is the template for everything
in §3.

---

## 1. TRADING LOSSES — venue truth, pulled live 2026-08-15/16

Signed reads via `virgil/wire.py` (`load_auth` → `KalshiClient`), key `3a1d2ead…`.

**Account state.** Balance `$1,011.83`; portfolio value `$1,872` (cents). 1,540 fills spanning
2026-06-17 → 2026-08-15 (630 taker / 910 maker). 313 settlements, 2026-06-19 → 2026-08-14.

**Realized P&L by family** from paginated `/portfolio/positions` (17 markets carrying rows):

| family | realized | fees | traded | n |
|---|---:|---:|---:|---:|
| KXSTATEBALLOTMEASURE | -34.43 | 6.79 | 828.35 | 4 |
| KXBILLSCOUNT | -15.00 | 0.94 | 115.00 | 1 |
| KXTRUMPSAYMONTH | -12.44 | 2.43 | 195.44 | 2 |
| KXJUDGECOUNT | -8.88 | 0.08 | 119.88 | 1 |
| KXROLEINPRODUCTIONDOOMSDAY | -3.64 | 3.40 | 236.64 | 3 |
| KXNEXTMANAGERMLB | -0.41 | 0.11 | 28.84 | 1 |
| KXPRIMARYPLACE | +0.17 | 0.21 | 16.83 | 1 |
| KXCPIYOY | +0.22 | 0.22 | 10.78 | 3 |
| KXPIRROOUT | +20.91 | 0.75 | 30.09 | 1 |
| **TOTAL** | **-53.50** | **14.92** | **1,581.85** | **17** |

Open: `KXSTATEBALLOTMEASURE-KY-A1`, -156.00 contracts, `$49.92` exposure.

**Two receipted figures do not reconcile with venue truth and must not be re-quoted as-is:**

- `TRUMPSAYMONTH -$12.44` ✅ exact venue match — but **no file on disk states it.** Same for
  `JUDGECOUNT -$8.88` ✅ exact venue match, **no disk receipt.** Both figures were in circulation with
  their only provenance being the venue itself; I confirmed them independently today. `BILLSCOUNT
  -$15` ✅ matches venue and is receipted at `archive/enchiridion_legacy/work/account-truth-2026-08-06.md:29`.
- `ROLEINPRODUCTION -$61.02` ❌ **CONFLICT.** Receipted at `family-census-20260815.md:268` —
  *"−$61.02 over 3 markets / 13 fills — maker fills at 0.31/0.72/0.64, then all three flattened as
  taker."* Venue `realized_pnl_dollars` says **-$3.64** across the same 3 markets ($236.64 traded,
  $3.40 fees). A 17× gap. One of the two is a different quantity (most likely a fills-level
  round-trip reconstruction vs the venue's own realized field), and **no code exists that can
  adjudicate it** — which is the whole point of specs S3/S7 below. Do not re-quote either figure
  without rebuilding it.
- ballot incident `-$81` ❌ **explained, and it mixes realized with mark-to-market.** Itemized at
  `ballot-base-rate-gate-20260815.md:47-53`: *"GA-A2 −17.11 / AR-A578 −13.41 / IA-A1 −10.70 / KY-A1
  **−39.78 (open)** → TOTAL −81.00."* Venue: **-$34.43 realized** + KY-A1 still open at `$49.92`
  exposure, -156 contracts. The −$39.78 is an unrealized mark quoted inside a total presented as a
  loss. Directionally right, but it is not $81 of realized loss.
- `-$1,197.65 / 2mo` taker exhaust — **not verifiable from `/portfolio/positions`**. That endpoint
  prunes fully-settled markets; total traded there is only $1,581.85 against 1,540 lifetime fills.
  It is receipted in prose at `ideation-burst-20260815.md:19` — *"we are −8.4c/fill on n=595
  (t ≈ −4.2), −$1,197.65 over two months"* — with band detail at `:39` (*"0–10c band, 10,573
  contracts, win rate 0.000, −$404.30; 20–30c band −$398.88 (−19.1c/ct)"*). The figure has to come
  from a fills/settlement reconstruction that no longer exists as runnable code, so it cannot
  currently be re-derived. Given n=595 and t≈−4.2 the *effect* is solid; the *dollar total* is
  unreproducible.

**LIVE NEAR-MISS, this lane, mistake #10 reproducing itself.** I attempted that reconstruction from
`/portfolio/settlements` and computed **-$11,679.55** lifetime. The account balance is $1,011.83, so
the number is impossible. Cause: I assumed `revenue` was cents and `yes_count_fp`/`no_count_fp` were
*held* contracts. They are *cumulative traded* counts, so every hedged row double-counts cost —
e.g. `KXYTVIEWSW-DRA26AUG09-12.25M` shows yes_count 130 **and** no_count 130 with `revenue: 0`
despite `market_result: yes`, because the net position was flat. Nothing compiled would have caught
this. I caught it with a plausibility check against balance, by hand. That is exactly the control
that does not exist.

**Also found while doing it:** `virgil/wire.py:299` —

```python
def get_settlements(self):
    return self._signed("GET", "/portfolio/settlements")    # lip_v5/exchange.py:74
```

A bare one-page call returning **100 of 313** rows, while its siblings `get_positions` (L243) and
`get_fills` (L270) both carry 50-iteration cursor loops with docstrings explaining that the
unpaginated read "was the same defect R3 already fixed for get_orders." **The lesson was ported
twice inside one file and skipped the third method.** This is item 9 recurring, live, today.

---

## 2. THE TEN — classification

Strict rule in force: *"someone remembers"* or *"we wrote it in a doc"* = **OPEN**.

### 1. reg-autoseat-v2c sealed but not deployed — **OPEN**
`reg-autoseat-v2c-2026-08-14.md` fixed a kill switch that could never fire: `reconcile()`'s
gone-order branch never queried `/portfolio/fills`, so the promised ">=2 fills / 7d → SUSPEND"
criterion "had nothing to count… the kill criterion was prose, not code."
Receipts, and the timeline is worse than logged. Doc authored **2026-08-14**; seal record
`"sealed_mt": "2026-08-15 09:36:05 MDT"` = **15:36 UTC, ~19h late**; incident fills at **04:25,
05:30, 14:09 and 17:51 UTC on 08-15** (4 NO maker fills GA-A2 / AR-A578 / IA-A1 / KY-A1, $199.69
escrow). **Three of the four fills preceded even the seal**, and `autoseat.py` mtime is
**2026-08-15 23:14:34 UTC** — the remediation *code* postdates the last fill by 5h23m and the first
by ~19h. Memory receipt: *"reg-autoseat-v2c killswitch fix was AUTHORED 08-14 but never
sealed/deployed — production ran v2.2 with the broken ≥2-fills/7d suspend."* The fix is present now
(`get_fills` L689, `_check_fill_suspend` L760-779).
Why OPEN: I ran the obvious seal-diff across the 11 regs on the **VPS** — every one matches its seal
hash, zero drift. The obvious check finds nothing while the incident happens anyway. Seal integrity
is compiled (`rung1.py::registration_ok` L375 → `halt("registration_not_sealed")` L508;
`protocol/gate/enforce_gate.py::check_registration_seal` L73 raises TAMPER DETECTED).
Seal-implies-deployed is enforced by nothing. Seal-to-deploy latency is measured by nothing.

**Two further seal defects found on the local chain** (which diverges from the VPS — see item 10c):
- **Authored-but-unsealed regs do exist locally:** `reg-polyus-score-unit-dollar.md`,
  `reg-polyus-score-unit-dollar-2.md`, `reg-addendum-slip-live-lip-credit-probe-2026-08-12.md`.
  Conversely 7 `registrations/…` ids (08-10 → 08-12) are **sealed-but-missing** — no such file exists
  anywhere under `senate/`. And every v3-series seal is absent locally, existing only on the VPS, so
  **the local reg chain cannot verify the deployed policy at all.**
- **The append-a-new-seal loophole.** `reg-autoseat-v2-2026-08-13.md` was sealed at 17:16:09 (sha
  `d101eb06`) and **re-sealed 65 seconds later at 17:17:14 with a different sha** (`c3dc2e8e`) — a
  sealed doc was edited, and a second seal record legitimized the edit. Because
  `check_registration_seal` matches the current sha against *a* record in `seals.jsonl`, appending a
  fresh seal after editing always passes. "Nothing below this line may be edited after sealing" is
  enforced only by the honour system. This is Gemini's *Sealed Poison Pill* with a live instance.

### 2. Fabricated provenance in `data/sources/lip_decay_spec.json` — **OPEN**
Cited a URL that 404s on a retired host, stamped `verified_at`. Now self-documenting:
`"citation was fabricated though the 5000 bps value is correct."` Corrected by hand.
Only mechanism: `domains/kalshi/tests/test_oracle_and_seats.py::test_zero_seed_money_invariant`
asserts `Path(f.source_artifact).exists()` — local file existence, not URL liveness, not schema,
not staleness. No JSON-schema validator over `data/sources/` exists. Gemini's Round-1 dispute
(accepted): a corrected fact is documentation; unvalidated data consumption stays OPEN.

### 3. Local SQLite vs venue truth — **MITIGATED (autoseat) / OPEN (domains/kalshi)**
autoseat has a real runtime reconciler: `autoseat.py::Autoseat.reconcile` (L604) treats
`/portfolio/orders` as truth and classifies a vanish against `/portfolio/fills` before quarantine,
with six pinning tests (`test_vanished_with_matching_fill_is_classified_and_counted`,
`test_taker_fill_is_not_our_maker_seat`, `test_vanished_without_fill_stays_gone_unexplained`,
`test_unreadable_fills_do_not_false_suspend`, `test_orphan_with_our_prefix_is_adopted`,
`test_gone_order_quarantines_market`). MITIGATED not IMPOSSIBLE because **those tests are in no CI
job** and can regress silently.
`domains/kalshi` has none: `harness/venue_client.py:134` exposes `list_open_orders()` (`?status=resting`)
and **nothing calls it against the DB**. `state/fact_store.py:126` reads `active_orders WHERE
status='RESTING'` purely locally; `interface/cli.py:175` writes `status="RESTING"` from CLI args;
`verify/invariants.py:87` sums local `collateral_usd` with no venue cross-check. Zero reconciler,
zero side-label check — the exact configuration that produced the 4-phantom-RESTING-orders episode.
Receipt: `terminal-taker-spec-20260815.md:12` — *"Our own DB `active_orders` mislabels these as
`side: 'yes'` at the NO price… Order `7102964c-…` reads `side='yes', price=0.32` … while the venue
fill reads `no_price_dollars: "0.3200", outcome_side: "no"`."*
**STILL BROKEN ON DISK RIGHT NOW.** `kalshi_domain.db::active_orders` holds 4 rows (KY-A1, RI-Q4,
AL-A4, NC-A2) with `side = 'yes'`, `status = CANCELED_BY_RYAN_INCIDENT`, `updated_at
2026-08-15T18:10:00Z`. The *status* was reconciled; **the side labels never were.** The half-fix is
itself the finding: the reconciliation was done by hand, by memory, and it missed a column.

### 4. Oracle read $0.00 during a $199.69 drawdown — **OPEN (fake-fixed)**
Confirmed live: `get_positions()` returns a **tuple** `(status, body)` and the body key is
`market_positions`, not `positions`. A consumer reading the wrong shape silently gets zero.
`harness/oracle_sync.py:29` guards `balance` only. The documented fix was
`raw_bal.get("portfolio_value", raw_bal.get("payout", 0))`.
**The test written for this incident does not test it.**
`tests/test_oracle_and_seats.py::test_oracle_sync_with_live_client` feeds a mock containing `payout`
and **no** `portfolio_value`, then asserts `open_positions_usd == 100.00` — it passes entirely
through the legacy fallback branch. Delete the fix and the test still goes green. No non-zero
assertion on any portfolio response exists.

### 5. Fee fact wrong (whole-cent vs 1/100-cent ceil) — **OPEN, and worse than logged**
**Four** independent `taker_fee_usd` implementations, **three** rounding rules:

| file | rounding | rate | pinning test |
|---|---|---|---|
| `tools/tapemine/fees.py::taker_fee_usd` L93 | ceil to $0.0001 ✅ venue | 0.07 × series mult | `test_tapemine.py:44,117` |
| `tools/lip_v5/cutover.py::taker_fee_usd` L362 | ceil to whole cent | `C.TAKER_FEE_RATE` | `test_cutover.py:426` |
| `tools/lip_maker_v4/lip_maker_v4.py::taker_fee_usd` L1624 | ceil to whole cent | `TAKER_FEE_RATE` | `test_lip_maker_v4.py:395-396` |
| `tools/pmus/score.py::taker_fee_usd` L111 | bankers_round_cents | **0.06** | `test_pmus.py:876` |

Plus Rust `crates/engine/src/risk.rs::taker_fee`. Each has its own golden vector; **no test compares
any implementation to any other**. A 1-contract 50c fill books $0.02 vs $0.0175 actual — a 14%
overstatement — and `lip_v5`'s own docstring concedes it "biases the hold-vs-cross comparison toward
HOLDING." `domains/kalshi` has no fee code at all, only
`"taker_formula": "ceil(0.07 * count * price * (1 - price))"` with unstated units.

**This is a REGRESSION, not a first offence.** `archive/enchiridion_legacy/work/review-nestor-reality.md:219`,
dated **2026-07**: *"`taker_fee` ceils to the whole cent; our own demo probe proved Kalshi ceils to
$0.0001."* Known and corrected a month before it was rediscovered on 08-15 from the venue receipt
(`terminal-taker-spec-20260815.md:32`: *"277 @ 0.14 → billed **2.3346**"* — the same fill I re-pulled
in §1).
**And it is STILL WRONG ON DISK.** The fact store was patched (`fact_history` key
`kalshi.fees.structure` → `ceil_to_hundredth_cent(...)`, `2026-08-15 20:31:38`, source
`venue_receipt:/portfolio/fills`), but `data/sources/fee_schedule.json` — the artifact
`state/seed.py:36` actually reads — is **unpatched**, still carrying the old `taker_formula` and
`"verified_at": "2026-08-14T17:00:00Z"`. Same shape as item 3: the *derived* copy was corrected and
the *source* artifact was not. A fact/artifact divergence is live at the time of writing.

### 6. A head answered "do fills cluster near window close?" with NO, against the tape — **OPEN**
The claim: `terminal-taker-spec-20260815.md:36` — *"Q2 — Do stale quotes persist near window close?
**NO. Census says zero.**"*, and `:88` — *"Window-close concentration is also absent… **No terminal-
window effect.**"* Against the tape: `temp-hourly-census-20260815.md:194` — ***"49.3% of fills land
in the final third of the hour vs 33.3% uniform"***; and all four 08-15 incident fills landed inside
T-24h of the weekly close. The NO rested on n=33 vs n=26 buckets in a series the same file calls
*"an effective sample size of about one"* (`:159`).
Nothing forces an empirical claim to be answered from the tape. `verify/base_rates.py` hardcodes
`historical_yes_prob: 0.76 / 0.68 / 0.82` under a comment crediting "Ballotpedia, NOAA, BLS, FOMC
archives" — no artifact, no source file, not among the 6 seeded facts. Its test asserts the
violation string contains `"76%"`: **it pins the constant to a copy of itself.** The constant could
be entirely invented and the suite is green.
Worse: `data/research/fill-forensics-20260815.md:319` concedes "the curfew alone would not have
stopped the overnight cluster" — a finding that **contradicts the compiled 24h curfew** — and no
test reads that file. All captured tape (`terminal_capture_20260815.jsonl`, `fills_all_20260815.json`,
`trades_all_ballot_20260815.json`) is inert; no test in `domains/kalshi/tests/` consumes any of it.

### 7. YTVIEWS "-$0.44 loss" was a `fee_cost` misread — **OPEN**
Sign and magnitude both wrong; true realized +$120.96. Engine-side the lesson *was* learned —
`lip_v5/engine.py:703-705` prefers the wire's `fee_cost` over the estimate, pinned by
`test_note52.py::test_a_charged_fee_is_booked_from_fee_cost`; Rust stamps
`fee_basis: "exchange_fee_cost"` (`crates/streak/src/strategy.rs:2656`). None of that reaches prose.
The only thing that ever policed a research brief was
`archive/protocol_legacy/honesty/citation_verifier.py` — resolves a cited artifact, checks freshness,
checks the content supports the claim class. **Archived, unwired** (`settings.json` = `{"hooks": {}}`),
and its `_repo_senate() = parents[2]` now resolves into `archive/`, so its paths are broken.

### 8. Base-rate gate nearly compiled from a wrong causal story — **OPEN** (was MITIGATED; Gemini's dispute accepted)
Preregistration caught it. But `archive/protocol_legacy/prereg.py` (`new`/`seal`/`verify`, with
`REQUIRED_SECTIONS` = HYPOTHESIS / DATA THAT DOES NOT EXIST YET / KILL CRITERION) is **archived and
unenforced — no hook, no CI job, no caller.** It worked because a human chose to write a prereg.
Gemini: *"Preregistration is a manual discipline, not a compiled enforcement."* Correct.
The catch itself is well receipted — `ballot-base-rate-gate-20260815.md` P1 **FAIL** / P2 PARTIAL /
P3 **FAIL, sign inverted**; *"Refining the prior inverts it… AUC 0.25 — worse than a coin"*; and the
money line at `:334`: ***"Compiling a wrong causal story is worse than no gate: this one would have
told us GA-A2 was the safest of the eight NO seats."***
**Open downstream defect, unresolved:** the falsified gate was already written into Ryan's Senate 2.0
constitution as Rule 2. Per memory, it was *"flagged to him with receipt; enforcing as written
(safe-direction) pending his rev."* A refuted causal story is currently live in the governing
document. Nothing propagates a retraction from a brief back into a constitution.

### 9. Lessons unported between bots — **OPEN**
Both artifacts located. ORIGINAL: `tools/virgil/seats.py:135-156`, **measured 2026-08-05** —
*"MEASURED on our own book tape (n=3,011 positions, 1,292 settled markets)… EVERY stop-loss tested
was significantly WORSE than holding (t = −5.9 to −6.9)"* and *"The round trip's reducing quote IS
the seat's own order… WEN-FROS killed by the LAGGARD CULL 11 min after the round trip opened."*
REBUILT 10 days later: `tools/lipseats/autoseat.py:174-190` (mtime 2026-08-15 17:12) — *"ROUND-TRIP-
ON-FILL (reg-autoseat-v3c) — **ported from virgil/seats.py**, whose own-book backtest (n=3,011
positions, 11 exit policies) measured…"*. The identical Aug-5 lesson, re-derived after paying for it
again, and the port is a **copy of the prose**, not an import of the code.
There is exactly one `seats.py` (`tools/virgil/seats.py`, 243 KB) plus a stale `seats.py.orig`;
round-trip logic (`rt_capital_econ` L219, `roundtrip_price` L344, `self.roundtrips` L1569) is
single-copy but **not shared** — no other tool imports it. No `common/`, `shared/`, or `lib/`.
Cross-tool reuse is ad-hoc module-level imports (`autoseat.py:102-104` → `rung1`, `speedgate`,
`virgil.lip_score`). The fee table in item 5 is the proof of the gap; `get_settlements` in §1 is the
proof that it recurs *inside a single file*.

### 10. Subagent numbers propagated without primary verification — **OPEN**
(a) Ballot LIP accrual reported as `$2.04/day per $100` — accrual divided by calendar window instead
of earning time. Truth from primary logs: **$7.89/day per $100** (43.5h span, $249.72 max escrow,
$35.75 accrued). The head repeated it to Ryan *and* briefed a third agent with it.
(b) = item 7.
(c) **This lane, twice.** My own -$11,679.55 (§1). And an auditor reading the local Mac checkout
concluded `reg-autoseat-v3` "was never sealed" — on the VPS it exists, is sealed, and hash-matches.
A confident finding from a non-authoritative replica.
The failure mode is specific and nasty: **the $2.04 figure was arithmetically valid.** It divided by
the wrong denominator. Any checker that verifies "a number carries a citation" passes it.

---

## 3. COMPILED PREVENTION SPECS — spec only, nothing built

Ranked by (loss prevented / effort). Effort in engineer-hours, honest, including the false-positive
tail: *a check that cries wolf gets disabled, and a disabled check is worse than none.*

### S1 — PYTEST IN CI, GATING DEPLOY  ★ build first
- **Closes:** nothing by itself. **Makes every other spec on this list load-bearing instead of decorative.**
- **Mechanism:** add a `python` job to `nestor-wt-lipv5/.github/workflows/ci.yml` running `pytest`
  across `tools/*/tests/` and `domains/kalshi/tests/`; make `deploy.yml` `needs:` it and drop the
  `|| true` that currently swallows a failed `systemctl restart`.
- **Files:** `.github/workflows/ci.yml`, `.github/workflows/deploy.yml`, new root `pytest.ini`.
- **Effort:** 8h — ~2h of wiring, ~6h fixing the tests that will immediately fail (see item 4's
  fallback-branch test and item 6's self-pinning assertion; both are green today and shouldn't be).
- **Loss prevented:** multiplier, not an addend. Converts 13,000 existing lines from ornament to control.
- **Kill condition:** flaky enough to block a valid deploy more than once a week — at which point it
  gets bypassed and is worse than nothing.

### S2 — UNPAGINATED-READ LINT  ★ highest ratio
- **Closes:** 9 (recurrence), Gemini's *API Pagination Regression*.
- **Mechanism:** AST test walking `virgil/wire.py`; any method calling `self._signed("GET", …)` on a
  list endpoint (`/portfolio/*`, `/markets`, `/events`) must contain a `cursor` loop. Raise
  `AssertionError("unpaginated list read: <method>")`.
- **File:** new `tools/virgil/tests/test_wire_pagination.py`.
- **Effort:** 2h.
- **Loss prevented:** unpriced but it **fails today** — `get_settlements` returns 100 of 313 rows,
  and `get_positions`' own docstring spells out the consequence: a truncated page "does not merely
  hide a position — it deletes that position's cost basis from `committed_capital()` and hands the
  engine budget it does not have." That is an over-deployment bug with the account's full balance
  ($1,011.83) as its ceiling.
- **Kill condition:** a legitimate single-page endpoint that the AST cannot distinguish, forcing an
  allowlist that grows past ~3 entries.

### S3 — FEE GOLDEN-VECTOR CROSS-CHECK  ★ free ground truth
- **Closes:** 5, 7 (partly).
- **Mechanism:** one test importing all four `taker_fee_usd` plus the Rust `taker_fee`, asserting
  agreement to $0.0001 against vectors **built from the venue's own `fee_cost` field on real fills**.
- **File:** new `tools/tests/test_fee_parity.py`; fixture from `/portfolio/fills`.
- **Effort:** 4h. Cheap because the ground truth is already on the wire: **1,540 real fills, each
  carrying an authoritative `fee_cost`** (e.g. the AR-A578 fill, `count_fp 277.00` at
  `no_price_dollars 0.1400`, `fee_cost 2.334600`). No data sourcing needed; the corpus is free.
- **Loss prevented:** a share of the **$1,197.65 / 2mo** taker exhaust. A 14% fee overstatement that
  admits to biasing hold-vs-cross toward HOLDING is a direct contributor to taker bleed; three of
  four implementations are wrong against the venue.
- **Kill condition:** the four implementations turn out to model genuinely different fee contexts
  (maker vs taker vs series multiplier), making a single invariant undefinable.

### S4 — CODE-SEAL MANIFEST (seal the artifact that trades, not the one people read)
- **Closes:** 1, Gemini's *Gate-Script Drift*, *Sealed Poison Pill* (partly).
- **Mechanism:** extend `protocol/seals.jsonl` to seal `.py` files. Each reg declares the sha256 of
  the source files implementing it. `autoseat`/`rung1` preflight hashes **its own `__file__`** and
  every declared module, and `halt("code_not_sealed", file=…)` on mismatch. CI recomputes the same
  set pre-deploy.
- **Files:** `protocol/gate/enforce_gate.py` (extend `check_registration_seal`),
  `tools/lipseats/autoseat.py::preflight`, `.github/workflows/deploy.yml`.
- **Effort:** 6h.
- **Loss prevented:** **$199.69** (item 1 directly — a seal-to-deploy check surfaces a sealed-but-
  unshipped remediation), plus the untracked-code tail. Note this is the *only* spec addressing the
  no-git-on-VPS exposure, where an edit to `enforce_gate.py` currently leaves no trace but mtime.
- **Kill condition:** legitimate hotfixes get blocked often enough that the halt is routinely cleared
  by hand — the same death `autoseat_halt.json` is already vulnerable to.

### S5 — VENUE-TRUTH RECONCILER FOR `domains/kalshi`
- **Closes:** 3 (kalshi side), 4.
- **Mechanism:** periodic + preflight job diffing local `active_orders` against
  `venue_client.list_open_orders()` on order_id, **side label**, price and count; any drift raises
  `VenueDriftError` and halts the gate. Adds a schema assertion that portfolio reads carry
  `market_positions`/`portfolio_value` and that a non-zero exposure never renders as $0.00.
- **Files:** new `domains/kalshi/harness/reconcile.py`; assertion into `harness/oracle_sync.py`;
  call site in `harness/gate.py::ExecutionGate.execute_action`.
- **Effort:** 5h.
- **Loss prevented:** **$199.69** (blind oracle during the drawdown) + **$81** ballot incident;
  removes the phantom-RESTING-orders class entirely.
- **Kill condition:** venue eventual-consistency produces drift alarms on in-flight orders that a
  settle-time tolerance can't absorb.

### S6 — PROVENANCE CHECKER OVER `data/sources/`
- **Closes:** 2, Gemini's *Stale Fact Poisoning*.
- **Mechanism:** CI test over every `data/sources/*.json`: JSON-schema (required `source`,
  `verified_at`, a value field), HTTP GET each `source` URL expecting 2xx, and fail if
  `now - verified_at > max_age`. Raise `ProvenanceError(file, url, status)`.
- **File:** new `domains/kalshi/tests/test_source_provenance.py`.
- **Effort:** 3h (+1h for an offline-cache mode so a network blip doesn't red the build — this is
  the false-positive tail that would otherwise get it disabled).
- **Loss prevented:** unpriced. It is the exact and only check that catches item 2, which shipped a
  404 citation stamped `verified_at` into the fact store consumed by pricing.
- **Kill condition:** venue doc URLs churn faster than the max_age window, making red the steady state.

### S7 — FIGURE SIDECAR WITH RE-EVALUATED DERIVATION
- **Closes:** 7, 10, Gemini's *Subagent Data Laundering*, *Persuasive Hallucination Pipeline*.
- **Mechanism:** every brief ships `<brief>.figures.json`; each entry is
  `{value, source: endpoint|file, field, numerator, denominator, expression}`. A checker
  **re-evaluates `expression` and compares to `value`**, and fails if any figure in the prose is
  absent from the sidecar.
- **File:** new `domains/kalshi/tests/test_brief_figures.py`.
- **Effort:** 10h.
- **Loss prevented:** the un-priced tail — a wrong number reaching Ryan and driving a capital
  decision. Realized instances: the $2.04 vs $7.89 accrual rate (3.9× understatement of the strategy
  actually being scaled), the YTVIEWS -$0.44 vs +$120.96 sign error, my own -$11,679.55.
- **Kill condition:** authors satisfy the schema with `expression: "value"` self-references — at
  which point it has become the vanity check Gemini warns about and should be deleted.
- **Honest limit (this is Gemini's attack, and it lands):** see §4.

### S8 — SEAL-CHAIN INTEGRITY CHECKER  ★ cheapest on the list
- **Closes:** 1 (the three defects found today), Gemini's *Sealed Poison Pill*.
- **Mechanism:** one test over `protocol/seals.jsonl` asserting (a) every authored `reg-*.md` has a
  seal, (b) every seal's file exists, (c) **no file has two seal records with different shas** —
  closing the append-a-new-seal-after-editing loophole, (d) local and VPS `seals.jsonl` agree.
  Raise `SealChainError(file, reason)`.
- **File:** new `domains/kalshi/tests/test_seal_chain.py`.
- **Effort:** 2h.
- **Loss prevented:** unpriced, but it **fails today on four counts**: 3 unsealed regs, 7
  sealed-but-missing files, the `reg-autoseat-v2-2026-08-13.md` double-seal with divergent shas, and
  a local chain missing the entire v3 series. Until (d) passes, the local checkout cannot verify what
  is actually trading.
- **Kill condition:** the double-seal rule blocks a legitimate re-seal workflow that the org actually
  wants (in which case, make re-sealing explicit with a `supersedes` field rather than deleting the check).

**RANK by (loss prevented / effort):** S1 (enabler, must be first) → S2 (2h, fails today) →
S8 (2h, fails today on four counts) → S3 (4h, free corpus, largest priced loss) → S6 (3h, unpriced
but sole coverage, and item 5 is live-wrong on disk) → S5 (5h, $280.69) → S4 (6h, $199.69 +
untracked-code tail) → S7 (10h, largest tail, weakest guarantee).

Total: **40 engineer-hours** to convert 8 OPEN items into mechanisms that run.

**Three things are wrong on disk right now** and want a hand-fix before any of this:
`data/sources/fee_schedule.json` still carries the superseded whole-cent formula (item 5);
`kalshi_domain.db::active_orders` still carries 4 rows with inverted `side` labels (item 3);
`virgil/wire.py::get_settlements` still reads one page of three (item 9).

---

## 4. GEMINI TRANSCRIPT (condensed)

CLI `~/.nvm/versions/node/v20.9.0/bin/gemini`, model `gemini-2.5-pro`, 2 rounds.
Prompts/outputs: `…/scratchpad/{g1,g2}.{txt,out.txt}`.

### Round 1 — (a) dispute classifications

> **5. MITIGATED → OPEN.** "A corrected JSON fact is documentation; the risk is unvalidated data
> consumption, which is not mitigated until a compiled process verifies that fact against a primary
> source."
> **8. MITIGATED → OPEN.** "Preregistration is a manual discipline, not a compiled enforcement; per
> your rule, this is an OPEN risk that the discipline will be forgotten or skipped."

Both accepted. Gemini declined to move anything in the generous direction — it found nothing I was
flagellating myself over. That drops the count to IMPOSSIBLE 0 / MITIGATED 2 / OPEN 8.

### Round 1 — (b) mistake classes we have not had yet

1. **Sealed Poison Pill** — "The seal system verifies a registration doc's integrity, not its
   correctness. A reg with a typo (`HARD_MAX_SEATS=10` instead of `1`) is sealed, the gate passes
   it, and the constant is compiled, causing the bot to deploy 10× its intended capital."
2. **Gate-Script Drift** — "`enforce_gate.py` is the one part of the seal protocol that cannot check
   itself. An edit to this file would disable the entire governance layer." **← best of the set; see below**
3. **Stale Fact Poisoning** — a `verified_at` fact the venue silently changed; "failing to exit a
   position before an unobserved early settlement, realizing a max loss."
4. **Subagent Data Laundering** — a subagent writes a *derived* fact into the JSON store; the head
   consumes it as primary, "losing provenance and inheriting any flaws from the subagent's logic."
5. **Persuasive Hallucination Pipeline** — a strategy approved on compelling prose without a
   mandatory reproducible backtest; the loss "chalked up to bad luck."
6. **Clock-Based Control Failure** — single VPS, single clock; drift makes the compiled 24h curfew
   fire at the wrong venue time, "trading into the illiquid post-close period."
7. **API Pagination Regression** — the `get_settlements()` defect generalized to any future list call.

### Between rounds — I tested class 2 against the live VPS

Confirmed, and worse than Gemini guessed. 20 seals, **all markdown, zero `.py`**. And
`/home/ubuntu/senate` is not a git repo, so an edit to the gate leaves no trace at all — Gemini
assumed there would at least be a diff to find. There isn't.

### Round 2 — attack (i): is the "report template" fix enforceable?

> "The proposed template fix for item 10 is **prose in a costume**. A template is a suggestion, not a
> control. A linter can check for the *presence* of a `[source: ...]` tag, but this is a vanity
> check. It would have passed the erroneous $2.04/day figure because the tag was present; it cannot
> validate that the source justifies the number or that the denominator is correct."

Its minimum machine-checkable version — typed figures with non-nullable `value`, `source_file`,
`source_field`, `derivation_logic`, and a generator that fails on a missing field — is S7. Gemini's
own closing caveat is the honest one: **"This forces structure but still does not verify
correctness."** S7 raises the cost of a laundered number and makes the denominator explicit enough
to be argued with. It does not make item 10 impossible. **Item 10 is the one item on this ledger
where the honest answer is that no compiled control closes it.**

### Round 2 — attack (ii): what would actually have caught item 1?

> "The seal-checker found nothing because it was checking the wrong artifact. It audited the
> *policy* (the markdown file) while the incident was caused by the *code* (`autoseat.py`). The code
> was never sealed. …The deploy gate must verify that the hash of the `.py` file being deployed
> matches the hash declared in the sealed registration. **This reveals that the artifact people audit
> (prose) and the artifact that trades (code) are dangerously decoupled.**"

That is S4, and it is the single most useful sentence either round produced.

### Round 2 — attack (iii): which one first?

Gemini's own ranking put "Resurrect Archived Controls" first at $200/hr — on a **self-admitted
guess** of $5,000 — then its prose argued for CI anyway. I discard the guessed figure and keep the
argument, which is right:

> "Without it, any new test or resurrected control is just more code that will only run when a human
> remembers to type `pytest`. …The second-place option, Pre-deploy Seal Verification, is critical for
> preventing Gate-Script Drift, the single most severe vulnerability. However, it is a narrow,
> specific control. It would not have caught the fee implementation bugs, the fake-fixed oracle, or
> the hardcoded base rates. …**The CI check does NOT cover direct, post-deploy edits on the VPS**,
> which the seal check is designed to detect. That is its primary weakness."

Hence the ordering in §3: S1 first as the enabler, S4 retained specifically because S1 cannot see the
un-versioned VPS.

---

## 5. WHAT THIS LEDGER SAYS

The org's failure mode is not that it lacks controls. It wrote `prereg.py`, `enforce_gate.py`,
`citation_verifier.py`, `honesty_lint.py`, `adversary.py`, a deploy-gate hook, and 13,000 lines of
tests — and then archived the enforcing half, emptied `deploy-gate/`, set `hooks: {}`, and shipped a
CI that only speaks Rust. Item 1's kill switch was "prose, not code." Item 4's fix has a test that
routes around it. Item 6's constant is pinned to a copy of itself. Item 8's discipline lives in
`archive/`.

The pattern across all ten is one thing: **a control was authored, and authoring was mistaken for
compiling.** S1 is the cheapest place to stop doing that.

The second pattern, visible only once the receipts were pulled: **the derived copy gets fixed and the
source artifact does not.** The fee fact was corrected in the fact store and left stale in
`fee_schedule.json`. The order rows had `status` reconciled and `side` left inverted. The pagination
lesson was written into two docstrings in `wire.py` and skipped the third method. The round-trip
backtest was ported as prose into `autoseat.py` rather than imported from `seats.py`. Each of those
is a hand-fix that ran out of attention before it ran out of scope — which is what a compiled check
is for.

And the fee error was already found and fixed in **July 2026** before regressing. Item 5 is the
proof that this ledger will need to be re-run: without S3, the same fact will be rediscovered from
the same venue receipt a third time.

*No code was modified and nothing was deployed in producing this ledger. Read-only throughout.*
