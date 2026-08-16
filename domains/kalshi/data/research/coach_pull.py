#!/usr/bin/env python3
# COACHELLA targeted pull. Same preregistered rule: full population, seeded shuffle
# (seed 20260815), unbiased prefix. Read-only, keyless.
import json, os, random, ssl, sys, time, urllib.request, urllib.parse
sys.path.insert(0, "/Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research")
from family_census_pull import get, enumerate_markets, pull_trades, pull_book, CACHE, SEED
F = "KXROLEATEVENTCOACHELLA"
mk = enumerate_markets(F)
rng = random.Random(SEED)
tk = sorted(m["ticker"] for m in mk); rng.shuffle(tk)
op = sorted(m["ticker"] for m in mk if m["status"] == "active")
json.dump({"seed": SEED, "series": F, "population_all": len(mk),
           "population_resolved": len(mk), "population_open": len(op),
           "sample": tk, "open": op},
          open(os.path.join(CACHE, f"sample2_{F}.json"), "w"), indent=1)
for i, t in enumerate(tk):
    try:
        n = len(pull_trades(t))
        if i % 10 == 0: print(f"  {i}/{len(tk)} {t} n={n}", flush=True)
    except Exception as e: print("FAIL", t, e, flush=True)
    time.sleep(0.6)
for t in op[:30]:
    try: pull_book(t)
    except Exception as e: print("BOOKFAIL", t, e, flush=True)
    time.sleep(0.6)
print("COACHDONE", flush=True)
