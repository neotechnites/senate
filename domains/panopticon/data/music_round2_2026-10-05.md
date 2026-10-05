# PANOPTICON music, round 2: "song opens, cut, huge drop" (2026-10-05)

Brief from feedback on rounds 1-2: the song's OWN opening plays from frame 1, then a cut/gap/thinning, then a huge full-band drop a few seconds in (SR20DET: 0.35 s silence from 5.36 s, hit at 5.70 s). Mid-song slices and "a snare comes in" don't count.

## Method
- Pool: all ~146 tracks already downloaded (music_vet, music_vet_b), plus 80 new SoundCloud pulls (every original MIL3SPERHOUR and YET soundsystem upload, plus close-circle tracks), plus 24 YouTube pulls (YET's remaining YouTube-only tracks and the LIMIT BREAK EP split by chapter, and YET/M3PH-adjacent artists). Around 250 tracks were measured. Audio is in the scratchpad only (music_vet_c/), not in any repo.
- Circle: the accounts that MIL3SPERHOUR and YET repost, like or collaborate with. That covers Lunanescence (chaindiver, Tsukuba Circuit), the Memory Archives label (YET's compilation, Major Axis), Shibuya Nights, Naoki, player404, C0NTR0LLER, Septem Noctes, Minimis, Thought-Forms and BASIX. MIL3SPERHOUR's other reposts are mostly riddim/dubstep (Bassfreak, JPKy and others) and were skipped.
- SoundCloud started returning 403 partway through. About 115 circle tracks never downloaded: Shibuya Nights, Naoki, Minimis, Memory Archives, Thought-Forms, Septem Noctes and most of Lunanescence. A few came via YouTube search instead.
- New detector, "first big drop" (not the biggest). Starting from the first audible frame, it finds the first point at least 2.5 s later where:
  - the next 2 s are within 4 dB of the track's loud level, and its sub-bass (25-120 Hz) is within 6 dB of the track's loud sub level;
  - the level is at least 6 dB above the intro median, or the sub-bass is at least 15 dB above it;
  - the level is at least 5 dB above the previous 1 s.
- The hit is then refined to 10 ms. "Gap" means time in the last 1.5 s spent more than 18 dB below the drop level.
- Check on SR20DET: drop 5.64 s, intro-to-drop lift +8 dB full / +22 dB sub, gap 0.30 s.
- Tempo: the meters disagree on some tracks, so ambiguous ones are given as two values. Check by ear.

## Part 1: audition set 3
Folder: `~/Desktop/panopticon-renders/trailer_reveal/music_audition_2/`.
- Picture is rough_v24, video stream copied, original audio dropped. Each file is 43.5 s.
- Audio: linear gain to -14.0 LUFS integrated, light limiter, peaks -1.4 dBFS or lower, 2 s fade-out.
- No dynamic loudnorm was used, so the intro-to-drop contrast is intact.
- Ranked by how closely the opening matches SR20: own opening, gap, size, earliness.
- None of these tracks was in the earlier two sets.

| # | File | Track (link) | Track start | Drop in video | Jump (full / sub) | Gap before | BPM | Note |
|---|---|---|---|---|---|---|---|---|
| 01 | 01_yet_soundsystem_ugh.mp4 | YET soundsystem "ugh" https://soundcloud.com/yetsoundsystem/ugh | 0:00 | **8.41 s** (would need 2.7 s trimmed, not forced) | +20 / +49 dB | **1.1 s near-silence** | ~154 (or 172; meters disagree) | Closest SR20 shape in the pool: quiet intro, hard cut, full hit. It's a 2-min sketch-like upload (Feb 2026) |
| 02 | 02_mimideath_snow.mp4 | MIMIDEATH "snow" https://www.youtube.com/watch?v=1ZyNf2q2kY0 | 0:00 | **11.02 s** (not forced) | +24 / +54 dB | **1.25 s** | ~174 | Biggest hit-after-gap among early drops. Leans major (-0.13) and is glitchy. YouTube upload |
| 03 | 03_yet_soundsystem_devil_trigger.mp4 | YET soundsystem "DEVIL TRIGGER" https://yetsoundsystem.bandcamp.com/track/devil-trigger | 0:00 | **12.0 s** (not forced) | +11 / +58 dB | 0.45 s dip | ~160 | Intro sits at -12 to -18 dB like SR20's, not near-silent. Huge sub entry, minor-leaning |
| 04 | 04_mimideath_abusive.mp4 | MIMIDEATH "abusive" https://www.youtube.com/watch?v=C__jC62LXBw | 0:00 | **8.66 s** (not forced) | +16 / +49 dB | 0.2 s (slight) | ~166 | Quiet intro then full band. Small riser rather than a clean cut |
| 05 | 05_mejer_insomnia.mp4 | Mejer "insomnia" https://www.youtube.com/watch?v=q0QV9W35OqA | trimmed 0.06 s | **5.70 s** (on title card) | +12 / +30 dB | none (fade-in intro) | ~167 | The only one whose own drop naturally lands on the title card. No gap. First ~2.4 s is a fade-in from silence (YouTube upload, so it may include padding) |
| 06 | 06_mil3sperhour_take_it_all.mp4 | MIL3SPERHOUR "TAKE IT ALL" https://soundcloud.com/mil3sperhour/take-it-all | 0:00 | **3.25 s** (would need 2.45 s padding, not forced) | +21 / +48 dB | 0.4 s | ~150 or ~171 (ambiguous) | The only early-drop track by MIL3SPERHOUR. The intro is only ~3 s. It's his rejected 2021 ANV6 submission, CC BY-NC-SA |
| 07 | 07_packback_x_saunter_wipedout.mp4 | Packback x Saunter "WIPEDOUT" https://castcadia.bandcamp.com/track/wipedout | 0:00 | **12.0 s** (not forced) | +11 / +29 dB | 0.35 s | ~160 | Darkest key reading of the set (minor +0.32). Opens with a hit at 0 s and 6 s, then dips into the drop. CASTCADIA's members, who ask for game work |
| 08 | 08_yet_soundsystem_now_loading.mp4 | YET soundsystem "NOW LOADING" https://soundcloud.com/yetsoundsystem/now-loading | cut in at 10.37 s | **5.70 s** (track drop 16.07 s) | +17 / +34 dB, +35 dB vs last 1 s | 0.75 s, intro thins 18 dB first | ~160 | Most SR20-like thinning before the hit, but the drop is late, so the picture starts inside the intro |

Close runners-up (YET, all drops later than 12 s, so they'd need the picture cut into the intro):
- WARHEAD: 17.2 s, +29/+76 dB, 0.75 s gap
- MOKUJIN STANCE: 14.3 s, 0.7 s gap
- S-RANK: 22.9 s, 1.15 s gap, darkest centroid
- SHIBUYA INCIDENT: 24.1 s, 1.1 s gap
- GUNSMOKE: 22.7 s, 1.4 s gap
- FMG-9: 28.4 s, 1.35 s gap, intro thins 14 dB first
- TM26: 27.5 s, 1.45 s gap

Others:
- Naoki "Suzuka 2050" (third-party YouTube upload): 11.3 s, +26 dB, but the first ~6 s is near-silent.
- player404 "moog city" remix: 12.1 s, 1.25 s gap, but it's a remix of a Minecraft track.

## Part 2: first big drop inside the first 10 s (all pools)
Drop time is measured from the start of the file. YouTube uploads can carry up to ~2 s of padding.

| Artist | Track | Link | BPM | First drop | Jump full / sub | Gap before? |
|---|---|---|---|---|---|---|
| jinkasei | intro sequence (8mb for a lifetime) | https://jinkasei.bandcamp.com/ | ~170 | 2.8 s | +14 / +40 dB | no (0.1 s) |
| MIL3SPERHOUR | TAKE IT ALL | https://soundcloud.com/mil3sperhour/take-it-all | ~150 or ~171 | 3.25 s | +21 / +48 dB | yes, 0.4 s |
| C0NTR0LLER | Deleting... | https://soundcloud.com/c0ntr0llerps2/deleting | ~155 | 3.45 s | +24 / +7 dB (little sub, not a full-band drop) | yes, 0.7 s |
| evilswagconjurer | Tselinoyarsk | https://soundcloud.com/evilswagconjurer/tselinoyarsk | ~164 | 4.7 s | +14 / +14 dB | no |
| 68+1 | walk away (love y'all guys) | https://www.youtube.com/watch?v=5M1dUjehyTs | ~177 | 5.45 s | +5 / +22 dB (modest) | no |
| Mejer | insomnia | https://www.youtube.com/watch?v=q0QV9W35OqA | ~167 | 5.76 s | +12 / +30 dB | no (fade-in) |
| YET soundsystem | KOI-55.01 | https://soundcloud.com/yetsoundsystem/koi5501 | ~160 | 6.0 s | +5 / +11 dB (small, looping swells) | no |
| YET soundsystem | ugh | https://soundcloud.com/yetsoundsystem/ugh | ~154 or 172 | 8.4 s | +20 / +49 dB | **yes, 1.1 s** |
| MIMIDEATH | abusive | https://www.youtube.com/watch?v=C__jC62LXBw | ~166 | 8.7 s | +16 / +49 dB | slight, 0.2 s |

Just over 10 s:
- kazahana "mania", 10.85 s (already auditioned)
- Collision.Is.Imminent, 10.9 s (already auditioned)
- MIMIDEATH "snow", 11.0 s, 1.25 s gap
- jinkasei "die4me", 11.3 s, riser with no gap
- Naoki "Suzuka 2050", 11.3 s
- YET "SOUL REAVER", 11.5 s
- Egofear "Neuralink", 11.65 s (earlier audition used a later drop)
- YET "DEVIL TRIGGER", 12.0 s
- Packback x Saunter "WIPEDOUT", 12.0 s

Every other MIL3SPERHOUR original has a late first drop:
- RIVER RUINS: ~105 s
- Zensphere: 22 s
- VASTEEL CAVE: 26 s
- DELTA: 38.5 s
- PUÑOS bootleg: 15.3 s

## Part 3: the two liked artists (public pages only)

### MIL3SPERHOUR (Austin, TX)
**(a) Size**
- SoundCloud: 2,281 followers, 27 tracks. Top plays: GAREGGA 18.5k, chaindiver 15.1k, NIGHTOPIA SKY 11k, RIVER RUINS ~20.8k (earlier read).
- YouTube: 5,170 subscribers. Mostly production tutorials; the RIVER RUINS breakdown has 11k views.
- Spotify: 2K monthly listeners.
- Last.fm: 1,959 listeners.
- Instagram: 715 followers (from a summarised page read).
- X: not readable.
- Price read: small independent act. With ~2k fans, a one-track trailer licence is plausibly in the low hundreds of USD rather than thousands. That is an inference: no rate card was found.

**(b) Reachability**
- Contact routes:
  - email mil3sperhourmusic@gmail.com (SoundCloud bio)
  - Discord @mil3sperhour, plus a "futurist hub" Discord server (discord.gg/wUQNEApuJZ; the tutorial lists discord.com/invite/yGZNFRYkDh)
  - X @Mil3sperhour, Instagram @mil3sperhour, YouTube @mil3sperhour
  - BeatStars store (beatstars.com/mil3sperhour, a beat-licensing marketplace; its pricing didn't render)
  - Gumroad sample pack, linktr.ee/mil3sperhour
  - a second SoundCloud, "mil3sperhour 2", for clips, VGM demos and works in progress
- Latest SoundCloud uploads: TECHNO MONITOR 77 and Prograde Point, both 2026-06-27.
- Latest YouTube upload: 2026-08-11 (Serum tutorial).
- Instagram's most recent post was reported as 2026-10-05 by a summarised read. Unverified.
- Cadence: a SoundCloud release every 1-3 months (2025: Feb x2, Jul, Sep; 2026: Apr, Jun x3), plus long YouTube tutorials.
- Replies to comments: yes. He answered 9 of 44 comments on the RIVER RUINS tutorial, with technical answers, and thanks commenters on Zensphere.

**(c) Game affinity and terms**
- Very strong game affinity:
  - Track names come from Sega/arcade games: GAREGGA, NIGHTOPIA SKY, SATURN SDK, chaindiver. His YouTube has an "ableton reconstruction" of ChainDive.
  - RIVER RUINS uses instruments he ripped from DoDonPachi's files (his own tutorial says so).
  - He was on "Under the Blue Sky: SEGA Racing Tribute" and "Foreground Renaissance", both on technomarina Bandcamp. His own description links the latter's VGMdb entry (vgmdb.net/album/161309).
  - He posts "sega rally inspired/racing game lounge music" sketches.
- Free downloads: many [FREE DL] tracks. NIGHTOPIA SKY, TAKE IT ALL and DELTA are tagged CC BY-NC-SA on SoundCloud. Non-commercial only, so a commercial trailer still needs his permission. Everything else is "all rights reserved".
- No "use my music in your video/game" statement and no licensing terms found.
- STRAFTAT:
  - NOT confirmed from a primary source. The developers' 49 Steam news posts (including the "MUSIC UPDATE", 30+ songs, March 2025) name only Major Axis as a music collaborator. The Steam store page has no music credits.
  - Two secondary sources agree: the community wiki and a fan "STRAFTAT Full Soundtrack" YouTube video (The Krozzus) list ETHERNET LAKE, NIGHTOPIA SKY 2022 REDUX and RIVER RUINS [FINAL V] alongside the Jungle Fatigue roster.
  - None of his own SoundCloud descriptions mentions STRAFTAT.

### YET soundsystem (Germany)
**(a) Size**
- SoundCloud: 276 followers, 80 tracks, including slowed duplicates. Typical plays 200-2,000; top track 2002 TOKYO has 3.8k.
- YouTube: 434 subscribers.
- Spotify: 1.3K monthly listeners.
- Instagram: 486 followers (summarised read).
- Bandcamp follower count: not readable.
- Price read: about a tenth of MIL3SPERHOUR's audience. Likely the cheapest of the two and the most likely to treat a game trailer as a big deal. That is an inference; no rates were found.

**(b) Reachability**
- No public email found.
- Routes: Bandcamp contact form, Instagram DM @yet.soundsystem (bio also tags @yet.vault), SoundCloud, YouTube @yetsoundsystem, linktr.ee/yetsoundsystem (socials and streaming only).
- Latest release: the 8MB album, uploaded to SoundCloud on 2026-06-18 (Bandcamp release date June 19, 2026) and to YouTube on 2026-06-19.
- The SoundCloud profile was edited 2026-09-20.
- Latest Instagram post date: not seen.
- Cadence: roughly monthly singles plus an EP or album 1-2 times a year (Limit Break EP Jun 2024; Forbidden Memories Jan 2025; Sub Zero EP Aug 2025; 8MB Jun 2026).
- Replies to comments: yes, almost every YouTube commenter gets a "thank you" (2 of 5, 3 of 9 and 2 of 5 comments on the three videos checked were his replies).

**(c) Game affinity and terms**
- Bandcamp bio: "grew up in the 90s, surrounded by the eternal soundtracks of video games like Street Fighter, Ridge Racer and Tekken".
- Nearly every title references a PS1/PS2 game or the hardware:
  - Tekken: KAZAMA 0ST, MOKUJIN STANCE, yoshimitsu 0ST, TAG TOURNAMENT
  - Legacy of Kain: Soul Reaver
  - also TWISTED METAL, TIME SPLITTERS, DEVIL TRIGGER, XGEARS, TSUKUBA CIRCUIT, LIMIT BREAK, FMG-9
  - hardware: PS2BOOTUP!, DUALSHOCK 2, KUTARAGI, PSX, NTSC-J, 8MB, NOW LOADING
- Free downloads: SOUL REAVER and PROTOTYPE. Everything else is "all rights reserved".
- No game placements, no licensing terms and no "use my music" statement found.
- Released on the Memory Archives label compilation (Major Axis and Lykos). That is the label tied to STRAFTAT's Major Axis collaboration, and a plausible warm route.

### Could not see
- X/Twitter for both. Instagram post dates for YET; the dates for MIL3SPERHOUR came only via a summarising fetch.
- SoundCloud comment replies (SoundCloud 403'd later reads).
- BeatStars lease prices. Bandcamp follower counts.
- Any primary STRAFTAT credit for MIL3SPERHOUR.
- About 115 circle tracks blocked by SoundCloud's 403 (Shibuya Nights, Naoki, Minimis, Memory Archives catalog).
- Tempo is ambiguous on "ugh" and TAKE IT ALL.
- Nothing was listened to. Drop times and gaps are from the meters, so judge by ear.
