# THE IDEATION ORGAN — standing spec (Claude x Gemini)

**Status:** live. **Instituted:** 2026-08-16. **Owner lane:** senate/kalshi research.

This is the reusable framework. Every fresh-ideation burst runs under it. A burst that
skips any of §2's mandatory steps is **invalid and must not be cited as a receipt.**

---

## 0. Why this exists

Ideation without a graveyard re-proposes dead ideas. Ideation with one adversary
converges on that adversary's blind spot. This organ enforces both fixes: a
**deduplication index** every idea must be cited against, and a **second independent
model** (Gemini) that generates its own ideas from the same fuel and cross-examines ours.

The organ's output is not ideas. It is **verdicts with numbers** — most of them deaths.
A burst that produces four survivors is a failed burst; a burst that produces one
survivor and four new graves is a good one.

---

## 1. GRAVEYARD INDEX

**Rule: no burst may propose an idea that maps to a grave below without explicitly
citing the grave and stating what makes the new idea distinct.** The citation is
mandatory and appears in the burst report.

Format: `idea | killing number | date`

### 1.1 Recent domain graves (senate/domains/kalshi/data/research, 2026-08-15/16)

| # | Idea | Killing number | Date |
|---|---|---|---|
| D1 | Terminal-taker "follow the elephant" sweep-following | excess over baseline ~+0.1c vs +2.0c required; 0/97 markets with takeable stale asks | 2026-08-15 |
| D2 | Stale-quote sniping at window close | 0/97 at T-7.5h; 0 takeable stale asks and 0 locked books in 4,834 snapshots at T-4h | 2026-08-16 |
| D3 | TEMP hourly 1c-lottery maker seat | 1 win in 200 fills = 0.50% vs 1.00% breakeven | 2026-08-15 |
| D4 | TEMP hourly in-band ($50-capped, 15–85c) maker seat | −$0.0741 per posted contract | 2026-08-15 |
| D5 | KXFEDFUNDSYEAR LIP seat | −$0.0008/posted ct/window rival-adjusted; 0.002x ballot per ct-hr; n=210, 174 fills | 2026-08-15 |
| D6 | KXUSCPIYEAR LIP seat | −$0.0012/ct; +$0.0033 [−0.0052,+0.0118] at ceiling, CI includes zero | 2026-08-15 |
| D7 | KXNOMGDPGROWTH LIP seat | −$0.0047/ct; rival at touch 932 ≈ target_size 1,000; 54.5% of family never trades | 2026-08-15 |
| D8 | GPU-class LIP seats (H200/H100/B200/RTX5090/A100) | +$0.0098/ct best = 0.015x ballot per contract-hour — positive but not worth capital | 2026-08-15 |
| D9 | KXROLEATEVENTCOACHELLA LIP seat | −$0.0371/ct; rival at touch 1,888 = 1.9x target_size; only 13/115 quotable in-band | 2026-08-15 |
| D10 | KXYTVIEWSW LIP seat | −$0.0073 at ceiling, −$0.0521 rival-adjusted; P(fill) 0.909 × settled loss $0.118; our side ITM 18% (9/50) | 2026-08-15 |
| D11 | Zero-fee maker-in/maker-out round-trip scalp | second leg fills only adversely, −8.4c/fill in the wings | 2026-08-15 |
| D12 | Maker-only MECE dutch book (free hedge legs) | BTC 28-bin ladder SUM_ASK 103.90c / bid 94.90c; 0 executable | 2026-08-15 |
| D13 | Free requote / join-and-chase vs adverse selection | books frozen 1–5h then gap 6–25 ticks in one 60s bar — no drift to chase | 2026-08-15 |
| D14 | Deep-cheap resting bids (<15c) | 10,573 ct at avg 3.7c, win rate **0.000**, −$404.30; 20–30c band −19.1c/ct | 2026-08-15 |
| D15 | Fee/rebate stacking, VIP maker, APY-on-escrow | perps maker dies on 417×/day turnover; program stacking 0/3,599; interest <$1/day | 2026-08-15 |
| D16 | Quote wider on the cheap side, sized by fee curvature | same n problem as H1; strictly dominated by not quoting the wings | 2026-08-15 |
| D17 | Programs feed as early warning of next week's LIP families | 82/82 future programs start within 28.2h; 100% are 4 toxic 15-min commodity families | 2026-08-15 |
| D18 | `initialized`-status markets as a pre-open lane | mechanism real (10/10 fetchable) but only pre-visible inventory is the toxic 15-min set | 2026-08-15 |
| D19 | `discount_factor_bps` variation across families | == 5000 for **100% of 3,935** live programs; zero variance exists | 2026-08-15 |
| D20 | LIP on scheduled-print families (CPI/PPI/FEDFUNDS) | KXCPICOREHEAD $0.0541/ct/day < ballot $0.0622; macro P_s 1.7–1.8 vs 3.25 analytic floor | 2026-08-15 |
| D21 | FEDFUNDS/FOMC path as a taker door | CME FedWatch public and free; Kalshi calibrated everywhere except post-streak open | 2026-08-15 |
| D22 | Weather-data-driven taker (NWS obs pipeline) | strictly dominated by B1, which extracts the same info from the tape for $0 | 2026-08-15 |
| D23 | 45–55c band as an alpha claim | fill-level +0.007, SE 0.052, n=91; 16/38 markets profitable; 67% of $ is one series on 13 fills | 2026-08-15 |
| D24 | Stop-loss / exit engineering on filled seats | every stop-loss worse than holding; gap is instantaneous, no exit exists between entry and loss | 2026-08-15 |
| D25 | evacuation-eject gate (rival depth drops >X% in N cycles) | 0/4 adverse fills caught at a 1-alarm/24-seat-h budget; 58 alarms/24h if tuned to catch | 2026-08-15 |
| D26 | drift-eject gate (mid moves ≥T ticks against us) | 0/4 at T≥2 ticks; ejects 2 seats while catching nothing; $12.80 cost | 2026-08-15 |
| D27 | share-spike gate (our share jumps, rivals left) | 0/4, and **wrong sign** — share FELL or was flat before all 4 fills | 2026-08-15 |
| D28 | Fundamentals / base-rate gate on ballot seats | gate is **anti-predictive**; P1 gap-ranking FAIL prior-independently, P3 fill-order sign inverted | 2026-08-15 |
| D29 | Inverted sweep bait (rest 6–25 ticks below pre-sweep touch) | fill probability <1% per 6h; collides with our own compiled post-sweep re-entry ban | 2026-08-15 |
| D30 | Deep-book churn as an early-warning signal for touch moves | P(touch moves \| deep churn)=0.0122 (n=983) vs 0.0140 (n=3,631) with none; **z=−0.46** | 2026-08-16 |
| D31 | Depth-bleed share timing (seat late as rivals decay) | rival depth decays only −8.2% over 3.7h ⇒ share improves ≤8.9% relative — noise | 2026-08-16 |
| D32 | Thin-rival in-band LIP pocket (ballot, rival touch ≤50ct) | P(fill/day)≈1.00 vs 0.215 kill threshold; thin mkts trade 16.50/mkt vs 16.67 for thick — identical flow. Net **−$0.157/ct/day** | 2026-08-16 |
| D33 | Post one tick behind the touch to filter indiscriminate takers | 0 fills in 104.3 seat-h at touch vs 4 fills in 48.8 seat-h behind; df=5000 halves the subsidy too | 2026-08-16 |
| D34 | End-of-window taker sweep on liquidity decay | decay is −8.2%/3.7h smooth and monotone — no cost cliff to time | 2026-08-16 |
| D35 | Restore the 1c spread after a transient widening | touch re-taken in ~1s; our observation interval is 300s | 2026-08-16 |

