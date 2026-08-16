# DRAFT REGISTRATION — autoseat v4: RECEIPT-GATED SCALE LADDER (unsealed)

Status: DRAFT. Seals only when the Rung-B trigger fires AND Ryan says go.
Extends sealed reg-autoseat-v3-2026-08-15.md (81d79db6). Everything in v3 stays
in force at every rung — curfew, killswitch, K1-K4, $50/market — except the
seat count and budget, which this ladder raises stepwise on receipts.

## The thesis this ladder tests

The venue's own estimates feed shows $35.75 accrued LIP rewards this week
($32.86 from 13 programs ending 2026-08-16 03:59Z), earned on ~$250 of resting
seats. Ryan's framing is correct: seats that evacuate before the terminal kill
zone earn this "for free." The unproven links are (a) estimates → credited
cash, and (b) fills stay rare outside the terminal window. Each rung buys the
next only with receipts.

## Rung A (LIVE NOW — sealed v3)
1 seat × $50. Curfew compiled. Running since 2026-08-15 ~18:59Z.

## Rung B — 5 seats × $50 = $250 (within Ryan's existing mandate)
TRIGGER (both required):
- B1: credited cash from the 08-16 03:59Z window closes lands ≥ 80% of the
  $32.86 accrued estimate (per kalshi.rewards.realization_accuracy the venue
  pays within 0.1%; the 20% slack is for our attribution error only), verified
  in credit_receipts.jsonl / balance deltas.
- B2: zero post-restart fills at the time of the flip.
MECHANISM: code change HARD_MAX_SEATS 1→5 + config budget_usd 250, max_seats 5,
max_new_per_cycle 2; tests updated; THIS document finalized and sealed with the
receipt numbers filled in; Ryan go recorded.
KILL while at Rung B: any 2 fills/7d (K4) or a single fill > $25 (K3) kills the
strategy, not just the rung. Curfew violations impossible by compilation.

## Rung C — the 20-seat target
20 × $50 = $1,000 exceeds Ryan's $250 sovereign mandate; raising it is HIS
call, not a registration's. Two paths, decided at Rung-B review with a full
week of per-program receipts:
- C-wide: 20 seats × $12.50 under the existing $250. OPEN QUESTION: do $12.50
  seats clear the modeled-credit floors, and does share (∝ our size vs field)
  make many small seats accrue comparably to few large ones? Answer from this
  week's per-program estimates + seat sizes before proposing.
- C-full: mandate raise to $1,000, 20 × $50. Only proposable with two clean
  measured windows (the original v3 §3 bar) — i.e., receipts showing
  credited ≥ 2× fill losses at Rung B scale.

## Standing at every rung
- Terminal curfew 24h, compiled; config can only lengthen.
- Fill-suspend ≥2/7d, single-fill >50% page, K1-K4.
- Evacuation/drift eject gates from the 2026-08-15 fill-forensics research are
  ADDED (never removed) as soon as the evidence supports a threshold; they get
  their own addendum with the forensics receipts attached.
- No seat rests through a window close, ever. The $30 that was "free" on
  08-15 is only free if you leave before the takers arrive.
