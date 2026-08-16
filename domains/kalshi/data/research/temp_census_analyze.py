#!/usr/bin/env python3
"""
Analysis for the preregistered KXTEMPCHIH maker-side census. Read-only, on-disk.

SIDE SEMANTICS (verified from the tape, only two combos exist in 1,337 prints):
  taker_side="yes" (outcome yes, book_side bid) -> taker BOUGHT YES
      => the resting order that filled was a NO bid at no_price.
  taker_side="no"  (outcome no,  book_side ask) -> taker BOUGHT NO
      => the resting order that filled was a YES bid at yes_price.
So a resting YES bid at c is hit only by a print with yes_price==c AND taker_side=="no".
   a resting NO  bid at c is hit only by a print with no_price ==c AND taker_side=="yes".
Queue priority is assumed PERFECT (we are always front of queue) => every number
below is an UPPER BOUND on fill rate and on favourable outcomes.
"""
import json, math
from pathlib import Path

ROOT = Path("/Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research")
CACHE = ROOT / "temp_census_cache"
TRADES = CACHE / "trades"

sample = json.loads((CACHE / "sample.json").read_text())
meta = json.loads((CACHE / "market_meta.json").read_text())


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (p, max(0.0, c - h), min(1.0, c + h))


def load(t):
    f = TRADES / f"{t}.json"
    if not f.exists():
        return None
    return sorted(json.loads(f.read_text()), key=lambda x: x["created_time"])


def yp(tr):
    return round(float(tr["yes_price_dollars"]), 4)


def sz(tr):
    return float(tr.get("count_fp") or tr.get("count") or 0)


def result_of(t):
    return ((meta.get(t, {}) or {}).get("result") or "").lower()


tickers = [t for t in sample["tickers"]
           if load(t) is not None and result_of(t) in ("yes", "no")]
print(f"# analyzed: {len(tickers)} markets (sample {sample['n']}, "
      f"population {sample['population']}, {len(sample['days'])} days)")

data = {t: load(t) for t in tickers}
res = {t: result_of(t) for t in tickers}
N = len(tickers)

nz = sum(1 for t in tickers if not data[t])
print(f"markets with ZERO prints all hour: {nz}/{N} = {nz/N:.4f}")
cnt = sorted(len(data[t]) for t in tickers)
print(f"total prints {sum(cnt)}; median prints/market {cnt[N//2]}; "
      f"p90 {cnt[int(N*0.9)]}; max {cnt[-1]}")
print(f"settlement base rate P(YES) = {sum(1 for t in tickers if res[t]=='yes')/N:.4f}")

print("\n## ARM 1 - always-resting deep bid, BOTH sides, every market-window")
for c in (0.01, 0.02, 0.03):
    yes_fill, no_fill = [], []
    for t in tickers:
        tr = data[t]
        if any(abs(yp(x) - c) < 1e-9 and x["taker_side"] == "no" for x in tr):
            yes_fill.append(t)
        if any(abs(yp(x) - (1 - c)) < 1e-9 and x["taker_side"] == "yes" for x in tr):
            no_fill.append(t)
    either = set(yes_fill) | set(no_fill)
    p, lo, hi = wilson(len(either), N)
    cc = int(round(c * 100))
    print(f"\n-- resting {cc}c on BOTH sides --")
    print(f"P(this market ever fills us at {cc}c) = {p:.4f} [{lo:.4f},{hi:.4f}] "
          f"({len(either)}/{N})")

    yw = sum(1 for t in yes_fill if res[t] == "yes")
    nw = sum(1 for t in no_fill if res[t] == "no")
    if yes_fill:
        pp, l2, h2 = wilson(yw, len(yes_fill))
        print(f"  YES {cc}c bid filled: {len(yes_fill)} mkts | "
              f"P(settle YES | filled) = {pp:.4f} [{l2:.4f},{h2:.4f}] ({yw}/{len(yes_fill)})")
    if no_fill:
        pp, l2, h2 = wilson(nw, len(no_fill))
        print(f"  NO  {cc}c bid filled: {len(no_fill)} mkts | "
              f"P(settle NO  | filled) = {pp:.4f} [{l2:.4f},{h2:.4f}] ({nw}/{len(no_fill)})")

    nf, wins = len(yes_fill) + len(no_fill), yw + nw
    if nf:
        ev = (wins - nf * c) / nf
        pw, wl, wh = wilson(wins, nf)
        print(f"  P(win | filled) = {pw:.4f} [{wl:.4f},{wh:.4f}]  "
              f"(breakeven = {c:.2f}; lottery premise assumes >= {c:.2f})")
        print(f"  EV per FILLED contract = ${ev:+.4f}  "
              f"[CI ${wl-c:+.4f}, ${wh-c:+.4f}]")
        print(f"  EV per MARKET-WINDOW (1 ct/side attempted, maker fee $0) "
              f"= ${(wins - nf*c)/N:+.5f}")
    # queue we must beat
    depth = []
    for t in yes_fill:
        depth.append(sum(sz(x) for x in data[t]
                         if abs(yp(x) - c) < 1e-9 and x["taker_side"] == "no"))
    for t in no_fill:
        depth.append(sum(sz(x) for x in data[t]
                         if abs(yp(x) - (1 - c)) < 1e-9 and x["taker_side"] == "yes"))
    if depth:
        depth.sort()
        print(f"  contracts printed at that tick per filled mkt: "
              f"median {depth[len(depth)//2]:.0f}, p90 {depth[int(len(depth)*0.9)]:.0f}, "
              f"max {depth[-1]:.0f}, TOTAL {sum(depth):.0f} across {N} mkts")

