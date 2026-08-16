#!/usr/bin/env python3
"""S1 backtest: 226 settled KXEARNINGSMENTION word-markets, 14 companies.

Price = last trade at or before 23:59:59 UTC the day BEFORE the call (a genuinely
tradeable, days-early price). Model sees only transcripts with call_date < call date.
Reports calibration and would-have taker edge in-band 15-85c after ceil-to-1c fees.
"""
import json, os, sys, math, datetime, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s1_word_predictor import predict, taker_fee_cents, load_transcripts

R = os.path.dirname(os.path.abspath(__file__))
C = os.path.join(R, "s1_transcript_cache")
M = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
     'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}


def call_date(ev):
    d = ev.split('-')[1]
    return f"20{d[:2]}-{M[d[2:5]]:02d}-{int(d[5:]):02d}"


def load_markets():
    out = []
    for l in open(os.path.join(C, "markets_raw.jsonl")):
        l = l.strip()
        if not l:
            continue
        for m in json.loads(l).get("markets", []):
            if m.get("result") not in ("yes", "no"):
                continue
            out.append({"ticker": m["ticker"], "event": m["event_ticker"],
                        "company": m["event_ticker"].replace("KXEARNINGSMENTION", "").split("-")[0],
                        "word": m["custom_strike"]["Word"],
                        "call_date": call_date(m["event_ticker"]),
                        "result": m["result"]})
    return out


def load_prices():
    """ticker -> last pre-call yes price in cents (volume-weighted over the last 5 trades)."""
    px, cur = {}, None
    for l in open(os.path.join(C, "precall_trades.txt")):
        s = l.strip()
        if s.startswith("KXEARNINGSMENTION"):
            cur = s
        elif s.startswith("{") and cur:
            tr = json.loads(s).get("trades", [])
            if tr:
                use = tr[:5]
                num = sum(float(t["yes_price_dollars"]) * float(t["count_fp"]) for t in use)
                den = sum(float(t["count_fp"]) for t in use)
                px[cur] = round(100 * num / den, 1)
            cur = None
    return px


def run(prior_a=1.5, prior_p=None, n_lb=6, loco=True, verbose=True):
    mkts = load_markets()
    px = load_prices()
    rows = []
    # global prior, leave-one-company-out
    by_co = collections.defaultdict(list)
    for m in mkts:
        by_co[m["company"]].append(1 if m["result"] == "yes" else 0)
    tot_y = sum(sum(v) for v in by_co.values())
    tot_n = sum(len(v) for v in by_co.values())

    for m in mkts:
        if m["ticker"] not in px:
            continue
        p0 = prior_p
        if p0 is None:
            if loco:
                y = tot_y - sum(by_co[m["company"]])
                n = tot_n - len(by_co[m["company"]])
                p0 = y / n
            else:
                p0 = tot_y / tot_n
        r = predict(m["company"], [m["word"]], asof=m["call_date"],
                    n_lookback=n_lb, prior_p=p0, prior_a=prior_a)[0]
        if r["n"] == 0:
            continue
        y = 1 if m["result"] == "yes" else 0
        price = px[m["ticker"]]
        # taker: cross the observed last price (conservative: no spread assumed, we pay `price`
        # for YES or 100-price for NO -- the actual ask would be a touch worse)
        e_yes = (r["p"] * 100 - price) - taker_fee_cents(price)
        e_no = ((1 - r["p"]) * 100 - (100 - price)) - taker_fee_cents(100 - price)
        side, entry, edge = ("YES", price, e_yes) if e_yes >= e_no else ("NO", 100 - price, e_no)
        pnl = ((100 - entry) if ((side == "YES") == (y == 1)) else -entry) - taker_fee_cents(entry)
        rows.append({**m, "p": r["p"], "k": r["k"], "n": r["n"], "price": price, "y": y,
                     "side": side, "entry": entry, "edge": edge, "pnl": pnl,
                     "inband": 15 <= price <= 85, "p0": p0})
    return rows


