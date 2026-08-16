# LIP seats — mechanism decomposition and the $6.50 bar
Lane 1, 2026-08-16. Read-only. All figures from VPS receipts; no orders placed.

Sources:
- `/home/ubuntu/kalshi_data/autoseat/autoseat.jsonl` — 1,167 events, 574 `seat_rate`, 163 live `cycle` with `spent_usd`
- `/home/ubuntu/kalshi_data/autoseat/credit_receipts.jsonl` — venue `/incentives` estimates feed, 3 snapshots
- `/home/ubuntu/senate/nestor-wt-lipv5/tools/lipseats/autoseat.py` — gate constants (1,606 lines)
- `~/scratchpad/ip_2026-08-15.jsonl` — 141,058 LIP program definitions
- `data/research/books_snapshot_T-7h5_20260815T2030Z.json` — all 110 ballot books
- `data/research/fill-forensics-20260815.md` — storm/sweep replay (reused, not re-run)

Working scripts: `~/scratchpad/lane1_{a,b,c,d,e,f,g}.py`

---

## 0. Headline

**The $2.04/day per $100 figure was a denominator error, and the strategy was already over
the bar before the gates went on.** Corrected with a time-weighted escrow denominator:
**$10.46/day per $100 at-risk, $7.67/day per $100 registered.**

The gates cost 59% of that. Gated Rung B lands at **$3.15/day per $100** — below the bar.
The gap closes on exactly one lever: **sustained share ≥ 0.331**.

**Unit correction, load-bearing:** `period_reward` is in centicents (÷10,000), not cents.
Receipt `reward_centicents: 7897 → reward_usd 0.7897` pins it. NC-A2's pool is **$285.00
per program window** = $62.20/day, not $28,500. Any prior note using ÷100 is 100x high.

---

## 1. The accrual identity, calibrated against real credits

Model: `rate = pool_per_day × share × df^ticks_behind`, df base 0.5 (venue-published 5000 bps).

Per-sample integration over all 574 `seat_rate` events versus the venue's own credit feed:

| | modelled | real | ratio |
|---|---|---|---|
| all 9 logged tickers | $43.11 | $32.13 | **0.745** |

Refitting the df base by log-SSE across tickers: **best fit b = 0.8, not 0.5.**

| df base | 0.05 | 0.125 | 0.25 | **0.5** | 0.7 | **0.8** | 0.9 | 1.0 |
|---|---|---|---|---|---|---|---|---|
| log-SSE | 52.5 | 26.7 | 12.8 | 4.30 | 2.62 | **2.49** | 2.68 | 3.10 |

The single strongest evidence: **KY-A1 sat at ticks_behind 2–4 in all 42 of its samples**
(model `E[share·df]` = 0.0153, predicted $0.42) **and accrued $2.27 — 5.4x the model.**
This independently reproduces the forensics receipt of **tb=0 $0.184/seat-h vs tb≥1
$0.187/seat-h — no yield difference at all.** Two different measurements, same answer.

**Verdict (a): the venue's published discount factor overstates the off-touch penalty by
~2.5x in log-slope. Being one tick behind costs ~20%, not 50%.** The residual flat 0.745
haircut is most likely dwell over-counting — we sample every 900 s while Kalshi samples
continuously, and 177 `outbid_tick` events confirm frequent between-sample outbidding.

Practical calibration: `realized $/seat-hour ≈ 0.745 × (pool_day/24) × share × 0.8^tb`.

---

## 2. The 22x per-seat spread is dwell time, not seat quality

The brief asked me to explain NC-A2 $8.85 vs AR-A578 $0.39 with numbers. It inverts:

| | credit | seat-hours | **$/seat-hour** | pool/day | mean share |
|---|---|---|---|---|---|
| NC-A2 | $8.8508 | 37.5 | $0.2360 | $62.20 | 0.144 |
| AR-A578 | $0.3904 | 0.5 | **$0.7808** | $54.56 | 0.512 |

**22.7x credit ratio = 75x dwell ÷ 3.31x rate. AR-A578 was the 3.3x *better* seat.**
It had the lower pool and the higher share, and it earned more per hour on both counts.
Its dwell was 0.5 h because **our own storm breaker ejected it** — the forensics N=4/1h
backtest caught exactly {AR-A578, KY-A1}, the same two markets.

The full per-ticker table:

