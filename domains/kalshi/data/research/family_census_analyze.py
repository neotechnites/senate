#!/usr/bin/env python3
"""Family census analyzer. Read-only, operates on family_census_cache/ only."""
import json, os, sys, math, statistics as st, datetime as dt, collections

ROOT = "/Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research"
CACHE = os.path.join(ROOT, "family_census_cache")
LIP = {  # live-window period_reward($) / target_size_fp -> $ per posted contract ceiling
    "KXFEDFUNDSYEAR": (25.0, 1000, 168), "KXUSCPIYEAR": (25.0, 1000, 168),
    "KXNOMGDPGROWTH": (25.0, 1000, 175), "KXH200MS": (15.0, 1000, 336),
    "KXB200MS": (15.0, 1000, 336), "KXROLEATEVENTCOACHELLA": (50.0, 1000, 242),
    "KXYTVIEWSW": (100.0, 1000, 166), "KXSTATEBALLOTMEASURE": (285.0, 1000, 110),
}


def wilson(k, n):
    if n == 0:
        return (0.0, 0.0, 0.0)
    p = k / n; z = 1.96; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (p, max(0, c - h), min(1, c + h))


def ci_mean(x):
    if len(x) < 2:
        return (x[0] if x else 0.0, float("nan"), float("nan"))
    m = st.mean(x); s = st.stdev(x) / math.sqrt(len(x))
    return (m, m - 1.96 * s, m + 1.96 * s)


def ts(s):
    s = s.replace("Z", "+00:00")
    if "." in s:
        head, rest = s.split(".", 1)
        frac, tz = rest[:-6], rest[-6:]
        s = f"{head}.{frac[:6].ljust(6, '0')}{tz}"
    return dt.datetime.fromisoformat(s)


def load(fam):
    smp = json.load(open(os.path.join(CACHE, f"sample2_{fam}.json")))
    meta = {m["ticker"]: m for m in json.load(open(os.path.join(CACHE, f"markets_{fam}.json")))}
    out = []
    for t in smp["sample"]:
        p = os.path.join(CACHE, "trades", f"{t}.json")
        if not os.path.exists(p):
            continue
        tr = json.load(open(p))
        tr.sort(key=lambda x: x["created_time"])
        out.append((t, meta.get(t, {}), tr))
    return smp, out


def yesprice(tr):
    return float(tr.get("yes_price_dollars") or (tr.get("yes_price", 0) / 100.0))


def lip_windows(fam):
    """Distinct (start,end) LIP windows for this family, from the captured
    incentive_programs payload (temp_census_cache/incentive_programs_all.json)."""
    global _IP
    try:
        _IP
    except NameError:
        _IP = json.load(open(os.path.join(ROOT, "temp_census_cache",
                                          "incentive_programs_all.json")))
    w = collections.defaultdict(set)
    for r in _IP:
        mt = r.get("market_ticker") or ""
        if mt.split("-")[0] == fam:
            w[mt].add((ts(r["start_date"]), ts(r["end_date"]), float(r["period_reward"]) / 1e4,
                       float(r["target_size_fp"])))
    return {k: sorted(v) for k, v in w.items()}


