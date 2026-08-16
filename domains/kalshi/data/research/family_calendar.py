#!/usr/bin/env python3
"""Speed character: is the tape concentrated on a KNOWN scheduled calendar?"""
import json, os, sys, collections, statistics as st
C = "/Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research/family_census_cache"
# 2026 scheduled prints (public calendars, stated here as the hypothesis to be TESTED
# against the tape - the tape is the receipt, this list is only the gate definition)
FOMC = {"2026-07-29", "2026-09-16", "2026-11-04", "2026-12-16"}   # decision days
CPI  = {"2026-08-12", "2026-07-14", "2026-09-11", "2026-10-13"}   # BLS CPI releases
GDP  = {"2026-07-30", "2026-08-27", "2026-09-24"}                 # BEA GDP releases
CAL = {"KXFEDFUNDSYEAR": FOMC | CPI, "KXUSCPIYEAR": CPI | FOMC, "KXNOMGDPGROWTH": GDP | CPI | FOMC}

for fam in sys.argv[1:]:
    smp = json.load(open(os.path.join(C, f"sample2_{fam}.json")))
    byday = collections.Counter(); vol = collections.Counter(); nm = 0
    for t in smp["sample"]:
        p = os.path.join(C, "trades", f"{t}.json")
        if not os.path.exists(p): continue
        nm += 1
        for x in json.load(open(p)):
            d = x["created_time"][:10]
            byday[d] += 1; vol[d] += float(x["count_fp"])
    tot = sum(byday.values()); totv = sum(vol.values())
    cal = CAL.get(fam, set())
    # event day = release day or the day after (release 8:30am ET / 2pm ET)
    ev = set()
    import datetime as dt
    for d in cal:
        D = dt.date.fromisoformat(d); ev.add(d); ev.add((D + dt.timedelta(days=1)).isoformat())
    days = sorted(byday)
    ed = [d for d in days if d in ev]
    en = sum(byday[d] for d in ed); evv = sum(vol[d] for d in ed)
    print(f"\n== {fam}  markets={nm} prints={tot} contracts={totv:.0f} over {len(days)} tape days")
    print(f"   scheduled-event days present in tape: {ed}")
    print(f"   share of PRINTS on event day or day+1 : {en}/{tot} = {en/max(tot,1):.3f}"
          f"   (uniform would be {len(ed)/max(len(days),1):.3f})")
    print(f"   share of CONTRACTS on those days      : {evv:.0f}/{totv:.0f} = {evv/max(totv,1):.3f}")
    print("   prints by day:", " ".join(f"{d[5:]}:{byday[d]}{'*' if d in ev else ''}" for d in days))
