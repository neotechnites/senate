# IDEATOR LANE — VENUE-MECHANICS — 2026-08-16

Archetype: what is visible-to-the-diligent before visible-to-the-lazy; execution mechanics as edge.
Run under `ideation-organ-SPEC.md`. Graveyard consulted: **122 graves** (sqlite `graveyard`).
Prior venue-mechanics lane: `ideation-burst-20260815.md` §2 (V1–V5). Prior fee lane: §1 (H1–H8) — this
burst deliberately goes elsewhere and does not re-run HOUSE-FEE.
Probing: read-only public GETs from VPS `129.146.115.241`. **No orders placed. No demo probes.**
Scripts: `/private/tmp/.../scratchpad/p{2,3,4,5,6,7,8}.py`; outputs `~/p{3,4,5,6,7,8}.json` on VPS.

---

## 0. HEADLINE — a 19,997-market surface nobody in the graveyard has looked at, and it is dead

Kalshi has shipped a **multivariate-event (MVE) parlay product**. Measured live today:

| Fact | Number |
|---|---|
| Open MVE markets in `/markets?status=open` | **19,997 of 20,000 scanned (99.985%)** |
| `price_level_structure` | `deci_cent` (0.1c tick) on **19,997/19,997**, vs 1c on ordinary markets |
| Legs enumerated in `mve_selected_legs` (exact ticker + side) | **yes**, leg counts 2…60 (mode 4) |
| `is_provisional: true` | 17,375 / 19,997 (86.9%) |
| Markets with **any bid** | **0 / 19,997** |
| Markets with an ask | 116 / 19,997 (0.58%) |
| Two-sided books | **0** |
| `/orderbook` yes+no arrays where `yes_ask_dollars` is populated | **empty** → the ask is a **synthetic house quote**, not a CLOB order (sizes 2–3,912 ct) |
| `no_ask_dollars` | **1.0000 on 100/100 scored** — you may only BUY from the house, never sell |
| House ask vs product-of-leg-mids | median **+2.10c**, mean **+3.99c**, **0/100 negative**, max +51.03c (+1284%) |
| Fréchet lower-bound arb (`ask < Σleg_bid − (n−1)`) | **0 / 85 violations**, best gap **−0.21** (21c from arb) |
| 24h prints | 5,619 MVE prints / 2,980 distinct tickers; **median 1.0 print/ticker**; **397/2,980 (13.3%)** print twice |
| Markets where `volume_fp > open_interest_fp` | **0 / 582** — **zero round-trips have ever occurred on this surface** |

**This is grave A40 (PolyUS MVE parlay engine) reproduced on Kalshi, with better instrumentation
and the same verdict.** Distinction from A40: Kalshi enumerates the legs exactly and posts a sized
house ask, so fair value is *computable*; A40 could only observe empty books. It dies anyway, on a
harder number: not "empty books" but **0 round-trips in 582 markets**.

Second correction banked: **the "`tickers=` batch silently drops >2" receipt is WRONG.** Re-run on 12
durable tickers (KXHIGHNY/KXBTCD/KXCPICOREHEAD/KXEOWEEK), n=1,2,3,5,10,12 returned **1,2,3,5,10,12,
0 missing, 0 extra**. The original truncation was MVE ephemeral tickers evaporating between calls.
Separately: `tickers=""` is silently ignored and returns a full unfiltered 100-market page.

---

## 1. CLAUDE'S 10 (mechanism-first, graveyard-cited, verdict with numbers)

