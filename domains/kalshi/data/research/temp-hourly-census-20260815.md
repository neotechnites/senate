# TEMP Hourly Census — MAKER-side kill test
Date: 2026-08-15 · Series: KXTEMPCHIH · **STRICTLY READ-ONLY, no orders, no auth used**

Prior kill `sweep-2026-08-10` ("TEMP HOURLIES DEAD") was made on TAKER economics.
This document tests the MAKER side: (a) the deep 1c resting-bid lottery, (b) a
$50-capped LIP seat in the 15–85c band.

**Both lanes: DEAD.** Receipts below.

---

## 0. Method and provenance

| Item | Value |
|---|---|
| Population enumerated | **9,195** finalized KXTEMPCHIH markets (`GET /trade-api/v2/markets?series_ticker=KXTEMPCHIH&status=settled`, 10 pages) |
| Preregistered sample | n=500, stratified across **39** calendar days, proportional allocation, `random.Random(20260815)` |
| Actually pulled | **374** markets (venue rate-limited the run; the sample list was **shuffled with the seed before any data was seen**, so the 374 is an unbiased random prefix, not a selected subset) |
| Trade record | `GET /trade-api/v2/markets/trades?ticker=...`, paginated, keyless, ~1 req/s |
| Cache (resumable) | `/Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research/temp_census_cache/` |
| Puller / analyzer | `temp_census_pull.py` · `temp_census_analyze.py` · raw output `census_results.txt` |

Sampling rule was written into the script header **before** the first trade pull and
was not altered. ARM 2's primary n=100 subsample is the preregistered one; the
extended arm is the seed-ordered prefix (order fixed pre-data) and is labelled as
secondary throughout.

### Side semantics — verified, not assumed
Only two `(taker_side, taker_outcome_side, taker_book_side)` combos exist in the tape:
`("yes","yes","bid")` and `("no","no","ask")`. Therefore:
- a resting **YES bid at c** is hit only by a print with `yes_price==c` **and** `taker_side=="no"`;
- a resting **NO bid at c** is hit only by a print with `yes_price==1-c` **and** `taker_side=="yes"`.

All fill numbers below assume **perfect queue priority** (we are always front of
queue). Every fill rate and every favourable-outcome rate is therefore an **upper
bound** on what a real seat would achieve.

### Tape shape
- **30.2%** of hourly market-windows (113/374) print **zero trades all hour**.
- Median prints/market **3**; p90 **40**; max **425**. Total prints 5,359.
- Settlement base rate P(YES) = **0.6257**.

---

## 1. LIP subsidy formula — SOURCED (this corrects an on-disk fake receipt)

The on-disk `data/sources/lip_decay_spec.json` cites
`https://trading-api.kalshi.com/trade-api/v2/lip_programs`. That host is retired and
that path **404s**. The file is a restatement, **not a captured payload** — it should
not have been treated as a receipt.

The live endpoint is **`GET /trade-api/v2/incentive_programs`** (keyless). Captured to
`temp_census_cache/incentive_programs_all.json` (20,000 rows). Actual TEMP rows:

```json
{"incentive_description":"series_lip","incentive_type":"liquidity",
 "market_ticker":"KXTEMPMIAH-26AUG1519-T92.99",
 "period_reward":800000,"target_size_fp":"1000.00","discount_factor_bps":5000,
 "start_date":"2026-08-15T22:00:00Z","end_date":"2026-08-15T23:00:00Z"}
```

| Series | `period_reward` | `target_size_fp` | `discount_factor_bps` | Window |
|---|---|---|---|---|
| KXTEMPCHIH / AUSH / DCH / LAXH / NYCH | **1,200,000** | 1000.00 | 5000 | 1 h |
| KXTEMPMIAH | **800,000** | 1000.00 | 5000 | 1 h |

**Units of `period_reward` = 1e-4 USD.** Derived, not assumed: the feed's distinct
reward values include **2,500,000** and **2,850,000**, which map to **$250.00** and
**$285.00** — exactly the `reward_usd_per_window_per_2sides` figures independently
receipted for the ballot LIP (AL-A4 $250.0, NC-A2 $285.0) in
`fill-forensics-20260815.md`. Two independent sources agree at 1e-4.

→ **KXTEMPCHIH = $120.00 per market-window. KXTEMPMIAH = $80.00.**

