# Fill Forensics — autoseat adverse maker fills, KXSTATEBALLOTMEASURE
Date: 2026-08-15
Scope: could an early-warning gate have fired BEFORE the 7 adverse fills, and what would it cost in false ejects?

---

## 0. TL;DR verdicts

| # | Gate | Verdict | Catches | False ejects | LIP forfeited |
|---|------|---------|---------|--------------|---------------|
| a | evacuation-eject (rival depth on our side drops >X% in N cycles) | **DEAD** | 0/4 at a 1-alarm-per-24-seat-h budget | 58 alarms/24 seat-h if tuned to catch best fill | n/a |
| b | drift-eject (mid moves >=T ticks against us) | **DEAD** | 0/4 at T>=2 ticks | 2 seats even while catching nothing | $12.80 |
| c | share-spike (our share jumps, rivals left) | **DEAD — wrong sign** | 0/4; share FELL or was flat before all 4 | n/a | n/a |
| d | ticks_behind>=1 residency (never rest behind the touch) | **COMPILE (provisional)** | 3/4 at K=4 cycles | 1 incremental (AL-A4) | $4.96 |
| e | post-sweep re-entry ban (do not seat into a book swept in last 6h) | **COMPILE — best per dollar** | 3/4 | **0 of 5** | **$0.00** |
| f | family sweep-storm circuit breaker | **COMPILE** | 2/4 on 8/15 + 2/3 overnight | contagion-only | $4.68 (16.5%) |

The single most important empirical fact: **these fills had no book precursor.** The order book was
frozen — literally constant integers — for 1 to 5 hours, then the entire NO ladder from the touch
down through our price was annihilated inside one 60-second bar. Gates (a)/(b)/(c) are attempts to
read a trend that does not exist in the data. The gates that survive are all *regime/entry* gates,
not *trend* gates.

---

## 1. Data inventory (what exists, what does not)

**Used (all read-only):**

| Source | Path | Coverage | Value |
|---|---|---|---|
| Full L2 book deltas + snapshots | VPS `/home/ubuntu/kalshi_data/competition/deltas-2026081{3,4,5*}.jsonl.gz` | ALL 110 ballot tickers, 08-13 00:00Z → 08-15 20:00Z, 578,971 ballot messages | **Decisive.** Enables exact per-tick book replay |
| fieldwatch | VPS `/home/ubuntu/kalshi_data/fieldwatch/fieldwatch.jsonl` | 13,504 rows, 60s cadence, but only **6 keys** (AK-BM2, AL-A4, NC-A2, RI-Q4, GA-A2, AL-A3) | 1 of 7 fills + 5 clean controls |
| autoseat seat_rate | VPS `/home/ubuntu/kalshi_data/autoseat/autoseat.jsonl` | 574 events, ~16 min cadence, **9 seats**, incl. all 4 of the 8/15 fills | ticks_behind / share / rate_per_day series |
| autoseat lifecycle | same file | `seat_gone`, `fill`, `eject_tick`, `retreated` | fill ground truth |

**Mac captures are irrelevant to this question — established in the first 3 minutes and abandoned.**
`cwing_books_*` (commodities), `kbt_books_*` (crypto), `xvenue_paper` (MLB), `dutchbook_paper`
(crypto), `ens_forward` (weather) contain **zero** KXSTATEBALLOTMEASURE rows. Only
`listing_books.jsonl` touches the family, with 120 rows total — a new-listing sampler at 20-min
cadence, best-bid/ask only, no depth. Useless for depth forensics.

**Ground truth from autoseat.jsonl (UTC):**

```
08-15 04:25:59  seat_gone  GA-A2     (250ct)
08-15 05:40:12  seat_gone  AR-A578   (277ct)   [fill ~05:30]
08-15 14:19:37  seat_gone  IA-A1     (217ct)   [fill ~14:09]
08-15 19:00:34  fill       KY-A1  filled=156.0 frac=1.0  [fill ~17:51]
08-15 16:52     halt-backup-fill-incident-20260815.json  "3 adverse fills + broken killswitch"
```

---

## 2. What actually happened — book replay of all 4 fills

