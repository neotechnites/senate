# Ideation cycle — band/time extension of the certainty-mirror (2026-08-16 ~04:15Z)

**Read-only. No orders. All numbers recomputed from primary artifacts.**

**Primary artifacts:**
- `data/research/event_tape_20260816.json` — full market lists + complete trade tapes for the 12 settled
  city-hour TEMP events of 26AUG15 hours 22/23 (6 cities x 2 hours; 120 markets, 1,221 trades, 44,238 ct),
  pulled keyless from api.elections.kalshi.com by `event_tape_pull_20260816.py`
- `data/research/settlement_status_20260816.json` — per-ticker results
- Method: taker acquire price p = yes_px (taker yes) or 100−yes_px (taker no); edge = settle(100/0) − p − 7·p·(1−p)c fee;
  clusters = city-hour events (same NWS reading settles a whole event)

## H1 — band extension: does the "mirror the taker" settle edge exist below 94c?

| band | n | ct | winrate | cw edge c/ct | clusters | clust t |
|---|---|---|---|---|---|---|
| 50–69 | 152 | 3,728 | 0.678 | +20.56 | 9 | 1.25 |
| 70–79 | 98 | 2,013 | 0.878 | +22.30 | 10 | 35.0 |
| 80–84 | 55 | 1,694 | 0.945 | +16.01 | 10 | 5.83 |
| 85–89 | 48 | 1,952 | 0.979 | +11.40 | 11 | 7.35 |
| **90–93** | 40 | 1,654 | 0.925 | **−34.27** | 9 | −0.28 |
| 94–96 | 153 | 2,450 | 0.993 | +4.56 | 12 | 1.37 |
| 97–99 | 359 | 19,824 | 0.994 | +1.42 | 12 | 15.68 |

**H1-DOWN (90–93): KILLED by live counterexample.** The band is contract-weighted −34.27c/ct, driven by a
single 700-ct sweep at 90c on `KXTEMPMIAH-26AUG1522-T85.99` (01:04:53Z) that settled NO — a confident
whale who was wrong. This is precisely the adverse-selection event the mirror fears, and it occurred one
band below the preregistered 94 threshold. The 94 line is empirically load-bearing, not arbitrary.

**H1-MID (85–89): CONDITIONAL, not fundable.** +11.40c/ct cw, 0.979 winrate looks rich, but the market
implies ~13% loss rate at those prices and one clear hot August night realizing 2.1% proves nothing —
one MIAH-sized wrong-way night erases weeks of harvest. Gate: replicate on ≥3 nights including at least
one marginal-weather night ($0/night — same keyless settlement replay). Multiple-testing note: 7 bands
scanned; N must be priced per trials ledger before any funding claim.

## H2 — time extension: does the ≥94 edge hold across the whole final hour?

| bucket | n | ct | winrate | cw edge | clusters | clust t |
|---|---|---|---|---|---|---|
| T-0..15m | 225 | 11,937 | 1.000 | +1.43 | 12 | 9.14 |
| T-15..30m | 83 | 4,065 | 0.988 | +2.48 | 11 | 5.33 |
| T-30..60m | 204 | 6,273 | 0.990 | +1.94 | 11 | 15.81 |
| >60m | — | — | — | — | — | (no tape: markets only trade in final hour) |

**H2: SURVIVED in-sample.** No edge decay across the hour; the harvest window is the entire final hour,
not the last minutes. This raises the mirror's capacity estimate but changes nothing about its conditions —
it attaches to the mirror FUNDABLE-CANDIDATE (lane_runs #25) and inherits its gates.

## Registry note (process finding — do not propagate)
All three hypotheses were registered via `senate ideate propose` (idea_edf7d4e0, idea_82c94695,
idea_a9986f5f) and all three show adversary_status=KILLED. That status is a **fail-closed artifact**:
`ANTHROPIC_API_KEY` is absent in this environment, the ModelGateway errors, and `MultiModelAdversary`
fails closed to KILLED for every proposal regardless of content (`senate/models/adversary.py:73`). The
registry verdicts are NOT genuine multi-model audits tonight. The empirical verdicts above stand on the
primary artifacts. Fix needed before the ideate organ's verdicts can be trusted: provision auditor keys.
