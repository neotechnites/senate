# PANOPTICON — Steam store page copy and asset list

**Drafted 2026-09-09. Paste-ready. Placeholders are marked `[PLACEHOLDER]`.**

Grounded in pod canon: `panopticon.game.definition`, `panopticon.tone`, `panopticon.tower.fiction`, `panopticon.tower.eye`, `panopticon.cover.absolute`, `panopticon.shooter.reload`, `panopticon.shooter.tracer`, `panopticon.open.guard_vision`, `panopticon.match.one_winner`, `panopticon.match.escalating_shooter`, `panopticon.player_counts`, `panopticon.launch.not_early_access`, `panopticon.not_a_message_game`, `panopticon.art.style`, `panopticon.ship.definition`, and `data/research/pricing-20260909.md`.

Tone target for every word below: **gritty but not tense.** Machine Party / STRAFTAT register. Semi-serious. Comedy ceiling is Lethal Company. Nothing on this page may read as horror, dread, or a thesis about surveillance.

---

## 1. NAME AND TAGLINE

**Store name:** `PANOPTICON`

No subtitle at launch. It is a dictionary word and Steam search will surface unrelated results (`panopticon.title`); a subtitle is the conventional fix and can be added post-launch without changing the identity. If you want one on day one, see Open Questions.

**Primary tagline (capsule art, trailer end card, social bio) — 36 chars:**

> One tower. One rifle. Everyone runs.

**Alternates, all under 40 chars:**

| Tagline | Chars | Use |
|---|---|---|
| `Move when it blinks.` | 20 | Best mechanical hook. Strong trailer end card. Weak on its own in a capsule because it hides the shooting. |
| `One shot. One long reload. Run.` | 31 | States the loop outright. Good on the vertical capsule where you have room for two lines. |
| `The eye is open. Don't move.` | 28 | Most atmospheric. Closest to the horror line you do not want to cross — use only over clearly non-scary art. |

Recommendation: `One tower. One rifle. Everyone runs.` on the capsules, `Move when it blinks.` as the trailer end card. They teach different halves of the game.

---

## 2. SHORT DESCRIPTION (Steam limit 300 characters)

**Final — 292 characters:**

```
One player holds the tower at the centre of the prison. The rest run the ring around it, unarmed, start to finish. The tower gets one shot, then a long reload, and while it reloads the eye closes and the ring goes dark. Cover is absolute. Move when it blinks. First-person versus, 1v1 to 1v7.
```

Why it is built this way: it names the asymmetry in the first clause, the goal in the second, the single mechanic that makes it a game in the third, and the player count last so nobody wishlists a game they cannot fill a lobby for. No adjectives. Nothing here is an open design question.

**Backup — 287 characters, if you would rather lead with the rifle than the ring:**

```
One player takes the tower at the centre of the prison. Everyone else runs the ring around it, unarmed. The tower has a rifle, sight of the whole ring, and a long reload. Cover is absolute, so the only thing that can kill you is the moment you choose to leave it. Reach the end and the tower is yours.
```

---

## 3. LONG DESCRIPTION ("About This Game")

Steam BBCode. Paste as-is. Everything above the first `[h2]` is what most people read.

```
[b]The tower can see the whole ring. It can only look at one part of it at a time.[/b]
You are unarmed, on foot, behind a concrete block, and the next piece of cover is fifteen metres of open ground away. The eye is open. You are not moving yet.

[h2]RUN THE RING[/h2]
PANOPTICON is a first-person versus game for two to eight players. One of you holds the tower at the centre of the prison with a rifle. The rest of you are prisoners in the ring around it, running a full lap from a start position to an end position that sits a few metres behind where you began.

Behind cover you cannot be shot. Not reduced damage, not a lower chance — [b]cover is absolute[/b]. The only thing in this game that can kill you is the moment you decide to leave it. That makes the prisoner's game timing, not dodging. You watch, you wait, you pick your window, and you commit.

[h2]HOLD THE TOWER[/h2]
You get one shot, and then a long reload.

Every shot leaves a tracer, so firing tells every prisoner on the course roughly where you were looking and what you wanted. While you reload, the eye closes and the light goes out, and the ring is dark for exactly as long as you are useless. When it opens again you have lost track of where everyone was.

So a shot costs you position, sight and knowledge, not just time. You can watch the entire ring, but you can only look at one part of it, and attention is the only thing you are actually short of.

[h2]BAIT THE SHOT[/h2]
The reload is the only safe passage on the map, and somebody has to spend their life to open it.

Draw the shot and everyone gets to move. Draw it badly and you were the only one who paid. Every prisoner would rather it was somebody else who broke cover first, and every prisoner knows the others are thinking the same thing. Nobody designed that standoff; it just falls out of the rules.

[h2]THE TOWER IS THE PRIZE[/h2]
Reaching the end does not win you the match. It wins you the tower.

The match ends when somebody wins from inside it, so everybody gets their turn behind the rifle and the whole game is a queue for one seat. There is no round timer. Instead the tower gets stronger every consecutive turn a player holds it, and you can see it happening — the reload shortens, the eye closes for less time, the dark windows get thinner. A match that has run long announces its own ending.

[h2]WHAT IS IN THE BOX[/h2]
[list]
[*] [b]First-person, 1v1 to 1v7.[/b] Tuned for 1v1 through 1v3. Larger lobbies are supported, but the small ones are what the game was built for.
[*] [b]The same movement for everyone.[/b] The tower runs, jumps and slides exactly like the prisoners do. The only thing that separates the two roles is the rifle.
[*] [b]Getting shot is instant.[/b] No ragdoll, no death animation, no waiting. It lands like a baseball to the side of the head and it is over.
[*] [b]Low-poly, and built to run on what you already own.[/b]
[*] [b]Finished at launch.[/b] Not Early Access. Not a roadmap. A 1.0.
[/list]
```

