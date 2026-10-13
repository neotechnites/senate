# Content pipeline build: shared rules for WP1-WP4 (head brief, 2026-10-12)

The design is `~/Documents/senate/domains/panopticon/data/plan/content-pipelines-design.md`. Read ALL of it. Your work package is in section (g). The goal, in Ryan's words: once he has the script and shots written out, he should be "one prompt and 20 minutes away from a short that looks identical to what I've described". The same goes for devlogs and trailers. The rules must be ENFORCED by code and gates, not prose.

- Game repo `~/Documents/olympus/panopticon`. Ryan's checkout there is on marble-tot-view with Godot open: never touch it. Work in `~/Documents/olympus/pano-cp-wpN` on branch `cp-wpN` from origin/main. Own only the files your WP lists.
- Schemas: WP1 writes `tools/content/cp/schema/*.json` FIRST, in under 15 minutes, and pushes branch `cp-schema` to origin. Until then, WP2-4 build against the abridged interfaces in the design. Merge origin/cp-schema when it lands, and adapt to it.
- PC: `ssh panopticon-pc` (PowerShell `-ExecutionPolicy Bypass`). Locks apply per capture only, never per project. Below-normal priority.
- Voice is ALWAYS en-US-AndrewNeural +5% through the patched edge-tts endpoint (wss://api.msedgeservices.com/tts/cognitiveservices/websocket/v1?Ocp-Apim-Subscription-Key=<token>). Fail loudly; never substitute another voice.
- Gemini: GEMINI_API_KEY is set. Use google-genai with file upload, as the design says.
- Test every tool on real data from today's three shorts (pano-short-* worktrees, PC content\haters_short, content\portal_spin, content\shorts\ragdoll_vnext, content\ragdoll_short). Unit tests are a bonus, not the proof.
- Never put files on the Mac Desktop root. No unbounded filesystem searches.
- When done, commit and push your branch. Don't merge to main; the head merges all four. Report in 6 lines or fewer: what works end to end, what doesn't, and the commit.
