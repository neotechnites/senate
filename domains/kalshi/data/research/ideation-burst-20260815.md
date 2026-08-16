# Ideation Burst 2026-08-15 — 4 archetype lanes + Gemini cross-check

Template discipline: `/Users/ryanwhitehead/Documents/senate/archive/enchiridion_legacy/work/steer-ideation-jul27.md`.
Every idea: **mechanism (who is the fish and why)** → **cheapest decisive kill test ($ and minutes)** → **verdict**.
All venue access read-only, keyless GETs only. No orders placed. Small-n labelled everywhere.

---

## 0. What this burst actually produced (read this if you read nothing else)

Three numbers are new and load-bearing, and two of them came out of tests run inline today:

1. **39 of 3,935 live LIP programs have `target_size_fp` < 1000.** Everything we have ever modelled
   assumed 1000. Six of those 39 are in-band, fill-safe, and score **22–62 $/day per $100** against
   the house 6.50 bar and our **realized ballot 2.04**. Two have rival qualifying depth of **1 contract**.
2. **Our own 2-month exhaust, joined to actual settlements, says the "45–55c is the only band where
   we're not the fish" claim is an artifact of size concentration.** Fill-level the 40–55c edge is
   **+0.7c ± 5.2c (n=91)** and 67% of its dollars are one series. What IS decisive: **outside 40–55c
   we are −8.4c/fill on n=595 (t ≈ −4.2), −$1,197.65 over two months.**
3. **Mirroring the informed taker at 0.94–0.995 in TEMP hourlies nets +$1,231 / +1.22c/ct over 374
   settled market-hours (t=+5.1, 237/243 markets profitable), out-of-sample** — on the same corpus
   whose maker side the hourly census killed. It dies at +2c of slippage. That is the whole gate.

---

## 1. LANE: HOUSE-FEE — the $0-maker asymmetry beyond LIP

Fee facts used throughout: maker `fee_cost: 0.000000` (venue-confirmed on our ballot fills);
taker `ceil(0.07·count·p·(1−p))` to **1/100 cent** (receipt-corrected in terminal-taker-spec).
Taker toll peaks at **1.75c/ct at p=0.50** and is **0.33c at p=0.05** — a 5.3× curvature.

| # | Idea | Mechanism / who is the fish | Cheapest decisive kill | Verdict |
|---|---|---|---|---|
| H1 | Mid-band 1c-wide two-sided quote (49/51) in slow markets | Taker crossing us pays 1.75c and we pay 0; we need only 0c of edge to break even where they need 1.75c | Already run: our own exhaust, 40–55c fill-level edge **+0.007 ± 0.052 (n=91)**. Free-fee advantage exists but the sample cannot show it | **CONDITIONAL** — needs n≥400 mid-band fills before any capital; see H2 for why it is not dead |
| H2 | **Fee-curvature is backwards from the tape, and that IS the edge** | Theory: a 1.75c toll at mid means only takers with >1.75c of conviction cross → mid-band takers should be the *most* informed. Tape says the opposite: TEMP prints at **p=0.40–0.55 lose −2.34c/ct across 513 prints, 20/48 markets profitable**. Mid-band takers cross a 1.75c toll and are still wrong. The fish is a fee-insensitive discretionary crosser | Confirmed inline on 374 settled TEMP markets. Extension: repeat the 0.40–0.55 taker-P&L cut on one non-weather settled family. **$0, 25 min** | **TRADE-shaped (as the theoretical basis for the mid-band-only gate, Z2/H1)** |
| H3 | Zero-fee round-trip scalp (maker in, maker out, capture 1 tick) | Both legs free, so 1 tick of spread is 1 tick of profit | Requires two maker fills. Our exhaust: **70–86% of our fills in every losing band were maker fills** — the resting side is the side being sold to. Second maker fill only arrives when we are wrong | **DEAD** — the second leg only fills adversely; measured −8.4c/fill in the wings |
| H4 | Maker-only MECE dutch book (free hedge legs) | A maker pays 0 across n legs; a taker pays Σfee, so a maker can hold a bracket set no taker can arb | Graveyard: BTC 28-bin ladder SUM_ASK **103.90c / bid 94.90c**; 0 executable in the settlement-lock census, pairs sum to 200.00 in 94.4% | **DEAD (re-killed, prior receipts)** |
| H5 | Free requote / join-and-chase (rung1 is retreat-only today) | Cancel+replace costs $0 as a maker; the competing ballot farmer requotes in **0.08–0.9s** while rung1 never requotes | The forensics answer it: books were **frozen for 1–5h then annihilated 6–25 ticks in one 60s bar**. There is no drift to chase. Requoting cannot outrun a gap | **DEAD for adverse-selection purposes**; keep as a *share* tool only (see V4) |
| H6 | Never rest maker in the wings — pure cost avoidance | Our resting deep bids are the product informed takers buy | Measured: **0–10c band, 10,573 contracts, win rate 0.000, −$404.30**; 20–30c band **−$398.88 (−19.1c/ct)**. 70–82% maker | **TRADE-shaped (subtraction)** — $1,197.65 / 2 months of avoidable loss |
| H7 | Fee/rebate stacking, VIP maker designation, APY-on-escrow | Free money from schedule mechanics | Graveyard: perps maker +0.3bps dies on 417×/day turnover; program stacking 0/3,599; interest on collateral <$1/day; PolyUS money-banned | **DEAD (prior)** |
| H8 | Quote wider on the *cheap* side only, tighter at mid, sized by fee curvature | Charge takers proportionally to how much the venue already charges them | Same n problem as H1; strictly dominated by simply not quoting the wings (H6) | **DEAD (dominated)** |

