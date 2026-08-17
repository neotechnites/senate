# Terminal close analysis — 2026-08-16 03:59Z ballot LIP window

**Analyst runtime:** 2026-08-16 04:29–04:31Z. Read-only. No orders, no state writes.
**Subject:** the first `KXSTATEBALLOTMEASURE` window-close observed from outside, with instruments
running and **zero seats of ours in the family**.

## Instruments

| # | dataset | span | rows | role |
|---|---|---|---|---|
| 1 | Mac `data/research/terminal_capture_20260815.jsonl` | 08-15 20:25 → 22:07Z | 2,331 | pre-close arm |
| 2 | VPS `/home/ubuntu/kalshi_data/terminal_capture_20260815.jsonl` | 08-15 22:10 → 08-16 03:52Z | 7,659 | **C2 third dataset** |
| 3 | VPS `competition/deltas-20260816-0{0,1,2,3}.jsonl.gz` | 08-16 00:00 → 04:00Z | 13,223 ballot msgs | independent L2 instrument |
| 4 | `incentive_programs` feed, pulled live 04:30:01Z | — | 10,000 programs | renewal watch |

110 markets, 5-min cadence, merged span **T-7.6h → T-0.13h**. Local copy of instrument 2:
`/private/tmp/claude-501/-Users-ryanwhitehead-Documents-senate-domains-kalshi/162f05b7-b9bf-49dd-b319-057450acadb5/scratchpad/vps_capture.jsonl`.

### Data-quality finding that had to be fixed before anything else

65 of 9,900 capture rows are **HTTP-200 responses carrying an empty orderbook** — all 65 in the Mac
arm, all between 20:00 and 22:10Z. Example, `WV-A1`:

```
21:42Z  yes_top [96,92,87,86]  no_top [2,1]
21:47Z  yes_top []             no_top []      <-- empty 200
21:52Z  yes_top [96,92,87,86]  no_top [2,1]   <-- identical book restored
```

Fed to the production sweep detector these manufacture **96-, 94-, 93-tick "sweeps."** Uncorrected
the night shows 90 sweeps and 2 storm edges; corrected it shows **31**. Every number below is on
the corrected set (rows with both sides empty dropped). See §3 for the gate consequence.

---

## 1. C2 FINAL VALIDATION — preregistered, third dataset

Runner: `…/scratchpad/c2b.py` (unmodified; the preregistered statistic). Depth = **min across the two
touch sides of the raw `orderbook_fp` level value, 1c/99c excluded**; in-band mid 15–85c; consecutive
per-ticker snapshot pairs. Window: **final 4 hours into the close, 23:59Z → 03:59Z**, VPS arm only.

| rival touch depth | pairs | touch-move % | ≥5c (mid) | ≥5c (side) | ≥10c (mid) |
|---|---:|---:|---:|---:|---:|
| ≤50 | 1,357 | **3.10** | 6 | 11 | 1 |
| 50–250 | 460 | **4.13** | 4 | 7 | 1 |
| 250–1000 | 520 | **0.96** | 3 | 4 | 1 |
| >1000 | 1,151 | **0.17** | 0 | 0 | 0 |

Coarse, as the kill line is written:

| bin | pairs | touch-move % | ≥5c mid | ≥5c side |
|---|---:|---:|---:|---:|
| ≤250 (thin) | 1,817 | **3.36** | 10 (0.550%) | 18 (0.991%) |
| >250 (thick) | 1,671 | **0.42** | 3 (0.180%) | 4 (0.239%) |

- **touch-move ratio thin/thick = 8.0x** (z = 6.27)
- **≥5c mid: 0.550% vs 0.180% → 3.06x**, kill line is 2x → **not crossed** (z = 1.80)
- **≥5c side: 0.991% vs 0.239% → 4.15x**, kill line is 2x → **not crossed** (z = 2.80)
- Monotonicity across all four bins holds, and the >1000 bin is still **0 dislocations in 1,151 pairs**.

### VERDICT: C2 SURVIVES its third window-close. No kill.

### But the margin narrowed, and the reason is diagnosable

The original panel had **zero** ≥5c events anywhere above 250. This close has four. All 22 ≥5c
dislocations in the final 4h, with the depth that preceded them:

