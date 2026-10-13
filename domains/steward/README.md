# Steward — Household Manager

Ryan's obligations manager: the house, the vehicles, recurring maintenance, events.

**Output is obligations CLOSED and Ryan-hours saved. Never artifacts.**

## Talk to the Domain Head

```bash
cd domains/steward && ./spinup.sh          # boots a head grounded in steward.db
python3 spinup.py --dry                    # print the prompt, launch nothing
```

Pod tests gate the boot: the head will not start if they fail.

## CLI

```bash
./steward.py status              # backlog + whether anything is actually verified
./steward.py telemetry --json    # what the Senate hub reads (it never SQLs this pod)
./steward.py add "Replace baseboards" --kind ONESHOT --domain HOUSE
./steward.py add "Drain water heater" --kind RECURRING --interval-days 365 \
    --anchor 2026-01-01 --interval-source https://www.epa.gov/watersense
./steward.py done 2 --verbatim "did it saturday"
```

## Design decisions, and whose they are

Every row in `state/canon.py` carries Ryan's verbatim words and the date he said them.
A fact with no Ryan quote does not steer this pod.

- **Recurrence is completion-based, not calendar-based.** `verify/recurrence.py`.
  Due 365 days after you actually did it, not every 1 January. This is why no
  off-the-shelf task app survived selection.
- **Ryan is the only oracle.** Nothing closes an obligation except a completion he
  reported, stored in `completions` with his own words. There is no receipt-hunting
  apparatus and there is not meant to be one.
- **The interface is a conversation, not a digest.** `verify/attention.py` enforces a
  FLOOR on silence — one nag per obligation per week, 6h global gap — and nothing
  more. It never schedules a message. Judgement about whether to speak belongs to the
  head, and choosing silence is logged in `wake_log` as a decision.
- **An interval with no `interval_source` is SELF-MARKED** and is reported that way
  everywhere. Store the number and a citation URL, never copyrighted prose.

## Where the truth lives

The **live DB is on the VPS** (`/home/steward/steward/data/steward.db`); Telegram and the
wake timer run there. Local `data/steward.db` is a read-only mirror: `spinup` and
`./steward.py status` pull it fresh, and local `add`/`done` are refused. Write with
`./remote.sh sql "..."`.
