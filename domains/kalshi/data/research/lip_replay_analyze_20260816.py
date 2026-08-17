#!/usr/bin/env python3
"""seats-lip-replay analyzer 2026-08-16 — pure on-disk, no network.
Inputs: lip_replay_cache_20260816/{curfew_survivors.json, books/*.json}
Gates replayed: 24h curfew (already applied upstream), band 15-85c own-side join,
rival touch depth >= 250, base-rate NO<=35c side gate (ballot only).
Yield model (facts table): reward decays 0.5**distance_ticks from qualifying touch;
share = our_weighted / max(target_size, our_weighted + rival_weighted);
est credit/day = (period_reward/window_days) * share * 0.85 (15% churn haircut).
"""
import json, os, math, datetime

CACHE = "/Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research/lip_replay_cache_20260816"
NOW = datetime.datetime(2026, 8, 16, 3, 55, tzinfo=datetime.timezone.utc)
PER_MARKET_CAP = 50.0


def ts(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))


def ladder(raw):
    """Kalshi orderbook: {'yes': [[price_cents, qty], ...], 'no': [...]} (bids).
    Newer payloads may use *_dollars fp strings. Return dict side-> list of (cents, qty) sorted desc."""
    out = {}
    for side in ("yes", "no"):
        lv = raw.get(side) or []
        parsed = [(float(row[0]), float(row[1])) for row in lv]
        fp = raw.get(f"{side}_dollars") or []
        if not parsed and fp:
            parsed = [(float(p) * 100, float(q)) for p, q in fp]
        parsed = [(int(round(p)), q) for p, q in parsed if q > 0]
        parsed.sort(reverse=True)
        out[side] = parsed
    return out


def analyze():
    surv = json.load(open(os.path.join(CACHE, "curfew_survivors.json")))
    rows = []
    for s in surv:
        p, m = s["program"], s["market"]
        t = p["market_ticker"]
        fam = t.split("-")[0]
        bf = os.path.join(CACHE, "books", f"{t}.json")
        if not os.path.exists(bf):
            rows.append({"ticker": t, "family": fam, "verdict": "NO_BOOK"})
            continue
        payload = json.load(open(bf))
        raw = payload.get("orderbook") or payload.get("orderbook_fp") or {}
        lad = ladder(raw)
        reward_usd = p["period_reward"] * 1e-4
        target = float(p["target_size_fp"])
        win_h = (ts(p["end_date"]) - ts(p["start_date"])).total_seconds() / 3600
        rem_h = (ts(p["end_date"]) - NOW).total_seconds() / 3600
        daily_reward = reward_usd * 24.0 / win_h

        best = None
        for side in ("yes", "no"):
            book = lad[side]
            rival = lad["no" if side == "yes" else "yes"]
            if not book:
                continue
            touch_p, touch_q = book[0]
            # join AT the touch (distance 0); own join price gate 15-85c
            join = touch_p
            if not (15 <= join <= 85):
                continue
            # pair-sum sanity: implied ask = 100 - rival_touch
            rival_touch = rival[0][0] if rival else None
            if rival_touch is not None and join + rival_touch > 99:
                continue
            # depth at relevant band: total resting at own-side touch (rival = others at our band)
            depth_at_touch = touch_q
            both_touch_depth = touch_q + (rival[0][1] if rival else 0)
            # base-rate side gate (ballot family): never NO <= 35c
            gated = fam == "KXSTATEBALLOTMEASURE" and side == "no" and join <= 35
            # our size at $50 cap: collateral = price/100 * count for bid side
            cost_per_ct = join / 100.0 if side == "yes" else join / 100.0
            ours = int(PER_MARKET_CAP / cost_per_ct)
            # df-weighted rival mass across both books, distance from own touch
            def wmass(lv, touch):
                return sum(q * (0.5 ** abs(touch - pp)) for pp, q in lv)
            rival_w = wmass(book, touch_p) + wmass(rival, rival[0][0] if rival else 0)
            our_w = ours * 1.0  # at touch, distance 0
            share = our_w / max(target, our_w + rival_w)
            est_day = daily_reward * share * 0.85
            cand = {"side": side, "join_c": join, "touch_q": touch_q,
                    "depth_at_touch": depth_at_touch, "both_touch": both_touch_depth,
                    "rival_w": round(rival_w, 1), "ours": ours, "share": round(share, 4),
                    "est_credit_day_usd": round(est_day, 4), "base_rate_gated": gated}
            if best is None or cand["est_credit_day_usd"] > best["est_credit_day_usd"]:
                best = cand
        r = {"ticker": t, "family": fam, "hrs_to_expiry": round(s["hrs_to_expiry"], 1),
             "reward_usd_window": reward_usd, "window_h": round(win_h, 1),
             "rem_h": round(rem_h, 1), "daily_reward_pool": round(daily_reward, 2)}
        if best is None:
            r["verdict"] = "NO_BAND"  # no side with own join in 15-85c
        else:
            r.update(best)
            if best["base_rate_gated"]:
                r["verdict"] = "BASE_RATE_GATE"
            elif best["depth_at_touch"] < 250:
                r["verdict"] = "DEPTH_FAIL"
            else:
                r["verdict"] = "QUALIFIED"
        rows.append(r)

    out = os.path.join(CACHE, "seat_replay_results.json")
    json.dump(rows, open(out, "w"), indent=1)
    from collections import Counter
    print(Counter((r["family"], r["verdict"]) for r in rows))
    print("---QUALIFIED or near---")
    for r in sorted(rows, key=lambda x: -(x.get("est_credit_day_usd") or 0)):
        if r["verdict"] in ("QUALIFIED", "DEPTH_FAIL") and (r.get("est_credit_day_usd") or 0) > 0:
            print(f"{r['ticker']:42s} {r['verdict']:10s} side={r.get('side')} join={r.get('join_c')}c "
                  f"touchq={r.get('depth_at_touch')} share={r.get('share')} "
                  f"est/day=${r.get('est_credit_day_usd')} pool/day=${r['daily_reward_pool']}")
    print("saved:", out)


if __name__ == "__main__":
    analyze()
