# IDEATOR LANE — MUSK archetype: what is NEW on the venue (census refresh)
Date: 2026-08-16 04:10Z · Organ: `ideation-organ-SPEC.md` · Graveyard at start: **122**
Fuel: built fresh, read-only, ~1 req/s. Nothing on disk was reused as a finding — only as a diff baseline.

## 0. FUEL — the census I built

**Series/fee layer.** 13,008 series enumerated across all 18 categories (the 5-category sweep
misses `Elections`/`Mentions`/`Climate and Weather`/`Commodities`/`Social`/`Exotics`/`Education`
— 2,462 series, 19% of the board). Diff vs the 2026-08-15 pull: **0 new series, 0 fee_multiplier
changes, 0 fee_type changes**, 21 Elections series removed. Fee landscape: 12,851 at
`quadratic`/`fee_multiplier=1`; **129 series `quadratic_with_maker_fees`** (makers PAY: 106 Sports,
10 Economics, 7 Entertainment, 3 Financials, 2 Crypto, 1 SciTech); 19 at `0.5` (all MLB, grave A21);
**9 at `fee_multiplier=0`** (KXBTCY, KXETHY, KXGDPYEAR, KXLAYOFFSYINFO, KXDOED, KXEXPAND,
KXGREENLAND, KXGAMBLINGREPEAL, KXPAHLAVIHEAD). `last_updated_ts` histogram 08-12:605, 08-13:419,
**08-14:1189**, 08-15:17, 08-16:2 — the 08-14 batch changed no fee field.

**Subsidy layer.** 141,058 historical programs + 8,000 fresh (08-06→08-17). Units confirmed:
`period_reward` is 1e-4 USD; ceiling per posted contract per period = `period_reward/target_size_fp`.
- **161 families first-subsidized on/after 08-10** — brand families (`*POS`), credit-card-spend
  (`*CC`), billionaire net worth (`*NW`), app downloads (`*APP`), AI-share, KXDOTA2,
  KXSTATEBALLOTMEASURE. All price at a uniform new_event tariff, $0.045–$0.058/ct/day raw.
- **Structural cut:** KXGOLD15M/KXSILVER15M/KXWTI15M went **96 subsidized windows/day
  (08-11..08-14) → 16 (08-15) → 8 (08-16) → 16 (08-17)**, a 6x cut. KXBTC15M/KXETH15M subsidy
  ended entirely 2026-05-12.
- **Added in the 13h since the last pull:** KXTEMPMIAH (50 programs), KXH100MON/KXB200MON/
  KXRTX5090MON (~20 each; GPU monthly `period_reward` 150,000/250,000 → **600,000**, 4x).
- Wind-down ramps to zero: KXDIESELD 252k→210k→168k→126k→84k→42k; KXUST2AD/5AD/10AD/30AD
  150k→120k→90k→30k; KXYTTOPVIDEOG2D/KXYTDAILYTOPVIDEOG/KXTRUEV 180k→…→20k; KXINXHUD/KXNDQHUD.