**Notes on the draft**

- The first two lines are the whole pitch and they are written to survive being read at a glance in a recommendation widget.
- Nothing above promises a feature that canon has not settled. No ghosts, no lives, no map count, no progression, no offline play. See §6.
- `[h2]WHAT IS IN THE BOX[/h2]` is where a map count, a mode list or a bot mode would go if they land. Leave the space.
- If you want the concept acknowledged in one line without the essay, add this and nothing more, under the first heading: *"The prison is built so one guard can watch everyone, and it works right up until he pulls the trigger."* That is flavour, and it is where the flavour stops (`panopticon.not_a_message_game`).

---

## 4. GENRE AND TAGS

**Genre (Steamworks dropdown, pick two):** `Action`, `Indie`.
Do not add `Casual` — it pulls the page toward the party-game shelf, and the pricing research shows that shelf is where the tone gets misread. Do not add `Strategy`.

**Tags, in the order to enter them.** The first five do most of the discovery work; Steam weights early tags heavily and users can only add more later.

| # | Tag | Why |
|---|---|---|
| 1 | **Multiplayer** | The largest true statement about the product. It is also the honest first warning that you need other people. |
| 2 | **PvP** | Separates it immediately from the co-op shelf (Lethal Company, R.E.P.O., PEAK) that the art style will otherwise file it under. |
| 3 | **Online PvP** | The specific store filter buyers of this genre actually use. |
| 4 | **Asymmetric VS** | The single tag that describes the product exactly, and the one that connects it to Dead by Daylight, Deceit and Witch It buyers. Verify the exact string in the Steamworks tag picker before entry. |
| 5 | **First-Person** | Sets the camera expectation before anyone opens a screenshot. |
| 6 | **Shooter** | True for one player in eight, but it is how the rifle half of the audience searches. |
| 7 | **Hide and Seek** | The prisoner's half of the game, and the tag that carries the Witch It / prop-hunt audience across. |
| 8 | **Sniper** | One shot, long reload, tracer. Small tag, unusually well matched. |
| 9 | **Indie** | Sets price and scope expectations correctly. Cheap to include, never hurts. |
| 10 | **Action** | Broad, high-traffic, and accurate. |
| 11 | **Competitive** | One winner per match. It is the honest label for a game with exactly one seat worth having. |
| 12 | **3D** | Cheap disambiguation against the 2D indie multiplayer shelf. |
| 13 | **Stylized** | Carries the low-poly look without committing to a register you have not chosen yet (`panopticon.art.style`). |
| 14 | **Fast-Paced** | True of the movement, and it pulls against anyone reading the capsule as slow horror. |
| 15 | **Replay Value** | Directly serves `panopticon.depth_over_content` — it is the claim you most want the page to make about itself. |

**Tags to leave off, deliberately:**

- `Horror`, `Psychological Horror`, `Survival Horror` — wrong product. This is the single worst mistake this page could make.
- `Funny`, `Memes` — above your comedy ceiling.
- `Singleplayer`, `Co-op`, `Local Multiplayer`, `Split Screen` — none of these are decided (`panopticon.testing.bots`: whether bots ship as a playable mode is undecided). Adding them and then not shipping them is a review-bomb vector.
- `Early Access` — not applicable, and Steam manages it as a status, not a tag.
- `Great Soundtrack`, `Atmospheric` — let users add these. Self-applied they read as filler.