| # | Idea | Mechanism / who is the fish | Nearest graves + distinction | Cheapest decisive kill | Verdict |
|---|---|---|---|---|---|
| **C1** | **MVE leg-bound (Fréchet) arb** | `1_{all} ≥ Σ1_i − (n−1)` is model-free. Long parlay + short each leg + (n−1) cash has payoff ≥0; arb iff `ask < Σleg_bid − (n−1)`. Fish = the house's independence pricer on correlated legs | A29 nested-strike monotonicity (0/34,614); cwing (3/3.19M, $0.01). **Distinct:** joint-vs-marginal across *different events*, not strikes in one ladder | Ran inline, free, 20 min | **DEAD(0/85 violations; best gap −0.21; and 0 bids exist in 19,997 markets so the short-parlay leg is unbuildable at any price)** |
| **C2** | **Sole-bidder MM on a zero-bid surface** — post the only bid in 19,997 markets and buy exits from trapped parlay holders | 0 bids exist anywhere; a 0.1c-tick bid *is* the entire book. Fish = retail who bought the parlay from the house and wants out | A40 (empty books, ~17 prints each); A41 PolyUS durable rebate (13–43h since last trade). **Distinct:** legs enumerated ⇒ we can price the exit exactly | Ran inline, free, 15 min | **DEAD(0/582 markets have volume > open interest ⇒ zero round-trips have ever happened; median 1.0 print/ticker; 13.3% print twice. There is no exit flow to bid for)** |
| **C3** | **Snipe the synthetic house quote when it lags a leg gap** | The parlay ask is derived from leg books; a 6–25-tick leg gap must leave it momentarily stale | D1/D2 stale-quote sniping (0/97 takeable stale asks; 0 locked books in 4,834 snapshots). **Distinct:** a *synthetic* quote has a different staleness generator than a resting CLOB order | Analytic, free | **DEAD(an n≥2 parlay cannot be statically replicated from binaries — a stale ask is an unhedgeable directional bet, not an arb. Confirmed by C1: 0/85 within 21c of the replication bound)** |
| **C4** | **MVE print → leg-hedge lead** (see §4) | A parlay ticker is minted the instant a user builds it (`created_time == open_time` to the second) naming the exact legs; on the fill the house must hedge into the leg CLOBs. Fish = anyone reading only the leg books | D17 programs-feed lead time **ALREADY DEAD** (82/82 future programs ≤28.2h, 100% the 4 toxic 15-min families) — cited, not re-tread: this is a **flow** lead measured in seconds inside durable sports/econ legs, not a *listing* lead in days. D30 deep-book churn (z=−0.46) | Forward test, **$0, ~90 min** — spec'd in §4 | **CONDITIONAL(gate: §4)** — the only survivor |
| **C5** | **Fade the house parlay vig** (sell the +2.10c median overround back) | Median markup +2.10c / mean +3.99c over product-of-leg-mids, 0/100 negative — a persistent, measurable overround | D15/A48/A71 fee-and-rebate mechanics. **Distinct:** this is a *product* overround, not a schedule | Ran inline, free | **DEAD(`no_ask_dollars = 1.0000` on 100/100 — the vig is strictly one-way; there is no price at which the parlay can be sold)** |
| **C6** | **`tickers=` batch blindness** — rivals batching >2 tickers are silently blind on the tail | Fish = any rival quoting a ladder off one batched call | — (new) | Ran inline, free, 10 min | **DEAD(receipt corrected: 12/12 durable tickers returned across n=1,2,3,5,10,12; 0 missing. The defect does not exist)** |
| **C7** | **Discovery poisoning** — `/markets?status=open` is 99.985% MVE, so 20 pages of 1,000 return **3** real markets; naive scanners never see the tail | Fish = rivals who enumerate inventory by paging `/markets` | D32 thin-rival in-band LIP pocket. **Distinct:** a *discovery* asymmetry rather than a depth one | Ran inline, free | **DEAD(the asymmetry is real and large, but what it hides is thin/unquoted inventory, already killed at −$0.157/ct/day by D32; P(fill/day)≈1.00 vs the 0.215 threshold)** |
| **C8** | **`client_order_id` dedupe outliving order lifetime** | A reused coid is rejected forever, even after the order is gone | A79 SCALP refusal-dominates (0 orders lifetime). **Distinct:** a silent no-op, not a refusal | Analytic | **DEAD as alpha** — it is our own namespace, no rival is exposed. **Promoted to a mistake-ledger invariant: a coid collision silently no-ops an intended order ⇒ phantom seat (believed seated, actually flat)** |
| **C9** | **`order_group_id` + STP `taker_at_cross`** — atomic multi-market posting with a shared exposure cap; enables a MECE ladder to be posted without partial-leg risk | Fish = anyone who must leg into brackets one order at a time | D12 maker-only MECE dutch book (BTC 28-bin SUM_ASK 103.90c / bid 94.90c, 0 executable); A28 ($8.50 board-wide, 15-month lockup = $0.02/day); A69 (pairs sum to 200.00 in 94.4%) | Analytic | **DEAD(dominated) — order groups make an already-dead strategy easier to express; 0 executable dutch books across three independent censuses** |
| **C10** | **`cancel → reduced_by` as a hidden-liquidity prober** | The synchronous `reduced_by` distinguishes "rested then cancelled" from "filled against invisible depth" | A5 censored queue test (**0.0% in every bucket, n=295,491**); A4 (level-loss 29%→18%/h) | Analytic + A5 | **DEAD(A5, n=295,491, 0.0% in every bucket — Kalshi's CLOB publishes full depth; there is no hidden liquidity for `reduced_by` to reveal)** |

**Score: 9 DEAD, 1 CONDITIONAL.** Per SPEC §2.4 no verdict above rests on n<10 except C6
(n=12 batch calls, above the bar) — all others are n∈[85, 295,491].

---

## 2. GEMINI'S INDEPENDENT 6 (round 1, blind to C1–C10)

| # | Gemini idea | Its own killing number/threshold |
|---|---|---|
| G1 | **Ticker-Blind Snipe** (funding pick) — rest maker on the 3rd ticker of a ladder that rivals' `tickers=` call silently dropped | fills on the 3rd ticker within 5s of a >3c move on ticker 1 or 2; threshold >0 |
| G2 | **LIP Rival-Fade Scalp** — invert the estimates feed, add size the moment a big rival exits | >25% drop in inverted rival depth followed by >10% accrual-rate rise in 5 min; threshold >1 instance |
| G3 | **Cancel-Ping Depth Probe** — 1-ct place+cancel; `reduced_by: 0` means it hit hidden liquidity | % of deep pings returning `reduced_by: 0`; threshold >0.5% |
| G4 | **Dumb Flow Harvesting** — use `is_taker` to find markets with high non-price-moving taker volume, quote only there | net P&L/fill after 1h; threshold >$0.005 |
| G5 | **Pre-Open Taker Imbalance** — >90% taker-buy in the first 30s of an `initialized` market ⇒ ride it | P&L of take at t+30s / close at t+90s; threshold >$0 |
| G6 | **Synchronous Fill-Cancel Race** — cancel out of the way of an incoming sweep, `reduced_by` scores the race | % cancels winning within 250ms; threshold >50% |

---

## 3. CROSS-EXAMINATION — condensed transcript (3 rounds, concessions named)

**ROUND 1 — Claude attacks Gemini, on data not rhetoric:**
- **G1:** premise falsified by my own re-run. 12 durable tickers, n=1,2,3,5,10,12 → 1,2,3,5,10,12, **0 missing**. The "drop" was MVE ticker evaporation. *The funding pick's mechanism does not exist.*
- **G2:** D31 — rival depth decays **−8.2% over 3.7h**, so share improves ≤8.9% relative = noise; D25 evacuation-eject caught **0/4** adverse fills at a 1-alarm/24-seat-h budget. The ">25% drop" event does not occur.
- **G3:** A5 — level-consumed-at-unchanged-price = **0.0% in every bucket, n=295,491**, vs his >0.5% threshold.
- **G4/G6:** re-skins of H3 (second maker leg fills only adversely, **−8.4c/fill**), D35 (touch re-taken in **~1s** vs our 300s observation), D33 (**0 fills in 104.3 seat-h**).
- **G5:** D17/D18 — the only pre-visible inventory is 4 toxic 15-min commodity families at **5,000–61,000 trades/mkt/hr**.

**ROUND 2 — Gemini's reply, verbatim-condensed:**
> "A1: Ticker-Blind Snipe. **Conceded.** The premise is false. A2: Cancel-Ping Depth Probe. **Conceded.**
> A3: LIP Rival-Fade Scalp. **Conceded.** The trigger event does not occur. A4: Pre-Open Taker
> Imbalance. **Conceded.** A5: Dumb Flow Harvesting / Synchronous Fill-Cancel Race. **Conceded.**"

**ROUND 2 — Gemini attacks C1–C10:**
> "C1 **Conceded** — unbuildable short leg. C2 **Conceded** — killing number: 0 round-trips in 582
> markets. C3 **Conceded** — a non-delta-one product cannot be statically replicated. C5 **Conceded**
> — `no_ask=1.0000`. C6 **Conceded**. C7 **Conceded** — friction, not alpha. C8 **Conceded** —
> operational hazard, not P&L. C9 **Conceded** — 0 executable dutch books across A28/A69. C10
> **Conceded** — killed by A5."
>
> **On C4 (his real attack, with a threshold):** "The strongest confound is **portfolio-level net
> hedging**. The house does not hedge one MVE; it hedges the net delta of its entire MVE book,
> possibly against offsetting flow on its main CLOB books. **Kill condition: correlation between
> signed MVE creation size ($) and the t+60s signed leg mid-change < 0.05.** Your test will fail
> because it assumes a 1:1 hedging relationship that does not exist."
>
> **On whether any money remains on MVE:** "**No.** This is not a market; it is a product shelf. Zero
> bids, zero round-trips, one-way `no_ask=1.0000`. Structurally identical to buying a lottery ticket
> from a kiosk. The only path to profit is a pure unhedgeable directional bet against a house that has
> priced in a median +2.10c vig. There is no structural edge."

**ROUND 3 — Claude presses with a new number; Gemini amends C4 and is forced to produce one new idea:**
- Claude: only **2,622/19,997 (13.1%)** MVE markets have `volume>0` ⇒ **86.9% of creations are never
  traded**, so a creation-triggered signal is 86.9% false-positive *before* the netting confound.
- Gemini: *"**Defend a filtered version.** The filter is **First MVE Trade**: act only after the MVE
  trades its first contract. The numeric threshold is `MVE_volume >= 1`."* — **Claude accepts this
  amendment**; C4 is restated in §4 as a *print*-triggered rather than *creation*-triggered signal.
  This is Gemini's one substantive contribution and it is credited by name.
- Gemini's mandated new idea, **G7 "Unsettled-Capital-Release Arbitrage"** (undercapitalized traders
  locked in settlement float of market A cannot trade correlated market B; threshold: expected
  mispricing in B > 1.5c/share). **Claude kills it inline:** the market object carries
  **`settlement_timer_seconds: 5`**. Capital is released in five seconds. There is no float window to
  arbitrage. **DEAD(settlement_timer_seconds = 5).** Gemini did not rebut.

