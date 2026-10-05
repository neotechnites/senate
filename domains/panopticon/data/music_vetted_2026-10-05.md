# PANOPTICON music: vetted producers (2026-10-05)

Builds on `music_artists_2026-10-05.md` (10 leads). The pool was widened to 38 candidates: the 10 leads, 3 that earlier research dropped, the STRAFTAT soundtrack roster, itch.io drum-and-bass sellers, and SoundCloud "ps1 jungle" uploaders. 75 tracks from 27 artists were pulled with yt-dlp and measured with librosa:
- **Tempo:** onset autocorrelation, searched in 150-185 and folded from half or double tempo.
- **Mode:** Krumhansl key profile. The minor margin is the minor-profile correlation minus the major one.
- **Brightness:** median spectral centroid in Hz. Lower is darker.
- **Breaks:** percussive onsets per beat.
- **Drop:** the biggest 4-second jump in loudness and sub-bass that follows a quieter 4-second passage.

Follower counts come from the profile page JSON (`followers_count`) at fetch time. The meters are a stand-in for listening. Nobody has heard these tracks yet, so the audition reel is the real test.

**Audition reel:** `~/Desktop/panopticon-renders/trailer_reveal/music_audition/01..08_*.mp4`. Each one uses the rough_v24 picture (video stream copied, original audio dropped) with the track's drop placed at 5.70 s on the title card. The music is -14.0 LUFS integrated, the true peak is -1 dB or lower, and each file is 43.5 s long. The no-music sound-effects cut was not used because the pano-trailer worktree was not readable from this session.

