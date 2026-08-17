#!/usr/bin/env python3
"""MLB slate depth sampler — STRICTLY READ-ONLY (public orderbook endpoint only).

Snapshots bid/ask depth for a slate of Kalshi tickers on an interval and writes
rows into m3_depth_samples in data/kalshi_domain.db. Reuses
harness.venue_client.KalshiVenueClient.fetch_public_orderbook (no auth, no orders).

Usage (from domain root /Users/ryanwhitehead/Documents/senate/domains/kalshi):

  # Discover slate tickers for a date token (writes state/mlb_slate_<token>.json)
  python3 -m harness.depth_sampler discover 26AUG16

  # One-shot dry-run (single snapshot of every slate ticker, rows tagged 'dry-run')
  python3 -m harness.depth_sampler sample --slate 26AUG16 --once --tag dry-run

  # Game-window sampling loop (60s interval until the given UTC time)
  python3 -m harness.depth_sampler sample --slate 26AUG16 --interval 60 \
      --until 2026-08-17T03:00:00Z --tag live

Table schema (created if absent):
  m3_depth_samples(id, ts_utc REAL, run_id TEXT, tag TEXT, ticker TEXT,
                   yes_bid INT, yes_ask INT, no_bid INT, no_ask INT,
                   yes_bid_qty INT, no_bid_qty INT,
                   yes_book TEXT, no_book TEXT, http_ok INT, err TEXT)
Prices are integer cents. yes_ask is derived as 100 - best no bid (Kalshi books
list resting bids on each side). yes_book/no_book are the raw ladders as JSON.
Every row comes from a live API response; failed fetches are recorded with
http_ok=0 and no fabricated prices.
"""
import argparse
import json
import sqlite3
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

DOMAIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DOMAIN_ROOT))

from harness.venue_client import KalshiVenueClient  # noqa: E402

DB_PATH = DOMAIN_ROOT / "data" / "kalshi_domain.db"
STATE_DIR = DOMAIN_ROOT / "state"

DDL = """
CREATE TABLE IF NOT EXISTS m3_depth_samples (
  id INTEGER PRIMARY KEY,
  ts_utc REAL NOT NULL,
  run_id TEXT NOT NULL,
  tag TEXT NOT NULL,
  ticker TEXT NOT NULL,
  yes_bid INTEGER, yes_ask INTEGER,
  no_bid INTEGER, no_ask INTEGER,
  yes_bid_qty INTEGER, no_bid_qty INTEGER,
  yes_book TEXT, no_book TEXT,
  http_ok INTEGER NOT NULL,
  err TEXT
);
CREATE INDEX IF NOT EXISTS idx_m3ds_ticker_ts ON m3_depth_samples(ticker, ts_utc);
"""


def _db():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("PRAGMA busy_timeout=30000")
    conn.executescript(DDL)
    return conn


def _get_json(client, path):
    """Public unauthenticated GET via the venue client's SSL context."""
    import urllib.request
    req = urllib.request.Request(
        client.base_url + path,
        headers={"Accept": "application/json", "User-Agent": "depth-sampler-readonly/1.0"},
    )
    with urllib.request.urlopen(req, context=client._ssl_ctx, timeout=15) as r:
        return json.loads(r.read().decode())


def discover(date_token: str) -> list:
    """Enumerate open KXMLBGAME markets whose ticker carries the date token."""
    import urllib.parse
    client = KalshiVenueClient()
    markets, cursor = [], None
    while True:
        params = {"series_ticker": "KXMLBGAME", "status": "open", "limit": 200}
        if cursor:
            params["cursor"] = cursor
        body = _get_json(client, "/trade-api/v2/markets?" + urllib.parse.urlencode(params))
        markets += body.get("markets", [])
        cursor = body.get("cursor")
        if not cursor:
            break
    slate = [
        {
            "ticker": m["ticker"],
            "title": m.get("title"),
            "open_time": m.get("open_time"),
            "expected_expiration_time": m.get("expected_expiration_time"),
        }
        for m in markets
        if f"-{date_token}" in m["ticker"]
    ]
    slate.sort(key=lambda m: m["ticker"])
    STATE_DIR.mkdir(exist_ok=True)
    out = STATE_DIR / f"mlb_slate_{date_token}.json"
    out.write_text(json.dumps({"fetched_at": datetime.now(timezone.utc).isoformat(),
                               "date_token": date_token, "markets": slate}, indent=2))
    return slate


def _load_slate(date_token: str) -> list:
    f = STATE_DIR / f"mlb_slate_{date_token}.json"
    if not f.exists():
        return [m["ticker"] for m in discover(date_token)]
    return [m["ticker"] for m in json.loads(f.read_text())["markets"]]