**Concessions ledger:** Gemini conceded **16** items by name (G1–G6, C1–C3, C5–C10). Claude conceded
**2**: (a) the `tickers=`-drops-past-2 receipt was mine and it was **wrong** — corrected in §0;
(b) C4's trigger, amended from *creation* to *first print* on Gemini's filter.

---

## 4. THE ONE SURVIVOR — C4, as amended

**C4 — MVE-PRINT → LEG-HEDGE LEAD.** `CONDITIONAL`.

*Mechanism.* Every MVE parlay publishes its exact constituent legs and sides. The house is the sole
counterparty (0 bids, 116 synthetic asks, `no_ask=1.0000`). When a parlay prints, the house acquires
a joint-event exposure it can only neutralise by trading the **leg** CLOBs — which are durable,
liquid, non-toxic markets (MLB game lines, econ). The public trades feed carries the MVE print. If
the print is visible before the leg hedge lands, the leg book is predictable for that interval. This
is the *only* asymmetry on the surface that survives: everything else about MVE is a one-way shelf.

*Why it is not D17.* D17 killed the **programs feed as a listing lead** — 82/82 future programs start
within 28.2h and 100% are the four toxic 15-min commodity families. C4 claims **no listing lead at
all**; it is an order-flow lead measured in seconds, inside durable leg markets. Different feed,
different clock, different inventory.

