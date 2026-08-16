# Family Vetting Census — 7 unvetted LIP families vs the ballot allowlist
Date: 2026-08-15 · **STRICTLY READ-ONLY, keyless public endpoints, ~1 req/s, no orders, no auth**

Method template: `temp-hourly-census-20260815.md` (preregistered sampling, verified side
semantics, scale-free kill arithmetic). Same arithmetic applied here.

**Result: 0 of 7 families are ALLOWLIST-CANDIDATE. 5 DEAD, 2 CONDITIONAL-but-not-worth-it.**
The single number that decides the census is in §1.

---

## 0. Method and provenance

| Item | Value |
|---|---|
| Pool economics | `GET /trade-api/v2/incentive_programs`, 20,000 rows captured → `temp_census_cache/incentive_programs_all.json`. **All 7 families present; no VPS/auth pull was needed.** |
| Market populations | `GET /markets?series_ticker=…&status={settled,closed,open}`, paginated |
| Trade tapes | `GET /markets/trades?ticker=…`, paginated |
| Books | `GET /markets/{ticker}/orderbook?depth=100` |
| Cache (resumable) | `data/research/family_census_cache/` — 610 trade tapes, 180 book snapshots |
| Scripts | `family_census_pull.py` · `family_census_analyze.py` · `family_calendar.py` · `family_summary.py` · `coach_pull.py` |

**Sampling rule** written into `family_census_pull.py`'s header *before* the first trade pull:
full enumeration → seeded shuffle `random.Random(20260815)` → unbiased prefix of n=80 (or the
full population where it is smaller). One amendment, made **after enumeration but before any
trade data was seen**, is recorded in the script docstring: the three YEAR families have **zero
resolved markets** (every market closes 2028–2037), so a settlement-based hazard arm is
impossible for them and the hazard arm uses the trade tape instead. Markets with zero trades
stay in the denominator.

### Side semantics — verified per family, not assumed
Across all 610 tapes only two `(taker_side, taker_outcome_side, taker_book_side)` combos exist —
`("yes","yes","bid")` and `("no","no","ask")` — in **every** family (KXFEDFUNDSYEAR 530/533,
KXUSCPIYEAR 522/630, KXNOMGDPGROWTH 86/85, KXH200MS 2448/1654, KXB200MS 1155/713,
KXYTVIEWSW 6110/5172). So the TEMP fill rule carries unchanged:
- resting **YES** bid at `q` is hit only by a print with `yes_price ≤ q` **and** `taker_side=="no"`;
- resting **NO** bid at `q` only by `yes_price ≥ 1-q` **and** `taker_side=="yes"`.

All fill rates assume **perfect queue priority** → every `P(fill)` and every net below is an
**upper bound** on what a real seat achieves.

### Phantom-level rule
1c and 99c levels are excluded from **every** depth, touch, spread and rival number below
(known instrument defect). A phantom level was present in **180/180** book snapshots — it is
universal, not incidental, and un-excluded depth is meaningless.

---

## 1. The census in one table — THE KILL

`NET $/ct-hr` normalises for window length, which differs 110h–336h and makes raw `$/window`
non-comparable. `NETrival` applies the pro-rata haircut for rival size already resting at the touch.

| family | win_h | LIP ceil $/ct | adverse $/ct | NET $/ct | eff ceil (rival) | **NET rival-adj** | NET $/ct-hr | **vs ballot** |
|---|---|---|---|---|---|---|---|---|
| KXFEDFUNDSYEAR | 168 | 0.0250 | +0.0203 | +0.0047 | 0.0195 | **−0.0008** | −4.9e−06 | −0.002x |
| KXUSCPIYEAR | 168 | 0.0250 | +0.0217 | +0.0033 | 0.0205 | **−0.0012** | −7.2e−06 | −0.004x |
| KXNOMGDPGROWTH | 175 | 0.0250 | +0.0164 | +0.0086 | 0.0129 | **−0.0047** | −2.7e−05 | −0.014x |
| KXH200MS | 336 | 0.0150 | +0.0022 | +0.0128 | 0.0120 | **+0.0098** | +2.9e−05 | 0.015x |
| KXB200MS | 336 | 0.0150 | +0.0048 | +0.0102 | 0.0113 | **+0.0065** | +2.0e−05 | 0.010x |
| KXROLEATEVENTCOACHELLA | 242 | 0.0500 | +0.0544 | −0.0044 | 0.0172 | **−0.0372** | −1.5e−04 | −0.078x |
| KXYTVIEWSW | 166 | 0.1000 | +0.1073 | −0.0073 | 0.0552 | **−0.0521** | −3.1e−04 | −0.159x |
| **KXSTATEBALLOTMEASURE** (allowlisted) | 110 | **0.2850** | +0.0683 | **+0.2167** | — | — | **+1.97e−03** | **1.000x** |