### 1.2 Archive graves (archive/enchiridion_legacy/work)

| # | Idea | Killing number | Date |
|---|---|---|---|
| A1 | Deribit cross-venue fair-value gate | EV −0.54c/ct, t=−4.21, 28,881 rows/662 events | 2026-08-06 |
| A2 | Sell cheap commodity wings at executable prices | mispricing 0.24c vs 1–4c spread; t ∈ [−2.37,+0.94], 703,544 snapshots | 2026-08-06 |
| A3 | Lead ≥2h wing cell | +1.1 to +8.5c at t=+34..44 with realized 0.00% on ~25 events = sample collapse | 2026-08-06 |
| A4 | Queue protection via crowded tick-floor depth | level-loss only 29%→18%/h at 5,000+ct (n=1,298) over 698,506 ticker-hours | 2026-08-06 |
| A5 | Censored queue test (level consumed at unchanged price) | 0.0% in every bucket, n=295,491 — conditioned away the event | 2026-08-06 |
| A6 | WTI hourly 1–5c wing sell, fully deployed | P(ruin before Sep 1) ≈83%; one YES = −$991 = whole bank | 2026-08-06 |
| A7 | WTI wing sell at f=3%/cycle | −48% on a bad day; 3-day cluster leaves 14% of bank | 2026-08-06 |
| A8 | t=+31.9 significance claim on the WTI survivor | 0 of 439 markets settled YES; rule-of-three bound 0.683%, EV +0.87c | 2026-08-06 |
| A9 | Crypto 15M wing trade | SELL −11.22c and BUY −5.96c in the same 40–60c band = 8.5c half-spread | 2026-08-06 |
| A10 | Crypto 15M implied-vol ratio edge | ratio 0.06–0.15 (7–16x realized) = decode defect; n collapsed to 29–94 rows | 2026-08-06 |
| A11 | KXWTI15M / KXBTC15M ladder trade | 1.0 market per event, 0/1 wings — no ladder exists | 2026-08-06 |
| A12 | Commodity dailies as a throughput venue | 1 cycle/day = 0.09%/day of bank | 2026-08-06 |
| A13 | KXTEMPCHIH / KXTEMPDCH hourlies | median spread 63c / 93c, 0 wings, 20–40% two-sided | 2026-08-06 |
| A14 | STREAK engine as sized | edge +1.0pp SE 13.5pp; +$1.20 on $47.58 over 6 days; 21% maker fill on 15s quote | 2026-07-28 |
| A15 | CPI-book maker resting (inflation scalping) | **100% of fills adverse**; structural | 2026-07-28 |
| A16 | Index spike-fade / 5-min reversal (DXY/INX/NDQ) | INX maker markout −10.91c t=−4.58 at \|move\|≥4c; 150 markets, 2,900 spikes | 2026-07-28 |
| A17 | Two-sided spread capture by resting both sides | ex-top-3 n=27, mean −$0.679, t=−2.24; 72% of inventory never nets | 2026-07-28 |
| A18 | Rung price floor as a policy knob | P&L swings $32 non-monotone across 0–30c; best 15c = +$1.97/day vs sd $22.15/day | 2026-07-28 |
| A19 | VOLBOOK metals dailies scale-up | 10/10 wins has p=0.204 under fair pricing; effective n=2 session-days | 2026-07-28 |
| A20 | Honeymoon / first-mover fraction on fresh windows | farmer preseated at/above target in **95% of 764 windows** (97% single clip ≥ target) | 2026-08-14 |
| A21 | MLB fee_multiplier 1→0.5 resurrection | best FWER 0.808 vs bar; pooled cell t=+0.18 vs 95% MDE 1.90c | 2026-08-14 |
| A22 | Exit-beats-hold (+4.120 c/ct) | band+family-matched frac≤0 = 0.1573 vs pre-specified 0.0025 | 2026-08-14 |
| A23 | Dead-book maker toll filter (−10.40 c/ct) | frac≤0 = 0.1867; effect carried by one band (−67.34 c/ct on 5 clusters) | 2026-08-14 |
| A24 | KXHIGH realized-temp vantage | book pinned-correct 98% by 18:00 local, 0 pinned-wrong (N=504) ⇒ ~$0/day | 2026-08-12 |
| A25 | Kalshi↔Polymarket cross-venue basis | 0/16 matched events net-positive; fees 4–5x any basis | 2026-08-12 |
| A26 | Naive top-rate LIP seats | **15/16 top seats settled NO** (the 1–4c wing trap) | 2026-08-12 |
| A27 | Turn-on-gated-market LIP | added 1c depth scores ≈0 | 2026-08-12 |
| A28 | Exhaustive-ladder dutch book | $8.50 locked board-wide with 15-month lockup = $0.02/day | 2026-08-12 |
| A29 | Nested-strike monotonicity arbitrage | **0 violations in 34,614 pairs** | 2026-08-12 |
| A30 | Long-tail wide-spread market making | T20 cricket makers lose p≈3e−5; MLB maker +1.19c fails Bonferroni ×8 | 2026-08-12 |
| A31 | LIP durable-family seats | competitors hold 25–30% share; KXVOTEPRIMARY $0.79/day + ruin bound | 2026-08-12 |
| A32 | Spotify streams settlement | $3.3M market settled minutes before 523k artificial streams stripped | 2026-08-12 |
| A33 | Drought series | $0.77/day capacity cap | 2026-08-12 |
| A34 | KXHURCAT recon-gap | perfect-oracle ceiling $22.92/day; 0/7 crossings had recon airborne | 2026-08-12 |
| A35 | KXTSAW TSA-daily arithmetic vantage | info real but taker gap $0.00 median; realistic $0.30/day | 2026-08-12 |
| A36 | AAAGAS county-level | no state/county daily series exists (1,962-series enumeration) | 2026-08-12 |
| A37 | LPGA dutch-book / resting probe | field sum-of-best-bids 6.2–8.0x fair; touch 0.01ct over a 10k 0.1c wall | 2026-08-12 |
| A38 | Golf dutch books / temp partitions (non-LIP) | PGA −0.03..−0.50%, no crossing | 2026-08-12 |
| A39 | Apify actor-publishing lane | median entrant $0 forever (93.2% below $20 floor); ≥50-day lag | 2026-08-12 |
| A40 | PolyUS MVE parlay engine | 23,760 ephemeral tickers/day, ~17 prints each, empty books | 2026-08-12 |
| A41 | PolyUS maker-rebate on durable books | trades once/day (13–43h since last trade, 0.0 BBO repricings/day) | 2026-08-12 |
| A42 | Tennis maker cells | 0 of 22 cells significant; 1c edge needs 589 day-clusters vs 67–75d tape purge | 2026-08-12 |
| A43 | Tennis "exclude final 60 min" filter | +13.15 c/ct = pure lookahead (duration is outcome-correlated) | 2026-08-12 |
| A44 | POLITICS_HIGH LIP | net negative in all configs; one sweep costs 15 days of LIP earn | 2026-08-12 |
| A45 | 10–19c maker-YES commodity cell | −5.75 c/ct, killed on sign | 2026-08-12 |
| A46 | 99c maker-NO | avg 99.63c ⇒ max gain 0.37c; CP-95 upper −0.83 c/ct | 2026-08-12 |
| A47 | 90–94c cell | 64x ct-vs-eq gap (size trap) + June-drawdown artifact | 2026-08-12 |
| A48 | Other US venues as maker subsidies / DFS / crypto rebates | all below bar; bank-bonus churn $4/day | 2026-08-12 |
| A49 | Settlement-lag discount | flat 1.94c tick floor, convexity excluded, N=5,304 | 2026-08-12 |
| A50 | Penny-jumping obligated quotes | their duty is tightness; 1c spreads appear wherever flow exists | 2026-08-12 |
| A51 | Resting alongside the obligated quoter | −2.2 to −3.9 c/ct, survives Bonferroni; $2,137/day gross bleed cluster-wide | 2026-08-12 |
| A52 | 15M top-tick maker | through-sweeps 92.5% of first fills (63/65 losses); −$726/day at $2k | 2026-08-12 |
| A53 | KXYTVIEWS vantage | 194/198 candle-hours ask=100; 0 ct ever traded the favoured side inside T-6h | 2026-08-12 |
| A54 | PolyUS scaling at $2k | best non-sports 2-way $20.5/day, below bar; 98.7% of notional is sports | 2026-08-12 |
| A55 | KXHEADLINE | $15.4k two-sided collateral for a $351/day pool; ceiling $23/day at 100% share | 2026-08-12 |
| A56 | Kalshi LIP at our capital, as a deployment | K_total 0.06–0.135 vs needed; dead pre-registration | 2026-08-13 |
| A57 | Rotating-seat column | dead unless share ≥8–14% sustainable; $1/day floor bites at 3.22% vs actual 3.26% | 2026-08-13 |
| A58 | Ornn siblings / hourly-index upside | 400 on all sibling paths; $1.07/mkt/day as seats | 2026-08-13 |
| A59 | Sunday UST window | no Sunday program exists; $20 pool dying at the Saturday cliff | 2026-08-13 |
| A60 | 0-maker dose-response ladder | all events now carry 5–13 makers — the $50/day branch is void | 2026-08-13 |
| A61 | MLB 99c maker/taker gates | taker 3/15 games vs ≥5 bar; maker queue-ahead median 355,848 ct vs 100k bar | 2026-08-13 |
| A62 | Gemini↔Kalshi cross-listing | perfect-oracle $3.91/day on $44k locked ~80 days; at $2k = $0.21/day, 120x under bar | 2026-08-13 |
| A63 | A1 index-displacement fade | sign agreement 0.513 CI[0.434,0.593] | 2026-08-13 |
| A64 | A2 hourly-index evidence clock | books absorb the print at no lag | 2026-08-13 |
| A65 | B1 incumbent-withdrawal entry | fills are 0.21% of depletion; hole is ambient 64.3% of time CI[55.0,73.6] | 2026-08-13 |
| A66 | Net-change-after-entry + matched-control K estimators | placebo showed pre-entry decline; controls produced absurd K=30–400 | 2026-08-13 |
| A67 | Funding carry | $0.30/day/$1k ⇒ $217k needed to clear bar | 2026-08-13 |
| A68 | Expiry pinning ("gamma") | round-number microstructure only, no gamma | 2026-08-13 |
| A69 | Settlement locks | 0 executable; pairs sum to 200.00 in 94.4% | 2026-08-13 |
| A70 | Program stacking | 0 of 3,599 | 2026-08-13 |
| A71 | VIP × 99c | filings cap eligible volume to $.03–$.97 — a 99c fill earns $0 VIP | 2026-08-13 |
| A72 | Front-running the obligated quoter's touch | touch re-taken in ~1s; size buys share only 4.2%→18% | 2026-08-13 |
| A73 | "Flow without subsidy = free spread" | captured maker round-trip −1.00c median in all six top-volume families (130k pairs) | 2026-08-13 |
| A74 | T1' uncovered-family seats (FEDFUNDSYEAR/USCPIYEAR) | P_s $1.79/day/side — floor bites below 55.9% share at any K | 2026-08-13 |
| A75 | Over-revert after sweeps | corrected +1.70c gross → ≈0.00c net; sign flips H30/H60/H300; −$25/day realized | 2026-08-13 |
| A76 | lipband "empty book = no competitor" | 249,433/249,433 records empty = parse defect; all 14 days void | 2026-08-13 |
| A77 | Expiry evacuation (take the surviving quote at T−5m) | **−45.71 c/ct net, cluster t=−17.94, 16/16 days negative** | 2026-08-13 |
| A78 | Pre-close freeze | population does not exist: genuine frozen >20m settled **N=1** | 2026-08-13 |
| A79 | SCALP shadow3/shadow4 deploy | refusal_dominates rate:book_poll 0.564 then 0.95 vs 0.50 limit; **0 orders lifetime** | 2026-08-13/14 |
| A80 | GPU A3 settlement-markout vantage | incremental PnL vs public-info arm = **$0.00** at T−24h | 2026-08-15 |
| A81 | GPU A4 direction-from-drift | 1/2 replication; rank-ordering **INVERTED** (movers posted smallest book moves) | 2026-08-15 |
| A82 | WTIH kill-test candidates 1 & 2 | neither branch fires — not executable / no usable control (unresolved, not confirmed) | 2026-08-13 |
| A83 | Bug-bounty / venue-defect lane (Kalshi + Polymarket) | submissions filed, no realized payout at time of sealing | 2026-08-12 |
| A84 | Sole-maker LIP attribution in zero-trade markets | not derivable from any public endpoint; canary risk on the 1-contract rival books | 2026-08-15 |
| A85 | Family calendar hypothesis (macro YEAR families) | FAILS — the three macro YEAR families are inert | 2026-08-15 |

