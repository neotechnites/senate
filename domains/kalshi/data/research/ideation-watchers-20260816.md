# IDEATION BURST — never-mined watcher exhaust (Mac, 2026-07-22 → 2026-08-16)

Run under `data/research/ideation-organ-SPEC.md`. Graveyard = 120 graves
(`sqlite3 data/kalshi_domain.db "SELECT idea, killing_number FROM graveyard"`).
Fee truth used everywhere below: `fee = ceil_to_0.0001(0.07 * n * p * (1-p))` dollars, maker $0.
Read-only. No orders placed.

---

## 0. WHAT THE FOUR WATCHERS ACTUALLY RECORDED

All four processes are **alive** (`ps`: pids 74712 dutchbook, 76388 xvenue, 74717 ens_forward,
76395 capture_cwing), each with a `caffeinate -is` companion.

| Watcher | Output file | Volume | Coverage | Nonzero? |
|---|---|---|---|---|
| `dutchbook_watch.py` | `dutchbook_paper.jsonl` | **47 episodes** | 12 active days of 24.6 elapsed; BTC 32 / ETH 11 / SOL 4; combos DY+15N 20, DN+15Y 14, BB_NO+15N 9, BA_NO+15Y 4 | **YES — and settlement-verified** |
| `xvenue_watch.py` | `xvenue_paper.jsonl` + `xvenue_watch.log` | **1,513 episodes**, 2,783 heartbeats (~19.3 d uptime) | 24 days, 510 distinct game-markets, 96/100 Kalshi games matched to a Poly slug | **YES — but the arb reading is wrong; the residual is directional** |
| `capture_cwing_books.py` | `cwing_books_{6 series}.jsonl` (~160 MB) | **422,742 full-ladder snapshots** | 14 days, ~3-min cadence, BRENTD/GOLDD/SILVERD/COPPERD/NATGASD/WTIH, size at every price | Data yes; **actionable events ~zero** |
| `ens_forward_capture.py` | `ens_forward.jsonl` | **114 city-days**, 86 settled, 451 scored bucket-days | 11 capture days × 6 cities, median 82 GEFS+ECMWF members | Data yes; **edge zero** |

### 0.1 dutchbook — the one that caught real events

Of 47 episodes, 33 are two-legged D-rung pairs with **both legs settled**.
**All 33 paid exactly 100c** — 0 joint-loss, 0 joint-win. The settlement-identity the script
asserts (threshold ordering `T<=K` for DY+15N, `T>=K` for DN+15Y) held without exception.

Recomputed with the true ceil-fee, not the script's un-ceiled `fee()`:

- median net **0.62 c/pair**, mean **1.30 c**, max **13.03 c**
- median displayed size **132 ct**; sizes range 0.25 → 2,000 (cap)
- realized **+$197.83** at full displayed size; **+$125.12** capped 500ct; **+$58.44** capped 200ct
- **one episode (13.03c × 835ct = $108.80) is 55% of the uncapped total**
- frequency **4.3 episodes/active day**, but only 12/24.6 days were active → **$2.38/elapsed-day at a 200ct cap**

### 0.2 xvenue — 1,513 events, and the "arb" is not an arb

Median logged net 7.1c, mean 10.0c, max 92.6c; median Poly ask depth 518 ct. After dropping
dust/resolved books (Poly ask outside 5–95c, or depth <100ct): **894 episodes**.

Two disqualifiers for reading these as locks:

1. **Poly ask-sum across both sides of the same game < 100 in 111/114 pairs** (median 87c) —
   an intra-Polymarket dutch book that cannot exist. Tightening the pairing window to 60s
   leaves n=22 (median 85c) and to 20s leaves n=1 → **UNDERPOWERED, not reported as a kill**;
   it is reported as evidence the two quotes are not simultaneous.
2. Kalshi bid-sum across both sides median **109c** at the same 60s window — also impossible
   on a coherent book, and explained by selection on a moving in-game book.