| ticker | seat-h | mean share | mean tb | pool/day | credit | $/seat-h |
|---|---|---|---|---|---|---|
| NC-A2 | 37.5 | 0.1439 | 0.04 | 62.20 | 8.8508 | 0.2360 |
| AL-A4 | 37.5 | 0.1205 | 0.44 | 54.56 | 6.5360 | 0.1743 |
| IA-A1 | 9.0 | 0.4692 | 0.64 | 62.20 | 6.0576 | 0.6731 |
| GA-A2 | 12.2 | 0.2354 | 0.78 | 62.20 | 4.3791 | 0.3575 |
| KY-A1 | 10.5 | 0.0930 | 3.43 | 62.20 | 2.2657 | 0.2158 |
| RI-Q4 | 23.8 | 0.0876 | 0.00 | 43.65 | 2.1884 | 0.0921 |
| AL-A3 | 8.2 | 0.1262 | 1.03 | 54.56 | 0.7897 | 0.0957 |
| ID-HJR4 | 4.2 | 0.1117 | 1.00 | 62.20 | 0.6683 | 0.1572 |
| AR-A578 | 0.5 | 0.5115 | 1.00 | 54.56 | 0.3904 | 0.7808 |
| **total** | **143.5** | | | | **32.126** | **0.2239** |

AK-BM2 accrued $2.65 with zero `seat_rate` events — seat time exists that predates logging,
so 143.5 h is a floor and $0.2239/seat-h is a mild over-estimate.

---

## 3. Variance attribution: where the dispersion actually lives

`r(mean share, $/seat-h) = +0.983`; `r(pool/day) = +0.240`; `r(mean tb) = −0.006`.

The correlation is not the argument — share is definitionally a multiplicand (Gemini's
objection, conceded). The non-tautological form is variance attribution across the three
multiplicands, in logs:

| | var(log) with df base 0.5 | share of total | **with refit df base 0.8** |
|---|---|---|---|
| pool/day | 0.175 | 15.0% | **24.6%** |
| share | 0.483 | 41.4% | **68.0%** |
| df | 0.507 | 43.6% | **7.4%** |

Under the venue's *stated* df, tick position looks as important as share. Under the df the
venue *actually pays* (§1), **share carries 68% of all dispersion and pool 25%.** Ballot pool
dispersion is genuinely small: across all 110 programs, pool/day runs $21.82–$62.20, CV 0.362.

**Verdict (c): pick the emptiest qualifying books, not the richest pools — by roughly 3:1.**

---

## 4. Share dynamics — and one claim I withdrew

Share by quartile of each seat's life: NC-A2 0.299/0.111/0.082/0.086 (Q4/Q1 = 0.29),
KY-A1 0.15, GA-A2 0.40, AL-A4 0.71, RI-Q4 0.71.

I originally read this as intrinsic crowding decay and proposed "rotate before decay" as a
lever. **Gemini attacked it as a diurnal artifact and was right.** Share by hour-of-day:

```
00Z .18  01 .14  02 .21  03 .12  04 .14  05 .285  06 .24  07 .23
08  .20  09 .19  10 .11  11 .12  12 .11  13 .11   14 .12  15 .17
16  .14  17 .15  18 .13  19 .11  20 .10  21 .10   22 .10  23 .074
```

**Hour-of-day spread is 3.85x — larger than the within-seat decay it was supposed to
explain.** Our long-lived seats spanned overnight→US-day. The lever is deleted.

Diurnal timing is also *not* usable here: seating only 00–09Z raises mean share ~1.48x but
cuts duty cycle to 37.5%, net 0.56x on the per-registered-$100 metric. It only pays if
capital can be redeployed elsewhere, and the mandate is ballot-only.

**Window age at entry does not predict lifetime share the way the brief hypothesised.**
`r(age@entry, mean share) = +0.62` — *later* entries got *higher* share (IA-A1 at 3.61 d →
0.469; AR-A578 at 3.63 d → 0.512; vs AL-A4/NC-A2 at 2.42 d → 0.12/0.14). Early seating is
not the edge.

**Rivals did not retreat as the program aged — they piled in.** Implied rival qualifying
depth `= our_ct × (1/share − 1)`:

```
NC-A2  Q1  601ct → Q2 1881 → Q3 2544 → Q4 2408
AL-A4  Q1 1871   → Q2 2160 → Q3 4164 → Q4 1728
RI-Q4  Q1 1957   → Q2 3192 → Q3 2697 → Q4 2429
family-wide by hour: 00Z 643 … 05Z 1175 … 14Z 3631, 15Z 3769, 16Z 3775   (5.9x rise)
```

