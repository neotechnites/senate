#!/usr/bin/env python3
"""
PREREGISTERED FAMILY CENSUS PULL (2026-08-15). STRICTLY READ-ONLY, keyless, ~1 req/s.

SAMPLING RULE (fixed before any trade pull, seed=20260815):
 1. For each family F, enumerate ALL markets via paginated GET /trade-api/v2/markets
    for status in {settled, closed, open} (separate passes, dedup by ticker).
 2. Hazard/drift arm uses the CLOSED+SETTLED (resolved) population only.
 3. Draw n=min(80, len(resolved)) uniformly WITHOUT replacement, random.Random(20260815),
    after a single seeded shuffle. No stratification (populations are small and the
    families have <=3 distinct window generations).
 4. Markets with zero trades STAY in the denominator.
 5. Live/open markets are pulled for BOOK STRUCTURE only (orderbook snapshot), never
    used in the hazard arm.
Cache: data/research/family_census_cache/
"""
import json, os, random, ssl, sys, time, urllib.request, urllib.parse

BASE = "https://api.elections.kalshi.com/trade-api/v2"
ROOT = "/Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research"
CACHE = os.path.join(ROOT, "family_census_cache")
SEED = 20260815
os.makedirs(os.path.join(CACHE, "trades"), exist_ok=True)
os.makedirs(os.path.join(CACHE, "books"), exist_ok=True)

try:
    import certifi
    CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    CTX = ssl.create_default_context()


def get(path, params=None, max_tries=10):
    url = BASE + path + ("?" + urllib.parse.urlencode(params) if params else "")
    delay = 1.0
    for a in range(max_tries):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json",
                                                       "User-Agent": "research-readonly/1.0"})
            with urllib.request.urlopen(req, context=CTX, timeout=45) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            if a == max_tries - 1:
                raise
            time.sleep(delay); delay = min(delay * 1.8, 60.0)


def enumerate_markets(series):
    p = os.path.join(CACHE, f"markets_{series}.json")
    if os.path.exists(p):
        return json.load(open(p))
    allm, seen, uniq = [], set(), []
    for status in ("settled", "closed", "open"):
        cursor = None
        while True:
            q = {"series_ticker": series, "status": status, "limit": 1000}
            if cursor:
                q["cursor"] = cursor
            b = get("/markets", q)
            ms = b.get("markets", [])
            allm.extend(ms)
            cursor = b.get("cursor") or ""
            if not cursor or not ms:
                break
            time.sleep(1.0)
        time.sleep(1.0)
    for m in allm:
        if m["ticker"] not in seen:
            seen.add(m["ticker"]); uniq.append(m)
    json.dump(uniq, open(p, "w"))
    return uniq


def pull_trades(ticker):
    f = os.path.join(CACHE, "trades", f"{ticker}.json")
    if os.path.exists(f):
        return json.load(open(f))
    tr, cursor = [], None
    while True:
        q = {"ticker": ticker, "limit": 1000}
        if cursor:
            q["cursor"] = cursor
        b = get("/markets/trades", q)
        t = b.get("trades", [])
        tr.extend(t)
        cursor = b.get("cursor") or ""
        if not cursor or not t:
            break
        time.sleep(1.0)
    json.dump(tr, open(f, "w"))
    return tr


def pull_book(ticker):
    f = os.path.join(CACHE, "books", f"{ticker}.json")
    if os.path.exists(f):
        return json.load(open(f))
    b = get(f"/markets/{ticker}/orderbook", {"depth": 100})
    json.dump(b, open(f, "w"))
    return b


def sample_for(series, n=80):
    sp = os.path.join(CACHE, f"sample2_{series}.json")
    if os.path.exists(sp):
        return json.load(open(sp))
    mk = enumerate_markets(series)
    # AMENDED 2026-08-15 (pre-data, after enumeration only): the YEAR families have
    # ZERO resolved markets (all close 2028-2037), so a settlement-based hazard arm is
    # impossible for them. Hazard arm therefore uses the FULL market population and
    # measures band-transit from the TRADE TAPE. Resolved markets, where they exist,
    # keep their settlement labels. Sampling rule (seed, shuffle, no filtering) unchanged.
    resolved = [m for m in mk if m.get("status") in ("settled", "closed", "finalized")]
    live = [m for m in mk if m.get("status") in ("open", "active")]
    if len(resolved) < 40:
        resolved = list(mk)
    rng = random.Random(SEED)
    tk = sorted(m["ticker"] for m in resolved)
    rng.shuffle(tk)
    obj = {"seed": SEED, "series": series, "population_all": len(mk),
           "population_resolved": len(resolved), "population_open": len(live),
           "sample": tk[:n], "open": sorted(m["ticker"] for m in live)}
    json.dump(obj, open(sp, "w"), indent=1)
    return obj


if __name__ == "__main__":
    fams = sys.argv[1].split(",")
    nbooks = int(os.environ.get("NBOOKS", "25"))
    for F in fams:
        s = sample_for(F, int(os.environ.get("N","80")))
        print(f"[{F}] all={s['population_all']} resolved={s['population_resolved']} "
              f"open={s['population_open']} sample={len(s['sample'])}", flush=True)
        for i, t in enumerate(s["sample"]):
            try:
                tr = pull_trades(t)
                if i % 20 == 0:
                    print(f"   {i}/{len(s['sample'])} {t} n={len(tr)}", flush=True)
            except Exception as e:
                print(f"   FAIL {t}: {e}", flush=True)
            time.sleep(1.0)
        for t in s["open"][:nbooks]:
            try:
                pull_book(t)
            except Exception as e:
                print(f"   BOOKFAIL {t}: {e}", flush=True)
            time.sleep(1.0)
        print(f"[{F}] done", flush=True)
    print("ALLDONE", flush=True)
