# IDEATOR LANE — SOROS/EVENT archetype (scheduled-information structure)

**Date:** 2026-08-16 · **Organ:** `ideation-organ-SPEC.md` · **Graveyard at entry:** 122
**Fuel:** the calendar of KNOWN information events vs Kalshi market structure around them.
**Read-only. No orders placed. No capital committed.**

---

## 0. The fuel, measured (all verified today, keyless public API via VPS)

### 0.1 Verified event dates
NFP/U3 print **Fri 2026-09-04** (`KXU3-26AUG` closes `2026-09-04T12:29Z`, 08:29 ET).
CPI print **Fri 2026-09-11** (`KXCPIYOY-26AUG` closes `2026-09-11T12:29Z`).
FOMC **Wed 2026-09-16**. NVDA call **Wed 2026-08-26** (`KXEARNINGSMENTIONNVDA-26AUG26`).
**Series that do not exist on Kalshi:** initial jobless claims (`JOBLESS` listed in the series
index, **0 open markets**), EIA weekly petroleum status, weekly crude/natgas inventories,
Freddie Mac FRM weekly. **The Thursday-claims / Wednesday-EIA lane in the task brief has no
instrument.** That angle is void before it starts.

### 0.2 The instrument that actually carries the flow — `KXAAAGASD`
Daily cumulative ">$X" ladder, 17 strikes on a 0.005 grid, one market per calendar day.
Opens 12:00Z (08:00 ET), closes **03:59Z (23:59 ET)**, settles on AAA's national average
published **~08:00–09:00Z the next morning** — the book shuts **4–5 h before the number exists**,
and opens ~4 h **after** the prior morning's publication (prior realized value public and fresh).

| Event | Volume (ct) | Settle | Δ vs prior |
|---|---|---|---|
| 26AUG10 | 342,092 | 4.0075 | — |
| 26AUG11 | 254,204 | 4.0125 | +0.5c |
| 26AUG12 | 231,519 | 4.0375 | +2.5c |
| 26AUG13 | 255,060 | 4.0725 | +3.5c |
| 26AUG14 | 250,240 | 4.0775 | +0.5c |
| 26AUG15 | 214,670 | 4.0725 | −0.5c |
| 26AUG16 (live) | 178,225 in 14h, OI 125,240 | — | — |

Median spread **1c**, **liquidity_dollars = 0** (no LIP subsidy anywhere in this family).
Weekly sibling `KXAAAGASW-26AUG17`: 357,389 ct, OI 196,414, 1c spread.
Our own exhaust: **271 fills / 7,211 ct**, 32% taker, fee $0.0019/ct.

### 0.3 The macro print ladders — front month is everything
| Series | front (26AUG) | 26SEP | 26OCT | 26NOV |
|---|---|---|---|---|
| KXU3 vol / spread | 196,416 / 2c | 21,237 / 5c | 10,326 / 7c | 4,154 / 5c |
| KXU3 **v24h** | 11,155 | **1** | **7** | **67** |
| KXCPIYOY vol / spread | 81,338 / 2c | 11,034 / 30c | — | 10,025 / 45c |
| KXCPICORE vol | 4,024 | 505 | 507 | 2,275 |

**Structural fact that kills a whole family of ideas: every front-month macro ladder closes
60 seconds BEFORE its own resolution event** (12:29Z vs an 08:30 ET print). There is no
post-print reaction window on Kalshi at all. The event is a *terminator*, never a *catalyst*.

### 0.4 Our own realized money — `KXEARNINGSMENTION`
~19 word-strikes per scheduled, publicly-webcast, transcribed earnings call.
**53 settled word-markets, 14 companies, 5,890 ct: +$481.95 realized, +8.18 c/ct**,
win rate 52.8%, company-clustered mean $34.43, **clustered t = +1.89 on 14 clusters**.
Fills spanned 2026-07-28 → 2026-08-06 = **10 calendar days ⇒ $48.20/day in-season**.
+8.18 c/ct is the largest per-contract number anywhere in this domain, and it is cash.

---