**Graveyard size at instantiation: 120 graves (35 domain + 85 archive).**

### 1.3 Recurring kill mechanisms (the structural reasons things die here)

1. **Edge lives inside the spread.** Measured mispricings run 0.2–3c gross against 1–4c
   spreads (8.5c half-spreads on crypto 15M). Real but not takeable.
2. **Adverse selection / no uninformed counterparty.** Where information is real, the book
   is pinned or evacuated — the winning side simply is not offered.
3. **Colonization and floors on the subsidy side.** Farmers preseat at target, share
   decays, and the $1/day per-market floor censors sub-scale seats; LIP K collapses 7–14x.
4. **Statistical artifacts.** Zero-event cells producing huge ratios, sample-collapse cells
   that "never lose", lookahead filters, composition/price-band mixtures, and multiplicity
   that no candidate clears. **This one bites the organ itself — see §2.4.**
5. **Capacity and capital arithmetic.** Correlated tails cap sizing near 1% of bank, and
   most survivors die on the plain $/day ceiling long before execution matters.

---

## 2. PROTOCOL — the mandatory burst sequence

### 2.1 Step 1 — Claude generates N against the graveyard
N = 4 (default). Each idea ships, in the report:
- the mechanism, and **the specific measured number from the fuel that supports it**;
- **a graveyard citation**: which graves it is nearest to, and the one sentence that makes
  it distinct. *No citation ⇒ the idea is discarded unexamined.*