print("\n## ARM 1b - WHEN does the 1c fill land? (noise would be uniform; informed is late)")
from datetime import datetime


def frac(t, x):
    m = meta.get(t, {}) or {}
    try:
        o = datetime.fromisoformat(m["open_time"].replace("Z", "+00:00"))
        c = datetime.fromisoformat(m["close_time"].replace("Z", "+00:00"))
        s = datetime.fromisoformat(x["created_time"].replace("Z", "+00:00"))
        span = (c - o).total_seconds()
        return (s - o).total_seconds() / span if span > 0 else None
    except Exception:
        return None


fr = []
for t in tickers:
    for x in data[t]:
        p = yp(x)
        if (abs(p - 0.01) < 1e-9 and x["taker_side"] == "no") or \
           (abs(p - 0.99) < 1e-9 and x["taker_side"] == "yes"):
            f = frac(t, x)
            if f is not None:
                fr.append(f)
            break
if fr:
    fr.sort()
    print(f"n={len(fr)} first-1c-fills; elapsed fraction of the hour at fill: "
          f"median {fr[len(fr)//2]:.3f}, p25 {fr[len(fr)//4]:.3f}, "
          f"p75 {fr[int(len(fr)*0.75)]:.3f}, mean {sum(fr)/len(fr):.3f}")
    print(f"  share of 1c fills in the LAST third of the window: "
          f"{sum(1 for f in fr if f > 2/3)/len(fr):.4f}  (uniform noise would be 0.333)")


def arm2_run(tks, label):
    transit = seated = filled = 0
    pnl, entries, drift = [], [], []
    for t in tks:
        tr = data[t]
        if not tr:
            continue
        ps = [yp(x) for x in tr]
        if any(0.15 <= p <= 0.85 for p in ps):
            transit += 1
        p1 = ps[0]
        side = "yes" if p1 < 0.50 else "no"
        q = round(min(p1, 1 - p1), 4)
        if not (0.15 <= q <= 0.85):
            continue
        seated += 1
        entries.append(q)
        hit = None
        for x in tr[1:]:
            if side == "yes" and x["taker_side"] == "no" and yp(x) <= q + 1e-9:
                hit = 1; break
            if side == "no" and x["taker_side"] == "yes" and (1 - yp(x)) <= q + 1e-9:
                hit = 1; break
        if hit:
            filled += 1
            pnl.append((1.0 if res[t] == side else 0.0) - q)
            last = ps[-1]
            drift.append((last if side == "yes" else round(1 - last, 4)) - q)
    n2 = len(tks)
    print(f"\n### {label}  (n={n2})")
    p, lo, hi = wilson(transit, n2)
    print(f"P(price transits 15-85c band) = {p:.4f} [{lo:.4f},{hi:.4f}] ({transit}/{n2})")
    if not seated:
        return
    p, lo, hi = wilson(filled, seated)
    mq = sum(entries)/len(entries)
    print(f"in-band seats (first print in band): {seated}; mean entry ${mq:.4f}")
    print(f"P(filled | seated, PERFECT queue) = {p:.4f} [{lo:.4f},{hi:.4f}] ({filled}/{seated})")
    if not pnl:
        return
    m = sum(pnl)/len(pnl)
    sd = (sum((x-m)**2 for x in pnl)/max(1,len(pnl)-1))**0.5
    se = sd/math.sqrt(len(pnl))
    w = sum(1 for x in pnl if x > 0)
    pw, wl, wh = wilson(w, len(pnl))
    print(f"FILLED n={len(pnl)}: mean settlement-minus-entry = ${m:+.4f} "
          f"95%CI [${m-1.96*se:+.4f}, ${m+1.96*se:+.4f}]")
    print(f"  P(filled side settles ITM) = {pw:.4f} [{wl:.4f},{wh:.4f}] ({w}/{len(pnl)})")
    md = sum(drift)/len(drift)
    print(f"  post-fill mark drift (last print - entry, our side) = ${md:+.4f}")
    # scale-free seat economics vs SOURCED LIP
    fillp = filled/seated
    adverse = fillp * (-m)
    for series, pr in (("KXTEMPCHIH", 1200000), ("KXTEMPMIAH", 800000)):
        sub = (pr*1e-4)/1000.0   # period_reward USD / target_size_fp contracts
        print(f"  [{series}] LIP ceiling ${sub:.4f}/posted-contract/window "
              f"(={pr*1e-4:.0f} USD / 1000 target, decay 0.5^0 at touch) "
              f"vs adverse ${adverse:.4f} -> NET ${sub-adverse:+.4f}/contract")
        lo_l = fillp*(-(m+1.96*se)); hi_l = fillp*(-(m-1.96*se))
        print(f"      net at 95%CI bounds of adverse: "
              f"[${sub-hi_l:+.4f}, ${sub-lo_l:+.4f}]")
        print(f"      at $50 cap = {50/mq:.0f} contracts: "
              f"${(sub-adverse)*(50/mq):+.2f}/seated window")

print("\n## ARM 2 - in-band (15-85c) maker seat")
arm2 = [t for t in sample["arm2"] if t in data]
arm2_run(arm2, "PRIMARY - preregistered n=100 subsample")
arm2_run(tickers, "SECONDARY - extended seed-ordered prefix (order fixed pre-data)")