This refutes the "we measured a period of competitor retreat" objection: the measured window
was the *most* competitive stretch of the program, so §5's rate is a floor, not a ceiling.

---

## 5. The corrected realized rate

`credit_receipts.jsonl` holds 3 snapshots — all three **identical** at $35.7454 total. That is
not zero accrual: seats were flat after the 08-15 16:52Z fill halt and `seat_rate` stops at
16:41Z. Treat the feed as an unmoving cumulative total for the window, not a rate series.

Ballot-only credit is $34.7746 (the other $0.9708 is older MLB-manager / EOWEEK / Pochettino
programs from Aug 1–4 activity).

Denominator, integrated from per-cycle `spent_usd` over 163 live cycles at 100% span coverage:

```
earning span  08-13 21:10Z → 08-15 16:41Z = 43.53 h = 1.8138 d
escrow-hours                    7,982 USD-h
time-weighted escrow            $183.37       (max $249.72, mean 3.67 concurrent seats)
logged seat-hours               143.5 → 159.8 incl. unlogged cycles
```

| basis | $/day per $100 |
|---|---|
| naive max escrow $249.72 | $7.68 |
| **$250 registered** | **$7.67** |
| **time-weighted at-risk $183.37** | **$10.46** |

Both clear $6.50. The original $2.04 divided $35.75 by 7 days when the accrual window was
1.81 days — a 3.9x error.

Robustness: only AL-A4 could carry pre-span credit (autoseat *adopted* an existing resting
order at 08-13 21:05Z), and AL-A4 is $6.54 = 18.8% of ballot credit, of which only part can
be pre-span. Even attributing *all* of it to unmeasured earlier time gives $8.49/day per $100
registered. The conclusion survives unless >38% of the credit predates the span, which no
ticker supports.

---

## 6. What the gates cost — replayed over the same 43.5 h

Gate constants from `autoseat.py`: `DEFAULT_CURFEW_S = 24h`, `DEFAULT_OFFTOUCH_CYCLES = 4`,
`DEFAULT_STORM_N = 4 / STORM_WINDOW_S = 3600`, `DEFAULT_REENTRY_BAN_S = 7200`.

| gate | seat-h blocked | % of 143.5 | yield cost |
|---|---|---|---|
| **terminal curfew (T-24h)** | 56.8 | 39.5% | 39.9% of credit |
| off-touch eject (4 cycles tb≥1) | 37.8 | 26.3% | see below |
| storm breaker N=4/1h | 12.3 | 8.0% | $4.68 = 16.5% (forensics) |
| post-sweep 2h re-entry ban | — | — | **$0.00, 0 false ejects** |
| **union retained** | **58.9 of 143.5** | | **41.0%** |

Two things make the curfew structurally worse than it looks:

1. **It keys off `prog["end_ts"]` — the LIP program end — not market close.** All 110 ballot
   programs share `end_date 2026-08-16T03:59:59Z`, so **the entire family goes dark at the
   same instant**. There is no rotation escape: 24 h out of a 110 h program = **21.8% of every
   program cycle is unseatable family-wide**. Discovery refuses new windows from 08-15 03:29Z.
2. **The markets do not settle then.** All 111 ballot markets close **2027-11-02** — 15 months
   out. The terminal kill zone is a *rent-expiry* evacuation (rivals unwinding LIP inventory
   before the subsidy stops), not a resolution event.

The off-touch eject buys **risk only, not yield** — measured, not assumed: tb=0 $0.184/seat-h
vs tb≥1 $0.187/seat-h. It removes 26% of seat-hours for zero measured yield difference.
Curfewed hours are likewise not lower-yield (mean share 0.1595 vs 0.1475 outside).

**The gates are still correct on risk.** At $0.2239/seat-h and 3.67 concurrent seats, a
$12.50 adverse fill costs 56 seat-hours = 15.2 wall-clock hours of accrual; a $32.50 fill
costs 145 seat-hours = 39.6 h. Four adverse fills landed in ~44 ungated hours. The gates
comfortably clear their own hurdle.

**Verdict (d): gates cost 59% of yield. $7.67 → $3.15/day per $100 registered.**

---

## 7. Seat count vs seat selection

Achievable share on the 08-15 20:27Z snapshot of all 110 ballot books, using **affordable
size = $50/price** (not a flat 250 — Gemini caught this; price is a hidden lever, since a
$50 seat at $0.09 buys 556 contracts and at $0.85 buys 59):

