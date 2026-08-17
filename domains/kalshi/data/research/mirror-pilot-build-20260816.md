# MIRROR-THE-CERTAINTY-TAKER (B1) — live executor build

**Built 2026-08-16. NOT LAUNCHED. No orders placed. Main session reviews and launches.**

Receipts this implements: `mirror-settlement-replay-20260816.md` (+1.59 c/ct on the
preregistered subset, n=62, 9 city-hour clusters, t=+5.42, 98.9% settle-with-taker on the
fillable arm) and `mirror-slippage-20260816.md` (median slip +1.0c, 215 triggers/hr,
43.2% of triggers unfillable).

## Files

| path | what |
|---|---|
| `/Users/ryanwhitehead/Documents/senate/nestor-wt-lipv5/tools/lipseats/mirror_pilot.py` | the executor (585 lines) |
| `/Users/ryanwhitehead/Documents/senate/nestor-wt-lipv5/tools/lipseats/tests/test_mirror_pilot.py` | 35 tests |

## Tests

```
python3 -m unittest tools.lipseats.tests.test_mirror_pilot   ->  Ran 35 tests, OK
python3 -m unittest discover -s tools/lipseats/tests -t .    ->  Ran 306 tests, OK (skipped=3)
```

306 = the pre-existing 271 + 35 new. The 3 skips are the pre-existing `test_fee_golden`
non-conformance skips, unchanged. Exit 0.

## AXIS-CONVERSION PROOF

`wire.KalshiClient.place_order(ticker, side, price_dollars, count, coid)` takes **side
"bid"/"ask" on the YES axis** and price in **dollars on the YES axis** (`wire.py:326-343`:
"bid = buy YES, ask = sell YES"). Buying NO *is* selling YES, so the acquire price must be
reflected: pay `p` for NO == sell YES at `1 - p`.

`mirror_axis(side, price_c)` returns:

| trigger | meaning | wire call |
|---|---|---|
| `("yes", 97)` | buy YES at 97c | `side="bid", price_dollars=0.97` |
| `("yes", 94)` | buy YES at 94c | `side="bid", price_dollars=0.94` |
| `("no", 97)` | buy NO at 97c | `side="ask", price_dollars=0.03` |
| `("no", 94)` | buy NO at 94c | `side="ask", price_dollars=0.06` |
| `("no", 99)` | buy NO at 99c | `side="ask", price_dollars=0.01` |

Fixtures this is proven against, all three agreeing:

1. **`autoseat.py:2809-2810`** — `wire_side = "bid" if side == "yes" else "ask"` /
   `yes_axis = p if side == "yes" else round(1.0 - p, 2)`.
   `test_matches_autoseat_conversion_exactly` asserts equality for **all 198 cases**
   (99 cents x 2 sides).
2. **`seats.py`/`autoseat._exit_quote:1084-1107`** — "Holding YES reduces by buying NO
   (wire `ask` at 1 - the no touch)"; returns `("ask", round(1.0 - p, 2), p)`.
3. **`autoseat.py:2539-2541`** — "a sell of YES buys NO at 1 - yes_price".

End-to-end round trip (`test_axis_round_trips_through_a_placed_order`): a taker print of
**NO at 96c** (i.e. a 4c YES print) against a book with best-YES-bid 4c yields
`ask_no = 100 - 4 = 96c`, and the order that reaches the FakeClient is
`side="ask", price=0.04, coid="mrp-..."` — the correct sell-YES-at-4c encoding of
buy-NO-at-96c. An inverted axis would have sent `bid @ 0.96`, buying the *losing* side.

**Taker-side price derivation** is separately fixture-tested
(`test_no_side_trigger_uses_the_no_acquire_price`): `p = yes_px` if `taker_side=="yes"`
else `100 - yes_px` — the same rule the slippage capture used.

**Book axis** (`parse_book`, from `mirror_slip.py:45-49`): ladders are ASCENDING so the
touch is the LAST row; `ask_yes = 100 - best_no_bid`, `ask_no = 100 - best_yes_bid`.
Pinned by `test_book_parse_reads_the_touch_off_an_ascending_ladder`.

## Trigger + sizing rule (as measured)

