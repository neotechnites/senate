# B1 MIRROR-THE-CERTAINTY-TAKER — preregistered live slippage gate

**Run:** 2026-08-16 01:06:17Z → 02:36:17Z (90.0 min), 2,493 global-tape polls @2s, keyless GETs via VPS.
**Strictly read-only. No orders placed.**
**Raw samples:** `/Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research/mirror_slippage_20260816.jsonl` (322 rows)
**Capture script:** `/home/ubuntu/mirror_slip.py` on VPS (129.146.115.241); log `/home/ubuntu/mirror_slip.log`

## Method (as preregistered)
Poll the venue-wide trades feed every 2s (1 req, cheaper and lower-latency than 60 per-market polls).
Filter to `KXTEMP*H-` prints. Taker acquire-price `p = yes_px if taker_side==yes else 100−yes_px`.
On `p ≥ 94`: immediately pull the orderbook (t0) and again at +2s (t2). Mirror-side executable ask =
`100 − best opposite-side bid`; depth = size at that level. **Slippage = exec_ask − trigger_price.**

## Volume / trigger rate
| metric | value |
|---|---|
| TEMP hourly prints seen | 818 |
| triggers (p ≥ 94) | **322** (39.4% of all TEMP prints) |
| **trigger rate** | **215 / hour** across the 6-city universe (60 open markets) |
| by series | MIAH 112, AUSH 73, NYCH 53, LAXH 51, DCH 25, CHIH 8 |
| by trigger price | 99c:87, 98c:81, 97c:54, 96c:46, 95c:29, 94c:25 |
| block trades | 0 |
| detection lag | median 2.76s, p90 12.9s (p90 inflated by serial trigger handling) |
| feed saturation | 38 / 2,493 polls hit the 1000-trade cap → ~1.5% of prints may be unseen (random, not price-selective) |

n = 322 ≫ the 30-trigger preregistered minimum. **No small-n caveat.**

## Slippage distribution (t0 book; t2 is materially identical)

**Of 322 triggers, 139 (43.2%) had ZERO executable liquidity on the mirror side** — the taker's own
print cleared the book and nothing was offered at any price. Those are not slippage, they are
non-events: you cannot mirror at all.

Among the **183 fillable** triggers (3 crossed-book outliers at −6c/−88c/−89c excluded → n=180):

| stat | value |
|---|---|
| mean slippage | **+0.72c** |
| median | **+1.0c** (raw untrimmed median 0.0c — the sample sits exactly on the 0/1 boundary) |
| p25 / p75 / p90 | 0c / +1c / +2c |
| sd | 0.89c |
| histogram | 0c: 88 (48%), +1c: 62 (34%), +2c: 20 (11%), +3c: 7, +4c: 2, ≤−1c: 4 |
| fills at ≤ +0.5c | 50.3% of fillable, **28.6% of all triggers** |
| fills at ≥ +2c | 15.8% of fillable |
| detect-lag ≤4s subset (n=138) | median 0.0c, mean +0.65c — faster detection barely helps |
| spread at trigger | median 7c, mean 16c |
| depth at exec ask | median 77 ct, p25 5 ct |

**Capacity (contract-weighted, the number that actually sizes the book):** 15,859 trigger contracts
in 90 min. Mirrorable at ≤ trigger price: **2,522 ct (15.9%)**. At < trigger+2c: **3,659 ct (23.1%)**.
Median trigger size is **2 contracts**; p90 is 83. Depth ≥ trigger size in 84.5% of fillable cases,
but depth ≥ 100 ct in only 40.3%.

## VERDICT: **HALVED** (not dead)

Per the preregistered thresholds — DEAD if median ≥ +2c, HALVED if ≥ +0.5c, ALIVE if < +0.5c:

- Median slippage is **+1.0c** (trimmed) / 0.0c (untrimmed), mean **+0.72c**. Squarely in the HALVED
  band, nowhere near the +2c kill line.
- Backtest edge +1.22c/ct minus mean slippage +0.72c/ct → **residual ≈ +0.50c/ct**, i.e. ~41% of the
  paper edge survives. Against the backtest's t=+5.1 this scales to roughly **t ≈ 2.1** — still
  positive, no longer overwhelming.

**Two haircuts the preregistration did not price, and they are bigger than slippage:**

1. **43.2% of triggers are unfillable at any price.** The backtest assumed every one of the 1,551
   in-band prints was mirrorable. It was not. This alone cuts the $1,231 to roughly $700 before
   slippage, and combined with slippage to roughly **$285 equivalent over the same 374 market-hours**.
2. **Capacity is tiny.** Only 15.9% of trigger contracts can be mirrored at the trigger price.
   Median trigger is 2 contracts. Even at 215 triggers/hour this is a very small-dollar surface —
   the per-contract edge is real but the contract count that clears both the fill test and the
   price test is ~28 ct/hour at ≤trigger price across all 6 cities.

## Recommendation for the next stage
Do **not** fund a general "mirror every ≥0.94 print" rule. The measurable, surviving subset is:
mirror only when the post-print book still shows an ask at **exactly the trigger price** (slip 0c,
48% of fillable cases, mean edge ≈ full +1.22c) **and** depth ≥ 25 ct. That is a live-book
precondition, checkable in one GET, and it converts the strategy from "+0.50c on everything" to
"+1.2c on the ~29% of triggers that pass". Next gate should be a settlement-linked replay: hold
this capture's 92 zero-slippage samples to settlement and confirm the +1.22c backtest edge survives
on the *fillable* subpopulation specifically — the 43% that clear the book may be exactly the
best-informed prints, which would be a selection bias against us.

Fees are unchanged and already in the backtest (`ceil(0.07·n·p·(1−p))`; ~0.33c/ct at p=0.95).
