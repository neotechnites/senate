#!/usr/bin/env python3
"""
S1 — earnings-call word-strike base-rate predictor.

Given a company and a list of word strikes, compute P(word is said on the next call)
from that company's OWN prior earnings-call transcripts. Pure base rate + Beta shrinkage.
No ML, no sentiment, no news. The thesis: management scripts are written in advance and
are heavily autocorrelated quarter-over-quarter, while the counterparty prices each strike
on news-cycle salience without opening last quarter's transcript.

Transcripts are cached by s1_pull_transcripts.py under s1_transcript_cache/<TKR>.json.

CLI:
    python3 s1_word_predictor.py NVDA "Tariff,Taiwan,TSMC" [--asof 2026-08-26]
"""
import json, os, re, sys

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s1_transcript_cache")

# ---- model constants (preregistered; see s1_backtest.py for the leave-one-company-out fit)
N_LOOKBACK = 6      # quarters of own-company history to use
PRIOR_P = 0.50      # Beta prior mean when the company has no history for a word
PRIOR_A = 1.5       # Beta prior strength, in pseudo-quarters
# Kalshi resolution: "the exact phrase/word, or a plural or possessive form ... Grammatical/
# tense inflections are otherwise not included."
SUFFIX = r"(?:'s|s'|es|s)?"


def word_pattern(word):
    """Regex matching a strike word/phrase incl. plural and possessive, per Kalshi rules."""
    parts = [p for p in re.split(r"\s+", word.strip()) if p]
    esc = [re.escape(p) for p in parts]
    esc[-1] = esc[-1] + SUFFIX
    return re.compile(r"(?<![A-Za-z0-9])" + r"[\s\-]+".join(esc) + r"(?![A-Za-z0-9])", re.I)


def load_transcripts(company, asof=None):
    """Own-company transcripts strictly BEFORE `asof` (YYYY-MM-DD), newest first."""
    p = os.path.join(CACHE, f"{company.upper()}.json")
    if not os.path.exists(p):
        return []
    recs = json.load(open(p))
    if asof:
        recs = [r for r in recs if r["call_date"] < asof]
    return sorted(recs, key=lambda r: r["call_date"], reverse=True)


SPLIT_PATS = ["questions & answers", "questions and answers",
              "question-and-answer session", "q&a session"]


def split_qa(text):
    """(prepared_remarks, qa); qa is '' when the section header is absent."""
    low = text.lower()
    for p in SPLIT_PATS:
        i = low.find(p, 200)
        if i > 0:
            return text[:i], text[i:]
    return text, ""


def predict(company, words, asof=None, n_lookback=N_LOOKBACK,
            prior_p=PRIOR_P, prior_a=PRIOR_A):
    """-> list of dicts: word, p, k, n, hits per quarter, prepared/Q&A split."""
    recs = load_transcripts(company, asof)[:n_lookback]
    out = []
    for w in words:
        pat = word_pattern(w)
        hits, per_q, pr_hits, qa_hits, qa_avail, counts = 0, [], 0, 0, 0, 0
        for r in recs:
            c = len(pat.findall(r["text"]))
            said = c > 0
            hits += said
            counts += c
            per_q.append({"q": r["quarter"], "date": r["call_date"], "said": said, "count": c})
            pr, qa = split_qa(r["text"])
            if qa:
                qa_avail += 1
                pr_hits += bool(pat.search(pr))
                qa_hits += bool(pat.search(qa))
        n = len(recs)
        p = (hits + prior_a * prior_p) / (n + prior_a) if n or prior_a else prior_p
        out.append({
            "word": w, "p": round(p, 4), "k": hits, "n": n,
            "raw_rate": round(hits / n, 4) if n else None,
            "mentions_total": counts,
            "mentions_per_call": round(counts / n, 2) if n else None,
            "last_call_said": per_q[0]["said"] if per_q else None,
            "prepared_k": pr_hits, "qa_k": qa_hits, "qa_calls": qa_avail,
            "quarters": per_q,
        })
    return out


# ---- taker economics -------------------------------------------------------------
def taker_fee_cents(price_cents):
    """Kalshi taker fee, ceil-to-1c per contract: ceil(0.07 * P * (1-P) * 100) cents."""
    import math
    pr = price_cents / 100.0
    return math.ceil(0.07 * pr * (1 - pr) * 100) / 1.0


def edge_after_fee(p_model, yes_ask_c, no_ask_c):
    """Best taker edge in c/ct after fee. Returns (side, entry_price_c, edge_c)."""
    e_yes = (p_model * 100 - yes_ask_c) - taker_fee_cents(yes_ask_c)
    e_no = ((1 - p_model) * 100 - no_ask_c) - taker_fee_cents(no_ask_c)
    return ("YES", yes_ask_c, e_yes) if e_yes >= e_no else ("NO", no_ask_c, e_no)


IN_BAND = (15, 85)


def in_band(price_cents):
    return IN_BAND[0] <= price_cents <= IN_BAND[1]


if __name__ == "__main__":
    comp = sys.argv[1]
    words = [w.strip() for w in sys.argv[2].split(",")]
    asof = None
    if "--asof" in sys.argv:
        asof = sys.argv[sys.argv.index("--asof") + 1]
    for r in predict(comp, words, asof):
        print(f"{r['word']:<20} P={r['p']:.3f}  {r['k']}/{r['n']}  "
              f"mentions/call={r['mentions_per_call']}  last={r['last_call_said']}")