**The census kill, scale-free and capital-free:** the best new family (KXH200MS) returns
**1.5% of the ballot family per posted-contract-hour**. Five of seven are **negative** once
rival depth at the touch is accounted for. There is no configuration, cap or gate that closes a
**67x–400x** gap in rate — the gap is in the numerator (`period_reward`), which we do not control.

**This is a rate kill, not a sign kill, and the distinction matters.** Four of the seven
(FEDFUNDS +0.0047, CPI +0.0033, GDP +0.0086, GPU +0.0128/+0.0102) are *positive* at the
assumption-free ceiling. FEDFUNDS on the full 210-market census with 174 fills has a 95% CI of
[+0.0002, +0.0091] that excludes zero — it is a genuinely profitable seat. It is still rejected,
because it earns **0.2% of what the same contract earns in the ballot family**. Nothing here is
rejected for being unprofitable; they are rejected for being a bad place to put the next dollar.

**The comparison needs no capital assumption.** Mean in-band entry price is within a 4.5c band
across every family measured — FEDFUNDS 0.3349, CPI 0.3415, GDP 0.3125, H200MS 0.3393,
B200MS 0.3394, Coachella 0.2919, YTVIEWSW 0.3015, **ballot 0.3361** — so a posted contract costs
essentially the same collateral everywhere. `$/posted contract` is therefore already a
capital-normalised return, and `$/posted-contract-hour` normalises the remaining window-length
difference. No assumption about cap size, entry price or inventory enters the ranking.

Note what this table does **not** say: the ballot family is not *safer*. Its adverse selection
($0.0683/ct) is the third-worst in the census and it is the family with the known terminal-
evacuation fill risk. It wins purely because `period_reward` is 11x–19x larger. **The allowlist
criterion that falls out of this census is the size of the subsidy, not the tameness of the tape.**

The ballot baseline row is measured by the **identical** seat reconstruction on
`trades_all_ballot_20260815.json` (110 tickers, 1,832 prints, window 08-11..08-16):
seats 75, fills 49, P(fill)=0.653, drift −0.1045 [−0.1521, −0.0569] → adverse $0.0683 against a
$0.2850 ceiling.

---

## 2. Pool economics — receipted, all 7 families (§a)

`period_reward` is in units of 1e-4 USD (established in the TEMP census by two independent
sources agreeing at 1e-4). Ceiling at the touch = `period_reward / target_size_fp`, decay
exponent 0, and assumes we capture our **full** pro-rata share — generous.

| family | live window | `period_reward` | `target_size_fp` | **$/posted contract** | live pool |
|---|---|---|---|---|---|
| KXFEDFUNDSYEAR | 08-11→08-18 (168h) | 250,000 | 1000.00 | **$0.0250** | $5,250 / 210 mkts |
| KXUSCPIYEAR | 08-11→08-18 (168h) | 250,000 | 1000.00 | **$0.0250** | $3,250 / 130 |
| KXNOMGDPGROWTH | 08-09→08-17 (175h) | 250,000 | 1000.00 | **$0.0250** | $3,575 / 143 |
| GPU class (all 10 tickers) | 08-15→08-29 (336h) | 150,000 | 1000.00 | **$0.0150** | **$26,160 / 1,744 mkt-windows** |
| KXROLEATEVENTCOACHELLA | 08-11→08-21 (242h) | 500,000 | 1000.00 | **$0.0500** | $5,700 / 114 |
| KXYTVIEWSW | 08-11→08-18 (166h) | 1,000,000 | 1000.00 | **$0.1000** | $7,600 / 76 |
| KXSTATEBALLOTMEASURE | 08-11→08-16 (110h) | 2,850,000 | 1000.00 | **$0.2850** | — |

Two receipts worth keeping:

1. **The reward was cut 58% mid-census.** FEDFUNDS and CPI paid `600,000` ($60) for the
   07-29→08-02 launch window and `250,000` ($25) for both windows since. The brief's "$5,250"
   is the current $25 tier. **A family's pool is not a constant** — any allowlist decision must
   re-read `incentive_programs`, not a cached figure.