*Preregistered kill test (both thresholds must pass; either failure ⇒ DEAD):*
1. **Lead exists.** For ≥200 MVE prints with `volume_fp ≥ 1`, measure the signed leg mid-move over
   t+0…+60s vs a matched same-market control minute drawn from the same session.
   **Threshold: mean signed move ≥ 1.0c in the leg direction with t ≥ 3.0, cluster-robust by leg market.**
2. **Gemini's netting gate.** Correlation between signed MVE notional and the t+60s signed leg
   mid-change. **Threshold: |ρ| ≥ 0.05** (Gemini preregistered <0.05 as the kill).
3. **Power floor (SPEC §2.4).** ≥200 prints on ≥30 distinct leg markets, else UNDERPOWERED, not a kill.

*Cost:* **$0, ~90 minutes wall clock** (read-only forward capture from the VPS: poll
`/markets/trades` filtered to MVE plus leg-market quotes at 1–2s cadence). No orders.
*Expected value if it passes:* leg markets are 1c-tick and liquid, so a 1.0c lead is one tick of
taker edge against a 0.33–1.75c taker toll — i.e. **it only pays in the wings**, and the wings are
D14/A45/A26 territory. Honest prior: **P(pass) ≤ 0.25**, and even on a pass it likely lands
CONDITIONAL again on the fee curvature rather than TRADE-shaped.