**The only subsidy number this analysis relies on:**
```
max LIP per posted contract per window = period_reward / target_size_fp
                                       = $120 / 1000 = $0.1200   (CHIH)
                                       = $80  / 1000 = $0.0800   (MIAH)
```
This is a **ceiling at the touch** (decay exponent 0), so it does **not** depend on how
`discount_factor_bps` is interpreted. It also assumes we capture our full pro-rata
share — generous.

> Not sourced, flagged: the *basis* of the 5000 bps decay ("50% per tick from the
> touch") appears only in the local seed, not in the payload. It is used **nowhere**
> in the ARM 2 kill. It is used only as a supporting argument in ARM 1, which is
> already dead without it.

---

## 2. ARM 1 — the 1c lottery. **DEAD.**

Strategy tested: rest 1c on **both** sides of every market-window, forever, maker fee $0.

| Tick | P(ever filled) | fills | won | P(win \| filled) | breakeven | EV / filled contract |
|---|---|---|---|---|---|---|
| **1c** | 0.5321 [0.4814, 0.5821] | 200 | **1** | **0.0050** [0.0009, 0.0278] | 0.0100 | **−$0.0050** [−0.0091, +0.0178] |
| 2c | 0.3583 [0.3114, 0.4081] | 135 | 1 | 0.0074 [0.0013, 0.0408] | 0.0200 | −$0.0126 [−0.0187, +0.0208] |
| 3c | 0.4037 [0.3552, 0.4542] | 152 | 2 | 0.0132 [0.0036, 0.0467] | 0.0300 | −$0.0168 [−0.0264, +0.0167] |

EV per market-window (1 contract/side attempted): **−$0.00267** (1c), −$0.00455 (2c),
−$0.00684 (3c). The lane gets *worse* as you move up the ladder — 2c and 3c miss
breakeven by a wider margin than 1c does.

**The premise fails on all three legs:**

1. **The lottery has essentially never paid.** 1 win in 200 fills = 0.50% against a
   1.00% breakeven. The "99:1" framing needs P(win) > 1%; the point estimate is half that.

2. **The counterparty is informed, not noise.** Elapsed fraction of the hour at the
   first 1c fill (n=199): median **0.661**, mean 0.564. **49.25%** of 1c fills land in
   the **final third** of the window against **33.3%** under uniform noise. These are
   not idle lottery tickets being sold — they are near-determined outcomes being
   dumped once the temperature is effectively known. This is exactly the adverse
   branch of question (a).

3. **The subsidy cannot rescue it, and is ~$0 anyway.** A 1c bid sits 30–90 ticks
   below the touch in a live market. Under any decaying-reward reading it earns
   approximately nothing; under the local seed's 0.5^ticks basis a 1c bid against a
   50c touch earns $120 × 0.5⁴⁹ ≈ $2e−13. There is no subsidy leg to stand on.

4. **Queue makes the modeled fill rate unreachable.** 82,795 contracts printed at the
   1c tick across 374 markets (median 23 per filled market, p90 1,421, max 8,100).
   The table above already grants us front-of-queue; a real order sits behind that
   inventory, so the true fill rate is far below 0.5321 and is concentrated in
   precisely the sweeps that are informed.

**Honest statistical caveat:** on settlement evidence *alone* the 95% CI upper bound
(+$0.0178/contract at 1c) still crosses zero — 200 fills cannot resolve a 1% breakeven.
Reaching a 95% upper bound below breakeven needs ~300 consecutive losing fills. The
kill therefore rests on the conjunction of legs 2–4, not on leg 1 in isolation.
**VERDICT: DEAD.** No configuration of this lane has a positive edge to compile.

---

## 3. ARM 2 — $50-capped in-band (15–85c) maker seat. **DEAD.**

Reconstruction from the trade tape (no historical book exists): at the first print of
the market, join the touch on the **cheaper side** at `q = min(p, 1-p)`, require
`q ∈ [15c, 85c]`, and **never move**. Fill = any later print that would have traded
through a resting bid at `q` on our side.

| Metric | PRIMARY (preregistered n=100) | SECONDARY (seed-ordered prefix, n=374) |
|---|---|---|
| P(price transits 15–85c band in the hour) | 0.3300 [0.2456, 0.4269] | **0.2941** [0.2502, 0.3422] |
| In-band seats established | 19 | **81** |
| **P(filled \| seated)**, perfect queue | 0.7368 [0.5121, 0.8819] | **0.8519** [0.7587, 0.9132] |
| Mean entry | $0.3332 | $0.2994 |
| **Mean settlement − entry (filled)** | **−$0.2493** [−0.3768, −0.1217] | **−$0.2278** [−0.2823, −0.1734] |
| P(filled side settles ITM) | 0.0714 (1/14) | **0.0580** (4/69) |
| Post-fill mark drift, our side | −$0.2521 | **−$0.2186** |

**Answer to question (b): the fill hazard is high and the flow is adverse, not noise.**
Conditional on a seat existing, you get filled **85%** of the time, and the side you
end up holding settles in your favour **5.8%** of the time after entering at ~30c. The
post-fill mark drift of **−$0.2186** confirms it is directional adverse selection, not
symmetric noise — the market moves against the filled side immediately and stays there.

### The scale-free kill (does not depend on the $50 cap)

```
adverse selection per POSTED contract = P(fill|seated) × E[loss|fill]
                                      = 0.8519 × $0.2278 = $0.1941
max LIP credit per POSTED contract    = $120 / 1000       = $0.1200   (CHIH)
------------------------------------------------------------------------
NET per posted contract per window    =                    −$0.0741
   95% CI (from the CI on E[loss|fill]) = [−$0.1204, −$0.0277]   ← excludes zero
```

For KXTEMPMIAH (the 800,000 family named in the brief) the ceiling is $0.0800 and the
net is **−$0.1141/contract**, CI [−$0.1604, −$0.0677].

**`target_size_fp = 1000` is what kills this, and the $50 cap is why it cannot be
fixed.** LIP pays out against a 1,000-contract target. At a ~30c entry, $50 of
collateral buys **167 contracts — 16.7% of target size**. You structurally cannot reach
the size at which the subsidy is generous, while you eat 100% of the adverse selection
on every contract you do post. The subsidy is $0.12/contract; the adverse selection is
$0.19/contract. The seat loses money **per contract, at any size** — the cap only bounds
how much you lose, never the sign.

At the $50 cap: **−$12.37 per seated window** (CHIH), **−$19.05** (MIAH). With ~0.29 of
windows producing an in-band seat, that is roughly **−$3.6/window** run continuously.

Both the primary (n=19 seats) and secondary (n=81 seats) arms agree in sign; the primary
arm's CI on net crosses zero at n=14 fills, the secondary arm's does not.
**VERDICT: DEAD.**

---

## 4. Verdicts

1. **1c-lottery lane — DEAD.** 1 win in 200 fills = **0.50%** against a **1.00%**
   breakeven; **49.3%** of fills land in the final third of the hour vs 33.3% uniform.
   Informed flow, not noise. Subsidy at 1c ≈ $0.

2. **In-band maker seat in TEMP hourlies — DEAD.** Net **−$0.0741 per posted contract
   per window**, 95% CI **[−$0.1204, −$0.0277]**, excludes zero. LIP ceiling $0.1200 <
   adverse selection $0.1941. −$12.37 per seated window at the $50 cap.

3. **Paper-trade measurement for next week: NONE AUTHORIZED.** Neither lane is alive,
   so no seat is preregistered. Do not deploy capital into TEMP hourly LIP.

### The one thing that survived, and it is not a seat yet
**30.2% of TEMP hourly windows print zero trades all hour.** A maker resting in *those*
windows faces literally zero fill hazard. This census did not test that lane and it is
a different lane from the two killed here. It is only exploitable if dead windows are
identifiable **ex ante**, and the LIP attribution rule for a market with no touch and no
trades is **not derivable from any public endpoint** — so it must not be assumed.

**Preregistered read-only test before this is ever considered:** from
`incentive_programs` + the trade tape, take the next 300 TEMP hourly windows; using only
information available **at window open** (prior-window volume, strike distance from the
then-current temperature, hour-of-day), fit and out-of-sample test a classifier for
"zero prints this hour". Gate: it must reach **precision ≥ 0.80 at recall ≥ 0.30** on
held-out windows. Below that gate the lane is unexploitable and is closed permanently.
No orders, no capital, no paper seat until that gate is passed.

### Tripwire that would reopen ARM 2
`period_reward / target_size_fp` rising above the measured adverse selection of
**$0.1941/contract** — i.e. `period_reward > 1,941,000` at `target_size_fp = 1000`.
Today CHIH is 1,200,000. Re-check the feed rather than re-running the census.