1. Poll `/markets/trades?limit=1000` every 2s; prime on first poll (never fire on backlog).
2. Keep `KXTEMP{CHIH,NYCH,LAXH,DCH,AUSH,MIAH}` with `H-` in the ticker.
3. Taker acquire price `p >= 94c` -> trigger; pull the book immediately.
4. Buy the **taker's own side** iff `exec_ask <= p` **and** `depth >= 25ct`.
5. `n = min(depth, floor(budget_left / ask), 100)`; skip if `n < 10`.

Note on sizing reality: at `p >= 94c` a $50 budget binds at ~51-53 ct, so `MAX_CLIP_CT=100`
is belt-and-braces, not the binding constraint. The `MIN_CLIP_CT=10` filter is the load-
bearing one (42 of 322 measured triggers were sub-1ct clips the 1c fee floor destroys).

## HARD CAPS — compiled constants, config may only TIGHTEN

```python
MIRROR_BUDGET_USD = 50.0   MAX_CLIP_CT = 100   MIN_CLIP_CT = 10
TRIGGER_PRICE_C = 94       MIN_DEPTH_CT = 25
STOP_LOSS_USD = -15.0      WINRATE_FLOOR = 0.95   WINRATE_MIN_N = 30
```

`load_config()` clamps every field back to the constant
(`min()` for ceilings, `max()` for floors). `test_config_can_only_tighten` feeds a config
demanding budget 5000 / clip 10000 / min-clip 1 / trigger 50 / depth 0 / stop -9999 /
winrate 0.10 and asserts **every one** comes back at the compiled value.
`test_config_tighter_values_survive` proves stricter values do pass through.

Open exposure never exceeds the budget: `test_budget_cap_is_never_exceeded_across_clips`
fires 8 triggers across 2 tickers on 5000ct books and asserts both
`open_exposure_usd() <= 50` and `sum(count x price) <= 50`.
Settlement frees budget (`test_settlement_frees_budget`).

## KILL CRITERIA

| # | rule | test |
|---|---|---|
| a | cumulative realized night P&L `<= -$15` -> STOP placing, write `mirror_halt.json`, ntfy **urgent** | `test_stop_loss_halts_and_writes_halt_file` |
| b | after `>= 30` settled clips, settle-with-taker `< 0.95` -> same stop | `test_winrate_halt_after_30_settled` (28/30 = 93.3% halts); `test_winrate_gate_does_not_arm_below_30` (9/10 = 90% does NOT halt) |
| c | `mirror_halt.json` present at startup -> `run()` returns **2**, places nothing, ledgers `startup_refused`, pages urgent | `test_startup_fails_closed_on_existing_halt_file` |
| d | `in_window()` guard (22:00Z -> 02:10Z, wraps midnight) + SIGTERM/SIGINT handler set `stop`, then a final settlement poll and `session_end` row | `test_window_guard_wraps_midnight`, `test_run_exits_when_window_closes` |

A halt **cancels nothing** — the bot is a pure taker and never rests an order. Halting
means it stops placing. A halted pilot ledgers `skip_halted` on every subsequent trigger
(`test_halted_pilot_places_nothing`).

## LEDGER — `/home/ubuntu/kalshi_data/mirror_pilot.jsonl`

One JSON row per event, `{"ts","event",...}`. Events:
`session_start`, `startup_refused`, `skip_no_ask`, `skip_slip`, `skip_thin`,
`skip_minclip`, `skip_budget`, `skip_halted`, `dry_placed`, `placed`, `place_error`,
`settled_win`, `settled_loss`, `halt`, `sigterm`, `window_closed`, `session_end`.

Skip rows carry `ticker, side, trigger_price_c, trade_id, trigger_ct, exec_ask_c,
depth_ct, budget_left_usd` so the live tape reconciles line-for-line against the replay.
Every `coid` is `mrp-<epoch>-<seq>`.

**Fees:** `taker_fee_usd = ceil_0.0001(0.07 * n * p * (1-p))` — the venue-true rule pinned
by `test_fee_golden.py` against 472 real fills, i.e. ceil to 1/100 of a cent. The
settlement replay used the harsher whole-cent ceil, so the measured +1.59 c/ct is
*conservative* relative to what this bot actually pays. Realized P&L per settled clip =
`(100c if result == side else 0) * n - cost - fee`.

## LAUNCH — VPS (DO NOT RUN WITHOUT REVIEW)

Deploy:

