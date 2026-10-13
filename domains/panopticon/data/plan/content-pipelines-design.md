# Content pipelines: design (phase 1, 2026-10-12)

Goal (Ryan, 2026-10-12): once a script with per-line shot notes exists, one prompt and about 20 minutes give a short, devlog or trailer cut that looks exactly as described. Every rule below is enforced by a tool or a gate that runs whether or not an agent read anything. Prose that only an agent reads does not count.

Sources: pod DB decisions 91-363, tasks 295-350; game repo origin/main ed473b24 `tools/content`, `tools/capture`; trailer worktree `pano-trailer` (work-trailer-reveal, 166 commits off main); the PC devlog framework `devlog_0\scripts`; today's three short worktrees; memory notes.

---

## (a) What Ryan approved and what he rejected

### Approved

| What | Evidence | Lesson for the tools |
|---|---|---|
| Trailer rough v20 | 212: "Looks good on the trailer". 209 on v19: "pretty much all of it is good" apart from the shove read | Only the noted shots were restaged (9a/9b); everything else came from tapes, identical at 1 fps. Reuse plus deterministic reshoot works |
| Every trailer shot can be reproduced exactly | 108: "for each shot its just run a script and record" | Tapes plus `reshoot_all.sh`. The capture key is the stage plus its args plus the commit |
| Real-time rough capture | 195: "i just want screen recorded real tim of the game" | ddagrab with lossless utvideo (`pc_rough`, trailer branch only) |
| Head-run refilm in 303 s end to end | 197, 199: "about five minutes for the hell shots", "No builder for a refilm" | Fast because it is a fixed command chain with no agent in the loop |
| Lossless chain, one H.264 4:2:0 crf 12 BT.709 encode | 199: "both pipelines need to not compress it", "1080p is fine". 202: "i want it to make teh fucking video" | One lossy encode only, at delivery. Never RGB or 4:4:4 for viewing |
| Forest short v5 visuals | 338: "the visuals are all good by me". v4 and v8: "Everything else fine" (336, 343) | Per-line shot notes, fixed after each note, converge in about 5 rounds |
| Polish short opener d | 91: "ok, good, lets use opener d" | Alternates side by side, Ryan picks one |
| Projectile v2: "same clips as before, really all you have to do is extend the final clip" | projectile.md 2026-09-22 | A new version is a recut of existing clips |
| River Ruins edit b | 281: "b is correct" | Music placement by beat, using numbers |
| Per-line framework, one clip per script line | 355: "we need to create a proper framework" | One line maps to one rendered clip. A change re-renders one file |
| Voice chain: trim, level, breaths | 357: "make it a stable volume, cut the ends for the keyboard sound, and cut my breaths. That's it." | A deterministic VO tool |
| Human-looking POV | shove.md: "make it look more like a human playing and make it less rigid" | The `human` driver layer in stage_driver |

### Rejected