The *powered* result comes from settlement. I resolved 109 of the 423 filtered tickers
(Kalshi's `tickers=` batch endpoint silently returns nothing above 2 tickers — batched in 2s):

| gap = kbid − pask | n tickers | game-day clusters | realized YES rate | Kalshi-short-only PnL | naive t | **clustered t** |
|---|---|---|---|---|---|---|
| ≥0c | 109 | 22 | 0.413 [0.320, 0.505] | +7.68 c/ct | 1.95 | **2.48** |
| ≥10c | 81 | 22 | 0.370 | **+12.03 c/ct** | 2.63 | **3.16** |
| ≥15c | 34 | 17 | 0.294 | +19.63 c/ct | 3.10 | **5.36** |
| ≥20c | 12 | 9 | 0.333 | +25.31 c/ct | 2.28 | 2.09 (n<10 clusters — UNDERPOWERED) |

Mean Kalshi bid at alarm **52.24c**; mean Poly ask **40.41c**; realized truth **41.28%**.
**Truth sits on the Polymarket ask and ~12c below the Kalshi bid.** The tradeable object is
therefore the *unhedged Kalshi short*, with Polymarket used only as a free oracle.

### 0.3 cwing books — 3.19M pairs, $0.01

Rungs are cumulative thresholds ("close **above** X" — verified in `rules_primary`), so
`P(>lo) >= P(>hi)` must hold. Executable violation = buy lo-YES at ask, sell hi-YES at bid,
net of true fees > 0.

**3 violations in 3,185,799 ordered lo<hi pair-observations (1 per 1.06M).**
Max displayed size on a violation **0.5 contracts**. Total **$0.01**. All 3 in KXWTIH.

(First pass found 81,524 "violations" worth $679k — that was my own decode defect: `bid_lo >
ask_hi` is the *normal* price of the in-between digital, not an arb. Corrected above. Logging
this because kill-mechanism #4 bites the organ.)

### 0.4 ens_forward — 451 bucket-days, t=0.03

Rule as written in the script ("margin 8c both sides", P from ensemble member fraction):
261 trades, **mean +0.06 c/ct, sd 34.88, t=0.03**; day-clustered (10 clusters) +3.99c, t=0.87.
BUY side n=159 mean −1.47c; SELL side n=102 mean +2.43c.

---

## 1. CLAUDE'S 4 IDEAS (generated against the graveyard, killing numbers preregistered)

**C1 — CROSS-PRODUCT TAKER LOCK (crypto, last 15 min of the hour).**
Mechanism: `KX{C}15M` (15-min digital, strike K), the `KX{C}D` rung (strike T) and the
`KX{C}` range bucket all settle on the **same index print at the same instant**; when the
threshold ordering makes one pair a partition of the state space, both legs can be bought as a
taker for <100c − fees. Number: **33/33 settled pairs paid exactly 100c**; +$58.44 realized at
a 200ct cap over 24.6 days.
*Graves:* **D12** (maker-only MECE dutch book, BTC 28-bin SUM_ASK 103.90, 0 executable),
**A28** (exhaustive-ladder dutch book, $8.50 board-wide, 15-month lockup = $0.02/day),
**A69** (settlement locks, 0 executable, 94.4% sum to 200.00), **A11** (no ladder exists).
*Distinct in one sentence:* all three graves are within-event or maker-side; this is a **taker**
lock across **three different products** on one index print with a **≤15-minute** lockup, and it
is the only one of the four that has been verified on 33 actual settlements rather than quoted.
*Preregistered kill:* net **$/elapsed-day at a 200ct cap must be ≥ $5/day** over the next 30
episodes. **Current: $2.38/day → FAILS unless fill realization holds at larger size.**

**C2 — KALSHI STALE-BID FADE, POLYMARKET AS A FREE ORACLE (one leg only).**
Mechanism: during live MLB, Kalshi's quoted `yes_bid` runs ~12c above the settlement-realized
frequency while the Polymarket ask sits on it. Sell the Kalshi YES at that bid as a taker; do
**not** execute on Polymarket at all — no second fee, no second venue, no custody.
Number: gap≥10c → n=81 tickers, 22 game-day clusters, **+12.03 c/ct, clustered t=3.16**,
realized YES rate 0.370 vs a 0.52 bid.
*Graves:* **A25** (Kalshi↔Polymarket cross-venue basis, 0/16 matched events net-positive, fees
4–5× any basis), **A1** (Deribit cross-venue fair-value gate, EV −0.54 c/ct, t=−4.21),
**A30** (MLB maker +1.19c fails Bonferroni ×8), **A62** (Gemini↔Kalshi cross-listing).
*Distinct in one sentence:* A25 and A62 tried to **capture the basis with a hedged two-leg
trade** and died on paying fees twice; this executes **one leg** and treats the other venue as a
free information source, which is exactly the cost structure A25's killing number rules out.
*Preregistered kill:* **median takeable Kalshi bid depth at the alarm < 25 contracts, OR the
alarm bid gone/repriced within 60s in >50% of alarms → DEAD.** (Not on disk: `xvenue_watch`
logs Poly depth but never Kalshi depth, and reads `yes_bid_dollars` from the /markets **list**
endpoint, which may be cached relative to the live orderbook.)

**C3 — COMMODITY-DAILY MONOTONICITY LOCK.**
*Graves:* **A29** (0 violations in 34,614 pairs) — this is the same idea at 92× the sample with
live depth attached. *Preregistered kill:* ≥1 executable violation per 100,000 pair-observations
at ≥25ct. **ACTUAL: 1 per 1,061,933, max size 0.5ct, $0.01 total.**

**C4 — ENSEMBLE SELL-SIDE ONLY.** The BUY/SELL asymmetry (−1.47c vs +2.43c) suggests the
ensemble is only useful for identifying *overpriced* buckets.
*Graves:* **A24** (KXHIGH realized-temp vantage; book pinned-correct 98% by 18:00 local,
N=504, ~$0/day), **D22** (weather-data taker dominated by the tape). *Distinct:* 9am-ET
forecast-time signal, sell-only, not a same-day realized-obs vantage.
*Preregistered kill:* day-clustered t < 2.0. **ACTUAL: 8 clusters, +2.90c, sd 13.35, t=0.61.**

---

## 2. GEMINI'S 4 IDEAS (generated independently, same fuel + same graveyard)

Invoked `~/.nvm/versions/node/v20.9.0/bin/gemini -p "$(cat g1.txt)"`; Gemini did **not** see
Claude's ideas at generation time.

- **G1 — Directional Kalshi MLB sale using Poly as a fair-value oracle.** Cites A25 ("directional,
  unhedged, not a basis trade"). Kill: mean profit/ct < +2.0c over 50 completed events. Cost $5, 90 min.
  *(Convergent with C2 — independently reached from the same fuel.)*
- **G2 — Volatility-gated dutch-book execution.** Cites D12. Kill: <10 qualifying vol episodes in 7 days. $10, 60 min.
- **G3 — Post a Kalshi ask at (bid − 1c) on the same alarm, to make instead of take.** Cites A30. Kill: fill rate <5% on 100 events. $20, 120 min.
- **G4 — Ensemble *variance* instead of median: bet the market underprices forecast dispersion.** Cites A24. Kill: two-sample p > 0.20 on the existing 451 bucket-days. $0, 45 min.
- **Gemini's funding pick:** G1. **Gemini's watcher verdicts:** keep dutchbook, keep xvenue, kill cwing, kill ens.

---

## 3. CROSS-EXAMINATION (condensed verbatim — required by §2.6)

### Round 1 — Claude attacks Gemini

> **G1:** agreed in substance, but your threshold is too lax — selling at the bid concedes ~5c of
> half-spread, so +2.0c is inside noise. And you named the wrong killing number: the binding
> unknown is not PnL, it is whether the alarm bid is **real**. `yes_bid_dollars` comes from the
> /markets LIST endpoint, which may be cached relative to the live orderbook. Restate as a
> depth/liveness number or concede.
> **G2:** gating cannot raise revenue, only cut uptime, and uptime is already the binding
> constraint — 12 active days of 24.6 elapsed, HHI over active days 0.215. Your threshold is a
> compute-savings test, not an edge test, and as written it fails the ≥10-event power rule.
> **G3:** INCOHERENT. An ask 1c **below** the standing bid is marketable and executes immediately
> against that bid — it is C2/G1 with a 1c worse limit price. There is no maker fill to measure
> and no $0 maker fee.
> **G4:** I ran it. Median ensemble sd = 1.96°F. HIGH-var n=121 mean +0.63c; LOW-var n=140 mean
> −0.44c; **two-sample t = 0.25 (p ≈ 0.80)**. Your own threshold was "p > 0.20 kills". Dead by
> your own number.

### Round 2 — Gemini concedes / rebuts, then attacks Claude

> **(1) G2: Conceded.** Gating reduces already-constrained uptime without proving a distinct edge
> from C1. The kill test was ill-posed.
> **G3: Conceded.** The proposed order is marketable and would execute as a taker, not a maker.
> The logic is incoherent.
> **G4: Conceded.** Dead by the preregistered p > 0.20 kill number (t=0.25, p≈0.80).
> **(2) G1 restated:** "KILL G1 if the median takeable size at the alarm bid is < 25 contracts OR
> if the alarm bid is removed or repriced within 5 seconds in >20% of events."
> **(3) Attack on C1:** "profitability hinges on optimistic fill assumptions at displayed size.
> KILL C1 if median net slippage (both legs) exceeds 1.5c over the next 30 attempts at 200ct."
> **Attack on C2:** "the edge is compensation for adverse selection — you hit the bid precisely
> when its maker is uninformed. KILL C2 if the median 60-second post-fill MTM loss against the
> Kalshi mid exceeds 4.0c."
> **(4) Verdicts:** C1 CONDITIONAL(slippage <1.5c); C2 CONDITIONAL(60s MTM loss <4.0c);
> C3 DEAD(1 per 1.06M); C4 DEAD(t=0.61); G1 CONDITIONAL(depth ≥25ct and bid persists >5s in 80%);
> G2 DEAD(conceded); G3 DEAD(conceded, incoherent); G4 DEAD(p≈0.80).
> Watchers: keep dutchbook, keep xvenue, kill cwing, kill ens.

**Named concessions:** Gemini conceded **G2**, **G3**, **G4** by name. Claude conceded that
**C2's binding unknown is Kalshi-side depth/liveness, not PnL**, and adopts Gemini's stricter
liveness clause (repriced within 5s in >20% of alarms) into C2's gate.

**Claude's partial rebuttal to Gemini's C2 attack, recorded:** the +12.03 c/ct is a
**settlement-realized** number, not a mark — every position was carried to the game's
settlement. A 60s MTM excursion cannot erase it. The MTM test is accepted only as a *proxy for
whether the bid was ever takeable*, which is the same question the depth gate asks.

---

## 4. POWER CHECK (§2.4)

| Verdict | Events | Powered? |
|---|---|---|
| C1 settlement identity 33/33 | 33 pairs, 12 days | YES |
| C1 $/day at 200ct cap | 47 episodes, 24.6 days | YES |
| C2 gap≥10c, +12.03 c/ct | 81 tickers, **22 game-day clusters** | YES |
| C2 gap≥20c, +25.31 c/ct | 12 tickers, **9 clusters** | **NO — UNDERPOWERED, not cited** |
| C3 3 per 3,185,799 | 3.19M pair-obs, 14 days | YES |
| C4 SELL-only t=0.61 | 102 trades, 8 day-clusters | **borderline — reported as DEAD only because the point estimate's clustered t is 0.61, well inside noise** |
| Poly ask-sum <100 in 111/114 | tightened to 60s → n=22; to 20s → n=1 | **NO — used as evidence of non-simultaneity, not as a kill** |
| G4 variance split t=0.25 | 261 trades, 10 day-clusters | YES (at the ≥10 floor) |

---

## 5. VERDICTS

| Idea | Verdict |
|---|---|
| **C2 / G1 — Kalshi stale-bid fade, Poly as a free oracle** | **CONDITIONAL(gate: median takeable Kalshi bid depth at alarm ≥ 25 ct AND alarm bid not repriced within 5s in ≥80% of alarms)** — the only TRADE-shaped survivor |
| C1 — cross-product crypto taker lock | **CONDITIONAL(gate: ≥$5/elapsed-day at a 200ct cap AND median two-leg slippage <1.5c over 30 episodes)** — currently $2.38/day, below its own bar |
| C3 — commodity-daily monotonicity lock | **DEAD(3 executable violations in 3,185,799 pair-obs = 1 per 1.06M; $0.01 total; max size 0.5 ct)** |
| C4 — ensemble sell-side only | **DEAD(8 day-clusters, +2.90 c/ct, sd 13.35, t=0.61)** |
| G2 — vol-gated dutch book | **DEAD(conceded; gating cuts uptime, and uptime is already 12/24.6 days)** |
| G3 — Kalshi ask at bid−1c | **DEAD(conceded; marketable order, executes as taker — not a maker trade)** |
| G4 — ensemble variance | **DEAD(two-sample t=0.25, p≈0.80, vs its own p>0.20 threshold)** |

### 5.1 Kill test for the survivor (C2/G1) — costed, per §2.5

Add three fields to `xvenue_watch.py` at each alarm: (a) the **live `/markets/{tk}/orderbook`**
best bid + size (not the cached list-endpoint `yes_bid_dollars`), (b) the same book re-pulled at
**+5s** and **+60s**, (c) the Kalshi ask. Then run one MLB slate.
**Cost: $0 capital (read-only, keyless market-data API), ~35 minutes of editing, 1 evening of
wall-clock, ~2,600 extra API calls/day (well under the 8 req/s ceiling already respected).**
**Pass:** median takeable size at the alarm bid ≥25 ct AND bid unchanged at +5s in ≥80% of
alarms AND the list-endpoint bid equals the live-book bid in ≥90% of alarms.
**Fail on any one ⇒ DEAD**, and C2 joins A25 as a cross-venue grave.

### 5.2 Kill test for C1 — costed

`dutchbook_watch.py` already logs everything needed except **fill realization**. Change nothing;
just let it accumulate to 30 more episodes and re-score at a 200ct cap.
**Cost: $0, 0 minutes (already running); ~7 more days of wall-clock at 4.3 episodes/active day.**

---

## 6. WATCHER KEEP/KILL (they consume Mac resources)

| Watcher | CPU time to date | Verdict | Number |
|---|---|---|---|
| `dutchbook_watch.py` | 15:08 | **KEEP** | 33/33 settlement-verified locks; only unresolved question is fill realization, and it is $0/0min to answer by waiting |
| `xvenue_watch.py` | 58:24 | **KEEP — but INSTRUMENT FIRST** | produced the only powered survivor (+12.03 c/ct, clustered t=3.16, 22 clusters); it is currently blind on the one field that decides the idea (Kalshi bid depth), so keeping it unmodified buys nothing |
| `capture_cwing_books.py` | 13:29, **~160 MB and growing** | **KILL** | 3 executable violations in 3,185,799 pair-obs over 14 days = $0.01; it is the most expensive of the four in disk and API calls and has produced the least |
| `ens_forward_capture.py` | 0:02 | **KILL the trading rule, KEEP the capture** | 261 trades, t=0.03; variance variant t=0.25 — but it costs 2 seconds of CPU/day and 170 KB total, so the resource argument for killing it does not bind; the *rule* is dead, the daemon is free |

---

## 7. LEDGER LINE (append to SPEC §4)

| Date | Burst | Fuel | Ideas (C/G) | Survivors | New graves | Graveyard size after | Tokens |
|---|---|---|---|---|---|---|---|
| 2026-08-16 | `ideation-watchers-20260816.md` | 4 Mac watchers: 47 dutchbook episodes, 1,513 xvenue episodes, 422,742 cwing book snapshots, 114 ens city-days | 4 / 4 | **1** (C2/G1 stale-bid fade, conditional on depth) | 6 (C1-cond, C3, C4, G2, G3, G4) | **126** | ~105k |