**Lane verdict:** the maker-fee asymmetry alone buys nothing. What it does is make the *mid-band* the
only place where a zero-edge quote is not a losing quote — which is the same conclusion the exhaust
reaches from the other direction. Lane's real output is H2+H6.

---

## 2. LANE: VENUE-MECHANICS — visible-to-the-diligent before visible-to-the-lazy

Corpus pulled inline today: **40,000 rows** from keyless `GET /trade-api/v2/incentive_programs`
(paged, deduped by `id`), = **3,935 live programs / 275 live series / 82 future programs**.
Scratchpad: `.../scratchpad/ip_all.json`, `thin_books.json`, `thin_tickers.json`.

| # | Idea | Mechanism / who is the fish | Cheapest decisive kill | Verdict |
|---|---|---|---|---|
| **V1** | **THIN-TARGET LIP POCKET** | `target_size_fp` is **1000 for 3,895 of 3,935** live programs — but **38 are 300 and 1 is 500**. Ceiling per posted contract = `period_reward/target_size_fp`, so a 300-target program pays **3.3× per contract** at the same pot. The fish is Kalshi's own parameterization in markets nobody quotes | **RUN INLINE TODAY** (see §2a). Live test: seat **$50** in `KXEOWEEK-26AUG22-1`, read `/v1/incentives/users/{uid}/estimates` at +24h. **$50 at risk, ~1 min of work, 24h wall clock** | **TRADE-shaped** |
| V2 | Programs feed as an early-warning of next week's LIP families | Know on Saturday which families pay Monday, before the market list shows them | **KILLED INLINE: 82/82 future programs start within 28.2h, and 100% of them are `KXSILVER15M` (24), `KXWTI15M` (24), `KXGOLD15M` (24), `KXTEMPMIAH` (10)** — four intraday families, all on the UNSAFE list (5,000–61,000 trades/mkt/hr). No weekly/multi-day program is ever pre-announced | **DEAD with numbers** |
| V3 | `initialized`-status markets fetchable before the open list | First-30s mispricing | Re-confirmed inline: 10/10 future-program tickers return `status: initialized` and are directly fetchable. But V2 shows the only pre-visible inventory is the 15-min commodity families. The visibility is real; the inventory is toxic | **DEAD as a lane** (mechanism confirmed, no tradeable surface) |
| V4 | **ESTIMATES-FEED SHARE INVERSION** | `GET /v1/incentives/users/{uid}/estimates` returns `program_id` + `reward_centicents` for our account, live (`lip_credit_watch.py` already reads it; realization matches the deterministic model to **≤10 bps**). Since `rate = P_s·our/(our+rival_qual)`, our own accrual **inverts** to `rival_qual = our_size·(P_s/rate − 1)` — a free live estimator of *qualifying* (post-discount-factor) rival depth, which raw book polling cannot give | Read the feed twice, 1h apart, on the 3 currently-seated programs; check inverted `rival_qual` against a simultaneous orderbook pull. **$0, 15 min** | **TRADE-shaped (instrumentation, not alpha)** |
| V5 | **SOLE-MAKER LIP ATTRIBUTION** | Two independent places now show markets with ~zero rival depth and zero trades: **30.2% of TEMP hourly windows print zero trades**, and `KXEOWEEK-26AUG22-1/-2` have **1 contract** of rival depth at the touch across 494h windows. Whether LIP pays a sole maker in a no-trade market is **not derivable from any public endpoint**. If it pays, an entire class of dead markets becomes zero-fill-hazard subsidy | Same $50/24h/1-GET test as V1 — one test answers both | **CONDITIONAL(gate: estimates feed shows non-zero `reward_centicents` for the program after one full window)** |
| V6 | `discount_factor_bps` variation | Some family pays a shallower decay from the touch, making behind-the-touch resting viable | **KILLED INLINE: `discount_factor_bps == 5000` for 100% of 3,935 live programs.** No variation exists | **DEAD with numbers** |
| V7 | Window-length arbitrage (1h → 502h windows) | Longer windows = more subsidy per unit of fill hazard if hazard is per-event not per-hour | Window-hours histogram: 336h (1,048 programs), 168h (342), 73h (183), 81h (165)… down to 1h. But hazard scales with hours-exposed, so the ratio is roughly invariant — **except** where rival depth is ~0, which is V1/V5 | **folded into V1** |
| V8 | The universal screen nobody had | `net/ct/window = (period_reward/target_size)·share − P(fill)·E[loss\|fill]`, with `E[loss\|fill] ≈ $0.20` measured twice independently (ballot **−$0.2013/ct**, TEMP **−$0.2278/ct**). Only **118 of 3,935 live program-rows** have a per-contract ceiling above $0.1941 — and the ceiling is multiplied by share, which for us realized at **~10%** on ballot | Apply to the full feed; it is a spreadsheet. **$0, 10 min** (already coded) | **TRADE-shaped (screen)** — this is why ballot lost: realized $0.0286/ct vs 72% fill × $0.20 |