- Raw rate raises A(07-25..08-05)→B(08-10..08-17): KXHIMS **9.49x**, KXMUSKNW 5.93x, KXCAVA 3.14x.
  Cuts: KXACTBLUETOP 0.10x, KXTRUMPMENTION 0.18x, **KXUSCPIYEAR 0.32x, KXFEDFUNDSYEAR 0.34x**
  (confirms the brief's "FEDFUNDS pools cut 2.4x"; measured here 2.9x).

**THE CENSUS'S ONE REAL FINDING — the raises are a period-length artifact.**
I re-derived every family's rate **duty-cycle-corrected**: total ceiling-$ delivered per posted
contract inside a fixed 7-calendar-day window (08-09..08-16), ÷7, ÷market count.

| family | raw $/ct/day | **duty-corrected $/ct/cal-day** | duty | overstatement |
|---|---|---|---|---|
| KXHIMS | 0.2246 | **0.0163** | 0.27 | **13.8x** |
| KXAAAGASD | 0.1502 | **0.0143** | 0.10 | 10.5x |
| KXCAVA | 0.0692 | 0.0143 | 0.28 | 4.8x |
| KXMUSKNW | 0.0950 | 0.0107 | 0.11 | 8.9x |
| KXTEMPMIAH | 1.9200 | **0.0114** | 0.01 | **168x** |
| KXGOLD15M | 6.4000 | **0.0095** | 0.00 | **674x** |
| KXSTATEBALLOTMEASURE (ref) | 0.0546 | **0.0306** | 0.65 | 1.8x |

KXHIMS's live program pays $0.145/ct over a **4.997-day** period (08-11T04:02→08-16T03:59) =
$0.029/ct/day. The $0.2246 came from a *different*, 0.445-day batch on 08-10 that does not repeat.
**Every family on the raises list is this artifact.** Kill mechanism #4 (SPEC §1.3) biting the organ
itself, exactly as §2.4 warns.

**Second finding — `target_size_fp` varies and has never been checked.** Distribution over 8,000
recent programs: **1000 → 5,841 · 300 → 2,116 · 2500 → 32 · 5000 → 7 · 10000 → 4**. For an identical
pool, `target_size=300` gives **3.33x** the per-posted-contract ceiling. Grave D19 established
`discount_factor_bps` has zero variance (==5000, 100% of 3,935); nobody checked the denominator.

**Live orderbooks pulled minutes ago** (note: the response key is `orderbook_fp` with
`yes_dollars`/`no_dollars` in decimal dollars — parsing `orderbook.yes` returns empty for every
market and reproduces grave **A76** exactly):

| market | bid/ask | spread | touch depth (bid/ask) | target |
|---|---|---|---|---|
| KXEOWEEK-26AUG22-0/1/2 | 65/69, 34/37, 15/19 | 3–4c | **1/2, 60/2, 1/2** | 300 |
| KXEOWEEK-26AUG15-1/2 | 4/5, 2/3 | 1c | 964/2302, 1607/1569 | 300 |
| KXEOWEEK-26AUG08-1/2 | 99/— | — | 45,343 / 45,076 | 300 |
| KXTRUMPTIME-26AUG22-H1..H5 | 8c spread on all 5 | 8c | **200/201 on every market** | 1000 |
| KXGENERICBALLOTVOTEHUB-26AUG21-T6.8 | 40/41 | 1c | 150/434 | 300 |
| KXHIMS-26NOVSUBS ×7 | 5 at 1c spread | 1c | 1,147–2,466 / 350–2,352 | 1000 |
| KXAAAGASD ×14 | 8 degenerate | — | 1 in-band: 73/76 at depth 10/9 | 1000 |

---

## 1. THE TEN — verdicts

| # | Idea (WHO is the fish) | Nearest grave — distinction | Verdict |
|---|---|---|---|
| M1 | **Chase the pool raises** (HIMS 9.5x / MUSKNW 5.9x / CAVA 3.1x). Fish: farmers ranking families on raw `period_reward`. | D5–D10 (per-family LIP seats) — distinct because it trades the *change* not the level | **DEAD(0.0163 vs 0.0306)** — duty-corrected KXHIMS is 0.53x ballot; 13.8x overstated |
| M2 | **`target_size_fp=300` class as a capital-efficiency lane** — same pool, 3.33x per-contract ceiling, so $2,000 covers 3.33x more seats. 2,116/8,000 programs. Fish: makers sizing to a 1,000 target everywhere. | **D19** (`discount_factor_bps` zero variance) — distinct because D19 checked the *numerator's* multiplier; this is the *denominator*, and it does vary 33x | **CONDITIONAL(gate: §2 below)** |
| M3 | **KXEOWEEK-26AUG22 uncolonized seat** — rival touch depth 1–60 vs target 300, 3–4c spread, $15.94/mkt/day pool, duty 0.70. Fish: the venue, paying for a seat nobody has taken 13.8h after open. | **A20** (farmer preseats at/above target in 95% of 764 windows) — distinct because A20's windows were hourly/daily; these are 21-day programs where colonization has a measurable *lag* | **CONDITIONAL(gate: §2)** — best survivor |
| M4 | **KXTRUMPTIME 8c-spread seat** — 8c spread on all 5 markets, rival depth *exactly* 200/201 on every one (one bot), duty-corrected $0.047 = 1.5x ballot. | **D33** (post one tick behind the touch: 0 fills in 104.3 seat-h) + A50 (1c spreads appear wherever flow exists) | **DEAD(200/201)** — a uniform 200/201 across 5 markets with an 8c spread is a *quote-obligation* bot, not flow; A50's converse: 8c persisting = no flow to earn from |
| M5 | **15M subsidy cut as a farmer-exodus trigger** — seat the surviving 16 windows/day after rivals leave; rival-share numerator up 6x. | **D17** (82/82 future programs start within 28.2h, all 4 toxic 15-min families) + A6/A7/A8/A11 | **DEAD(0.0095)** — duty-corrected 15M rate is $0.0095/ct/cal-day = 0.31x ballot; the 6x cut *reduced* duty to 0.00, so exodus makes a smaller pie, not a bigger slice |
| M6 | **The 161-family new_event flood** — screen the brand/CC/NW/APP families for one that beats ballot. | **A85** (family-calendar hypothesis: macro YEAR families inert) | **DEAD(1.33x on n=1)** — duty-corrected best is KXSCHUMERRUN $0.0407 on **one** market; §2.4 UNDERPOWERED, and 1 market × 1000ct × $0.0407 = $40.70/day ceiling at 100% share, unreachable |
| M7 | **`quadratic_with_maker_fees` blacklist** — 129 series charge makers; never quote there. Fish: us, if we don't check. | **A15/A51** (maker bleed) | **DEAD(hygiene, 0 alpha)** — a filter, not a trade; recorded as a standing constraint |
| M8 | **The 9 `fee_multiplier=0` series as a zero-friction taker door.** Fish: nobody — the fee was never the binding cost. | **D11** (zero-fee maker-in/maker-out round-trip: −8.4c/fill) + A73 (−1.00c median captured round-trip in all 6 top-volume families) | **DEAD(−8.4c)** — D11 already priced the zero-fee case; the spread, not the fee, is the toll |
| M9 | **Pool wind-down ramps as a 3-day-ahead window-death forecast** (DIESELD 252k→42k linear, UST*AD 150k→30k). | **D17** (programs feed as early warning) — distinct because D17 forecast *births*, this forecasts *deaths* | **DEAD(exit-only)** — tells you when to leave, never where to go; and D34 already showed decay is smooth (−8.2%/3.7h), no cliff to time |
| M10 | **GPU `*MON` `period_reward` 4x raise (150k/250k → 600k)** — the 08-15 census preregistered a tripwire at "period_reward above ~1,000,000"; it fired at 600k. | **D8** (GPU-class LIP +$0.0098/ct = 0.015x ballot per ct-hr) | **DEAD(0.019)** — duty-corrected $0.019/ct/cal-day = 0.62x ballot; the tripwire fires on the wrong variable (raise the *reward*, lengthen the *period*, rate unchanged) |

**Tally: 1 conditional survivor (M3), 1 secondary conditional (M2, a modifier not a trade), 8 dead.**

---

## 2. BEST SURVIVOR — M3, and its costed kill test

**M3: seat KXEOWEEK-26AUG22-0/1/2 at target size (300 ct each) while rival touch depth is 1–60.**

Arithmetic, all measured today:
- ceiling $0.0531/ct/period-day, duty 0.70 → **$0.0374/ct/calendar-day** (1.22x ballot's $0.0306).
- share at target: 300/(300+R) with R ∈ {1,2,60} → **99.7% / 99.3% / 83.3%**.
- gross ceiling = 3 markets × 300 ct × $0.0374 × share = **$33.5/day**; if `discount_factor_bps=5000`
  halves the at-touch payout (D33's reading, contra the census's decay-exponent-0 reading),
  **$16.8/day**. The bar is $25/day. **The trade straddles the bar on a single unresolved parameter.**
- capital: 300 ct at 65c/34c/15c = **$342** one-sided.

**The within-family colonization curve — run free, from data already pulled:**

| KXEOWEEK event | open_time | age | rival touch depth vs target 300 |
|---|---|---|---|
| 26AUG22 | 2026-08-15T14:00 | **13.8 h** | **1–60 (0.3%–20% of target)** |
| 26AUG15 | 2026-08-08T14:00 | 7.5 d | 964–2,302 (**3.2x–7.7x** target) |
| 26AUG08 | 2026-08-01T14:00 | 14.5 d | 45,076–45,343 (**150x** target) |

A20's mechanism is confirmed *within this family* — but with a lag that A20's hourly windows could
not show. n=3 live markets, one family ⇒ **UNDERPOWERED under §2.4; this is not reported as a kill.**

**KILL TEST (preregistered, before running):**
Re-pull `GET /trade-api/v2/markets/{ticker}/orderbook?depth=10` (parse `orderbook_fp.yes_dollars` /
`no_dollars`, NOT `orderbook.yes` — grave A76) for the 3 KXEOWEEK-26AUG22 markets, 3x/day for 4 days
= 36 requests. **Cost: $0.00 (keyless, read-only). Time: 12 minutes total (3 min/day).**
- **Killing number:** median rival touch depth `R` across the 3 markets on day 4 after open.
- **Threshold:** `R ≥ 300` (share ≤ 50% ⇒ ceiling ≤ $16.8/day even ungated) ⇒ **DEAD**.
  `R < 60` sustained through day 4 (share ≥ 83%) ⇒ escalate to the $342 one-sided seat.
- **Second, free branch:** re-run the same measurement on KXTRUMPTIME-26AUG22 (opened the same
  minute, 08-15T14:00, already at 200/201 = 20% of its 1,000 target). If two families opened
  simultaneously colonize at different rates, `target_size` is the discriminator and **M2 upgrades
  from CONDITIONAL to a measured modifier**; if they converge, M2 dies with M3.

**M2's own gate:** across all 2,116 `target_size=300` programs, median share-weighted duty-corrected
rate must exceed the `target_size=1000` cohort's by >1.5x after controlling for family. Test: pure
on-disk recomputation from `ip_new.jsonl` + `ip_2026-08-15.jsonl`. **Cost $0, 20 minutes.**

---

## 3. CLAUDE ↔ GEMINI EXCHANGE (condensed verbatim; SPEC §2.6 receipt)

**Round 1 — Gemini's 4 independent ideas** (generated from the census summary alone, blind to mine):
1. *"Systematically farm the outlier subsidy in KXHIMS markets."* Fish: HIMS-fundamentals takers
   insensitive to a 1c spread, plus the venue. Mechanism: "raised 9.49x to $0.2246/contract/day,
   4.1x the ballot rate… 4 of 7 in-band, 1c spreads, bid depth 1147–2466." Grave A26, "distinct
   because A26 refers to the wing trap in toxic fast-resolving 15-minute LIPs." Kill test: post 100
   ct for 6h, ~$50.
2. *"Act as a predator, not a farmer, in thinly-quoted KXCAVA."* Fish: "under-capitalized makers
   drawn in by the 3.14x rate hike." Grave D32, "distinct because D32 killed being the *maker*;
   this is being the *predator*."
3. *"Fade the final farmers in the structurally cut 15-minute commodity LIPs"* — buy 1c wings in the
   last 3 minutes. Grave A11. Kill test $4, 1 hour.
4. *"Reallocate maker capital on the second derivative of subsidy rates"* — quit the CUTS list, move
   everything to the RAISES list. Grave D5–D10, "distinct because it trades the *change*."
   **Gemini's ranking 1>4>2>3; single funding pick: 1, "and the $0.2246/ct/day rate for KXHIMS."**

**Round 2 — Claude attacks, on data, not rhetoric.**
> "Your $0.2246 is a PERIOD-LENGTH ARTIFACT. KXHIMS's live program pays $0.145/ct over a 4.997-day
> period = $0.029/ct/day. The 0.2246 came from the 08-10 KXHIMS-26AUGSUBS batch, period 0.445d, which
> does not repeat. Duty cycle 0.27. **Duty-corrected KXHIMS = $0.0163 vs ballot $0.0306 — 0.53x, not
> 4.1x. Overstatement 13.8x.** Same correction: AAAGASD 0.1502→0.0143, TEMPMIAH 1.92→0.0114 (168x),
> GOLD15M 6.40→0.0095 (674x), CAVA 0.0692→0.0143, MUSKNW 0.0950→0.0107. Your ideas 1, 2 and 4 all rest
> on the artifact; idea 4 *is* the artifact-generating machine. Your idea 3: grave A8 already measured
> that population — 0 of 439 markets settled YES, rule-of-three upper bound 0.683%; your own >100x
> threshold is unreachable at 0.683%."

**Gemini's concessions, recorded by name:**
> "I concede my round-1 ideas 1, 2, and 4. They were based on a rate calculation artifact exposed by
> your duty-cycle correction; the killing number for my top pick KXHIMS was its corrected rate of
> $0.0163/ct/day versus the $0.0306 ballot reference. I concede idea 3 was killed by the historical
> win rate of 0/439 (0.683% upper bound), making my suggested >100x return threshold unreachable."
> — **4 of 4 conceded.**

**Gemini's counter-attacks on M1–M10** (verdicts, condensed): M1 DEAD(0.0163) · M2 TRADE-shaped
("the 3.33x multiplier correctly identifies markets where less capital is needed") · M3 TRADE-shaped
("rival depth 1–60 a fraction of target 300 — an open, uncontested seat") · M4 CONDITIONAL(8c) ·
M5 CONDITIONAL(rival depth) · M6 DEAD(1.33x) · M7 DEAD(hygiene) · M8 CONDITIONAL(volume) ·
M9 DEAD(hygiene) · M10 DEAD(0.019).
**Gemini's pick: M3.** Its proposed test: *"Place a 10-contract maker order inside the 3–4c spread
on one KXEOWEEK-26AUG22 market and hold for 15 minutes. ~$5 at risk."*

**Claude's rebuttal of Gemini's verdicts (concessions and refusals recorded):**
- *I refuse M2 and M3 as TRADE-shaped.* Gemini graded both on rate alone and ignored capacity: M3's
  gross ceiling is **$16.8–$33.5/day against a $25/day bar**, straddling it on one unresolved
  parameter (`discount_factor_bps` at-touch treatment). Both stay **CONDITIONAL**.
- *I reject Gemini's kill test for M3.* A 10-contract order for 15 minutes tests nothing: it is 3.3%
  of target size, earns a share-weighted fraction too small to measure, commits capital, and its
  15-minute horizon cannot see a colonization curve whose measured half-life is **days** (13.8h → 1–60
  ct; 7.5d → 964–2,302 ct). My substitute is **read-only, $0, 12 minutes, and 4 days long**, which is
  the timescale the mechanism actually lives on.
- *I concede to Gemini on M4.* Its CONDITIONAL was softer than my DEAD; I hold DEAD but record that
  the killing number (uniform 200/201 across 5 markets) is a **structural inference**, not a measured
  P&L, and is therefore weaker than the other nine verdicts.
- *Gemini's M5 CONDITIONAL is wrong on sign* and I did not accept it: it argued the exodus raises our
  share numerator. The duty measurement says the 6x cut drove 15M duty to **0.00** — a larger slice of
  a pie that stopped being baked. DEAD stands.

---

## 4. NEW GRAVES FROM THIS BURST (8) — graveyard 122 → 130

| # | Idea | Killing number |
|---|---|---|
| M1 | Chase `period_reward` pool raises (HIMS/MUSKNW/CAVA) | duty-corrected $0.0163 vs ballot $0.0306; raw 9.49x "raise" is a 13.8x period-length artifact |
| M4 | KXTRUMPTIME 8c-spread seat | rival depth exactly 200/201 on 5/5 markets = obligation bot, not flow; 8c persisting ⇒ no flow (converse of A50) |
| M5 | 15M subsidy cut as farmer-exodus trigger | duty-corrected $0.0095/ct/cal-day = 0.31x ballot; the cut drove duty to 0.00 |
| M6 | The 161-family new_event flood | best duty-corrected $0.0407 on n=1 market (UNDERPOWERED); $40.70/day ceiling at 100% share |
| M7 | `quadratic_with_maker_fees` blacklist as a trade | 129 series, 0 alpha — a constraint, not a lane |
| M8 | 9 `fee_multiplier=0` series as a taker door | D11's −8.4c/fill already priced the zero-fee case; the spread is the toll |
| M9 | Pool wind-down ramps as a forecast | exit-only signal; D34 already showed decay is smooth, no cliff |
| M10 | GPU `*MON` 4x `period_reward` raise / the 08-15 tripwire | $0.019/ct/cal-day = 0.62x ballot; tripwire watches the numerator while the period lengthens |

**Standing correction to the organ:** any future burst quoting a `$/ct/day` LIP rate **must** state
the duty cycle alongside it. Raw `period_reward/target_size/period_days` overstated six of six
families I checked, by 4.8x to 674x. This is a new instance of SPEC §1.3 mechanism #4 and it fooled
both models in this burst until the correction was run.

**Standing correction #2:** the orderbook response key is `orderbook_fp` with `yes_dollars`/
`no_dollars` in **decimal dollars**. Parsing `orderbook.yes` returns empty for 100% of markets and
regenerates grave **A76** verbatim. I hit this and caught it against a known-liquid control.

---

## 5. LEDGER LINE (append to SPEC §4)

| Date | Burst | Fuel | Ideas (C/G) | Survivors | New graves | Graveyard after | Tokens |
|---|---|---|---|---|---|---|---|
| 2026-08-16 | `ideator-musk-20260816.md` | fresh census: 13,008 series (18 categories), 149,058 incentive programs, 73 live orderbooks | 10 / 4 | **1 CONDITIONAL (M3)** + 1 modifier (M2) | 8 | **130** | ~160k |
