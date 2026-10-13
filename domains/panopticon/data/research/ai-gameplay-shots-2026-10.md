# AI / agent scripted gameplay shots: research (2026-10-12)
Scope: Godot 4 stage + capture pipeline. Source = web search summaries (abstracts, docs); not deep-read. Items marked [unverified] are claims from search snippets or my background knowledge.

## (a) LLM/agent to in-engine shot choreography
No published system writes *first-person gameplay-bot* choreography from a sentence. Closest work is cutscene/camera planning; all share one pattern: LLM emits a small structured plan, a deterministic executor runs it.
- **Cutscene Agent** (arXiv 2604.25318, Apr 2026): director agent + animation/cinematography/sound subagents, engine reached via MCP (issue ops, observe scene), visual feedback loop, CutsceneBench. Cinematographer uses a *tool whitelist + templates* (Dolly, Orbit...) and assigns cameras to time ranges on a cut track. https://arxiv.org/pdf/2604.25318
- **AI Director** (Dartmouth MS thesis 2026, Unity): LLM writes editable shot-strategy plans; deterministic layer executes in real time. Plan = inspectable/editable. https://digitalcommons.dartmouth.edu/masters_theses/277
- **VERTIGO** (2604.02467, Unity): script -> structured shot attributes from film-theory value sets -> trajectory generation. https://arxiv.org/pdf/2604.02467
- **Camera and Lighting Agent** (2606.31946): LLM maps narrative cues to camera behaviours from a skill library, then optimises path for occlusion avoidance. https://arxiv.org/pdf/2606.31946
- **Prose Storyboard Language** (Ronfard): one-sentence-per-shot limited vocabulary, human+machine readable: a model for our shot DSL. https://arxiv.org/pdf/1508.07593 ; Cine-AI (2208.05701) cites declarative camera-idiom languages.
- Intermediate reps seen: template names + parameters on a time track (Cutscene Agent), attribute records (VERTIGO), strategy plans (AI Director). Nobody uses behaviour trees for shots. Convergent lesson: constrain the LLM to a whitelist of verbs with numeric params; never let it write raw engine code per shot.