Reconstructed from snapshots + deltas. `ahead>p` = contracts resting on our own side at prices more
aggressive than ours (the queue that must be cleared before we are hit). Our seats are NO-side.

**GA-A2 — our NO bid @ 20c, filled 04:25Z**

```
utc          no_touch  ahead>p    at_p
08-15 03:30      21       598     1455
08-15 03:45      21       598     1455
08-15 04:00      21       598     1455
08-15 04:15      21       598     1455
08-15 04:21      21       635     1455
08-15 04:25      21       385     1455   <- fill minute
08-15 04:26      15         0        0   <- entire ladder gone, touch -6 ticks
08-15 04:27      13         0        0
```

**AR-A578 — NO @ 18c, filled 05:30Z**

```
08-15 01:18      27      6226        0
   ... unchanged for 3 hours ...
08-15 04:19      27      6226        0
08-15 04:30      23       204        0   <- first collapse (this book, pre-seat)
08-15 04:45      18         0      202   <- we seat here
08-15 05:30      19        20      279   <- fill minute
08-15 05:31      15         0        0
```

**IA-A1 — NO @ 23c, filled 14:09Z**

```
08-15 10:16      24       381      237
   ... unchanged for 3h51m ...
08-15 14:02      24       381      237
08-15 14:07      24       356      237
08-15 14:09      23         0      237   <- fill minute
08-15 14:10      20         0        0
```

**KY-A1 — NO @ 32c, filled 17:51Z**

```
08-15 12:16      36       560      356
   ... unchanged for 5h09m ...
08-15 17:25      36       544      356
08-15 17:40      35       445      356
08-15 17:50      35       300      356
08-15 17:51      35       375      356   <- fill minute
08-15 17:52      11         0        0   <- touch -25 ticks
```

**The signature is identical in all four: multi-hour frozen book, then a 6-to-25-tick annihilation
in under 60 seconds.** Our-side touch never moved more than **1 tick** at any point in the entire
pre-fill life of any of the four seats.

---

## 3. Gate-by-gate evidence

### (a) evacuation-eject — DEAD

Feature: `drop_pct` = (trailing-60min max of `ahead>p` − current) / max, computed every minute.
Labels: pre-fill = the 60 min before each fill (n=63 minutes); control = all other seat-minutes
(n=2,828, 47 seat-hours).

```
feature       pre_med    pre_p90    ctl_med    ctl_p90    ctl_p99
drop_pct        0.000      0.116      0.000      0.107      1.000
tick_drop       0.000      0.000      0.000      0.000      2.000
```

The pre-fill and control distributions are **statistically identical**. At a false-alarm budget of
1 alarm per 24 seat-hours the threshold is drop_pct >= 1.000, which catches **0/4** fills.

Per-fill best trailing-60min drop before the fill: GA-A2 0.505, KY-A1 0.464, AR-A578 0.116,
IA-A1 0.066. Tuning the gate to catch the *best* of these (0.505) produces **58.05 false alarms per
24 seat-hours** — control minutes exceed 0.505 in 114/2,828 cases (4.03%).

Distinct-alarm rate at X=50%, W=30min, per seat:

```
GA-A2     13.4 seat-h   2 alarms   3.57/24h   FILL
IA-A1      9.3 seat-h   1 alarm    2.57/24h   FILL
KY-A1     11.8 seat-h   1 alarm    2.03/24h   FILL
AL-A4     42.6 seat-h   0 alarms   0.00/24h   no fill
NC-A2     42.7 seat-h   6 alarms   3.37/24h   no fill
RI-Q4     27.6 seat-h   0 alarms   0.00/24h   no fill
ID-HJR4    4.3 seat-h   1 alarm    5.52/24h   no fill   <- highest alarm rate, never filled
AL-A3      8.7 seat-h   1 alarm    2.75/24h   no fill
```

Complete overlap; the highest-alarm seat never filled. **DEAD.**

### (b) drift-eject — DEAD

Our-side touch tick change over trailing W before each fill: GA-A2 **0**, AR-A578 **0**,
IA-A1 **0**, KY-A1 **1**. Backtest:

```
T=1 W=15/30/60m   2/4 caught   3 FP (AL-A4,NC-A2,AL-A3)   $14.05 forfeited
T=2 any W         0/4 caught   2 FP (AL-A4,NC-A2)         $12.80 forfeited
T=3 any W         0/4 caught   1 FP (NC-A2)               $5.75 forfeited
T=5 any W         0/4 caught   0 FP                       $0.00
```

At any threshold that avoids firing constantly, it catches nothing. Price did not drift — it
gapped. **DEAD.**

### (c) share-spike — DEAD, and the hypothesis is backwards

The premise was "rivals left, our share spikes". The tape says the opposite: **rivals piled in.**

```
seat       share first -> last     direction
GA-A2      0.3634 -> 0.0917        FELL (rivals x2.9 the field)
AR-A578    0.5256 -> 0.4973        FELL
IA-A1      0.5116 -> 0.2145        FELL / flat last 6 cycles
KY-A1      0.2073 -> 0.0310        FELL / flat last 6 cycles
```

fieldwatch confirms mechanistically for GA-A2: `field_vs_entry` climbed 1.00 -> 2.91 over the 11h
before the fill while our share fell 0.370 -> 0.092. **No fill was preceded by a share rise.**

Worse, the naive "field grew" version of this gate is **anti-predictive**. `field_2x_entry` fired
on 93.5% of rows (2,450/2,620) for AK-BM2, which never filled, and on only 9.9% (65/659) for
GA-A2, which did. Max `field_vs_entry`: AK-BM2 11.92, AL-A4 9.69, NC-A2 6.43 (all no-fill) vs
GA-A2 2.91 (fill). **DEAD.**

### (d) ticks_behind >= 1 residency — COMPILE (provisional)

The only per-seat state variable in the existing telemetry with real separation. Exposure-weighted
over 153.1 seat-hours from `seat_rate`:

```
bucket    seat-hrs  fills   fills/100h
tb=0         104.3      0         0.00
tb=1          25.6      3        11.72
tb>=2         23.2      1         4.31
```

**Zero fills in 104.3 seat-hours at the touch; 4 fills in 48.8 seat-hours behind it.** All 4 fills
had ticks_behind >= 1 at the last sample before the fill (GA-A2 1, IA-A1 1, AR-A578 1, KY-A1 4).
The 3 seats that survived to the manual 19:00Z cancel were at tb=0.

Backtest — eject after K consecutive cycles at tb>=1 (streak resets on tb=0):

```
  K   caught   lead (min)                                       FP  FP seats                 forfeit
  2      4/4   AR-A578 6, GA-A2 610, IA-A1 337, KY-A1 701        4  AL-A4,NC-A2,AL-A3,ID-HJR4  $11.70
  4      3/4   GA-A2 577, IA-A1 306, KY-A1 670                   3  AL-A4,AL-A3,ID-HJR4         $4.96
  6      3/4   GA-A2 544, IA-A1 274, KY-A1 638                   3  AL-A4,AL-A3,ID-HJR4         $4.75
```

K=4 is the knee. Two of its three "false ejects" (AL-A3, ID-HJR4) were ejected by autoseat's
*existing* outbid logic anyway, so the **incremental** cost is AL-A4 alone, ~$4.00. AR-A578 is
structurally uncatchable at K>2 — that seat lived under 20 minutes and produced only 2 seat_rate
samples.

**No yield confound**, which is the key check: LIP accrual per seat-hour is the same in both
buckets — tb=0 $0.184/seat-h vs tb>=1 $0.187/seat-h. Ejecting behind-the-touch seats does not
forfeit disproportionately good seats.

Caveats, stated plainly:
- n = 9 seats. Fisher exact on seat-episodes (tb>=1: 4 fill/2 no-fill; tb=0: 0 fill/3 no-fill)
  gives **two-sided p = 0.167**. Not significant.
- The mechanism is probably **correlational, not protective**. A 6-25 tick sweep clears the touch
  too — being at the touch would not have saved us. What tb>=1 really marks is "a rival is actively
  outbidding us here", i.e. a contested book, which is the kind of book that attracts the sweep.