2. **The GPU class is one instrument for pool purposes.** All 10 tickers (H200/H100/B200/
   RTX5090/A100 × MS/WS) carry `period_reward=150000, target_size_fp=1000, discount_factor_bps=5000`
   with no exceptions across 2,025 rows. `$0.0150` generalises exactly; the depth work below on
   the two largest (H200MS 286 rows, B200MS 246) transfers on pool economics with no assumption.

---

## 3. Fill hazard and speed character (§b, §c)

### 3.1 The three macro YEAR families — inert, and the calendar hypothesis FAILS

These are not weekly markets. **Every market closes 2028–2037** (FEDFUNDS: 21 strikes × 10 Januaries;
CPI: 13 × 10 Februaries; GDP: 13 × 11). The weekly LIP window sits on a decade-dated instrument.

| | FEDFUNDS | CPI | GDP |
|---|---|---|---|
**All three were expanded to the FULL population** (no sampling at all — 210/130/143 markets,
every LIP-funded market in the family), because the priority-1 verdict was inside the noise at n=80.

| | FEDFUNDS | CPI | GDP |
|---|---|---|---|
| markets (full census) | **210** | **130** | **143** |
| zero-trade markets | 0/210 | 0/130 | **78/143 (0.545)** |
| median prints/day | 1.92 | 2.47 | 18.3 (over a 0.18d median span) |
| P(tape ever in 15–85c) | 0.9905 | 0.9615 | 0.4476 |
| in-band seats / mkt-windows | 583/630 | 317/390 | 64/65 |
| **P(fill \| seated)** | 0.2985 [0.2627,0.3368] | 0.2618 [0.2165,0.3129] | 0.3438 [0.2392,0.4660] |
| post-fill drift, our side | −0.0681 [−0.0830,−0.0532] | −0.0829 [−0.1154,−0.0504] | −0.0477 [−0.0911,−0.0044] |
| fills (evidence base) | **174** | **83** | 22 |
| **NET $/ct at ceiling** | **+0.0047 [+0.0002,+0.0091]** | +0.0033 [−0.0052,+0.0118] | +0.0086 [−0.0063,+0.0235] |

**Per-window, the hazard is entirely a launch-week phenomenon:**

| window | reward | FEDFUNDS P(fill) / drift | CPI P(fill) / drift |
|---|---|---|---|
| 07-29→08-02 (launch) | $60 | **0.431 / −0.1094** | **0.457 / −0.1051** |
| 08-03→08-11 | $25 | 0.240 / −0.0391 | 0.110 / −0.0273 |
| 08-11→08-18 (live, truncated) | $25 | 0.217 / −0.0129 | 0.188 / −0.0532 |

**(c) Speed character — the gateable-calendar premise does not survive contact with the tape.**
63.3% of FEDFUNDS prints and 51.2% of CPI prints land on a "scheduled-event day or day+1"
against a 26.7%/22.2% uniform baseline — but **that is confounded**: the markets were listed
`2026-07-29T18:00Z`, the same day as the July FOMC decision. Launch and FOMC are not separable
in this tape.

The one **clean, unconfounded** scheduled print in the sample — the BLS CPI release on
**2026-08-12** — moved nothing:

```
FEDFUNDS prints/day: 08-09:27  08-10:46  08-11:72  08-12:24*  08-13:10*  08-14:17  08-15:5
CPI      prints/day: 08-09:87  08-10:66  08-11:32  08-12:23*  08-13:13*  08-14:12  08-15:2
                                                    ^ CPI release day — a LOCAL MINIMUM
```

CPI release day is a local *minimum* in both families. **These decade-dated markets are inert
with respect to the monthly data calendar.** The proposed "eject 48h before FOMC" gate is
therefore **unmeasured, not validated**: there has been no FOMC since these markets listed
(next: 2026-09-16). The only observed high-hazard regime is *listing week*, which a calendar
gate would not catch and which recurs whenever the venue lists a new strike ladder.

### 3.2 GPU class — the only families with a positive sign

H200MS and B200MS agree closely, which is what licenses generalising to the class:

| | KXH200MS | KXB200MS |
|---|---|---|
| markets / sampled | 165 / 89 | 141 / 80 |
| zero-trade | 6/89 (0.078) | 6/80 (0.075) |
| P(tape in 15–85c) | 0.8831 | 0.8625 |
| seats / mkt-windows | 100/116 (0.862) | 105/124 (0.847) |
| **P(fill \| seated)** | 0.1810 [0.1251,0.2778] | 0.0952 [0.0526,0.1665] |
| drift, our side | **−0.0121** [−0.0421,+0.0179] | −0.0500 [−0.1018,+0.0018] |
| **NET $/ct** | **+0.0128 [+0.0074,+0.0182]** | **+0.0102 [+0.0053,+0.0152]** |