| Failure class | Evidence (Ryan's words) | Root cause found |
|---|---|---|
| Lighting and exposure differ from the game | 193 (v14): "blown the fuck out... intricate detail"; 191: "the colors... are way way off" | Stage scripts set exposure 3.8 and ambient 3.6. `--look=social`. Stale nearest filter in `C:\dev\verify` |
| Wrong resolution | 193: "its in like 730p"; 197 (v15): "you put the game in the top left of the screen but recorded the whole screen" | Saved settings are windowed 1280x720 and resized the capture window. **Today:** ragdoll_vnext and portal_spin film at 810x1440 (the PC screen is 2560x1440) and **upscale** to 1080x1920 (`capture.ps1`, `portal_spin.md`) |
| Mistimed or jumbled cuts | 198 (v16): "the shots timing are completely fucked... jumbled up"; 293: three words land at 7.8 s, not by 6 s; 340/342: effects shot off its word | The white sync marker was misread. Beats were placed by eye, not computed |
| Lossy re-compression | 199: "it looks like its been compressed 3 times"; 202: RGB master "green and stuttered" in Chrome | Multiple lossy passes. **Today:** cut.py writes libx264 crf 14 intermediates |
| Empty takes from a sleeping display | 225: "its takes recorded nothing" | The display sleeps after 10 minutes and ddagrab then gets no frames |
| Windows desktop in the cut | 342 (forest v7): "the end cuts to Windows" | The take ran past the game's exit and the tail was never trimmed |
| Camera clipping, bad framing | 330: "Last shot cuts through a tree"; "r02 lane POV dominated by one tree" | No geometry check on the lens |
| CLAUDE.md or agent files in editor shots; models in map shots | 362: "so unforgivable it's not even funny" | The editor ran on an unscrubbed project root |
| Text over text or cards | 339: "subtitles cover the on-screen text"; ryan-examples memory: "all the quotes being on top of one another" (screen SPACE, not time) | Captions sit at a fixed y with no knowledge of other text |
| Clip shorter than its line | 356: "they all seem to freeze after some period of time"; PLAYBOOK 2026-09-22: "never slow down clips its looks terrible" | `fit: line` holds the last frame and `slow` slows the clip. render_lines.py's own docstring still says "last frame held (tpad)" although map.tsv says the line FAILS: the rule lives in prose, not in code |
| Footage does not match the note | 340 (task) v21: "cut away... so fast that its really unclear"; "two shots are clearly not the same shot"; 350: "to robotic... following a line"; 313: bot-play takes rejected; projectile: "the people hes shooting at are retarded. they need to look like real players" | Nothing compares the take with the note before Ryan sees it |
| Rebuilding footage that exists | memory reuse-existing-footage: "there is no excuse for it... especially for ragdoll which already has like 6 versions" | No inventory. The brief was written as if the short were new |
| Footage from the wrong build | 351: "we shouldn't show any gameplay from a build past the night I playtested... you know that" | The commit cut-off was not enforced on takes |
| Wrong deliverable or media offline | 358: "I don't want the mp4... I want a timeline"; 363: Resolve "media offline" | Paths Resolve had already seen were overwritten |
| PC locked up or serialised | 356: "without locking up my entire pc"; shorts-common rule 9 (one lock per whole short) serialised three agents | The lock covered a whole project instead of one take. Renders ran at normal priority |
| Killing processes the agent did not start | 353 | The pipeline must own its process ids |
| Over-checking | 171/196: "dont even bother checking", "i dont want it to be checking fucking anything"; turnaround memory: "shit that should take 8 minutes take 30" | Agents add proofs. The gates must be the only checks, fixed and fast |
| Music laid over a cut made for another song | 232: "were putting music over a trialer cut for a specific song" | The trailer is cut to the beat map of the chosen song |
| Voice substitution | Coordinator 2026-10-12: always en-US-AndrewNeural at +5%, never a robot voice. portal_spin swapped in piper on the 403 | The voice tool has no fallback. It fails loudly |
| Tool sprawl | Today: four one-off cutters (`ragdoll_vnext/cut.py`, `haters_short/cut.ps1` and `captions.py`, `portal_spin/cards.py` and `film.ps1`) | `assemble.py` could not do stacked captions, cards or real-time portrait capture, so each agent wrote its own |

---

## (b) Architecture

```
spec.md (Ryan's script) --parse--> spec.json --translate (LLM, schema-gated)--> shots.json
inventory.sqlite --match--> plan.json  (every line: reuse | capture | editor | fetch | card)
plan.json --> voice --> captures (new only) --> line renders --> final --> gates --> Gemini review --> deliver
```

### One spec format: Ryan's script, the way he writes it

`tools/content/projects/<name>.md`. Header keys, then one line per script line. Example, as written for portal_spin:

```
# portal_spin
kind: short                      # short | devlog | trailer
music: Windmill Isle (Day)       # name or path; optional
captions: pop                    # pop | stack | none
base: ragdoll_short              # optional: an earlier project whose footage this version reuses
cutoff: 8b1c...                  # optional: no take from a commit newer than this (devlog 0 = 2026-09-12 00:04)

L1 "Do you think this change to my game is an improvement or should i scrap it?" {slow zoom on the portal, ALREADY SPINNING}
L2 "This guy on my last two shorts asked the same thing, make the portal spin" {sniper-POV gameplay, comment card: @commenter "make the portal spin"}
M1 {no voice: 2 s, the shover turns back and gets sniped, end on the hit}
L4 "..." {the portal waving WITHOUT spinning, at ed473b24~1}
```

Grammar: `L<n>[a-z]? "<voice text>" {<shot note>}` or `M<n> {<note>}` for a beat with no voice. Only the header and the `L/M` lines are machine-read. Everything else in the file is free notes. Ryan's text and notes are never rewritten. The translation goes into `shots.json`, next to the spec.

### Spec to machine shot list

`content plan` parses the spec deterministically into `spec.json`. One LLM call (the Claude session running `content`, given only the schema, the stage vocabulary from `stages/README.md`, and the map catalog) then fills `shots.json`. The result is schema-validated, and any field the model guessed is marked `interpreted: true` with a single line saying why.

```json
{"line":"L2","text":"...","note":"sniper-POV gameplay, comment card ...",
 "source":"game",                        // game | editor | online | card | black | reuse
 "game":{"map":"bentham_ring","pov":"guard","hud":"crosshair","stage":"scope_hunt",
         "set":"", "bots":7, "ref":"main", "humans":"on"},
 "editor":null, "online":null,
 "overlays":[{"kind":"comment_card","handle":"@commenter","text":"make the portal spin",
              "in":"word:This guy","out":"line_end","placeholder":true}],
 "beats":[{"word":"Ragdolls","event":"hit","tolerance_s":0.034}],
 "min_seconds":"voice",                  // the voice length decides it, filled after voice
 "continuity":"same_take_as:L1",         // two POVs of one event = one tape
 "interpreted":[]}
```

### Matching against the existing-asset inventory

`inventory.sqlite` (on the PC at `content\_inventory.sqlite`, with a pulled copy on the Mac) has one row per usable clip under `panopticon-renders\content\**`, built by `content inventory` (it walks only known project folders, never an open-ended search):

| column | from |
|---|---|
| path, sha1, duration, w, h, fps, codec, lossless | ffprobe |
| project, version_first_used | folder and the cut's `_lines.json` |
| commit, map, pov, stage, set, bots, seed, look | the take manifest `take.json` (new takes) or the `notes\NN.take.log` / jobs.txt / capture line (older takes, parsed once) |
| caption | one Gemini Flash description of the clip, generated once and cached by sha1 |
| approved | `yes` when the clip appears in a cut Ryan passed (from the table in (a), and later from `content approve <cut>`) |

Matching runs in order, and the first hit wins:
1. **Explicit.** The note names a file or "same as vN", or the header sets `base:`, and the line text matches a line in the base project's `_lines.json`: reuse that line's clip and window.
2. **Capture key.** Same `stage + set + pov + map + bots`, and the commit is on or after the newest content-changing commit for that map (`git log -1 -- maps/<map> characters weapons`) and no later than `cutoff:`. Reuse.
3. **Description.** The caption embedding is similar to the note at ≥ 0.80 and the format matches (aspect, resolution ≥ output). The line is proposed as `reuse?`, then confirmed by a Gemini Flash call comparing the clip with the note (yes/no). Reuse on yes.
4. Otherwise capture, editor or fetch.

**Reuse gate (G2):** the plan fails if a line is scheduled for capture while rule 1 or rule 2 had a hit, unless the note says `refilm`. A version N+1 with `base:` set therefore plans as a pure recut, and the plan printout gives the counts (`reuse 7 / capture 0`).

---

## (c) Shared tools

Every tool lives in `tools/content/cp/` on main (a Python package with one module per tool) and is called through the single entry point `tools/content/content`. The PC side runs `python cp\<tool>.py`, pushed by the Mac. Every output file gets a sidecar `<file>.prov.json` (inputs, encoder, lossless flag, commit, tool version). Gates read those sidecars.

| Tool | CLI | In, out | Status |
|---|---|---|---|
| plan | `content plan <spec>` | spec.md, inventory, stage vocabulary → spec.json, shots.json, plan.json | **New** (the parser is new; brief.py's table parser stays for old briefs) |
| inventory | `content inventory [--project P]` | PC content folders → inventory.sqlite (incremental by mtime) | **New** |
| voice | `content voice <spec> [--ryan DIR]` | spec lines → `voice\L##.wav`, `voice\words.json`, `voice\manifest.json` | **Wrap** pc/voice.py (see below) |
| capture game | `content capture <spec> L3` or `--all-new` | shots.json row → `takes\L03\take.avi` (utvideo RGB, native size), `take.json` (args, commit, seed, events, lighting, clip events, sync t0) | **Wrap and port**: `pc_rough` from work-trailer-reveal plus the take loop from main `shot.sh`. Replaces today's capture.ps1 and film.ps1 |
| tape | `content tape <spec> L3` | staged take → tape.json; capture replays it | **Reuse** tape.sh (trailer branch), ported to main |
| capture editor | `content editor <spec> L5` | row with `editor:{ref, scene, dock, camera}` → take.avi | **New**: builds a scrubbed throwaway worktree (362 list, enforced by code), opens the editor in the capture monitor, scopes the dock |
| fetch | `content fetch <spec> L7` | `online:{url, from, to}` or `--find WORD` → `external\<name>.mkv` (lossless re-cut of the downloaded stream) + SOURCES.md | **Reuse** pc/fetch.py, with crf 18 changed to lossless |
| card | `content card comment --handle H --text T` | → png (rounded card, shadow) + layout box | **Reuse** pc/card.py; add the comment-card text renderer (today's ASS hack in cut.py) |
| captions and layout | internal to render | words.json, overlays, OCR text boxes of the footage → ASS file with collision-free positions | **New**: merges assemble.py pop captions, haters' `stack` mode and the cut.py card |
| music | internal to render | track, ducking points → bed at -18 under the voice, -14 LUFS / -1 dBTP | **Reuse** pc/loudnorm.py and the music.tsv logic from timeline_lines |
| render | `content render <spec> [--only L3]` | plan, takes, voice → `lines\L##.mkv` (lossless, exactly the slot length), `edl.json`, `final\master\<tag>.mkv`, `final\<tag>.mp4` | **Wrap**: render_lines.py generalised to 9:16 and 16:9 and fed by plan.json; holds, loops and slowing removed from code |
| timeline | `content timeline <spec>` | lines, wavs, music → `builds\<stamp>\<tag>.fcpxml` + hard-linked media | **Reuse** timeline_lines.py and publish_timeline.py (devlog only) |
| verify | `content verify <spec>` | final, edl, prov, take manifests → `verify.json` (G7–G13) | **New** (gathers the freezedetect and motion code from shot.sh) |
| review | `content review <spec>` | final.mp4, spec, edl → `review.json` | **New** (see e) |
| deliver | `content deliver <spec>` | → PC `final\<tag>_vN.mp4` and Mac `~/Desktop/panopticon-renders/content/<kind>/<name>/`, never overwriting | **New** (small) |
| pclock | `content lock screen|heavy` (library) | lease file `C:\dev\locks\<slot>\owner.json` {owner, pid, expires} | **New**, replacing content.lock |

### Voice tool (coordinator rule)
- Voice pinned to `en-US-AndrewNeural`, rate `+5%`. These are constants in `cp/voice.py`, not spec fields. The spec cannot change the voice, and no code path names another engine.
- Endpoint pinned: the patched edge-tts (PR #491, `wss://api.msedgeservices.com/tts/cognitiveservices/websocket/v1`). The tool checks `edge_tts.__version__`, or the patched module's endpoint constant, against a pinned value. If it differs, it stops with "voice: edge-tts endpoint not the pinned one".
- **Preflight** (`content voice --check`, run first by every pipeline before any PC work): synthesise "Panopticon voice check." and assert all of the following: non-empty mp3, duration 0.8–3 s, at least 2 WordBoundary events, voice name echoed in metadata. On any failure the build stops with `VOICE FAILED: <http status>`. Nothing is substituted, and there is no piper or system voice.
- Word timings come from edge-tts WordBoundary. If the new endpoint returns no boundaries, faster-whisper 1.2.1 (on the PC) force-aligns the same Andrew wav against the known text. That is alignment, not substitution. The words.json format is unchanged.
- For Ryan's recordings (`--ryan DIR`, one clip per line): the vo_clean chain of decision 357 (trim the key-press ends, compress plus loudnorm, attenuate breaths), then faster-whisper alignment for words.json.

### Capture backend: native portrait without upscaling
The PC console is 2560x1440, so a 1080x1920 window cannot be ddagrabbed. That is why today's 810x1440 takes were upscaled.
- **Primary: a capture-only virtual monitor.** An IddCx virtual display driver, installed once over ssh as admin, adds monitor 2 at 1080x1920 (and 1920x1080 for devlog and trailer, switched per job by the tool). Windows extends to it, the taskbar shows only on the main display, and its wallpaper is solid `#FF00FF`. ddagrab runs with `output_idx=<virtual>`. Results: native resolution, Ryan's screen never covered, and a deterministic desktop detector (G3).
- Every take: wake the display (1 px mouse nudge plus `SetThreadExecutionState(ES_CONTINUOUS|ES_DISPLAY_REQUIRED)` held for the take), `GameSettings.window_held`, white **head and tail** markers drawn by run_clip (a tail marker is new). The take is trimmed to the frames strictly between them, so desktop at either end is impossible by construction. Below-normal priority, `-threads 4`. The tool kills only the process ids it started.
- run_clip.gd additions (owned by WP2): `--tail-marker`; `[clip]` events, where each frame a sphere of radius 2× the camera near plane is cast at the camera against terrain, props and character layers; `[light]` logs the environment's exposure, ambient, sky energy and look actually in effect; `[event]` hit, shove and death with take time (exists); `--deny-look` refuses `--look=social` and any exposure override unless `look_override: yes` is in the row.

### Locks (per capture, not per project)
- `screen`: held only for one real-time take (about 30–60 s). Agents queue per take, so three shorts interleave.
- `heavy`: one heavy ffmpeg render at a time (decision 356), held per line render batch. Plan, voice, smoke runs and Gemini calls take no lock.
- A lease expires after 3× the job's expected duration, so a dead agent cannot wedge the PC.

---

## (d) Gates

Each gate is code in `cp/gates.py`, returns pass/fail plus a one-line reason, and is written to `verify.json`. An agent cannot skip a gate, add one, or argue with one. Overrides exist only as spec fields Ryan typed (`refilm`, `look_override`, `freeze: waive`).

| # | Checks | How | Fails |
|---|---|---|---|
| G0 | Preflight: voice endpoint works, PC reachable, virtual monitor present, lock dir writable, ffmpeg has ddagrab and utvideo | `content preflight` | Before anything runs |
| G1 | Spec parses. Every L/M line has a shots.json row. Every row validates against the schema. Every `interpreted` field is listed | jsonschema | At plan time |
| G2 | Reuse: no capture scheduled where inventory rule 1 or 2 hits; `cutoff:` respected by every reused clip and every capture ref | plan.json vs inventory | At plan time |
| G3 | No desktop or editor chrome in game takes: trimmed between the white markers; < 0.5 % of `#FF00FF` pixels in any frame (wallpaper); frame size equals the requested size | ffmpeg on the take at 10 fps | Per take → one automatic retake, then the line fails |
| G4 | Not empty, black or frozen: file > 1 MB/s; blackdetect; freezedetect ≥ 0.75 s = 0; motion ≥ 0.02 (shot.sh numbers) | ffmpeg | Per take → retake |
| G5 | No camera clipping: zero `[clip]` events inside the used window | take.json | Per take → line fails (restage; never retried blindly) |
| G6 | Lighting as in the game: `[light]` equals the map's shipped values; no look override; median luma within ±15 % of the map's reference still (`cp/ref/<map>.png`, game PC capture at 1080p) | take.json + ffmpeg signalstats | Per take → line fails |
| G7 | Resolution and format: line clips and final are 1080x1920 at 60 fps (short) or 1920x1080 at 60 fps (devlog, trailer); every source's height ≥ output height (scale factor ≤ 1.0, so no upscale); a landscape source in a short is allowed only as an explicit `letterbox` overlay | ffprobe + prov | Per line render |
| G8 | Lossless chain: walk prov from final back to the sources; exactly one lossy encode after the source (the delivery mp4); intermediates are utvideo, ffv1 or x264 qp0 | prov.json | At final |
| G9 | No clip shorter than its line: on-screen footage ≥ slot at speed 1.0; renderer has no tpad, loop or speed < 1 (refused in code); post-check mpdecimate duplicate-frame ratio < 2 % per line and freezedetect = 0 | render plan + ffmpeg | Per line → plan marks the line "needs footage", and capture extends the take (`seconds += shortfall + 1`) |
| G10 | Beats land on words: for every `beats` entry, `|t_word - t_event| ≤ tolerance` (default 2 frames), where t_word comes from words.json + line start and t_event from take.json `[event]` mapped through edl.json | arithmetic | Per line render → renderer re-solves the in-point (PLAYBOOK projectile method) once, then fails |
| G11 | Text never shares screen space: every caption box, card box and OCR'd on-screen text box in the footage (OCR at 4 fps of the line clip) has zero pairwise intersection at every time; on conflict the layout engine moves the caption to the next free y slot, and only if none exists does the gate fail. Stacked captions (haters) are legal: stacking means distinct boxes | layout solver + tesseract | Per line render |
| G12 | OPSEC and agent files: OCR of every editor take and of the final at 2 fps for banned tokens (`CLAUDE`, `claude`, `.md`, `agent`, `AI`, `tools/`, `addons/`, `.claude`, `ddd`, the PC name, IPs, `whitehead`, `ryan`, `stackintegrated`); editor worktree scrub checked by listing before launch | tesseract + scrub list | Editor take → fails before filming; final → blocks delivery |
| G13 | Audio: the voice manifest says AndrewNeural +5% (or Ryan's wavs); -14 LUFS ±1, ≤ -1 dBTP; game audio off unless `keep-audio` | ebur128 + manifest | At final |
| G14 | Spec match: Gemini verdict per line (e); Gemini Flash take check per new take ("does this take show: <note>? yes/no + why") | review.json | Take check → retake once; final → one automatic fix round for failing lines, then stop and report those lines with Gemini's words |
| G15 | Deliverable: versioned name, nothing Resolve has seen is overwritten (363), devlog emits fcpxml and no concat unless asked (358), Mac copy exists | filesystem | At deliver |

Over-checking is designed out by the same table. These gates are the only checks: no agent stills, no dailies round for rough drafts, no 1 fps self-review. The whole verify plus review step is budgeted at 2 minutes for a short.

---

## (e) Gemini review

**Method: the API via google-genai Files upload, not the CLI.** The CLI (0.5.4) inlines files with a hard 20 MB cap (today's 41 s short is 34 MB), has no response schema, no fps or offset control, and runs as an agent with tools. Measured today on `ragdoll_vnext_v1.mp4` (41 s, 34 MB): upload reached ACTIVE in seconds; `gemini-2.5-pro` 12.5 s, `gemini-2.5-flash` 7.8 s; 22,970 prompt tokens at fps=2; schema-valid JSON that correctly located L4's words and described the comment card. The package needs `pip install google-genai` (2.29.0) in a venv on the Mac. Reviews run on the Mac and need no PC.

```python
f = client.files.upload(file=final_mp4)                 # the delivered H.264, what Ryan watches
wait_until(f.state == "ACTIVE")
parts = [types.Part(file_data=types.FileData(file_uri=f.uri, mime_type="video/mp4"),
                    video_metadata=types.VideoMetadata(fps=4))]   # shorts; devlog: fps=1, per-chapter offsets
resp = client.models.generate_content(model="gemini-2.5-pro", contents=parts + [PROMPT],
         config=types.GenerateContentConfig(response_mime_type="application/json",
                                            response_schema=SCHEMA, temperature=0))
client.files.delete(name=f.name)
```

Prompt shape. The timings come from edl.json, so Gemini judges known windows instead of searching for them:

```
You are checking a video edit against its shot list. Judge only what is visible and audible.
Output size: 1080x1920 portrait. The game is a low-poly N64-style first-person game.
For EACH line below, watch the window [start, end] and report:
- heard: the words spoken in the window (verbatim)
- seen: what is on screen, concretely (camera POV, map, who moves, what happens, any text)
- matches_note: yes | partly | no, judged strictly against the NOTE
- defects: any of [desktop_or_os_ui, editor_ui_or_files, camera_inside_geometry, text_overlap,
  frozen_or_looping, slowed_motion, wrong_pov, wrong_map, wrong_event, event_off_word,
  too_dark_or_blown_out, robotic_motion, cut_mid_action, letterboxed_or_cropped, other:<text>]
- why: one sentence if not yes
Lines:
L1 [0.00-4.31] VOICE: "Do you think this change..." NOTE: {slow zoom on the portal, ALREADY SPINNING}
L2 [4.31-9.02] VOICE: "..." NOTE: {...}  BEAT: hit lands on "Ragdolls" at 8.37
...
Then: overall_defects (anything between lines, at cuts, at the head or tail).
```

Schema: `{lines:[{id, heard, seen, matches_note, defects[], why}], overall_defects[]}`.

Verdict:
- `no`, or any defect other than `other`, fails the line.
- `partly` passes with a note in the report.
- A failing line is re-asked once with that window clipped (`start_offset`/`end_offset`) at fps=8. Only a second fail counts, which suppresses one-off misreads.
- Cost is about 25k tokens for a 40 s short. A devlog runs per chapter at fps=1.
- The per-take check (G14) uses `gemini-2.5-flash` on the take with the same defect list and only that row's note.

---

## (f) Entry points

```
content short   <spec.md> [--tag vN]     # 9:16, 1080x1920, edge-tts Andrew unless --ryan
content devlog  <spec.md> [--ryan DIR]   # 16:9, per-line clips + fcpxml timeline (no concat mp4)
content trailer <spec.md> [--movie]      # 16:9, tapes, cut to the song's beat map; --movie for the final
```

Shared flow, one orchestrator (`cp/run.py`), resumable by stage (each stage skips when its outputs' hashes match):

| Step | Short: what happens | Target |
|---|---|---|
| 0 preflight (G0) | voice check, PC, monitor, locks | 0:20 |
| 1 plan (G1, G2) | parse, LLM translate, inventory match, print `reuse n / capture m`, write plan.json | 2:00 |
| 2 voice | 8 lines edge-tts + boundaries (runs alongside 3) | 0:40 |
| 3 stage and smoke | for capture lines without an existing stage: write or adapt the plugin and run a headless smoke on the Mac (`[event]` lines must show the beat) | 6:00 |
| 4 capture (G3–G6, G14 take check) | `sync.sh` once, then about 4 new takes at about 45 s each (screen lock per take) + take checks in parallel | 4:30 |
| 5 render (G7–G11) | line clips, captions, cards, music, master, mp4 (heavy lock) | 2:30 |
| 6 verify + review (G12, G13, G14) | ffmpeg/OCR gates + Gemini | 2:00 |
| 7 deliver (G15) | versioned PC and Mac copies, 5-line report | 0:30 |
| **Total** | | **≈ 18:30** (a pure recut skips 3–4: ≈ 8 min) |

Devlog: same steps. Voice is Ryan's wavs through the VO chain. Render is per line with `--jobs` under the heavy lock, and the output is `builds\<stamp>\*.fcpxml` (decisions 355–363). `cutoff:` is mandatory for devlog 0. About 54 lines, mostly reuse, so the target is render-bound: about 12 min plus about 1.5 min per new take.

Trailer: every capture row needs a `tape:`, and capture replays the tape (decision 108). Music is a beat map (onsets from the song) feeding G10 for every cut. `--movie` swaps the capture backend to frame-exact for the final. The refilm of one map is `content trailer spec --only-map hell`, about 5 min as today.

What the one prompt is: "content short projects/portal_spin.md". The agent runs the orchestrator and acts only where a step hands back work: writing stage plugins in step 3, or a fix round on a G14 failure. Everything else is a command.

---

## (g) Builder work packages

Four packages with disjoint files, joined only by the JSON files below. The schemas live in `tools/content/cp/schema/*.json` and are written first by WP1, then frozen for the build.

| WP | Owns (files) | Delivers | Consumes |
|---|---|---|---|
| **WP1 Spec, plan, inventory** | `cp/spec.py`, `cp/plan.py`, `cp/inventory.py`, `cp/schema/`, `cp/match.py` | `spec.json`, `shots.json`, `plan.json`; `inventory.sqlite`; gates G1, G2 | inventory scan of the PC folders; Gemini Flash for captions (calls `cp/gemini.py` from WP4) |
| **WP2 Capture (PC)** | `tools/capture/run_clip.gd` (tail marker, `[clip]`, `[light]`, `--deny-look`), `cp/capture.py`, `cp/editor.py`, `cp/pclock.py`, `cp/pc/capture.ps1`, port of `pc_rough` and `tape.sh` to main, the virtual monitor install script | `takes/<line>/take.avi` + `take.json`; gates G3–G6 | `plan.json` rows with `source: game|editor` |
| **WP3 Voice and render** | `cp/voice.py` (pinned Andrew, preflight), `cp/vo_clean.py`, `cp/render.py` (from render_lines.py), `cp/layout.py` (captions, cards, OCR boxes), `cp/music.py`, `cp/timeline.py`; `card.py`, `fetch.py` changes | `voice/manifest.json`, `words.json`; `lines/L##.mkv`, `edl.json`, master, mp4, fcpxml; gates G7–G11, G13 | `plan.json`, `take.json`, external clips |
| **WP4 Orchestrator, verify, review** | `tools/content/content` (entry), `cp/run.py`, `cp/gates.py` (runner + G12, G15), `cp/gemini.py`, `cp/review.py`, `cp/deliver.py`, `cp/preflight.py` | `verify.json`, `review.json`, delivered files, report; G0, G12, G14, G15 | everything above via the files only |

Fixed interfaces (abridged; WP1 writes the full schemas on day one):

```
plan.json   {name, kind, aspect:[w,h], fps:60, cutoff, base, lines:[{id, text, note, source,
             reuse:{path, in, len}|null, game|editor|online|card spec, overlays[], beats[], continuity}]}
take.json   {line, path, w, h, fps, commit, args, seed, t0, t1, events:[{t, kind, who}],
             light:{exposure, ambient, sky, look}, clip_events:[{t, what}], gates:{G3..G6}}
voice/manifest.json {engine:"edge-tts", voice:"en-US-AndrewNeural", rate:"+5%", endpoint, lines:{L1:{wav, dur, words:[...]}}}
edl.json    {lines:[{id, start, dur, parts:[{path, in, len, speed:1.0}], overlays:[{kind, box, t0, t1}],
             captions:[{text, box, t0, t1}], beats:[{word, t_word, t_event}]}], master, final}
*.prov.json {inputs:[sha1], encoder, lossless:bool, tool, version}
review.json {model, fps, lines:[{id, heard, seen, matches_note, defects, why}], overall_defects}
```

Order and conflicts: all four start at once against the frozen schemas. WP2 is the only writer of run_clip.gd and of anything under `tools/capture/`. WP3 is the only writer of the existing `tools/content/pc/*.py` it adopts. WP4 tests on fixture JSON until the others land. Only WP2 touches the PC desktop session. The driver install is done once by WP2 and needs no Ryan command.

### Interpretations (one line each)
- "Wrong lighting vs the game" is gated against the shipped environment values plus a reference still per map. The v36 Mac lift (313) is allowed only as a spec field.
- Real-time capture (195) is the only rough capture. Offline capture exists only under --final; if real-time capture cannot run, the take fails. There is no fallback.
- "Text overlapping" is a screen-space rule (ryan-examples memory). Stacked, persistent captions stay legal.