```
median book 0.152   p75 0.359   p90 0.699   top-5 distinct 0.961
```

Our realized mean share was **0.16 — statistically the median book.** Gemini's point lands:
0.16 is roughly the post-response equilibrium available to anyone playing the median book.
The top-5 (0.961) is an instantaneous pre-response snapshot and I do **not** use it in the
projection. **p75 = 0.359 (2.24x) is the defensible sustained target.**

Marginal book quality by fleet size (mean share of the top-n distinct books):

| seats | capital | mean share | implied $/day per $100 |
|---|---|---|---|
| 1 | $50 | 0.985 | 19.35 |
| **5** | **$250** | **0.961** | **18.88** |
| 10 | $500 | 0.928 | 18.23 |
| 20 | $1,000 | 0.831 | 16.32 |

Marginal share decays only 0.72x from seat 5 to seat 20. **This is a rate problem, not a
capital problem — $1,000 would deliver nearly the same $/day per $100 as $250.** Capital is
capped at $250 by mandate regardless, and that cap costs nothing on this metric.

**Verdict (c): 5 emptiest qualifying books, decisively. Not the 5 richest pools.**

**Blocking constraint:** `HARD_MAX_SEATS = 1` is a Python constant in `autoseat.py`, not a
config knob — "raising this is a CODE change behind a new sealed reg". **Rung B does not
exist today.** Everything below assumes it is raised to 5.

---

## 8. Lever ranking

| # | lever | measured size | notes |
|---|---|---|---|
| **L1** | **share at entry — thin rival touch depth** | 68% of dispersion; 0.152→0.359 = **2.24x** | the only lever big enough to close the gap alone |
| **L2** | **duty cycle / curfew** | 39.9% of credit, **21.8% structural blackout** | keys off program end, not market close; whole family dark at once |
| **L3** | **seat count 1→5** | **~3.5x** deployed capital at ~constant rate | share is per-market; 5 seats in 5 books do not cannibalise. Blocked by `HARD_MAX_SEATS=1` |
| **L4** | **off-touch eject** | 26.3% of seat-hours for **zero** measured yield gain | pure risk purchase; keep it, but price it honestly |
| **L5** | **df recalibration 0.5→0.8** | df drops from 43.6% → 7.4% of dispersion | stop over-paying for tick position in the scorer |
| **L6** | **pool selection** | CV 0.362, 25% of dispersion | weakest; do not optimise for it |
| — | ~~rotation before share decay~~ | **withdrawn** | diurnal artifact (§4) |
| — | ~~diurnal timing~~ | **withdrawn** | 1.48x rate × 0.375 duty = 0.56x net |

---

## 9. Projection — gated 5-seat Rung B at $250

Every step verified independently by Gemini (§10).

```
(1) ungated, per $100 registered   34.7746 / 1.8138 / 250    × 100 = $7.667/day
(2) ungated, per $100 at-risk      34.7746 / 1.8138 / 183.37 × 100 = $10.455/day
(3) gate retention                 58.9 / 143.5                    = 0.4104
(4) gated, current selection       7.667 × 0.4104                  = $3.147/day  ✗
(5) uplift needed for 6.50         6.50 / 3.147                    = 2.066x
(6) breakeven sustained share      0.16 × 2.066                    = 0.331
(7) gated + p75 selection (2.24x)  3.147 × 2.24                    = $7.05/day   ✓
(8) gated + median selection       3.147 × 0.95                    = $2.99/day   ✗
```

**$6.50 is reachable at $250 and needs no more capital — but only if seat selection sustains
mean share ≥ 0.331 and `HARD_MAX_SEATS` goes to 5.** At the median book it fails at $2.99,
and no amount of capital fixes that, because the bar is denominated per $100.

Margin is thin: p75 = 0.359 against a 0.331 breakeven is 8% headroom.

**Runway is the real risk.** The ballot LIP is a one-off `new_event` launch subsidy expiring
**2026-08-16 03:59:59Z**. `KXSTATEBALLOTMEASURE` has 110 `new_event` programs and **zero
`series_lip` successors**. Across all 1,394 families that ever had a `new_event` program, only
**33%** ever received a second program type. The 50–500x census advantage of ballot is a launch
subsidy, and it has hours left. Rung B has nothing to run on unless Kalshi posts a successor.

---

## 10. Gemini exchange (condensed, verbatim attribution)

