# B1 MIRROR-THE-CERTAINTY-TAKER — night-1 post-mortem and kill

**Run:** 2026-08-17, read-only keyless GETs via VPS 129.146.115.241. **No orders placed.**
**Lane status:** HALTED (`stop_loss`, `mirror_halt.json`) and staying halted.
**Verdict: DEAD.**

Night 1 realized **-$49.10 net** (+$0.95 on one clip, -$50.05 on two clips in one market).
Ledger: `/home/ubuntu/kalshi_data/mirror_pilot.jsonl` (VPS), 1,044 rows, 3 sessions.

---

## 1. What happened in KXTEMPAUSH-26AUG1621-T93.99

**Settlement pins Austin at exactly 93°F.** In the hour-21 ladder, `T92.99` settled **yes** and
`T93.99` settled **no**. We bought the single boundary strike in the ladder and missed by **1°F**.
`T94.99`–`T98.99` all settled no as well; the crowd's modal view was wrong across the entire
upper ladder, not just at our strike.

Full tape, `/markets/trades` (44 prints, 0 block trades), YES-price path:

| time (Z) | taker | ct | yes px | note |
|---|---|---|---|---|
| 00:00:03 | yes | 20.00 | 87 | |
| 00:00:32 | yes | 55.00 | 89 | |
| 00:03:18 | yes | 16.03 | **94** | first trigger; we skipped, exec ask 95c |
| 00:06:26 | yes | 55.00 | 95 | skip_slip (ask 96) |
| 00:13:07 | yes | 3.00 | 96 | skip_slip |
| 00:14:12 | yes | 2.00 | 97 | skip_slip |
| **00:15:53** | yes | **0.01** | **98** | a one-hundredth-of-a-contract print sets 98c |
| 00:16:07 | yes | 50.00 | 98 | |
| 00:17:06 | yes | 5.00 | 98 | |
| 00:17:31 | yes | 1.02 | 98 | |
| **00:19:44** | yes | **0.01** | 98 | **trigger for `mrp-1786925985-1`** |
| 00:19:46 | yes | 14.04+1.00+18.96 | 98 | **= our 34 ct fill, $33.32** |
| **00:23:39** | yes | **173.81** | 98 | **trigger for `mrp-1786926219-2`** (largest print of the session) |
| 00:23:40 | yes | 17.00 | 98 | **= our 17 ct fill, $16.66** |
| 00:47:15–00:47:52 | yes | 220.00 | **99** | last of the momentum |
| **00:51:01** | **no** | 60.00 | 95 | **the turn — first informed seller, 9 min before close** |
| 00:53:48 | no | 71.00 | 36 → 1 | book collapses 99c → 1c in 167 seconds |
| 00:54:28–00:57:46 | yes | 934.00 | 1 | scavengers |
| 01:00:00 | — | — | — | close; settles **NO** |

**~662 ct of YES takers bought at ≥94c and were wiped.** Our $49.98 was 7.7% of that.

