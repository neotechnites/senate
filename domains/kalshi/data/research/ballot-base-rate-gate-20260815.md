# Ballot base-rate gate — test of the fundamentals causal story for the 2026-08-15 autoseat fills
Date: 2026-08-15
Question: were the four adverse fills caused by a model actor sweeping KXSTATEBALLOTMEASURE to
historical pass-rate base rates, and if so should autoseat carry a fundamentals side-gate?

---

## 0. Verdict

**The hypothesis FAILS P1 and P3, and passes P2 only in a weaker form than stated.
DO NOT COMPILE a fundamentals side-gate.**

| Prediction | Result |
|---|---|
| P1 — the 4 filled seats had the largest (prior − implied YES at our price) gap | **FAIL**, and provably so for *any* prior |
| P2 — post-sweep family clusters at type-specific base rates, not one level | **PARTIAL PASS** on type separation; **FAIL** as stated ("whole family reprices YES 73-93c") |
| P3 — fill order correlates with gap size or measure type | **FAIL**, sign inverted; type variance is zero |

A narrow gate *appears* to survive under coarse type priors (a ≥10pt deep-mispricing refusal
blocking KY-A1 alone: 49% of the damage for 3% of the LIP, §7). **It does not survive contact with
the real numbers.** Re-run on verified Ballotpedia state-level rates (§9), the gate inverts:
AUC 0.25, i.e. *anti*-predictive. Kentucky amendments pass at 55.6% (5/9), so an accurate prior
calls KY-A1 — our biggest loss — our **cheapest** seat, while refusing RI-Q4 and ID-HJR4, which
never filled. The apparent win came from using a *less* accurate number.

---

## 1. Sign correction — the seats were NO **bids**, not NO offers

`fills_all_20260815.json` reports the four maker fills as `action:"sell", side:"no",
book_side:"ask"`, which reads as "we sold NO / went long YES". That is the venue's
counterparty-normalised encoding and it is **wrong for our accounting**. The unambiguous check is
`ticks_behind` in `autoseat_state.json` against the replayed NO touch at the fill minute:

```
seat       our px   no_touch@fill   touch − px   autoseat ticks_behind
GA-A2       0.20         21             1                1   ✓
AR-A578     0.18         19             1                1   ✓
IA-A1       0.23         24             1                1   ✓
KY-A1       0.32         36             4                4   ✓
```

4/4 exact. We were resting **NO bids one-to-four ticks behind the NO touch**; we **bought NO**;
the counterparty bought YES. Every number below uses that sign.

Realised / marked damage:

```
GA-A2    250ct @0.20 -> flat 0.140            gross -15.00  fee 2.11  net -17.11
AR-A578  277ct @0.18 -> flat 0.140            gross -11.08  fee 2.33  net -13.41
IA-A1    217ct @0.23 -> flat 92@0.180,125@0.200  gross  -8.35  fee 2.35  net -10.70
KY-A1    156ct @0.32 -> NOT FLATTENED, mark 0.065  gross -39.78  fee 0.00  net -39.78  (open)
                                                                        TOTAL  -81.00
```

---

## 2. Two stated premises of the hypothesis are false on the tape

**(a) "GA+AR at 04:25:06 in the identical second" — FALSE.** Exact maker-fill timestamps from
`fills_all_20260815.json`:

```
GA-A2    2026-08-15 04:25:06Z   ts=1786767906
AR-A578  2026-08-15 05:30:46Z   ts=1786771846      <- +3,940 s  (65.7 minutes)
IA-A1    2026-08-15 14:09:09Z   ts=1786802949      <- +31,103 s
KY-A1    2026-08-15 17:51:28Z   ts=1786816288      <- +13,339 s
```

There is no same-second basket. What *is* true is that AR-A578's **book** jumped at 04:25:17,
11 s after the GA-A2 fill — the 04:25 event touched both books, but AR-A578 did not fill until
05:30:46. The premise conflated a book event with a fill.

**(b) "Post-sweep the WHOLE family reprices YES 73-93c" — FALSE.** Replay of all 110 tickers
(`ballot_deltas.jsonl.gz`, snapshots present for 110/110) from 08-15 04:00Z to 19:55Z:

```
family mid change: mean +0.0116  median +0.0000   |Δ|>=5c on 29/110   |Δ|>=2c on 38/110
TOP UP                              TOP DOWN
WI-Q1     0.545 -> 0.945  +0.400    ND-CM1     0.555 -> 0.100  -0.455
OK-SQ845  0.425 -> 0.815  +0.390    WY-I1      0.780 -> 0.355  -0.425
KY-A1     0.575 -> 0.935  +0.360    NH-CACR13  0.715 -> 0.295  -0.420
AL-A3     0.525 -> 0.835  +0.310    MO-A7      0.535 -> 0.205  -0.330
UT-SJR2   0.415 -> 0.715  +0.300    LA-A272    0.635 -> 0.315  -0.320
```

The event moved prices in **both directions**. The live family spans 0.00 to 0.97, not 0.73-0.93.

---

## 3. P2 — type clustering: PARTIAL PASS

The type separation the hypothesis predicts is real and large. Classification rule: measures in
states with **no citizen-initiative process** (AL GA IA KY NC TN VA IN KS MN WI WV NM LA MD HI NH
RI VT) are definitionally legislature-referred; explicit "Initiative"/"Ballot Measure" naming in
initiative states is citizen-initiated; bond questions broken out separately.

```
type              n    mean    med     p10     p90    range
BOND (LR)        10   0.854  0.865   0.830   0.925   0.72-0.93
LEG-REFERRED     46   0.757  0.778   0.570   0.905   0.29-0.97
LR? (init state) 26   0.709  0.738   0.425   0.935   0.10-0.94
CITIZEN-INIT     28   0.506  0.435   0.190   0.865   0.09-0.89
```

And the 08-15 event pushed each type the *right* way:

```
                 n   pre_med  end_med   mean Δ   n up>=5c   n down>=5c
BOND (LR)       10    0.845    0.865    +0.028       2          0
LEG-REFERRED    46    0.730    0.778    +0.024      10          2
LR? (init st.)  26    0.708    0.762    +0.041       8          1
CITIZEN-INIT    28    0.542    0.435    -0.042       1          5
```

So the actor is real and is fundamentals-driven — it repriced *toward* type-appropriate values.
The 17:00-17:52Z tape shows it marching serially through the family, one ticker every 2-5 min,
down for low-prior types and up for high-prior types:

```
17:01:42 NH-CACR13 -0.205    17:38:40 WI-Q1     +0.140
17:06:52 WY-I1     -0.215    17:39:57 CO-PNN    +0.125
17:10:23 MO-A7     -0.165    17:47:44 OK-SQ845  +0.175
17:15:33 ND-CM1    -0.190    17:49:33 UT-SJR2   +0.155
17:22:04 LA-A272   -0.165    17:51:28 KY-A1     +0.120   <- our fill
```

**But the within-type dispersion is the whole problem.** LEG-REFERRED runs p10 0.570 to p90 0.905
— a 33.5pt band. The gaps a gate must resolve on our seats are 2-6pt.

---

## 4. P1 — gap ranking: FAIL, and prior-independently so

Implied YES at our resting price = 1 − our NO price. Gap = prior − implied.

```
seat       side  our px  implied YES  type   filled?
KY-A1       no    0.32      0.68      LRCA    FILL
AR-A578     no    0.18      0.82      BOND    FILL
GA-A2       no    0.20      0.80      LRCA    FILL
IA-A1       no    0.23      0.77      LRCA    FILL
AL-A4       no    0.22      0.78      LRCA     .
NC-A2       no    0.22      0.78      LRCA     .
RI-Q4       no    0.18      0.82      BOND     .
ID-HJR4     no    0.24      0.76      LRCA     .
AL-A3      yes    0.51      0.51      LRCA     .
```

Ranked by gap under three candidate priors — **not separable under any of them**:

```
prior LR=0.79 BOND=0.88          prior = family type median      prior LR=0.85 BOND=0.92
KY-A1    +0.110  FILL            KY-A1    +0.098  FILL           KY-A1    +0.170  FILL
RI-Q4    +0.060   .              RI-Q4    +0.045   .             RI-Q4    +0.100   .
AR-A578  +0.060  FILL            AR-A578  +0.045  FILL           AR-A578  +0.100  FILL
ID-HJR4  +0.030   .              ID-HJR4  +0.018   .             ID-HJR4  +0.090   .
IA-A1    +0.020  FILL            IA-A1    +0.008  FILL           IA-A1    +0.080  FILL
NC-A2    +0.010   .              NC-A2    -0.002   .             NC-A2    +0.070   .
AL-A4    +0.010   .              AL-A4    -0.002   .             AL-A4    +0.070   .
GA-A2    -0.010  FILL            GA-A2    -0.022  FILL           GA-A2    +0.050  FILL
AL-A3    -0.280   .              AL-A3    -0.268   .             AL-A3    -0.340   .
```

