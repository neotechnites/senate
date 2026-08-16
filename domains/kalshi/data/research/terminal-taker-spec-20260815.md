# Terminal-Taker Spec — KXSTATEBALLOTMEASURE LIP window
Author: taker-side research lane. Date: 2026-08-15T20:35Z. All venue access READ-ONLY (GET only: `/portfolio/fills`, `/portfolio/positions`, `/markets`, `/markets/trades`, `/markets/{t}/orderbook`).

**Verdict up front: the thesis as stated is FALSIFIED. The taker's edge was real and large (+$58.69, +8.4% in <15h on our 4 fills), but it did NOT come from stale quotes. There are zero stale/crossed quotes in this series right now, and the replicable follow-the-sweep version nets ~+1c/contract before spread crossing — i.e. approximately zero. Do not fund it. Run the kill test in §7 first.**

---

## 1. The receipt: our 4 adverse fills, and what the taker actually made

Source: `/Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research/fills_all_20260815.json` (1540 account fills, 9 in this series), cross-checked against `/portfolio/positions` and the public tape.

Our resting orders were **NO bids** (venue: `book_side: "ask"`, `is_taker: false`, `fee_cost: 0.000000` — maker waiver confirmed). Our own DB `active_orders` mislabels these as `side: 'yes'` at the NO price — **a real bug: `harness/venue_client.place_post_only_order` maps `side='no'` to `yes_price = 100 - price_cents`, but the state row stores the raw `price` with `side` from the caller. Order `7102964c-…` reads `side='yes', price=0.32` in `data/kalshi_domain.db` while the venue fill reads `no_price_dollars: "0.3200", outcome_side: "no"`.** Fix the state writer before any further reconciliation work.

| market | fill (UTC) | T-to-close | cnt | our NO entry | taker's YES px | taker notional | taker fee | mark @19:00Z | mark now | taker net now | ROI |
|---|---|---|---|---|---|---|---|---|---|---|---|
| GA-A2 | 04:25:06 | T-23.6h | 250 | 0.20 | 0.80 | $200.00 | $2.80 | 0.86 | 0.86 | **+$12.20** | +6.1% |
| AR-A578 | 05:30:46 | T-22.5h | 277 | 0.18 | 0.82 | $227.14 | $2.86 | 0.86 | 0.86 | **+$8.22** | +3.6% |
| IA-A1 | 14:09:09 | T-13.8h | 217 | 0.23 | 0.77 | $167.09 | $2.69 | 0.81 | 0.79 | **+$1.65** | +1.0% |
| KY-A1 | 17:51:28 | T-10.1h | 156 | 0.32 | 0.68 | $106.08 | $2.38 | 0.84 | 0.93 | **+$36.62** | +34.5% |
| **TOTAL** | | | 900 | | | **$700.31** | **$10.73** | | | **+$58.69** | **+8.4%** |

Hold-to-settlement (all four YES): **+$188.96 / +27.0%** — but resolution is **2027-11-02**, a 15-month hold. That is 20%/yr on locked collateral, not an edge.

Our side, for the record: realized −$34.43 + $6.79 fees = **−$41.22**, plus KY-A1 still open (short 156 YES @ 0.68, marked 0.935) = **−$39.78 unrealized. Total ≈ −$81.00.**