### 2a. V1 receipts — measured live books, 15 Aug 2026 ~22:30Z

Scored with the house ballot scorer (DF=0.5, $50 seat, cheaper-side touch, band 5–85c, window-normalized).
`$/d/100` is **MODEL**; fill-safety `tr/hr` is **MEASURED** from the public trade tape (24h).

| ticker | $/day/$100 | touch | rival qual | share | tr/hr | window | remaining |
|---|---|---|---|---|---|---|---|
| KXGENERICBALLOTVOTEHUB-26AUG21-T6.8 | **62.34** | 40c yes | 455 | 0.22 | 0.58 | 166h | 134h |
| KXAPRPOTUS-26AUG21-39.8 | **35.33** | 8c yes | 7 | 0.98 | 0.88 | 166h | 134h |
| KXEOWEEK-26AUG22-2 | **31.77** | 15c yes | **1** | 1.00 | **0.00** | 502h | 494h |
| KXEOWEEK-26AUG22-1 | **31.66** | 33c yes | **1** | 0.99 | **0.00** | 502h | 494h |
| KXAPRPOTUS-26AUG21-39.5 | **29.79** | 17c yes | 63 | 0.82 | **0.00** | 166h | 134h |
| KXEOWEEK-26AUG22-0 | **22.64** | 34c no | 60 | 0.71 | **0.00** | 502h | 494h |
| — total at $50/seat | **$106.76/day model on $300** | | | | | | |

Reference bars: house 6.50 $/day/$100; ballot **modelled** median 3.17 / max 17.0; ballot
**realized** 2.04 ($35.75/week on ≤$250). The whole family list ranked by ceiling:
`KXTEMPMIAH $1.92/ct/day` (dead on adverse selection), `KXMAMDANIEO`/`KXGENERICBALLOTVOTEHUB` **$0.4821**,
`KXAAAGASD $0.1502`, `KXRAIN $0.0649`, **`KXSTATEBALLOTMEASURE $0.0622`**, `KXAPRPOTUS $0.0603`.

