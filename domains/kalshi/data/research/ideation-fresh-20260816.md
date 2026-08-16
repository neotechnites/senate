# Ideation Burst — 2026-08-16 (first run under the organ)

**Spec:** `ideation-organ-SPEC.md`. **Graveyard at entry:** 114 graves. **At exit:** 120.
**Constraint honoured:** completely fresh — every idea below cites the graves it is distinct from.
**Read-only. No orders. No capital committed.**

---

## 0. Outcome in one block

Eight ideas generated (4 Claude, 4 Gemini). **One survivor.** Six new graves, one merge.

| Idea | Source | Verdict |
|---|---|---|
| C2 **Depth-conditional seat screen** | Claude | **TRADE-shaped (subtraction)** |
| C1 Thin-rival in-band LIP pocket | Claude (= Gemini G1) | **DEAD** — net −$0.157/ct/day |
| C3 Depth-bleed share timing | Claude | **DEAD** — ≤8.9% relative share gain |
| C4 Deep-churn early warning | Claude | **DEAD** — z = −0.46 |
| G2 Post one tick behind the touch | Gemini | **DEAD** — 0 fills at touch vs 4 behind |
| G3 End-of-window taker sweep on decay | Gemini | **DEAD** — −45.71 c/ct prior; decay is smooth |
| G4 Restore the 1c spread after widening | Gemini | **DEAD** — touch re-taken in ~1s vs our 300s |

The burst's most valuable product is not the survivor. It is that **the most attractive
idea of the night — the one both models independently ranked #1 — died on a $0 test.**

---

## 1. Fuel

**Read:** `terminal-taker-spec-20260815.md`, `temp-hourly-census-20260815.md`,
`family-census-20260815.md`, `ideation-burst-20260815.md`, `fill-forensics-20260815.md`,
`ballot-base-rate-gate-20260815.md`.

**Tonight's captures — new data, never before analysed:**

| Source | Rows | Markets | Sweeps | Window (UTC) |
|---|---|---|---|---|
| Mac `terminal_capture_20260815.jsonl` | 2,245 books | 110 | 15 | 20:25 → 22:07 |
| VPS `/home/ubuntu/kalshi_data/…` | 2,589 books | 110 | 24 | 22:10 → 00:06 |
| **Combined panel** | **4,834 snapshots / 4,724 consecutive pairs** | 110 | 39 | **3.7h, ending T−4h** |

Full `orderbook_fp` ladders, both sides, 300s median interval. Window close 2026-08-16T03:59Z.

### 1.1 The panel's primary measurements (all new tonight)

| Measurement | Value |
|---|---|
| Median bid-ask spread | **1c**; 59.4% of all snapshots are 1c-wide; p90 = 5c |
| Locked / crossed books | **0 of 4,834** |
| Book changed between snapshots | 1,061 / 4,724 = 22.5% |
| …of which the **touch price** moved | **63 (5.9%)** — 998 were deep-level-only churn |
| Touch-move rate | 1.33% per 300s = **0.160 per seat-hour** |
| Mid change on a touch move | median +0.5c, **mean +0.16c** (indistinguishable from zero drift) |
| Touch moves ≥5c | 14% of moves = one per 43.7 seat-hours |
| Total depth trend | **−8.2% over 3.7h**, monotone, **no evacuation cliff** |
| Rival touch depth (220 sides, final snap) | median **891 ct**, p25 201, p10 50 |
| Mid distribution | 75/110 in-band (15–85c), 32/110 >85c, 3/110 <15c |

### 1.2 A preregistered prediction resolved early, for free

`terminal-taker-spec-20260815.md` §7d predicted: *"at T−15m the count of takeable stale
asks is still ≤2/97."* At **T−4h**: **0 takeable stale asks and 0 locked books across 4,834
snapshots**. The stale-quote thesis is not resurrected. Grave **D2** confirmed at 50x the
prior sample. Depth bleeds smoothly rather than evacuating — grave **D1**'s mechanism
independently re-confirmed.

---

## 2. Claude's four, against the graveyard

### C1 — THIN-RIVAL IN-BAND LIP POCKET
**Mechanism.** LIP share = `our/(our+rival_qual)`. Median rival touch depth is 891 ct, but
**18/110 markets hold a touch side ≤50 ct in ≥90% of snapshots**, and **15 of those sit
in-band (15–85c)**: AZ-P319 (mid 74c, 17 ct), AZ-P320 (58c, 25 ct), LA-A607 (64c, 25 ct),
NM-A1 (76c, 25 ct), AR-SJR15 (74c, 41 ct), AZ-P142 (60c, 45 ct), CO-I109, IA-A1, LA-A220/
A271/A272/A414. Posting 500 ct against rival 35 gives **share 0.935 vs the ~10% ballot
actually realized = a 4.86–9.1x multiplier**.

