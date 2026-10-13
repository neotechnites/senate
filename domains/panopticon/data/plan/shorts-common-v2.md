# Shorts: rules for every short agent (pipeline v2, 2026-10-12)

## Hard limits
- First draft within 20 minutes of your start. An iteration within 10 minutes. Report your wall time.

## Setup
- Worktree `~/Documents/olympus/pano-<name>-v2` on branch `work-<name>-v2`, created from origin/content-v2.
- Never touch Ryan's checkout `~/Documents/olympus/panopticon` or `C:\dev\panopticon`.
- Read `tools/content/PLAYBOOK.md` and nothing else of the tooling unless a command fails.
- Shot lookup: `~/Documents/senate/domains/panopticon/data/plan/shots-catalogue.md`.

## The pipeline is the only way
- Brief: `tools/content/projects/<name>.md`. Run `tools/content/short.sh <name> --tag vN`. It holds the PC lock from sync to assemble, so three shorts share the PC safely.
- Never run shot.sh or assemble.sh on their own on the PC.
- Never write a cutter, caption or ffmpeg script of your own. If the pipeline can't do something, stop and report the gap in one line.
- Real time only. Movie Maker exists only for `--final`.

## Footage rules (every one paid for)
- Trailer shots are off limits: no `trailer_*` stage, no trailer tape, nothing from `trailer_reveal`.
- Gameplay must look like real people playing:
  - Use bot matches or tapes with the human layer. No robotic staged look.
  - Bodies are placed and moving before the cut. Nothing spawns in frame.
- Heat shimmer off (`shimmer=0`). No HUD; a guard POV keeps the crosshair or scope. Game audio off.
- The tower eye looks at the POV player in any shot where it's visible.
- The camera never clips into models or terrain.
- No Windows desktop at the head or tail of any shot.
- No clip shorter than its line: no freeze, no slow motion, no loops. Get more picture instead.
- Text never shares screen space with other text or cards. Quotes stack, each in its own slot.
- Ryan's examples are concepts, not literal rules.
- Captions keep Ryan's typos exactly.

## Reuse
- A new version starts as a copy of the previous version. Only the lines Ryan's notes name change.
- Untouched lines stay frame-identical.

## Before you report
- Make one 1 fps contact sheet of the finished cut.
- Look at it against every note: right shot, eye, clipping, desktop, text layout. Fix real defects only.
- No other checks.

## Deliver and report
- Delivery goes to `~/Desktop/panopticon-renders/content/shorts/<name>/<name>_<tag>.mp4` (short.sh does it).
- Commit your brief and any new stage, push your branch, don't merge.
- Report in at most 80 words: the Mac path, its length, your wall time, and any deviation with the reason.
