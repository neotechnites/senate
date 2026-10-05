# Music round 3: SR20DET-template screen (2026-10-05)

Template, measured from each track's own 0:00: (a) full-energy drums in the first second, (b) 3-9 s of drums, (c) 0.2-1.5 s cut, (d) sub-bass (<120 Hz) enters with the full band after the cut, (e) instrumental, (f) hard not harsh, 155-180 bpm.

**Result: nothing passes. No new audition was made.** 275 unique tracks scored (music_vet, _b, _c, _d; wav/m4a duplicates and the earlier audition clips under music_vet_c/chk collapsed). No audio was downloaded and none was added to a repo.

## Meter and calibration on SR20DET
Meter: 11.6 ms frames, broadband RMS and sub-120 Hz RMS from an STFT. A cut is a run of 46 ms-smoothed energy at least 15 dB under the preceding 3 s median, starting 2.5-10.5 s in. Reported against the same file's own 0:00.

| measure | SR20DET | rule |
|---|---|---|
| drum start | 0.06 s | <= 1.0 s |
| first second vs drum section | -0.1 dB | >= -6 dB |
| drums active (frames) | 100% | >= 80% |
| drum length | 5.33 s | 3-9 s |
| cut | 5.39 s, 0.30 s long (-45 dB floor) | 0.2-1.5 s |
| bass entry | 5.69 s | |
| sub-band jump after cut | +18.9 dB (floor +29.8 dB) | >= 8 dB (floor >= 8) |
| broadband jump | +8.0 dB | >= 2 dB |
| bpm | 172.3 | 155-180 |
| centroid / hf>5k share / flatness | 2241 Hz / 1.0% / 0.011 | reference for harsh |
| crest | 6.9 dB | reference (limited, dense) |

SR20DET scores a clear pass on a-d. Its bass entry sits at 5.69 s with no shift, which is the 5.70 s target.

## Funnel (strict thresholds, 275 tracks)
- (a) full-energy start, measured on the first second: 176 (a lenient test; many tracks just start loud)
- a track with any 0.2-1.5 s cut at 2.5-10.5 s: 8; with 3-9 s of drums before a cut: 25 have a cut at all in that window at any length
- a + c: 2; a + b + c: 1; a + b + c + d: **0**
- loose rerun (cut only -10 dB, window to 13 s): a+b+c 6, a-d 0

## Candidates that pass a-c, and the near misses
| track | a | b | c | d | what is missing |
|---|---|---|---|---|---|
| Packback x Saunter - SIERRA (castcadia) | pass 0.0 s | pass 5.1 s | pass 0.21 s at 5.1 | **fail** | sub-bass is already in the opening drums (low band equal before and after, +/-1 dB); the "drop" is the same groove returning. A second, longer gap at 10 s. |
| mimideath 77e73f (snow, auditioned in round 2) | pass 0.0 s | **fail 9.67 s** | pass 0.41 s | pass +34 dB | drums last 9.7 s and are quiet (about 24 dB under the drop); bass lands at 10.1 s. Needs a 4.4 s shift. |
| yet soundsystem mwg-karasawa | pass 0.03 s | **fail 10.2 s** | borderline 1.46 s | pass +17.6 dB | cut at 10.2 s, bass at 11.6 s. |
| music_vet_d yKGaOWBvV6A | fail 0.78 s | fail 11.2 s | pass 0.24 s | pass +50 dB | first drum at 0.78 s, bass at 12.2 s; far too long a lead-in. |
| r3cream Twisted Relic | **fail** (quiet 14 dB-down intro, 3 s) | fail 3.0 s | pass 0.2 s | pass +25.6 dB | opens with a soft pad-like intro, not full drums. |
| mil3sperhour ravetrax-remix | pass | fail 2.95 s | pass 0.37 s | fail +6.7 dB | cuts every few bars (a stutter edit), bass already present. |
| Packback x Saunter / sawteeth / saturn-sdk and others | | | | | short stutter gaps with no sub-band jump (<= +6.6 dB). |