def _parse_book(body):
    """Normalize either API book shape to ([(price_cents, qty), ...] yes, no).

    Legacy shape: {"orderbook": {"yes": [[cents, qty], ...], "no": [...]}}
    Current shape: {"orderbook_fp": {"yes_dollars": [["0.3400", "12.00"], ...],
                                     "no_dollars": [...]}}  (resting bids per side)
    """
    ob = body.get("orderbook") or {}
    yes = [(int(p), float(q)) for p, q in (ob.get("yes") or [])]
    no = [(int(p), float(q)) for p, q in (ob.get("no") or [])]
    if not yes and not no:
        fp = body.get("orderbook_fp") or {}
        yes = [(round(float(p) * 100), float(q)) for p, q in (fp.get("yes_dollars") or [])]
        no = [(round(float(p) * 100), float(q)) for p, q in (fp.get("no_dollars") or [])]
    return yes, no


def _snapshot_one(client, conn, run_id, tag, ticker):
    ts = time.time()
    try:
        try:
            body = client.fetch_public_orderbook(ticker)
        except Exception as e:
            if "429" not in str(e):
                raise
            time.sleep(2.0)  # single retry on venue rate limit
            body = client.fetch_public_orderbook(ticker)
        yes, no = _parse_book(body)
        yes_bid = max((p for p, _ in yes), default=None)
        no_bid = max((p for p, _ in no), default=None)
        yes_ask = 100 - no_bid if no_bid is not None else None
        no_ask = 100 - yes_bid if yes_bid is not None else None
        yes_qty = sum(q for _, q in yes)
        no_qty = sum(q for _, q in no)
        conn.execute(
            "INSERT INTO m3_depth_samples (ts_utc, run_id, tag, ticker, yes_bid, yes_ask,"
            " no_bid, no_ask, yes_bid_qty, no_bid_qty, yes_book, no_book, http_ok, err)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,1,NULL)",
            (ts, run_id, tag, ticker, yes_bid, yes_ask, no_bid, no_ask,
             yes_qty, no_qty, json.dumps(yes), json.dumps(no)),
        )
        return True
    except Exception as e:
        conn.execute(
            "INSERT INTO m3_depth_samples (ts_utc, run_id, tag, ticker, http_ok, err)"
            " VALUES (?,?,?,?,0,?)",
            (ts, run_id, tag, ticker, str(e)[:300]),
        )
        return False


def sample(date_token, interval, until_utc, once, tag, pace=0.35):
    tickers = _load_slate(date_token)
    if not tickers:
        print(f"No slate tickers for {date_token}; run discover first.", file=sys.stderr)
        return 1
    client = KalshiVenueClient()
    conn = _db()
    run_id = f"{date_token}-{uuid.uuid4().hex[:8]}"
    print(f"run_id={run_id} tickers={len(tickers)} interval={interval}s tag={tag}")
    while True:
        loop_start = time.time()
        ok = 0
        for t in tickers:
            ok += _snapshot_one(client, conn, run_id, tag, t)
            time.sleep(pace)
        conn.commit()
        print(f"{datetime.now(timezone.utc).isoformat(timespec='seconds')} wrote {ok}/{len(tickers)} books")
        if once:
            break
        if until_utc and datetime.now(timezone.utc) >= until_utc:
            print("until reached; stopping")
            break
        time.sleep(max(1.0, interval - (time.time() - loop_start)))
    conn.close()
    return 0


def main():
    ap = argparse.ArgumentParser(description="Read-only MLB slate depth sampler")
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("discover")
    d.add_argument("date_token", help="e.g. 26AUG16")
    s = sub.add_parser("sample")
    s.add_argument("--slate", required=True, help="date token, e.g. 26AUG16")
    s.add_argument("--interval", type=float, default=60.0)
    s.add_argument("--until", default=None, help="UTC ISO time to stop, e.g. 2026-08-17T03:00:00Z")
    s.add_argument("--once", action="store_true")
    s.add_argument("--tag", default="live")
    args = ap.parse_args()
    if args.cmd == "discover":
        slate = discover(args.date_token)
        for m in slate:
            print(m["ticker"], "|", m["title"])
        print(f"{len(slate)} markets -> state/mlb_slate_{args.date_token}.json")
        return 0
    until = None
    if args.until:
        until = datetime.fromisoformat(args.until.replace("Z", "+00:00"))
    return sample(args.slate, args.interval, until, args.once, args.tag)


if __name__ == "__main__":
    sys.exit(main())
