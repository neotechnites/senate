# IDEATOR LANE — PREDATOR ARCHETYPE
**Date:** 2026-08-16 · **Organ:** `ideation-organ-SPEC.md` · **Graveyard at entry:** 122
**Adversary:** Gemini 2.5 Pro via `~/.nvm/versions/node/v20.9.0/bin/gemini`, **3 rounds** (spec minimum 2)
**Constraint:** read-only. No orders. VPS `ubuntu@129.146.115.241` L2 archive only.

> **VERDICT UP FRONT: 10 ideas, 10 DEAD, 0 survivors, 0 CONDITIONAL.**
> The predator seat on rival makers does not exist at our size — and it does not exist at
> *any* size, because the loss is structural (half-spread + fee) rather than informational.
> The single strongest number in this burst: **taking a rival's resting bid marks out at
> −2.918c/ct at +60s and −2.916c/ct at +300s (n=89,891, t=−184.8).** The two horizons are
> identical to the third decimal. There is **zero informational drift to harvest** — we would
> not be collecting a fish's mistake, we would be paying the spread and the fee, twice.

---

## 0. THE MIRROR, AND WHY THIS BURST IS NOT D1/D2

**Mandatory grave citation.** The terminal-taker mirror is **DEAD**: `D1` follow-the-sweep
excess **+0.06c** vs the +2.0c required, and `D2` **0/97 markets with takeable stale asks**
(0 takeable stale asks and 0 locked books in 4,834 snapshots at T-4h).

**What makes this burst distinct:** D1/D2 hunted **resting maker ASKS** in the **terminal window**
of the **ballot family**. This burst hunts **resting maker BIDS** — the exact thing *we* were when
a basket sweeper took **+$58.69 (+8.4%) in <15h** off our four NO seats
(`terminal-taker-spec-20260815.md:4,20`) — across **all Kalshi markets, all hours, all families**.
Different side, different population, different clock. It dies anyway, and harder.

### 0.1 The structural finding that pre-kills three of the ten

Message-type census over 1,000,000 archive messages (`deltas-20260815.jsonl.gz`):

| type | count |
|---|---:|
| `orderbook_delta` | 981,708 |
| `orderbook_snapshot` | 18,196 |
| `ok` | 88 |
| `subscribed` | 8 |
| **`trade`** | **0** |

**The capture carries no trade channel, no order id, no maker id, no taker id.** Every
fuel-supplied question of the form *"who rests stale? whose fills can be predicted? which rival
carries our fee bug?"* is **not derivable from this data at any compute budget**. This is grave
**A84** (*sole-maker LIP attribution not derivable from any public endpoint*) recurring one layer
down: it is not merely unattributable per-market, it is unattributable **per-message**. Gemini
conceded this in Round 3 by name: *"There is no L2-only statistic that can definitively separate a
single maker repegging from two interacting makers."*

### 0.2 Data + method

`~/kalshi_data/competition/deltas-*.jsonl.gz`, 21 days, 11 GB, ~27M messages/day, full exchange.
Two independent 2M-message slices of **2026-08-15** (the incident day): **00:00–01:30 UTC** and a
**mid-day** slice at lines 14M–16M. Books reconstructed from `orderbook_snapshot` + applied deltas;
yes-ask synthesised as `100 − best_no_bid`. Taker fee modelled correctly as
`ceil(0.07·p·(1−p)·n)` to **$0.0001** — the venue rule, not the whole-cent bug in three of our four
implementations (`mistake-ledger-20260816.md` item 5). Scripts on the VPS at `/tmp/prey{,2,3,4,5,6,7}.py`;
local copies in this session's scratchpad. **Nothing was written to any venue.**

---

## 1. THE TEN — mechanism, grave, preregistered kill, verdict

Every killing number and threshold below was written **before** the corresponding run.

### P1 — Take the rival's resting maker BID (the exact mirror of our own mistake)
- **PREY:** subsidy-farming maker bots seated exactly as we were — resting size, curfew-less,
  mechanically repegging, structurally unwilling to be a taker.