Both CIs exclude zero and are positive. The reason is simply that these markets barely move:
a 1.2c drift is the smallest adverse selection in the census.

**(c) Speed character:** activity is concentrated in the **front settlement month** and collapses
the moment it expires — H200MS printed 375/213/251/256 on 07-27..07-30 (26JUL expiring 07-31),
then 8/18/4/1 on 08-01..08-04. The far months (27JUL, 27AUG, 27SEP) are dead. This *is* a real,
gateable structure — but the gate would confine the seat to dead far-month markets, which is
exactly where rival makers already sit (§4) and where the LIP is most oversubscribed.

### 3.3 The two mention/role families — highest ceilings, worst outcomes

| | KXROLEATEVENTCOACHELLA | KXYTVIEWSW |
|---|---|---|
| markets / sampled | 115 / 115 (full census) | 195 / 80 |
| resolved population | 0 | **119** (real settlement arm) |
| **live markets in 15–85c band** | **13/115 (0.113)** | 26/76 |
| seats / mkt-windows | 16/103 (0.155) | 55/76 (0.724) |
| **P(fill \| seated)** | **0.8750** [0.6398,0.9650] | **0.9091** [0.8042,0.9605] |
| drift, our side | −0.0621 [−0.1097,−0.0146] | −0.1110 [−0.2210,−0.0010] |
| settled loss/ct | n/a (nothing resolves until 2027-12) | **+0.1180** [+0.0058,+0.2302] |
| P(our side settles ITM) | n/a | **0.1800** (9/50) |

KXYTVIEWSW is the only new family with a genuine settlement arm, and it reproduces the TEMP
pathology exactly: you are filled **91%** of the time and the side you are left holding settles
in your favour **18%** of the time after entering at ~30c. Adverse selection **$0.1073** against
a **$0.1000** ceiling — dead at the ceiling, before any rival haircut.

Coachella is dead for a different and more basic reason: **89% of its live markets are not
quotable in-band at all** (mid outside 15–85c), so the family cannot supply seats, and the few
it does supply fill 88% of the time.

---

## 4. Book structure (§d) — rival saturation is the second kill

All depth numbers exclude 1c/99c.

| family | median spread | depth ≤3 ticks (YES/NO) | **rival AT touch** | our pro-rata share posting 1000 | eff $/ct |
|---|---|---|---|---|---|
| KXFEDFUNDSYEAR | 4.0c | 536 / 796 | 285 | 0.778 | $0.0195 |
| KXUSCPIYEAR | 13.5c | 1325 / 1025 | 218 | 0.821 | $0.0205 |
| KXNOMGDPGROWTH | 6.0c | 800 / 800 | **932** | **0.518** | $0.0129 |
| KXH200MS | 4.0c | 378 / 360 | 250 | 0.800 | $0.0120 |
| KXROLEATEVENTCOACHELLA | 1.0c | 3838 / 662 | **1,888** | **0.346** | $0.0173 |
| KXYTVIEWSW | 32.0c | 1442 / 3524 | 812 | 0.552 | $0.0552 |

**The generalisable finding: when rival at-touch depth ≥ `target_size_fp`, the marginal
$/contract collapses and the family is unenterable.** GDP (932 vs 1,000) and Coachella
(1,888 vs 1,000) are both already saturated by rivals alone — the target size is met
without us, so our marginal contribution earns a fraction of a pool that is already being paid
out. This flips GDP from +$0.0086 to **−$0.0047** and Coachella from −$0.0044 to **−$0.0371**.

Book quality is also poor where the ceiling is highest: KXYTVIEWSW has a **32c** median spread
and **13 of 25** live books are one-sided after removing phantom levels — there is no two-sided
touch to seat against in half the family.

> **Flagged, not sourced:** the LIP attribution rule (whether payout is strictly pro-rata on
> qualifying size, and what qualifies when the book is one-sided) is **not derivable from any
> public endpoint**. The pro-rata haircut above is the natural reading and is applied uniformly,
> but it is the one modelled leg in this census. It only ever makes the verdicts *worse*; the
> ceiling column is the assumption-free bound, and on that column alone 2 of 7 (Coachella,
> YTVIEWSW) are already dead and the other 5 still lose the rate comparison by 67x-400x.

