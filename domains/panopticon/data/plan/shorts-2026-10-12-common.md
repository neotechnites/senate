# Shorts 2026-10-12: rules shared by every short agent (head brief)

Three shorts are wanted as ROUGH DRAFTS, fast, and right the first time: haters, ragdoll_vnext and portal_spin. Each one is built by one agent from the Mac, which drives the PC over ssh (`ssh panopticon-pc`; PowerShell needs `-ExecutionPolicy Bypass`; the Mac has no sshd, so the Mac pulls from the PC).

## Read first (these rules were paid for)
- Game repo `~/Documents/olympus/panopticon` (origin/main ed473b24 or later). Read `tools/content/PLAYBOOK.md`, `tools/content/README.md` and `tools/capture/stages/README.md` IN FULL and follow them. Ryan's checkout at `~/Documents/olympus/panopticon` is on his local branch marble-tot-view with Godot open: NEVER edit it. Work in your own worktree `~/Documents/olympus/pano-short-<name>` on branch `work-<name>` from origin/main.
- Pod DB `~/Documents/senate/domains/panopticon/data/panopticon.db`, decisions 195, 197, 199, 225, 327-343 and 355-356 (forest short and devlog failures). No unbounded filesystem searches.

## Hard rules
1. Portrait native 1080x1920 (never landscape then cropped). No HUD; a guard POV keeps the crosshair only.
2. Real-time rough capture (ddagrab), not Movie Maker. Film at the game's own lighting (no exposure/ambient overrides). The PC's saved settings are windowed 1280x720; run_clip.gd holds the take's size, so check the game fills the frame.
3. Trim every take at the last game frame: no Windows desktop at the head or tail of anything.
4. Never slow a clip below 1x and never freeze. A line that outruns its picture gets more picture.
5. Every POV looks like a human playing (`human` on, glances, flinch). Bodies are placed and moving before the cut; nothing spawns in frame.
6. Captions: burned in, at 0.72 of the height, never covering on-screen text such as comment cards. Haters is the exception (see its brief).
7. The PC display sleeps after 10 min and ddagrab then records nothing. Before capturing, wake it with a 1 px mouse nudge in the console session, as the playbook and decision 225 describe.
8. Below-normal priority, ffmpeg capped at 4 threads.
9. **ONE PC JOB AT A TIME.** Three agents share one PC and one `C:\dev\verify`. Do all prep on the Mac first: brief, script table, voice (edge-tts), stage plugin, and a headless smoke with run_clip.gd on the Mac (never windowed Godot on the Mac). Then take the PC lock before ANY `sync.sh`, `shot.sh`, assemble or render: `ssh panopticon-pc "New-Item -ItemType Directory C:\dev\content.lock"`. That command fails if the lock exists, in which case wait 30 s and retry. Write your short's name into `C:\dev\content.lock\owner.txt`. Do every PC step for your short in one go, then `Remove-Item -Recurse C:\dev\content.lock`. Also, before your first PC step, check `tasklist` for Godot/ffmpeg left by the old PC-side agents. If any are running and you don't hold the lock, wait.
10. Existing work: the PC Claude session was building these shorts and has been told to stop and keep its files. Check `C:\Users\ddd\Desktop\panopticon-renders\content\shorts\<name>\` and `C:\dev\worktrees\<name>` for takes, TTS or stage scripts you can reuse. Reuse only what matches your brief exactly.
11. Rough draft means: first good take, no dailies review round, and no showing shots to Ryan before the cut. Do one look of your own at 1 fps over the finished cut, checking for desktop frames, a game that doesn't fill the frame, frozen frames, or a wrong shot. Fix only real defects.
12. Deliver `final\<name>_v1.mp4` on the PC, and copy it to the Mac at `~/Desktop/panopticon-renders/content/shorts/<name>/<name>_v1.mp4` (never the Desktop root). Commit your stage and brief files on `work-<name>` and push the branch. Don't merge to main.
13. Report in 5 lines or fewer: Mac path, length, and any deviation from the brief with the reason.