- a preregistered killing number **and threshold**, written before the test is run.

### 2.2 Step 2 — Gemini generates its own N independently
Invoked as `~/.nvm/versions/node/v20.9.0/bin/gemini -p "..."`. The prompt supplies the
**same fuel and the same graveyard**, and asks for N fresh ideas in the same
IDEA/MECHANISM/KILLING NUMBER/COST shape, plus a ranking and a single funding pick.
Gemini must not see Claude's ideas in this step — independence is the point.

### 2.3 Step 3 — Cross-examination, **minimum 2 rounds**
- **Round 1:** Claude attacks each Gemini idea, citing graves by number. Gemini attacks
  each Claude idea and must state a killing number with a threshold.
- **Round 2:** Claude runs the test the adversary preregistered — on data, not rhetoric —
  and reports the result even when it goes against Claude. Gemini concedes or rebuts.
- **Round 3+ (as needed):** until every idea has a verdict.
- Concessions are recorded by name. A round where neither side concedes anything is a sign
  the exchange was too polite and must be re-run harder.

### 2.4 Step 4 — Power check on every kill and every survivor
Because kill mechanism #4 bites the organ itself: **any verdict resting on fewer than ~10
events must be labelled UNDERPOWERED and may not be reported as a kill.** A ratio computed
on n=2 is not a result. This rule exists because it was needed in the first burst.