This is the marginal-temperature regime the funding conditions explicitly demanded be tested
(limit #2 of `mirror-settlement-replay-20260816.md`). It was tested. The strategy failed it.

## 2. Manipulation shape — hypothesis REJECTED

Both bait sub-hypotheses fail on the tape:

- **Nobody sold into the mirrors.** Between the first 98c print (00:15:53) and the last 99c print
  (00:47:52), there were **zero NO takers at any price**. The first NO taker appears at 00:51:01,
  four minutes after the last YES buy and after the information arrived. Nobody painted 98c and
  sold; the counterparty to all of it was a resting maker who was simply right. The prints were
  **sincere and sincerely wrong** — which is strictly worse than manipulation, because
  manipulation is filterable and being-wrong is not.
- **Trigger size does not discriminate.** Clip 1 was triggered by a **0.01 ct** print — absurd, and
  a real defect. But clip 2 was triggered by a **173.81 ct** print, the largest single trigger in
  that market's life, and it was equally wrong. On night 1 as a whole, settle-with-taker by trigger
  size: <1 ct 86.7% (n=90), 1–10 ct 93.8% (n=576), 10–100 ct 90.3% (n=196), ≥100 ct 97.8% (n=46).
  **Every bucket is below the 98.11% breakeven**, including the largest.

Night-0 triggers were not meaningfully different in shape: median 2.00 ct across all 322,
median 5.17 ct on the gated 62, 21% of gated triggers sub-1-contract. Same distribution,
opposite outcome. The difference between the nights is the **weather**, not the tape.

## 3. The decisive number: night 1 is an independent 908-trigger sample

Night 1 logged **1,030 triggers ≥94c**, of which 908 resolve — **~3x the night-0 sample**, and
it includes marginal hours. Breakeven win rate is **98.11%**.

| sample | n | settle-with-taker |
|---|---|---|
| night-0 fillable (`mirror-settlement-replay-20260816.md`) | 183 | **98.91%** |
| night-0 preregistered subset | 62 | **100.00%** |
| **night-1 all resolved triggers** | **908** | **92.51%** |
| **night-1 live-gate-equivalent** (zero-slip, depth ≥25) | **133** | **87.22%** |

Two-proportion z on the fillable arms: **z = 3.22, p = 0.0013**. The 98.9% and the 92.5% are not
the same population. **12 of 19 market-hours on night 1 contained at least one wrong certainty
print** (Austin-1621: 23 wrong of 85). On night 0, **zero of 9 clusters** contained one.

At 92.51% and a 95.90c mean exec, EV = `0.9251·4.1 − 0.0749·95.9` ≈ **−3.4c/ct**;
at the live gate's 87.22%, ≈ **−8.5c/ct**.

## 4. Concentration + trigger-size counterfactuals

Re-run of `settlement_status_full_20260816.json` + `mirror_slippage_20260816.jsonl`, same
ceil-fee pricing and sizing (`min(count, depth, 100)`), then the identical replay on night 1.

| gate | night-0 net | night-0 worst mkt-hr | **night-1 net** | **night-1 worst mkt-hr** |
|---|---|---|---|---|
| (0) baseline live gate | +2.05 c/ct (n=62, t=5.73) | **+$0.01** | **−8.49 c/ct** (n=133, t=−2.03) | **−$76.76** |
| (a1) max 1 clip / market-hour | +2.25 (n=9, t=5.28) | +$0.01 | **−1.01** (n=15) | −$4.72 |
| (a2) max $17 / market-hour | +2.29 (n=12, t=5.10) | +$0.02 | **−9.09** (n=30) | −$17.08 |
| (b) trigger_ct ≥ 10 | +2.09 (n=29, t=5.84) | +$0.20 | **−8.00** (n=67) | −$77.17 |
| (c1) 1 clip + trigger ≥10 | +2.26 (n=8, t=5.32) | +$0.14 | **−4.44** (n=12) | −$28.40 |
| (c2) $17 cap + trigger ≥10 | +2.33 (n=9, t=5.19) | +$0.14 | **−6.64** (n=15) | −$17.08 |

**The +1.59c does not survive.** Pooled over both nights at the live gate:
`(1443·(+2.05) + 2042·(−8.49)) / 3485` = **−4.13 c/ct**. Cluster-weighted over 24 clusters:
**−10.4 c/ct**.

Two things this table proves, and they are both fatal:

1. **The gates are unfalsifiable on night-0 data.** The worst market-hour in the entire 322-trigger
   historical sample is **+$0.01** — there is no losing market-hour anywhere in it. A concentration
   cap cannot be tuned on a sample containing zero instances of the event it exists to survive.
   Every "+2.0c/ct, t=5.x" in the funding report was measured on a night where the strategy could
   not lose, and the t-statistic was measuring the *level* of a constant, not a risk-adjusted edge.
2. **Applied to tonight, the best gate is not survival, it is slower bleeding.** `trigger_ct ≥ 10`
   would have blocked clip 1 (the 0.01 trigger, −$33.37) but clip 2's 173.81 ct trigger sails
   through; with the full $50 budget it takes the larger clip and loses **more**. The `$17/market-hour`
   cap is the only rule that bounds the night, at **−$17.08**, and it bounds every future night to
   −$17 on a lane whose honest expectancy is now negative.

## 5. Verdict: DEAD

> **Grave line:** B1 mirror-the-certainty-taker died on 2026-08-17 at 01:31:52Z in
> KXTEMPAUSH-26AUG1621-T93.99, buying 51 contracts of "Austin hits 94°F" at 98c on a night
> Austin reached 93°F. It was never an edge — it was a 98.9% win rate harvested from one
> physically-determined hot evening, priced as if the 1.1% tail were the whole risk. The
> independent 908-trigger night that followed printed 92.51%, six points below the 98.11%
> breakeven, and −8.49c/ct through the exact live gate. Risking 98c to win 2c requires being
> right 98.11% of the time; the tape says the certainty takers are right about 92%. Two nights,
> pooled, −4.13c/ct. The 1.59c was regime luck and the negative skew collected it back in
> 167 seconds.

**Not CONDITIONAL, and the reasons are structural, not sizing:**

- The failure mode is **not filterable by anything observable at trigger time**. Not trigger size
  (largest bucket, 97.8%, still sub-breakeven), not depth, not slippage, not block-trade flag,
  not counterparty behaviour (no adverse flow existed until the information landed). The only
  variable that separates night 0 from night 1 is *how close the outcome was to the strike* —
  knowable only at settlement.
- **Payoff geometry is unfixable.** 2c up, 98c down needs 98.11%; the honest estimate is 92.51%
  ±1.7pp. That is not a gate problem, it is a 6-point hole. No position sizing makes a
  negative-expectancy bet positive.
- The prior held exactly: **high-win-rate / negative-skew lanes die like this**, on the first
  regime where the thing everybody was certain about turned out to be a coin flip at the boundary.

**What would have to be true to reopen — and none of it is a tweak to this lane:**

1. A settle-with-taker rate **≥ 99.0%** measured on ≥1,500 triggers spanning **≥10 nights** with
   at least 3 independently-classified marginal-outcome nights, with the 95% lower bound above
   98.11%. Night 1 alone puts the pooled point estimate at ~94% over 1,091 triggers; clearing
   99.0% from here is arithmetically out of reach without discarding night 1, which is not
   permitted.
2. An **ex-ante marginality filter** validated out-of-sample — e.g. refusing any strike within
   2°F of the live METAR/NWS observation, or any ladder position where the adjacent strike is
   not itself ≥97c. Note this is a different strategy (it needs the weather feed, which the
   mirror lane by construction does not use), and it should be proposed as such rather than as a
   restart. A mirror that has to check the thermometer is not a mirror.
3. Any restart proposal must be priced against **−4.13c/ct pooled**, not against the +1.59c,
   and must carry a preregistered kill at n=100 triggers.

Absent all three, the lane is closed. The reusable asset from this work is the trigger-capture
infrastructure (`mirror_slip.py`, the 2s global-tape poller), not the signal.

---

**Receipts**
- `/Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research/mirror_slippage_20260816.jsonl` (322 night-0 triggers)
- `/Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research/settlement_status_full_20260816.json` (56/56 finalized)
- `/home/ubuntu/kalshi_data/mirror_pilot.jsonl` (VPS — night-1 ledger, 1,030 triggers ≥94c)
- `/home/ubuntu/aus_tape.json` (VPS — full trade tape, Austin hour-21 ladder T92.99–T95.99)
- Replay scripts: `/home/ubuntu/n1.py`, `/home/ubuntu/n2.py`, `/home/ubuntu/tape2.py` (VPS)
