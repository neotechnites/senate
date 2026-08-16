#!/usr/bin/env python3
"""Refresh the census markdown's FEDFUNDS/CPI/GDP rows from the expanded population."""
import io, sys, contextlib, re
sys.path.insert(0, "/Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research")
import family_census_analyze as A
out = {}
for f in ("KXFEDFUNDSYEAR", "KXUSCPIYEAR", "KXNOMGDPGROWTH"):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = A.analyze(f); A.band_now(f); A.books(f)
    out[f] = (r, buf.getvalue())
    print(buf.getvalue())