**Graveyard citations.** Distinct from **A26** (naive top-rate seats screened on *rate* and
caught the 1–4c wing trap, 15/16 settled NO — this screens on *rival thinness* with a hard
in-band constraint that excludes wings). Distinct from the V1 thin-**target_size** pocket
(that was `target_size_fp`=300 in KXEOWEEK; this is rival depth in ballot). **A57** states
the rotating-seat column is "dead unless share ≥8–14% sustainable" — this pocket delivers
93.5%, i.e. it clears that grave's own revival tripwire.

### C2 — DEPTH-CONDITIONAL SEAT SCREEN
**Mechanism.** The compiled eject rules were fitted on **4 adverse fills**. This panel has
**4,724 pairs**. It shows touch instability is not a market-wide constant but a steep,
monotone function of rival touch depth.

**Graveyard citations.** Distinct from **D25/D26/D27** (evacuation/drift/share ejects, all
0/4, all *time-series* triggers fired during a seat) — this is a **cross-sectional
admission screen** applied *before* seating, using a variable none of those three used.

### C3 — DEPTH-BLEED SHARE TIMING
Seat late, after rival depth has decayed. **Killed inline:** decay is −8.2% over 3.7h, so
share improves at most **8.9% relative** — noise against C1's 4.86x. **DEAD.**

### C4 — DEEP-CHURN AS EARLY WARNING
94% of book changes are deep-only; treat them as a leading indicator of the touch move.
**Killed inline:** P(touch moves next step | deep churn) = **0.0122 (n=983)** vs **0.0140
(n=3,631)** without. **z = −0.46** — if anything the wrong sign. **DEAD.**

---

## 3. THE GEMINI EXCHANGE — verbatim-condensed (mandatory under spec §2.6)

Invocation: `~/.nvm/versions/node/v20.9.0/bin/gemini -p "$(cat prompt.txt)"`. Three rounds.

### 3.1 Round 0 — Gemini's four, generated independently from the same fuel + graveyard

> **Trade 1 — LIP revenue farm on thinly supported sides.** *"The money exists in the LIP
> formula's `our_size/(our_size+rival_qual)` term. Data: 28/220 sides have <=50 contracts at
> the touch… posting 50 of our own contracts captures 50% of the LIP reward… This is not a
> general maker seat (Graveyard #3); it is targeted exploitation of low-competition markets."*
> Killing number: `(Adverse PnL per fill) + (LIP revenue per contract) < 0`.
>
> **Trade 2 — Provide second-level liquidity one tick behind the touch.** *"The touch is
> stable (moves in only 1.33% of snapshots) but deep churn is high… This implies the touch
> is defended. By posting one tick away we are filled only by takers large enough to sweep
> the entire touch. This selects for indiscriminate takers, reducing adverse selection."*
> Killing number: fill rate <0.1% over 4h.
>
> **Trade 3 — End-of-window taker sweep on predictable liquidity decay.** *"Total book depth
> bleeds a predictable -8.2% over 3.7h, monotonically. The cost to move the mid-price by a
> fixed amount should therefore decay predictably… This is not following (Graveyard #1); it
> is initiating based on a predictable market structure change."* Killing number: R² of
> `cost_to_sweep(N)` vs time <0.6.
>
> **Trade 4 — Maker-post to fill transient 1c-spread gaps.** *"59.4% of books are 1c-wide.
> This implies an algorithmic equilibrium. We watch for single-snapshot deviations where one
> side pulls out, widening the spread to >3c, and immediately post to restore the 1c spread."*
> Killing number: fillable gap events per hour <1.
>
> **Ranking: 1) Trade 1, 2) Trade 2, 3) Trade 3, 4) Trade 4. I will fund Trade 1. The
> evidence is strongest.**

**Note:** Gemini's #1 pick and Claude's C1 are the same idea, reached independently. That
convergence is why it got the hardest test of the night.

### 3.2 Round 1 — Claude attacks Gemini

- **vs Trade 2:** DEAD on our own receipts. Fill forensics: **0 fills in 104.3 seat-hours AT
  the touch vs 4 fills in 48.8 seat-hours BEHIND it** — being behind the touch is the marker
  of a *targeted* book, not a filter for indiscriminate takers. Corroborating **A51**
  (resting alongside the obligated quoter, −2.2 to −3.9 c/ct, survives Bonferroni). And
  **D19**: `discount_factor_bps`=5000 means depth behind the touch qualifies at 50% decay —
  you halve the subsidy to buy worse fills.
- **vs Trade 3:** DEAD twice. **A77** expiry evacuation = **−45.71 c/ct net, t=−17.94, 16/16
  days negative**. **A78** pre-close freeze: the population does not exist, N=1. And tonight's
  decay is −8.2% over 3.7h, monotone and smooth — **there is no cost cliff to time**.