```bash
scp -i ~/.ssh/senate_vps_ed25519 \
  /Users/ryanwhitehead/Documents/senate/nestor-wt-lipv5/tools/lipseats/mirror_pilot.py \
  ubuntu@129.146.115.241:/home/ubuntu/senate/nestor-wt-lipv5/tools/lipseats/mirror_pilot.py
scp -i ~/.ssh/senate_vps_ed25519 \
  /Users/ryanwhitehead/Documents/senate/nestor-wt-lipv5/tools/lipseats/tests/test_mirror_pilot.py \
  ubuntu@129.146.115.241:/home/ubuntu/senate/nestor-wt-lipv5/tools/lipseats/tests/test_mirror_pilot.py
```

Verify on the VPS, then DRY-RUN first (recommended: 10 min, no `--live`, no `MIRROR_GO`):

```bash
ssh -i ~/.ssh/senate_vps_ed25519 ubuntu@129.146.115.241 \
  'cd /home/ubuntu/senate/nestor-wt-lipv5 && python3 -m unittest discover -s tools/lipseats/tests -t . -p "test_*.py" 2>&1 | tail -3'

ssh -i ~/.ssh/senate_vps_ed25519 ubuntu@129.146.115.241 \
  'ls -l /home/ubuntu/kalshi_data/mirror_halt.json 2>&1'   # must be "No such file"

# DRY RUN — reads only, ledgers dry_placed
ssh -i ~/.ssh/senate_vps_ed25519 ubuntu@129.146.115.241 \
  'cd /home/ubuntu/senate && NESTOR_ENV_FILE=/home/ubuntu/nestor/.env \
   nohup python3 nestor-wt-lipv5/tools/lipseats/mirror_pilot.py \
     --ledger /home/ubuntu/kalshi_data/mirror_pilot_dry.jsonl \
     >> /home/ubuntu/kalshi_data/mirror_pilot_dry.log 2>&1 &'
```

**LIVE** (only after the dry run looks right; the process self-exits at 02:10Z):

```bash
ssh -i ~/.ssh/senate_vps_ed25519 ubuntu@129.146.115.241 \
  'cd /home/ubuntu/senate && \
   NESTOR_ENV_FILE=/home/ubuntu/nestor/.env MIRROR_GO=1 \
   nohup python3 nestor-wt-lipv5/tools/lipseats/mirror_pilot.py --live \
     >> /home/ubuntu/kalshi_data/mirror_pilot.log 2>&1 & \
   echo started pid $!'
```

`--live` is refused unless `MIRROR_GO=1`; `load_auth()` refusal exits 2 before any loop.

## MONITORING

```bash
# live tail
ssh -i ~/.ssh/senate_vps_ed25519 ubuntu@129.146.115.241 \
  'tail -f /home/ubuntu/kalshi_data/mirror_pilot.jsonl'

# running P&L + skip census
ssh -i ~/.ssh/senate_vps_ed25519 ubuntu@129.146.115.241 \
  "python3 -c \"
import json,collections
rows=[json.loads(l) for l in open('/home/ubuntu/kalshi_data/mirror_pilot.jsonl')]
c=collections.Counter(r['event'] for r in rows)
s=[r for r in rows if r['event'].startswith('settled_')]
print(dict(c))
print('settled', len(s), 'wins', sum(1 for r in s if r['event']=='settled_win'),
      'pnl \\$%.2f' % sum(r['pnl_usd'] for r in s),
      'ct', sum(r['count_ct'] for r in s))
if s: print('c/ct %.3f' % (100*sum(r['pnl_usd'] for r in s)/sum(r['count_ct'] for r in s)))
\""

# halt check
ssh -i ~/.ssh/senate_vps_ed25519 ubuntu@129.146.115.241 \
  'cat /home/ubuntu/kalshi_data/mirror_halt.json 2>/dev/null || echo "no halt"'

# manual kill
ssh -i ~/.ssh/senate_vps_ed25519 ubuntu@129.146.115.241 'pkill -f mirror_pilot.py'
```

To block all future starts: write any JSON to
`/home/ubuntu/kalshi_data/mirror_halt.json` — the pilot fails closed on it.

## Open items for review

- `refresh_universe()` reads the 6 open-market lists every 10 min for the log; it does not
  gate triggers (a 10-min-stale universe would falsely skip newly-opened hourlies).
- Settlement polling is every 60s per open clip via `get_market`; with a ~50ct budget the
  open-clip count stays in single digits, so this is a few req/min against the 3 req/s bucket.
- Fill accounting trusts the place response's `fill_count`; partial fills are ledgered but
  exposure is booked at full clip size (conservative — it over-reserves budget, never under).
