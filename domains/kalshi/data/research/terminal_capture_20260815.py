#!/usr/bin/env python3
"""One-night terminal-evacuation capture — reg-autoseat-v3 research support.

Polls the PUBLIC orderbook of every KXSTATEBALLOTMEASURE market whose weekly
LIP window closes 2026-08-16 03:59Z, every ~5 minutes, from launch until
04:15Z, appending one jsonl line per (sweep, ticker).  Read-only, no auth,
self-terminating.  Purpose: record the maker evacuation + informed taker
arrival that killed our seats on 08-15, from the outside, in markets we no
longer occupy — the dataset for the evacuation/drift eject gates and the
terminal-taker spec.
"""

import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
POD = os.path.dirname(os.path.dirname(HERE))          # domains/kalshi
sys.path.insert(0, POD)
sys.path.insert(0, os.path.dirname(os.path.dirname(POD)))  # senate root

from harness.venue_client import KalshiVenueClient    # noqa: E402

TICKERS = json.load(open(os.path.join(HERE, "terminal_capture_tickers.json")))
OUT = os.path.join(HERE, "terminal_capture_20260815.jsonl")
END_EPOCH = 1786852500        # 2026-08-16 04:15:00Z
SWEEP_GAP_S = 300.0
REQ_GAP_S = 1.0


def main():
    client = KalshiVenueClient()
    sweep = 0
    while time.time() < END_EPOCH:
        sweep += 1
        t0 = time.time()
        ok = err = 0
        with open(OUT, "a") as fh:
            for tk in TICKERS:
                if time.time() >= END_EPOCH:
                    break
                try:
                    book = client.fetch_public_orderbook(tk)
                    fh.write(json.dumps({
                        "ts": round(time.time(), 2), "sweep": sweep,
                        "ticker": tk, "book": book}) + "\n")
                    ok += 1
                except Exception as exc:              # noqa: BLE001
                    fh.write(json.dumps({
                        "ts": round(time.time(), 2), "sweep": sweep,
                        "ticker": tk, "error": str(exc)[:150]}) + "\n")
                    err += 1
                time.sleep(REQ_GAP_S)
            fh.write(json.dumps({"ts": round(time.time(), 2),
                                 "sweep": sweep, "sweep_done": True,
                                 "ok": ok, "err": err}) + "\n")
        wait = SWEEP_GAP_S - (time.time() - t0)
        if wait > 0:
            time.sleep(min(wait, max(0.0, END_EPOCH - time.time())))
    print("capture complete")


if __name__ == "__main__":
    main()
