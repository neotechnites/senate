# How people make and edit videos with Claude / agents (2025-2026) — sourced, 2026-10-12

Question (decision 377): a script with each line tied to a visual goes in; an editable timeline comes out. How do people who do this with Claude actually do it?

## The architecture everyone converges on
1. Ingest + analyse footage (Whisper transcript; CV saliency/motion for shot picking).
2. Agent maps script lines / narration beats to candidate clips.
3. Rough assembly written to a timeline.
4. Export to the NLE (XML/FCPXML/AAF) for the human to finish.
Nobody claims more than a rough cut: "80-90% of the way" (Mosaic). Our map.tsv -> render_lines -> timeline_lines -> publish is this same shape.

## Tools found
- Mosaic (YC W25) https://mosaic.so — node-based agentic editor; shot selection = saliency + motion + safe-rect detection under LLM judgment; exports XML to Resolve/FCP/Premiere with proxies relinkable to full-res. HN launch thread https://news.ycombinator.com/item?id=45980760: pitfalls = non-deterministic cuts across identical runs, no transitions/music sync, browser-only, doubts at 1TB+ footage.
- samuelgursky/davinci-resolve-mcp (3.5k stars) https://github.com/samuelgursky/davinci-resolve-mcp — MCP over Resolve's scripting API; plan -> review -> confirm before destructive actions; first-pass assembly cuts, "no automatic editorial judgment".
- barckley75/resolve-claude-mcp https://github.com/barckley75/resolve-claude-mcp — Claude Desktop -> Resolve scripting API; warns: watch the tool calls, keep backups, render proofs.
- hiteshK03/davinci-resolve-mcp https://github.com/hiteshK03/davinci-resolve-mcp — runs a bridge INSIDE Resolve to unlock scripting on the FREE edition; faster-whisper word-level subtitles instead of Studio transcription. LEAD: this is the claim we needed on Sunday morning (we concluded free = no external scripting). Untested.
- AFangTeam/chatcut-to-fcpxml https://github.com/AFangTeam/chatcut-to-fcpxml — AI-edited timeline -> frame-accurate FCPXML (multi-track, keyframed zooms, fades, captions); shaders/LUTs/plugin transitions have no FCPXML equivalent.
- hetpatel-11/Adobe_Premiere_Pro_MCP https://github.com/hetpatel-11/Adobe_Premiere_Pro_MCP — 283 tools; rule: inspect first, one focused mutation, read back state.
- KyaniteLabs/kinocut https://github.com/KyaniteLabs/kinocut — guardrailed ffmpeg MCP; takes exact timecodes (no shot selection); JSON "video receipts"; fails closed on QA gates.
- cartesiancs/cartcut (808 stars) https://github.com/cartesiancs/cartcut — layer editor + Claude Code MCP; cut from transcript; AI edits sit in normal undo history.
- misbahsy/video-audio-mcp https://github.com/misbahsy/video-audio-mcp — raw ffmpeg tools (trim/concat/overlay), no script layer.
- Remotion https://github.com/remotion-dev/remotion — "make videos agentively": agent writes React code that renders; motion graphics, not footage editing.

## Output format for continued human editing
Native NLE XML (FCPXML / Premiere XML / AAF) dominates. Zero OTIO+LLM repos found; OTIO is studio interchange, not an agent target. Our FCPXML choice matches practice.

## Pitfalls most cited
(a) non-determinism run to run; (b) rough-cut ceiling; (c) destructive-action risk -> plan/review/confirm gates + backups; (d) FCPXML loses shaders/LUTs/plugin transitions; (e) scale at TB footage; (f) setup friction (bridges, restarts).

## What this says about our weekend
- The pipeline shape we ended with is the standard one; the cost was building it live instead of reading this first.
- Nothing found does shot ACCURACY for in-engine footage: every tool picks from footage that already exists. The footage has to be shot right; selection is the easy part. (Shot-accuracy method still unpinned — Ryan's call.)
- Lead to test when the remake starts: the free-edition Resolve MCP bridge. If it works, the Mac head can drive Resolve directly instead of import-by-fcpxml.
