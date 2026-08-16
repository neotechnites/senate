#!/usr/bin/env python3
"""S1 transcript puller: fool.com quote page -> transcript links -> cached raw text."""
import json, os, re, sys, time, urllib.request, html, ssl
SSLCTX = ssl.create_default_context()
SSLCTX.check_hostname = False
SSLCTX.verify_mode = ssl.CERT_NONE

CACHE = "/Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research/s1_transcript_cache"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
            return urllib.request.urlopen(req, timeout=40, context=SSLCTX).read().decode("utf-8", "ignore")
        except Exception as e:
            if i == tries - 1:
                print("  FAIL", url, e); return ""
            time.sleep(2 + 2 * i)
    return ""

def find_links(tkr):
    """Return ordered unique transcript paths from the fool quote page."""
    out = []
    for ex in ("nasdaq", "nyse"):
        h = get(f"https://www.fool.com/quote/{ex}/{tkr.lower()}/")
        if not h or len(h) < 50000:
            continue
        links = re.findall(r'"(/earnings/call-transcripts/\d{4}/\d{2}/\d{2}/[^"\\]+)', h)
        # keep only links whose slug mentions this ticker
        pat = re.compile(r"[-/]" + re.escape(tkr.lower()) + r"[-/]")
        links = [l for l in links if pat.search(l)]
        for l in links:
            if l not in out:
                out.append(l)
        if out:
            break
    return out

DATE_RE = re.compile(
    r"(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t|tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?\s+(\d{1,2}),?\s+(\d{4})", re.I)
MON = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}

# Call-opening phrases: the operator's greeting is the first real content on every page.
START_PATS = ["good morning", "good afternoon", "good day", "thank you for standing by",
              "welcome to the", "ladies and gentlemen", "prepared remarks", "greetings"]
# Fool page furniture that follows the call body (headlines here would inject false hits).
END_PATS = ["by motley fool transcribing", "summarize with ai", "fool.com on share",
            "duration:", "[operator signoff]", "motley fool returns", "read next"]

def strip_html(h):
    """Fool serves the body inside an RSC/JSON payload; unescape, de-tag, then bound
    to the call itself so page chrome ('read next' headlines, ads) cannot inject hits."""
    h = h.replace("\\u003c", "<").replace("\\u003e", ">").replace('\\"', '"').replace("\\n", "\n")
    h = re.sub(r"(?is)<(script|style|nav|header|footer|aside|form)\b.*?</\1>", " ", h)
    h = re.sub(r"(?is)<br\s*/?>", "\n", h)
    h = re.sub(r"(?is)</(p|div|h\d|li)>", "\n", h)
    seg = re.sub(r"(?s)<[^>]+>", " ", h)
    seg = html.unescape(seg)
    seg = re.sub(r"[ \t\xa0]+", " ", seg)
    seg = re.sub(r"\n{3,}", "\n\n", seg).strip()
    low = seg.lower()
    cands = [low.find(p) for p in START_PATS]
    cands = [c for c in cands if c > 0]
    s = min(cands) if cands else 0
    ends = [low.find(p, s + 5000) for p in END_PATS]
    ends = [e for e in ends if e > s]
    e = min(ends) if ends else len(seg)
    return seg[s:e].strip()

def split_qa(text):
    """(prepared_remarks, qa). Fool marks the Q&A section explicitly; empty qa if absent."""
    low = text.lower()
    for p in ["questions & answers:", "questions and answers:", "questions & answers",
              "questions and answers", "question-and-answer session", "q&a session"]:
        i = low.find(p, 200)
        if i > 0:
            return text[:i], text[i:]
    return text, ""

def call_date(text, url):
    """Best-effort actual call date; fall back to URL publish date."""
    head = text[:4000]
    m = DATE_RE.search(head)
    if m:
        mo = MON[m.group(1)[:3].lower()]
        return f"{m.group(3)}-{mo:02d}-{int(m.group(2)):02d}"
    u = re.search(r"/(\d{4})/(\d{2})/(\d{2})/", url)
    return f"{u.group(1)}-{u.group(2)}-{u.group(3)}" if u else "1900-01-01"

def pull(tkr, maxn=9):
    os.makedirs(CACHE, exist_ok=True)
    out = os.path.join(CACHE, f"{tkr}.json")
    have = {}
    if os.path.exists(out):
        have = {t["url"]: t for t in json.load(open(out))}
    links = find_links(tkr)
    print(f"{tkr}: {len(links)} transcript links found")
    recs = list(have.values())
    for l in links[:maxn]:
        url = "https://www.fool.com" + l
        if url in have:
            continue
        h = get(url)
        if not h:
            continue
        txt = strip_html(h)
        if len(txt) < 3000:
            print("  short, skip", l, len(txt)); continue
        q = re.search(r"-(q[1-4])-(\d{4})-", l)
        recs.append({"ticker": tkr, "url": url, "quarter": (q.group(1) + q.group(2)) if q else "?",
                     "call_date": call_date(txt, url), "chars": len(txt), "text": txt})
        print(f"  + {q.group(0) if q else '?'} {recs[-1]['call_date']} {len(txt)}c")
        time.sleep(1.0)
    recs.sort(key=lambda r: r["call_date"], reverse=True)
    json.dump(recs, open(out, "w"))
    return len(recs)

if __name__ == "__main__":
    for t in sys.argv[1:]:
        pull(t)