**Honest discounts before anyone sizes this:** (i) share compresses once seated — ballot modelled
0.12 and realized ~0.10, YTVIEWSW was projected to fall from 0.358 to 0.15–0.25; apply the same
5× haircut and $107/day becomes ~$20/day. (ii) `KXAPRPOTUS` and `KXTRUMPACT` are political-news
repricers, a different adverse-selection character from ballot's 15-month-dated inertia.
(iii) share = 0.99–1.00 on the EOWEEK pair is exactly the V5 attribution question — it may pay $0.
(iv) n=1 snapshot. (v) 30 of the 39 thin-target markets are **out-of-band or fill-unsafe**
(`KXTRUTHSOCIAL` runs 8–20 trades/hr; nine `KXTRUMPACT` strikes sit at 99c).

---

## 3. LANE: BENTER — computable-trajectory doors

| # | Idea | Mechanism / who is the fish | Cheapest decisive kill | Verdict |
|---|---|---|---|---|
| **B1** | **MIRROR-THE-CERTAINTY-TAKER (TEMP hourlies, 0.94–0.995)** | The computable trajectory is *temperature*, and we do not even need the NWS feed — the tape hands it to us. Someone rests a 1c lottery bid; an informed taker pays 94–99c to take the other side once the hour's high is effectively determined. The fish is the **1c-lottery rester** (the census measured them at **1 win in 200 fills** = 0.50% against a 1.00% breakeven, with **49.3% of fills in the final third**). We stop being the rester and become the mirror of the taker | **ALREADY RUN, out-of-sample** (§3a) on the 374 settled markets in `temp_census_cache/` — a corpus built for the *maker* kill, so this is not the data that generated the idea. Remaining gate is slippage only | **CONDITIONAL(slippage gate: median executable price ≤ trigger + 0.5c on 30 live triggers)** |
| B2 | Threshold structure inside B1 | Below 0.94 the taker is *wrong*: **0.90–0.94 returns −11.13c/ct across 5,011 contracts (t=−2.6, win 0.81 vs 0.92 breakeven)**. Above 0.94 they are right. A sharp price threshold, not a smooth drift | Same corpus; already computed | supporting receipt — it rules out "series-wide drift" (the artifact that killed the follow-the-sweep study) |
| B3 | LIP on scheduled-print families (CPI / PPI / FEDFUNDS) | Knowable calendar + lazy crowd | `KXCPICOREHEAD` is live at **$0.0541/ct/day** — *below* ballot's $0.0622 — and the family character is a data-print repricer (`KXUSPPIYOY` measured **0.41–7.99 trades/hr**, unsafe near print). Macro P_s measured 1.7–1.8, under the 3.25 analytic floor | **DEAD with numbers** |
| B4 | FEDFUNDS / FOMC path as a taker door | Public calendar, computable base rates | The crowd is not lazy here — CME FedWatch is public and free, and the calibration map says Kalshi is calibrated everywhere except the post-streak open | **DEAD (prior calibration map)** |
| B5 | **KXAAAGASD daily gas** | **$0.1502/ct/day — 2.4× ballot, the top 1000-target family**, 17 live markets, 16h windows. AAA's published daily national average is a slow-moving trailing mean = a genuinely computable trajectory | Run the §2a scorer over the 17 live `KXAAAGASD` markets + 24h tape. **$0, ~20 min, 34 keyless GETs.** Kill if <3 markets clear 6.50 at ≤1.0 trades/hr — the family measured **7.9–32.8 trades/hr** in the Aug-14 census, so expect it to die on fill-safety | **CONDITIONAL(gate: ≥3 markets clear 6.50 at ≤1.0 tr/hr)** — expected to fail, but it is 20 free minutes on the highest ceiling in the 1000-target universe |
| B6 | Zero-print-window classifier (TEMP) | 30.2% of hourly windows print zero trades → zero fill hazard for a maker | Preregistered in the hourly census: 300 windows, open-time-only features, gate **precision ≥0.80 at recall ≥0.30** out-of-sample. **$0, ~60 min** | **CONDITIONAL(prediction gate, unchanged)** — and now *also* blocked by V5: even a perfect classifier is worthless if a sole maker accrues $0 |
| B7 | Cross-strike monotonicity inside a TEMP hour ladder | ~10 strikes per hour must be monotone in implied probability; violations are structural free money | Scan the cached 374 market-hours for monotonicity breaks in contemporaneous prints. **$0, 20 min.** Prior: BTC 28-bin ladder censused DEAD (SUM_ASK 103.90) | **CONDITIONAL(gate: ≥1 violation exceeding 2× round-trip taker fee)** — low prior |
| B8 | Weather-data-driven taker (pull NWS obs, price the hour directly) | Beat the crowd with the actual observation feed | Strictly dominated by B1: B1 extracts the same information from the tape for free, with no data pipeline, no forecast model, and no latency race | **DEAD (dominated)** |