## (b) Deterministic replay / input tape, Godot 4
- Godot has **no first-party replay**. Community pattern: seeded RNG + list of InputEvents/actions stamped with physics tick, replayed via Input.parse_input_event or direct action injection. [secondary source: tessl skill doc] https://tessl.io/registry/testland/gameplay-recording-replay
- **Klotho** (C#/.NET, 4.4+): fixed-point FP64, record/playback/seek, deterministic physics; needs C#. https://godotengine.org/asset-library/asset/5234
- **Physics caveat**: Godot Jolt README explicitly disclaims determinism; upstream Jolt is deterministic same-binary/platform, cross-platform needs CROSS_PLATFORM_DETERMINISTIC build (~8% cost). Rapier plugin claims cross-platform physics determinism but scene tree/input/scripting are not. https://godot.rapier.rs/blog/balaur-engine/ ; https://www.gdquest.com/library/glossary/deterministic_simulation
- Implication: tape replay is reliable on the *same machine+binary+fps*; across Mac/PC expect drift. So record tape of *intent* (target waypoints, look targets, beat triggers), not raw key presses, and use closed-loop steering toward waypoints so drift self-corrects. Keep final capture on one machine.
- **GdUnit4 scene runner** can simulate input, await signals/conditions: usable as a test harness around a shot. https://store.godotengine.org/asset/mikeschulze/gdunit4/

## (c) Human-like first-person camera
- Mouse path synthesis: minimum-jerk surge then corrective submovements fits real pointing better than pure min-jerk over long moves (arXiv 2110.00443); Bezier path libs with deviation/jitter/easing exist (BezMouse, pyclick). For a trailer, apply min-jerk (or critically damped spring) to yaw/pitch with overshoot + small correction. https://arxiv.org/pdf/2110.00443
- Gaze/glance: Andrist et al. head-eye coordination model (ICMI 2012), parametric, validated: https://www.microsoft.com/en-us/research/?p=557628 ; dwell-time-dependent head contribution (Pan et al., via arXiv 2602.06164): https://arxiv.org/pdf/2602.06164
- Concrete defaults (Convai Unity SDK): micro-saccade interval mean ~1.8 s, max 2.5 deg, 0.07 s duration. https://docs.convai.com/api-docs/plugins-and-integrations/convai-unity-sdk/utilities/gaze-and-attention/profiles-and-tuning
- Not found: published first-person "bot reads as player" camera model. Build from above: glance scheduler (look at objective -> scan side/threat -> back), velocity profile bell-shaped, pitch rarely exceeds ~±30 deg, tiny drift/noise 0.05-0.2 deg, slight lag behind movement direction. [unverified numbers beyond Convai]

## (d) In-engine shot validation
Searches found no cinematic-tool-specific literature; QA practice [background knowledge, unverified]: event log with frame index + sim time; assertions on named events ("door_opened at tick N ±2"); camera-frustum + raycast visibility of subject (center and 4 bbox corners, per frame, % visible); screen-space bbox size/position of subject vs shot spec; check no clipping (camera sphere cast vs geometry, near-plane penetration); frame-hash/pixel-diff against golden frames for regression. Cutscene Agent uses visual feedback loop (render, VLM critique); Camera/Lighting Agent optimises for occlusion. Pattern: executor emits JSON telemetry per shot; validator script passes/fails before any render is looked at.

## (e) Godot 4 cinematic tooling
- **Movie Maker mode**: `godot --path P --write-movie out.avi --fixed-fps 60 --resolution 1920x1080 --quit-after N`; fixed delta each frame so render speed doesn't matter; works in exports; writer type differs by version (AVI/MJPEG in 4.1, OGV in newer; custom MovieWriter possible, e.g. PNG sequence). Resolution capped by display unless stretch disabled/canvas_items. https://docs.godotengine.org/en/4.4/tutorials/animation/creating_movies.html ; https://godotengine.org/article/movie-maker-mode-arrives-in-godot-4
- **Phantom Camera** (Cinemachine-like): priority-based virtual cameras, follow/look-at/framing, per-camera tween on cut, path follow. Fits "shot = virtual camera + priority swap". https://github.com/ramokz/phantom-camera ; https://phantom-camera.dev
- No Godot Cinematic-Sequencer equivalent found; AnimationPlayer with method/call tracks is the built-in timeline.

## Use now
1. Define a shot JSON (Prose-Storyboard-style): verb whitelist (move_to, look_at, glance, hold, trigger, cut) + numeric params + `expect` events; LLM fills JSON only.
2. Executor in-engine reads JSON, runs everything in `_physics_process` on fixed ticks; time = tick count, never wall clock.
3. Record *intent tapes* (waypoints, look targets, trigger ticks) with a seeded RNG, not raw keys; closed-loop steer so Mac/PC drift self-corrects.
4. Capture with `--write-movie --fixed-fps 60 --quit-after N` (or PNG-sequence writer) on the one capture machine; cross-check same build on both machines once.
5. Camera feel: yaw/pitch via min-jerk/critically damped spring with overshoot-and-correct, Convai saccade defaults (1.8 s, 2.5 deg, 0.07 s), glance scheduler driven by the JSON `glance` verb.
6. Per-frame telemetry JSON: tick, cam transform, subject visibility %, screen bbox, named events; validator asserts beats land within ±2 ticks and subject visible >= threshold before render review.
7. Use Phantom Camera (or plain Camera3D) for non-bot cuts/orbits; keep bot POV as a separate camera.
8. Wrap a shot run in GdUnit4 scene runner (await signals) as the pass/fail harness.

## Dead ends
- Packaged Godot input record/replay addon: none found; Klotho is C#-only.
- Relying on Godot Jolt cross-platform determinism: disclaimed.
- Video-generation camera papers (LAMP, CamPilot, Camera Artist): pixel generation, not engine control.
- Bezier mouse libs: 2D cursor, not 3D camera; use only as inspiration.
- Raw LLM-written GDScript per shot: no source supports it working reliably; every system constrains to templates/whitelists.