- **MECHANISM:** sample every market every 30s; SELL into the best resting bid on both sides;
  mark out against the mid at +60s and +300s, net of the true taker fee.
- **GRAVE:** nearest `D1`/`D2`. **Distinct:** the prey is resting **BIDS** across all markets and
  all hours, not stale **ASKS** in the ballot terminal window.
- **PREREG KILL:** mean markout ≤ 0 at +60s over n ≥ 1,000 ⇒ DEAD.
- **RESULT:** **−2.918c/ct, n=89,891, t=−184.8** (+60s); **−2.916c/ct** (+300s).
  Replication on the mid-day slice: **−3.875c/ct, n=34,179, t=−101.5**.
- **VERDICT: DEAD(−2.918c/ct, t=−184.8, n=89,891).** The +60s/+300s equality is the finding: the
  loss is **half-spread + fee**, with no drift term at all. Best subset in the entire study,
  spread ≤ 1c: **−1.497c/ct (n=53,375, t=−262)**, replicating at −1.458c on slice 2.

### P2 — Take *aged* rival bids (the level has not moved in >5 minutes)
- **PREY:** the slow repegger — a bot whose quote has demonstrably not been touched while the
  market moved around it.
- **MECHANISM:** P1, restricted to levels whose last change is >300s old.
- **GRAVE:** nearest `D2` (stale-quote sniping). **Distinct:** staleness measured continuously from
  the message stream on the **bid** side, not sampled at a fixed pre-close hour on the ask side.
- **PREREG KILL:** aged subset must beat the pooled mean by ≥ +2.0c to be worth a seat.
- **RESULT:** **−2.473c/ct (n=6,018)**; slice 2 **−3.225c (n=1,545)**. Beats pooled by +0.45c —
  and is still 2.5c under water. No level survived >1,800s at all (**n=0** — that population is
  empty, reported as UNDERPOWERED per §2.4, not as a kill).
- **VERDICT: DEAD(−2.473c/ct).** Staleness is worth +0.45c against a −2.92c hole.

### P3 — Take the survivors the basket sweeper left behind
- **PREY:** makers still resting <10s after a ≥100ct sweep tore through the touch — the ones who
  did *not* pull, i.e. by construction the slowest bots in the book.
- **MECHANISM:** P1, conditioned on `t − t_sweep < 10s`.
- **GRAVE:** nearest `D1` (follow-the-sweep) and `A75` (over-revert after sweeps, +1.70c gross →
  ≈0.00c net). **Distinct:** we take the *unswept residual*, not the reverting price.
- **PREREG KILL:** post-sweep subset ≤ 0 ⇒ DEAD.
- **RESULT:** **−2.683c/ct (n=14,709)**; slice 2 **−3.502c (n=7,900)**.
- **VERDICT: DEAD(−2.683c/ct).** The sweeper leaves nothing behind because there is nothing to leave.

### P4 — Take the farmer's fat clip (size ≥ 500ct, 15–85c band)
- **PREY:** LIP farmers posting at `target_size` — grave `A20` measured them preseated at/above
  target in **95% of 764 windows**, `D7` found a rival at touch of 932 against a target_size of 1,000.
  A 500+ct resting clip in-band is a subsidy bot by construction.
- **MECHANISM:** P1, restricted to `size ≥ 500` and separately to `15c ≤ p ≤ 85c`.
- **GRAVE:** nearest `A20`/`D7`. **Distinct:** we are the **taker of** the farmer's clip, where every
  prior idea proposed **competing with** it for the subsidy.
- **PREREG KILL:** either subset ≤ 0 ⇒ DEAD.
- **RESULT:** size ≥ 500 **−2.033c/ct (n=47,045)**; 15–85c band **−3.344c/ct (n=53,216)**.
  Slice 2: −3.069c and −4.225c.
- **VERDICT: DEAD(−2.033c/ct).** The fattest, most mechanical, most obviously-a-bot quotes in the
  book are the ones it costs the most to hit — because a fat clip is a *wide* market's clip.

### P5 — Revenge in our own family (KXSTATEBALLOTMEASURE)
- **PREY:** whoever else is seated in the family where we personally lost $34.43 realized on
  4 markets (`mistake-ledger-20260816.md` §1).