| time (Z) | ticker | depth | before | after | Δmid | Δside |
|---|---|---:|---|---|---:|---:|
| 00:36 | NM-A4 | 80 | 37/71 | 37/88 | 8.5 | 17 |
| 00:51 | NM-A4 | 80 | 37/88 | 38/96 | 4.5 | 8 |
| 02:01 | ID-HJR4 | 39 | 78/82 | 76/90 | 3.0 | 8 |
| **02:01** | **ID-P1** | **492** | 31/35 | 32/42 | 4.0 | **7** |
| 02:05 | CO-PNN | 155 | 57/58 | 31/53 | 15.5 | 26 |
| 02:06 | ID-HJR4 | 28 | 76/90 | 76/81 | 4.5 | 9 |
| 02:06 | ID-P1 | 21 | 32/42 | 37/42 | 2.5 | 5 |
| 02:06 | LA-A272 | 50 | 31/32 | 34/39 | 5.0 | 7 |
| 02:10 | CO-PNN | 25 | 31/53 | 46/53 | 7.5 | 15 |
| 02:12 | UT-SJR2 | 125 | 71/72 | 62/69 | 6.0 | 9 |
| 02:16 | MO-A7 | 220 | 17/21 | 23/28 | 6.5 | 7 |
| **02:16** | **NH-CACR13** | **286** | 29/30 | 35/42 | 9.0 | **12** |
| **02:16** | **OK-SQ845** | **276** | 81/82 | 70/77 | 8.0 | **11** |
| **02:17** | **WI-Q1** | **973** | 54/96 | 85/92 | 13.5 | **31** |
| 02:17 | WY-I1 | 2 | 27/33 | 26/48 | 7.0 | 15 |
| 02:31 | NM-A4 | 5 | 38/98 | 38/39 | 29.5 | 59 |
| 02:40 | AZ-P141 | 205 | 79/83 | 73/93 | 2.0 | 10 |
| 02:40 | AZ-P144 | 5 | 57/62 | 57/78 | 8.0 | 16 |
| 02:40 | AZ-P319 | 5 | 72/77 | 72/85 | 4.0 | 8 |
| 02:45 | AZ-P141 | 87 | 73/93 | 81/88 | 1.5 | 8 |
| 02:45 | AZ-P144 | 5 | 57/78 | 57/62 | 8.0 | 16 |
| 02:45 | AZ-P319 | 1 | 72/85 | 72/77 | 4.0 | 8 |

**All four thick-bin (>250) events land in the 02:01–02:17Z burst** — a 16-minute band, T-2.0h to
T-1.7h. Outside that band, depth ≥250 bought complete immunity exactly as the original panel said.

**Qualifier to carry forward:** depth ≥250 is protective *in the base state* and **degrades inside a
terminal storm**. Depth and the storm breaker are not redundant here; the storm breaker is what
covers the residual C2 does not.

### Cumulative C2 progress

| observation | metric | ≤50 vs >1000 | coarse ≤250 vs >250 | verdict |
|---|---|---:|---:|---|
| original panel (3,213 in-band pairs) | touch-move | **45x** | 19.4x | no kill; 0 thick ≥5c |
| live prelim | touch-move | **11.6x** | — | no kill |
| **this close, final 4h (3,488 pairs)** | touch-move | **18.2x** | **8.0x** | **no kill** |
| this close, full VPS span (5,138 pairs) | touch-move | 20.6x | 11.1x | no kill |

**Window-closes banked: 1 of 3.** C2 remains TRADE-shaped (subtraction). Two more independent
window-closes required before the depth ≥250 floor is treated as validated. Both remaining
observations should record thick-bin dislocations separately inside and outside storm bands, since
that is now the only place the effect leaks.

---

## 2. WHAT A CLOSE LOOKS LIKE WITH NOBODY TO SHOOT AT

Detector: the exact production one (`replay3.py::note_book`) — worst tick-drop of the raw touch
across yes/no between consecutive marks, `SWEEP_TICKS = 4`.

### Sweeps still happened. Density, per hour:

| hour (Z) | T-minus | native ~5min | **900s production grid** | ≥ storm threshold (4/1h)? |
|---|---|---:|---:|---|
| 20:00 | T-8h | 3 | 2 | no |
| 21:00 | T-7h | 5 | 1 | no |
| 22:00 | T-6h | 5 | 1 | no |
| 23:00 | T-5h | 1 | 1 | no |
| 00:00 | T-4h | 2 | 1 | no |
| 01:00 | T-3h | 0 | 1 | no |
| **02:00** | **T-2h** | **15** | **14** | **YES** |
| 03:00 | T-1h | 0 | 0 | no |
| **total** | | **31** | **21** | |