### 3a. B1 receipts — 374 settled `KXTEMPCHIH` market-hours, 5,359 public prints

Rule: on a public print where the taker acquires an outcome at price p, buy the **same** outcome at
the same p as a taker, pay the full taker fee, hold to settlement.

| condition | prints | contracts | net $ | c/ct | ROC | mkts profitable | t |
|---|---|---|---|---|---|---|---|
| **p ∈ [0.94, 0.995)** | 1,551 | 100,787 | **+$1,231.47** | **+1.22** | +1.24% | **237/243** | **+5.1** |
| … last third of window | 814 | 29,417 | +$388.54 | +1.32 | +1.34% | 130/134 | +2.0 |
| … within T-15min | 682 | 21,298 | +$293.96 | +1.38 | +1.40% | 115/118 | +3.1 |
| p ∈ [0.90, 0.94) — control | 217 | 5,011 | **−$557.89** | −11.13 | −12.15% | 63/70 | −2.6 |
| p ∈ [0.40, 0.55) — control | 513 | 7,377 | −$172.72 | −2.34 | — | 20/48 | — |
| p ≤ 0.10 (i.e. *being* the rester) | 563 | 142,235 | **−$767.68** | −0.54 | — | 6/128 | — |

Mean hold **33 min** (9 min in the T-15 cut). Capacity **$266 of notional per market-hour**.

**Slippage sensitivity — this is the entire question:**

| extra paid vs trigger price | net | c/ct | t |
|---|---|---|---|
| +0.0c | +$1,231.47 | +1.22 | +5.1 |
| +0.5c | +$727.54 | +0.72 | +3.2 |
| +1.0c | +$223.60 | +0.22 | +1.2 |
| +2.0c | +$43.68 | +0.04 | −0.9 |
| +3.0c | −$67.39 | −0.07 | −2.5 |

The informed taker consumes the very liquidity we would need. **If we routinely pay 1c more than the
print we are mirroring, the strategy is a coin flip; at 2c it is dead.** Kill test: log 30 live
triggers and the best executable price 2s later. **$0 (read-only book polling), ~90 min of wall clock.**
Do not fund a single contract before that number exists.

---

## 4. LANE: BEZOS-TAPE — mine our own exhaust

Source: `data/research/fills_all_20260815.json` — **1,540 account fills, 329 distinct markets,
2026-06-17 → 2026-08-15, 59% maker** — joined inline to **actual settlement results** pulled
market-by-market (`GET /markets/{ticker}` → `result`; 289 of 329 settled). Buys only.

### 4a. The receipt table (contract-weighted)

| entry band | fills | contracts | avg entry | win rate | edge/ct | net $ | % maker |
|---|---|---|---|---|---|---|---|
| 0–10c | 104 | 10,573 | 0.037 | **0.000** | −3.82c | **−404.30** | 70 |
| 10–20c | 143 | 2,893 | 0.144 | 0.095 | −5.15c | −148.98 | 68 |
| 20–30c | 77 | 2,088 | 0.229 | 0.041 | **−19.10c** | **−398.88** | 82 |
| 30–40c | 48 | 786 | 0.359 | 0.232 | −13.09c | −102.88 | 72 |
| 40–45c | 45 | 496 | 0.422 | 0.593 | +16.45c | +81.60 | 62 |
| **45–55c** | 46 | 963 | 0.497 | 0.689 | **+18.97c** | **+182.71** | 86 |
| 55–65c | 32 | 429 | 0.609 | 0.539 | −7.67c | −32.90 | 64 |
| 65–80c | 72 | 1,078 | 0.724 | 0.757 | +2.61c | +28.08 | 51 |
| 80–101c | 119 | 2,638 | 0.896 | 0.846 | −5.22c | −137.80 | 71 |
| **TOTAL** | | | | | | **−$933.35** | |

