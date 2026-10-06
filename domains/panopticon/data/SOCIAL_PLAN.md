# PANOPTICON — audience plan

Ship 2027-04-01. ~29 weeks. Budget: 4 h/week, no more. Mechanics win the rest.

## 1. Channels, in order

1. **Vertical video (TikTok + YouTube Shorts + Reels).** One clip, three uploads. The only place strangers find you without you knowing them first.
2. **X + Bluesky.** Same text both. Where devs, press and creators live, and where a clip gets quoted instead of scrolled past.
3. **Reddit** (r/godot, r/IndieDev, later r/Games for the trailer). Reach with zero followers, and Godot + hell pit + solo dev is its diet.
4. **Discord.** Small numbers, best conversion. It is also the playtest queue.
5. **YouTube long-form devlog, monthly.** Expensive, but everything else points at it and it is where a creator can understand the game in one sitting.

Skip: Instagram feed posts (Reels only), Threads, Mastodon, a newsletter, a website. Skip itch.io as a channel — use it to host playtest builds, nothing else.

## 2. Per channel

**Setup, once, ~3 h.** Handle `panopticongame` everywhere. Avatar: the tower gunport render, square. Banner: `map_base_run.png`. Bio: *One guard in the tower. Everyone else runs the pit. Solo-made in Godot, Steam 2027.* Pin one clip.

- **Vertical video.** 30–45 min per post when the footage exists: trim, a 4-word hook, no music you did not make. 3–4/week. A good one is 8–15 s, one idea, payoff inside 2 s: a ghost shove-catching a runner mid-jump over the lava river, or a crosshair finding a runner through a stalactite gap.
- **X/Bluesky.** 10 min. 4–5/week: the day's clip, a screenshot, one line about a mechanic you changed and why. Reply to other devs more than you post.
- **Reddit.** 20 min. One post/week per sub. Screenshot Saturday on r/IndieDev, a technical post on r/godot (pixel lava, GL Compatibility, bots that use cover). Answer every comment.
- **Discord.** 30 min setup, 15 min/day. Channels: #devlog, #clips, #playtest, #bugs. Post the raw clip here before it goes public.
- **Devlog.** 4–6 h. Monthly, in a week where nothing else lands. 6–10 min, one problem and how you solved it.

### 10 posts, best first

| # | Post | Capture |
|---|------|---------|
| 1 | Lava waterfall reveal: walk to the lake edge, camera tilts up the falling lava wall | S5 lake, first-person, human, **Y** on, HUD off |
| 2 | Ghost shove-catches a runner mid-jump between platforms; he lands in lava | S2 chain, third-person/spectator, human ghost + bot runner |
| 3 | Guard scope finds a runner through a stalactite gap, one shot | S1 cave, guard POV, bots running, zoom held |
| 4 | Hologram decoy eats the shot; the real runner sprints past. Cut guard POV → runner POV | S1 or S2, two passes, human, **2** |
| 5 | Three demon pads back to back, no cuts, no HUD | S4 demon run, first-person, human, **no T** (real speed is the point) |
| 6 | Camo runner walks the open lane while the scope sweeps over him | S1 lane, guard POV bot, human runner, **4** |
| 7 | "One guard. Seven prisoners. One lap." Slow orbit of the whole pit, text on screen | Bots only, cinematic camera, no keys |
| 8 | Death cam: shot mid-jump, body falls, camera pulls up to the tower's own view | S2, bots, spectator overlook |
| 9 | Greybox vs painted hell rock, same camera pose, hard cut | `tools/shot.gd`, two stills |
| 10 | Shield eats a headshot at the portal; runner finishes the lap | S5 → portal, human, **1**, **Y** off |

## 3. Capture pipeline

On the PC: OBS at 60 fps for anything you play, Godot's `--write-movie` for anything that plays itself. `tools/shot.gd` already covers stills from an arbitrary pose.

What is missing, in order:

1. **`tools/capture/run_clip.gd`** — loads `scenes/match/match.tscn`, bots only, ghosts on, fixed seed, a named camera path per section (`--shot=s2_chain`), runs N seconds, quits. With `--write-movie` that is deterministic b-roll while Ryan is elsewhere. This is the pipeline.
2. **A detached free camera during a live match**, plus a key to hide the HUD. Today the only non-player camera is `SpectatorProfile`, which exists only after you die, so every clip is locked to what the player was looking at.
3. Cheap: `tools/net/scripted_intent_source.gd` already replays intents. Record a human's intent stream to a file and you have a replay — reshoot the same shove from four angles without landing it again.

## 4. Six weeks

- **W1 (3 h):** accounts, avatar, banner, bio. Cut posts 1, 3, 9 from existing footage. Post one.
- **W2 (4 h):** build `run_clip.gd`. Post 7 and 2.
- **W3 (3 h):** free camera + HUD toggle. Post 5, 8. First Reddit post (r/godot, the lava shader).
- **W4 (4 h):** devlog #1: "one guard, everyone else runs". Discord opens in its description.
- **W5 (3 h):** sculpt S3 once its blockout is done. Posts 4 and 6 off S1/S2. Screenshot Saturday.
- **W6 (3 h):** intent replay. Recut the best clip from a better angle. Ask Discord for playtesters.

## 5. Metrics

Track weekly: clip views and completion rate, follower count per channel, Discord joins, wishlists once the page exists.

**The one number each week:** before the Steam page, *new followers across all channels*. After it, *wishlists added*. Nothing else changes a decision.

## Addendum (Ryan, 2026-09-14): the "crazy clip" format
Shorts from real sessions with friends, framed as a clip that just happened in an existing game, not as promotion: e.g. the guard missing 15 shots while a friend twirls and dodges. No title card, no hook text, caption written like a player ("bro would not die"). Capture with OBS during playtests; reshoot angles with the free camera / intent replay. Posts 2, 4, 6 in the table become this format once there is human footage.

## Addendum (Ryan, 2026-09-14)
Get a comment with a suggestion, implement it, make content on how it was implemented from that comment (the parry-the-nuke clip that went viral on Twitter).

## Regime decision, 2026-09-14 (Ryan's words)
"do tiktok and instagram at the same time, and maybe some shorts, but keep doing devlogs on youtube, then we'll see how stuff looks. so stop concluding, lets do a few things and see how stuff works. the worst case scenario is a banger gets released on youtube and now i cant use it closer to release, or i release a dud on youtube and then when i do release those poorly performing videos dont do very well"

## Experiment log
| # | Posted | Piece | Length | TikTok | YouTube | Instagram | Notes (Ryan) |
|---|---|---|---|---|---|---|---|
| 1 | 2026-09-15 late | Shove short, rough_v11 (music) / v11_nomusic (TT+IG) | 59 s | 650 views, avg watch 14 s | 1,300 | not visible (needs Creator account) | "pretty good for less than 24 hours, but they seem to not be getting any more" |
| 2 | 2026-09-23 early | Projectile short, rough_v11_ryan (music, YT) / tiktok_v11_nomusic_1080 (TT) | 52 s | ~1,000 views | ~1,200 | account permanently disabled 2026-09-22 (automated fake-account classifier; one appeal, refused) | Ryan: "alright these ones did slightly better. about 1k on tiktok and 1.2k on youtube. better ratio of likes, and longer retention on youtube". Both posts are Ryan's own voice (post 1 used TTS only in the pre-record rough cuts). What changed vs post 1: comment-reply framing with an on-screen comment card (the real comment was on the lost Instagram, so it was recreated), 59 s -> 52 s, explainer rather than showcase. TikTok web/Studio upload silently failed several times ("published" with nothing on the profile, then "draft does not exist"); posted from the phone app off a TikTok-safe re-encode (H.264 High 4.1, yuv420p tv/BT.709, 30 fps, AAC, faststart). |