def summarize(rows, label=""):
    def stats(rs):
        if not rs:
            return None
        n = len(rs)
        brier_m = sum((r["p"] - r["y"]) ** 2 for r in rs) / n
        brier_k = sum((r["price"] / 100 - r["y"]) ** 2 for r in rs) / n
        ll_m = sum(math.log(max(1e-6, r["p"] if r["y"] else 1 - r["p"])) for r in rs) / n
        ll_k = sum(math.log(max(1e-6, r["price"] / 100 if r["y"] else 1 - r["price"] / 100)) for r in rs) / n
        return n, brier_m, brier_k, ll_m, ll_k

    print(f"\n=== {label} ===")
    for nm, rs in [("ALL", rows), ("in-band 15-85c", [r for r in rows if r["inband"]]),
                   ("wings", [r for r in rows if not r["inband"]])]:
        s = stats(rs)
        if not s:
            continue
        n, bm, bk, lm, lk = s
        print(f"{nm:<16} n={n:<4} Brier model={bm:.4f} market={bk:.4f}  "
              f"logloss model={-lm:.4f} market={-lk:.4f}")

    for nm, rs in [("ALL", rows), ("in-band 15-85c", [r for r in rows if r["inband"]]),
                   ("in-band & edge>=5c", [r for r in rows if r["inband"] and r["edge"] >= 5]),
                   ("in-band & edge>=10c", [r for r in rows if r["inband"] and r["edge"] >= 10]),
                   ("in-band & edge>=20c", [r for r in rows if r["inband"] and r["edge"] >= 20])]:
        if not rs:
            continue
        n = len(rs)
        mp = sum(r["pnl"] for r in rs) / n
        wr = sum(1 for r in rs if r["pnl"] > 0) / n
        sd = (sum((r["pnl"] - mp) ** 2 for r in rs) / max(1, n - 1)) ** 0.5
        t = mp / (sd / n ** 0.5) if sd else 0
        # company-clustered t
        cl = collections.defaultdict(list)
        for r in rs:
            cl[r["company"]].append(r["pnl"])
        cm = [sum(v) / len(v) for v in cl.values()]
        cmm = sum(cm) / len(cm)
        csd = (sum((x - cmm) ** 2 for x in cm) / max(1, len(cm) - 1)) ** 0.5
        ct = cmm / (csd / len(cm) ** 0.5) if csd else 0
        print(f"{nm:<20} n={n:<4} edge/ct={mp:+7.2f}c  win={wr:.3f}  t={t:+.2f}  "
              f"clusters={len(cl)} clust_t={ct:+.2f}")

    # calibration deciles
    print("calibration (model P bucket -> realized yes rate):")
    b = collections.defaultdict(list)
    for r in rows:
        b[min(9, int(r["p"] * 10))].append(r["y"])
    for k in sorted(b):
        v = b[k]
        print(f"  P {k/10:.1f}-{(k+1)/10:.1f}  n={len(v):<4} realized={sum(v)/len(v):.3f}")


if __name__ == "__main__":
    rows = run()
    json.dump(rows, open(os.path.join(C, "backtest_rows.json"), "w"), indent=0)
    summarize(rows, "S1 backtest, LOCO prior, a=1.5, n_lb=6")
    if "--sweep" in sys.argv:
        for a in (0.5, 1.0, 1.5, 3.0):
            for nlb in (4, 6, 8):
                rs = run(prior_a=a, n_lb=nlb)
                ib = [r for r in rs if r["inband"]]
                mp = sum(r["pnl"] for r in ib) / len(ib)
                bm = sum((r["p"] - r["y"]) ** 2 for r in rs) / len(rs)
                print(f"a={a} n_lb={nlb}: n={len(rs)} Brier={bm:.4f} inband_edge={mp:+.2f}c n_ib={len(ib)}")