---

## 5. Our own position history in these families

Checked `fills_all_20260815.json` (1,540 fills) per the brief's flag.

- **KXYTVIEWSW: the "-$0.44 realized loss" flag is a misread.** Our actual book is
  **+$120.96 realized** across 9 settled markets / 27 fills (17 maker, 10 taker), computed
  yes-equivalent (`cash = -q x yes_price`, plus `q x 1{result==yes}`). The figure −0.4415 in our
  records is **exactly the `fee_cost` line on the single fill
  `KXYTVIEWSW-JUS26AUG09-17.0M` 2026-08-06T05:09:33** — a fee, booked as a realized P&L.
  Per-market: +3.99, +53.20, +10.04, +59.04, −19.22, −22.77, −3.99, −12.17, +52.86.
- **KXROLEATEVENTCOACHELLA: zero fills, ever.** No prior loss in this family.
- The nearest analogue that *did* burn us is **KXROLEINPRODUCTIONDOOMSDAY: −$61.02** over 3
  markets / 13 fills — and its signature is the same terminal-evacuation pattern as the ballot
  incident: maker fills at 0.31/0.72/0.64, then all three flattened as **taker** inside two
  timestamps (08-05T16:23:11, 08-06T16:05:06) paying $3.40 in fees. **That is the family-class
  warning the brief was reaching for, and it survives** — role/mention markets evacuate.
- n=9 markets is far too small to be a family verdict either way; §3.3's n=50 settled fills is
  the evidence that kills KXYTVIEWSW, not our own book.

---

## 6. Verdicts

| # | family | verdict | driving number |
|---|---|---|---|
| 1 | **KXFEDFUNDSYEAR** | **DEAD on rate (−$0.0008/posted ct/window rival-adjusted; 0.002x ballot per ct-hr)** | full census n=210, **174 fills**: net at ceiling +$0.0047 [+0.0002,+0.0091] — real but **0.2% of ballot rate**; rival haircut (285 at touch) erases it |
| 2 | **KXUSCPIYEAR** | **DEAD on rate (−$0.0012; 0.004x ballot)** | full census n=130, 83 fills: +$0.0033 [−0.0052,+0.0118] at ceiling — CI includes zero |
| 3 | **KXNOMGDPGROWTH** | **DEAD (−$0.0047)** | rival at-touch **932 ≈ target_size 1,000**, share 0.518; and **54.5% of the family never trades at all** |
| 4 | **GPU class** (H200/H100/B200/RTX5090/A100 × MS/WS) | **CONDITIONAL — positive but not worth capital** | +$0.0098/ct (H200MS), +$0.0065 (B200MS) = **0.015x ballot per contract-hour** |
| 5 | **KXROLEATEVENTCOACHELLA** | **DEAD (−$0.0371)** | rival at-touch **1,888 = 1.9x target_size**; only **13/115** markets quotable in-band; adverse $0.0544 > ceiling $0.0500 |
| 6 | **KXYTVIEWSW** | **DEAD (−$0.0073 at ceiling, −$0.0521 rival-adjusted)** | P(fill) 0.909 x settled loss $0.118; our side settles ITM **18%** (9/50) |

**No family is promoted to the allowlist. KXSTATEBALLOTMEASURE remains the only one that
clears, by 67x–400x on rate.**

### The one thing worth re-checking rather than re-running
The GPU class has the highest net per posted contract of the seven (+$0.0128 H200MS, CI
[+0.0074,+0.0182]) and holds the largest live pool in the census (**$26,160** across 1,744
market-windows); KXFEDFUNDSYEAR is the other CI-excludes-zero positive. Both are rejected on
*rate*, not *sign*. **Tripwire:** `period_reward` for the GPU class rising above **~1,000,000** (from today's
150,000) would put it within 2x of the ballot family's rate and make it worth a real vetting
pass. Re-read `incentive_programs` — do not re-run this census. The same tripwire logic applies
to FEDFUNDS/CPI, which already demonstrated a 2.4x reward swing ($60 → $25) inside three weeks.

### What is NOT authorized by this document
No paper seat, no capital, no allowlist change in any of the 7 families. The GPU "CONDITIONAL"
is **not** a deferred yes — the named missing measurement (LIP attribution rule under one-sided
books, §4) is not obtainable from public endpoints, and the lane fails on rate regardless of
how that measurement resolves.
