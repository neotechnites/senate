# Gate-Funnel Replay — autoseat v2.8 full stack
2026-08-16 · replay span 2026-08-13T00:15Z → 2026-08-16T01:45Z · 295 cycles @900s · 74 hours · 110 KXSTATEBALLOTMEASURE markets

**Answer to Ryan's question: no. The stack would have placed 0 of our 10 actual seats, and it never once
had 5 seatable candidates at the same time — the most it ever had was 2.**

---

## Method

L2 books rebuilt tick-by-tick from `competition/deltas-2026081{3,4,5},deltas-20260816-0{0,1}.jsonl.gz`
(597,182 ballot-family lines: `orderbook_snapshot` seeds + signed `delta_fp` applied per price level).
Gate arithmetic is a line-for-line port of `autoseat.py` v2.8 `discover()` / `_note_book()` /
`rival_touch_depth()` and `rung1.model_seat()` → `lip_score.snapshot_share()` (target 1000, df 0.5,
ours = 250ct at $50/0.20 etc.). Programs from `temp_census_cache/incentive_programs_all.json`
(110 rows, all start 08-11T14:02Z / end 08-16T04:00Z, `period_reward` $100–$285, target 1000, df 5000bps).
Books are sampled at the 900s cycle grid, exactly as the live loop pulls them, so the sweep ledger
and storm breaker see the same observation cadence they see in production.

Config replayed: Rung B (`max_seats=5`, `per_market_usd=$50`, `max_new_per_cycle=1`), everything
else from `autoseat.config.vps.json`. Effective window floor = `max(90000, 86400 + 2*900)` = **90,000s**.

---

## (1) THE FUNNEL — market-cycles, cumulative, over 295 cycles × 110 markets

| # | stage | market-cycles | % of universe | retained from prior |
|---|---|---:|---:|---:|
| 0 | universe (family allowlist, g3 blocklist, speedgate) | 32,450 | 100.00% | — |
| 1 | **alive** — window ≥ 90,000s to close, not paid_out | 22,330 | 68.81% | 68.8% |
| 2 | **band** — own-side join price in 15–85c, pair-sum ≤ 99c, ≥10ct | 17,810 | 54.88% | 79.8% |
| 3 | **credit floors** — modeled ≥ $1.50 and ×K(0.515) ≥ $0.75 | 15,367 | 47.36% | 86.3% |
| 4 | **depth** — min touch qty ≥ 250 panel units (1c/99c excluded) | 11,915 | 36.72% | 77.5% |
| 5 | **share** — R1.model_seat share at entry ≥ 0.331 | **64** | **0.20%** | **0.54%** |
| 6 | **post-sweep re-entry ban** — no ≥4-tick collapse in trailing 2h | 44 | 0.14% | 68.8% |
| 7 | **family storm breaker** — <4 family sweeps in trailing 1h | **32** | **0.10%** | 72.7% |

Per hour: mean 110 markets alive-eligible, **75.8 alive**, 60.6 in band, 53.1 past credit,
42.4 past depth, **0.39 past share**, 0.28 past sweep-ban, **0.20 seatable**.

### The funnel's whole loss is one gate — and it is a gate-pair collision

Marginal pass rates over the 15,367 band+credit market-cycles (each gate applied alone):

| gate applied alone | passes | rate |
|---|---:|---:|
| depth ≥ 250 | 11,915 | **77.54%** |
| share ≥ 0.331 | 1,426 | **9.28%** |
| both together | 64 | **0.416%** |
| *(if independent, expected)* | *1,105* | *7.19%* |

**17.3x anti-correlated.** They are the same variable with opposite signs: LIP share is
`our_size / (our_size + df-weighted rival size)`, so the depth floor selects precisely the books
where share cannot clear. Proof from the tape:

- The 1,362 market-cycles that pass **share** but fail **depth** have median rival touch depth **20**, p90 **132** — share lives in the sub-250 region C2 exists to exclude.
- Among the 11,915 **depth**-passing market-cycles, best-side share is median **0.0706**, p90 **0.1656**, p99 **0.3011**, **max 0.4886** — the 0.331 floor sits above the 99th percentile of the population the depth gate admits.

Storm breaker cost: active in **52/295 cycles (17.6%)**; it destroyed 12 otherwise-seatable
candidates across 9 cycles. Post-sweep ban cost: 20 candidates.

