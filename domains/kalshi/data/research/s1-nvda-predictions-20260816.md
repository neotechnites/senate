# S1 — NVDA 2026-08-26 word-strike predictions (PREREGISTERED)

**Written 2026-08-16. Predictions below are FINAL as of this timestamp.** Read-only; no orders placed.

Event `KXEARNINGSMENTIONNVDA-26AUG26` · 19 word strikes · model = own-transcript base rate, `n_lookback=4`, Beta(prior_p=0.50, a=1.5) shrinkage, no recency decay.

NVDA history used (all call_date < 2026-08-26): q12027@2026-05-20, q42026@2026-02-25, q32026@2025-11-19, q42025@2025-02-26

> **The backtest does NOT support funding this model.** See `s1_backtest.py` / verdict at bottom.
> These predictions are recorded to keep the preregistration honest, not as a trade recommendation.


## Full table

| Word | Model P | k/n | mentions/call | said last call | prep/Q&A | yes bid/ask | mid | model side | entry | fee | edge after fee | in-band 15-85 | vol / OI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Dividend (2+ times) | 0.136 | 0/4 | 0.0 | N | 0/0 of 2 | 40/46 | 43.0 | NO | 60c | 2c | +24.4c | YES | 3395 / 2048 |
| TSMC | 0.318 | 1/4 | 0.75 | N | 0/0 of 2 | 58/61 | 59.5 | NO | 42c | 2c | +24.2c | YES | 1391 / 947 |
| Humanoid | 0.318 | 1/4 | 0.25 | Y | 0/0 of 2 | 50/53 | 51.5 | NO | 50c | 2c | +16.2c | YES | 2270 / 1380 |
| Talent | 0.318 | 1/4 | 0.25 | N | 1/0 of 2 | 48/53 | 50.5 | NO | 52c | 2c | +14.2c | YES | 606 / 391 |
| Domestic | 0.136 | 0/4 | 0.0 | N | 0/0 of 2 | 28/34 | 31.0 | NO | 72c | 2c | +12.4c | YES | 84 / 79 |
| Cosmos | 0.682 | 3/4 | 0.75 | N | 2/0 of 2 | 54/55 | 54.5 | YES | 55c | 2c | +11.2c | YES | 2901 / 1297 |
| Automation | 0.318 | 1/4 | 0.25 | N | 0/0 of 2 | 43/46 | 44.5 | NO | 57c | 2c | +9.2c | YES | 828 / 518 |
| Rent | 0.318 | 1/4 | 0.75 | Y | 0/0 of 2 | 16/21 | 18.5 | YES | 21c | 2c | +8.8c | YES | 518 / 439 |
| Taiwan | 0.136 | 0/4 | 0.0 | N | 0/0 of 2 | 22/25 | 23.5 | NO | 78c | 2c | +6.4c | YES | 1082 / 410 |
| Gaming | 0.864 | 4/4 | 2.25 | Y | 2/0 of 2 | 78/79 | 78.5 | YES | 79c | 2c | +5.4c | YES | 2366 / 1918 |
| Arizona | 0.136 | 0/4 | 0.0 | N | 0/0 of 2 | 21/29 | 25.0 | NO | 79c | 2c | +5.4c | YES | 74 / 74 |
| Omniverse | 0.500 | 2/4 | 1.25 | N | 1/0 of 2 | 57/61 | 59.0 | NO | 43c | 2c | +5.0c | YES | 188 / 115 |
| Hyperscaler | 0.864 | 4/4 | 7.75 | Y | 1/1 of 2 | 91/93 | 92.0 | NO | 9c | 1c | +3.6c | no | 1495 / 813 |
| H20 | 0.136 | 0/4 | 0.0 | N | 0/0 of 2 | 19/25 | 22.0 | NO | 81c | 2c | +3.4c | YES | 3491 / 2603 |
| Tariff | 0.318 | 1/4 | 0.75 | N | 0/1 of 2 | 21/27 | 24.0 | YES | 27c | 2c | +2.8c | YES | 2420 / 2307 |
| Self Driving | 0.682 | 3/4 | 1.5 | Y | 1/0 of 2 | 73/77 | 75.0 | NO | 27c | 2c | +2.8c | YES | 356 / 241 |
| GM / General Motors | 0.136 | 0/4 | 0.0 | N | 0/0 of 2 | 4/10 | 7.0 | YES | 10c | 1c | +2.6c | no | 1798 / 1765 |
| Hermes | 0.318 | 1/4 | 0.25 | Y | 0/0 of 2 | 30/31 | 30.5 | YES | 31c | 2c | -1.2c | YES | 1227 / 720 |
| Trump | 0.136 | 0/4 | 0.0 | N | 0/0 of 2 | 9/15 | 12.0 | YES | 15c | 1c | -2.4c | no | 712 / 649 |

In-band (mid 15-85c): **16/19**. Mean model edge in-band: **+9.41 c/ct**. Model side is NO on 11/16 in-band strikes.

## Top 3 model edges (in-band)

- **Dividend (2+ times)** — model P=0.136 (0/4 prior calls, 0.0 mentions/call), market mid 43.0c, take **NO @ 60c**, edge **+24.4 c/ct** after 2c fee.
- **TSMC** — model P=0.318 (1/4 prior calls, 0.75 mentions/call), market mid 59.5c, take **NO @ 42c**, edge **+24.2 c/ct** after 2c fee.
- **Humanoid** — model P=0.318 (1/4 prior calls, 0.25 mentions/call), market mid 51.5c, take **NO @ 50c**, edge **+16.2 c/ct** after 2c fee.

## Preregistered pass bar (Gemini-set, accepted verbatim)

Realized **>= +2.0 c/ct net of fees** over the next **>=10 company calls / >=50 word-markets**. Below that ⇒ DEAD. This file is the first entry in that ledger.

## Backtest verdict (the receipt)

226 settled KXEARNINGSMENTION word-markets, 14 companies, price = last trade at 23:59:59Z the day BEFORE the call; 214 had a pre-call print. Model sees only transcripts with `call_date < call date`.

| metric | model | market |
|---|---|---|
| Brier, all 214 | 0.2317 | **0.1485** |
| Brier, in-band 155 | 0.2429 | **0.1967** |
| log-loss, all 214 | 0.6963 | **0.4533** |

The market wins on every scoring rule. Under a logistic `y ~ logit(price) + base_rate`, the base-rate coefficient is **-0.402** (wrong sign) and log-loss improves 0.4432 -> 0.4416 **in-sample** — i.e. the own-transcript base rate carries no incremental information the price does not already have. Best in-band taker cell across an 8-way (lookback x decay) LOCO sweep: **+1.16 c/ct, clustered t=+0.87** — and that is the argmax of the sweep, so it is optimistically biased. **Below the +2.0 c/ct bar.**

Worse, the base rate is *anti*-predictive at the top: strikes said in **every** prior call, in-band, priced mean 73.5c, realized only **0.500** (n=12) — taking YES there loses **-25.3 c/ct**.

**VERDICT: the base-rate predictor is DEAD. Do not fund the $150 NVDA run on this model.**

## The one thing that did measure positive (a different idea, not this one)

Unconditional **taker-NO**, in-band 15-85c, day before the call: **+4.90 c/ct, n=155, 13 company clusters, clustered t=+2.35**, yes-rate 0.394 vs mean price 46.1c. That is a systematic YES-overpricing effect, not a transcript effect — the model contributes nothing to it. It is one earnings season and the 40-60c bucket is **-7.64 c/ct**, so it is an observation to test, not a funded lane.