CLI: `~/.nvm/versions/node/v20.9.0/bin/gemini`. Both rounds ran, exit 0. Prompts and raw
output: `~/scratchpad/gem_r1.txt`, `gem_r1_out.txt`, `gem_r2.txt`, `gem_r2_out.txt`.

### Round 1 — Gemini attacks (6 attacks, verbatim quotes)

1. *"The strongest reason the $10.46/day per $100 AT-RISK is overstated is extreme sample bias.
   The entire 43.53h data window represents the dying hours of a one-off LIP program… it's a
   sample of the competition packing up and going home."*
2. *"Your conclusion that share drives $/seat-hour (r=+0.983) is a textbook case of confusing
   correlation with causation. It is mathematically inevitable, not causally instructive."*
3. *"The 'headroom' in Finding 8 is an illusion. A snapshot of an empty book is not an
   actionable signal… Your realized mean share of 0.16 is not a measure of your failure to
   select, but likely the true, competition-adjusted equilibrium."*
4. *"Are dwell time and rate independent? It is highly plausible they are anti-correlated…
   the highest-yielding opportunities may be in the most unstable, flighty markets."*
5. *"The 'decay' is not intrinsic to the seat. It's an artifact of when you entered… The causal
   claim should be about timing, not rotation."*
6. *"You calculate that gates reduce uptime to 41% and naively multiply this by the flawed,
   overstated ungated rate. This assumes the expected value of a seat-hour is identical across
   all 143.5 hours… That is certainly false."*

### Round 2 — my answers, and Gemini's verification

| # | outcome | evidence |
|---|---|---|
| 1 | **refuted** | rival depth rose 5.9x (643→3,775 ct) across the window — rivals piled in, not out. The window was the *most* competitive stretch, so $10.46 is a floor |
| 2 | **partly conceded, restated** | dropped the correlation claim; replaced with log-variance attribution (share 68%, pool 25%, df 7% at the refit df base) |
| 3 | **magnitude conceded** | redid headroom with affordable size $50/price; median 0.152 does bracket our 0.16. Dropped top-5 (0.961) from the projection, used p75 (0.359) |
| 4 | **refuted for these cases** | forensics storm backtest caught exactly {AR-A578, KY-A1} — their short dwell was gate-induced, not market flightiness |
| 5 | **fully conceded** | hour-of-day share spread 3.85x > within-seat decay 0.29–0.71x. Lever deleted |
| 6 | **tested, holds** | curfewed hours had *higher* share (0.1595 vs 0.1475); forensics measured tb=0 $0.184 vs tb≥1 $0.187/seat-h. Risk point accepted and quantified instead (§6) |

Gemini's verification of §9, verbatim: *"All calculations are correct."* On the ratio
compounding: *"Your approach of multiplying the gated rate by the selection uplift is a valid
first-order approximation. The two factors — gating and selection — are largely independent.
Gating is a mechanical rule applied after a market is selected, while selection is the process
of choosing which markets to enter."*

Its verdict: *"$6.50/day per $100 registered is defensible, but it is aggressive and hinges on
two critical, non-trivial assumptions"* — sustaining share ≥ 0.331, and raising
`HARD_MAX_SEATS`. Its single number: *"$7.05/day… The most important context for that number
is the breakeven sustained share of 0.331."*

One Gemini claim I do **not** adopt: it argued the off-touch gate removes the lowest-share
hours and so supplies an unmodelled tailwind. I measured the opposite for the curfew
(curfewed hours had higher share), so the projection takes no credit for it.

---

## 11. What I could not measure

- **Feed grain.** Three identical snapshots cannot distinguish "estimates update daily at the
  04:00Z rollover" from "we genuinely earned nothing after the halt". If the feed *is* daily-
  stale, $34.77 covers only 30.83 h and the true rate is **$14.8/day per $100 at-risk**. Both
  branches clear the bar; the reported figure is the conservative one. One receipt pull
  straddling a 04:00Z boundary while seated settles it.
- **Pre-logging seat time.** AK-BM2 earned $2.65 with no `seat_rate` events, and AL-A4's seat
  was *adopted* from a pre-existing order. Bounded in §5, not eliminated.
- **Sweep detection is inferred.** Every "sweep" is a touch collapse in the L2 tape; cancels
  and trades are indistinguishable (per fill-forensics). The storm-breaker cost of 16.5% is
  reused from that replay, not re-derived here.
- **Share sustainability.** The p75 = 0.359 target is a snapshot with no rival response
  modelled. It is the single assumption the whole projection rests on and it is untested.