**Two-thirds of the night's sweeps fall in one hour, T-2h to T-1h, with zero seats of ours in the
family.** Largest: `WI-Q1` 39 ticks at 02:17Z, `NM-A4` 31 ticks at 23:46Z, `CO-PNN` 26 ticks at 02:10Z.

### The independent L2 instrument agrees

Ballot-family orderbook deltas, ≥4 distinct price levels removed on one side within one second:

| hour (Z) | T-minus | ballot delta msgs | ≥4-level 1s cascades |
|---|---|---:|---:|
| 00:00 | T-4h | 1,980 | 15 |
| 01:00 | T-3h | 2,216 | 10 |
| **02:00** | **T-2h** | **4,026** | **63** |
| 03:00 | T-1h | 5,001 | 31 |

Same shape, same peak hour, from a different recorder with 1-second resolution and no dependence on
the 5-min poller. Biggest cascades were real money, not dust: `WY-I1 no` 8 levels **$5,198** at
03:14:42Z, `CO-PNN yes` 7 levels **$5,293** at 02:09:57Z, `LA-A272 no` 8 levels **$3,242** at 02:07:33Z.

### But the makers did not leave, and the books never emptied

| T-h | 2-sided % | median min-side touch depth | median $book/mkt | median levels | median spread |
|---:|---:|---:|---:|---:|---:|
| 7.5 | 97.0 | 500 | 17,411 | 14 | 1c |
| 5.0 | 100.0 | 451 | 16,596 | 15 | 1c |
| 3.0 | 100.0 | 500 | 16,843 | 15 | 1c |
| 2.0 | 100.0 | 484 | 17,485 | 15 | 1c |
| 1.0 | 100.0 | 487 | 16,319 | 15 | 1c |
| 0.5 | 100.0 | 475 | 16,201 | 16 | 1c |
| **0.0** | **100.0** | **452** | **16,220** | **15** | **1c** |

Family resting capital, non-phantom: **$2,119,583 at T-8h → $1,976,996 at T-0.5h. A 6.7% decline
over 7.5 hours, monotone and gentle, with no cliff.**

Final observed sweep, **03:52Z, T-0.13h, 110 markets:**
- markets one-sided or empty excluding 1c/99c: **0 / 110**
- median min-side touch depth: **452**
- median spread: **1c**

And the sweeps were not evacuations. **18 of 21 (86%) production-grid sweeps had the touch back
within 2c inside one hour.** Only three did not — `KY-A1` (0.93→0.82), `UT-SJR2` (0.71→0.62),
`WI-Q1` (0.93→0.85) — all three in the 02:16–02:17Z burst, all three re-priced rather than abandoned.

### Answer: STRUCTURAL, not prey-driven.

The terminal sweep machinery ran on schedule into a family containing **none of our capital**. It
produced a 14-sweep hour at T-2h, a 63-cascade hour on the L2 feed, and multi-thousand-dollar level
removals — with nothing of ours to take. Predation does not require prey here because **this is not
predation**: it is the LIP maker cohort rolling quotes as the subsidy clock expires. The evidence
that separates the two readings is that resting capital fell only 6.7%, spread never left 1c, 86% of
touches recovered inside an hour, and **100% of 110 books were two-sided with median depth 452 eight
minutes before the close**.

**Correction to the working model:** last week's terminal violence was not *about* our seats. What
was about our seats was that we were **resting sub-250 depth inside the storm band** — the same band
that produced 4 of this week's 4 thick-bin dislocations and 18 of its 22 dislocations overall. The
violence is weather. Our loss was exposure to it.

**One asymmetry worth noting, not yet explained:** last week the sweeps clustered T-24h..T-10h; this
week the single burst is T-2h..T-1h. The mechanism is stable, the *timing* is not, which argues for
keeping the curfew wide rather than narrowing it to the observed burst.

---

## 3. GATE THRESHOLD TUNE-CHECK — receipts

Replayed over the corrected full night at the production 900s cycle grid.

### `sweep_ticks = 4` (post-sweep re-entry ban, 2h)

**FIRED 21 times.** Receipts (900s grid, ticker / T-minus / ticks):