---

## (2) WOULD THE 5 RUNG-B SLOTS FILL — no, never

| hourly seatable count | hours | % of 74 |
|---|---:|---:|
| **≥ 5 candidates** | **0** | **0.0%** |
| ≥ 1 candidate | 13 | 17.6% |
| = 0 candidates | 61 | 82.4% |

Restricting to the 51 hours where any window is still alive: ≥5 → **0 (0.0%)**, ≥1 → 13 (25.5%),
0 → 38 (74.5%). At cycle granularity: 267/295 cycles have **zero** candidates, 24 have one, 4 have
two. **Max concurrent seatable candidates over the entire replay = 2.**

Only **5 distinct markets** were ever seatable across 74 hours:
GA-A2 (18 cycles), NM-BQ2 (6), SD-AK (6), NC-A2 (1), AR-A578 (1).
All of them on 08-13 and 08-14. **08-15: 0. 08-16: 0.** Two independent reasons for the shutout
after 08-15T03:00Z: the 90,000s window floor mathematically excludes every ballot program from that
instant forward (all 110 close 08-16T04:00Z), and no book cleared depth+share before it anyway.

Running the real occupancy loop (`max_new_per_cycle=1`, storm eject, 24h curfew eject):
**7 placements, peak 3 concurrent seats, 25.5 seat-hours** against 5 slots × 73.75h = 368.75
available slot-hours → **6.9% slot utilization**. The other 93.1% of Rung B's capital sits idle.

---

## (3) OUR ACTUAL 10 SEATS — every one refused

Gates evaluated on the reconstructed book at the cycle boundary immediately **preceding** each
seat's real placement (so our own order is not yet in the ladder). `†` = later filled.

| # | seat | entry (UTC) | window | band | depth | share | credit | sweep | storm | **first refusing gate** |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | AL-A4 no @0.20 | 08-13 20:08 | ok 186,671s | ok | **100** ✗ | **0.3146** ✗ | ok $18.54 | ok | **14/1h** ✗ | **storm** (also depth, share) |
| 2 | NC-A2 no @0.22 | 08-13 20:08 | ok 186,670s | ok | 788 ok | **0.2025** ✗ | ok $13.61 | ok | **14/1h** ✗ | **storm** (also share) |
| 3 | AL-A4 no @0.22 | 08-14 06:52 | ok 148,051s | ok | 823 ok | **0.1222** ✗ | ok $5.71 | ok | **5/1h** ✗ | **storm** (also share) |
| 4 | AL-A3 yes @0.51 | 08-14 10:54 | ok 133,555s | ok | **127** ✗ | 0.3503 ok | ok $14.77 | ok | ok | **depth** |
| 5 | GA-A2 no @0.20 † | 08-14 10:54 | ok 133,554s | ok | 550 ok | **0.2665** ✗ | ok $12.81 | ok | ok | **share** |
| 6 | RI-Q4 no @0.18 | 08-14 11:14 | ok 132,310s | ok | 518 ok | **0.2139** ✗ | ok $7.15 | ok | ok | **share** |
| 7 | ID-HJR4 no @0.24 | 08-14 20:03 | ok 100,570s | ok | 470 ok | **0.1761** ✗ | ok $6.38 | **1,800s** ✗ | ok | **share** (also post-sweep) |
| 8 | IA-A1 no @0.23 † | 08-15 00:46 | **83,597s** ✗ | ok | **4** ✗ | 0.3385 ok | ok $10.18 | ok | ok | **window/curfew** (also depth) |
| 9 | AR-A578 no @0.18 † | 08-15 01:07 | **82,352s** ✗ | ok | **23** ✗ | 0.4198 ok | ok $10.92 | ok | ok | **window/curfew** (also depth) |
| 10 | KY-A1 no @0.32 † | 08-15 02:00 | **79,142s** ✗ | ok | **20** ✗ | 0.4386 ok | ok $12.49 | ok | ok | **window/curfew** (also depth) |

**Seats the stack would have placed: 0 of 10.**