---

## 5. ASSET LIST

Formats: PNG or JPG for all capsules and screenshots unless noted. All capsule art must carry the game's logo/title, legible at the smallest size it will be shown at. Valve rejects capsules containing marketing copy, review scores, awards, discount flashes, or "Coming Soon" text.

**Legend:** ✅ producible now · 🟡 needs art direction locked (`panopticon.open.prisoner_form`, milestone `art_direction_locked` 2026-12-15) · 🔴 needs a finished, dressed map and real gameplay footage.

### Store capsules

| Asset | Exact size | Status | What it should show for THIS game |
|---|---|---|---|
| **Small Capsule** | 462 × 174 | 🟡 | Read at 231×87 in search results. Wordmark plus one silhouette element only. Best candidate: the closed eye as a horizontal slit behind `PANOPTICON`. No characters — nothing legible survives at that size. |
| **Header Capsule** | 920 × 430 | 🟡 | The workhorse; it is the image on the store page, the library, the wishlist email. The tower centred, the eye lit, a single tiny runner in silhouette at the base for scale. Scale is the whole idea and this is the one asset that can carry it. |
| **Main Capsule** | 1232 × 706 | 🟡 | Front page and daily deal slot. The reload frame: eye closed, ring dark, three runners moving in near-silhouette. It is the most distinctive image the game owns and nothing else on Steam looks like it. |
| **Vertical Capsule** | 748 × 896 | 🟡 | Portrait, used in sales and front-page features. The only asset whose shape matches the tower. Tower full height, ring wrapping the bottom third, wordmark at the base. |
| **Page Background** | 1438 × 810 | 🟡 | Heavily darkened and blurred behind the page. Deliberately low-detail: the ring seen from above, tower light falling across it. Do not put anything you care about here. |

### Steam client library assets (required before release, not for a Coming Soon page)

| Asset | Exact size | Status | What it should show |
|---|---|---|---|
| **Library Capsule** | 600 × 900 | 🟡 | Portrait, in the user's own library grid. Can and should be the moodiest asset you make — this one is only ever seen by people who already own it. |
| **Library Header** | 920 × 430 | 🟡 | May reuse the Header Capsule. No reason to make a second one. |
| **Library Hero** | 3840 × 1240 | 🟡 | Ultra-wide banner behind the library detail page, cropped hard at every window width. Keep everything meaningful inside a ~860 × 380 centre safe area. Content: the ring stretching to both edges, tower dead centre. The aspect ratio is a gift for this game's geometry. |
| **Library Logo** | 1280 × 720, **PNG with transparency** | ✅ | Wordmark only, on transparency. Specify anchor (centre or bottom-left) in Steamworks. This is the one asset that can be finished today because it needs no game art. |

### Icons

| Asset | Exact size | Status | What it should show |
|---|---|---|---|
| **Community Icon** | 184 × 184 | 🟡 | Steam group, badges, forums. Use the eye. Nothing else survives a circle crop at this size. |
| **Client Icon** | 32 × 32 `.ico` (containing 16×16, 24×24, 32×32, 48×48) | 🟡 | Taskbar and desktop shortcut. The eye again, reduced to a slit and a pupil. |
| **Achievement icons** | 64 × 64 each | 🟡 | Only if you ship achievements. Undecided — do not budget for these yet. |

### Screenshots

Minimum 5 to pass store review. Ship 8. **1920 × 1080** minimum, 16:9, PNG or JPG. Actual gameplay only — no text overlays, no logos, no compositing. Order matters; the first is the one that appears on hover in several widgets.

| # | Status | Shot |
|---|---|---|
| 1 | 🔴 | **Tower POV down the rifle.** The ring wrapping away left and right, one runner caught mid-break between two covers, no shot fired yet. Sells the entire role in one frame. |
| 2 | 🔴 | **Prisoner POV, pinned.** Pressed against a low block, tower light sweeping the open ground in front of you, next cover clearly too far. Sells the decision, which is the actual product. |
| 3 | 🔴 | **The reload.** Eye closed, ring dark, several runners moving at once in silhouette. The most distinctive frame the game has. Should also be the basis of the Main Capsule. |
| 4 | 🔴 | **Tracer in flight**, seen from the ring, passing through where the player stood a beat ago. Teaches a mechanic no other game on the shelf has. |
| 5 | 🔴 | **Wide exterior of the ring.** Tower at centre, the full 360 lap, the end sitting just behind the start. This one image explains the map shape better than any sentence in §3 does. |
| 6 | 🔴 | **The arrival.** A runner reaching the end, a few metres behind their own starting position, tower still lit above them. |
| 7 | 🔴 | **A second map in a different theme** (hell against Victorian concrete, per `panopticon.maps.plan`). Proves variety without claiming a number. |
| 8 | 🟡 | **Lobby at 1v3**, if the lobby UI is presentable. Sets player-count expectations honestly before purchase. Cut it rather than ship an ugly one. |

