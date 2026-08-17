#!/usr/bin/env python3
"""seats-lip-replay 2026-08-16T03:51Z — STRICTLY READ-ONLY, keyless, ~1 req/s.
Pulls fresh incentive_programs, then market meta + orderbooks for qualified-family
programs that survive the 24h curfew. Cache: data/research/lip_replay_cache_20260816/
"""
import json, os, ssl, time, urllib.request, urllib.parse, datetime

BASE = "https://api.elections.kalshi.com/trade-api/v2"
CACHE = "/Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research/lip_replay_cache_20260816"
os.makedirs(os.path.join(CACHE, "books"), exist_ok=True)
os.makedirs(os.path.join(CACHE, "markets"), exist_ok=True)
try:
    import certifi
    CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    CTX = ssl.create_default_context()

FAMS = ("KXFEDFUNDSYEAR", "KXUSCPIYEAR", "KXNOMGDPGROWTH",
        "KXSTATEBALLOTMEASURE", "KXRAIN", "KXBTCD")
NOW = datetime.datetime(2026, 8, 16, 3, 51, tzinfo=datetime.timezone.utc)
CURFEW = NOW + datetime.timedelta(hours=24)


def get(path, params=None, max_tries=8):
    url = BASE + path + ("?" + urllib.parse.urlencode(params) if params else "")
    delay = 1.0
    for a in range(max_tries):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json",
                                                       "User-Agent": "research-readonly/1.0"})
            with urllib.request.urlopen(req, context=CTX, timeout=45) as r:
                return json.loads(r.read().decode())
        except Exception:
            if a == max_tries - 1:
                raise
            time.sleep(delay); delay = min(delay * 1.8, 45.0)


def parse_ts(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))


def main():
    # 1. fresh incentive programs (paginated)
    fp = os.path.join(CACHE, "incentive_programs_all.json")
    if os.path.exists(fp):
        allp = json.load(open(fp))
    else:
        allp, cursor = [], None
        while True:
            q = {"limit": 1000}
            if cursor:
                q["cursor"] = cursor
            b = get("/incentive_programs", q)
            rows = b.get("incentive_programs", [])
            allp.extend(rows)
            cursor = b.get("cursor") or ""
            print(f"  pulled {len(allp)} programs...", flush=True)
            if not cursor or not rows:
                break
            time.sleep(1.0)
        json.dump(allp, open(fp, "w"))
    print(f"TOTAL programs: {len(allp)}", flush=True)

    # 2. filter: qualified family, LIP-type, active NOW, not paid out
    cand = []
    for p in allp:
        t = p.get("market_ticker", "")
        if not any(t.startswith(f + "-") for f in FAMS):
            continue
        if p.get("incentive_type") != "liquidity" or p.get("paid_out"):
            continue
        try:
            st, en = parse_ts(p["start_date"]), parse_ts(p["end_date"])
        except Exception:
            continue
        if st <= NOW < en:
            cand.append(p)
    from collections import Counter
    c = Counter(p["market_ticker"].split("-")[0] for p in cand)
    print("ACTIVE-NOW programs by family:", dict(c), flush=True)
    json.dump(cand, open(os.path.join(CACHE, "active_now_programs.json"), "w"), indent=1)

    # 3. market meta for candidates -> curfew on market close_time
    survivors = []
    for p in cand:
        t = p["market_ticker"]
        mf = os.path.join(CACHE, "markets", f"{t}.json")
        if os.path.exists(mf):
            m = json.load(open(mf))
        else:
            try:
                m = get(f"/markets/{t}").get("market", {})
            except Exception as e:
                print(f"  MKTFAIL {t}: {e}", flush=True)
                continue
            json.dump(m, open(mf, "w"))
            time.sleep(0.7)
        close = m.get("close_time") or m.get("expiration_time")
        if not close:
            continue
        ct = parse_ts(close)
        en = parse_ts(p["end_date"])
        eff = min(ct, en)  # effective window expiry for the seat
        if eff >= CURFEW and m.get("status") in ("open", "active"):
            survivors.append({"program": p, "market": m,
                              "eff_expiry": eff.isoformat(),
                              "hrs_to_expiry": (eff - NOW).total_seconds() / 3600})
    print(f"CURFEW survivors (>=24h, open): {len(survivors)}", flush=True)
    json.dump(survivors, open(os.path.join(CACHE, "curfew_survivors.json"), "w"), indent=1, default=str)

    # 4. orderbooks for survivors
    for s in survivors:
        t = s["program"]["market_ticker"]
        bf = os.path.join(CACHE, "books", f"{t}.json")
        if os.path.exists(bf):
            continue
        try:
            b = get(f"/markets/{t}/orderbook", {"depth": 100})
            json.dump(b, open(bf, "w"))
        except Exception as e:
            print(f"  BOOKFAIL {t}: {e}", flush=True)
        time.sleep(0.7)
    print("ALLDONE", flush=True)


if __name__ == "__main__":
    main()
