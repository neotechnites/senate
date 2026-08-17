#!/usr/bin/env python3
"""Pull full market lists + trade tapes for the 11 settled city-hour TEMP events (2026-08-16 gate).
Keyless read-only GETs, throttled. Output: event_tape_20260816.json"""
import json, subprocess, time, sys

BASE = "https://api.elections.kalshi.com/trade-api/v2"
OUT = "/Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research/event_tape_20260816.json"
EVENTS = [f"{s}-{h}" for s in ["KXTEMPAUSH","KXTEMPCHIH","KXTEMPDCH","KXTEMPLAXH","KXTEMPMIAH","KXTEMPNYCH"]
          for h in ["26AUG1522","26AUG1523"]]

def get(url, tries=4):
    for i in range(tries):
        p = subprocess.run(["curl","-s","--max-time","20",url], capture_output=True, text=True)
        try:
            d = json.loads(p.stdout)
            if "error" in d and d["error"].get("code")=="too_many_requests":
                time.sleep(8*(i+1)); continue
            return d
        except Exception:
            time.sleep(4)
    return None

data = {"pulled_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "events": {}}
for ev in EVENTS:
    d = get(f"{BASE}/markets?event_ticker={ev}&limit=100")
    time.sleep(0.7)
    if not d or "markets" not in d:
        print("SKIP event", ev, d); continue
    mkts = []
    for m in d["markets"]:
        rec = {"ticker": m["ticker"], "status": m["status"], "result": m.get("result",""),
               "volume": m.get("volume",0), "close_time": m.get("close_time"), "trades": []}
        if True:  # finalized markets zero out `volume`; always pull trades
            cursor = ""
            while True:
                u = f"{BASE}/markets/trades?ticker={m['ticker']}&limit=1000"
                if cursor: u += f"&cursor={cursor}"
                td = get(u); time.sleep(0.7)
                if not td or "trades" not in td: break
                rec["trades"].extend(td["trades"])
                cursor = td.get("cursor") or ""
                if not cursor: break
        mkts.append(rec)
    data["events"][ev] = mkts
    print(ev, "markets:", len(mkts), "trades:", sum(len(m["trades"]) for m in mkts), flush=True)

json.dump(data, open(OUT,"w"))
print("WROTE", OUT)