```
20:45 T-7.3h AZ-P319   6    02:15 T-1.8h CO-PNN     11    02:31 T-1.5h MO-A7      8
20:46 T-7.2h LA-A39    8    02:16 T-1.7h ID-P1       7    02:31 T-1.5h ND-CM1     8
21:31 T-6.5h LA-A39    5    02:16 T-1.7h KY-A1      12    02:31 T-1.5h NH-CACR13 12
22:31 T-5.5h LA-A277   4    02:16 T-1.7h LA-A272     7    02:31 T-1.5h OK-SQ845  11
23:46 T-4.2h NM-A4    31    02:17 T-1.7h UT-SJR2     9    02:32 T-1.5h WY-I1     15
00:46 T-3.2h NM-A4    17    02:17 T-1.7h WI-Q1      39    02:45 T-1.2h AZ-P141   10
01:01 T-3.0h NM-A4     8                                  02:45 T-1.2h AZ-P144   16
                                                          02:45 T-1.2h AZ-P319    8
```

**VERDICT: no change to the threshold.** 4 ticks caught every event that later produced a ≥5c
dislocation, and the smallest firing (4 ticks, LA-A277) is a genuine touch collapse. Raising it to 5
would have dropped LA-A277 and AZ-P319 for no benefit; lowering it to 3 adds noise into a detector
whose output feeds a 2h ban.

**VERDICT: one code change is decisive and required.** The detector must reject empty-book
snapshots before comparing marks. Evidence: 65 empty HTTP-200 rows manufactured **59 phantom sweeps
(90 → 31 native)** and **2 spurious storm rising edges**, with fake magnitudes up to 96 ticks — an
order of magnitude above any real event that night. In production this fires the 2h re-entry ban and
the storm breaker on nothing. Guard:

```python
def note_book(tk, ybk, nbk, now):
    if not ybk or not nbk:      # empty-200 from the venue is not a sweep
        marks.pop(tk, None)     # drop the stale mark so the NEXT pair is not compared across it
        return
```

Dropping the mark (rather than merely skipping) matters: otherwise the recovery snapshot 5 minutes
later is compared against a pre-glitch mark and the phantom reappears with the opposite sign.

### `storm` = 4 family sweeps in trailing 1h

**FIRED ONCE, at 08-16 02:30:00Z, T-1.50h, n = 6 in the trailing hour**, peaking at 14 in the
02:00–03:00Z hour. On the finer native cadence it fires twice — 21:30Z (T-6.5h, n=8) and 02:15Z
(T-1.75h, n=4).

**VERDICT: no change.** The single production-grid firing sits 16 minutes after the burst opened
(02:01Z) and covers the entire band that contains all four thick-bin ≥5c dislocations — precisely
the residual risk C2's depth floor does not catch (§1). The threshold is doing the job it was
specified for. It also stayed quiet through the six preceding hours, which had 7 sweeps between
them: no false-positive cost on this night.

### `curfew` = 24h (effective window floor `max(90000, 86400 + 2×900)` = 90,000s)

**FIRED CONTINUOUSLY.** The window closed 08-16T04:00Z, so curfew began refusing at
**08-15T03:00:00Z** and refused every candidate for the whole 25 hours to the close. The entire
observed span (T-7.6h → T-0.13h) is inside it, as is 100% of the night's sweep activity, and all 22
≥5c dislocations.

**VERDICT: no change.** This night cannot discriminate the threshold — nothing was seatable at any
point in it, so there is no in-sample evidence either way. Note only that the burst arrived at
T-1.5h while last week's arrived T-24h..T-10h; a curfew narrowed to the observed terminal band would
have been wrong last week. Leave at 24h.

### Summary

| gate | fired? | first receipt | change |
|---|---|---|---|
| `sweep_ticks = 4` | 21x (grid) / 31x (native) | 08-15 20:45Z, T-7.3h, AZ-P319, 6 ticks | **threshold: no change. Code: add empty-book guard (decisive).** |
| `storm` 4-per-1h | 1x (grid) / 2x (native) | 08-16 02:30Z, T-1.50h, n=6 | no change |
| `curfew` 24h | continuous | 08-15 03:00Z | no change |

---

## 4. RENEWAL WATCH — baseline snapshot

**Recorded:** at **04:21Z**, 0 new ballot windows existed.

**Verified independently at my own runtime, 2026-08-16T04:30:01Z**, pulling
`GET /trade-api/v2/incentive_programs?limit=1000` (10 pages, 10,000 programs) plus the markets and
events feeds. Raw: `…/scratchpad/ip_now.jsonl`, `bm_now.json`, `bm_ev.json`.

### `KXSTATEBALLOTMEASURE` — dark

- **110 programs total, all in a single cohort:** start `2026-08-11T14:02Z`, end `2026-08-16T03:59Z`,
  `incentive_description = "new_event"`, `target_size_fp = 1000`, `discount_factor_bps = 5000`.