def analyze(fam):
    smp, mk = load(fam)
    rew, tgt, hrs = LIP[fam]
    ceil = rew / tgt
    n = len(mk)
    ntr = [len(t) for _, _, t in mk]
    zero = sum(1 for x in ntr if x == 0)

    # --- tape span / prints per day
    spans, ppd = [], []
    for _, _, tr in mk:
        if len(tr) >= 2:
            d = (ts(tr[-1]["created_time"]) - ts(tr[0]["created_time"])).total_seconds() / 86400
            spans.append(d)
            ppd.append(len(tr) / max(d, 1 / 24))

    # --- ARM: in-band maker seat, per LIP WINDOW (the unit the subsidy is paid on).
    # Windows come from incentive_programs (period_reward is per window per market).
    # For each (market, window): entry price = last print at-or-before window start,
    # else first print inside the window. Join the touch on the CHEAPER side at
    # q = min(p,1-p); require q in [0.15,0.85]; NEVER move. Fill = any later print in
    # the window that would trade through a resting bid at q on our side.
    # Verified side semantics (temp census): resting YES bid at q is hit by a print with
    # yes_price<=q AND taker_side=="no"; resting NO bid at q by yes_price>=1-q AND
    # taker_side=="yes". Perfect queue priority => every fill rate is an UPPER BOUND.
    WINMAP = lip_windows(fam)
    nprog = len(WINMAP)
    ceils = []
    perwin = collections.defaultdict(lambda: [0, 0, 0, []])  # window -> [mktwin, seats, fills, drift]
    seats = 0; fills = 0; losses = []; itm = 0; nres = 0; drifts = []
    transit = 0; mktwins = 0
    for tk, m, tr in mk:
        px = [yesprice(x) for x in tr]
        if any(0.15 <= p <= 0.85 for p in px):
            transit += 1
        if not tr:
            continue
        T = [ts(x["created_time"]) for x in tr]
        for (ws, we, prw, ptg) in WINMAP.get(tk, ()):
            mktwins += 1
            ceils.append(prw / ptg)
            PW = perwin[(ws.isoformat()[:10], we.isoformat()[:10], prw)]
            PW[0] += 1
            pre = [px[i] for i in range(len(tr)) if T[i] <= ws]
            inw = [i for i in range(len(tr)) if ws < T[i] <= we]
            p0 = pre[-1] if pre else (px[inw[0]] if inw else None)
            if p0 is None:
                continue
            side = "yes" if p0 <= 0.5 else "no"
            q = min(p0, 1 - p0)
            if not (0.15 <= q <= 0.85):
                continue
            seats += 1; PW[1] += 1
            hit = None
            start = inw[0] if (not pre and inw) else None
            for i in inw:
                if start is not None and i == start:
                    continue
                yp = px[i]; tside = tr[i].get("taker_side")
                if side == "yes" and yp <= q and tside == "no":
                    hit = i; break
                if side == "no" and (1 - yp) <= q and tside == "yes":
                    hit = i; break
            if hit is None:
                continue
            fills += 1; PW[2] += 1
            post = [px[i] for i in inw if i > hit]
            last = post[-1] if post else px[hit]
            ourmark = last if side == "yes" else 1 - last
            drifts.append(ourmark - q); PW[3].append(ourmark - q)
            res = (m.get("result") or "").lower()
            if res in ("yes", "no"):
                nres += 1
                won = 1.0 if res == side else 0.0
                itm += won
                losses.append(q - won)
    # transit rate per day (band presence normalised by tape span)
    md_span = st.median(spans) if spans else float("nan")

    P_t, tl, th = wilson(transit, n)
    P_f, fl, fh = wilson(fills, seats)
    L, ll, lh = ci_mean(losses) if losses else (float("nan"),) * 3
    D, dl, dh = ci_mean(drifts) if drifts else (float("nan"),) * 3
    # scale-free kill: use settlement loss when resolved population exists, else mark drift
    if losses and len(losses) >= 10:
        basis, B, blo, bhi = "settlement", L, ll, lh
    else:
        basis, B, blo, bhi = "markdrift", -D, -dh, -dl
    adverse = P_f * B if not math.isnan(B) else float("nan")
    print(f"\n=== {fam}  (LIP ${rew}/window /{tgt} = ${ceil:.4f} per posted contract, {hrs}h window)")
    print(f"  population all={smp['population_all']} resolved={smp['population_resolved']} "
          f"open/active={smp['population_open']}  sampled n={n}")
    print(f"  zero-trade markets: {zero}/{n} = {zero/n:.3f}   median prints {st.median(ntr):.0f}  "
          f"p90 {sorted(ntr)[int(.9*len(ntr))]:.0f}  total {sum(ntr)}")
    print(f"  median tape span {md_span:.2f} d   median prints/day {st.median(ppd) if ppd else float('nan'):.2f}")
    print(f"  P(tape ever in 15-85c band) = {P_t:.4f} [{tl:.4f},{th:.4f}]  ({transit}/{n})")
    print(f"  LIP-funded markets in feed = {nprog}; sampled markets with a program = "
          f"{sum(1 for t,_,_ in mk if t in WINMAP)}  -> market-windows evaluated {mktwins}")
    print(f"  in-band seats established   = {seats}  ({seats/max(mktwins,1):.3f} of market-windows)")
    print(f"  P(filled|seated) perfectQ   = {P_f:.4f} [{fl:.4f},{fh:.4f}]  ({fills}/{seats})")
    if drifts:
        print(f"  post-fill mark drift our side = {D:+.4f} [{dl:+.4f},{dh:+.4f}]  n={len(drifts)}")
    if losses:
        print(f"  settled loss/contract (entry-payoff) = {L:+.4f} [{ll:+.4f},{lh:+.4f}]  n={len(losses)}"
              f"   P(our side ITM) = {itm/nres:.4f} ({itm:.0f}/{nres})")
    print("  per-LIP-window (start end reward$ | mktwins seats fills P(fill) meanDrift):")
    for k in sorted(perwin):
        v = perwin[k]
        pf = v[2] / v[1] if v[1] else float("nan")
        dr = st.mean(v[3]) if v[3] else float("nan")
        print(f"    {k[0]}..{k[1]} ${k[2]:6.2f} | {v[0]:5d} {v[1]:5d} {v[2]:5d}  {pf:.3f}  {dr:+.4f}")
    print(f"  --- KILL ARITHMETIC (basis={basis}) ---")
    print(f"  adverse selection / posted contract = {P_f:.4f} x {B:+.4f} = ${adverse:+.4f}")
    print(f"  LIP ceiling / posted contract       = ${ceil:.4f}")
    print(f"  NET / posted contract / window      = ${ceil - adverse:+.4f}"
          f"   [{ceil - P_f*bhi:+.4f}, {ceil - P_f*blo:+.4f}]")
    return dict(fam=fam, ceil=ceil, n=n, zero=zero / n, P_t=P_t, seats=seats, P_f=P_f,
                adverse=adverse, net=ceil - adverse, basis=basis)


