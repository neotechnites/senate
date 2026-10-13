# Content pipeline v2 (head panopticon-14, 2026-10-12, Gemini 3.1 Pro audited twice)

Evidence: scratchpad hist_A..D (every content episode Sep 9 - Oct 12, Mac and PC transcripts), cp_map.md (the cp branches as built), gemini_audit1/2.md.

## Root causes
1. tools/content/shot.sh (work-trailer-reveal): `[ "$MODE" = rough ] && [ "${SIZE##*x}" -gt 1440 ] && MODE=movie`. Every 1080x1920 short is silently filmed frame by frame by Movie Maker, because portrait doesn't fit the 2560x1440 screen. This is why "real-time capture" never happened for shorts: ragdoll, forest, haters.
2. The tooling that worked (shot.sh + pc_rough real-time + tapes + assemble.py segment cache + PLAYBOOK) lives only on work-trailer-reveal, 166 commits off main. Shorts agents work from main's older copies, or write their own cutters (5 one-off cutters today).
3. One fresh agent per version re-reads tooling and re-decides rows Ryan gave no notes on.
4. The cp rewrite (7.8k lines, 24 gates, LLM translate, Gemini clip matching, virtual monitor) never ran end to end. A 2-line recut refilms everything. Its no-upscale rule pushed haters into Movie Maker again.

## Build list (smallest first)
1. Portrait real time: run_clip.gd `--portrait` renders the match plus its CanvasLayers (crosshair, scope vignette) in a 1080x1920 SubViewport, shown rotated in a 1920x1080 borderless window. pc_rough ddagrabs 1920x1080; transpose=1 gives native 1080x1920. Delete the movie fallback. Movie Maker only with an explicit --movie (final).
2. shot.sh in rough mode: one take, no silent retries; a failed gate prints and stops.
3. PC lock: one capture or heavy render at a time across agents.
4. Merge the trailer stack to main; delete the divergent copies. Leave cp unmerged; keep only voice.py's pinned Andrew +5% with preflight and no fallback voice, and run_clip's `--deny-look`.
5. assemble.py: no freeze, no slow (`fit: line` hold, `slow`, speed < 1 and `fill` slowing removed; a short line fails "Lx needs +N s"). Captions `pop | stack | none`: stack = quotes one by one in their own slots, with quote marks. Cards get their own band. Captions never share screen space with them.
6. Versions: vN+1 brief = copy of vN; edit only the noted rows. The segment cache keeps every other row frame-identical. Nothing is overwritten; names are versioned.
7. SHOTS.md catalogue: every take or tape Ryan accepted (map, POV, event, the cut it was in, file). Notes resolve to catalogue rows. Gameplay comes from tapes of real-looking play (bot matches with player_feel/human), not scripted stages Ryan called robotic.
8. Raw-take contact sheet at 1 fps, compared with Ryan's note before assemble (the one check, seconds).

## Who does what
The head writes the brief (shot rows plus script table) from Ryan's script. It spawns ONE agent per short, directly, never a manager over managers. That agent runs the fixed commands: sync, voice, shot, assemble, deliver. A second agent only when a new tape or stage must be authored.

## Acceptance test
The haters short, end to end, from its brief: native 1080x1920, real time, crosshair upright, no desktop frames, quotes stacked with quote marks, delivered to the Mac within minutes.