## 1. THE MEASUREMENTS (run this burst, cheapest-decisive-first)

### TEST A — who is the fish in `KXAAAGASD`? (41,343 trades / 1,953,342 ct / 8 settled events)
Markout of every trade vs actual settlement, signed by taker side:

| Cell | Taker | **Maker** | t | n |
|---|---|---|---|---|
| ALL | +1.71 c/ct | **−1.71** | +10.87 | 41,343 |
| last 30 min to close | +3.13 | **−3.13** | +2.76 | 4,243 |
| last 60 min to close | +3.32 | **−3.32** | +2.86 | 7,636 |
| first 30 min from open | +3.20 | **−3.20** | +4.56 | 1,168 |
| **in-band 5–95c** | **+4.88** | **−4.88** | **+11.23** | 33,810 / 742,934 ct |
| wings <5c or >95c | −0.23 | +0.23 | −0.83 | 7,533 |

**The maker is the fish in the highest-throughput non-crypto family on the exchange.**

### TEST B — back-month macro capacity
Best back-month book trades **67 ct/day** (KXU3-26NOV); most trade 0–7. At **100% share**,
a full 2.5c half-spread, and **zero** adverse selection: **$1.68/day** vs a $20–50/day bar.

### TEST C — is the informed-taker edge copyable? (my own idea, tested against myself)
Copy taker direction, pay the next printed price:
lag 0m **+3.08** · 1m +3.15 · 5m +3.11 · 15m +3.17 · **60m +3.05 c/ct**, day-clustered
**t = +2.31, 8 clusters**. Edge survives a 60-minute lag ⇒ **not a latency race**.
Per-day: −0.14 | **+10.24** | +2.59 | +0.62 | +6.62 | +3.40 | +0.69 | −1.64.
**Leave-one-out: drop Aug09 and the other 7 days average +1.73 c/ct — BELOW the ~1.75 c/ct
taker fee at 50c.** 8 clusters < the n≥10 power rule (§2.4). Reported as CONDITIONAL by me,
not as a trade.

### TEST D — earnings-mention maker vs taker (Gemini's preregistered kill on my C6)
| Side | ct | c/ct | company-clustered t |
|---|---|---|---|
| MAKER | 4,249 | **+6.27** | +1.29 (13 clusters) |
| TAKER | 1,642 | **+13.13** | **+1.94 (9 clusters)** |
| MAKER band 15–85c | 4,189 | +6.54 | |
| **TAKER band 15–85c** | 1,404 | **+14.97** | |
| MAKER wing <15c | 56 | −13.00 | |
| TAKER wing <15c | 25 | −14.84 | |
| TAKER wing >85c | 213 | +4.33 | |

**My C6 hypothesis is inverted and dead by the adversary's own threshold.** The wings are
negative on **both** sides — an independent reconfirmation of D14 and A46 in a new family.

---

## 2. THE TEN IDEAS — mechanism, fish, grave, kill test, verdict

