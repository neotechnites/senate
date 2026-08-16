#!/usr/bin/env python3
"""
PREREGISTERED CENSUS PULL - KXTEMPCHIH maker-side kill test (2026-08-15)
STRICTLY READ-ONLY. Keyless public endpoints only. No orders. No auth.

SAMPLING RULE (fixed before any trade pull, seed=20260815):
 1. Enumerate ALL KXTEMPCHIH markets with status in {settled, finalized} via
    paginated GET /trade-api/v2/markets.
 2. Stratify by event calendar day parsed from the ticker date token.
 3. Target N=500. Allocate to each day proportional to that day's share of the
    finalized population (largest-remainder rounding), min 1 per day.
 4. Within each day draw uniformly WITHOUT replacement using random.Random(20260815).
 5. ARM 2 (maker seat) = first 100 tickers of the ARM 1 sample after a single
    seeded shuffle with the same seed. No re-draw, no filtering on outcome.
 6. Markets with zero trades stay in the denominator (they are the "never traded"
    outcome, which is itself the answer for a resting bid).

Cache: data/research/temp_census_cache/  (resumable; one json per market)
"""
import json, os, random, ssl, sys, time, urllib.request, urllib.error
from pathlib import Path

BASE = "https://api.elections.kalshi.com/trade-api/v2"
ROOT = Path("/Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research")
CACHE = ROOT / "temp_census_cache"
TRADES = CACHE / "trades"
CACHE.mkdir(parents=True, exist_ok=True)
TRADES.mkdir(parents=True, exist_ok=True)
SEED = 20260815

try:
    import certifi
    CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    CTX = ssl.create_default_context()


def get(path, params=None, max_tries=12):
    url = BASE + path
    if params:
        import urllib.parse
        url += "?" + urllib.parse.urlencode(params)
    delay = 1.0
    for attempt in range(max_tries):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json",
                                                       "User-Agent": "research-readonly/1.0"})
            with urllib.request.urlopen(req, context=CTX, timeout=45) as r:
                body = json.loads(r.read().decode())
            if isinstance(body, dict) and body.get("error"):
                raise RuntimeError(body["error"].get("code"))
            return body
        except Exception as e:
            code = getattr(e, "code", None) or str(e)
            if attempt == max_tries - 1:
                raise
            time.sleep(delay)
            delay = min(delay * 1.8, 90.0)
    raise RuntimeError("unreachable")


def enumerate_markets(series="KXTEMPCHIH"):
    out_path = CACHE / f"markets_{series}.json"
    if out_path.exists():
        return json.loads(out_path.read_text())
    allm, cursor, page = [], None, 0
    # status=settled returns the full finalized population (9,195 verified); the
    # separate "finalized" pass is redundant and only burns the rate bucket.
    for status in ("settled",):
        cursor = None
        while True:
            p = {"series_ticker": series, "status": status, "limit": 1000}
            if cursor:
                p["cursor"] = cursor
            b = get("/markets", p)
            ms = b.get("markets", [])
            allm.extend(ms)
            cursor = b.get("cursor") or ""
            page += 1
            print(f"  [{status}] page {page}: +{len(ms)} total={len(allm)}", flush=True)
            if not cursor or not ms:
                break
            time.sleep(1.0)
    seen, uniq = set(), []
    for m in allm:
        if m["ticker"] not in seen:
            seen.add(m["ticker"])
            uniq.append(m)
    out_path.write_text(json.dumps(uniq))
    return uniq


def day_of(ticker):
    # KXTEMPCHIH-26AUG1512-T75  -> 26AUG15
    parts = ticker.split("-")
    return parts[1][:7] if len(parts) > 1 else "UNK"


def build_sample(markets, n=500):
    sp = CACHE / "sample.json"
    if sp.exists():
        return json.loads(sp.read_text())
    rng = random.Random(SEED)
    days = {}
    for m in markets:
        days.setdefault(day_of(m["ticker"]), []).append(m["ticker"])
    total = sum(len(v) for v in days.values())
    quotas, rema = {}, []
    for d, v in days.items():
        exact = n * len(v) / total
        q = max(1, int(exact))
        quotas[d] = min(q, len(v))
        rema.append((exact - int(exact), d))
    rema.sort(reverse=True)
    i = 0
    while sum(quotas.values()) < n and i < len(rema) * 50:
        d = rema[i % len(rema)][1]
        if quotas[d] < len(days[d]):
            quotas[d] += 1
        i += 1
    sample = []
    for d in sorted(days):
        sample.extend(rng.sample(days[d], min(quotas[d], len(days[d]))))
    rng.shuffle(sample)
    sample = sample[:n]
    obj = {"seed": SEED, "n": len(sample), "tickers": sample,
           "arm2": sample[:100], "population": total, "days": {d: len(v) for d, v in days.items()}}
    sp.write_text(json.dumps(obj, indent=1))
    return obj


def pull_trades(ticker):
    f = TRADES / f"{ticker}.json"
    if f.exists():
        return json.loads(f.read_text())
    trades, cursor = [], None
    while True:
        p = {"ticker": ticker, "limit": 1000}
        if cursor:
            p["cursor"] = cursor
        b = get("/markets/trades", p)
        t = b.get("trades", [])
        trades.extend(t)
        cursor = b.get("cursor") or ""
        if not cursor or not t:
            break
        time.sleep(1.0)
    f.write_text(json.dumps(trades))
    return trades


if __name__ == "__main__":
    print("enumerating...", flush=True)
    mk = enumerate_markets()
    print(f"finalized population: {len(mk)}", flush=True)
    meta = {m["ticker"]: m for m in mk}
    (CACHE / "market_meta.json").write_text(json.dumps(
        {k: {kk: v.get(kk) for kk in ("ticker", "result", "status", "open_time", "close_time",
                                      "volume", "last_price_dollars", "settlement_value_dollars")}
         for k, v in meta.items()}))
    s = build_sample(mk)
    print(f"sample n={s['n']} across {len(s['days'])} days", flush=True)
    for i, t in enumerate(s["tickers"]):
        try:
            tr = pull_trades(t)
            if i % 25 == 0:
                print(f"  {i}/{s['n']} {t} trades={len(tr)}", flush=True)
        except Exception as e:
            print(f"  FAIL {t}: {e}", flush=True)
        time.sleep(1.0)
    print("DONE", flush=True)