- Reward tiers: $285.00 ×51, $250.00 ×12, $125.00 ×16, $110.00 ×9, $145.00 ×7, $200.00 ×5, $100.00 ×10.
- **Programs with `end_date` ≥ 2026-08-17: 0.**
- **Programs with `end_date` > now: 0.**
- `paid_out`: **false for all 110** as of 04:30Z — settlement of the LIP escrow had not posted 31
  minutes after the close.
- Markets feed still returns 111 tickers (110 `active`, 1 `inactive`) and 36 open events, all with
  `close_time = 2027-11-02T23:59Z`. **The markets are alive; the subsidy is not.** Any renewal will
  appear as a *new incentive program on the existing tickers*, not as new tickers — the watcher must
  poll the programs feed, not the markets feed.

### Family subsidies still active at 04:30:01Z — 2,331 programs

| family | n | desc | start | end | reward |
|---|---:|---|---|---|---:|
| KXFEDFUNDSYEAR | 210 | — | 08-11T04:05 | 08-18T03:59 | $25.00 |
| KXH200MS | 143 | series_lip | 08-15T04:16 | 08-29T04:16 | $15.00 |
| KXNOMGDPGROWTH | 143 | — | 08-09T21:16 | 08-17T03:59 | $25.00 |
| KXUSCPIYEAR | 130 | — | 08-11T04:05 | 08-18T03:59 | $25.00 |
| KXB200MS | 123 | series_lip | 08-15T04:16 | 08-29T04:16 | $15.00 |
| KXH100MS | 121 | series_lip | 08-15T04:16 | 08-29T04:16 | $15.00 |
| KXROLEATEVENTCOACHELLA | 114 | — | 08-11T01:41 | 08-21T03:59 | $50.00 |
| KXRTX5090MS | 109 | series_lip | 08-15T04:16 | 08-29T04:16 | $15.00 |
| **KXYTVIEWSHIGH** | **51** | **series_lip** | **08-16T04:16** | **08-30T04:16** | **$100.00** |
| KXTEMPMIAH | 20 | series_lip | 08-16T04:00 | 08-16T05:00 | $80.00 |

### The abrupt-appearance pattern, timestamped

**New subsidies spawn on a daily 04:16Z tick.** 08-15T04:16Z spawned the entire GPU wave
(`KXH200MS`/`KXB200MS`/`KXH100MS`/`KXRTX5090MS`/`KXA100MS`/`*MAX`/`*WS`, ~600 programs at $15.00 each,
14-day). **08-16T04:16Z — 17 minutes after the ballot window closed and 14 minutes before this pull —
spawned exactly one new family: `KXYTVIEWSHIGH`, 51 programs, $100.00/period, target 1000, df 5000bps,
running to 08-30T04:16Z.** Also new since midnight: `KXH100MON`/`KXB200MON`/`KXRTX5090MON` (59
programs, 08-16T00:01Z → 08-30, $15.00) and `KXRAIN` re-armed at 08-16T03:31Z → 08-17T05:00Z at $100.00.

**`new_event`-pattern subsidies active anywhere right now: 0.** The two that ran yesterday
(`KXDIESELD` 21 programs, `KXTRUMPTIME` 5 programs) both expired at `2026-08-16T03:59Z` — the same
instant as the ballot family. **All three `new_event` cohorts share one expiry timestamp**, which
means the `new_event` channel is not a rolling stream but a synchronized batch that empties and
refills. It is currently empty.

### Watch instruction

Poll `incentive_programs` at **04:16Z ± 5 min daily** filtered to
`incentive_description == "new_event"` and to `market_ticker` prefixes not seen the prior day. The
ballot family's own renewal, if it comes, will land as a new `new_event` cohort on the existing 110
tickers with a fresh `start_date`/`end_date` pair. As of **2026-08-16T04:30:01Z it has not.**

---

## Artifacts

- `…/scratchpad/c2b.py` — preregistered C2 runner (unmodified; §1)
- `…/scratchpad/close_q23.py` — close-behavior + gate replay (§2, §3)
- `…/scratchpad/vps_capture.jsonl` — local copy of instrument 2
- `…/scratchpad/ip_now.jsonl`, `bm_now.json`, `bm_ev.json` — 04:30:01Z renewal pull (§4)

Scratchpad root:
`/private/tmp/claude-501/-Users-ryanwhitehead-Documents-senate-domains-kalshi/162f05b7-b9bf-49dd-b319-057450acadb5/scratchpad`