### 2.5 Step 5 — Verdicts and kill tests
Every idea ends as exactly one of:
- **TRADE-shaped** — measured, positive, and executable as stated;
- **CONDITIONAL(gate: …)** — the gate is a named measurement with a numeric threshold;
- **DEAD(number)** — the killing number, in the verdict line.

**Every survivor ships its kill test cost in $ and minutes.** Survivors without a costed
kill test are downgraded to DEAD.

### 2.6 The enforcement clause
> **A burst report that does not contain the verbatim-condensed Claude↔Gemini exchange —
> both sides' ideas, both sides' attacks, and the named concessions — is INVALID and must
> not be cited as a receipt by any downstream document.**

---

## 3. CADENCE + BUDGET

**Fires on data arrival:**
- a window close completes,
- LIP credit receipts land,
- new fills arrive,
- a new capture completes (Mac or VPS).

**Otherwise:** maximum **1 burst per idle day**. Idle days do not need bursts; the organ is
fed by data, not by the calendar.

**Effort tiers:**
| Work | Agent | Cap |
|---|---|---|
| Scans, on-disk kill tests, graveyard refresh | `researcher-med` | ~60k |
| Full bursts (generation + cross-exam + tests) | `researcher` | **~150k per burst** |

**Hard constraints:** read-only; **no orders**; no daemons; no capital committed by a burst.
A burst may only *recommend* a costed test.

**Ledger:** every burst appends one line to §4 below.

---

## 4. LEDGER

| Date | Burst | Fuel | Ideas (C/G) | Survivors | New graves | Graveyard size after | Tokens |
|---|---|---|---|---|---|---|---|
| 2026-08-16 | `ideation-fresh-20260816.md` | 6 research .md dated 20260815; Mac+VPS terminal captures (4,834 snapshots, 110 mkts, 3.7h) | 4 / 4 | **1** (depth-conditional seat screen) | 6 | **120** | ~115k |

---

## 5. REPRODUCTION

Graveyard sources:
- `/Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research/*.md`
- `/Users/ryanwhitehead/Documents/senate/archive/enchiridion_legacy/work/`
- sealed autoseat reg chain killed gates: `fill-forensics-20260815.md` §0 (a/b/c)

Gemini invocation: `~/.nvm/versions/node/v20.9.0/bin/gemini -p "$(cat prompt.txt)"`