- NC-A2 survived a 3-tick collapse at tb=0 on 08-14 12:10, so tb=0 is not proof against sweeps —
  just against the ones we observed.

Compile it because the payoff is asymmetric and cheap (~$4-5 to remove 3 of 4 fills), not because
the statistics are settled.

### (e) post-sweep re-entry ban — COMPILE, best per dollar

Found by asking what the book looked like *before we sat down*, not before the fill. Worst 1-minute
our-side touch collapse in the 6 hours **preceding seat placement**:

```
seat       seated (UTC)     worst pre-seat 1min collapse      outcome
AR-A578    08-15 04:45      14 ticks  at 04:26                FILLED 05:30
IA-A1      08-15 04:46      17 ticks  at 04:03                FILLED 14:09
KY-A1      08-15 06:00      12 ticks  at 05:25                FILLED 17:51
GA-A2      08-14 14:54       0 ticks                          FILLED 04:25
AL-A4      08-14 00:08       3 ticks  at 08-13 18:51          no fill
NC-A2      08-14 00:08       0 ticks                          no fill
RI-Q4      08-14 15:14       0 ticks                          no fill
ID-HJR4    08-15 00:03       1 tick   at 08-14 22:38          no fill
AL-A3      08-14 14:54       1 tick   at 08-14 13:24          no fill
```

**Perfect separation at any threshold in 4..11 ticks.** Filled seats were seated into books that had
been blown up 12-17 ticks within the preceding 20-45 minutes. Non-filled seats were seated into
books whose worst prior disturbance was 0-3 ticks.

Gate: **do not place a new seat in a market whose our-side touch fell >=5 ticks in any single minute
within the last 6h.**

- Blocks AR-A578, IA-A1, KY-A1 = **650 of the 900 contracts** filled on 8/15.
- Blocks **0 of 5** non-filled seats. **$0.00 forfeited LIP** on the observed window.
- Fisher exact (flagged: 3 fill/0 no-fill; clean: 1 fill/5 no-fill) **two-sided p = 0.048**.

Caveat that matters: all three flagged seats were placed inside one ~90-minute window
(08-15 04:45-06:00) following one market-wide episode. Statistically this is closer to n=1 episode
than n=3 independent events. But it is a zero-cost gate, so it costs nothing to be wrong.

Mechanically it is exactly right: autoseat freed escrow from the GA-A2/ID-HJR4 losses at 04:26 and
immediately redeployed it into three books that had just been swept — it walked the capital back
into the blast radius.

### (f) family sweep-storm circuit breaker — COMPILE

Replayed all 110 ballot tickers. Defining a sweep as a >=5-tick NO-touch drop in one minute, there
were 93 sweeps in ~68 hours, and they cluster hard into storms:

```
08-13 23h   4     08-15 04h  11   <- GA-A2 filled 04:25
08-14 00h  12     08-15 05h   9   <- AR-A578 filled 05:30
08-14 01h   7     08-15 14h   1   <- IA-A1 filled 14:09 (isolated)
                  08-15 17h  10   <- KY-A1 filled 17:51
                  08-15 18h   6
                  08-15 19h   9
```

The 08-13 23h -> 08-14 01h storm (23 sweeps) is **exactly when the earlier overnight incident
happened** (3 fills, 744ct, -$149.77). That is independent out-of-sample confirmation on data the
gate was not fitted to. **6 of the 7 fills occurred inside a sweep storm.**

Backtest (flat the family when >=N sweeps occur in trailing W hours):

```
params      caught   which                 blocked seat-h   forfeit   % of LIP
N=4 W=1h     2/4     AR-A578, KY-A1              12.3        $4.68      16.5%
N=6 W=1h     2/4     AR-A578, KY-A1              11.2        $4.12      14.5%
N=4 W=2h     2/4     AR-A578, KY-A1              19.7        $7.14      25.2%
```

Total observed baseline: 153.1 seat-hours, $28.36 accrued LIP.