| # | Idea | Mechanism / who is the fish | Cheapest decisive kill | Verdict |
|---|---|---|---|---|
| Z1 | "45–55c is the one band where we're not the fish" → build a strategy that lives only there | The anomaly sweep's framing | **KILLED INLINE.** Contract-weighted the band is +18.97c/ct, but **fill-level it is +0.007 with SE 0.052 on n=91** — indistinguishable from zero. Only **16 of 38 markets (42%) profitable**, median market P&L **−$0.52**, and **$176.26 of the $264.31 (67%) is one series, KXDXYDUD, on 13 fills**. The band's dollars are one concentrated bet, not a distribution | **DEAD as an alpha claim** |
| **Z2** | Same band, restated as a **gate** rather than a strategy | Outside 40–55c: **−0.084/fill on n=595, SE 0.020, t ≈ −4.2** — decisive. Inside: flat. The fish outside the band is us; inside it, nobody is | Already measured. Implementation kill: re-run this table monthly and require the outside-band number to stay below −0.03/fill | **TRADE-shaped (subtraction): ~$1,198 / 2 months, i.e. ~$600/month of avoidable loss** |
| Z3 | The deep-cheap resting bid is our single largest leak | **10,573 contracts bought at avg 3.7c with a 0.000 win rate, 70% of them as a maker.** A fairly-priced 3.7c book should win ~3.7% of the time; zero in 10,573 is not variance, it is selection: our resting bids are only lifted once the outcome is known | Nothing further needed. It corroborates the hourly census's independent finding (1 win in 200 fills at 1c, 49.3% of fills in the final third) on 50× the sample | **DEAD lane, confirmed twice — never rest below 15c again** |
| Z4 | We lose as a **maker**, not as a taker | Maker share is **70–86% in every losing band** and 51–64% in the two profitable ones. Our resting orders are the product | Cross-check against fill forensics: **0 fills in 104.3 seat-hours at the touch vs 4 fills in 48.8 seat-hours behind it** — being behind the touch is the marker of a contested (i.e. targeted) book | **TRADE-shaped (composes with the compiled tb≥1 K=4 eject)** |
| Z5 | **SELF-FADE** (proposed by Gemini, tested inline) | If our wing entries are systematically wrong, take the other side of ourselves | Flipping every wing fill into a **taker** buy of the opposite outcome at 1−p, full taker fees: **+$1,031.40, +5.03c/ct, per-fill mean +7.48c, t=+5.41, 136/194 markets profitable**. Deep subset (<20c): **+$486.32, t=+3.93, 83/89 markets profitable, 95% fill-win** | **CONDITIONAL → generalized.** As stated it is self-referential (it measures *our* badness, not a market inefficiency) and unexecutable (the flip price must exist after the print). Its executable generalization **is B1**, which is out-of-sample and gives the same sign |
| Z6 | KXDXYDUD as a dedicated lane | The one genuinely profitable series: **13 fills, +$176.26** | Pull the full DXY-family tape + our fills; require ≥40 fills and a positive fill-level mean before any capital. **$0, 30 min** | **CONDITIONAL(n gate: ≥40 fills)** — n=13, do not act |
| Z7 | Stop-loss / exit engineering on filled seats | Cut the losers early | Already run: **`seats.py` backtest — every stop-loss is worse than holding.** And the forensics show the gap is instantaneous (6–25 ticks in one 60s bar), so no exit exists between entry and the loss | **DEAD (prior, re-confirmed by mechanism)** |
| Z8 | Time-of-day / storm-window conditioning on our own fills | Fills cluster in storms | Already compiled: **6 of 7 fills inside a sweep storm**; family breaker N=4/W=1h catches 2/4 for $4.68 (16.5% of LIP); post-sweep re-entry ban catches 3/4 for **$0.00** | **already COMPILED — no new idea, listed for completeness** |

---

## 5. Gemini cross-check (verbatim attacks, folded in)

Invocation: `~/.nvm/versions/node/v20.9.0/bin/gemini -p "$(cat gem_prompt.txt)"`.
Prompt = the six candidate ideas + the full collision-fuel numeric summary.
Raw output: `.../scratchpad/gem_out.txt`; prompt: `.../scratchpad/gem_prompt.txt`.