**Provenance reconciliation (the bot's own logs disagree with the venue — the venue wins).** The maker bot's transcript (`~/.gemini/antigravity-cli/brain/ee45b442-…/.system_generated/logs/transcript_full.jsonl`) records **3 fills**, not 4, and its status dump lists 4 *resting* orders on `KY-A1, RI-Q4, AL-A4, NC-A2` at 18–32c — which is where the "4 fills at 18–32c" framing came from. Only `KY-A1` appears on both lists, and it appears as the *same order id* `7102964c` in both. Resolution: the bot's 3-fill snapshot predates the 17:51:28 KY-A1 fill. **The venue's 4 fills (GA-A2, AR-A578, IA-A1, KY-A1) are correct; the 18–32c prices in the thesis are the resting-order prices of a partly different set of markets, and the "80-89c / 11-14c" drift figures appear nowhere in the bot logs — they are reconstructed here from the tape and they hold.** Also note `RI-Q4, AL-A4, NC-A2` never filled. **`GET /portfolio/orders?status=resting` now returns 0 orders** — despite the log's claim that cancels failed with 410, nothing is resting. Only exposure is KY-A1.

**Settlement date correction.** The bot log states these settle "Nov 2026 — ~15 months locked". The venue says `close_time: 2027-11-02T23:59:00Z`, `expected_expiration_time: 2027-11-03T10:00:00Z`. **It is Nov 2027, ~15 months out.** The month count was right, the year was wrong, and any model keyed on the year is wrong.

**LIP window, confirmed from the program feed** (via bot logs, `lip_programs_full.json`): `start 2026-08-11T14:02:00Z`, `end 2026-08-16T03:59:59.999999Z`, `reward_usd_per_window_per_2sides` of **250.0 (AL-A4) to 285.0 (NC-A2, AK-BM2)**. This matters for §6: the maker subsidy is ~$31/day/side per market, and we earned ~$15–20 of it while losing $81. The subsidy does not cover the adverse selection.

**Fee formula correction (receipt-verified).** The stored spec says `ceil(0.07*count*price*(1-price))`. Observed fees are `ceil(...)` to **1/100 of a cent**, not to whole cents: 277 @ 0.14 → 0.07·277·0.14·0.86 = 2.334556 → billed **2.3346**; 92 @ 0.18 → 0.950544 → billed **0.9506**; 225 @ 0.14 → 1.89630. Update `data/sources/fee_schedule.json` — the whole-cent ceiling would have been a rounding *cost*, and modelling it as such overstates cost by up to 0.99c per fill.

---

## 2. Q2 — Do stale quotes persist near window close? **NO. Census says zero.**

Live census of all 110 open `KXSTATEBALLOTMEASURE` markets at **T-7.5h** (`books_snapshot_T-7h5_20260815T2030Z.json`, 97 with two-sided books):

- markets with takeable YES asks ≤ (last trade − 3c): **0 / 97**
- locked or crossed books (ask ≤ bid): **0 / 97**
- spread: **median 1c, mean 2.3c**

There is no stale-quote inventory to snipe. The books are tight *right now*, 7.5 hours before the window close, with makers still posted. Our bot was not uniquely slow in the sense of leaving quotes far from fair — it was posted at reasonable levels and got **run over**.

The bot's own root-cause note claims **"terminal book evacuation — as the subsidy ends, the other makers pull their resting orders, the book evacuates, our orders become the front-line, and a taker reaches us."** The census contradicts it: at T-7.5h, with the subsidy 7.5 hours from ending, **median spread is 1c and 0/97 books show evacuation.** Makers have not pulled. The evacuation story is a plausible-sounding narrative that the tape does not support, and it is the load-bearing assumption of both the maker post-mortem and this taker thesis.

What the bot logs *do* establish, and what is actually true: rung1 is **retreat-only — it joins the touch and never requotes or cancels** (the competing farmer requotes in 0.08–0.9s, so chasing was deliberately excluded), the kill-switch ("2 fills/7 days suspends placement") **was never wired to fill detection**, and the budget check summed only *resting* collateral, so when $137 converted to locked positions it re-deployed another $199.66 on top. So: our bot was not slow to *price*. It was structurally incapable of *withdrawing*. That is a different bug and it has a different fix (§6.1).

**The thesis mechanism is wrong.** Re-reading the KY-A1 tape (`trades_all_ballot_20260815.json`): at 17:51:28 a single taker order walked the book 0.65 → 0.84 in one second, consuming 300 @ 0.65, 75 @ 0.67, 356 @ 0.68 (our 156 inside that), 100 @ 0.84 — VWAP 0.6875, 831 contracts. Prior print was 0.64 at 10:02. Our 0.68 quote was **1–4c from the last trade, not stale**. The taker's edge was not that our quote was old; it was that they were willing to pay 19c through the book and were right. Price then continued to 0.92 (18:23) and 0.93 (18:38) on further prints. Same structure in AR-A578 (04:25:06: 6,025 contracts all at 0.73, one second) and GA-A2 (04:25:06: 2,090 contracts at 0.79–0.80). **GA-A2 and AR-A578 initiate at the identical second — one actor sweeping a basket of ballot markets simultaneously.**

---

## 3. Q3 — Signal source: orderflow cascade, and the drift FOLLOWS the print

Decisive structural fact: **every market in this series has `close_time` 2027-11-02 and `expected_expiration_time` 2027-11-03.** Nothing resolves for 15 months. A 68→93c move on 2026-08-15 cannot be ballot-outcome news; there is no news event with that information content. It is a **repricing cascade**: a large basket buyer walks multiple books, price gaps, and the new level holds.

Ordering, from the tape: in all four cases the large taker cluster comes **first**, and the drift accumulates **after** it (AR-A578: 0.73 sweep 04:25 → 0.77 at 04:39 → 0.82 at 05:30 → 0.85 at 17:58 → 0.86 at 18:22, monotone over 14h). There is no pre-print drift. So the signal is observable, public, and free — which is also why it is probably not worth much.

---

## 4. The event study — is "follow the elephant" tradeable?

602 same-second same-taker-side trade clusters across 110 markets, Aug 13–15 (`sweep_events_20260815.json`). Entry = **first print of the next cluster** (realistic: you cannot fill inside the sweep), both legs charged taker fee, cents per contract, net:

| trigger | horizon | n | net mean | net med | win | t |
|---|---|---|---|---|---|---|
| taker=YES, ≥1000 ct | +24h | 37 | **+4.12c** | +2.98c | 70% | 3.56 |
| taker=YES, ≥2000 ct | +24h | 26 | +4.68c | +3.47c | 69% | 3.06 |
| taker=YES, ≥500 ct | +24h | 60 | +1.76c | +0.42c | 52% | 2.00 |
| taker=NO, ≥1000 ct | +24h | 18 | **−1.87c** | −2.02c | 22% | −1.65 |
| taker=NO, ≥500 ct | +24h | 24 | −3.14c | −2.07c | 17% | −2.24 |

**The asymmetry is the kill.** If this were genuine sweep-conditional momentum, the NO side would mirror it. It does not — NO-side follow-through is negative at every threshold and horizon. That is the signature of a **series-wide YES drift** over the sample, not a signal.

Confirmed directly. Unconditional gross YES drift, +24h after *any* cluster: **+3.12c** (n=265). After taker-YES ≥1000: **+6.14c**. So:

```
signal excess over baseline  = 6.14 − 3.12 = +3.02c / contract (gross, 24h)
roundtrip taker fee @ p≈0.80 = 0.07·0.80·0.20 + 0.07·0.86·0.14 = 1.96c
                        net  = +1.06c / contract
minus one tick of spread crossing on entry            = −1.00c
                                             ≈ +0.06c / contract
```

**Approximately zero.** The whole complex was launched 2026-08-10/11 and drifted up ~3c/day over the three days of tape. n=265 overlapping observations across 110 correlated markets in one 3-day window is an effective sample of roughly *one*.

Window-close concentration is also absent: taker=YES ≥500ct, exit +24h, bucketed by hours-to-close — T-0..24h **+1.98c mean / −0.74c median** (n=33) vs T-48..96h **+1.15c / +0.42c** (n=26). No terminal-window effect.

---

## 5. Strategy spec (specified so it can be killed, not so it can be funded)

**Name:** `terminal-taker-cascade`. **Status: NOT FUNDED. Paper only.**

- **Universe:** open `KXSTATEBALLOTMEASURE-*`, two-sided book, spread ≤ 3c.
- **Entry trigger:** a same-second taker cluster of **≥1000 contracts, taker_side=YES, walking ≥3 price levels**, detected on `/markets/trades`. Enter on the *next* observed print or the then-current YES ask, whichever is worse. Basket confirmation (≥2 markets swept within the same 5s) is the strongest variant — it is the only one with a mechanism story, and both 04:25:06 events had it.
- **No NO-side variant.** It is negative in-sample and there is no reason to expect otherwise.
- **Sizing:** hard $50/market (`kalshi.exposure.caps`), $100 total across the lane. At p=0.80 that is **62 contracts**; at p=0.68, 73 contracts. Max 2 concurrent markets.
- **Fee math at size:** 62 ct @ 0.80 entry = $0.694; 62 ct @ 0.86 exit = $0.522. **Roundtrip $1.22 on $49.60 = 2.46%.** The signal must clear 2.5% gross before it earns anything. At p=0.50 the roundtrip would be $1.09+$1.09 = 4.4% — **never trade this near 50c**; the fee curve peaks there and the whole edge is ~3c.
- **Exit:** taker exit at **+24h**, or on the first opposing ≥1000ct cluster, whichever first. **Do not hold to settlement** — Nov-2027 resolution locks $50 for 15 months for a 27%-if-right payoff that is unhedgeable and uncapped in drawdown. Flipping is the only defensible exit.
- **Expected value, honest:** +0.06c/contract → **$0.04 per market per event**. At the observed ~86 qualifying events/week across the complex, capped to 2 concurrent, ~20 executable/week → **~$0.80/week, standard deviation ~$4/event.** The strategy is indistinguishable from zero and the variance dominates.

---

## 6. What is actually worth investigating instead

The $58.69 was earned by the *initiator*, not the follower. Three defensible follow-ups, in order of expected value:

1. **Stop bleeding as a maker.** Our −$81 came from resting NO into a one-way basket buyer with no adverse-selection guard. A rule as crude as "cancel all quotes in a market on any same-second taker cluster ≥500ct on the opposing side, and do not requote for 60min" would have avoided the IA-A1 (14:09) and KY-A1 (17:51) fills entirely — both came after that market had already been swept earlier the same day. That is a free −$50 avoided with no new capital. Prerequisite: rung1 is **retreat-only and has no in-window cancel path at all**, and its cancel attempts in the incident errored 410 (wrong HTTP method — `cancel_order` uses `DELETE /portfolio/orders/{id}`; verify against the live API before relying on it). Wiring the kill-switch to fill detection and adding `if hours_to_window_end < 24: CANCEL_ALL` are both prerequisites to *any* further maker deployment, and are worth more than this entire taker lane.
2. **The basket signature.** GA-A2 and AR-A578 swept in the same second. If one actor systematically sweeps N ballot markets simultaneously, the *un-swept* members of the basket are the trade — not the swept ones. Untestable on 3 days of tape; needs 4+ weeks.
3. **Post-window-close spread widening.** If makers evacuate at 03:59Z, the spread should widen measurably. That is a maker opportunity (quote wide into the vacuum, zero fee), not a taker one. Tonight's capture (§7) measures it.

---

## 7. PREREGISTERED KILL TEST

**Locked before observation. If the primary gate fails, the strategy is dead and does not get a second look.**

### 7a. Tonight's capture (window close 2026-08-16T03:59Z). Read-only, manual, no daemons.

Run this at **five** timestamps: `T-6h (21:59Z)`, `T-2h (01:59Z)`, `T-15m (03:44Z)`, `T+15m (04:14Z)`, `T+2h (05:59Z)`.

At each timestamp, for **all** open `KXSTATEBALLOTMEASURE-*`:
1. `GET /trade-api/v2/markets?series_ticker=KXSTATEBALLOTMEASURE&status=open&limit=200` → save whole payload.
2. `GET /trade-api/v2/markets/{ticker}/orderbook` for every ticker → save full `orderbook_fp` ladders (not just top of book — the depth profile is the measurement).
3. `GET /trade-api/v2/markets/trades?ticker={ticker}&limit=1000` (paginate) → save full tape.

Write to `/Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research/books_snapshot_{LABEL}_{ISO}.json` using the same schema as the already-captured `books_snapshot_T-7h5_20260815T2030Z.json` (baseline, T-7.5h, in hand).

Derive per snapshot: median spread; total resting depth within 5c of mid; count of markets with zero depth on a side; count of takeable asks ≤ (last − 3c).

### 7b. Primary gate (kills or advances the taker strategy)

Over **two** consecutive window closes (2026-08-16 and 2026-08-23), paper-log every trigger firing per §5 (≥1000ct, taker=YES, ≥3 levels), entry at the *quoted ask at detection time* — not the sweep VWAP, not the next print — and exit at +24h at the then-quoted bid, both legs charged `ceil(0.07·c·p·(1−p))` to 1/100c.

- **PASS** requires: **n ≥ 25 trades**, **net mean ≥ +2.0c/contract**, **AND net mean ≥ +2.0c above the matched baseline** (same entry/exit timestamps, same markets, triggered by *any* cluster ≥100ct rather than the ≥1000 YES filter). The baseline arm is mandatory — without it the result is unreadable, as §4 proves.
- **KILL** on any of: n < 25; net mean < +2.0c; excess over baseline < +2.0c; or the taker=NO arm (logged in parallel, never traded) remaining negative while YES is positive — that asymmetry means you are still measuring drift.

Prediction on record, from §4: **this fails.** Expected excess ≈ +0.1c against a required +2.0c.

### 7c. Secondary gate (the maker-defense rule, §6.1 — cheap and likely to pay)

Replay our own fills against the tape with the guard: "cancel and stand down 60min after any same-second opposing cluster ≥500ct in that market." **PASS if it avoids ≥60% of adverse-fill loss across 4+ window closes.** On this window it avoids 2 of 4 fills and −$50.48 of −$81.00 = 62%, but n=1 window — that number is a hypothesis, not a result.

### 7d. Tonight's specific falsifiable prediction (free, resolves in 9h)

From the T-7.5h census: **0/97 markets have takeable stale asks.** If the stale-quote thesis is right, that count should rise materially as makers evacuate. **Prediction: at T-15m the count is still ≤ 2/97.** If it comes back ≥ 10/97, the stale-quote thesis is resurrected and §5 should be rewritten around sniping rather than following.

---

## 8. Artifacts

- `/Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research/fills_all_20260815.json` — 1540 account fills, full history
- `/Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research/trades_all_ballot_20260815.json` — 1832 public trades, 110 markets
- `/Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research/sweep_events_20260815.json` — 602 same-second taker clusters with forward prices
- `/Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research/books_snapshot_T-7h5_20260815T2030Z.json` — full ladders, all 110 markets, T-7.5h baseline

**Biggest unknown:** everything here rests on **3 days of tape in a series that opened 2026-08-10**, one window close, 110 markets that move together. The +3.12c/day unconditional drift is the entire story and it has an effective sample size of about one. No conclusion in §4 survives a second week of data being different.