**The 4 that filled — all 4 refused, each by ≥1 gate, with no overlap in the refusing gate:**
- **GA-A2** (the earliest and the only one outside the terminal zone) is stopped by the **share floor alone** — it passed depth (550), credit, window, sweep and storm. Share 0.2665 vs 0.331.
- **IA-A1 / AR-A578 / KY-A1** (the 08-15 terminal-window incident, $199.69 escrow) are each stopped **twice, independently**: by the **90,000s window floor** (they sat 79k–84k from close, inside the curfew+2-cycle exclusion) and by the **depth floor** (rival touch 4, 23, 20 — all in the sub-250 gap-risk region, exactly where C2's 7/7 ≥5c dislocations lived). Their share was 0.34–0.44, i.e. the share floor would have *waved them through*; depth and curfew are what catch them.

Note the inversion: **share and depth refuse disjoint halves of our own book.** Seats 1,4,8,9,10 fail
depth; seats 1,2,3,5,6,7 fail share. Not one seat passes both.

Credit floors refused nothing (10/10 pass, $5.71–$18.54 modeled vs a $1.50 floor) — the credit
floors are inert at these pool sizes and carry no selectivity.

---

## (4) OTHER HISTORY — anywhere else the stack would ever have placed

**By construction, nowhere.** `data/research/fills_all_20260815.json` holds 1,540 fills from
2026-06-17 to 2026-08-15 across **88 families**; 1,520 are non-ballot and every one is refused at
gate 0 by the `families: ["KXSTATEBALLOTMEASURE"]` allowlist.

Counterfactual with the **family gate as the only relaxation** (all other gates intact):

| refusal that still stands | non-ballot fills covered |
|---|---:|
| g3 info-flow blocklist (KXAAAGASD, KXRAIN, KXDIESELD, KXUST\*AD, KXEOWEEK…) | 560 |
| speedgate FAST | 136 |
| **survive both — family gate is the ONLY thing stopping them** | **835 (54.6%)** |

For those 835, the stack's *own* gates would not reliably refuse them, and that is the finding:
per `family-census-20260815.md` §3.4, rival at-touch depth is **285 (FEDFUNDS), 218 (CPI), 932
(GDP), 250 (H200MS), 1,888 (Coachella), 812 (YTVIEWSW)** — 5 of 6 **pass** the 250 depth floor,
and their $/ct at ceiling ($0.0120–$0.0552 on ≥168h windows) clears the $1.50 modeled-credit floor
on a 250-contract seat. Yet **five of seven are net-negative rival-adjusted**
(FEDFUNDS −$0.0008, CPI −$0.0012, GDP −$0.0047, Coachella −$0.0372, YTVIEWSW −$0.0521/ct) and the
best survivor, KXH200MS at +$0.0098/ct, returns **1.5% of the ballot family per posted contract-hour**
(census §3.2 table; ballot +1.97e−03 $/ct-hr vs H200MS +2.9e−05).

**So: the gate stack contains no rate test and no adverse-selection test. Relax the family gate and
the stack seats into families that lose money at −$0.0008 to −$0.0521/ct. The allowlist is
load-bearing in a way the eight compiled gates are not, and it must not be relaxed as a fix for
the starvation below.**

---

## (5) THE ONE SENTENCE

**Yes — the stack starves placement: over 74 hours it produced seatable candidates in only 13 hours
(17.6%), never more than 2 at once against 5 slots (0 hours with ≥5, 6.9% slot utilization), and it
would have placed 0 of our 10 actual seats — because the share floor (0.331) and the rival-depth
floor (250) are 17.3x anti-correlated, jointly passing 0.416% of band-and-credit-clearing
market-cycles when independence predicts 7.19%.**

The corollary Ryan should weigh: this is not pure loss. The same collision refuses **all 4 fills**,
including the 08-15 terminal-window incident, which the window floor and the depth floor each catch
on their own. The question is not whether the gates work — they do — but whether a strategy that
seats 7 times in 3 days at a peak of 3 concurrent seats is worth running at Rung B scale. Either
the share floor or the depth floor can be kept; keeping both leaves ~0.4% of the tape.

---

### Artifacts
- replay engine: `/private/tmp/claude-501/-Users-ryanwhitehead-Documents-senate-domains-kalshi/162f05b7-b9bf-49dd-b319-057450acadb5/scratchpad/replay.py` (+ `replay2.py` marginals, `replay3.py` seat probe)
- per-cycle funnel: VPS `/tmp/funnel.jsonl` (295 rows), local copy in the same scratchpad
- cited: `family-census-20260815.md`, `fill-forensics-20260815.md`, `seats-mechanism-20260816.md`, `ideation-fresh-20260816.md` (C2)