def band_now(fam):
    mk = json.load(open(os.path.join(CACHE, f"markets_{fam}.json")))
    a = [m for m in mk if m["status"] == "active"]
    def F(x):
        try: return float(x)
        except: return None
    inb = out = nq = 0
    for m in a:
        b, k = F(m.get("yes_bid_dollars")), F(m.get("yes_ask_dollars"))
        if not b or not k or b <= 0.01 or k >= 0.99:
            b2 = [v for v in (b, k) if v and 0.02 <= v <= 0.98]
            if not b2:
                nq += 1; continue
            mid = sum(b2) / len(b2)
        else:
            mid = (b + k) / 2
        if 0.15 <= mid <= 0.85: inb += 1
        else: out += 1
    tot = len(a)
    print(f"  LIVE BAND CENSUS ({tot} active markets, mid ex-1c/99c): in 15-85c band "
          f"{inb} ({inb/max(tot,1):.3f}), outside {out}, unquotable {nq}")
    return inb, tot


def books(fam):
    d = os.path.join(CACHE, "books")
    rows = []
    for fn in sorted(os.listdir(d)):
        if not fn.startswith(fam + "-"):
            continue
        j = json.load(open(os.path.join(d, fn)))
        b = j.get("orderbook_fp") or j.get("orderbook") or {}
        Y = [(float(p), float(sz)) for p, sz in (b.get("yes_dollars") or [])]
        N = [(float(p), float(sz)) for p, sz in (b.get("no_dollars") or [])]
        rows.append((fn[:-5], Y, N))
    if not rows:
        print("  BOOK: no snapshots"); return
    # PHANTOM RULE: 1c and 99c levels are excluded from every depth/touch number
    # (known instrument defect; they are not real liquidity).
    def real(L):
        return [(p, s) for p, s in L if 0.02 <= p <= 0.98]
    sp, dy, dn, rb, ra, ph, one_sided, empty = [], [], [], [], [], 0, 0, 0
    for tk, Y, N in rows:
        if any(p <= 0.011 for p, _ in Y + N) or any(p >= 0.989 for p, _ in Y + N):
            ph += 1
        Yr, Nr = real(Y), real(N)
        if not Yr or not Nr:
            (empty if not (Yr or Nr) else one_sided)
            if not Yr and not Nr:
                empty += 1
            else:
                one_sided += 1
            continue
        bb = max(p for p, _ in Yr)
        ba = 1.0 - max(p for p, _ in Nr)
        sp.append(ba - bb)
        dy.append(sum(s for p, s in Yr if p >= bb - 0.03))
        dn.append(sum(s for p, s in Nr if p >= (1 - ba) - 0.03))
        rb.append(sum(s for p, s in Yr if abs(p - bb) < 1e-9))
        ra.append(sum(s for p, s in Nr if abs(p - (1 - ba)) < 1e-9))
    print(f"  BOOK {len(rows)} live snapshots: two-sided(ex 1c/99c) {len(sp)}, "
          f"one-sided {one_sided}, empty {empty}, phantom 1c/99c level present {ph}/{len(rows)}")
    if not sp:
        return
    print(f"  spread median {st.median(sp)*100:.1f}c (p25 {sorted(sp)[len(sp)//4]*100:.1f}c, "
          f"p75 {sorted(sp)[3*len(sp)//4]*100:.1f}c) | depth within 3 ticks of touch (ex 1c/99c): median YES {st.median(dy):.0f} NO {st.median(dn):.0f}")
    rt = st.median(rb) + st.median(ra)
    rew, tgt, hrs = LIP[fam]
    print(f"  RIVAL MAKERS at touch (ex-phantom): median yes-bid {st.median(rb):.0f}, "
          f"no-bid {st.median(ra):.0f}, combined {rt:.0f}")
    print(f"  pro-rata haircut posting 1000: share {1000/(1000+rt):.3f} -> effective "
          f"${rew/tgt*(1000/(1000+rt)):.4f}/posted contract (vs ceiling ${rew/tgt:.4f})")


if __name__ == "__main__":
    for f in sys.argv[1:]:
        try:
            analyze(f); band_now(f); books(f)
        except Exception as e:
            import traceback; traceback.print_exc()
