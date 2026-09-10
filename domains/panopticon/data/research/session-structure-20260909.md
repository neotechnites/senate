# PANOPTICON — Round Length & Match Structure
**Research brief · 2026-09-09 · question: what round length and overall match/session structure makes this game fun and retentive?**

Author decides. This brief presents options with tradeoffs and the evidence behind them. Every sourced claim carries its URL inline. Estimates are marked **ESTIMATE**; my own reasoning is marked **INFERENCE**; things I could not source are marked **NO SOURCE FOUND** rather than guessed.

---

## RECOMMENDATION

### The mechanism, in one line

Stick Fight has exactly **one** arc length and repeats it forever. PEAK has **three nested** arc lengths. That is the difference, and it is the thing to design.

Keith Burgun names it precisely: bad games "have some short gameplay loop that just 'shuts off' at some point, usually because a timer, health bar, or victory points total filled up or emptied out," and repetition at a single scale causes fatigue because "your brain is aware of it. It is apparent to your subconscious that you are doing the same thing over and over and over again." The fix is **nested arcs of varying lengths**, so that "all of those little purple tactical arcs mean something slightly different, because they are now taking place in a different spot on the yellow arc." — <http://keithburgun.net/arcs-in-strategy-games/>

So: PANOPTICON needs at least three arcs, each roughly 4–6× the one below it, and the top one must be able to be **lost**.

**And nesting alone is not sufficient — the arcs have to carry something.** Jesse Schell: **"Resources in a game are worth more if there is a chance they can be taken away."** — <https://www.inventoridigiochi.it/wp-content/uploads/2020/07/art-of-game-design.pdf> The measurable version, from review mining (§2): **0 of 1,298 Stick Fight negative reviews mention losing progress; 13 of 1,372 PEAK negative reviews do.** Nobody rages about losing a Stick Fight round because a Stick Fight round contains nothing that can be lost.

So each of the three arcs needs a **spine** (a fixed order that gives the run acts), a **ratchet** (something banked at each boundary that only accumulates or only depletes), and a **clock** (a terminator that ends it). The open design question is what a runner banks by clearing a floor, and what the shooter's tower turn accumulates — if the answer is "nothing", PANOPTICON is Stick Fight with a sniper.

**What you do NOT need, and this is load-bearing: an unlock economy.** PEAK's 64 badges grant **cosmetics only**, and its 10 Ascent tiers unlock nothing but permission to make the game harder. All of PEAK's investment lives inside a single run. — <https://peak.wiki.gg/wiki/Badges>, <https://peak.wiki.gg/wiki/Ascent>

**One structural warning up front.** Versus party games churn harder than co-op for a mechanical reason: co-op needs a near-zero atomic network (*"For It Takes Two, you just need a buddy. That's it"*) while versus needs enough players with good ping in your timezone to fill lobbies fast — <https://newsletter.gamediscover.co/p/analysis-multiplayer-game-discovery>. Stick Fight's own reviews record the death spiral: *"there are almost no players anymore! Most lobbies are empty... it's completely pointless and boring."* **PANOPTICON being optimized for 1v1–1v3 is a genuine structural advantage. A structure that only works at 8 players inherits Fall Guys' failure mode, whose latest-month peak is 0.48% of its all-time peak.**

### Concrete numbers

| Arc | Name | Target length | Precedent |
|---|---|---|---|
| 1 | **Floor / segment** | **25–40 s**, target 30 s | Move or Die rounds are 20 s (official); Pac-Man's chase phase is 20 s against a 5–7 s scatter window |
| 2 | **Run (one round)** | **3:00–3:30**, hard cap 4:00 | Halo 3 "Team Duck Hunt" shipped at literally *"3 Minutes of fun per round; 5 rounds"* |
| 3 | **Tower turn** | 1 run, or a block of 2 | VSH queue, Halo Juggernaut |
| 4 | **Match** | **12–16 min at 1v3; 16–24 min at 1v7** | Halo 3 Duck Hunt total = 15 min; Fall Guys pre-nerf = 15–20 min, post-nerf ≈ 6–9 min |

**Floors: 5 per run**, matching both the Halo Reach ancestor (a "five level" gametype) and the 3-min round budget at ~30 s/floor plus transitions.

### The reasoning chain

1. **The ancestor already answered the round-length question.** Halo 3 "Team Duck Hunt," documented by its own creator, ran **3 minutes per round, 5 rounds**, recommended 12–16 players, ducks one-shot, sniper with damage resistance and infinite ammo, respawn 5 s with respawn-time growth on. — <https://archive.forgehub.com/threads/team-duck-hunt.104927/> The Halo Reach version was *"a five level Duck Hunt map built on Forge World, with each level designed to be progressively more difficult for the ducks. Cover decreases and traps are added as the level continues,"* recommended 8–16 players. — <https://halocustoms.com/maps/duck-hunt.2330/> (Cloudflare-blocked to direct fetch; text recovered consistently via search index and the Wayback copy). A 3-minute round and 5 floors is not a guess — it is the thing that was already fun.