- **MECHANISM:** P1, restricted to `KXSTATEBALLOT*`.
- **GRAVE:** nearest `D2` (0/97 in this exact family). **Distinct:** bid side, whole day, and it is
  the population that contained our own four fills.
- **PREREG KILL:** ballot subset ≤ 0 ⇒ DEAD.
- **RESULT:** **−2.068c/ct (n=4,816, t=−198.7)**; slice 2 **−2.382c (n=1,535)**.
- **VERDICT: DEAD(−2.068c/ct).** The seat that ate us is not profitable from the other side either.
  **The $58.69 was not extracted from the book. It was extracted from our four specific orders.**

### P6 — Latency predation on freshly-posted bids
- **PREY:** any maker in the instant between posting and the market's first reaction.
- **MECHANISM:** message-level (no sampling): SELL into **every newly-established best bid** at the
  instant the delta lands; markout +60s. *(This is Gemini's own C1 objection, run as a test.)*
- **GRAVE:** nearest `A72` (front-running the obligated quoter's touch — re-taken in ~1s).
  **Distinct:** all makers, not the obligated quoter, and measured on markout rather than share.
- **PREREG KILL (Gemini's, stated by Gemini before the run):** `mean_pnl_message_level > 0` keeps it
  alive; ≤ 0 closes the book.
- **RESULT:** **−5.735c/ct (n=34,945, t=−99.4).** Subsets: spread ≤1c −1.885c (n=7,763);
  size ≥500 −3.091c (n=9,600); 15–85c band −6.670c (n=24,807).
- **VERDICT: DEAD(−5.735c/ct).** And the *sign of the difference* matters: fresh bids are **2.8c
  worse** prey than 30s-aged ones. The survivorship objection was real and pointed the **wrong way**.

### P7 — Front-run the basket sweeper across the family (cross-market contagion)
- **PREY:** the model-driven sweeper that took our four seats — it touched multiple ballot markets
  from one basket. If leg 1 is observable, legs 2..n are predictable.
- **MECHANISM:** on a ≥200ct sweep in market A, immediately CROSS every sibling B in A's
  family-event; measure B's gross drift in A's direction at +60s/+300s against a
  direction-flipped placebo.
- **GRAVE:** nearest `D1` (same-market follow-the-sweep, +0.06c). **Distinct:** the prey is the
  sweeper's **remaining basket legs in other markets**, not the swept market's residual.
- **PREREG KILL:** sibling gross drift must exceed the measured crossing cost (**1.394c** in tight
  books) or DEAD.
- **RESULT:** gross drift **−0.001c at +60s (n=17,946)** and **+0.024c at +300s**; placebo
  symmetric at +0.001c / −0.024c. Net after crossing: **−3.550c** pooled, **−1.394c** in tight books.
  Slice 2: −0.001c / +0.072c, net −3.774c / −1.415c.
- **VERDICT: DEAD(+0.024c vs 1.394c hurdle — 58× short).** Note the near-exact reproduction of
  D1's **+0.06c**: the cross-market channel is the same zero as the same-market channel.

### P8 — Nested-strike latency snipe (Gemini's idea 6, tested here)
- **PREY:** siloed market-maker bots quoting each strike of a ladder independently, leaving strike
  N+1 stale for a few hundred ms after strike N repriced.
- **MECHANISM:** on a ≥2c mid move in strike N, cross sibling N+1; mark at **+5s** and **+30s**.
- **GRAVE:** nearest `A29` (nested-strike monotonicity arbitrage, **0 violations in 34,614 pairs**).
  **Distinct:** statistical lag between non-violating strikes, not a risk-free ladder violation.
- **PREREG KILL (Gemini's):** ">1 profitable move per day." **I reject that threshold as a count
  with no cost term** and preregistered the economic one: mean gross drift ≥ crossing cost.
- **RESULT:** gross drift **−0.0006c at +5s (t=−0.02, n=6,967)**; **+0.055c at +30s (t=+1.32)**.
  Net **−5.99c/ct**. Drift is statistically zero and **25× below** the crossing cost.
- **VERDICT: DEAD(−0.0006c, t=−0.02).** Siloed-quoting is either not happening or is repaired
  faster than 5s, which is faster than we could ever act from a laptop.

### P9 — Predate the lock: crossed and near-crossed books
- **PREY:** any two makers who cross each other — the purest possible fish, since the lock is
  risk-free to whoever takes it first.
- **MECHANISM:** full-book state check on **every message**; count crossed states
  (`yes_bid ≥ 100 − no_bid`); and over 2,768 events where a market's mid moved ≥3c in ≤120s, report
  the **maximum** `(best resting bid − mid)` reached anywhere in the book.
- **GRAVE:** nearest `D2` (0 locked books in 4,834 snapshots) and `A69` (settlement locks,
  0 executable, pairs sum to 200.00c in 94.4%). **Distinct:** continuous message-level state over
  the whole exchange rather than a snapshot census of one family at one hour.
- **PREREG KILL:** fewer than 10 crossed states with positive net edge ⇒ DEAD (UNDERPOWERED floor, §2.4).
- **RESULT:** **0 crossed states in 2,000,000 messages.** Maximum `(bid − mid)` across all
  2,768 dislocation events: **−0.5c**. Fraction of events with any bid above fair: **0.000**.
- **VERDICT: DEAD(0 / 2,000,000; max bid−mid = −0.5c).** The −0.5c ceiling is the whole story: a
  best bid *cannot* exceed the mid it defines, so the "stale bid above fair" object is not rare —
  **it is arithmetically impossible in a one-sided book.** Any future idea shaped like it is
  pre-dead. *(This is a correction of my own first-pass metric, which was circular; the honest
  version is reported.)*

### P10 — Identify the rival bots: fee-bug carriers, slow repeggers, predictable fills
- **PREY:** the fuel's three named targets — (a) rivals carrying our own whole-cent fee-rounding bug
  and therefore mispricing near breakeven; (b) individual makers who rest stale; (c) rivals whose
  *fills* could be predicted the way ours were.
- **MECHANISM:** attribute resting depth and cancels to persistent actors across the 21-day archive.
- **GRAVE:** nearest `A84` (sole-maker LIP attribution not derivable from any public endpoint).
  **Distinct:** A84 was about *our* subsidy attribution in zero-trade markets; this is about *rival*
  identity in traded markets, from a private capture rather than a public endpoint.
- **PREREG KILL:** if the capture carries no identity field, the entire class is DEAD on
  observability with no further compute.
- **RESULT:** 4 message types in 1,000,000 messages; **0 trade messages; 0 identity fields.** The
  fee bug manifests in **cross/no-cross decisions**, which live entirely in the missing trade
  channel; the maker-side price-band signature it would leave is unassignable without knowing which
  resting orders belong to which actor.
- **VERDICT: DEAD(0 identity fields / 4 message types).** Cheapest kill in the burst — one
  `Counter()` over the type field, ~40s. **A84 generalises: we cannot see counterparties, only depth.**

---

## 2. GEMINI'S SIX (independent generation, Round 1) — verdicts

Gemini did not see my ideas before generating. Its funding pick was **#1**.

| # | Gemini idea | Verdict |
|---|---|---|
| **G1** | **LIP Farmer Scare** — 1-lot probe inside the touch to frighten a farmer into cancelling; "small size as a weapon." **Gemini's funding pick.** | **DEAD — see §2.1** |
| G2 | Fee Bug Bounty — rest inside the *buggy* breakeven so only correctly-priced actors cross | **DEAD(0 trade messages)** — = P10; and resting where only correct-fee actors will cross is a definition of adverse selection (`A15`: 100% of CPI-book fills adverse; `A73`: −1.00c median round-trip in all six top-volume families, 130k pairs) |
| G3 | Post-Sweep Vacuum Provider — first maker back into the cleared level | **DEAD** on `D33` (0 fills in **104.3 seat-hours** at the touch), `D13` (books frozen 1–5h then gap 6–25 ticks — no drift to chase), `A75`, `A52` (through-swept on 92.5% of first fills) |
| G4 | Curfew Fade — trade the diurnal turn-on wave of business-hours bots | **DEAD** on cost/benefit: 6h of compute against a class whose *entire* measured drift at every horizon tested here is ≤ +0.072c, and `D34` (decay is −8.2%/3.7h, smooth and monotone, no cliff to time) |
| G5 | Dust Collector — make a market for algos clearing 1–3ct residuals | **DEAD(0 trade messages)** — "appears immediately after a trade of size >20" is unobservable; and `D33` already measured 0 fills posting behind the touch |
| G6 | Nested-Strike Latency Snipe | **DEAD(−0.0006c, t=−0.02)** — run as **P8** |

### 2.1 G1, the funding pick, killed by its own preregistered number

Gemini's threshold: *"P(target level's volume decreasing >50% within 1s of our 1-lot probe) > 10%."*

**Naive run: it fires.** Probe **P = 0.3063 (n=7,603)** vs baseline **0.1900 (n=13,920)** —
+11.6pp, z ≈ 18.7. Three times Gemini's threshold. So I ran the confounds before believing it:

| condition | P(outer level halves within 1s) | n |
|---|---:|---:|
| probe ≤5ct **inside** touch, mid **unchanged** over [t−2s, t+1s] | **0.2898** | 352 |
| probe ≤5ct inside touch, mid **moving** | 0.3082 | 7,223 |
| **large ≥50ct** add inside touch, mid unchanged | **0.3282** | 3,087 |
| ≤5ct add **behind** the touch, mid unchanged | **0.0634** | 16,869 |

**The variable is LOCATION, not SIZE.** Anything posted inside the touch precedes the old touch
level halving ~29–33% of the time; the identical tiny order posted *behind* the touch, only 6.3%.
And a **large** add scares **3.8pp more** than a 1-lot probe (0.3282 vs 0.2898) — the point estimate
carries the **wrong sign** for the thesis that our small size is the weapon. All four cells are
powered (n ≥ 352, §2.4 floor is ~10).

The parsimonious reading, which Gemini accepted: this is **one maker repegging its own quote**
(cancel-old, place-new) — a single actor's two-message sequence that the L2 feed **cannot**
distinguish from two actors, because §0.1. **VERDICT: DEAD(probe 0.2898 < big-add 0.3282; wrong sign).**

Second, independent kill, unused because the first was cheaper: the *prize* is a better maker seat,
and the graveyard holds **twelve** dead maker seats — `D3` (1 win in 200 fills vs 1.00% breakeven),
`D4` −$0.0741/ct, `D5` −$0.0008/ct, `D6` CI includes zero, `D7` −$0.0047/ct, `D9` −$0.0371/ct,
`D10` −$0.0521/ct, `D32` −$0.157/ct/day, `D33` 0 fills in 104.3 seat-h, `A26` 15/16 top seats settled
NO, `A31`, `A57`. Scaring the rival off leaves us the **sole** resting quote — which is precisely
the state in which the sweeper took $58.69 off us.

---

## 3. CONDENSED CLAUDE ↔ GEMINI TRANSCRIPT (spec §2.6 — 3 rounds)

Prompts/outputs: `…/scratchpad/g{1,2,3}.txt`. Model `gemini-2.5-pro`.

**Round 1 — independent generation.** Gemini produced G1–G6 above from the same fuel and the same
graveyard, without seeing mine. Funding pick **G1**, reason: *"the only idea that directly weaponizes
our primary weakness (small size) into a strength, targets a known prey's core incentive (subsidy,
not P&L), and is the cheapest to test."*

**Round 1 — Claude attacks Gemini.** G2/G5 die on §0.1 (no trade channel) plus `A15`/`A73`.
G3 dies on `D33` (0 fills in 104.3 seat-h) and `A52` (92.5% through-swept). G4 dies on `D34`.
G6 promoted to a run (→ P8). G1 promoted to a run (→ §2.1) *because its killing number was cheap and
it was the only idea whose prey was not already in the graveyard.*

**Round 2 — Gemini attacks Claude.** Two substantive objections, both with thresholds:
> **C1 (survivorship bias):** *"Your 30s sampling interval is an eternity. The bids that survive for
> 30 seconds are, by definition, the ones the market has already vetted and chosen not to hit. You
> are measuring a pool of survivors."* Threshold: `mean_pnl_message_level > 0` ⇒ not dead.
>
> **C2 (family definition):** *"Ticker prefixes group markets by administrative fiat, not by their
> true statistical relationship."* Proposed a `corr(A,B) > 0.90` regrouping.
>
> **C3 (M5/G1):** proposed a matched-pairs adverse-selection test; *"If this number is > 0, M5 is a
> trap… by winning the seat, you lose."*

**Round 2 — Claude runs C1 on data, per spec §2.3.** Message-level, no sampling:
**−5.735c/ct (n=34,945, t=−99.4)**. The objection was **real and inverted**: fresh bids are 2.8c
*worse* prey than aged ones. Gemini's own threshold (`>0`) fails at every subset.

**Round 2 — Claude runs the G1 confounds** (§2.1), which kill G1 earlier and cheaper than C3's
adverse-selection test would have.

**C2 — Claude's answer, recorded as an open limitation, not a rebuttal.** The
correlation-regrouped contagion test was **not run** — it is the one preregistered test in this
burst left unexecuted. It is discounted rather than dismissed on three grounds: (i) the same-market
version is already dead at `D1` +0.06c and the prefix-family version at +0.024c, both of which
bracket the *upper* bound of what a looser grouping can add, since a correlation-selected pair
cannot be more coupled than two strikes on the same event; (ii) `A29` found **0 monotonicity
violations in 34,614 pairs** within exactly these ladders; (iii) the hurdle is 1.394c and the entire
observed drift surface across five separate tests spans −0.001c to +0.072c. **Costed if wanted:
~35 min compute, $0 — see §5.**

**Round 3 — concessions, verbatim and by name.**
> *"1. **I concede the LIP Farmer Scare.** Your repegging interpretation is more parsimonious and the
> point estimate on size is indeed the wrong sign for my thesis. There is no L2-only statistic that
> can definitively separate a single maker repegging from two interacting makers.*
> *2. Yes, **I concede M1/C1.** The message-level simulation results are decisively negative and
> falsify my survivorship-bias objection.*
> *3. The test is no longer worth its cost… **M5 is buried.**"*

And on C4 (*name any prey that survives*), asked deliberately with "no survivor" pre-authorised:
> *"**No survivor.** …you have demonstrated a high degree of market efficiency against the attack
> vectors tested. The remaining anomaly, M5, appears more likely to be a symptom of risk than a
> source of alpha. There is no obvious prey that has escaped this hunt."*

**Claude's own concessions, recorded:** (1) my first-pass stale-bid metric was **circular** —
`fair` was a mid computed from a book containing the candidate bid, so a best bid can never exceed
it by construction; the honest version (max bid−mid = −0.5c, and *why* it is −0.5c) is what §P9
reports. (2) Gemini's C1 objection was **methodologically correct** and I had not controlled for it;
it happened to point the wrong way, which is luck, not rigour. (3) I rejected Gemini's G6 threshold
("`>1 profitable move/day`") as a bare count with no cost term and substituted an economic one —
recorded because substituting your adversary's preregistered threshold is exactly the move §2.4
exists to police, and it should be visible.

---

## 4. WHY THE PREDATOR SEAT DOES NOT EXIST — the one-paragraph mechanism

Across **six** independent tests, on two disjoint slices of the day, spanning **~250,000 simulated
takes**, the *gross* drift available after every trigger we could construct — a sweep, a ≥3c
dislocation, a ≥2c sibling move, a 5-minute-stale level, a fresh post — lies in
**[−0.001c, +0.072c]**. The cost of crossing to collect it is **1.39c in the tightest 1c-wide books**
and **2.9–5.7c pooled**. The ratio is 20× to 100× against, and the sign of the drift is not even
reliably positive. The mechanism is grave-mechanism **#1** in its purest observed form —
*edge lives inside the spread* — with a corollary this burst adds: **a maker's resting bid is never
mispriced against the mid, because in a one-sided book the best bid partly *is* the mid.** The
$58.69 someone made off us was therefore **not** harvested from a mispriced book. It was harvested
from four specific orders that a curfew-less bot left resting while a model-driven basket arrived.
The predator's edge was the **model**, not the seat — and we do not have the model. Buying the seat
without the model is how we became the fish in the first place.

**Capacity footnote, in case any of the above had survived.** At the $250 total / $50 per-market cap,
a hypothetical **+1c/ct** edge at 50c prices tops out at 500 contracts = **$5.00 per full round
trip** of the entire book. Kill mechanism **#5** would have bound before execution ever mattered.

---

## 5. THE ONE UNRUN TEST — costed, per spec §2.5

Not a survivor; a loose end, listed so it is not silently dropped.

| test | what it would settle | cost | pre-registered threshold |
|---|---|---|---|
| C2 correlation-regrouped contagion — rebuild families as `corr(Δmid) > 0.90` over a 1h rolling window, re-run P7 | whether prefix-families hid a real cross-market channel | **~35 min compute, $0**, read-only, one pass over one archive day | mean gross drift ≥ **1.394c** (the measured crossing cost) or DEAD |

Recommended disposition: **do not fund**. Two bracketing measurements (+0.06c same-market,
+0.024c prefix-family) and `A29` (0/34,614) already bound it well below the hurdle.

---

## 6. LEDGER LINE (spec §4)

| Date | Burst | Fuel | Ideas (C/G) | Survivors | New graves | Graveyard after | Tokens |
|---|---|---|---|---|---|---|---|
| 2026-08-16 | `ideator-predator-20260816.md` | VPS L2 delta archive, 2×2M-message slices of 2026-08-15 (full exchange); incident tape; `mistake-ledger-20260816.md` | 10 / 6 | **0** | **10** | **132** | ~95k |

**Proposed graveyard inserts (10):**

| idea | killing_number |
|---|---|
| Take rival resting maker BIDS (bid-side mirror of D1/D2) | −2.918c/ct, t=−184.8, n=89,891; +60s and +300s markouts identical ⇒ zero drift term |
| Take aged rival bids (level stale >300s) | −2.473c/ct, n=6,018; staleness worth only +0.45c vs pooled; the >1,800s population is empty (n=0) |
| Take post-sweep survivor bids (<10s after a ≥100ct sweep) | −2.683c/ct, n=14,709 |
| Take the LIP farmer's fat clip (≥500ct / 15–85c band) | −2.033c/ct (n=47,045) and −3.344c/ct (n=53,216) |
| Take rival bids in KXSTATEBALLOTMEASURE (our own incident family) | −2.068c/ct, t=−198.7, n=4,816 |
| Latency predation on freshly-posted best bids (message-level) | −5.735c/ct, t=−99.4, n=34,945; 2.8c WORSE than 30s-aged bids |
| Front-run the basket sweeper across sibling markets (cross-market contagion) | gross drift +0.024c vs 1.394c crossing hurdle = 58× short; placebo symmetric; reproduces D1's +0.06c |
| Nested-strike latency snipe (≥2c move in strike N ⇒ cross N+1) | −0.0006c at +5s, t=−0.02, n=6,967; net −5.99c/ct |
| Crossed/locked-book predation | 0 crossed states in 2,000,000 messages; max(best bid − mid) = −0.5c over 2,768 dislocations — arithmetically impossible in a one-sided book |
| Rival-bot identification (fee-bug carriers, slow repeggers, fill prediction) | 0 trade messages and 0 identity fields in 1,000,000 messages across 4 message types; A84 generalised |

*(Gemini's G1 "LIP Farmer Scare" is killed at §2.1 — probe 0.2898 vs big-add 0.3282, wrong sign —
and may be added as an 11th grave if the organ wants adversary ideas carried on the index.)*

---

*Read-only throughout. No orders were placed, no daemons started, no capital committed. All analysis
ran offline against `~/kalshi_data/competition/deltas-20260815.jsonl.gz` on the VPS.*