| our idea | Gemini's attack | Gemini verdict | our response after testing |
|---|---|---|---|
| V1 thin-target pocket | "The KXEOWEEK markets with 1 rival contract are a **trap; that one contract is likely a canary** testing the same hypothesis. Once we place size, the rival (or Kalshi) will know the loophole is being actively exploited." Killing number: LIP accrual in zero-trade windows < $0.01 | CONDITIONAL(1-contract live test) | **Accepted and adopted.** The canary framing is the sharpest thing in the review. Test size drops from $50 to **1 contract** where possible; the $50 version is only for the ≥6.5 in-band seats with genuine rival depth |
| Z2 mid-band gate | "The mechanism is **loss-avoidance, not alpha generation**… you have a null result, not an edge… you'd concentrate all risk into a band where your P/L is statistically indistinguishable from zero" | TRADE (as risk gate, not strategy) | **Correct, and it is what our own fill-level test independently found.** Restated as Z2 (subtraction) rather than Z1 (strategy) |
| H1 mid-band spread capture | "The fish is a **fee-insensitive taker. This species does not exist for size.** The only actor shown to trade with size is the sweeper, who is demonstrably informed… picking up pennies in front of a steamroller" | **DEAD** | **Partially rebutted with data Gemini did not have:** TEMP prints at 0.40–0.55 lose **−2.34c/ct over 513 prints**, so a fee-insensitive *losing* mid-band taker demonstrably does exist. But Gemini is right that they carry no size (7,377 contracts vs 142,235 at the wings, **19×** less). Downgraded H1 to CONDITIONAL on n, and the capacity ceiling is now the binding objection |
| V4 estimates inversion | "An information advantage, not a trading strategy… it will lead to chasing markets with **low `rival_qual`, which are likely low for a reason**". Killing number: API update latency > 30s | TRADE (monitoring only) | **Accepted.** Re-labelled instrumentation. The latency check is added to the V4 kill test. The "low for a reason" warning is exactly the V5 attribution risk |
| Idea-5 inverted sweep bait (rest 6–25 ticks below the pre-sweep touch) | "An actor that sophisticated is **not sweeping market orders twice in a row**; they will use passive fills or VWAP on the second pass. You are posting a free option… capital sits idle for hours." Killing number: fill probability < 1% per 6h | CONDITIONAL | **Accepted, and demoted.** It also collides with our own compiled post-sweep re-entry ban — the bait is literally the behaviour the ban exists to prevent. Dropped from the ranked list |
| V5 sole-maker attribution | "Identical to #1… the **single point of failure for the entire dead-market seating concept**" | CONDITIONAL(same test) | **Accepted** — V1 and V5 are merged into one $50/24h test |

**Gemini's three missed ideas:**

1. **FROZEN-BOOK TAKER** — snipe stale quotes the instant a frozen book thaws.
   → **DEAD, and we have the census.** The terminal-taker spec measured **0/97 markets with a
   takeable ask ≤ (last trade − 3c)** and **0/97 locked-or-crossed books** at T-7.5h, median spread
   1c. There are no stale quotes to snipe. Gemini did not have this receipt in the prompt summary;
   it is the same falsified thesis, re-derived.
2. **ADVERSE-SELECTION ARBITRAGE ("your own exhaust is a map of your incompetence")** —
   → **The best contribution of the review.** Tested inline as Z5 (**+$1,031.40, t=+5.41**), then
   generalized out-of-sample to **B1** (**+$1,231.47, t=+5.1, 237/243 markets profitable**), which is
   now the #2 ranked survivor of the whole burst. Gemini's framing ("do the opposite of your maker
   model in the wings, you pay taker fees against a measured 8.4c edge") is exactly right on sign and
   roughly right on magnitude — the executable version nets 1.22c/ct rather than 8.4c because the
   flip must be crossed at market, not at our own resting price.