- **vs Trade 4:** DEAD. **A72**: touch re-taken in **~1s**; size buys share only 4.2%→18%.
  Our snapshot interval is **300s** — we cannot observe the event, let alone race it. **A50**:
  the obligated quoter's duty is tightness, so 1c spreads appear wherever flow exists.
- **vs Trade 1:** **agreed and built out** into C1 with the 15-market in-band cohort.

### 3.3 Round 1 — Gemini attacks Claude

> **On C1:** *"The 20-50x thinner depth is not a free multiplier; it is the market price for
> extreme gap risk. These 15 markets are thin because they are brittle… This is adverse
> selection. The killing number is the true hazard rate for this subset."*
>
> **On C2:** *"The model is fatally miscalibrated by applying a panel-wide average hazard
> rate to a hand-picked cohort of extreme outliers. The entire premise of C1 is that these 15
> markets are different."*
>
> **Decisive test proposed:** *"Bin all historical market-hours by rival touch depth (<50,
> 50-250, >250). Calculate the frequency of >10c mid-price gaps in the subsequent window for
> each bin. The C1 thesis is killed if the <50 depth bin exhibits a gap frequency more than
> 5x higher than the other bins."*

**Claude concedes the C2 attack.** Applying a panel average to a selected cohort was a real
methodological error. It is fixed in §4.

### 3.4 Round 2 — Claude runs Gemini's preregistered test

In-band (mid 15–85c), 300s pairs:

| rival touch depth | pairs | touch-move % | ≥5c % | ≥10c % |
|---|---|---|---|---|
| ≤50 | 866 | **4.04** | 0.35 | 0.23 |
| 50–250 | 716 | **2.93** | 0.56 | 0.14 |
| 250–1000 | 525 | **0.38** | 0.00 | 0.00 |
| >1000 | 1,106 | **0.09** | 0.00 | 0.00 |

**Gemini's threshold is nominally met: ratio 5.42x > 5x.** Claude refused the kill:

> *"It rests on n=2 gap events in the thin bin; **z = 1.12**. That is the 'sample collapse
> producing a huge ratio' failure mode our graveyard flags as recurring kill mechanism #4
> (see A3, A8, A19). I do not accept a kill on n=2. But the well-powered version of your
> point is real and I concede it: touch-move rate is monotone in rival depth, **4.04% vs
> 0.09% = 45x, z = 5.85**. Your intuition was right; your chosen statistic was underpowered."*

Claude also disclosed the hole rather than papering over it: *"tonight's capture is BOOK
ONLY. P(fill) in these 15 markets is UNMEASURED."*

### 3.5 Round 3 — Gemini's concessions and the closing arithmetic

> **A.** *"Yes, a kill requires statistical conviction, which n=2 (z=1.12) does not provide."*
>
> **B.** *"The 45x touch-move rate reaches us through the channel of **adverse selection on
> stale quotes**. The high touch frequency means our quotes are constantly stale, and getting
> filled before we can move them crystallizes losses not captured by the gap model alone."*
>
> **C.** *"E[Loss] = P(fill/day) × E[loss|fill]; E[LIP] = $0.043/day. Kill condition:
> P(fill/day) × $0.20 > $0.043. **Threshold: P(fill/day) > 21.5%**."*
>
> **D.** *"**CONDITIONAL(gate)**: gate on passing the P(fill) test."*

**Gemini conceded 3 of its own 4 ideas by name:** *"Trade 2: Conceded. The 0 fills vs 4 and
−2.2 to −3.9 c/ct bleed are indefensible. Trade 3: Conceded. The −45.71 c/ct historical loss
and N=1 population are fatal. Trade 4: Conceded. A 300s snapshot interval cannot observe or
monetize a 1s touch-retake."*

**Exchange status: RAN. 3 rounds, both directions, concessions on both sides.**

---

## 4. Resolution — C1 dies on the gate Gemini specified

Gemini's gate was `P(fill/day) > 21.5%`. Claude ran it on the existing tape
(`trades_all_ballot_20260815.json`, 1,832 public trades across 110 markets, 3 days):

| Cohort | Markets | Trades | Trades/market |
|---|---|---|---|
| **Thin pocket (in-band, rival touch ≤50)** | 12 | 198 | **16.50** |
| All other ballot markets | 98 | 1,634 | **16.67** |

**The thin pocket trades at the same rate as the thick markets.** Thinness is not absence of
flow — it is **absence of competing absorption**. That inverts the thesis: at 5.50
trades/market/day with our touch share at 0.935, **P(≥1 fill/day) ≈ 1.00**, against a kill
threshold of 0.215.

