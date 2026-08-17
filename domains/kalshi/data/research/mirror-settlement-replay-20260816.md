# B1 MIRROR-THE-CERTAINTY-TAKER — settlement-linked replay (decisive gate)

**Run:** 2026-08-16, read-only keyless GETs via VPS 129.146.115.241. **No orders.**
Supersedes the 03:50Z draft of this file, which was computed on an **incomplete settlement set**
(34 of 56 tickers; the 22 missing were *all* in the unfillable arm, so the arm that the whole
adverse-selection question rests on was under-counted by half — n=68 instead of n=139).

**Artifacts**
- Triggers: `/Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research/mirror_slippage_20260816.jsonl` (322 rows, 56 unique tickers)
- Settlements: `/Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research/settlement_status_full_20260816.json` — **56/56 tickers, all `finalized`**, 18+ yes / 16+ no split (not a degenerate all-YES night)

## Method
Mirror = buy the taker's own side at the **recorded executable ask** `exec_ask_t0` (not the trigger price).
Payoff 100 if `market.result == trigger side` else 0. Fee = Kalshi taker formula
`ceil(7·n·p·(1−p))` cents **ceiled to the whole cent per order** — this is materially harsher than the
continuous 0.33c/ct the backtest used, and it is what killed the equal-weighted view (42 of 322 triggers
are sub-1-contract clips where a 1c minimum fee is 2c+/ct). All figures below are therefore
**contract-weighted net**, reported under three sizing rules to prove the result is not a sizing artifact.
Unfillable arm is a counterfactual priced at the trigger price (the price you'd have had to pay if a book existed).

## 1. Was the certainty-taker right? (the adverse-selection test)

| arm | n triggers | settle-with-taker rate | losses |
|---|---|---|---|
| **FILLABLE** (executable ask existed) | 183 | **98.91%** | 2 |
| **UNFILLABLE** (book cleared, n=139) | 139 | **100.00%** | 0 |

Both losses are the *same* ticker (`KXTEMPLAXH-26AUG1523-T68.99`, side `no`) and are the crossed-book
outliers — exec ask 9c against a 97c trigger. They cost 9c each, not 97c. Excluding those 3 known
crossed-book rows, the clean fillable arm is **180/180**.

**Selection against us is NOT confirmed.** The gap is 1.1pp on 2 trades inside one cluster, and it runs
the *cheap* way (the mispriced-fill rows). The unfillable prints were not better-informed; they were
merely smaller-book. The killing hypothesis from the slippage report is rejected.

## 2. Realized net P&L at the recorded executable ask (after ceil fees)

| subpopulation | n | net c/ct — size=min(cnt,depth) | size=depth | size=min(depth,100) |
|---|---|---|---|---|
| ALL FILLABLE (incl. 3 outliers) | 183 | **+1.62** | +1.37 | +1.71 |
| FILLABLE clean | 180 | +1.63 | +1.39 | +1.82 |
| ZERO-SLIP | 88 | +1.59 | +1.46 | +1.92 |
| **PREREG: fillable & ask==trigger & depth≥25** | **62** | **+1.59** | **+1.45** | **+1.92** |
| UNFILLABLE counterfactual @ trigger px | 139 | +1.14 | — | — |

The fillable set out-earns the unfillable counterfactual (+1.62 vs +1.14 c/ct). The +1.22c/ct backtest
edge survives settlement at real executable prices.

## 3. Preregistered subset — hour-clustered t

62 trades, 2,483 ct, mean exec price 97.85c, **9 city-hour clusters** (one NWS reading settles every
ticker in a cluster, so clusters are the honest unit of independence).

| cluster | n | ct | net c/ct | losses |
|---|---|---|---|---|
| AUSH-22 | 7 | 115 | +1.78 | 0 |
| AUSH-23 | 4 | 39 | +1.69 | 0 |
| DCH-23 | 2 | 13 | +1.64 | 0 |
| LAXH-22 | 1 | 22 | +4.64 | 0 |
| LAXH-23 | 11 | 69 | +3.15 | 0 |
| MIAH-22 | 17 | 1,794 | +1.49 | 0 |
| MIAH-23 | 10 | 307 | +1.56 | 0 |
| NYCH-22 | 8 | 123 | +1.47 | 0 |
| NYCH-23 | 2 | 2 | +1.00 | 0 |

Cluster mean **+2.05 c/ct**, sd 1.13, k=9 → **t = +5.42** (size=depth: +1.99, t=+5.46; capped-100: +2.13, t=+6.18).
Every cluster is positive; the t is driven by level, not by one outlier.

## VERDICT: **FUND-CANDIDATE**

Preregistered rule was `net ≥ +1.0 c/ct with |t| ≥ 2`. Realized **+1.45 to +1.92 c/ct with t = +5.4 to +6.2**
under every sizing rule, with the adverse-selection kill hypothesis explicitly rejected. Gate passed.

**The honest limits, unchanged by this pass:**
1. **Breakeven win rate is 98.11%** (mean exec 97.85c + ~0.25c/ct fee at real clip sizes). Observed
   0 losses in 9 clusters bounds the cluster win rate only to **≥71.7%** (95% Clopper-Pearson); at the
   trade level 62/62 bounds it to ≥95.3% — *below* breakeven. **This night cannot by itself prove the
   loss rate clears the bar.** The statistical power still lives in the 374-market-hour backtest (t=5.1);
   this replay is a consistency check that passed, not independent proof.
2. **One night, one weather regime.** Clear hot mid-August evening; hourly temp outcomes were close to
   physically determined. A marginal-temperature night is the real test and has not been run.
3. **Capacity is the binding constraint, not edge.** Preregistered-subset mirrorable volume is
   2,483 ct / 90 min ≈ 1,655 ct/hr at ~+1.6c/ct → **~$26/hr gross ceiling** at perfect capture across all
   6 cities. Sub-1-contract clips are fee-negative and must be filtered (min order ≥ ~10 ct).

**Conditions before capital:** (a) Ryan approval; (b) one settlement replay on a weather-uncertain night;
(c) hard min-clip filter ≥10 ct to escape the ceil-fee trap; (d) size capped to the ~1,600 ct/hr surface.