**STRAFTAT credits** come from the community wiki music page (https://straftat.wiki/wiki/Music), which lists artist and track for every song. The Steam page (https://store.steampowered.com/app/2386720/STRAFTAT/) does not list music credits. Most of the STRAFTAT artists are on the Jungle Fatigue label (sawteeth.bandcamp.com), so the game probably licensed existing catalog. A STRAFTAT credit therefore means "licensed into a shipped game", not "wrote to a brief".

## The 8 (best first)

| # | Artist | Profile | Audition track (drop used) | BPM | Key | Followers seen | Confirmed game credits | Commission status | Published price | Contact |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | CASTCADIA (project of Packback + Saunter) | https://soundcloud.com/castcadia , https://castcadia.bandcamp.com | ZEROCORE https://castcadia.bandcamp.com/track/zerocore (drop 111.6 s) | 171.9 | D min | SC 175 | STRAFTAT: "WRLD", plus "ECCO" and "SIERRA" as Packback ft. CASTCADIA (wiki). Their own SC tags say "straftat" | **Yes, stated.** SC bio: "Let us make music for your game! Shoot us a message or email us" | none | castcadiamusic@gmail.com ; X @castcadia |
| 2 | MIL3SPERHOUR | https://soundcloud.com/mil3sperhour | RIVER RUINS https://soundcloud.com/mil3sperhour/river-ruins (drop 104.5 s) | 170.0 | G# min | SC 2,281 | STRAFTAT: ETHERNET LAKE, NIGHTOPIA SKY 2022 REDUX, RIVER RUINS (wiki) | No statement. Contact details are posted | none | mil3sperhourmusic@gmail.com ; Discord @mil3sperhour |
| 3 | R3CREAM | https://soundcloud.com/r3cream , https://itch.io/profile/r3cream | Fracture https://soundcloud.com/r3cream/fracture (drop 12.0 s) | 160.1 | C min | SC 12 | Infinite Body Problem (https://toastergamess.itch.io/infinite-body-problem): page credits "R3cream – Music Composer & Sound Designer". Confirmed | **Yes, stated** on the itch profile ("fine working with anyone who's interested"). Targets late-90s/2000s game DnB | none | Discord r3cream ; itch DMs |
| 4 | YET soundsystem (Germany) | https://soundcloud.com/yetsoundsystem , https://yetsoundsystem.bandcamp.com | SIBERIA https://yetsoundsystem.bandcamp.com/track/siberia (drop 23.3 s) | 164.7 | F# min | SC 276 | none found | No statement | none | Instagram @yet.soundsystem ; YouTube @yetsoundsystem ; Bandcamp |
| 5 | Major Axis (UK/Spain, Memory Archives label) | https://majoraxis.bandcamp.com , https://soundcloud.com/majoraxis | Astro https://majoraxis.bandcamp.com/track/astro (drop 17.2 s) | 168.0 | A min | SC 532 | STRAFTAT: 11 tracks (wiki). Axyz is claimed in his Bandcamp bio, but no game page was found: UNCONFIRMED | No statement | none | https://linktr.ee/majoraxis ; Instagram @majoraxis.wav |
| 6 | Accelio (Brooklyn) | https://accelio.bandcamp.com | Uplink https://accelio.bandcamp.com/track/uplink (drop 125.8 s) | 166.8 | C min | not found (no SC account located) | STRAFTAT: 6 tracks incl. Soundboy, Shape The Future, Edge of the World (wiki) | No statement. Email is in the Bandcamp bio | none | acceliomusic@gmail.com |
| 7 | Sawteeth (Seoul; runs the Jungle Fatigue label) | https://sawteeth.bandcamp.com | Growing Sprout (V.I.P. Mix) https://sawteeth.bandcamp.com/track/growing-sprout-v-i-p-mix (drop 225.9 s) | 169.9 | D min | not found | STRAFTAT: 4 tracks (wiki) | **Partly.** Bio: "Mail me for mixing/mastering/production services" (production work, not game scoring) | none | sawteethjunglist@gmail.com ; Discord via Bandcamp links |
| 8 | Jens Vide (Sweden) | https://jensvide.bandcamp.com , https://jensvide.com | Disillusion (Psycho-Kin OST) https://jensvide.bandcamp.com/track/disillusion-psycho-kin-ost (drop 35.0 s) | 163.7 | A min | SC 1 (he mostly uses itch/Bandcamp) | Psycho-Kin (Steam, Dec 2025, https://store.steampowered.com/app/2875000/PsychoKin/). The Steam page lists no music credit; the credit rests on his Bandcamp OST release and a press write-up. FUNKYHEART: his OST is on Bandcamp. BastionOS, Shrimp Game, ENDHELL, Babel Adventure, Shadow Walker are claimed on his site/Twine and were NOT opened | **Yes, stated.** Site says "Do you want memorable music for your game? Contact me now". Twine: "Available to hire" | none | jens@jensvide.com ; X @JensVide777 |

Why each fits, or the doubt:
1. **CASTCADIA:** the only shortlisted act that explicitly asks game developers for work. The sound is Y2K/PS1 jungle and it already ships in a FPS. ZEROCORE has the biggest measured drop on the list (+41 dB sub-bass jump). The doubt is that it is a group project, so ask who would actually write the cue.
2. **MIL3SPERHOUR:** RIVER RUINS is classic intelligent jungle, the closest match to the Ridge Racer / Metalheadz mood (20.8k plays). The doubt is that most of his recent output is Sega-style riddim and dubstep, and at 2.3k followers he is the largest on the list, so he may price higher.
3. **R3CREAM:** the darkest minor reading of the 8 (minor margin +0.24). He has an open commission offer and a confirmed credit. The doubts are 160 bpm (bottom of the range), very short tracks, and amateur scale (12 followers).
4. **YET soundsystem:** the whole catalog is named for PS1/PS2 games (Tekken, Soul Reaver, Twisted Metal). This is the closest sound to the brief, with real chopped breaks. The doubts are that no game credit or commission statement exists, and the only contact route is social DMs.
5. **Major Axis:** polished atmospheric jungle with the most game placements. The doubt is that his music leans liquid/ambient (calm) rather than tense, and as a label founder he is the act most likely to be near the budget ceiling.
6. **Accelio:** dark C-minor jungle on the STRAFTAT roster, with a direct email. The doubts are that there is no game-work statement and no follower count could be checked.
7. **Sawteeth:** label boss on the STRAFTAT roster who openly sells production services, a likely broker to the rest of the Jungle Fatigue roster. The doubt is that the tracks are bright for the brief (centroid 3,100-3,800 Hz) and the drops come late.
8. **Jens Vide:** the most real shipped game credits and an explicit hire offer. The doubt is that Disillusion is dark synth with frantic breaks rather than PS1 jungle, and its measured drop is the weakest of the 8 (+9.6 dB).

First alternates are in order:
1. **Tormund** (STRAFTAT): Beholder, 172 bpm, F min, strong drop. His only contact route is Instagram via linktree.
2. **ROOXG** (STRAFTAT, SC 396): New Age of the Shadow Moon, 174 bpm, D# min. His bio says "contact @ any platform".
3. **Lifelikemoviee** (STRAFTAT, SC 246): A Hidden Ninja, 165 bpm, D min. Email nomovie1996@gmail.com.

## Rejected (measured or checked)

| Candidate | Reason |
|---|---|
| kyro (kyro67; Jungleworks set https://soundcloud.com/kyro-106676672/sets/jungleworks) | Published price $65 loop / $130 track. But the 3 portfolio tracks are about 2 min and very bright (centroid 3,400-4,200 Hz) with almost no drop (+0.4 to +4 dB). Main SC has 6 followers and no credit |
| Coties (SC ccoties, 46) | Commission open, but the sound is "colorful". Best track Caliope is in G major; Inferno has a weak 170 lock. No credit |
| WWG / Whole Wheat Games | Not measured. YouTube only, quality unverified, no credit confirmed |
| LastDayDreaming | Measured Bandcamp tracks are not in range (FRACTURED does not lock at 170; CORRUPTED is 184.5). The Neo-Jungle pack was not downloadable. No credit |
| Lufus | Drama Division (176.8, C# min) fits on paper. But he is a stock-pack seller with the 50M-download mobile credits unverified, no commission statement, and mostly EDM remixes |
| Dylan J Ras | Fox's Den 164.5 F min fits. But he offers non-exclusive free-for-credit work only, with no credit. The SC "dras" account (117) looks like a different person |
| Question.It | Bright racing mood (Aquamarine centroid 3,670); Silky is in a major key. No credit or commission statement |
| US Golf 95 | All 4 measured tracks are in major keys and chill. No commission route |
| Eco Ship | Hyphenization (168, D min) fits well. But no contact, commission statement or credit was found |
| jinkasei | die4me (170, D min) fits. But no commission statement, the SC account is unused, and the catalog is mostly breakcore/"angelpunk" |
| Tonymelodics | STRAFTAT credit and Kitbashed (164, A# min) fits. But he has no contact route beyond Bandcamp, and SC shows 0 tracks |
| Tormund / ROOXG / Lifelikemoviee | Good fits (see alternates). They lost only on contact route or brightness |
| BLAKLESS | REAL ANGEL is 169.6 C# min, but the catalog is breakcore/edits with no commission statement or credit |
| ruby (snwlvl) | Open to commissions (itch). But measured tracks are ambient/breakcore: MUTHUR has no drop and dame muri! is 152 bpm |
| evilswagconjurer | Free type-beat uploader (3 followers). No contact or commission statement |
| PlanarianHugger | All OST-jam tracks are in major keys, plus meme mashups. The PS1 "Avian Wasteland" entry was not reachable |
| theblade_ | Metal and Undertale covers. Wrong genre |
| KRIMSU | Polish "vixa" DJ mixes. Wrong genre |
| Thought Forms (STRAFTAT) | Could not resolve: the SC/Bandcamp "Thought Forms" is a Bristol shoegaze band |
| hyperix (STRAFTAT) | No profile found |
| ethereal2080 | Sample-pack company, not a composer for hire |
| elevchyt, mariosello1, NicoleMarieT, MorphonautAudio, Musinova, ducksoles | Itch asset packs. No downloadable preview through yt-dlp, and no commission statement or contact seen |
| Pizza Hotline, Machine Girl, Sewerslvt | Out of range per brief |

## Not verified
- Published prices: none of the 8 publishes one. Ask each for a quote on the 45 s cue plus 12 tracks with exclusive rights.
- STRAFTAT credits rest on the community wiki, not on in-game or Steam credits.
- These were not opened: Major Axis's Axyz credit; Jens Vide's credits beyond Psycho-Kin and FUNKYHEART.
- Follower counts for Accelio and Sawteeth.
- "Exclusive" willingness: CASTCADIA, MIL3SPERHOUR and the STRAFTAT roster already license their catalog, so exclusivity for new work must be asked explicitly.
- Drop points were found by algorithm. On a few reels (R3CREAM, Major Axis) the jump is a sub-bass entry rather than a full drop, so judge them by ear.