### S1 — Earnings-call word base rate, taker-only, in-band 15–85c
**Fish & why:** the counterparty prices each word-strike on news-cycle salience — "will they say
*tariff*, *AI*, *recession*" — and never opens last quarter's transcript. Management scripts are
written before the call and are heavily autocorrelated quarter-to-quarter; the base rate over a
company's own prior 4 transcripts is free, public, and available days early. The scheduled event
(the call) is what forces the mispricing to resolve.
**Fuel:** our realized **+14.97 c/ct taker in-band**, 1,404 ct, 9 company clusters, t=+1.94;
whole book +$481.95 = **$48.20/day in-season**.
**Graves:** nearest is **D28** (fundamentals/base-rate gate on ballot seats is *anti-predictive*).
Distinct: D28's base rate was a **gate on which subsidy seat to occupy**; here the base rate **is
the contract's fair value**. Also near **A15** (CPI-book maker 100% adverse) — distinct: taker side,
non-macro, and the measured sign is positive not negative.
**Preregistered kill:** realized **< +2.0 c/ct net of fees** over the next 10 company calls
(≥50 word-markets) ⇒ DEAD. (Gemini's threshold, accepted verbatim.)
**Kill test cost:** transcripts $0 (IR sites / 8-K). ~$150 capital at 25 ct × ~20 strikes,
**~120 min of build + 4 calls**. Next windows: NVDA **2026-08-26**, then the Sep/Oct season.
**VERDICT: CONDITIONAL(gate: ≥ +2.0 c/ct net over ≥10 company clusters, prospective)** — the
only survivor, and the only lane in this burst backed by realized cash rather than a backtest.

### S2 — Duty-cycle honesty check on S1 (the capacity gate, stated as its own idea)
**Mechanism:** earnings season is ~3 weeks × 4/yr ≈ 84 trading days. $48.20/day in-season
amortizes to **$11.1/day** across the year. The idea only clears the bar if the off-season is
filled by something else, or if per-call size scales.
**Fuel:** 5,890 ct over 10 days = 589 ct/day ≈ $300 notional/day — capital is *not* the binding
constraint; **calendar supply is**.
**Graves:** **A33** (drought series, $0.77/day capacity cap), **A55** (KXHEADLINE ceiling $23/day).
Distinct: those were capped by *pool size*; this is capped by *duty cycle* and is fixable by
widening the company universe rather than by taking more share.
**Kill:** if 10 calls' worth of qualifying strikes (|price − base rate| ≥ 20c) numbers **< 40 in a
full season**, the lane cannot be scaled ⇒ DEAD on supply.
**Cost:** $0, ~30 min — count qualifying strikes across one already-passed earnings week.
**VERDICT: CONDITIONAL(gate: ≥40 qualifying strikes per season).**

### S3 — `KXAAAGASD` maker seat, any time bucket
**Fish:** us. **Kill:** Test A — maker **−1.71 c/ct** over 1,953,342 contracts (t=+10.87 against),
**−3.13 c/ct** in the last 30 min, **−3.20 c/ct** in the first 30 min. Every bucket is the wrong sign.
**Graves:** **A73** (captured maker round-trip −1.00c in all six top-volume families) — this
extends A73 into the single highest-throughput non-crypto family and makes it *worse*, −1.71c.
**VERDICT: DEAD(−1.71 c/ct on 1.95M contracts, t=+10.87).**

### S4 — "Overnight information-gap fade": make both sides in the last 30 min because the AAA
number is already determined and nothing can move it *(Gemini's Idea 5 — adopted, then killed)*
**Claimed fish:** late-day noise traders "trading on nothing."
**Kill:** exactly inverted. Late-day **takers are the informed side**, maker −3.13 c/ct, t=+2.76.
Gemini's own preregistered kill ("net loss over any 5-day week") fires on **7 of 8 days**.
**Graves:** **A77** (expiry evacuation −45.71 c/ct), **A78** (pre-close freeze population N=1).
**VERDICT: DEAD(−3.13 c/ct, 4,243 trades). Gemini CONCEDED by name.**

### S5 — Macro calendar roll-down: rest inside the wide back-month spread and harvest the
scheduled compression when it becomes front month *(Gemini's Idea 2 and its funding pick)*
**Fish:** traders paying a 5–45c liquidity premium for immediacy in a book scheduled to tighten
to 2c on a known date. The mechanism is real — the spread *does* compress 5c→2c and volume 10×.
**Kill:** capacity, not compression. Best back-month book = **67 ct/day**; at 100% share, full
2.5c half-spread, **zero** adverse selection ⇒ **$1.68/day**, 12–30× under bar. Test A supplies
the adverse-selection term and it is negative.
**Graves:** **A20** (farmer preseated in 95% of 764 windows), **A57** (rotating-seat column).
**VERDICT: DEAD($1.68/day ceiling vs $20/day bar). Gemini CONCEDED by name, including that its
own preregistered kill was misspecified.**

### S6 — Front-month print-day taker on KXU3 / KXCPIYOY / KXPAYROLLS
**Would-be fish:** nobody. **Kill, two independent ways:**
(i) *Structural* — the ladder closes at 12:29Z, **60 seconds before the 08:30 ET print**. There is
no post-information trading window in existence, so no reaction trade can be constructed.
(ii) *Empirical* — the family census (2026-08-15) found the one clean unconfounded scheduled print
(BLS CPI, Aug 12) was a **LOCAL MINIMUM** of hazard in decade-dated macro markets: trade counts
87 → 66 → 32 → **23 (release day)** → 13 → 12. Prints drain these books, they do not fill them.
**Graves:** **D21**, **A85**, **D20**.
**VERDICT: DEAD(close is T−60s to the print; release day is a hazard minimum, 23 vs 87 trades).**

### S7 — FOMC 2026-09-16 as a taker door via `KXFED` (87 markets listed since 2025-10-13)
**Fish:** none identified. CME FedWatch publishes the same distribution free and earlier.
**Graves:** **D21** verbatim — *"CME FedWatch public and free; Kalshi calibrated everywhere except
post-streak open."* No distinctness available; this is a re-tread and is discarded as such.
**VERDICT: DEAD(D21) — re-tread, not re-tested.**

### S8 — Post-streak open in the `KXAAAGASD` daily ladder
**Mechanism:** D21's one named exception is the **post-streak open**. Here the open sits 4 h after
a fresh public print, so the opening ladder is a pure extrapolation of a same-sign run.
**Fish:** the open-price setter over-extrapolating a physical, mean-reverting index.
**Fuel:** deltas +0.5, +2.5, +3.5, +0.5, −0.5 c/day; a run of 4 positives Aug11→Aug14.
**Power:** the settled endpoint exposes **12 events**; streak ≥2 subsets give **n = 3**.
**Per §2.4 this is UNDERPOWERED and may not be reported as a kill OR as a survivor.**
Gemini's threshold (mean streak-open delta must exceed +2.5 c/day over n≥10) cannot be evaluated.
**Kill test cost:** **$0**, ~10 min/day of free logging for ~5 weeks to reach n≥10 streaks.
**VERDICT: CONDITIONAL(gate: n≥10 streak-opens accumulated, then |implied − realized| ≥ 2.5c).**
Labelled **UNDERPOWERED**, not a receipt.

### S9 — Follow the informed taker in `KXAAAGASD` at a lag
**Mechanism:** Test A says taker flow is informed by +4.88 c/ct in-band. If the information is
slow (a physical index), a copier should capture some of it without racing.
**Fuel:** +3.05 c/ct at a **60-minute** lag, day-clustered t=+2.31.
**Kill (mine, run and reported against myself):** leave-one-out — drop Aug09 and the remaining
7 days average **+1.73 c/ct, below the 1.75 c/ct taker fee**; and 8 clusters < the n≥10 rule.
The measurement also uses the *next printed price*, not the executable ask, so it is optimistic
by up to the 1c spread.
**Graves:** **D1** (follow-the-elephant, excess +0.1c vs +2.0c required) — distinct population
(D1 was 97 ballot markets with 0 takeable stale asks; this is a 250k-ct/day daily commodity
ladder with 1c spreads), but the *shape* of the kill is identical and that is a warning.
**VERDICT: CONDITIONAL(gate: ≥20 day-clusters AND leave-one-out mean ≥ +3.5 c/ct at the
executable ask).** Not fundable at n=8 with one-day carry.

### S10 — Gas wings (<5c / >95c) on either side, and the general wing rule
**Kill:** taker −0.23 c/ct (t=−0.83, n=7,533); maker +0.23 c/ct — statistically zero. In the
earnings family the same cells read **maker −13.00 / taker −14.84 c/ct** below 15c.
**Graves:** **D14** (deep-cheap bids, win rate 0.000, −$404), **A46** (99c maker-NO), **A26**
(15/16 top seats settled NO). This burst reconfirms them in two *new* families independently.
**VERDICT: DEAD(0.23 c/ct ≈ 0 in gas; −13 to −15 c/ct in earnings wings).**
**Standing rule extracted: every strategy in this domain lives in 15–85c or dies.**

---

## 3. CLAUDE ↔ GEMINI EXCHANGE (condensed, per §2.6)

**Round 1 — Gemini generates 6 independently** (did not see Claude's ideas). Verbatim-condensed:
1. *Weekend gas-price stickiness* — sell a 1c straddle Sunday night; fish = weekday momentum
   traders who don't adjust for low weekend variance. 2. ***Macro calendar roll-down*** — rest
   inside the wide back-month spread, harvest scheduled compression; fish = payers of the
   immediacy premium. **[Gemini's funding pick]** 3. *Pre-call sentiment fade* — maker-NO >95c,
   maker-YES <5c in the last 60 min before a call; fish = social-media-driven retail.
   4. *Earnings semantic correlation* — driver word vs passenger-word basket; fish = traders
   pricing each word in isolation. 5. *Overnight gas information-gap fade* — make both sides in
   the last 30 min because the number is already determined; fish = late-day noise traders.
   6. *Macro serial-correlation fade* — fade the new front month's overreaction after a print.
   Gemini's own summary: *"the fuel is moderately supportive."*

**Round 1 — Claude attacks, citing graves.** Idea 1 and 3 collide with **D14/A46** (wings) before
any test; Idea 4 collides with **A29** (0 violations in 34,614 pairs; 3 in 3,185,799) and with
the fact that word-strikes are **not nested**, so no arbitrage relation exists to violate; Idea 6
collides with **S6's structural close** — there is no post-print book to fade because the front
month has already settled and the new front month is the 67-ct/day book of Test B.

**Round 2 — Claude runs the tests on data and reports, including against himself.**
Tests A/B/C/D above were run and handed to Gemini in full, with the losing results for Claude's
own C6 and C9 included.

**Round 2 — Gemini's named concessions (verbatim):**
> *"Idea 5: Overnight Gas Information Gap Fade. **CONCEDE.** Test A data is definitive. A maker-side
> loss of −3.13 c/ct (t=+2.76 against) in the target window directly refutes the hypothesis. The
> preregistered kill condition was met (loss on 7/8 days). The premise that late-day takers are
> uninformed is inverted by the data."*
> *"Idea 2: Macro Calendar Roll-Down. **CONCEDE.** Test B correctly identifies that the idea fails
> on capacity, not spread dynamics. Daily volume of <70 contracts in the most active back-month
> book makes the strategy unable to clear the $20–50/day bar, even with perfect execution. My
> preregistered kill was misspecified; the binding constraint is volume."*
> **Gemini conceded its own funding pick.**

**Round 2 — Gemini attacks Claude, with preregistered thresholds:**
- On **C1/S1**: *"You are betting the market is dumb money; you may be the dumb money"* — the price
  may deviate from the base rate for a correct forward-looking reason. **Kill: < +2.0 c/ct net over
  the next 10 calls (≥50 word-markets).** Verdict TRADE-shaped. → **Threshold accepted verbatim.**
- On **C2/S8**: deltas of 0.5–3.5c are inside spread + fee. **Kill: mean streak-open delta fails to
  exceed +2.5 c/day over n≥10 streaks.** Verdict DEAD. → **Claude rebuts: only n=3 streaks exist on
  the endpoint, so this is UNDERPOWERED under §2.4 and cannot be scored either way. Gemini's DEAD
  verdict is rejected on power, not on sign.**
- On **C6**: *"rests on a correlation from a single losing company (PLTR), an n=1 anecdote."*
  **Kill: mean realized maker c/ct ≤ mean realized taker c/ct.** Verdict TRADE-shaped.

**Round 3 — Claude runs Gemini's C6 kill immediately (Test D).**
**MAKER +6.27 c/ct ≤ TAKER +13.13 c/ct.** The threshold fires.
> **CLAUDE CONCEDES C6 BY NAME.** My hypothesis that the maker side is the profitable side in word
> markets is **inverted**: the taker side earns 2.1× the maker side, and in-band taker is +14.97
> c/ct. Gemini's "n=1 anecdote" objection to my PLTR reasoning was correct on process; its
> TRADE-shaped verdict was wrong on direction. Both sides lose something in this round.

**Round 3 — Gemini's revised funding pick:** *"C1: Earnings-Call Word Base Rate. It is the only
idea family with a large, statistically significant, realized positive cash return (+8.18 c/ct in
Test D)... The other viable ideas are best viewed as filters or refinements."*
**Claude concurs — with the correction that Test D's +8.18 c/ct is company-clustered t=+1.89 on 14
clusters, which is CONDITIONAL, not "statistically significant." Gemini's word choice is
overstated and is not adopted.**

---

## 4. VERDICT TABLE

| # | Idea | Verdict |
|---|---|---|
| **S1** | Earnings-call word base rate, taker, in-band 15–85c | **CONDITIONAL(≥ +2.0 c/ct net over ≥10 company clusters)** — funded test |
| S2 | S1 duty-cycle / supply gate | CONDITIONAL(≥40 qualifying strikes per season) |
| S3 | KXAAAGASD maker seat, any bucket | **DEAD(−1.71 c/ct, 1.95M ct, t=+10.87)** |
| S4 | Overnight information-gap fade *(Gemini 5)* | **DEAD(−3.13 c/ct; 7/8 days)** — conceded |
| S5 | Macro calendar roll-down *(Gemini 2, its pick)* | **DEAD($1.68/day ceiling)** — conceded |
| S6 | Front-month print-day taker | **DEAD(close = T−60s; release day 23 vs 87 trades)** |
| S7 | FOMC 09-16 via KXFED | **DEAD(D21)** — re-tread |
| S8 | Post-streak open, KXAAAGASD | CONDITIONAL — **UNDERPOWERED, n=3 streaks** |
| S9 | Follow the informed taker at a lag | CONDITIONAL(≥20 clusters, LOO ≥ +3.5 c/ct at the ask) |
| S10 | Gas/earnings wings, either side | **DEAD(≈0 in gas; −13 to −15 c/ct in earnings)** |

**Void before testing (no instrument exists):** initial jobless claims (Thursdays), EIA weekly
petroleum status (Wednesdays), weekly crude/natgas inventories, Freddie Mac FRM. `JOBLESS` is in
the series index with **0 open markets**. The brief's Thursday/Wednesday lane has nothing to trade.

**Distinctness from the standing survivor:** the C2/G1 stale-bid fade in
`ideation-watchers-20260816.md` is a **cross-venue, live-in-play, one-leg directional MLB** trade
gated on Kalshi bid depth. **S1 shares no venue pair, no sport, no in-play clock, and no oracle** —
its information source is the company's own prior transcripts, its event is a scheduled call, and
it is a taker in a 19-strike word ladder. No MLB idea is proposed in this burst.

---

## 5. THE ONE COSTED KILL TEST (per §2.5)

**S1 — Earnings-call word base rate.**
Build: scrape the company's own prior 4 transcripts (IR site / 8-K, free), count word frequency
per strike, flag |market price − base rate| ≥ 20c, **restrict to 15–85c**, **taker only**.
**Cost: $0 data, ~120 min build, ~$150 capital** (25 ct × ~20 qualifying strikes × ~4 calls).
**First window: NVDA call 2026-08-26** (`KXEARNINGSMENTIONNVDA-26AUG26` already listed —
27,177 ct, OI 18,698, 4c spread, 19/19 two-sided).
**Pass:** ≥ +2.0 c/ct net over 10 company calls / ≥50 word-markets. **Fail ⇒ grave.**

---

## 6. LEDGER LINE

| Date | Burst | Fuel | Ideas (C/G) | Survivors | New graves | Graveyard after | Tokens |
|---|---|---|---|---|---|---|---|
| 2026-08-16 | `ideator-soros-20260816.md` | 41,343 KXAAAGASD trades / 1.95M ct / 8 events; 53 settled KXEARNINGSMENTION markets / 5,890 ct realized; front-vs-back-month structure on 4 macro ladders | 10 / 6 | **1** (S1, conditional) | **6** (S3,S4,S5,S6,S7,S10) | **128** | ~95k |