```
E[LIP]  /ct/day = $0.043
E[loss] /ct/day = P(fill) x E[loss|fill] = 1.00 x $0.20 = $0.200
NET             = -$0.157 /ct/day
```

`E[loss|fill] = $0.20` is measured twice independently (ballot −$0.2013, TEMP −$0.2278).

> ### C1 / Gemini-Trade-1: **DEAD — net −$0.157/ct/day.**
> The 4.86x share multiplier is bought by becoming the sole absorber of undiminished flow.
> **New grave D32.** Filed with its own reason: *the pocket's thinness was the rivals'
> verdict on it, not their oversight.*

---

## 5. THE SURVIVOR

### C2 — DEPTH-CONDITIONAL SEAT SCREEN — **TRADE-shaped (subtraction)**

**The finding.** Touch instability is a steep monotone function of rival touch depth, and
the ≥5c dislocations are **completely segregated**:

| rival touch depth (in-band) | pairs | gaps ≥5c |
|---|---|---|
| ≤250 | 1,582 | **7** |
| >250 | 1,631 | **0** |

**Fisher exact one-sided p = 0.0070.** Touch-move rate 4.04% vs 0.09% = **45x, z = 5.85**.

**The rule.** *Do not seat where rival touch depth is below 250 contracts.* Every ≥5c
dislocation in the panel — 7 of 7 — occurred below that line; **zero** occurred in 1,631
pairs above it.

**Why it is a subtraction and not alpha.** It does not find money; it removes the region
where the gap risk lives. This composes with the existing compiled stack (`ticks_behind≥1`
K=4 eject, post-sweep re-entry ban, family sweep-storm breaker) as an **admission screen
applied before seating**, where all three of those are triggers fired during a seat.

**It also kills its own most attractive use.** The screen's rule and C1's pocket are in
direct opposition: C1's 15 markets are exactly the sub-250 region the screen excludes. The
screen is what says no to the idea both models ranked first.

**Standing caveat.** One window close, one family, 3.7h, 110 co-moving markets. The 45x
ratio is decisively powered; the **absolute** rates rest on 36 touch moves in the thin bins.
The screen is a *gate*, not a P&L claim.

### Kill test — cost and threshold

| Item | Value |
|---|---|
| **Test** | Re-run the depth-binned table on the next **3** window closes using the existing capture scripts (Mac + VPS, already built, already scheduled) |
| **Cost** | **$0 and ~25 minutes** of analysis (capture is automated; no capital, no orders) |
| **Accumulates** | ~4,700 pairs/night ⇒ ~14,000 additional in-band pairs |
| **PASS** | ≥5c gap rate stays **0** in the >250 bin across ≥6,000 in-band pairs, and the thin/thick touch-move ratio stays >10x |
| **KILL** | any ≥5c gap appears in the >250 bin at a rate within 2x of the ≤250 bin — the segregation was a one-window artifact |

---

## 6. New graves filed tonight

| # | Idea | Killing number |
|---|---|---|
| D30 | Deep-book churn as early warning for touch moves | 0.0122 (n=983) vs 0.0140 (n=3,631); **z=−0.46** |
| D31 | Depth-bleed share timing (seat late) | −8.2%/3.7h ⇒ ≤8.9% relative share gain |
| D32 | Thin-rival in-band LIP pocket | P(fill/day)≈1.00 vs 0.215 threshold; **net −$0.157/ct/day** |
| D33 | Post one tick behind the touch | 0 fills in 104.3 seat-h at touch vs 4 in 48.8 behind; df=5000 halves subsidy |
| D34 | End-of-window taker sweep on decay | decay −8.2%/3.7h smooth and monotone; prior −45.71 c/ct |
| D35 | Restore the 1c spread after transient widening | touch re-taken ~1s vs our 300s observation interval |

Plus **D2 strengthened**: 0 takeable stale asks and 0 locked books in 4,834 snapshots.

**Graveyard: 114 → 120.**

---

## 7. Reproduction

Analysis scripts (scratchpad, this session):
`an.py` (spreads/locks/stability) · `an2.py` (churn predictivity, depth trend) ·
`an3.py` (persistence, thin cohort, hazard) · `an4.py` (Gemini's depth-binned test) ·
`an5.py` (share-vs-hazard trade-off)

Gemini prompts: `gp.txt` (round 0), `gp2.txt` (round 2 cross-exam), `gp3.txt` (round 3).

Data: `/Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research/terminal_capture_20260815.jsonl`,
VPS `ubuntu@129.146.115.241:/home/ubuntu/kalshi_data/terminal_capture_20260815.jsonl`,
`trades_all_ballot_20260815.json`.

**Nothing in this document authorizes capital, a seat, an order, or an allowlist change.**