---

## 5. LEDGER LINE (append to SPEC §4)

| Date | Burst | Fuel | Ideas (C/G) | Survivors | New graves | Graveyard size after | Tokens |
|---|---|---|---|---|---|---|---|
| 2026-08-16 | `ideator-mechanics-20260816.md` | live read-only VPS census: 20,000 open markets, 19,997 MVE, 116 house asks, 30,000 24h prints, 582 MVE OI markets, 12-ticker batch control | 10 / 7 | **1** (C4, amended) | **16** (C1–C3, C5–C10, G1–G7) | **144** (DB count; 128 before this burst) | ~95k |

### New graves to insert into `graveyard`

```
C1 | MVE parlay Fréchet leg-bound arb | 0/85 violations, best gap -0.21; 0 bids in 19,997 markets
C2 | Sole-bidder MM on the zero-bid MVE surface | 0/582 markets with volume>open_interest = zero round-trips ever; median 1.0 print/ticker
C3 | Sniping the stale synthetic house parlay quote | n>=2 parlays are not statically replicable; 0/85 within 21c of the replication bound
C5 | Fading the house parlay vig | no_ask_dollars = 1.0000 on 100/100; markup median +2.10c is strictly one-way
C6 | tickers= batch-blindness snipe | receipt falsified: 12/12 durable tickers returned at n=1,2,3,5,10,12
C7 | /markets discovery poisoning as an edge | real (99.985% MVE) but hides only D32 inventory at -$0.157/ct/day
C8 | client_order_id dedupe as an edge | own-namespace only; reclassified as a phantom-seat invariant
C9 | order_group_id / STP taker_at_cross multi-leg posting | dominated: 0 executable dutch books (D12, A28, A69)
C10 | cancel reduced_by as a hidden-liquidity prober | A5: 0.0% in every bucket, n=295,491; no hidden depth exists
G1 | Ticker-blind 3rd-ticker snipe | premise false, 12/12 returned (Gemini conceded)
G2 | LIP rival-fade scalp | D31 -8.2%/3.7h decay; D25 0/4 (Gemini conceded)
G3 | Cancel-ping hidden-depth probe | A5 0.0%, n=295,491 vs >0.5% threshold (Gemini conceded)
G4 | Dumb-flow harvesting via is_taker | H3 -8.4c/fill second leg (Gemini conceded)
G5 | Pre-open taker imbalance | D17/D18, only pre-visible inventory is 4 toxic 15-min families (Gemini conceded)
G6 | Synchronous fill-cancel race | D35 touch re-taken in ~1s vs 300s observation (Gemini conceded)
G7 | Unsettled-capital-release arbitrage | settlement_timer_seconds = 5; no float window exists
```

## 6. SIDE-RECEIPTS BANKED (not ideas — facts for downstream docs)

1. `/markets?status=open` is **99.985% MVE** (19,997/20,000). Any inventory enumeration must go via
   `series_ticker`/`events`, never by paging `/markets`.
2. `tickers=` is **correct** for up to at least 12 tickers; `tickers=""` is silently ignored and
   returns an unfiltered page. **The earlier "drops past 2" receipt is retracted.**
3. MVE markets are **`deci_cent`** (0.1c tick) — the only 0.1c surface found on Kalshi. Legs remain 1c.
4. `settlement_timer_seconds: 5` — collateral is released ~5s after close.
5. MVE `mve_selected_legs` gives exact leg tickers + sides; total MVE open interest **545,480 ct**
   across 582 markets, and **not one contract of it has ever been closed by a trade**.
