# Zero-Print Window Gate — KXTEMP hourly (read-only, preregistered)
Date: 2026-08-16 | Lane: predict zero-trade hourly windows at window-open
Gate (preregistered in temp-hourly-census-20260815.md): **precision >= 0.80 at recall >= 0.30, out-of-sample.** Below gate => CLOSED PERMANENTLY.

## VERDICT: CLOSED PERMANENTLY
TEST precision at the preregistered operating point = **0.733** (required 0.80).
Even an oracle threshold chosen *on the test set* tops out at **0.761** (basic) / **0.767** (enriched) at recall 0.30. Precision only reaches 0.80 at recall ~0.18-0.20 — below the required recall floor. No threshold exists that satisfies both constraints.

## Grave line (graveyard table format)
`TEMP zero-print window prediction (dead-window maker seat) | precision 0.733 @ recall 0.435 out-of-sample (oracle ceiling 0.761 @ recall 0.30) vs 0.80 gate | 2026-08-16`

## Data
- Universe: all **9,132** KXTEMPCHIH one-hour market-windows, 2026-07-08 21:00Z -> 2026-08-15 18:00Z, from cached `temp_census_cache/markets_KXTEMPCHIH.json` (all `finalized`). 9,098 usable after requiring a prior window.
- **No new VPS pulls were needed.** Label source = `volume_fp == 0`, validated against all 374 cached trade tapes: **374/374 agreement**, zero mismatches (`volume_fp==0` <=> empty tape). This is why the sample is 9,132 windows instead of 374.
- Base rate: **0.266** overall (census's 30.2% was the 374-market subsample). Train 0.197, test 0.354-0.370 — a real regime shift toward *more* dead windows late in the sample, which makes precision **easier** in test, and it still failed.

## Preregistered split (fixed before fitting)
Train = first 60% of windows by `open_time`; test = last 40%. Cut = 2026-07-31T15:00Z. Train n=5,458, test n=3,640. Threshold selected **on train only** as max-precision subject to train recall >= 0.30; applied unchanged to test.

## Features (all audited for lookahead)
| feature | source | verdict |
|---|---|---|
| prior-window total prints, same city | sum `volume_fp` over the event closing exactly at this window's open | clean — all trades timestamped before open |
| prior-window zero-fraction | frac of prior event's strikes with zero prints | clean |
| strike distance from ladder center | `abs(floor_strike - median(strikes in event))`; ladder created ~1h pre-open | clean, uses no volume |
| hour-of-day (sin/cos), weekend flag | `open_time` | clean |
| (enriched only) same-strike prior-hour zero, dist^2, ladder size | as above | clean |
| REJECTED: `expiration_value` (realized temp) | settlement | **lookahead — excluded** |

## Results
Logistic (preregistered feature set), coefficients: intercept -3.98, log1p(prior_tot) +0.004, prior_zfrac **+3.36**, dist **+0.59**, sin_h +0.18, cos_h -0.13, weekend +0.22. Signal is real but weak — it is almost entirely "yesterday's hour was dead and this strike is far from center," which is exactly the information the market already prices.

Chosen rule: flag window if `sigmoid(x'w) >= 0.4468` (train-calibrated, train precision 0.596 @ recall 0.301).

| set | precision | recall | flagged |
|---|---|---|---|
| TEST @ preregistered threshold | **0.733** | 0.435 | 798 / 3,640 |
| TEST oracle @ recall 0.30 | 0.761 | 0.30 | 531 |
| TEST oracle @ recall 0.20 | 0.766 | 0.20 | 351 |
| TEST oracle @ recall 0.10 | 0.828 | 0.10 | 163 |
| Enriched model, TEST @ train thr | 0.739 | 0.456 | 700 |
| Enriched, oracle @ recall 0.30 | 0.767 | 0.30 | — |

High-precision hand rules exist but are recall-starved and fail the floor by an order of magnitude: `prior_zfrac>=0.95 & dist>=2` gives precision 0.944 at **recall 0.025** (n=36); `prior_zfrac==1.0` gives 0.900 at **recall 0.040** (n=60). The gate's recall floor was set precisely to reject these.

## Honest blocker (stated regardless of outcome)
Even a pass would not have earned capital. **LIP attribution for a no-touch/no-trade window is not derivable from any public endpoint** — the census established that `incentive_programs` publishes the per-window reward pool and target size but never the realized per-participant credit, and with zero prints there is no tape to reverse-engineer it from. A clearing pass would only have earned the **next** test: a ~$50 instrumented probe posting real size in flagged windows to observe actual LIP credit. That probe is now moot.

## Reproduce
`/private/tmp/claude-501/-Users-ryanwhitehead-Documents-senate-domains-kalshi/162f05b7-b9bf-49dd-b319-057450acadb5/scratchpad/gate2.py` (labels + features + tape validation) then `gate3.py` (split, fit, evaluate).
