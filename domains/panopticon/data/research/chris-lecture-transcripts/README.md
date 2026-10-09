# Chris Zukowski "How To Market A Game" lecture transcripts

How the lectures are built, what a saved page gives you, and how to get a transcript out.

## What is in a saved lecture page

Teachable "revamped_lecture_player" page. Useful bits, all greppable:

- `<h2 id="lecture_heading" data-lecture-id=... data-next-lecture-id=... data-previous-lecture-id=...>` holds the lecture title.
- `<div class="hotmart_video_player" data-attachment-id=... data-lecture-id=...><iframe src="https://player.hotmart.com/embed/<MEDIA_ID>?signature=...&token=...&user=...">` is the only content. The HTML comments say `attachments.count=1, kind=video`; there is no text block, no transcript, no JSON blob, no captions file.
- The sidebar `<li data-lecture-id=...>` list gives every lecture id, title and duration (copied into each transcript file).
- The `wistia_responsive_*` class names are legacy CSS only; the video host is Hotmart, not Wistia.

## Why it cannot be fetched without the session

The iframe URL carries a per-session `signature` and `token`. Without them the
embed page and `https://api-player-embed.hotmart.com/v1/media/<MEDIA_ID>`
answer HTTP 401 (verified with curl on 2026-10-09 for `OLDAVY0XZx`). Captions,
when a video has them, are served as a WebVTT subtitle track referenced from
that same signed media response. So the pull has to happen from the logged-in
browser.

## Steps per lecture (Chrome, logged in)

1. Open the lecture page, start the video, open DevTools (Cmd-Opt-I) > Network tab.
2. Click the CC button on the player (or press `c`). If the button is missing or greyed out, the video has no captions: go to step 6.
3. Filter the Network list by `vtt`. You get one `.vtt` file, or several numbered segment files if the track is chunked. The JSON response of `api-player-embed.hotmart.com/v1/media/<MEDIA_ID>` also lists the subtitle URLs under a `subtitles` key.
4. Right-click each .vtt > Copy > Copy URL, then in Terminal, while the page is still open (the URLs are signed and expire):
   `curl -L -o <lecture-slug>.vtt '<URL>'`
   For several segments, download each and concatenate in order.
5. Convert to plain text (strips timestamps and dedupes rolling cues):
   `python3 -I vtt2txt.py <lecture-slug>.vtt > <lecture-slug>.txt`
   Paste the text under `## Transcript` in `<lecture-slug>.md`.
6. No captions: filter the Network tab by `m3u8`, copy the playlist URL, then
   `ffmpeg -i '<URL>' -vn -ac 1 -ar 16000 <slug>.wav` and
   `whisper <slug>.wav --model medium --language en --output_format txt`
   (or `mlx_whisper` on Apple silicon). Same slug naming.

Slug = lecture title lower-cased, punctuation dropped, spaces to hyphens, e.g. `how-short-descriptions-work`.

## vtt2txt.py

```python
import sys, re
cues, last = [], None
for block in open(sys.argv[1], encoding="utf-8").read().split("\n\n"):
    lines = [l for l in block.splitlines() if l.strip() and "-->" not in l
             and not l.startswith(("WEBVTT", "NOTE", "X-TIMESTAMP", "STYLE"))
             and not l.strip().isdigit()]
    text = re.sub(r"<[^>]+>", "", " ".join(lines)).strip()
    if text and text != last:
        cues.append(text); last = text
print("\n".join(cues))
```

## Repeating the HTML scrape (title, media id, nav)

```python
# python3 -I scrape.py "<saved page>.md"
import sys, re, html
t = open(sys.argv[1], encoding="utf-8", errors="replace").read()
print(re.search(r'id="lecture_heading".*?</svg>\s*&nbsp;\s*(.*?)</h2>', t, re.S).group(1).strip())
print(re.search(r'player\.hotmart\.com/embed/([A-Za-z0-9]+)', t).group(1))
for m in re.finditer(r'<li[^>]*data-lecture-id="(\d+)"[^>]*>(.*?)</li>', t, re.S):
    print(m.group(1), html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(2)))).strip())
```