### Trailer

**Spec:** H.264 MP4, 1920 × 1080 (upload higher if you have it; Steam transcodes down), 30 or 60 fps, ~10–15 Mbps, stereo AAC, audio normalised to roughly −23 LUFS with peaks below −1 dBFS. Steam requires a separate poster/thumbnail frame at the same aspect ratio. Mark it as the **Gameplay** trailer, and make sure it is first in the order so it autoplays at the top of the page.

**Status:** 🔴 — cannot exist before a dressed map and real matches.

**Beat sheet — 65 seconds, no voiceover, no review quotes, gameplay from frame one:**

| Time | Beat |
|---|---|
| 0:00–0:04 | Black. One sound: a bolt cycling. The eye opens and light falls across the ring. |
| 0:04–0:18 | Prisoner side. Cuts no longer than two seconds: waiting behind cover, a break, an arrival, a break that does not make it. |
| 0:18–0:32 | Cut to the tower. One shot. The tracer. The eye closes and the screen goes dark on the reload — hold the dark a full beat longer than is comfortable. |
| 0:32–0:47 | The bait, told in one uncut sequence: one runner draws the shot, three others move in the dark. |
| 0:47–0:56 | Escalation montage. The same reload, three times, each shorter. The dark window narrowing. |
| 0:56–1:05 | The arrival at the end, the seat changing hands. Title card, `Move when it blinks.`, `1v1 to 1v7`, `April 1, 2027`, `Wishlist now`. |

The first six seconds decide whether anyone sees the rest. Do not open on a logo sting.

### Honest schedule read

Only one asset on this page can be produced today: the **Library Logo** wordmark, and by extension a first pass at the small and header capsules if you are willing to redo them. **Every screenshot and the entire trailer are blocked on a dressed map**, and every capsule is blocked on `panopticon.open.prisoner_form` and the low-poly register (`panopticon.art.style`), which is milestoned at `art_direction_locked` 2026-12-15.

Practical consequence: **a full store page cannot go up before roughly January 2027.** A **Coming Soon page can go up much earlier** — it needs the name, the short description, the header capsule, the genre and tags, and a release date. Screenshots and a trailer can be added afterwards, and the page can be updated freely. Given `panopticon.content.strategy` counts wishlists as the launch metric, getting a Coming Soon page live with a placeholder-quality header capsule and adding real assets later beats waiting for a perfect launch page.

Two hard dates to respect: Valve requires the store page live **at least two weeks before** the release date, and the app itself must pass a build review. Also note from the pricing research: **Spring Sale 2027-03-18 to 03-25 lands two weeks before ship on 2027-04-01** — the game will not be released and therefore cannot participate, and no discount is permitted in the 30 days after release beyond the launch discount itself.

### Fields Steamworks will demand that are not covered above

- **Release date:** 2027-04-01 (`panopticon.ship.definition`).
- **Price:** `[PLACEHOLDER — $9.99]`. The pricing research recommends $9.99 with a 20% launch discount and specifically rules out $12.99 as a dominated price point. Ryan's stated instinct is $12. Not settled.
- **Supported languages:** English only unless a localisation decision exists. Say so honestly.
- **Platforms:** Windows. Mac only if it is actually built and tested (`panopticon.ship.definition`: "Mac if it can be swung"). Do not tick a box you have not run a build on.
- **System requirements:** `[PLACEHOLDER — must be measured, not guessed.]` The dev PC (i7 7th gen, 32 GB, RX 6600 XT) is the reference machine and is comfortably mid-range, so the true minimum sits well below it. Measure on the weakest hardware you can borrow before filling this in — an invented minimum spec is a refund generator.
- **Multiplayer metadata:** tick Online PvP and set the max player count to 8. Do not tick LAN, local, or split screen.

---

## 6. DO NOT CLAIM

Each of these is either undecided in canon or actively wrong for the product. Every one is a refund or a negative review if it goes on the page and does not ship.

