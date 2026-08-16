#!/usr/bin/env python3
"""Unified scale-free comparison. Reads the analyzer, adds the rival haircut and the
per-contract-HOUR normalisation (window lengths differ 110h..336h, so $/window is not
comparable across families)."""
import io, sys, contextlib, importlib
sys.path.insert(0, "/Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research")
import family_census_analyze as A

FAMS = ["KXFEDFUNDSYEAR", "KXUSCPIYEAR", "KXNOMGDPGROWTH", "KXH200MS", "KXB200MS",
        "KXROLEATEVENTCOACHELLA", "KXYTVIEWSW"]
rows = []
for f in FAMS:
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            r = A.analyze(f); A.band_now(f); A.books(f)
    except Exception as e:
        print(f"{f}: SKIP ({e})"); continue
    txt = buf.getvalue()
    eff = None
    for line in txt.splitlines():
        if "effective $" in line:
            eff = float(line.split("effective $")[1].split("/")[0])
    rew, tgt, hrs = A.LIP[f]
    ceil = rew / tgt
    adv = r["adverse"]
    rows.append(dict(fam=f, hrs=hrs, ceil=ceil, adv=adv, net=ceil - adv,
                     eff=eff, netr=(eff - adv) if eff is not None else None))
# ballot baseline, measured by the identical method in this census
rows.append(dict(fam="KXSTATEBALLOTMEASURE*", hrs=110, ceil=0.2850, adv=0.0683,
                 net=0.2167, eff=None, netr=None))
print(f"{'family':26}{'win_h':>6}{'ceil$/ct':>10}{'adverse$':>10}{'NET$/ct':>9}"
      f"{'effCeil':>9}{'NETrival':>10}{'NET $/ct-hr':>13}{'vs ballot':>10}")
base = None
for r in rows:
    if r["fam"].startswith("KXSTATE"): base = r["net"] / r["hrs"]
for r in rows:
    ph = (r["netr"] if r["netr"] is not None else r["net"]) / r["hrs"]
    e = f"{r['eff']:.4f}" if r["eff"] is not None else "   -  "
    nr = f"{r['netr']:+.4f}" if r["netr"] is not None else "   -   "
    print(f"{r['fam']:26}{r['hrs']:6d}{r['ceil']:10.4f}{r['adv']:+10.4f}{r['net']:+9.4f}"
          f"{e:>9}{nr:>10}{ph:+13.2e}{(ph/base if base else 0):9.3f}x")