2. **The match must be short enough that people actually win.** Fall Guys explicitly shortened its show and said why: *"Winning a game of Fall Guys is an amazing moment. At the same time, we want wins to feel achievable for all players. By lowering the length of Knockout shows, we hope to push this balance in a more healthy direction. This also has the added benefit of making our games even snappier, letting you play more games in less time!"* — <https://www.fallguys.com/news/fall-forever-update> The change: from ~5 rounds / 60 players down to *"3 rounds and 32 players."*

   **INFERENCE / derived arithmetic (mine, not a source's):** in a single-winner match with N players, expected play time between your own wins ≈ N × match length. At 8 players and a 25-minute match that is ~3.3 hours between wins. At 4 players and a 14-minute match it is ~56 minutes. The single-winner rule the author wants is *exactly* the rule that makes match length expensive, so the match must be short to compensate. The board-game literature puts a floor on this: **"The player only needs a 5% chance of winning, for the game to remain enjoyable"** — <https://daniel.games/catch-up-mechanics/>

3. **Being the shooter is the win condition, so the seat must be capped and consumable, not just won.** See Option tables below. The mechanic the author is proposing — win a deathmatch, earn the tower — is **not shipped anywhere I could verify** (closest: Halo's "Nauticide" variant, *"The player with the most kills becomes the Juggernaut"* — <https://www.halopedia.org/Juggernaut>, with no anti-camp rule documented). That is the opportunity and the risk.

4. **Floors are already the ancestor's structure, but for a different reason than the author's.** Reach's five levels escalated difficulty (cover decreases, traps increase). The author's argument is attention localization and comeback windows. Those two goals pull in opposite directions — see §5.

### Three structures to choose between

The author's spec — **one winner, the shooter seat is earned not rotated, everyone gets the chance at it, first to win as shooter takes the match** — is satisfiable three ways. All three respect the spec; they differ in where the arc comes from.

---

#### OPTION A — "Ancestor+": open deathmatch, then hold the tower until someone clears the ring

- **Opening deathmatch:** 60–90 s free-for-all on the ring floor. Winner takes the tower.
- **Round:** one run, 5 floors, ~3 min. All other players are runners.
- **Win condition:** the shooter wins the *match* by eliminating **every** runner before the last floor. Anything less and the seat passes.
- **Seat passes to:** the runner who got furthest / survived (a mini-deathmatch is not re-run — surviving *is* the deathmatch).
- **Anti-camp:** a shooter who fails but got close keeps nothing — the claim is consumed by using it (transplanted from VSH's *"When someone becomes the boss, their queue points will be set to 0"* — <https://forums.alliedmods.net/archive/index.php/t-182108.html>).
- **Length:** 1v3 → ~4–6 rounds → **14–20 min**. 1v7 → ~6–9 rounds → **20–30 min**.

| Pro | Con |
|---|---|
| Closest to the source material and to the author's stated instinct | Length is unbounded in the worst case; needs a terminator (see "Forcing an ending") |
| Seat is unambiguously a prize; holding it is the win | At 1v7 a strong shooter may take it round 1 and end the match in 5 min — anticlimax |
| Zero extra systems | "Everyone gets a chance" is only probabilistically true |

---

#### OPTION B — "Everyone gets one turn": fixed tower rotation, best turn wins

- **Opening deathmatch:** 60–90 s. Determines **tower order** (and, at 5–8 players, *who makes the cut* — only the top 4 get a tower turn; that is how "not everyone has to be the shooter, but everyone has the chance" is honored literally).
- **Round:** each qualifying player gets exactly **one** 3-minute tower turn.
- **Win condition:** the player whose tower turn scored highest (runners eliminated, weighted by how early) wins the match. Ties broken by runner performance.
- **Length:** deterministic. 4 tower turns × 3 min + 90 s deathmatch + transitions ≈ **14–15 min** regardless of lobby size.

| Pro | Con |
|---|---|
| Fixed match length at every player count — the single biggest retention lever | Score-based, not "first to win as shooter" — a softer reading of the spec |
| Camping is structurally impossible | Later tower turns have information advantage (they've watched the others) — needs handling |
| The deathmatch has real teeth: it decides who even gets a shot | Feels more like a tournament than a brawl; less "one more round" energy |
| Everyone knows exactly when their turn is coming — anticipation is an arc | The match can be decided before the last turn |

---

#### OPTION C — "Move or Die shape": points every round, first to N

- Everyone scores every round, including last place (Move or Die: **1st = 5, 2nd = 2, 3rd = 2, last = 1; first to 50 points** — <https://www.gamegrin.com/reviews/move-or-die-review/>). Shooter scores more per round than any runner can.
- Tower seat goes to the current **points leader**, or to whoever wins the previous round.
- **Length:** ~10–15 rounds → **30–45 min** at 3 min/round. Too long for the target unless rounds drop to ~90 s.

| Pro | Con |
|---|---|
| Nobody sits out, nobody is ever eliminated from the session | Directly conflicts with "there should only ever be one winner" — points feel like a scoreboard, not a victory |
| Proven shape: Move or Die matches are *"between five and ten minutes"* at 20 s rounds — <https://hardcoregamer.com/reviews/review-move-or-die/193393/> | Requires ~90 s rounds to fit, which fights the 5-floor structure |
| Leader-seat rule gives a natural, legible escalation | The strongest player takes the seat and holds it — the camping failure, unmitigated |

---

### Forcing an ending (required in all three options)

A single-winner match built from repeatable rounds has no natural terminator. Every comparable game ships one:

- **PEAK's fog.** It rises once all players pass a height threshold **or after "16 minutes and 40 seconds (1000 seconds)"**, whichever is first, closing as *"a shrinking sphere at a linear rate"* and dealing *"2.5 Cold every ~2.4 seconds."* — <https://peak.wiki.gg/wiki/Fog>
- **TTT's Haste Mode, on by default.** `ttt_haste = 1`, `ttt_haste_starting_minutes = 5`, `ttt_haste_minutes_per_death = 0.5` — the round starts short and *buys* time with each death, so a boring round ends fast and an eventful one extends. Session caps: `ttt_round_limit = 6`, `ttt_time_limit_minutes = 75`. Verified against Facepunch's own `init.lua`. — <https://raw.githubusercontent.com/Facepunch/garrysmod/master/garrysmod/gamemodes/terrortown/gamemode/init.lua> and <https://www.troubleinterroristtown.com/config/settings/>
- **SpeedRunners' shrinking screen.** The camera follows the leader; falling off-screen eliminates you, and *"after the first elimination, the boundaries of the screen increasingly enclose the in-game reaction."* If nobody dies for a set time the screen shrinks anyway. — <https://squareblind.wordpress.com/2020/05/25/speedrunners-the-videogame-embracing-everyday-instinct-in-a-superhuman-footrace/>, <https://en.wikipedia.org/wiki/SpeedRunners>
- **Halo Dreadnaut.** *"20 kills as Juggernaut wins the game"* — the reign is capped by converting it into a match win. — <https://www.halopedia.org/Juggernaut>

**Recommended terminator (INFERENCE):** TTT's haste model is the best fit — the round clock is short by default and extends only when the shooter is converting. It solves pacing and dead-player downtime with one number, and it punishes a shooter who stalls.

### Anti-camp package (required if the seat is earned — Options A and C)

The arcade format, which invented the earned seat, **never solved camping mechanically.** Its own etiquette page patches it socially: *"If you're an expert and dominating the competition, give others a chance to challenge one another after you win a few games."* — <https://rockymountevents.com/the-top-5-etiquette-rules-to-follow-at-an-arcade/> That norm will not survive online strangers.

The quantified failure: fairness measured as the max ratio of games played between any two players reaches **9 with 10 players** under pure winner-stays; a "5 players, winner stays 3 games" rule still yields *"a little over 1.5"* over 30 games across 1000 simulated trials. — <https://www.oflatt.com/winner-stays.html>

Mitigations that actually ship, most-to-least mechanical:

1. **Reset on serve.** VSH/FF2: *"You earn 10 queue points per round you play… The player with the most queue points at the end of a round will become the next boss. When someone becomes the boss, their queue points will be set to 0."* — <https://forums.alliedmods.net/archive/index.php/t-182108.html>, <https://wiki.teamfortress.com/wiki/VS_Saxton_Hale_Mode_(custom_game_mode)>
2. **Cap the reign with a win condition** (Dreadnaut, above).
3. **Handicap the incumbent.** Halo Infection's Last Man Standing gets *a waypoint broadcasting their position to the zombies* — the game actively punishes whoever is winning at surviving. — <https://www.halopedia.org/Infection>
4. **Random for the first N rounds, then queue.** Valve's official 2023 VSH chose *pure* random: *"When a round starts, one player is chosen at random to play as Saxton Hale."* — <https://wiki.teamfortress.com/wiki/Versus_Saxton_Hale>
5. **Difficulty escalation on repeat.** A shooter on their second or third consecutive turn should be *more visible*, not more powerful.

**Note the signal:** the entire VSH lineage — the closest shipped analogue to an "earned boss seat" — chose a **seniority** queue or randomness, never a skill contest. Nobody awards the boss seat for winning. **INFERENCE:** the transplantable piece for PANOPTICON is not the queue, it is the **reset** — a champion's claim should be consumed by using it.

---

## EVIDENCE

### 1. Round and match lengths in comparable games

| Game | Round | Match / session | Source & tier |
|---|---|---|---|
| **Halo 3 "Team Duck Hunt"** | *"3 Minutes of fun per round"* | *"5 rounds"* = 15 min; 12–16 players recommended | **Creator's own post** — <https://archive.forgehub.com/threads/team-duck-hunt.104927/> |
| **Halo Reach "Duck Hunt 2.0"** | NO SOURCE FOUND | 5 levels; min 8 / max 16 players; Forge World; Infection-based | HaloCustoms (403 to fetch; via search index + Wayback) — <https://halocustoms.com/maps/duck-hunt.2330/> |
| **Halo Infinite "Duck Hunt"** | NO SOURCE FOUND | Official 343 Action Sack mode since 2025-01-21; ring arena, sniper in centre, *"get from point A to point B without losing your hat to the sniper in the middle of the ring"* | **Official** — <https://www.halowaypoint.com/news/action-sack> |
| **Fall Guys (classic)** | *"approximately 1 to 5 minutes max"*; ~2–3 min typical | *"Every match contains 5 rounds"*; *"about 15 to 20 minutes, 59 contestants will fall and one player will come out victorious"* | Press — <https://screenrant.com/fall-guys-rounds-each-game-match-mediatonic/>, <https://www.gamepressure.com/fall-guys-ultimate-knockout/game-length/z1d7b4> |
| **Fall Guys (post Fall Forever)** | same | *"Knockout games will now consist of 3 rounds and 32 players"* | **Official** — <https://www.fallguys.com/news/fall-forever-update> |
| **Fall Guys (individual timers)** | Fall Ball *"down to 120 seconds from 150"*; Team Tail Tag & Royal Fumble to 1:30 from 2:00; Hex-A-Gone 5-min cap | Creative mode allows 1–30 min round limits | **Official** — <https://twitter.com/fallguysgame/status/1305861272358064128>, <https://www.pcgamer.com/fall-guys-patch-notes/> |
| **Stick Fight** | *"Matches can end in about five seconds"*; *"each round lasts between five to 30 seconds"* (explicitly an estimate by the reviewer) | **No built-in first-to-N at all** — the game runs continuously with a win counter; a feature request for round/kill limits was declined | Press — <https://www.heypoorplayer.com/2021/04/09/stick-fight-the-game-review-switch/>, <https://dailycampus.com/2024/01/23/the-backlog-stick-it-to-them-in-stick-fight-the-game/>; forum — <https://steamcommunity.com/app/674940/discussions/0/1840188800805409705> |
| **PEAK** | Per biome: *"Each section should take you approximately 20 to 30 minutes to climb"*; fog forces the issue at **1000 s (16:40)** per segment | *"the average player takes about five hours to reach the summit"*; experienced *"closer to two hours, or even under one"*; WR **22:27.267** | Press — <https://www.thegamer.com/peak-how-long-to-beat-guide/>; wiki — <https://peak.wiki.gg/wiki/Fog>; primary — <https://www.speedrun.com/PEAK/runs/y4nx5n2m> |
| **Lethal Company** | ~11 min per day (3 posters agree; **forum anecdote only**) | 3 days to quota (~33 min); quota rises every 4 days; missing it wipes the save | Wiki (code-derived) — <https://lethal.miraheze.org/wiki/Quota>; forum — <https://steamcommunity.com/app/1966720/discussions/0/4032474464290919755/> |
| **Dead by Daylight** | Generator = **90 charges @ 1/s = 90 s solo**; 5 of 7 needed. Survivors spend *"an average of one minute being chased throughout the match"* (BHVR, July 2024) | **Average match length: NO SOURCE FOUND** — BHVR has never published one. Hard caps: trial limit 60 min (halved from 120), Endgame Collapse +5 min | **Official wiki** — <https://deadbydaylight.wiki.gg/wiki/Generators>, <https://deadbydaylight.wiki.gg/wiki/Trials>; **Official BHVR stats** — <https://forums.bhvr.com/dead-by-daylight/discussion/420795/new-stats-july-2024> |
| **Trouble in Terrorist Town** | `ttt_roundtime_minutes = 10`, but `ttt_haste = 1` by default so real rounds **start at 5 min and grow +30 s per death**. `ttt_preptime_seconds = 30`, `ttt_posttime_seconds = 30`, `ttt_firstpreptime = 60` | `ttt_round_limit = 6`, `ttt_time_limit_minutes = 75` | **Verified against source code** — <https://raw.githubusercontent.com/Facepunch/garrysmod/master/garrysmod/gamemodes/terrortown/gamemode/init.lua>; docs — <https://www.troubleinterroristtown.com/config/settings/> |
| **Hunt: Showdown** | Boss banishing *"takes a little over 3min"* | **45 min hard cap** (reduced from 60 in update 1.9); drops to 5 min remaining when the last bounty extracts. **Average: NO SOURCE FOUND** | Wiki — <https://huntshowdown.wiki.gg/wiki/Game_Modes/Bounty_Hunt> |
| **Ultimate Chicken Horse** | *"Each round is estimated to last a minute"* | **MaxScore 250, Goal = 50** → effectively 5 goal points to win. *"At 5 points to win a game can take anywhere from 3-6 minutes"*; dev notes that before the round limit existed *"games would drag on to 40 minutes or more"* | Ruleset XML via guide — <https://gamepretty.com/ultimate-chicken-horse-how-to-edit-your-ruleset-files/>; wiki — <https://en.wikipedia.org/wiki/Ultimate_Chicken_Horse>; forum+dev — <https://steamcommunity.com/app/386940/discussions/0/217691032449111377> |
| **Move or Die** | **20 s** — *"the rules change every 20 seconds"* | **First to 50 points** (5/2/2/1). *"entire games are between five and ten minutes"*. Mutators every 6 rounds, and the same player *cannot* be picked twice in a row | **Official** — <https://store.steampowered.com/app/323850/Move_or_Die/>, <https://moveordiegame.com/>, <https://www.moveordiegame.com/updates/mutators/>; press — <https://hardcoregamer.com/reviews/review-move-or-die/193393/>, <https://www.gamegrin.com/reviews/move-or-die-review/> |
| **SpeedRunners** | **NO SOURCE FOUND** for round length | *"A player must win 3 rounds to win the match altogether"* (teams need 4). Screen shrinks after first elimination | Wiki — <https://en.wikipedia.org/wiki/SpeedRunners> |
| **Crab Game** | Bomb Tag 30 s cycles; Stepping Stones 2-min cap; Lights Out ~7 s to hide. Most per-mode timers: **NO SOURCE FOUND** | Elimination funnel to one winner; 35 players, 28 maps, 9 modes. Lobby constants: freeze phase min 5 s, round-over 3 s, game-over 3 s | **Official Steam** — <https://store.steampowered.com/app/1782210/Crab_Game/>; mod source — <https://github.com/lammas321/CrabGameLobbyPlus> |
| **DEVOUR** | Per-map run length: **NO SOURCE FOUND** | *"a single session lasting up to an hour"*; 1–4 players; destroy 10 totems | **Official Steam** — <https://store.steampowered.com/app/1274570/DEVOUR/> |
| **Among Us** | Discussion **15 s**, Voting **120 s**, Kill cooldown **45 s**, Emergency cooldown 15 s, 1 emergency meeting/player | *"around 15 minutes on average"* — **low-tier blog, no methodology** | Reverse-engineered protocol spec (community technical doc, not Innersloth) — <https://github.com/roobscoob/among-us-protocol/blob/master/07_miscellaneous/01_the_structure_of_the_gameoptionsdata_object.md>; length — <https://theglobalgaming.com/gaming/average-match-time-length-among-us> |
| **Golf With Your Friends** | Per-hole time limit default: **NO SOURCE FOUND** (the widely repeated "2 min / 12 strokes" is unverified; the wiki hosting it is Cloudflare-blocked) | 18 holes Classic, 9 in Couch Mode; up to 12 players; a configurable out-of-time penalty exists and Team17 confirmed the behavior in-thread | Steam — <https://store.steampowered.com/app/431240/Golf_With_Your_Friends/>; forum+publisher — <https://steamcommunity.com/app/431240/discussions/2/2913220877909847076> |
| **Deceit** | Night/blackout *"180/180/90 seconds per floor, respectively"*; 6/6/3 fuse boxes per floor; a fuse adds 30 s; downed players wait 10 s to respawn (+5 s per elimination vote) | Three zones, escape via hatch; a third of players infected. **Total match length: NO SOURCE FOUND** | **Official dev patch post** — <https://store.steampowered.com/news/app/466240/view/5320438099036147981>; Steam — <https://store.steampowered.com/app/466240/Deceit/> |
| **Rocket League** (comparator) | — | *"Matches are usually five minutes long"* | <https://en.wikipedia.org/wiki/Rocket_League> |
| **Clash Royale** (comparator) | — | *"Battles last up to three minutes in normal time, with elixir generation doubling during the final minute"* | <https://en.wikipedia.org/wiki/Clash_Royale> |

**Retention-vs-session-length data: mostly NO SOURCE FOUND.** The session's search budget ran out before this could be worked properly. What surfaced, all third-party and none of it game-genre-specific: a "Goldilocks" 20–40 min session recommendation for Quest content (<https://developers.meta.com/horizon/blog/optimize-user-time-goldilocks-session-length-meta-quest/>), and a claim that mean first-session time across games is 9 minutes with longer first sessions averaging 31% D1 retention vs 20% for shorter (<https://www.gamedeveloper.com/business/how-first-session-length-impacts-game-performance>). **Neither is evidence about round length in a PvP party game.** No GDC talk naming a target match length was found.

---

### 2. Why Stick Fight reads as shallow and PEAK reads as a satisfying long investment

**The named mechanism: irreversible, legible, shared accumulation inside a bounded run — and the round is the unit that either carries it or destroys it.**

Jesse Schell states the principle directly, in *The Art of Game Design* (p. 192): **"Punishment creates endogenous value. We've talked about the importance of creating value within a game. Resources in a game are worth more if there is a chance they can be taken away."** And, from his own playtest data on Toontown Online: *"This combination of light punishments is just enough to make players use caution in battles. **We tried lighter versions, and it made battles boring — there was no risk in them.**"* — <https://www.inventoridigiochi.it/wp-content/uploads/2020/07/art-of-game-design.pdf>

His Lens #33 (Triangularity, p. 182) is the diagnostic: *"I find that about eight out of ten times someone comes to me asking for help on a game prototype that 'just isn't fun,' the game is missing this kind of meaningful choice"* — the choice between a safe small reward and a risky big one.

#### The cleanest single piece of evidence: a null result

Steam review corpora pulled via the `appreviews` API on 2026-09-09 (English; helpfulness × recent × updated filters; Stick Fight n=2,562, PEAK n=3,735):

> **0 of 1,298 Stick Fight negative reviews mention losing progress. 13 of 1,372 PEAK negative reviews do — and the angriest PEAK reviews in the corpus are about it.**

Nobody rages about losing a Stick Fight round because a Stick Fight round contains nothing that can be lost. **The rage is the investment.**

#### The playtime distribution — the retention tell

| lifetime hrs at review | Stick Fight | PEAK |
|---|---|---|
| <1h | 10.9% | 2.7% |
| 1–5h | 24.3% | 11.1% |
| 5–20h | 43.6% | 33.9% |
| 20–50h | 13.0% | **29.0%** |
| 50–100h | 4.6% | **16.1%** |
| >100h | 3.6% | 7.2% |

**Median lifetime playtime among reviewers: Stick Fight 7.5 h, PEAK 35.3 h.** 67% of Stick Fight reviewers had under 10 hours; only 35% of PEAK reviewers did. Neither game is badly reviewed — Stick Fight sits at **93.6% positive (93,506/99,915)**, PEAK at **94.6% (282,961/299,039)**. **Shallowness is not a quality complaint.**

#### The achievement design tells you what unit each game recognises

Stick Fight's 28 achievements, top by global completion — <https://steamcommunity.com/stats/674940/achievements/>:

| % | name |
|---|---|
| 80.6 | Walkover — win a round by every opponent falling off the map |
| 78.7 | Your kung fu is strong — kill an opponent with a mid-air kick |
| 73.4 | Killing Spree — kill 4 in a row without dying |
| 67.3 | Double Kill |
| 48.5 | Ace — kill 3 other players in one round |

**Every one is a within-round combat verb or a lifetime kill tally. There is no achievement in Stick Fight that describes an arc. The longest structure the game recognises is a kill streak.**

PEAK's badges map the attrition funnel of a single climb — <https://steamcommunity.com/stats/3527290/achievements/>:

| % of all owners | badge |
|---|---|
| 73.8 | Beachcomber — climb past the SHORE |
| 59.5 | Trailblazer — climb past the TROPICS |
| 44.1 | Volcanology — climb past the CALDERA |
| 42.0 | Alpinist — climb past the ALPINE |
| **31.5** | **Peak Badge — reach the PEAK** |
| 17.3 | Survivalist — escape without ever losing consciousness |

**Two out of three people who bought PEAK have never reached the summit.** Stick Fight's most common achievement is cleared by 80.6% of owners. PEAK's payoff is genuinely scarce; Stick Fight's are handed out in the first session.

#### Stick Fight's structural problem, in its own players' words

The two most mechanically precise reviews in the corpus are a hostile one and a friendly one saying the same thing:

> **"boring, not what i expected. there is no score and this game play endlessly"** — negative, 1.4 h

> **"go-to party game when not taken seriously. no objective, no rules, just fight. pretty fun"** — *positive*, 10.1 h

Both independently identify the fact that there is **no terminal state and no score**. This is confirmed structurally: Stick Fight has no built-in first-to-N at all, and a Steam feature request to add round or kill limits was resisted. — <https://steamcommunity.com/app/674940/discussions/0/1840188800805409705>

> "Ragdoll stickmen blasting with random weapons while the entire level collapses around you never gets old... **for about 2 hours.** It's hilarious with 3/4 buddies on voice, but solo it's pretty shallow and the maps get repetitive fast." — positive, 11.1 h, 9 helpful votes

> "this game is really funny but **theres no replay value aside from forcing another one of your friends to buy it**" — positive, 5.6 h

Press says the same: *"Once every person is killed, the stick figures are picked up and placed onto the next stage to start all over again with little room for a break"*; *"Since there is only one mode for the game, over time the gameplay can eventually feel flat making this a one trick pony."* — <http://www.nintendoworldreport.com/review/56733/stick-fight-the-game-switch-review> And *"Matches can end in about five seconds"*; *"The game's one hundred levels are varied, but it doesn't take long to revisit them."* — <https://www.heypoorplayer.com/2021/04/09/stick-fight-the-game-review-switch/> Even its highest-scoring review (9/10, Nintendo Blast) flags *"little incentive for a continuous sequence of matches."* — <https://opencritic.com/game/11169/stick-fight-the-game/reviews>

**Honest counter-finding, do not skip it:** RNG/luck complaints are a *minority* theme in Stick Fight's negatives (**0.6%**), and "repetitive/boring" is actually **more** common in PEAK's negatives (7.4%) than Stick Fight's (5.3%). Stick Fight's negative reviews are overwhelmingly about **bugs, hackers and abandonment (20.8%)**. The shallowness read is real, but it lives in the *positive* reviews ("great for 2 hours") and in the playtime distribution — not in complaint volume. PEAK escaped the *disengagement*, not the complaint.

#### What PEAK accumulates, and the reviews that prove it hurts to lose

All of the following are **negative** reviews. That is the point.

> "we were carrying bing bong the entire way up from the shore we first met him all the way up to the very peak. he became our best friend. we loved him. right before rescuing our dear friend, everyone got disconnected... **we have wasted 2 hours of our lives for NOTHING.**" — negative, 21 h

> "Had a **1.5 hour long run** with friends, barely surviving through the roots and mesa, **resorting to cannibalism at one point**... **A very intense and memorable run completely ruined**" — negative, 37.7 h

> "**One wrong move and you've lost all your progress**" — negative, 27.9 h

> "**1 simple mistake will cause your run to be over.** ... **Losing stamina after failing a climb due to lack of stamina** is a baffling design decision." — negative, 2.7 h

That last is a hostile reviewer accurately describing the **death spiral**: failure permanently shrinks the resource that prevents failure. That is irreversibility made mechanical.

The mechanical substrate, verified:

- **One stamina bar absorbs everything.** *"You have just the one bar, and then things take chunks out of it: how much stuff is in your backpack, being hungry, getting injured."* — <https://aftermath.site/peak-climbing-impressions-review/> Game Informer: the bar *"grows and shrinks based on consumables, fall damage, and status effects"*, and *"items like the energy drink or lollipop significantly improve climbing abilities, but the sugar crash afterwards could force you to fall asleep and slide off the cliff."* — <https://gameinformer.com/review/peak/a-brilliant-co-op-climbing-adventure>
- **The biome ORDER is fixed while the terrain rotates.** *"While the game engine generates a new mountain daily, the order of its environments remains the same: ascend from the rocky Shore, avoid poisonous fauna in the Tropics, then survive the frozen winds of the Alpine, and dodge the fire storms of the Caldera."* — Game Informer, same URL. **A PEAK run has an act structure with stable dramatic beats and variable content.**
- **Campfires bank altitude and gate the next biome** (all players within 19.2 m; autosaves; *"prevents any hunger or the fog from rising until a Scout leaves the Campfire area"*). — <https://peak.wiki.gg/wiki/Campfire>
- **The fog is the clock.** Rises after *"16 minutes and 40 seconds (1000 seconds)"* or once all Scouts pass a height threshold, closing as *"a shrinking sphere at a linear rate"*, dealing *"2.5 Cold every ~2.4 seconds."* — <https://peak.wiki.gg/wiki/Fog>
- **Cooperation is enforced, not encouraged.** Nick Kaman (Aggro Crab), GDC 2026, "Putting the 'Friend' in Friendslop": **"That's why you can't get items out of your backpack on your own. You need a friend to do it."** And: *"The feeling you get when you get to the peak, and you only did it because your friends helped you along the way, is a pretty beautiful feeling."* — <https://www.gamedeveloper.com/business/peak-co-developer-aggro-crab-shares-lessons-in-friendslop>
- **Death does not eject you socially.** Kaman: **"The ghost actually gets to keep interacting with people. You can talk to your friends and you have this bird's eye view."** Same URL. **INFERENCE, and the most transferable single idea in this brief:** in most permadeath co-op the session dies socially before it dies mechanically. PEAK demotes a dead player into a spotter with a camera advantage, so a 4-player run keeps 4 voices to the end.

#### Meta-progression: the factual answer, and it is the opposite of what you'd guess

**PEAK has NO power-based meta-progression. Zero stat carryover. Zero permanent unlocks that make you stronger.** Its 64 badges grant **cosmetics only** — *"Every badge has an associated reward cosmetic item"*, and the Ascendant Medal for all 64 *"offers no gameplay functionality."* — <https://peak.wiki.gg/wiki/Badges> The 10 tiers (Tenderfoot, Peak, Ascents 1–8) unlock **permission to make the game harder**, never easier: A1 fall damage ×2, A2 hunger +60%, A3 all items +2.5 weight, A4 no Flares at the Peak, A5 ~100 cold damage at night, A6 climbing costs +40% stamina, A7 spawn with 10 Curse, A8 requires all Amulets + Nadir. — <https://peak.wiki.gg/wiki/Ascent>

**So the investment is 100% within a single run.** This is the opposite of the Hades / Rogue Legacy model, and it is the correct read: **you do not need a persistent unlock economy to get PEAK's effect.** Stick Fight, meanwhile, is the null case on both axes — 28 achievements that grant nothing, no score, no rank, no leaderboard, and a total state reset between rounds.

#### The theory, with the caution attached

- **Berlin Interpretation (IRDC 2008), on permadeath:** *"You are not expected to win the game with your first character. You start over from the first level when you die. **The random environment makes this enjoyable rather than punishing.**"* — <https://www.roguebasin.com/index.php/Berlin_Interpretation> **Permadeath is only tolerable when paired with randomization.** PEAK's daily map regeneration is the precondition, not decoration. Stick Fight has randomization *without* accumulation — the useless half of the pair.
- **Michael Toy, co-creator of Rogue:** *"We were trying to make it more immersive by making things matter, but not to make it more painful."* — <https://www.gamedeveloper.com/design/-i-rogue-i-co-creator-permadeath-was-never-supposed-to-be-about-pain-> Permadeath was added *after* saves existed, because reloading destroyed decision weight.
- **The constraint, from Sid Meier (GDC 2010):** *"When random things happen, paranoia strikes the heart of the gamer. The computer is all of a sudden 'after them.'"* and *"If something bad happens, if there is a setback to the player, they react much differently. They complain the game is broken."* — <https://venturebeat.com/technology/quotes-from-sid-meiers-keynote-gdc-speech> **If accumulated progress is destroyed by a dice roll rather than a decision, investment converts into "the game is broken."** Schell says the same (p. 194): punishment must be for things the player *"is able to understand and prevent."*
- **Raph Koster's two death modes:** *"When we grasp a pattern, we usually get bored with it and iconify it"* / *"When we meet noise, and fail to make a pattern out of it, we get frustrated and quit."* — <https://www.theoryoffun.com/theoryoffun.pdf>
- **Loss aversion is roughly 2:1** (Kahneman & Tversky 1979) — <https://en.wikipedia.org/wiki/Loss_aversion>. Escalation of commitment: Staw (1976), *"Knee deep in the big muddy"* — <https://en.wikipedia.org/wiki/Escalation_of_commitment>. Jamie Madigan on the felt experience: because losses hurt more, a 50/50 bet *"feels more like 30/70 in favor of a terrible outcome."* — <https://www.psychologyofgames.com/2022/06/level-drain-and-loss-aversion-in-dd/>
- **The dissent, included so this isn't a strawman — David Sirlin:** *"This is a false dichotomy. We can allow the player to stop playing without excessive penalty and make a challenging game."* — <https://www.sirlin.net/articles/save-game-systems> PEAK's negative reviews are full of people who agree with him.

#### Linguistic evidence that the arc is real

Among positive reviews over 80 characters:

| | Stick Fight (n=289) | PEAK (n=1,112) |
|---|---|---|
| uses "run / climb / expedition / ascent" | 3.1% | **16.2%** |
| uses "round / match" | **7.3%** | 0.7% |
| uses "we / us / our" | 3.5% | **7.3%** |
| median review length | 36 chars | **71 chars** |

**PEAK players narrate in runs; Stick Fight players narrate in rounds.**

#### The party-game depth problem, with retention numbers

Benchmark: multiplayer titles typically retain only **6% of peak launch CCU** at equilibrium, *"with best-case scenarios reaching merely 10-20%."* — <https://newsletter.gamediscover.co/p/analysis-multiplayer-game-discovery>

Latest-month peak as a share of all-time peak concurrent (steamcharts.com, 2026-09-09):

| Game | All-time peak | Aug 2026 peak | Survival |
|---|---|---|---|
| Fall Guys | 172,026 | 819 | **0.48%** |
| Lethal Company | 239,369 | 5,465 | 2.3% |
| Content Warning | 63,320 | 2,077 | 3.3% |
| Human Fall Flat | 127,516 | 6,446 | 5.1% |
| **Stick Fight** | **5,033** | **606** | **12.0%** |
| Ultimate Chicken Horse | 15,850 | 2,195 | 13.9% |
| R.E.P.O. | 266,908 | 40,259 | 15.1% |
| Golf With Your Friends | 20,592 | 4,086 | 19.8% |
| **PEAK** | **169,910** | **122,714** | **72.2%** |

Sources: <https://steamcharts.com/app/674940>, <https://steamcharts.com/app/3527290> and the corresponding per-app pages. Fall Guys is the canonical cliff — three consecutive ~50% monthly halvings after launch. Overcooked! 2 inverted the curve entirely, hitting its **all-time peak in Dec 2025, 7.5 years after launch.**

**Three findings from this that bear directly on PANOPTICON:**

1. **Versus party games churn harder than co-op for a structural reason: the matchmaking death spiral.** Co-op needs a near-zero atomic network — *"For It Takes Two, you just need a buddy. That's it"* — whereas versus needs enough players with good ping in your timezone to start games quickly. — <https://newsletter.gamediscover.co/p/analysis-multiplayer-game-discovery> Stick Fight's reviews show it happening: *"there are almost no players anymore! Most lobbies are empty, and you simply can't find matches. it's completely pointless and boring"* (21 helpful votes). **PANOPTICON is a versus game optimized for 1v1–1v3. That small atomic network is a genuine structural advantage — protect it. A design that only works at 8 players inherits Fall Guys' failure mode.**
2. **Fall Guys' diagnosed failures were social and structural, not content.** Median retention **13 days** despite 1.5M players in 24 hours; causes named as *"few opportunities to play and hangout with friends"*, punishing elimination, and *"few metagame mechanics that set up long term goals."* — <https://departmentofplay.net/rise-fall-guys-how-to-save-a-hit/> **A 60-player battle royale separates your friend group in round one.**
3. **UGC adds variety, not depth.** Stick Fight ships a level editor and *"over 100,000 community made levels"* (<https://store.steampowered.com/app/674940/Stick_Fight_The_Game/>) and still holds three-digit concurrents. The broad UGC advantage is real — a ~1,200-game study found **"75% better CCU"** at two years and **"115% difference"** at five (<https://newsletter.gamediscover.co/p/analysis-ugc-still-powers-sales-and>, whose authors explicitly caveat that they *"can't answer"* the causation direction) — but **INFERENCE: variety was never Stick Fight's deficiency.**

**The single most actionable finding for PANOPTICON's randomness budget** comes from Clever Endeavour (Ultimate Chicken Horse), explaining why they **removed random power-ups** from their new game's main mode: *"low barrier to entry but also a high skill ceiling"*; **"every time you receive a power-up, it completely reworks your mental model"**; **"players need to feel like every time they play the game, they get significantly better."** — <https://www.cleverendeavourgames.com/blog/2026/7/10/why-did-we-remove-power-ups-from-the-main-game> That is the direct indictment of Stick Fight's random-weapon-spawn model, and the direct warning against making PANOPTICON's shooter loadout or trap placement heavily randomized.

#### The answer, assembled

| | Stick Fight | PEAK |
|---|---|---|
| Atomic unit | ~5 s – 1 min round | 1.5–4 h ascent, 5–6 **ordered** biomes |
| State at unit boundary | **Total reset** | Campfire autosave; permanent altitude; consumed revives; degraded stamina ceiling |
| Death | Instant respawn next round | Ghost: keeps voice + overhead view, cannot climb |
| Resource model | **None** | One stamina bar absorbing hunger, weight, injury, poison, temperature — and it only shrinks |
| Novelty source | 100 levels + 100k UGC levels | 14 baked maps, one per day at 17:00 UTC, **fixed biome order** |
| Social requirement | Optional | Enforced — can't open your own backpack |
| Meta-progression | None | Cosmetics + harder-difficulty unlocks. **Zero power.** |
| Reviewer median lifetime | 7.5 h | 35.3 h |
| Reached the win state | n/a — **no win state** | 31.5% of owners |

**Ranked by strength of evidence, of the candidate mechanisms:**

1. **Sunk investment that can be lost** — strongest. Named by Schell, evidenced by the 0-vs-13 asymmetry.
2. **Persistent within-session state** — strongest, and the *substrate* for #1. Nothing can be lost that was never accumulated.
3. **Irreversibility / resource depletion** — strong. The bar that only shrinks.
4. **Narrative of the run** — strong, and measurable (16.2% vs 3.1% "run" language).
5. **Shared fate** — strong, and *designed* (the backpack rule; the ghost).
6. **Mastery curve** — moderate. 24-hour maps give within-day mastery; 10 tiers give long-arc mastery.
7. **Escalating stakes** — moderate, and *structural* rather than difficulty-based: the biome order is fixed, so altitude rises monotonically while the mistake budget only shrinks.
8. **Randomness dominating skill** — **weak as an explanation for Stick Fight.** Only 0.6% of its negatives mention luck.
9. **Skill expression ceiling** — weak/unsourced for these two games specifically; assembled from theory.

**One sentence:** PEAK gives a session a **spine** (fixed biome order = acts), a **ratchet** (campfires bank altitude while revives and stamina only deplete), and a **clock** (the 24-hour map makes today's mountain a shared object of mastery worth retrying and worth abandoning tomorrow). Stick Fight has a great verb and none of the three.

**INFERENCE — the translation to PANOPTICON:** the shooter's tower turn is the natural spine; whatever the runners bank at each floor is the ratchet; the round terminator is the clock. If a runner's death costs the group nothing and a floor cleared banks nothing, PANOPTICON is Stick Fight with a sniper. **And note what PEAK proves you do *not* need: an unlock economy. All of PEAK's investment lives inside one run.**

---

### 3. Single-winner match structures built from many short rounds

**Fall Guys — the elimination funnel, and the population is the escalation dial.** Levels are authored for a target population band: *"some mini-games being suited for when the match still has close to 60 players, while others are for 15 or less."* — <https://tvtropes.org/pmwiki/pmwiki.php/VideoGame/FallGuys> **INFERENCE:** this is why the funnel produces an arc for free — the *same* rules feel different at 60 and at 6, and each player's win probability rises visibly round over round, so the last round reads as a final rather than as round 5 of 5. The cost: eliminated players sit out. At 1–5 min per round across ~4 remaining rounds, a round-1 elimination means up to ~20 min of spectating.

**Ultimate Chicken Horse — points, with the escalation in the level.** MaxScore 250 with Goal worth 50 (→ 5 goal points), Solo worth 30. Point types include **Comeback** (reach the goal as an Underdog) and **Postmortem** (reach the goal after dying — so dead players still score). **Underdog** = *"you haven't reached the goal for the past 2 (or more) turns while others have."* — <https://cleverendeavourgames.freshdesk.com/support/solutions/articles/32000028991-custom-rules-and-presets>, <https://steamcommunity.com/app/386940/discussions/0/133257959063819864/> Known criticism of the comeback bonus: a player objects that earning its achievement means *"you would have to be bad on purpose."*

**Move or Die — the cleanest "everyone scores every round" model.** 20 s rounds, 5/2/2/1 scoring (last place still scores), first to 50, and escalation supplied by a **stacking mutator layer**: 20 mutators, *"Every 6 rounds, a random player that has mutators selects a mutator from 3 randomly generated to choose,"* with modifiers that *"overlap each following mini game until the next Mutation selection."* Official changelog confirms an explicit fairness guard preventing *"the same player from being selected twice in a row for mutator selection."* — <https://move-or-die.fandom.com/wiki/Mutators>, <https://cogconnected.com/review/move-or-die-review/>, <https://www.moveordiegame.com/updates/mutators/> The arc comes from **accumulating chaos**, not accumulating score.

**Mario Party — randomized bonus stars, and Nintendo shipped an off-switch.** From MP7 the pool grew and selection became random: *"starting with Mario Party 7, games have had six potential Bonus Stars… only three Bonus Stars would ever be awarded, and it was random as to which ones would show up."* Superstars gives two (three at 30+ turns) *and* an explicit revert: *"have only the three classic Bonus Stars…regardless of turn count."* — <https://www.mariowiki.com/Bonus_Star> The commonly stated intent — keep *"results in question down to the very end, so no player is ever truly out of the running"* with the acknowledged cost that *"it's not unusual for one player to dominate a game and not finish in the top spot"* — is **wiki editorial, not a Nintendo statement**. A designer interview stating why bonus stars were added: **NO SOURCE FOUND.** **INFERENCE:** the off-switch is the verdict.

**Catch-up mechanics — the literature, and the sharpest warning.** The anti-rubber-band argument, which applies directly to a shooter seat that trailing players can steal: *"they discourage good decisions and promote a boring style of play… it punishes racing skill; the better one is, the more likely one is to be the target of an unavoidable attack."* Its prescription is not to remove catch-up but to make it **skill-expressive**: reward skilled deployment rather than mere possession, and *"use it to ratchet up the tension and give players new ways to show their skill."* — <https://lawofgamedesign.com/2014/08/25/theory-rubber-bands/>

A useful taxonomy: **Feelbad** (directly punishing the leader — *"anti-meritocratic and feelbad"*), **Ramps** (a final round worth double), **Big Moves**, **Politics**, **Obscuring the leader**, **Early game ending**. Its thesis: catch-up should be *"intrinsically built into your game"*, and the number to design against is **5%** — *"The player only needs a 5% chance of winning, for the game to remain enjoyable."* — <https://daniel.games/catch-up-mechanics/> A second taxonomy warns that heavy-handed direct mechanisms *"may create a bloated pile of band-aids."* — <https://thethoughtfulgamer.com/2017/03/28/catch-up-mechanisms/>

On the blue shell, with real designer statements: director **Hideki Konno** on introducing it in Mario Kart 64 — *"we wanted to create a race where everyone was in it until the end"*; director **Kosuke Yabuki** said Nintendo considered removing it and decided the game would feel incomplete without it. — <https://en.wikipedia.org/wiki/Blue_shell>

Dave Mark's distinction is the most operationally useful: **overt** rubber-banding (visible teleporting) breaks immersion; **covert** versions make catch-up feel organic. His Split/Second case is the interesting one — rubber-banding there exists not for fairness but because *"being in the lead isn't a particularly fun experience when you can't trigger the game's main selling point."* He also notes that **built-in comeback systems (Mario Kart's item distribution) reduce the required rubber-band strength.** — <https://www.gamedeveloper.com/design/rubber-banding-as-a-design-requirement>

**Dead-player downtime — how shipped games solve it:**

| Game | What dead players do | Source |
|---|---|---|
| Among Us | Ghosts *"can talk any time"* (unlike the living), *"complete their remaining tasks to help the living members earn a victory"*; dead Impostors *"can still continue their sabotage"* | <https://among-us.fandom.com/wiki/Ghost> |
| TTT | No respawn until next round, but **prop possession** lets you influence play; dead players hear each other; a formal 30 s posttime phase shows the round report | <https://troubleinterroristtown.wiki.gg/wiki/Game_mechanics>, <https://www.troubleinterroristtown.com/config/settings/> |
| Ultimate Chicken Horse | **Postmortem points** — *"given to players who reach the goal after dying"* | <https://cleverendeavourgames.freshdesk.com/support/solutions/articles/32000028991-custom-rules-and-presets> |
| Move or Die | No elimination problem — last place scores 1 point every 20 s | <https://www.gamegrin.com/reviews/move-or-die-review/> |
| Dead by Daylight | "Play While You Wait" lets a queuing killer play a survivor trial | <https://soren.com/en/news/dead-by-daylight/2026-04-29-killers-can-now-play-as-survivors-while-queuing> |

The stated design principle: *"Having a significant time-gap between a player being logically and strictly eliminated is generally a bad thing."* It distinguishes **logical elimination** (can't win but still playing — the worse state) from **strict elimination**, and names the failure modes that follow: hopeless situations, kingmaking, and griefing. — <https://optimisticlucio.neocities.org/wiki/Player-Elimination>

---

### 4. Earning the antagonist role vs rotating it

**Games where "it" is earned.** Halo Juggernaut is the purest model: one random player starts as Juggernaut, and *"The other players' goal is to kill the current Juggernaut, in order for them to become the next Juggernaut."* Only the Juggernaut scores. Shipped variants map almost exactly onto the author's proposal: **Dreadnaut** (*"20 kills as Juggernaut wins the game"* — the antagonist owns the win condition), **Mad Dash** (*"Juggernaut scores by reaching the destination zones"*), **Nauticide** (*"The player with the most kills becomes the Juggernaut"* — the closest published analogue to "a deathmatch decides who shoots"), **Naut-Tacular** (*"Any players who get a multi-kill become a Juggernaut"*). — <https://www.halopedia.org/Juggernaut>

**TF2 VS Saxton Hale is the best precedent, and it splits both ways.** Community VSH / Freak Fortress 2 uses a **seniority queue**: 10 queue points per round played, highest total becomes the next boss, **reset to 0 on serving**. — <https://forums.alliedmods.net/archive/index.php/t-182108.html> The TF2 wiki records the hybrid: *"Saxton Hale will be chosen randomly for the first 3 rounds (then by queue)."* — <https://wiki.teamfortress.com/wiki/VS_Saxton_Hale_Mode_(custom_game_mode)> Valve's official 2023 implementation went **fully random**. — <https://wiki.teamfortress.com/wiki/Versus_Saxton_Hale>

**Where rotation works:** Left 4 Dead Versus forces it — *"Each Round of a versus game consists of two turns, with one team playing as the Survivors and the other playing as the Infected. When the turn ends, the teams switch sides,"* and crucially *"Points are only awarded to teams playing as the Survivors"* — the antagonist seat is a **scoring-denial** seat, not a scoring seat, with identical map spawns across both turns so the comparison is fair. — <https://left4deadwiki.com/wiki/Versus> Gmod Murder, Zombie Escape, and Among Us all pick the antagonist **randomly**; **NO SOURCE FOUND** for any earned/queued antagonist in vanilla Murder. — <https://wiki.facepunch.com/gmod/gamemodes/Murder>, <https://github.com/Source2ZE/ZombieReborn>

**The failure mode is real and unsolved.** See "Anti-camp package" above for the arcade etiquette evidence and the oflatt fairness numbers. **NO SOURCE FOUND:** any shipped game that awards the antagonist seat by *winning a deathmatch* and documents how it handles a repeat champion. **INFERENCE: the author's exact mechanic is under-explored in shipped design. That is both the opportunity and the risk — nobody has debugged it for him.**

**What breaks when the role is rotated — Evolve is the cautionary case, and it does not say what you'd expect.** Forced monster assignment made people quit: solo-queue players were shoved into the monster seat because *"the game prioritized a player-controlled monster over everything except keeping party members from being the monster,"* forcing solo players into it *"even if it was their least favored choice"* — and when they wanted hunter levels *"they often just quit."* — <https://steamcommunity.com/app/273350/discussions/0/611698195151979451>, <https://steamcommunity.com/app/273350/discussions/0/353915953245587344>

**But the assumption that "everyone wants to be the antagonist" is not what Evolve's data shows.** The most-viewed community thread is titled *"Why no one wants to be the monster?"* — citing stress, isolation, skill floor, blame, and repetitiveness: *"being a monster is way too stressful"*; players preferred hunter where *"everything doesnt depend entirely upon me."* — <https://steamcommunity.com/app/273350/discussions/0/610573009241132082> Post-mortem: balanced *"around the few top tier players"* producing *"extremely poor balance for lower level players"*; matches were *"hide and seek simulators"* with 15+ minutes of downtime before combat; *"the game never felt really satisfying due to the 4v1 nature."* — <https://steamcommunity.com/app/273350/discussions/0/141136086934209353> Commercial outcome: 2.5M shipped by May 2015 but rapid decline, 44 paid DLC skin packs at launch, "Overwhelmingly Negative" reviews, F2P relaunch in July 2016 (+15,930% players), servers off for good July 2023. — <https://en.wikipedia.org/wiki/Evolve_(video_game)>

**Dead by Daylight is the counter-case, and it is the better analogue for PANOPTICON.** The killer seat is *over*-subscribed: *"The amount of Killer players outnumbers the amount of Survivor players in the matchmaking queue, which makes the Killer role more statistically popular and queue time longer."* Reported killer queues (Aug 2025): *"wait 10 minutes"* standard, *"roughly 4-6 minutes"* even at 11PM–12AM, up from 2–3 minutes three months earlier. — <https://forums.bhvr.com/dead-by-daylight/discussion/454765/these-killer-queue-times-are-killing-me-boss-1v4-and-bhvr-just-added-more-salt-to-the-wound> (Tracker-level figures of killer 3–12 min vs survivor 6–12 s from <https://www.deadbyqueue.com/> came via search snippet and are **second-hand**; direction is region- and time-dependent, with older threads reporting the inverse — <https://forums.bhvr.com/dead-by-daylight/discussion/458541/its-just-me-or-survivors-queue-are-getting-longer>.)

The cost of the seat is stress, and DbD players name it precisely: everything rests on the killer so *"all failure is the killer's fault"*; failure in a chase *"doesn't give the killer a chance to reset and think"*; you are *"alone juggling 4 different people."* — <https://forums.bhvr.com/dead-by-daylight/discussion/311026/why-playing-killer-feels-so-much-more-stressfull-than-playing-survivor>

**INFERENCE, and the load-bearing read for this design:** the antagonist seat is desirable when it is powerful, expressive, and low-mechanical-load (DbD's killer) and undesirable when it is stressful, lonely, and mechanically demanding (Evolve's monster). A single shooter in a tower with a clear power fantasy is **DbD-shaped, not Evolve-shaped.** So "earned seat" is defensible — but the same forces that make it desirable make **camping it the dominant strategy**, and the author's plan to make the shooter *"slightly harder"* is the single lever that pushes the seat back toward Evolve. That tuning is knife-edged and cannot be settled on paper.

Also worth weighing against the 1v7 case: *"one out of five people in any asymmetrical, four-on-one multiplayer game like Evolve is destined to feel ganged up on."* — <https://bloody-disgusting.com/editorials/3603104/asymmetrical-multiplayer-flop-evolve-paved-way-dead-daylight-friday-13th/> (403 on fetch; line surfaced via search snippet — **second-hand**)

---

### 5. Floors vs one continuous run, and the attention mechanic

**The ancestor already used floors — but for a different reason than the author's.** Reach's Duck Hunt was five levels *"designed to be progressively more difficult for the ducks. Cover decreases and traps are added as the level continues."* — <https://halocustoms.com/maps/duck-hunt.2330/> That is **difficulty escalation**, not attention localization. **INFERENCE: the author's justification is a different mechanism bolted onto the ancestor's existing structure, and the two goals pull apart** — escalating difficulty makes the front floor *harder*, while the attention argument makes the back floors *safer*. Both compress the interesting play into the lead position.

**The proven "attention window" designs are short, recurring, and unannounced — the opposite of a floor boundary.**

- **Pac-Man is the cleanest documented case of "the antagonist's attention is predictably elsewhere, and good players exploit it."** Ghosts cycle scatter/chase on a fixed table: levels 1–4 run **7 s scatter / 20 s chase, 7/20, 5/20, then chase forever**. In scatter *"the ghosts give up the chase for a few seconds and head for their respective home corners,"* and *"Good players will take full advantage of the scatter periods by using the brief moment when the ghosts are not chasing Pac-Man to clear dots from the more dangerous areas of the maze."* — <https://www.gamedeveloper.com/design/the-pac-man-dossier> Iwatani's stated reason for alternating at all was that constant pressure is exhausting rather than fun. — <https://www.mentalfloss.com/fun/video-games/your-pac-man-game-learning-different-strategies-each-ghost> **Note the ratio: the safe window is ~25% of the cycle, and the ghosts are still in the maze — scatter is reduced targeting, not safety.**
- **Alien: Isolation caps attention intensity deliberately.** The Director *"never tells the alien exactly where you are, but advises it to head towards your general"* area, and tracks a **menace gauge**; *"Once it reaches a threshold, then the alien will go into the vents for a time, known as backstage mode"* — an explicit, designed relief window. Designers used **"donut-shaped"** search zones so the alien would not camp the objective the player needs. — <https://www.gamedeveloper.com/design/revisiting-the-ai-of-alien-isolation>, <https://www.gamedeveloper.com/design/the-perfect-organism-the-ai-of-alien-isolation> The donut idea maps straight onto a tower: don't let the shooter permanently hold the one angle that matters.
- **Dead by Daylight splits attention *spatially and simultaneously*, not temporally.** Seven generators, five needed, one killer: *"when the map is big and the generators are well-spread, killers have a hard time patrolling them, which greatly reduces the pressure that is placed on survivors."* — <https://elocarry.net/blog/dead-by-daylight/all-maps-ranked-best-to-worst/> The killer's counter is the 3-gen (collapse the spatial problem to one patrol loop), which BHVR nerfed in **patch 7.5.0 (Jan 2024)** because *"the 3-gen strategy … has become very strong."* — <https://steamcommunity.com/app/381210/discussions/0/4145068731423230954/> **INFERENCE: DbD's version gives the antagonist a real decision. A floor system removes that decision and replaces it with a schedule.** First-party BHVR writing articulating "attention as a resource": **NO SOURCE FOUND.**

**Precedent for floors as segmentation, and what it actually buys.**

- **PEAK is the strongest positive precedent, and it shows what to copy.** A run uses six biomes (Shore → Tropics/Roots → Alpine/Mesa → volcanic pair → Peak — <https://blueprintedgaming.com/docs/peak/biome-walkthrough>, <https://peak.wiki.gg/wiki/Locations>; note the Steam page still says "4 biomes" and TheGamer says five — **three published numbers conflict**). The campfire gate is the mechanism: **all players within 19.2 m** to light it, then the fog wall dissipates; it heals, feeds, autosaves, and *"prevents any hunger or the fog from rising until a Scout leaves the Campfire area."* — <https://peak.wiki.gg/wiki/Campfire> **This is a comeback window that is a property of the space, and the leaders visibly pay for it by waiting.** That is why it feels earned rather than handed over.
- **Slay the Spire uses floor *index* as a pacing contract.** Each act is 17 floors with guarantees: floor 1 is always an easy combat, **floor 9 is always a Treasure Room**, **floor 15 is always a Rest Site**, 16 is the boss. — <https://slaythespire.wiki.gg/wiki/Map_Generation> Floors deliver a **guaranteed breather at a known index** while everything else stays random.
- **Fall Guys segments for recovery from failure, not for safety.** Checkpoints are *"small areas where players respawn after falling off a level"*; Space Race is *"divided into four main sections."* Falling sends you back and **costs you position**. Fall Guys even ships **Invisible Checkpoints** for creators — *"an aesthetic tweak that allows you to design levels without showing off checkpoints"* — so segmentation can be functional while the course reads as continuous. — <https://fallguysultimateknockout.fandom.com/wiki/Checkpoints> (402-blocked; via search index), <https://www.fallguys.com/news/fall-forever-update>
- **The Level Design Book on pacing:** *"alternate highs and lows"* because *"players adjust to prolonged periods of high intensity"*; low-intensity areas *"feel like rewards"*; *"Don't try to force the player to be 'on' all the time."* — <https://book.leveldesignbook.com/process/preproduction/pacing>

**The continuous alternative already gets attention-splitting for free from geometry, and the Halo literature says so.** The Level Design Book's **Chill Out (Halo 1)** study describes a map where one elevated watcher demonstrably cannot cover everything: *"Two of these views are too narrow to hit a running enemy more than once, yet it is a valuable position for spotting enemies"*; *"Some of these positions are about information more than the damage a player could deal from them."* — <https://book.leveldesignbook.com/studies/mp/chill-out> On sightlines generally: *"Sniper alleys offer very long sightlines for long range attacks or suppression, while close quarters areas offer shallow sightlines"*; the design goal is *"Varying the quantity and length of sightlines"* and *"Balancing the rate of visual information that the player must process"* because *"a large busy view with many deep sightlines will overwhelm the player about what is relevant."* — <https://book.leveldesignbook.com/process/combat/balance>, <https://book.leveldesignbook.com/process/combat/cover>

**A hard warning for a tall tower:** *"Most maps tend to max-out at three different floor planes for any given area,"* and on controllers *"players often park their camera's vertical rotation aimed at roughly head / chest height, and restrict their aiming movements to the horizontal axis,"* making extreme height variation frustrating. — <https://book.leveldesignbook.com/process/layout/flow/verticality> **If floors are stacked vertically around a tower, this is a direct constraint on how many can be visible at once.**

**SpeedRunners is the cheapest alternative to floors and does the opposite thing:** the camera follows the **leader**, and *"Any player that fails to keep up with the leading player within that screen is eliminated"*; after the first elimination *"the boundaries of the screen increasingly enclose."* — <https://squareblind.wordpress.com/2020/05/25/speedrunners-the-videogame-embracing-everyday-instinct-in-a-superhuman-footrace/> It localizes the **action** rather than the shooter's attention, on a continuous loop, at zero extra level-design cost.

**Player-controlled attention is the third option, and it is the most interesting one.** Prop Hunt's lineage runs CrateDM (1998) → Boxwar (2002, which added third person so players could judge *"how well others will see us"*) → Prop Hunt (2009), which reversed polarity to *"seekers who try to flush-out the hiders,"* producing *"more frantic slapstick."* — <https://www.blog.radiator.debacle.us/2017/05/from-modders-to-mimics-peoples-history.html> The taunt/decoy is the mechanic that lets a **player** move the antagonist's attention rather than a schedule doing it.

**And there is a game literally built on the Panopticon.** Michael C. Stewart's *Panopticon* is a 2.5D platformer where you *"manipulate and evade spotlights to escape a prison,"* explicitly inspired by *Discipline and Punish*, whose designer statement is: *"This game intends to regulate the player's behavior by granting them a cigarette that attracts the attention of spotlights."* — <https://www.michael-c-stewart.com/panopticon> **That cigarette is the purest existing statement of this game's core tension: a thing you want, that buys the watcher's attention.** Academic treatment also exists: Tom van Nuenen, *"Playing the Panopticon: Procedural Surveillance in Dark Souls,"* Games and Culture (2016) — <https://journals.sagepub.com/doi/10.1177/1555412015570967> (403 to fetch; abstract not retrieved).

**Costs of segmentation.**

- **Level design cost: NO SOURCE FOUND.** No dev writing directly addresses "N segments = N distinct spaces" as a multiplayer tradeoff.
- **Over-segmentation is a documented failure.** Yacht Club shipped a Shovel Knight build with checkpoints *"almost on every other screen"* and pulled back. Their solution to the tension problem was to make checkpoints **destructible for gold**, so *"cocky players opt for a reward, but would be sent waaaaay back if they failed."* Their conclusion: *"there is no hard and fast rule: it depends on the game you are trying to create."* — <https://www.yachtclubgames.com/blog/check-point-design/>
- **Checkpoints reduce tension by construction** — removing them *"adds stakes to each decision, heightening tension."* — <https://www.linkedin.com/advice/0/what-best-practices-using-checkpoints-save-points-level-8fcpf>
- **The specific risk here (INFERENCE, flagged):** a floor boundary is a **guaranteed non-event**. Every trailing runner knows the shooter cannot look at them, so the time between floors is strictly dead — no decision, no read, no bluff. Pac-Man's scatter is 5–7 s against 20 s of chase; Alien's backstage is short and unannounced. If PANOPTICON's floors invert that ratio (long safety, short exposure), the antagonist stops mattering.
- **The second, sharper risk (INFERENCE):** with 1–7 runners, a floor system means the shooter's target pool per floor is small, and the **front** floor is strictly more lethal than a continuous course would be. **The safety you grant the back is paid for by the front — which means leading is punished, and the race may invert into everyone deliberately stalling.** That is a rubber band built into the geometry. It could be excellent (free comeback windows) or fatal (nobody wants to lead). It is the single biggest open question in this design and cannot be resolved by argument.

**Jump King / Only Up design writing on segmentation vs continuous: NO SOURCE FOUND.**

---

## WHAT ONLY A PLAYTEST CAN SETTLE

These are the decisions where the research runs out. Each needs bot simulation, human sessions, or both — argument will not close them.

1. **Does floor segmentation invert the race?** If the shooter can only watch the lead floor, leading is dangerous and stalling is optimal. Instrument: run bots with a "hold back one floor" policy against bots that push; if the stallers win, the mechanic is broken as specified. **This is the highest-priority test.**
2. **Floor length: 25 s vs 30 s vs 40 s.** Depends entirely on shot difficulty, course speed, and cover density — none of which any source can tell you. Target: enough time for the shooter to make 2–4 meaningful decisions per floor.
3. **Number of floors: 3, 5, or 7.** Reach used 5; the vertical-planes constraint (max ~3 visible planes) may cap what actually reads on screen.
4. **Is the shooter seat actually the desired seat *in this game*?** DbD-shaped (over-subscribed) or Evolve-shaped (a chore)? Measure it directly: in playtests, log how often people volunteer for the tower and how they feel after a bad tower turn. The author's plan to make the shooter *"slightly harder"* is the knob that moves the game between these two outcomes, and it is knife-edged.
5. **Does a strong player camp the seat in real lobbies?** Simulate with a skill-differential bot ladder over 30-match sequences and compute the oflatt fairness ratio (max games-as-shooter between any two players). If it exceeds ~1.5 at 4 players, an anti-camp mechanic is mandatory, not optional.
6. **Does the opening deathmatch feel like the start of the game or a tax before the real game?** No source can answer this. Test the alternative (random first shooter) head-to-head.
7. **Is 1v7 fun at all, or does the shooter simply not miss?** Halo 3's Duck Hunt scaled **duck movement speed by player count** — 16 players 75%, 14 players 90%, 12 players 100%, 10 players 110% — and the creator explicitly flagged the high-count values as untested estimates. — <https://archive.forgehub.com/threads/team-duck-hunt.104927/> Expect to need the same lever, and expect to have to find the values yourself.
8. **Dead-runner downtime tolerance.** How long will a shot runner watch before they check their phone? Every comparable game solves this differently (ghost tasks, prop possession, postmortem points, instant respawn). The number of seconds people tolerate is empirical.
9. **Whether the terminator (haste-style elastic clock vs a rising threat vs a hard round cap) reads as tension or as an arbitrary buzzer.** Burgun's whole objection is to loops that *"shut off"* arbitrarily — <http://keithburgun.net/arcs-in-strategy-games/> — so the terminator has to feel diegetic. Which one does is a feel question.
10. **What a cleared floor banks, and whether losing it hurts.** The whole depth mechanism (§2) rests on there being something to lose. Candidates: a banked head-start, a shared team resource, a revive charge, position in the shooter queue. Whether any of them *feels* like a loss is empirical — and Sid Meier's warning applies: if progress is destroyed by a dice roll rather than a decision, players will say **"the game is broken"** (<https://venturebeat.com/technology/quotes-from-sid-meiers-keynote-gdc-speech>).
11. **How much randomness the design can carry.** Clever Endeavour removed random power-ups from their new game's main mode because *"every time you receive a power-up, it completely reworks your mental model"* and *"players need to feel like every time they play the game, they get significantly better"* (<https://www.cleverendeavourgames.com/blog/2026/7/10/why-did-we-remove-power-ups-from-the-main-game>). Whether randomized shooter loadouts or trap placement help or destroy the mastery curve here is a playtest question, not an argument.
12. **What a shot runner should become.** PEAK's answer is a ghost who *"gets to keep interacting with people"* with a bird's-eye view (<https://www.gamedeveloper.com/business/peak-co-developer-aggro-crab-shares-lessons-in-friendslop>) — the session keeps all its voices. Whether a PANOPTICON ghost should get a spotter camera, a taunt that pulls shooter attention, or nothing at all is testable and consequential.
13. **Match length at each player count.** The derived rule (time between wins ≈ N × match length) says 8-player matches should be shorter than 4-player ones, but that fights the fact that 8 players need more tower turns. Only session data resolves the tradeoff.

---

## RESEARCH GAPS AND CAVEATS

- The session's WebSearch budget (200 calls) was exhausted mid-research. The **retention-vs-session-length literature is essentially unstarted** — no GDC talk naming a target match length was located.
- **All Fandom wikis are Cloudflare-blocked (HTTP 402)** to the fetcher. That specifically blocked: the Fall Guys per-round timer table and round-by-round qualification targets, the Among Us settings ranges, the Golf With Your Friends per-hole time limit, and the Ultimate Chicken Horse default phase timers. Where text is quoted from these it came via search index and is flagged.
- **HaloCustoms, GameFAQs, ForgeHub (current), Reddit, and SteamDB are all blocked** to this tool. The Halo Reach Duck Hunt gametype's actual numeric settings live inside the `.bin` file and are published nowhere; the Halo 3 equivalent is the only version with real numbers.
- **No average match length is published by the developers of Dead by Daylight or Hunt: Showdown.** Community figures circulating for both have no methodology.
- PEAK's biome count is published as **4 (Steam/Landfall), 5 (TheGamer), and 6 (Wikipedia/wiki.gg)**. Not resolved here.
- **Review-corpus caveats for §2:** Stick Fight n=2,562 vs PEAK n=3,735, built from the same filter mix, but PEAK's corpus skews toward its 2026 Final Ascent update window. Playtime comparisons are directionally solid, not precise.
- **PEAK's relative decay is not dramatically better than Stick Fight's** before its update spike — July 2026 was 21% of its peak month average; Stick Fight at month 14 was 31% of its. The real difference is **~40× the absolute scale plus a live-ops surface that can re-peak** (PEAK +212% MoM in Aug 2026). Do not read the table as "PEAK doesn't decay."
- **No Landfall postmortem, GDC talk, or interview on Stick Fight's longevity exists.** Every critical claim about it is third-party. Do not imply Landfall self-diagnosed this.
- **Unverifiable, do not cite without checking:** no Derek Yu / Spelunky "narrative of the run" verbatim could be confirmed (Boss Fight Books not openly readable); **no Slay the Spire GDC talk exists** in GDC Vault; no verbatim from Engelstein's *Achievement Relocked* (MIT Press blocks fetch) despite it being the most on-thesis book in the field; no RPS/Eurogamer/Polygon PEAK design piece was located. Stephen Totilo's Game File interview with Nick Kaman is paywalled (<https://www.gamefile.news/p/peak-interview>) and is likely the best unread source.