| Do not claim | Why |
|---|---|
| **Anything about what happens after you are shot** — ghosts, lives, respawns, spectating, "come back from the dead" | `panopticon.open.eliminated_agency` and `panopticon.open.ttk` are both open, and `panopticon.open.shooter_win_condition` has three live candidates that each imply a different answer. The page must simply not raise the question. |
| **A number of maps** | `panopticon.maps.plan` targets ~10 but has a documented floor of 3. Never print a number you might have to cut. |
| **Progression, unlocks, cosmetics, ranked, leaderboards, seasons, battle pass** | None exist in canon in any form. |
| **Bots, offline play, single-player, or "play solo"** | `panopticon.testing.bots` says whether bots ship as a playable mode is undecided. This is the highest-risk item on the list because it is exactly what a buyer with no friends will look for. |
| **Mods, workshop, custom maps, map editor** | Never discussed. |
| **Mac or Linux/Steam Deck support** | Mac is conditional and untested; Steam Deck has never been considered. Verified Deck status is applied by Valve, not claimed by you. |
| **Dedicated servers, matchmaking, crossplay, region selection** | No netcode architecture decision exists in canon. |
| **Voice chat or proximity chat** | Not in canon, and it is the first feature people assume in this genre. |
| **Traps, hazards, or a guard who "controls the prison"** | `panopticon.guard.role`: "No traps for now." The guard shoots; that is the whole kit. |
| **A role-flip finale, a portal fight, or "turn on your captor"** | `panopticon.idea.role_flip_portal` is logged explicitly as an idea, not canon. |
| **Music during matches, or a soundtrack as a feature** | `panopticon.music`: in-game music is undecided; only menu music is committed. |
| **Any horror framing** — "terrifying", "dread", "you are being hunted", "psychological horror" | `panopticon.tone`: gritty but not tense, Machine Party register, explicitly not horror. This one misrepresents the product to the exact audience most likely to refund it. |
| **Any comedy framing above the Lethal Company line** — "chaotic", "hilarious", "ragdoll mayhem" | Same fact. The comedy ceiling is Lethal Company; it is not Peak or R.E.P.O. |
| **A message, a theme, or Foucault** | `panopticon.not_a_message_game`. The panopticon is flavour that fits the structure. One line of it is charming; two is a manifesto. |
| **"Endless replayability", "hundreds of hours", "never the same twice"** | Unfalsifiable filler that reads as indie boilerplate. `panopticon.depth_over_content` is a design commitment, not a marketing claim, and Steam readers discount it on sight. |
| **A roadmap, "more content coming", or anything with the words Early Access** | `panopticon.launch.not_early_access`, ruled emphatically. The page states a finished game and nothing else. |
| **2v6 or any asymmetric-sides variant** | Canon supports it (`panopticon.player_counts`) but no mode has been designed around it. State the range 1v1 to 1v7 and stop. |

---

## 7. OPEN QUESTIONS FOR RYAN

These are the places where the copy needed something canon does not answer. Each has a working assumption already baked into the draft above so nothing is blocked.

1. **Price.** Draft says `[PLACEHOLDER — $9.99]`. Research recommends $9.99 with a 20% launch discount, and rules out $12.99 as dominated. Your instinct was $12. What goes in the field?

2. **When does the Coming Soon page go live?** This is the highest-leverage scheduling decision on the page, because wishlist *velocity* is what Steam reads, and `panopticon.content.strategy` says audience-building does not wait on the page. Going up in early 2027 with a finished page collects fewer wishlists than going up mid-2026 with a placeholder capsule. Which do you want?

3. **April 1st.** The ship date is April Fools' Day. Content Warning launched 2024-04-01 and it did not hurt them, but a store page that appears with an eye on it and a launch date of April 1 will be read as a bit by some fraction of visitors. Keep the date, or move it a few days?

4. **Subtitle or not.** `PANOPTICON` alone is a dictionary word competing with unrelated Steam search results. A subtitle fixes it. If you want one, the draft has no opinion — but it should be added before the page goes live rather than after, because renaming a live page loses the URL slug.

5. **How much of the concept survives into the copy.** §3 includes one optional line of panopticon flavour and nothing more. Do you want that line in, out, or replaced with something in your own voice?

6. **Does the tower's escalation get stated on the page?** The draft says "the tower gets stronger every consecutive turn a player holds it" and describes the shortening reload. That is `panopticon.shooter.reload`, which is ratified, but the fact calls the reload form the "MVP" version and floats material changes later. Confirm the shortening reload is what ships, or the line comes out.

7. **British or American spelling.** The draft uses "centre" because canon does. The Steam audience is US-majority. Trivial, but pick one and it applies everywhere including the trailer end card.

8. **Who is the developer/publisher name on the page?** `panopticon.identity.accounts` says this is personal work under **neotechnites** and must never touch Stack Integrated. The Steamworks account, the bank details and the printed developer name all need to be the personal identity. Worth confirming before anything is registered, because it is not fixable later without Valve support.
