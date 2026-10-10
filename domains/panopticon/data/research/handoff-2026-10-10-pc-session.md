# Handoff: PC session 2026-10-09 evening -> 2026-10-10 ~02:00 (Ryan returning to the Mac)

READ THIS FIRST ON THE MAC. The PC was authoritative for this session (Mac away). UPDATE 02:20: the PC now has GitHub access
(new key ~/.ssh/olympus_ed25519 on the PC, alias github-olympus; both repos point at GitHub over SSH). Pod pushed (f805da6+),
game main pushed = 4d7a990f (PC merges + the Mac's beach-docs commit). The Mac just pulls both from GitHub as normal.

## 1. Devlog 0 script (task 290) -- WHERE WE ARE
Files: data/research/devlog0-script-notes-2026-10-09.md (Ryan's draft, verbatim, in order), devlog0-transcripts-2026-10.md
(the seven-devlog research + outline), devlog0-timeline-2026-09-09_to_10-09.md (day-by-day of the month, for the log section;
two lines known wrong: Oct 7 "music licensed" is false, Oct 5 "tower ending" is the trailer's ending).

AGREED ORDER (final, after several revisions; Ryan rejected concept-first and rejected any "what I'm going to make" feature section
as marketing, not a log):
  hook (advice montage; last line must PLANT "deep": "online, multiplayer, and -- the part they'd hate -- it's deep")
  -> intro (2 lines) -> origin (Duck Hunt story; prop hunt->Witch It, TTT->Among Us) -> premise + Invincible-style title card
  ("being watched by someone with power over you and you can't tell if they're looking... that sounds like a PANOPTICON")
  -> hinge ("that sounds like exactly the kind of game I'm about to complain about": friendslop, 3 hours and never again)
  -> thesis (depth: Melee/Game & Watch brother story, Nuketown loadouts, Monkey Ball minigames, Chao Garden; "fun of friendslop
     with the depth of games that had to be worth your money") -> cost beat ("netcode... content takes time... these are the art
     skills I'm working with" over a bad map) -> coda ("I can't let this game go unmade... do it justice")
  -> THE LOG: "So what does this actually look like? Right now -- like this." Chronological month, failures INSIDE it as its turns
     (not a separate 'what broke' section), ends on the forest before/after as the climax -> open questions + one named next
  -> ask (last 30 s only).
WRITTEN SO FAR: 931 words (hook 80, intro 25, origin+card 234, premise 67, hinge+thesis 382, cost+coda 143) ~4:55 at 190 wpm.
NEXT TO WRITE: the log, ~800 words (first evening+bots ~150, netcode ~100, maps ~250, look + forest before/after ~200, two
failures woven in). Then open questions+next ~150, ask ~100. Target total ~2,100-2,200 words, 11-13 min.
Ryan's last paragraph ("I'm not sure yet, not ready to share") is to be replaced by the log pivot line above.
Title: option 2 "I'm making the one game every solo dev is told not to make". Hook: real clips of YouTubers' advice if cheap,
else Ryan says it. Project started 2026-09-09 (first commit) = one month; "year and a half" is the idea.

Chris Zukowski exercise (done tonight, feeds the Steam page later): four key gameplay elements SETTLED = 1) Snipe runners from
the tower 2) Race to the portal 3) Sabotage the other prisoners 4) Survive each map's traps. Reserve phrases: bait the sniper /
break on the reload; whoever makes it out takes the rifle; a different prison each round. Three short-description drafts recorded
(decision "steam short description: three drafts v1"); Ryan: "terrible, B is the best, I'll do it by hand after watching Chris".

Playtime comparables (for the thesis): Oh Deer 1.9 h avg, Content Warning 5.2, PEAK 14.2, R.E.P.O. 20.4, Lethal 25.4 | Crawl 4.6,
Cuphead 12.6, Portal 2 16.6. Aim "3 hours and never again" at the clones, not at Lethal/REPO.

## 2. Forest short (task 385) -- v11 IS THE POST
content/forest_short/forest_short_rough_v11.mp4 (49.8 s, Ryan's voice from "Audio Clips\short 6\short 6.aup4", Sunshine Airport
MK8 bed at short 3's level, -14.1 LUFS / -0.9 dBTP, captions burned, effects take refilmed to his words, no desktop frames,
last TTS tail cut, holds after "and haze" until "These changes"). Visuals approved by Ryan at v5. Post copy is in the chat log /
below. Versions v4..v11 and every note are in notes.md (top entry = newest). Posting = Ryan.
Copy -- TikTok: "before / after of my forest map. the only real change was the lighting. what would you add or change?
#gamedev #indiedev #devlog #godot #n64 #lowpoly #fps #multiplayer #beforeandafter #PANOPTICON".
YouTube title: "I lit my forest map like a real forest (before / after)". Pinned comment: "the 'before' isn't a joke, that's
genuinely what it looked like with the lighting off".
Music ruling: Nintendo isn't in TikTok's library; uploaded as original sound. YouTube = Content ID claim, video stays up, no strike.

## 3. Game repo merges to main tonight (PC, C:\dev\panopticon)
b34ff950 beach-island6 (from agent clone panopticon-island: lighthouse foundation, hut z-fight, waterfall into a plunge pool,
  road bed) -- Ryan has NOT judged it; task 386 stays open.
5d853670 marble finish bits (tower texture test, shot.gd --traps=open) -- the real marble finish items (trapdoor nits, lane
  layout, cues, ToT) are NOT done; ToT trial 2 is on branch marble-tot, unmerged.
a6d335b8 forest-fog pass 1 (tint only; Ryan: "did literally nothing").
a323297f forest-fog pass 2: the mist was BRIGHTER than the haze and excluded from depth haze (fog_disabled), so it read as a lit
  plate; now hazes with distance, values down in the gloom. Ryan has not judged it in game. Frames: proofs/forest/fog/pass2_*.png.
Editor rule reaffirmed (decision 162): after a merge, Reload the open scene, never Save first.

## 4. Open on Ryan
devlog hook (clips vs spoken); the log section (his words); which short-description; fog + beach + marble judged in game;
Steam tax/banking (18) and Coming Soon vs full page (96) against the 2026-10-15 HARD date; the four gameplay elements were
decided on the Mac earlier and never stored there -- check that session and reconcile with the settled set above.

## 5. Process notes
Capture on this PC: Ryan chose "leave it; queue captures" (filming opens the game window on his screen). Agents that wait on
background jobs stop and must be resumed; one-number edits must be briefed as the exact line, not the folder (Ryan: "that should be
a 2 second thing"). Four lectures of Chris's course are transcribed in data/research/chris-lecture-transcripts (one has no
transcript; needs the Mac browser).