It catches only 2/4 because a *trailing* window cannot save the seat that **starts** the storm —
GA-A2's own fill at 04:25 was the first sweep of the 04h storm, and IA-A1's 14:09 fill was an
isolated 1-sweep hour. This is a **contagion gate, not a prediction gate**: it protects the 2nd
through Nth victim. Given that 3 of the 7 fills (the overnight cluster) and 2 of the 4 on 8/15 were
downstream victims, that is most of the damage.

Expectancy: at the parent-supplied -$149.77 / 744ct = **-$0.2013 per contract**, the 433 contracts
of AR-A578 + KY-A1 are ~$87 avoided, plus ~2 of the 3 overnight fills (~$100). Roughly **$150-190
avoided for $4.68 forfeited**.

---

## 4. Recommended stack

These are complementary, not alternatives. In precedence order:

1. **(e) post-sweep re-entry ban** — 6h lockout per ticker after any >=5-tick 1-min collapse on our
   side. Zero measured cost. Ship first.
2. **(f) family storm breaker** — N=4 sweeps in trailing 1h -> stop *new* seating family-wide and
   flatten resting seats. $4.68 / 16.5% of LIP.
3. **(d) tb>=1, K=4 eject** — ~$4-5, removes the residual.
4. Keep the compiled 24h terminal curfew. It is orthogonal: all 4 of the 8/15 fills were inside
   T-24h, but so were many safe seat-hours, and the curfew alone would not have stopped the
   overnight cluster.

Note gates (e) and (f) overlap substantially — (e) is the per-ticker case of (f). Deploying (e)
alone captures most of the benefit at literally zero measured yield cost.

---

## 5. Missing capture — specify these before the next window

1. **Trade tape.** The deltas give net book change only; a `delta_fp` of -30 cannot be distinguished
   between a cancel and a trade. Every conclusion about "a sweep" is inferred from touch collapse,
   not observed aggression. **Subscribe the Kalshi `trade` websocket channel for
   KXSTATEBALLOTMEASURE and log aggressor side, price, count.** Without this, the question "was
   there a build-up of aggressive one-way flow before the sweep?" is unanswerable — and that is the
   single most likely place a genuine early-warning signal is hiding.

2. **Direct fill timestamps.** autoseat only detects fills at its ~15-min poll (`seat_gone` at
   04:25:59, 05:40:12, 14:19:37 vs actual fills 04:25, 05:30, 14:09 — up to 10 min of lag, and
   KY-A1's 17:51 fill was not logged until 19:00:34, 69 minutes late). **Log the fills websocket
   per-order**, so lead times are measured against truth rather than a poll boundary.

3. **fieldwatch coverage gap.** It watched 6 keys while 9+ seats were resting; AR-A578, IA-A1 and
   KY-A1 — three of the four fills — had no fieldwatch series at all. **Auto-register every resting
   seat with fieldwatch at placement time.**

4. **Overnight 08-13/14 incident is only partially reconstructable.** Book deltas cover it, but
   there is no `seat_rate` or fieldwatch series for those tickers/prices, so per-seat ticks_behind
   and share for those 3 fills could not be recovered. Their exact tickers and resting prices were
   not recoverable from `halt-backup-20260813/` either (it contains only
   `autoseat_halt.json` / `rung1_halt.json`, 186 and 376 bytes, no per-seat state).

---

## 6. Reproduction

Working files (scratchpad, session-local):
`/private/tmp/claude-501/-Users-ryanwhitehead-Documents-senate-domains-kalshi/162f05b7-b9bf-49dd-b319-057450acadb5/scratchpad/`
- `ballot_deltas.jsonl.gz` — 578,971 ballot book messages, 08-13 → 08-15, extracted from VPS `competition/deltas-*`
- `replay.py` -> `books.pkl` — per-minute book reconstruction for our 9 seats
- `gates2.py`, `roc.py`, `family.py` — gate backtests, ROC test, family sweep census
- `fieldwatch.jsonl`, `autoseat.jsonl` — copies of VPS telemetry

Nothing was written to the VPS except `/home/ubuntu/tmp_ff/` (extraction scratch — safe to delete).
No orders placed or cancelled; no autoseat code or state modified.
