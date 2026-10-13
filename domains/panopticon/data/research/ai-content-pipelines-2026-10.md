# AI content pipelines and automated gameplay capture (2026-10)
Method: WebSearch snippets only (no deep page reads, ~20 min). Claims marked [unverified] come from third-party blogs or search summaries; check the primary source before relying on them.

## 1. Agent-driven video pipelines (script -> shot list -> footage -> cut)

**What exists**
- **OpenMontage** (AGPL, GitHub calesthio/OpenMontage, mid-2026). The coding agent is the orchestrator. A YAML pipeline manifest plus per-stage "director" skill files drive Python tools. Python does tools and persistence. The agent does creative decisions, self-review and checkpoint policy. A proposal stage fixes audience, format, duration, aspect, tone and blocked claims before anything renders. A human "Gate" approves cost before paid generation. Render paths are FFmpeg, Remotion and HyperFrames. Script diff, scene manifest, caption file and render command are all separate inspectable artifacts. Sources: [AGENT_GUIDE](https://cdn.jsdelivr.net/gh/calesthio/OpenMontage@main/AGENT_GUIDE.md), [silenceper](https://silenceper.com/en/article/2026-07-31-openmontage-agent-video-production/), [DevelopersDigest](https://developersdigest.tech/blog/openmontage-agentic-video-production). Listings disagree on status and counts [unverified].
- **FireRed-OpenStoryline** (Apache-2.0): natural-language editing via an LLM agent, MCP server, human-in-the-loop refinement. [writeup](https://blog.brightcoding.dev/2026/10/08/firered-openstoryline-natural-language-video-editing-with-llm-agents)
- **Agentic Video Editor** (Gemini + FFmpeg): a reviewer agent sends feedback to a director agent, which revises the edit plan. [pyshine](https://pyshine.com/Agentic-Video-Editor-AI-Powered-Video-Production/)
- **DaVinci-AutoEdit-Agent**: a Codex skill that drafts the script and a TTS plan, builds an edit blueprint, then builds a Resolve timeline, with user confirmation at each creative stage. [listing](https://www.sourcepulse.org/projects/32085140)
- A survey counts 50+ open "script-to-video" repos active in Sept 2026, mostly generative-video oriented, not real-footage assemblers. [pixo](https://pixo.video/blog/open-source-ai-video-pipelines)
- **OpenTimelineIO** is the neutral interchange format (clips, tracks, EDL/AAF/FCPXML adapters). It is used in studio shot-tracking and cut-diff workflows. [OTIO use case: shots added/removed from the cut](https://opentimelineio.readthedocs.io/en/v0.15/use-cases/shots-added-removed-from-cut.html). I found no agent project that clearly emits OTIO [unverified].
- **Captions**: Remotion has a documented path. whisper.cpp with token timestamps, then `convertToCaptions()` (200 ms token combine recommended), then a `Caption` type (text, startMs, endMs, confidence), then `createTikTokStyleCaptions` to group words into on-screen pages. The whisper.cpp token-timestamp build may crash. [Remotion docs](https://remotion.dev/docs/install-whisper-cpp/convert-to-captions), [Caption type](https://remotion.dev/docs/captions/caption). I found no official end-to-end shorts example.

**What they get right that home-grown pipelines miss**
1. Pipeline stages are declared as data (manifest) with a separate skill/prompt per stage. Orchestration is not hard-coded in one script.
2. Every stage emits a separate inspectable artifact (script, scene manifest, captions, render command). Human review attaches to artifacts, not to opaque renders.
3. Approval gates sit before expensive or irreversible steps.
4. A proposal/brief with explicit constraints (blocked claims, duration, aspect) comes first.
5. A reviewer agent is separate from the creator agent, and the loop is bounded.
6. Edit decisions are data (EDL/OTIO/JSON timeline), so re-cutting is cheap and diffable. A change to one shot does not mean a re-render of everything.
7. Captions come from word-level timing of the final voice track, not from script text.

## 2. Automated gameplay capture

**Engine tooling**
- **Godot 4 Movie Maker mode**: forces a fixed frame delta (like `--fixed-fps`), so capture is non-real-time and frame-exact. It outputs AVI/MJPEG or PNG sequence + WAV, and supports trailers and cutscenes. Live input stays active during capture. [Godot article](https://godotengine.org/article/movie-maker-mode-arrives-in-godot-4), [docs](https://docs.godotengine.org/en/4.1/classes/class_moviewriter.html). The community addon "Movie Maker Plus" adds timestamps and MP4 conversion (4.6). [asset](https://www.godotengine.org/asset-library/asset/edit/21906)
- **Godot replay**: no first-party input replay. The community pattern is a seeded RNG plus input events tagged with `Engine.get_physics_frames()`, replayed on the same physics ticks. [Tessl skill summary](https://tessl.io/registry/testland/gameplay-recording-replay) (secondary source, and I found no named Godot addon). Godot physics is not guaranteed cross-machine deterministic. Same-machine, same-build replay is realistic.
- **Unreal**: Sequencer (Level Sequences as shots, with takes per shot), Take Recorder (records gameplay actors into keyframed tracks for later free camera work), DemoNet replay. Sequencer play rate is separate from game time dilation. [Epic docs](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-sequencer-movie-tool-overview). **Unity**: InputEventTrace for input capture, Timeline/Cinemachine for cameras.
- Pro trailer practice (shot lists, replay/free cam, time control): I found only vendor/indie material, e.g. [StraySpark](https://www.strayspark.studio/blog/cinematic-game-trailer-without-sequencer-indie-guide) (spline cameras, filmback presets). No studio postmortem retrieved. The known pattern is: record a replay or a scripted run, then re-render it with a free camera at fixed timestep, with time dilation, per shot.

**LLM and camera research**
- **AI Director** (Dartmouth master's thesis 2026, Unity): the LLM produces editable shot-strategy plans and a deterministic camera layer executes them. This is the cleanest "LLM plans, code executes" split. [thesis](https://digitalcommons.dartmouth.edu/masters_theses/277)
- **Cutscene Agent** (arXiv 2604.25318): an LLM agent generating full 3D cutscene assets in a game engine. [paper](https://arxiv.org/pdf/2604.25318)
- **LAMP** (2512.03619): the LLM writes symbolic motion programs in a cinematography DSL, deterministically mapped to trajectories. [paper](https://arxiv.org/pdf/2512.03619)
- **CinemaTraj** (2607.26910): the LLM composes atomic camera moves (dolly, orbit, crane, pan) over a scene graph. [paper](https://arxiv.org/pdf/2607.26910)
- **FilmAgent** (2501.12909): multi-agent director/cinematographer/actor roles in virtual 3D. [paper](https://arxiv.org/pdf/2501.12909v1)
- **VERTIGO** (Unity): renders previews of generated camera motion, scores them with a VLM, and trains with DPO. Reported character off-screen rate fell from 38% to about 0%. [survey 2604.02467](https://arxiv.org/pdf/2604.02467)
- **LensCraft** [paper](https://arxiv.org/pdf/2506.00988). Shared lesson: the LLM emits a small vocabulary of parameterised shot primitives, not raw transforms.

## 3. Verifying a clip matches its shot description without a human

Techniques found:
- **VLM judge on sampled frames**. About 10 evenly spaced frames plus the shot text, returning JSON scores (content, action, camera match) with a one-line rationale. [2606.16184](https://arxiv.org/pdf/2606.16184), [2607.04311](https://arxiv.org/pdf/2607.04311)
- **Event-list completion**: the VLM first describes frames, then marks each predefined event done or not done. Ask it to judge strictly. [2412.16211](https://arxiv.org/pdf/2412.16211)
- **Per-shot PASS/FAIL with a reason**, and on failure regenerate with corrective guidance and keep the better-scoring candidate. [CoAgent](https://arxiv.org/pdf/2512.22536), [FilmWorld](https://arxiv.org/pdf/2607.19038)
- **Engine-side ground truth** (standard QA practice, no specific source retrieved): log events and camera pose per frame. Check subject in frustum, screen-space size, and ray-cast occlusion between camera and subject. Check scripted events fired within the shot's time window.

Limits:
- VLMs are optimistic, weak on blur, small subjects and fine timing, and cannot judge "feels good".
- Frame sampling misses short events (a hit lasting 3 frames).
- Telemetry proves the thing was in frame, not that it was readable or attractive. A subject can be in the frustum, tiny, behind foliage, or lit badly.
- Ray-cast occlusion ignores transparent or particle occluders, and bounding boxes are coarse.
- Logs confirm "event X happened", not "the shot looks like the description". Use telemetry as the hard gate and a VLM as a soft second opinion on a few frames.
- Verifier and generator should be different models or prompts, or errors correlate.

## What transfers to PANOPTICON
1. Make the shot spec data (JSON/YAML per shot: id, duration, camera primitive, subjects, required events, bot script id) and have the LLM emit only that. Deterministic code executes it (AI Director / LAMP split).
2. Use a small vocabulary of camera primitives (orbit, dolly, track, static, crane) with parameters. Do not let the LLM write transforms.
3. Capture with Godot Movie Maker at fixed fps, so the render is frame-exact and the machine speed doesn't matter. Use PNG sequence + WAV for lossless re-cuts.
4. Replay for re-shoots: seed + input/bot script keyed to physics frame, same build, same machine. Record a run once, then re-film it with different cameras and time scale.
5. Per-frame telemetry sidecar (camera pose, subject screen rect, visible/occluded flag, event log with timestamps) written next to each clip. Use it as the hard verification gate before any VLM look.
6. VLM check as second gate on about 8-10 sampled frames, with event-list strict judging and a JSON PASS/FAIL plus reason. Cap retries (e.g. 3) and keep the best-scoring take.
7. The cut is an EDL/OTIO-style JSON timeline (clip ref, in/out, transitions, caption page refs). The ffmpeg or Remotion assembler is a pure function of it, so single-shot swaps re-render cheaply.
8. Captions: word-timed from the final AI voice track (whisper token timestamps, grouped into TikTok-style pages). Pin the whisper.cpp build.
9. Stage artifacts plus a brief/proposal with blocked claims and a human gate before publish, as OpenMontage does. This fits the "versions change only noted lines" rule: diff the shot-spec JSON between versions.
10. Separate reviewer agent from the builder agent (Agentic Video Editor pattern), with bounded review loops.

## What doesn't transfer
- Generative-video pipelines (text-to-video, diffusion camera control: CameraCtrl, Auteur, ChatCam/NeRF). PANOPTICON renders real engine footage.
- Radiance-field and ScanNet-based camera research (CinemaTraj evaluation). Only its primitive vocabulary is useful.
- Unreal Sequencer, DemoNet and Take Recorder, and Unity Timeline/Cinemachine. Concepts only, with no Godot code reuse.
- Full cross-machine deterministic lockstep replay. Godot physics doesn't guarantee it, so don't depend on it.
- Paid-generation cost gates (OpenMontage's main Gate). PANOPTICON has little paid generation.
- Whole-pipeline frameworks such as OpenMontage (AGPL, TTS/stock-asset oriented). Borrow structure, not code.
- VLM scoring as the primary gate. It is too optimistic for fine timing and tiny subjects.