3. **SWEEP-BASKET CORRELATION** — map the sweeper's basket; when market A of basket {A,B,C} is swept,
   front-run legs B and C.
   → **CONDITIONAL, and genuinely new.** Direct support exists: **GA-A2 and AR-A578 initiated at the
   identical second**, and 93 sweeps in 68 hours cluster into storms (08-14 00h: 12; 08-15 04h: 11;
   08-15 17h: 10). Against it: the sweeper is *simultaneous*, not sequential — same-second baskets
   leave no milliseconds to front-run — and the follow-the-sweep event study already netted
   **+0.06c** after fees with the NO side at **−1.87c** (the asymmetry that proved it was series-wide
   drift, not signal). Cheapest kill: from `sweep_events_20260815.json` (602 clusters, already on
   disk), measure the **lag distribution between legs of same-actor baskets**. If p90 lag < 2s the
   idea is arithmetically dead. **$0, 25 min.** Prior: dead.

---

## 6. Ranked survivors — (edge $ × probability) / test cost

Probability = our honest odds the idea survives its own kill test. Edge is per month unless stated.

| rank | idea | edge if true | P(survives) | test cost | score |
|---|---|---|---|---|---|
| **1** | **Z2 — mid-band-only gate (never rest or buy outside 40–55c)** | **+$600/mo** avoided loss | **0.90** | **$0** (measured; monthly re-run) | ∞ — it is a subtraction that is already paid for |
| **2** | **V1+V5 — thin-target LIP pocket / sole-maker attribution** | $20–30/day after a 5× share haircut ≈ **+$600–900/mo** | **0.40** | **$50 at risk + 24h + 1 GET** | ~5–7 $/$ |
| **3** | **B1 — mirror-the-certainty-taker, TEMP 0.94–0.995** | +1.22c/ct on $266/market-hour of capacity ≈ **+$3.3/market-hour** | **0.35** (slippage) | **$0** + ~90 min of live book logging | high |
| **4** | **V4 — estimates-feed share inversion** | enabler: turns modelled share into realized share for every seat we run | **0.75** | **$0, 15 min** | high (multiplier, not standalone) |
| **5** | **B5 — KXAAAGASD census** ($0.1502/ct/day, 2.4× ballot) | +$10–20/day if any market clears | **0.15** | **$0, 20 min, 34 GETs** | cheap lottery ticket |
| 6 | V8 — the universal `ceiling × share − P(fill)·$0.20` screen over all 3,935 programs | prevents the next ballot | 0.85 | $0, 10 min | run it before the next family is seated |
| 7 | Gemini-3 — sweep-basket lag distribution | kills or opens a class | 0.10 | $0, 25 min | run only when idle |
| 8 | Z6 — KXDXYDUD n-gate | unknown | 0.25 | $0, 30 min | n=13, do not act |

**Not ranked / dropped:** H3, H4, H7, H8, V2, V3, V6, B3, B4, B8, Z1, Z3, Z5-as-stated, Z7,
Gemini-1, inverted-sweep-bait — all DEAD with numbers above.

---

## 7. Reproduction

Working files (session scratchpad, absolute):
`/private/tmp/claude-501/-Users-ryanwhitehead-Documents-senate-domains-kalshi/162f05b7-b9bf-49dd-b319-057450acadb5/scratchpad/`
- `ip_all.json` — 40,000 incentive-program rows (deduped to 40,000 unique `id`), pulled 2026-08-15 ~22:30Z
- `thin_tickers.json`, `thin_books.json` — the 39 `target_size_fp < 1000` markets with live books (`orderbook_fp`) + 24h tape
- `settle.json` — settlement `result` for all 329 tickers in our fill history
- `gem_prompt.txt`, `gem_out.txt` — the Gemini cross-check, verbatim

On-disk inputs used read-only:
- `/Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research/fills_all_20260815.json`
- `/Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research/temp_census_cache/` (374 settled market tapes + `market_meta.json`)
- `fill-forensics-20260815.md`, `terminal-taker-spec-20260815.md`, `temp-hourly-census-20260815.md`
- `/Users/ryanwhitehead/Documents/senate/archive/enchiridion_legacy/work/lip-family-census-2026-08-14.md`, `orthogonal-ideas-2026-08-14.md`

**Gotcha for the next run:** the keyless orderbook payload key is **`orderbook_fp`** (prices as
dollar strings), not `orderbook`. Parsing `orderbook` returns `null` for every market and silently
reports an empty book — it cost this lane one full pass.

No orders placed, no cancels, no credentials used beyond public GETs. Nothing written outside
`data/research/` and the session scratchpad.