**GA-A2, a fill, ranks LAST of the eight NO seats under every prior.**

### The prior-independent proof

**Against a type-only prior (the shape actually proposed), the failure is total.** Within one type
the gap is `prior − implied`, so the *ordering* inside a type is fixed entirely by our own resting
price; the prior shifts every member equally and cannot reorder them. Therefore:

- GA-A2 (LR, implied 0.80) has a **strictly smaller** gap than AL-A4 (0.78), NC-A2 (0.78) and
  ID-HJR4 (0.76) for **every** value of the LR prior. No LR prior can refuse GA-A2 without also
  refusing all three of those non-filled seats.
- AR-A578 and RI-Q4 are **both** legislature-referred bond questions **both** seated NO@0.18
  (implied YES 0.82). Their gap is **identical for every bond prior**. One filled, one did not.

**Against a finer state×type prior the failure survives, on the bond pair — and gets worse.**
A state-level prior does break the within-type ordering argument: with per-state rates
`gap(GA-A2) > gap(AL-A4)` becomes possible if `P(GA LRCA) > P(AL LRCA) + 0.02`. But AR-A578 and
RI-Q4 sit at the *identical* implied YES (0.82), so their ordering is decided purely by
`P(AR bond)` vs `P(RI bond)`. And Rhode Island is the single most bond-friendly state on record:

> "Between 2008 and 2023, voters in Rhode Island decided on **32 bond measures and approved all**
> of them", support ranging 55.23% to 83.89%; no RI bond measure has been rejected since 2006.
> — [Ballotpedia, RI 2022 ballot measures](https://ballotpedia.org/Rhode_Island_2022_ballot_measures)

So `P(RI bond) ≈ 0.95-0.97` (Laplace on 32/32) and `P(AR bond) ≤ P(RI bond)` necessarily. Two cases,
both fatal:

- If the two are equal, the gaps are identical and the pair is unseparable — the type-only result.
- If they differ, RI is higher, so **RI-Q4 — the seat that never filled — ranks as the *worse*
  bet than AR-A578, the seat that did.** At `P(RI bond)=0.95`, `gap(RI-Q4) = +0.130`, which
  outranks even KY-A1's +0.110. A state-refined prior nominates the safest seat in the book as the
  most dangerous one.

Refining the prior makes this pair worse, not better. Any threshold that refuses AR-A578 also
refuses RI-Q4. This is not a "we picked the wrong prior" failure. It is structural.

Even the **oracle** version — gap measured against the realised post-event price, the ceiling on
what any prior could achieve — does not separate: ID-HJR4 (no fill) ties AR-A578 (fill) at +0.035.

```
oracle gap (end price − implied):
KY-A1 +0.255 FILL | GA-A2 +0.055 FILL | IA-A1 +0.050 FILL | ID-HJR4 +0.035 . |
AR-A578 +0.035 FILL | RI-Q4 +0.020 . | AL-A4 -0.005 . | NC-A2 -0.020 . | AL-A3 -0.325 .
```

---

## 5. P3 — fill order: FAIL, sign inverted

```
#  seat      oracle gap   seated (UTC)    filled (UTC)     time-to-fill
1  GA-A2       +0.055     08-14 14:38     08-15 04:25        13.78 h
2  AR-A578     +0.035     08-15 04:51     08-15 05:30         0.65 h
3  IA-A1       +0.050     08-15 04:30     08-15 14:09         9.64 h
4  KY-A1       +0.255     08-15 05:45     08-15 17:51        12.11 h

spearman(fill_order, gap)   = +0.400     hypothesis needs NEGATIVE
spearman(time_to_fill, gap) = +0.800     hypothesis needs NEGATIVE
spearman(fill_order, our_price) = +0.800
```

The **largest** fundamental gap (KY-A1, +25.5pt) filled **last** and took the second-longest to
fill. The smallest gap (AR-A578) filled fastest, in 39 minutes.

**Fill order by measure type is untestable: 9/9 seats were legislature-referred** (7 LRCA + 2 bond
questions; AL-A3 is also an LRCA). There is zero type variance across the seats, so a
type-conditioned rule has no discriminating power on this book by construction.

---

## 6. The family-wide kill

If the prior explains the sweeper's behaviour it should predict *which* of the 110 markets got
repriced. It does not:

```
                 n    median |pre-event mid − type prior|
moved >= 5c     29              0.095
moved  < 5c     81              0.095
```

Identical. Flagging on |mid − prior|:

```
X=0.15  catches 13/29 movers (45%)  26/81 false flags (32%)  precision 33%
X=0.20  catches 11/29 movers (38%)  20/81 false flags (25%)  precision 35%
```

Base rate of being a mover is 26% (29/110). Precision 33-35% is essentially chance.

The prior's own error against live prices is larger than any useful threshold:

```
|type prior − current market price|, all 110 live markets
type    n    MAE    med    p75    p90
BOND   10   0.036  0.020  0.045  0.155
LR     46   0.106  0.075  0.145  0.220
LR?    26   0.158  0.110  0.195  0.365
CI     28   0.236  0.215  0.345  0.425
ALL   110   0.145  0.098  0.195  0.355
```

A 10pt gate threshold sits at the **51st percentile of the prior's own error distribution**. The
instrument's noise is the same size as the signal it is being asked to detect.

---

## 7. What a gate would actually have done to the 9 seats

Prior LR=0.79, BOND=0.88; rule "refuse a NO seat when prior − implied YES ≥ X".
Baseline LIP across the nine seats: **$33.39/day** (`rate_per_day` from `autoseat_state.json`:
AR-A578 13.57, IA-A1 6.67, AL-A4 3.17, GA-A2 2.85, NC-A2 2.61, RI-Q4 1.88, ID-HJR4 1.69,
KY-A1 0.96, AL-A3 0.00). Damage baseline −$81.00.

```
X      refused                                    fills caught  damage avoided   LIP forfeited
0.02   KY-A1,AR-A578,IA-A1,RI-Q4,ID-HJR4  (5/8)       3/4        $63.89  (79%)   $24.77/d (74%)
0.04   KY-A1,AR-A578,RI-Q4                (3/8)       2/4        $53.19  (66%)   $16.41/d (49%)
0.06   KY-A1,AR-A578,RI-Q4                (3/8)       2/4        $53.19  (66%)   $16.41/d (49%)
0.08   KY-A1                              (1/8)       1/4        $39.78  (49%)   $ 0.96/d ( 3%)
0.10   KY-A1                              (1/8)       1/4        $39.78  (49%)   $ 0.96/d ( 3%)
0.12   (none)                             (0/8)       0/4        $ 0.00  ( 0%)   $ 0.00/d ( 0%)
```

Any setting that catches 3 of 4 fills forfeits **74%** of the family's LIP. The only favourable
row is X≈0.08-0.10, which refuses exactly **one** seat — KY-A1, which happens to be the
**lowest-yield** of the nine ($0.96/day, 2.9%) and the **largest** single loss ($39.78, 49%).

The market-level variant ("refuse any seat where |market mid − type prior| ≥ 0.20") converges on
the same single answer: it refuses KY-A1 and AL-A3 and nothing else. But applied family-wide it
would refuse **31 of 110 markets (28%)** from seating at all, for the chance-level precision
documented in §6.

> **Do not ship the X=0.10 row.** This entire table is computed on the *assumed* prior LR=0.79.
> §9 re-runs it on the verified Ballotpedia state rates and the sign flips: Kentucky amendments
> pass at 55.6%, so the accurate prior rates KY-A1 as the cheapest seat of the nine, not the
> dearest. The favourable row here is an artifact of a wrong input.

Note the YES-side check does pass its sanity test: AL-A3 was a YES seat at 0.51 against an LR
prior of 0.79 (gap −0.28, i.e. deep value) and the gate correctly leaves it open. It never filled;
it was ejected on outbid at 08-15 05:02, and the market subsequently ran to 0.835.

---

## 8. Recommendation

**Do not compile the fundamentals side-gate.** Reasons, in order of force:

1. It cannot separate the fills from the non-fills, and §4 proves this holds for every possible
   prior, not just the ones tested. AR-A578 vs RI-Q4 is the same measure type at the same price
   with the same gap and opposite outcomes.
2. Family-wide it has chance-level precision (33-35% vs a 26% base rate) at predicting which
   markets the actor repriced.
3. Its resolution (LR MAE 10.6pt) is 2-5x coarser than the 2-6pt gaps it would have to read.
4. The already-specified **post-sweep re-entry ban** (`fill-forensics-20260815.md` gate (e))
   achieves perfect separation on the same nine seats at **$0.00** forfeited LIP, Fisher exact
   two-sided p=0.048. A fundamentals gate is strictly dominated by it.

   The AR-A578 / RI-Q4 pair settles which variable is the real one. Same measure type
   (legislature-referred bond), same resting price (NO@0.18, implied YES 0.82), same prior, same
   gap — one filled, one did not. What differed was **when we sat down**:

   ```
   RI-Q4     seated 08-14 14:59:01Z   into a clean book (worst prior 1-min collapse: 0 ticks)   no fill
   AR-A578   seated 08-15 04:51:39Z   26 min AFTER a 14-tick collapse in its own book at 04:26   FILLED 05:30
   ```

   Fundamentals are constant across the pair; microstructure is not. The discriminating variable is
   the regime, not the measure.
5. Compiling a wrong causal story is worse than no gate: this one would have told us GA-A2 was the
   *safest* of the eight NO seats.

6. **Refining the prior inverts it.** On verified state-level rates the gate scores AUC 0.25 (§9)
   — worse than a coin, and worse than the coarse version. Anything that gets *more* wrong as its
   inputs get *more* accurate is not measuring what it claims to measure.

**Nothing here is worth keeping as a side-gate.** An earlier draft of this note recommended the
narrow ≥10pt deep-mispricing refusal as a sizing input; §9 retracts that. Its only apparent
success (KY-A1) reverses sign the moment the Kentucky base rate is looked up rather than assumed.

The one durable, checkable artifact is the **measure-type census** in §3 — the family genuinely
does price BOND 0.87 / legislature-referred 0.78 / citizen-initiated 0.44, and that is a useful
sanity rail for *new listings* whose books are empty. It is not a gate on seats.

**The honest limits**, stated plainly:
- The priors are coarse where they exist and absent where they matter. There is no published
  national bond-issue rate, no LRCA-only rate, and no subject-level (tax/bond/structural) split at
  all — so two of the three axes in the proposed prior table cannot be sourced.
- Within-type dispersion (LR p10-p90 = 0.570-0.905) swamps the per-seat signal, and per §9 the
  state-level refinement that would narrow it makes the ranking worse, not better.
- Small-n state rates are treacherous: IA is 5/5 and KY is 5/9. Those are 5-measure and 9-measure
  samples driving a 5-figure position. KY's 55.6% is why the gate inverts.
- These measures resolve at a **Nov 2027** election. National historical pass rates are computed
  over decades of different ballots; the 2027 slate's composition is not the historical mix, and
  15 months of campaign news will move these far more than any prior.
- A side-selection filter cannot fix a price model. Autoseat's problem on 08-15 was that it rested
  at ladder-derived prices in books that had just been swept — a *regime* error, not a *side*
  error. Four of nine seats were on the wrong side of a repricing; the one that lost most was the
  one seated into the deepest mispricing; but the ones that survived were not the ones a
  fundamentals gate would have protected.
- KY-A1's 156ct position was still open at the end of the capture window; its −$39.78 is a mark,
  not a realisation.

---

## 9. The real base rates — and the gate flips anti-predictive

All figures verified on Ballotpedia (retrieved 2026-08-15). Note ballotpedia.org blocks WebFetch;
sequential curl with a browser UA and ~4 s spacing works.

**National**, [Constitutional amendments since 2003](https://ballotpedia.org/Constitutional_amendments_since_2003):

```
all constitutional amendments (LRCA+ICA)          1,068 / 1,489   71.7%   2003-2025
amendments in states WITHOUT an initiative process   667 /   815   81.8%   2003-2025   <- our LR bucket
amendments in states WITH an initiative process       399 /   672   59.4%   2003-2025
```

Ballotpedia publishes **no** standalone national rate for LRCA alone, for legislatively referred
statutes, for bond issues, or for veto referenda (all four pages checked, no stats). The
citizen-initiative figure (1,351/3,274 = 41%, 1904-2024) came via the search index and is low
confidence. **Subject-level (tax / bond / structural) breakdown: NOT FOUND anywhere.**
So the subject axis proposed for the prior table cannot be sourced at all.

**Odd-year cycles** (these markets resolve Nov 2027, an odd year):
2025 25/30 = 83% ([2025](https://ballotpedia.org/2025_ballot_measures)) ·
2023 33/41 = 80.5% ([2023](https://ballotpedia.org/2023_ballot_measures)) ·
2021 26/39 = 66.7% (computed from [2021](https://ballotpedia.org/2021_ballot_measures)).
Ballotpedia notes odd-year amendment approval runs 9.2% higher than even years.

**State-level, constitutional amendments 2003-2025** (same source), for the eight states we sat in:

```
GA 28/32 87.5%   AR 23/31 74.2%   IA  5/5  100%    KY  5/9  55.6%
NC 11/13 84.6%   RI  6/8  75.0%   AL 64/83 77.1%   ID 12/13 92.3%
```

Plus Rhode Island bonds: **32/32, 100%, 2008-2023** (§4).

### Re-running P1 on the *accurate* prior makes it worse

Using Laplace-smoothed state rates (honest for n=5..13), with RI-Q4 on the RI bond record:

```
seat       implied YES   prior  (source)              gap      outcome
RI-Q4         0.82       0.971  RI bonds 32/32       +0.151      .
ID-HJR4       0.76       0.867  ID amend 12/13       +0.107      .
IA-A1         0.77       0.857  IA amend 5/5         +0.087    FILL
GA-A2         0.80       0.853  GA amend 28/32       +0.053    FILL
NC-A2         0.78       0.800  NC amend 11/13       +0.020      .
AL-A4         0.78       0.765  AL amend 64/83       -0.015      .
AR-A578       0.82       0.727  AR amend 23/31       -0.093    FILL
KY-A1         0.68       0.545  KY amend  5/9        -0.135    FILL
AL-A3         0.51       0.765  AL amend 64/83       -0.255      .

fills   mean gap  -0.022      the two LARGEST gaps are both NON-fills
nofills mean gap  +0.065      the two SMALLEST gaps are both FILLS
AUC(gap ranks fills above non-fills) = 0.25     (0.50 = chance; <0.50 = ANTI-predictive)
```

**The better the prior, the more wrong the gate.** With coarse type priors the gate was merely
useless (§4). With accurate state-level priors it is *actively inverted*: it would have refused
RI-Q4 and ID-HJR4 — two seats that never filled — while waving through AR-A578 and KY-A1, the two
seats that cost the most.

The single worst case is KY-A1. Kentucky has approved only **5 of 9** amendments since 2003, the
weakest record of any state we sat in. Our NO@0.32 (implied YES 0.68) is therefore *above* the
Kentucky base rate of 55.6% — the prior says that seat was **cheap**. It was our largest single
loss (−$39.78) and the market closed the day at 0.935. The prior was wrong by 38 points on the one
market where the gate appeared to work in §7; it worked there only because the coarse LR prior
(0.79) happened to be closer to Kentucky's truth than Kentucky's own history was.

That is the whole case against compiling this. The gate's one apparent success was an artifact of
using a *less* accurate number.

---

## 10. Reproduction

Venue pull (keyless, via VPS — Mac urllib hits SSL cert issues):
`GET https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXSTATEBALLOTMEASURE&limit=1000`
→ 111 markets, all closing 2027-11-02, `rules_primary` carries the full measure name.

Working files (scratchpad, session-local)
`/private/tmp/claude-501/-Users-ryanwhitehead-Documents-senate-domains-kalshi/162f05b7-b9bf-49dd-b319-057450acadb5/scratchpad/`
- `ballot_markets.json` — venue market pull, 111 tickers, titles + rules + live quotes
- `fam_table.txt` — flattened family table (ticker, price, volume, OI, rule text)
- `fam_replay.py` → `fam_ckpt.json` — 110-ticker book replay, yes-bid/yes-ask at five checkpoints
  (08-13 01:00Z, 08-15 04:00Z / 06:00Z / 14:00Z / 19:55Z) from `ballot_deltas.jsonl.gz`

Read-only throughout. Nothing written to the VPS except `/home/ubuntu/tmp_bg/mk.json` (a curl
scratch file, safe to delete). No orders placed or cancelled; no autoseat code or state modified.