Wide net: tracks with a big sub-band jump in 3-13 s but no real cut (energy dip under 6 dB) were also checked and dropped; the remaining ones with a real dip (peeb 430af0, invvar 5c01ae, Aquamarine) show no cut-then-bass shape (continuous or sub-bass already present).

**Three nearest misses:** (1) mimideath 77e73f: structure right, drums 0.7 s too long and weak; (2) yet soundsystem mwg-karasawa: right shape but 10 s drum section; (3) Packback x Saunter SIERRA: right timing (5.1 s cut) but no sub-bass absent-then-present.

## (e) and (f)
Not scored for any track: no track reached a full a-d pass, so there was nothing to check for vocals or harshness. Reference (f) values are above.

## Per-track flags (strict a b c d, 1 = pass)

- `music_vet/audio/accelio/Accelio - A-Spec.mp3` 1000
- `music_vet/audio/accelio/Accelio - Jazz Club (Featuring ROOXG).mp3` 1000
- `music_vet/audio/accelio/Accelio - Midas.mp3` 1000
- `music_vet/audio/accelio/Accelio - Phendrana's Edge.mp3` 1000
- `music_vet/audio/accelio/Accelio - Shape the Future.mp3` 1000
- `music_vet/audio/accelio/Accelio - Soundboy.mp3` 1000
- `music_vet/audio/accelio/Accelio - Starshine.mp3` 1000
- `music_vet/audio/accelio/Accelio - Uplink.mp3` 1000
- `music_vet/audio/blakless/BLAK.LESS - BLAK.LESS - REAL ANGEL.mp3` 1000
- `music_vet/audio/blakless/BLAK.LESS - BLAK.LESS - Vader’s Burden.mp3` 0000
- `music_vet/audio/castcadia/CASTCADIA - HARDWIRE.mp3` 1000
- `music_vet/audio/castcadia/CASTCADIA - ZEROCORE.mp3` 1000
- `music_vet/audio/castcadia/Packback x Saunter - SECTOR.mp3` 1000
- `music_vet/audio/castcadia/Packback x Saunter - SIERRA.mp3` 1110
- `music_vet/audio/castcadia/Packback x Saunter - WIPEDOUT.mp3` 1000
- `music_vet/audio/coties/Caliope.mp3` 1000
- `music_vet/audio/coties/Inferno.mp3` 1000
- `music_vet/audio/coties/Latom!.mp3` 1000
- `music_vet/audio/dras/Dylan J Ras - Fox's Den.mp3` 1100
- `music_vet/audio/dras/Dylan J Ras - ZYMOGENS.mp3` 1000
- `music_vet/audio/ecoship/Eco Ship - Down Shift.mp3` 0100
- `music_vet/audio/ecoship/Eco Ship - Hyphenization.mp3` 1000
- `music_vet/audio/ecoship/Eco Ship - Porcelain Shores.mp3` 1000
- `music_vet/audio/ecoship/Eco Ship - Sound Blue.mp3` 1000
- `music_vet/audio/evilswag/Tselinoyarsk.mp3` 0000
- `music_vet/audio/evilswag/free jungle background music.mp3` 0000
- `music_vet/audio/evilswag/ps1, ape escape type jungle, FREE.mp3` 1000
- `music_vet/audio/jensvide/Jens Vide - Disillusion ｜ Psycho-Kin OST.wav` 1000
- `music_vet/audio/jensvide/Jens Vide - Glitch Star Dreamer.wav` 1000
- `music_vet/audio/jensvide/Jens Vide - In My Mind.wav` 0000
- `music_vet/audio/jensvide/Jens Vide - Red Hot Chili Desert.wav` 1000
- `music_vet/audio/jensvide/Jens Vide - Scent of Salt.wav` 1100
- `music_vet/audio/jensvide/Jens Vide - The Swirl ｜ Psycho-Kin OST.wav` 1000
- `music_vet/audio/jinkasei/jinkasei - chamber.mp3` 1000
- `music_vet/audio/jinkasei/jinkasei - die4me.mp3` 0000
- `music_vet/audio/jinkasei/jinkasei - intro sequence (8mb for a lifetime).mp3` 0000
- `music_vet/audio/jinkasei/jinkasei - the numbers.mp3` 0000
- `music_vet/audio/kyro/ambiental song.mp3` 1000
- `music_vet/audio/kyro/menu song.mp3` 0000
- `music_vet/audio/kyro/snow song.mp3` 1000
- `music_vet/audio/lastday/Last Day Dreaming - CORRUPTED.mp3` 0000
- `music_vet/audio/lastday/Last Day Dreaming - FRACTURED.mp3` 1000
- `music_vet/audio/lifelike/lifelikemoviee - lifelikemoviee - A Hidden Ninja.mp3` 0110
- `music_vet/audio/lifelike/lifelikemoviee - lifelikemoviee - I'm Different.mp3` 1000
- `music_vet/audio/lifelike/lifelikemoviee - lifelikemoviee - It's Alive.mp3` 1000
- `music_vet/audio/lufus/Lufus - Drama Division.mp3` 1000
- `music_vet/audio/lufus/Lufus - Gear Shift.mp3` 1000
- `music_vet/audio/lufus/Lufus - Night Runner.mp3` 0000
- `music_vet/audio/majoraxis/Blade of The Assassin.mp3` 1000
- `music_vet/audio/majoraxis/Major Axis - Astro.mp3` 1000
- `music_vet/audio/majoraxis/Major Axis - Crystal.mp3` 1000
- `music_vet/audio/majoraxis/Major Axis - Eternity.mp3` 1000
- `music_vet/audio/majoraxis/Major Axis - Mirage.mp3` 1000
- `music_vet/audio/majoraxis/Phantom's Quest.mp3` 1000
- `music_vet/audio/mil3sperhour/ETHERNET LAKE [FREE DL].mp3` 1000
- `music_vet/audio/mil3sperhour/Mil3sperhour & Bassfreak - Mil3sperhour & Bassfreak - Emotio.mp3` 1000
- `music_vet/audio/mil3sperhour/Mil3sperhour - Mil3sperhour - VASTEEL CAVE.mp3` 1000
- `music_vet/audio/mil3sperhour/RIVER RUINS [FREE DL].mp3` 0000
- `music_vet/audio/planarian/Ascend From The Dark.mp3` 1000
- `music_vet/audio/planarian/Ghosts of An Undulated Mind.mp3` 0000
- `music_vet/audio/planarian/Obligatory Sewer Level Music.mp3` 1000
- `music_vet/audio/questionit/Question.It - Aquamarine.mp3` 1000
- `music_vet/audio/questionit/Question.It - Oceanic.mp3` 1000
- `music_vet/audio/questionit/Question.It - Silky.mp3` 1100
- `music_vet/audio/questionit/Question.It - Wonderhill.mp3` 1000
- `music_vet/audio/r3cream/Forgotten Horror.mp3` 1000
- `music_vet/audio/r3cream/Fracture.mp3` 0000
- `music_vet/audio/r3cream/Greasy Shiny Rock.mp3` 1100
- `music_vet/audio/r3cream/Twisted Relic.mp3` 0101
- `music_vet/audio/rooxg/ROOXG - ALTERED SELF.mp3` 0100
- `music_vet/audio/rooxg/ROOXG - NEW AGE OF THE SHADOW MOON.mp3` 0000
- `music_vet/audio/rooxg/ROOXG - ROOXG - OMEGA X.mp3` 1000
- `music_vet/audio/rooxg/ROOXG - ROOXG - SLEEPLESS MALLS.mp3` 0000
- `music_vet/audio/rooxg/ROOXG - THE WARNING.mp3` 0100
- `music_vet/audio/ruby/MUTHUR.mp3` 0000
- `music_vet/audio/ruby/dame muri!.mp3` 0000
- `music_vet/audio/ruby/they chase shadows.mp3` 1000
- `music_vet/audio/sawteeth/Sawteeth - Growing Sprout(V.I.P. Mix).mp3` 1000
- `music_vet/audio/sawteeth/Sawteeth - The Missing Link.mp3` 1000
- `music_vet/audio/sawteeth/Sawteeth - The Silk Road.mp3` 1000
- `music_vet/audio/tonymelodics/Tonymelodics - Gluetronic.mp3` 1000
- `music_vet/audio/tonymelodics/Tonymelodics - Kitbashed.mp3` 1000
- `music_vet/audio/tonymelodics/Tonymelodics - Morbid Cynic.mp3` 1000
- `music_vet/audio/tonymelodics/Tonymelodics - Rage Hack.mp3` 1000
- `music_vet/audio/tormund/Tormund - Fluency Model.wav` 1000
- `music_vet/audio/tormund/Tormund - Intimacy Model.wav` 1000
- `music_vet/audio/tormund/Tormund - Soul Machine Model.wav` 1000
- `music_vet/audio/tormund/Tormund - Spirit Machine Model.wav` 0000
- `music_vet/audio/tormund/Tormund - Tormund - Beholder.mp3` 1000
- `music_vet/audio/usgolf95/US Golf 95 - Acclaim𝗦𝗣𝗢𝗥𝗧𝗦.mp3` 1000
- `music_vet/audio/usgolf95/US Golf 95 - Eidos.mp3` 1000
- `music_vet/audio/usgolf95/US Golf 95 - ＳＱＵＡＲＥＳＯＦＴ.mp3` 1000
- `music_vet/audio/usgolf95/US Golf 95 - 𝕄𝕀ℂℝ𝕆PROSE.mp3` 1000
- `music_vet/audio/yet/YET soundsystem - DEVIL TRIGGER.mp3` 0000
- `music_vet/audio/yet/YET soundsystem - EXOSKELETON.mp3` 1000
- `music_vet/audio/yet/YET soundsystem - SIBERIA.mp3` 1000
- `music_vet/audio/yet/YET soundsystem - TWISTED METAL.mp3` 1000
- `music_vet/audio/yet/YET soundsystem - YAMI YET.mp3` 1000
- `music_vet/seg/01.wav` 1000
- `music_vet/seg/01_n.wav` 0000
- `music_vet/seg/02.wav` 0000
- `music_vet/seg/02_n.wav` 1100
- `music_vet/seg/03.wav` 0000
- `music_vet/seg/03_n.wav` 1000
- `music_vet/seg/04.wav` 1000
- `music_vet/seg/04_n.wav` 0110
- `music_vet/seg/05.wav` 1000
- `music_vet/seg/05_n.wav` 0000
- `music_vet/seg/06.wav` 1000
- `music_vet/seg/06_n.wav` 1000
- `music_vet/seg/07.wav` 1000
- `music_vet/seg/07_n.wav` 0000
- `music_vet/seg/08.wav` 1000
- `music_vet/seg/08_n.wav` 1000
- `music_vet_b/audio/68plus1/64706b.wav` 0000
- `music_vet_b/audio/68plus1/c96c45.wav` 1000
- `music_vet_b/audio/afterlifeslave/ac681d.wav` 0000
- `music_vet_b/audio/akiba/1fbaed.wav` 1000
- `music_vet_b/audio/akiba/4f0fdc.wav` 1000
- `music_vet_b/audio/akiba/6a9ae4.wav` 0000
- `music_vet_b/audio/akts/1cfc20.wav` 1000
- `music_vet_b/audio/collision/c1ca09.wav` 0000
- `music_vet_b/audio/depthcharm/f4b4d6.wav` 0000
- `music_vet_b/audio/egofear/f146e1.wav` 0000
- `music_vet_b/audio/eightiesheadachetape/854d5a.wav` 1000
- `music_vet_b/audio/eightiesheadachetape/96a868.wav` 0000
- `music_vet_b/audio/erythh/122ab0.wav` 1000
- `music_vet_b/audio/fath/72a917.wav` 0000
- `music_vet_b/audio/gaxve/806061.wav` 0000
- `music_vet_b/audio/gaxve/c7004c.wav` 1000
- `music_vet_b/audio/glitchtrode/ca44d8.wav` 0000
- `music_vet_b/audio/hysia/e46b2f.wav` 1000
- `music_vet_b/audio/invvar/5c01ae.wav` 1000
- `music_vet_b/audio/iwakura/cca0cd.wav` 0000
- `music_vet_b/audio/kazahana/8b2f6b.wav` 1000
- `music_vet_b/audio/kazahana/e38ee0.wav` 1000
- `music_vet_b/audio/kazahana/ea2c90.wav` 1000
- `music_vet_b/audio/kentenshi/0d602b.wav` 1000
- `music_vet_b/audio/kentenshi/35f96a.wav` 1000
- `music_vet_b/audio/mejer/3b9f8e.wav` 1000
- `music_vet_b/audio/mejer/ae6757.wav` 0000
- `music_vet_b/audio/mejer/dd4595.wav` 1000
- `music_vet_b/audio/mimideath/64f114.wav` 0100
- `music_vet_b/audio/mimideath/77e73f.wav` 0011
- `music_vet_b/audio/mindvacy/e4083c.wav` 0000
- `music_vet_b/audio/neuronist/ee5621.wav` 0000
- `music_vet_b/audio/nyteout/19336c.wav` 0000
- `music_vet_b/audio/nyteout/dceb2e.wav` 0000
- `music_vet_b/audio/peeb/430af0.wav` 1000
- `music_vet_b/audio/purity/2c67af.wav` 1000
- `music_vet_b/audio/purity/447c36.wav` 1000
- `music_vet_b/audio/purity/7131a6.wav` 1000
- `music_vet_b/audio/rispaa/c18646.wav` 1000
- `music_vet_b/audio/sometheus/9fb21b.wav` 0000
- `music_vet_b/audio/spurme/fad72a.wav` 1000
- `music_vet_b/audio/swyvern/b8461a.wav` 1000
- `music_vet_b/audio/trashiii/1d6e54.wav` 0000
- `music_vet_b/audio/usedcvnt/b50032.wav` 1000
- `music_vet_b/audio/usedcvnt/d4f0c3.wav` 0000
- `music_vet_b/audio/wintermaniac/57a47e.wav` 1000
- `music_vet_b/audio/wintermaniac/fa87d0.wav` 0000
- `music_vet_b/audio/ykort/42acc6.wav` 1000
- `music_vet_c/audio/basix265/gentle-raster-flow-20.m4a` 1000
- `music_vet_c/audio/boy404/2013-audi-a3.m4a` 1000
- `music_vet_c/audio/boy404/artificial-clouds.m4a` 1000
- `music_vet_c/audio/boy404/higher-player404-remix.m4a` 1000
- `music_vet_c/audio/boy404/index100.m4a` 1000
- `music_vet_c/audio/boy404/invisible.m4a` 0000
- `music_vet_c/audio/boy404/isle-of-memory.m4a` 1000
- `music_vet_c/audio/boy404/moog-city-player404-remix.m4a` 0000
- `music_vet_c/audio/boy404/player404.m4a` 1000
- `music_vet_c/audio/boy404/polyphony.m4a` 1000
- `music_vet_c/audio/boy404/r-301.m4a` 1000
- `music_vet_c/audio/boy404/roos.m4a` 1000
- `music_vet_c/audio/boy404/ufo.m4a` 1000
- `music_vet_c/audio/c0ntr0llerps2/blue-hell-7.m4a` 0000
- `music_vet_c/audio/c0ntr0llerps2/deep-dive-6.m4a` 0000
- `music_vet_c/audio/c0ntr0llerps2/deleting.m4a` 0000
- `music_vet_c/audio/c0ntr0llerps2/disk-space.m4a` 0000
- `music_vet_c/audio/c0ntr0llerps2/dropping-through-sky-4.m4a` 0000
- `music_vet_c/audio/c0ntr0llerps2/ifg-3.m4a` 1000
- `music_vet_c/audio/mil3sperhour/california-jpky-mil3sperhour-remix.m4a` 0000
- `music_vet_c/audio/mil3sperhour/chaindiver.m4a` 0000
- `music_vet_c/audio/mil3sperhour/delta-final.m4a` 0000
- `music_vet_c/audio/mil3sperhour/garegga.m4a` 0000
- `music_vet_c/audio/mil3sperhour/kamata-free-dl.m4a` 1000
- `music_vet_c/audio/mil3sperhour/nightopia-sky.m4a` 1000
- `music_vet_c/audio/mil3sperhour/progradepoint.m4a` 1000
- `music_vet_c/audio/mil3sperhour/pun-os-pulseras-y-paletas.m4a` 1000
- `music_vet_c/audio/mil3sperhour/ravetrax-remix.m4a` 1010
- `music_vet_c/audio/mil3sperhour/resurge-x-neddie-debug-mil3sperhour-remix.m4a` 1000
- `music_vet_c/audio/mil3sperhour/saturn-sdk.m4a` 1100
- `music_vet_c/audio/mil3sperhour/searchin-for-my-dreams-remix.m4a` 1000
- `music_vet_c/audio/mil3sperhour/taka-mil3sperhour-remix.m4a` 1000
- `music_vet_c/audio/mil3sperhour/take-it-all.m4a` 0000
- `music_vet_c/audio/mil3sperhour/technomonitor77.m4a` 1000
- `music_vet_c/audio/mil3sperhour/universal-resonance-final.m4a` 1000
- `music_vet_c/audio/mil3sperhour/zensphere-bucolic-systems.m4a` 1000
- `music_vet_c/audio/yetsoundsystem/2002-tokyo.m4a` 1000
- `music_vet_c/audio/yetsoundsystem/3am-lobby.m4a` 1000
- `music_vet_c/audio/yetsoundsystem/8mb.m4a` 0000
- `music_vet_c/audio/yetsoundsystem/blue-stream-2.m4a` 1100
- `music_vet_c/audio/yetsoundsystem/bluestreamps1ps2jungle.m4a` 1100
- `music_vet_c/audio/yetsoundsystem/bust-a-move.m4a` 0000
- `music_vet_c/audio/yetsoundsystem/decoy-single.m4a` 0000
- `music_vet_c/audio/yetsoundsystem/devil-trigger.m4a` 0000
- `music_vet_c/audio/yetsoundsystem/dualshock2.m4a` 1000
- `music_vet_c/audio/yetsoundsystem/emotion-engine.m4a` 1100
- `music_vet_c/audio/yetsoundsystem/encounter-1.m4a` 0000
- `music_vet_c/audio/yetsoundsystem/file-city.m4a` 1000
- `music_vet_c/audio/yetsoundsystem/hydro.m4a` 1000
- `music_vet_c/audio/yetsoundsystem/kazama-0st.m4a` 1000
- `music_vet_c/audio/yetsoundsystem/koi5501.m4a` 1000
- `music_vet_c/audio/yetsoundsystem/kutaragi.m4a` 1000
- `music_vet_c/audio/yetsoundsystem/life-points.m4a` 0000
- `music_vet_c/audio/yetsoundsystem/mokujin-stance.m4a` 0000
- `music_vet_c/audio/yetsoundsystem/mwg-karasawa.m4a` 0011
- `music_vet_c/audio/yetsoundsystem/now-loading.m4a` 1000
- `music_vet_c/audio/yetsoundsystem/ntsc-j.m4a` 1000
- `music_vet_c/audio/yetsoundsystem/prototype.m4a` 0100
- `music_vet_c/audio/yetsoundsystem/ps2bootup.m4a` 1000
- `music_vet_c/audio/yetsoundsystem/psx.m4a` 1000
- `music_vet_c/audio/yetsoundsystem/s-rank.m4a` 0000
- `music_vet_c/audio/yetsoundsystem/shibuya-incident-2.m4a` 1000
- `music_vet_c/audio/yetsoundsystem/shibuya-incident-single.m4a` 1000
- `music_vet_c/audio/yetsoundsystem/siberia.m4a` 1000
- `music_vet_c/audio/yetsoundsystem/skyring-ps1-jungle.m4a` 1000
- `music_vet_c/audio/yetsoundsystem/skyring.m4a` 1000
- `music_vet_c/audio/yetsoundsystem/soul-reaver.m4a` 0000
- `music_vet_c/audio/yetsoundsystem/soul-reaver1.m4a` 0000
- `music_vet_c/audio/yetsoundsystem/summit-rush.m4a` 1000
- `music_vet_c/audio/yetsoundsystem/tag-tournament.m4a` 1000
- `music_vet_c/audio/yetsoundsystem/tm26-3.m4a` 1000
- `music_vet_c/audio/yetsoundsystem/tsukuba-circuit.m4a` 1100
- `music_vet_c/audio/yetsoundsystem/ugh.m4a` 0000
- `music_vet_c/audio/yetsoundsystem/virtual-beauty.m4a` 0000
- `music_vet_c/audio/yetsoundsystem/warhead.m4a` 0000
- `music_vet_c/audio/yetsoundsystem/xgears.m4a` 1000
- `music_vet_c/audio/yetsoundsystem/yami-yet.m4a` 1000
- `music_vet_c/audio/yetsoundsystem/yet-soundsystem-chaos-theory-sc-version.m4a` 0000
- `music_vet_c/audio/yetsoundsystem/yet-soundsystem-kazama-ps1-jungle.m4a` 1000
- `music_vet_c/audio/yetsoundsystem/yoshimitsu-ost.m4a` 1000
- `music_vet_c/audio_yt/rel/-24iesn8qGI.wav` 1100
- `music_vet_c/audio_yt/rel/5mEZHBnPH1I.wav` 1000
- `music_vet_c/audio_yt/rel/Mb7XWxB15Ns.wav` 1000
- `music_vet_c/audio_yt/rel/_eHJKWIRHzc.wav` 1000
- `music_vet_c/audio_yt/rel/huldkCZB3Ms.wav` 0000
- `music_vet_c/audio_yt/rel/kAqZaX4PA9g.wav` 1000
- `music_vet_c/audio_yt/rel/s6sxt2fUKwk.wav` 1000
- `music_vet_c/audio_yt/rel/wedHNJlOCS4.wav` 1000
- `music_vet_c/audio_yt/yet/5F69weKE8Jk.wav` 1000
- `music_vet_c/audio_yt/yet/BnHWUNA38pU.wav` 0110
- `music_vet_c/audio_yt/yet/D6ux1SPugwM.wav` 0000
- `music_vet_c/audio_yt/yet/VXAiV0t8MPw.wav` 1000
- `music_vet_c/audio_yt/yet/_6lK30S_9Yc.wav` 0000
- `music_vet_c/audio_yt/yet/cnEBOcxDokk.wav` 1000
- `music_vet_c/audio_yt/yet/ep_accelerate.wav` 0000
- `music_vet_c/audio_yt/yet/ep_limit_break.wav` 0000
- `music_vet_c/audio_yt/yet/ep_time_splitters.wav` 0000
- `music_vet_c/audio_yt/yet/fc5q3fXhqyo.wav` 0000
- `music_vet_c/audio_yt/yet/iwZ3Ii61lGc.wav` 1000
- `music_vet_c/audio_yt/yet/lnO_LPkB8c0.wav` 0000
- `music_vet_c/audio_yt/yet/qL2_GCDbvgA.wav` 1000
- `music_vet_d/audio/7JlHCyE__T4.wav` 1100
- `music_vet_d/audio/BTiC5KY9H1M.wav` 0000
- `music_vet_d/audio/LIGe-td4u2Y.wav` 0000
- `music_vet_d/audio/_hsMMqRiOPE.wav` 0000
- `music_vet_d/audio/dR4FXotFqW0.wav` 0110
- `music_vet_d/audio/fEIpCsvcHUs.wav` 0000
- `music_vet_d/audio/iI0Qe_XlBlw.wav` 0100
- `music_vet_d/audio/ic0DonLGRBQ.wav` 0000
- `music_vet_d/audio/qIi_2E-0wWw.wav` 0100
- `music_vet_d/audio/tUH4AgiFSNc.wav` 0000
- `music_vet_d/audio/tnue5aUOq7U.wav` 0000
- `music_vet_d/audio/yKGaOWBvV6A.wav` 1000
