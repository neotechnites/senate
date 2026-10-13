# Shot engine design (content pipeline v3), 2026-10-12

## What Ryan needs (his words, 2026-10-12)
Content = shorts, devlogs, trailers. All share: (1) gameplay footage at any build stage, scripted bots, real-time capture before final, Godot movie mode only at final; (2) online clips; (3) Godot/Blender window capture. Success test: a shot like "a POV shot of runners running on the forest map, and the POV runner shoves the other off the map" produced within 10 minutes with no glaring issues: no clipping through trees, looks like gameplay (first person, not machinima), the shove and the fall visible, in-game ragdoll, runners don't run into walls, no inhuman look speed, animations work, composition of a person playing. Those are examples of an outcome that must emerge from the pipeline, not a checklist for an agent, and not fixed by infinite watch-and-retry. The stage scripting must be portable to other maps and re-runnable on new builds. Editing is second.

## Why every attempt failed (from the Sep 9 - Oct 12 record)
1. Every defect was found by watching a PC take after the fact: trunks at the lens, boulder stops the shove, POV dies, camera snaps, runners hit walls, scope loses target. Each discovery cost a PC take (~1 min) plus an agent round (~5-10 min). Nine haters versions, seven ragdoll versions, none converged.
2. Stages were hand-placed by numbers guessed per shot (degrees, radii), tuned by trial on the PC. Nothing knew where the open lane, the clean pit edges, or the tower's lines of sight were.
3. Correctness rules lived in prose for agents, which they skipped or misread. Gates ran only after capture.
4. The head shipped versions without checking them against the base and all notes.

## The engine
### A. Map knowledge, baked (decision 80: map-agnostic, baked data)
`tools/capture/lane_bake.gd` runs headless per map and writes `tools/capture/lanes/<map>.json`:
- the ring lane centreline as arc samples (deg -> position, width, floor height);
- per sample: pit-side edge type (clean drop | lip | boulder | rail), inner-side obstacle distance, nearest occluder distance along the lane (trunks, pillars, cover), overhead clearance;
- tower windows: for each window, which lane samples are in line of sight and the apparent size of a runner there at a given scope fov;
- cover points, pads, traps, portal arc, spawn pads.
Built from the map's collision and visible meshes; no map names in the shot code. Re-baked when the map changes (hash of the map scene).

### B. Shot spec, declarative
`tools/content/shots/<name>.json`, written by the head from Ryan's note. Fields are intents resolved against the lane bake, never degrees:
```
{ "map": "forest", "pov": "runner",
  "players": {"runners": 3, "guard": "tower"},
  "find": {"stretch": {"min_len_m": 18, "edge": "clean_drop", "occluder_min_m": 3.0, "los_from_tower": false}},
  "cast": [{"role": "pov", "lane": "inner", "lead_m": 0},
           {"role": "victim", "lane": "edge", "lead_m": 1.5},
           {"role": "extra", "lane": "mid", "lead_m": 6}],
  "beats": [{"t": 3.2, "who": "pov", "do": "shove", "target": "victim"},
            {"t": 4.0, "who": "pov", "do": "look", "at": "victim"}],
  "end": {"after": "victim_below_rim", "plus_s": 0.7},
  "camera": {"human": true, "glance_rate": "normal"},
  "seconds_max": 9 }
```
`shots.py resolve` picks the concrete stretch from the bake (first match by numbers), places the cast, and writes `stage.json`. The same spec resolves on another map or a rebaked map.

### C. One generic stage runner
`tools/capture/stages/spec_stage.gd` replaces per-shot .gd files: reads `stage.json`, casts bodies on the lane via the existing human driver (`stage_driver`, `player_feel`, `human` layer: steering, overshoot, glances, flinch), runs the beats, fires the tower per the spec. All existing per-shot stages stay for the trailer; new shots use the runner.

### D. One dry run, no search (revised after Gemini audit 3)
There is no seed/stretch retry loop. The resolver places the cast from the bake by numbers; beats that need contact (shove, hit) are kinematic: for the beat window the driver locks the victim's position relative to the shover (or the guard's aim to the target), then hands the body to the ragdoll. A shot is right because of A+B+C, not because a check passed.
`shot.sh` still runs the stage headless once on the Mac (seconds, fixed-fps, same seed as the PC take; the trailer tapes proved fixed-fps runs reproduce to the frame). That run is a smoke, not a search: if it reports a lens occluder, a camera jump, a POV out/shoved, a body off-lane or against geometry, an animation state stuck, a beat that didn't fire, or the end rule unmet, the SPEC or the BAKE is wrong and the run stops with the numbers for the head to fix the model. It never re-rolls.
Spec validation: strict JSON schema with enums (edge: clean_drop|lip|boulder|rail; lane: inner|mid|edge; do: shove|look|hit|stop) before Godot is touched.
run_clip also logs per frame: each body's animation state and playback position (stuck = same position > 0.3 s while moving), and for a guard POV the angle between aim and target (tracking lag).

### E. Capture and cut (existing v2 tooling, kept)
pc_rough real-time take, lossless; assemble.py voice-first cut, segment cache, pop/stack captions appearing instantly, cards timed to words, no hold/slow; versioned delivery, never overwrite; notes ledger as the only base; agent briefs verbatim.
Post-capture gates stay as a backstop only (desktop frames, internal cuts, duration) and should never be the first place a defect is found.

### F. Head duty
Before anything reaches Ryan: a 1 fps sheet of the cut beside the base, checked against every note on that short. A version that is not better on every note goes back, unseen.

## Not in scope now
Gemini review of videos (Ryan's rule), virtual monitors, LLM clip matching, inventory embeddings.

## Audit (Gemini 3.1 Pro, audit 3)
Keep: stage_driver primitives (steer, human, lane, shove, look_back), player_feel, run_clip, shot.sh capture. Delete: per-shot stage .gd files for new shots, runtime probing as the source of placement, any retry loop. Missing (now added above): kinematic beat locks, schema enums, animation-state and scope-tracking logs. Base-version and trailer-footage refusals already exist in version.sh/shot.sh.

## Acceptance
`shots.py resolve forest_pov_shove && shot.sh haters 7` yields one take, first try, with the shove and fall in frame and none of the listed defects, inside 10 minutes. Then haters from the agreed script in one run.
