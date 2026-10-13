# How ~$1M indie multiplayer games got there: steady tail vs external virality
Date: 2026-10-08. Scope: small-team online/local multiplayer, party, co-op and versus games on Steam, roughly $1M-$5M gross. Mega-hits are excluded (Among Us, Lethal Company, R.E.P.O., Content Warning, PEAK, Phasmophobia, Fall Guys, Chained Together, and the near-mega tier listed at the bottom).

## Bottom line
- **Across all eras, steady is the majority: 16 of 27 (59%).** 8 of 27 (30%) had a clear external spike: 6 at launch and 2 long after launch. 3 of 27 (11%) are mixed (a creator-driven climb with no single spike).
- **The era split matters more than the overall average.** Of the 14 games launched 2013-2018, 13 are steady. Of the 9 games launched 2021 or later, all 6 self-published titles priced at $15 or less got there through a virality wave. The 3 recent steady games were publisher-backed (Team17 twice) and priced at $20-25.
- **Price splits the paths cleanly.** Every in-band game priced at $3-8 needed virality or a creator-driven climb (Mage Arena, Dale & Dawson, PICO PARK, Hand Simulator, Pacify). The one possible exception is Mount Your Friends, which is ambiguous. Almost every steady game was $13-20 at list price and was ported to consoles.
- **Crawl is the textbook steady case.** It made US$2.5M+ on Steam from 475k+ copies over about 10 years (Startup Daily, Oct 2025), which works out to about $5.26 per copy, or about 35% of its $14.99 list price. In 12 years no single month accounts for more than 3% of its lifetime reviews.

## Method and confidence
- **Review counts, prices, release dates and review history** come from the Steam store API (appdetails, appreviews, and the monthly review histogram), pulled 2026-10-08. Owner ranges come from SteamSpy.
- **Revenue estimates (Boxleiter)** use gross ≈ total reviews × list price × 20, with a plausible range of ×14 to ×30. This is calibrated on Crawl's reported figures: $2.5M / (7,324 reviews × $14.99) = ×22.8. Where developer or press figures exist they are quoted instead. The estimates cover Steam only unless noted and are **gross before Steam's 30% cut**. A developer typically nets about 55-65% of gross after the cut, refunds and VAT. Treat every revenue figure as ±40%.
- **Raijin.gg, a third-party tracker, undercounts older games.** It puts Crawl at $1.5M and 163k copies against the reported $2.5M and 475k, so it is used only as a cross-check.
- **How paths were classified.** The main input is the shape of the monthly Steam review history:
  - Peak month share is the peak month's share of lifetime reviews.
  - First 3 months is the share of lifetime reviews in the first three months.
  - Month at 50% is the number of months it took to reach half of lifetime reviews.

  Review shape was combined with dated press or creator evidence where it could be found. A launch-front-loaded decay with no outside trigger counts as STEADY ("solid launch then tail"), which is the "normal" path the question describes. VIRAL means a sharp spike tied to creators, TikTok or chart virality.
- **Wishlists:** launch wishlist counts are not public for any of these games except where noted. Nothing reliable was found, so the column is omitted.
- **Selection bias:** the candidate list was built from games that are memorable, and viral games are more memorable, so the viral share here is probably an overestimate. Also, three "viral" calls (Ghost Watchers, PICO PARK, Lockdown Protocol) rest mainly on the shape of the review history plus genre and streamer context, without a named creator video.

## Full table (27 in-band games)
Abbreviations: yrs = years since first Steam release (early access counts). Platforms: W/M/L = Win/Mac/Linux, plus console ports. Price = list price at launch. Rev est. = gross, Steam only unless noted.

| # | Game (dev) | First on Steam | yrs | Price | Platforms | Steam reviews | Rev est. (gross) | Path | Shape (peak mo share / first-3-mo / mo to 50%) | Key evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Crawl (Powerhoof, 2 people) | Aug 2014 EA, 1.0 Apr 2017 | 12 | $14.99 | WML; PS4/XB1/Switch 2017 | 7,324 | **$2.5M reported** (Steam) | STEADY | 3% / 5% / 60 | Startup Daily 2025: $2.5M+, 475k+ copies, "funded the studio for a decade". Reviews ran 350-820 a year for 9 years with no spike. |
| 2 | Nidhogg (Messhof) | Jan 2014 | 12.7 | $9.99 (later $14.99) | WM; PS4/Vita | 7,927 | $1.6M (Raijin $2.2M) | STEADY (launch-led) | 10% / 10% / 28 | Came from IGF/press. Decay from 1,475 reviews (2014) to 1,244 to 726, then a flat tail of about 200-350 a year. |
| 3 | TowerFall Ascension (Matt Thorson) | Mar 2014 | 12.6 | $14.99 | WML; PS4, Switch, XB1 (Ouya first) | 3,631 | $1.1M Steam; about $500k all platforms by mid-2014, with PS4 the larger share | STEADY | 5% / 5% / 59 | AOL/Eurogamer 2014: about $500k, roughly 80% from PS4 and PC, credited to Sony featuring. Reviews flat at 120-480 a year. |
| 4 | Lovers in a Dangerous Spacetime (Asteroid Base, 3 people) | Sep 2015 | 11.1 | $14.99 | WML; XB1, PS4, Switch | 4,076 | $1.2M (Raijin $1.4M) + consoles | STEADY | 3% / 5% / 52 | Peak month is only 112 reviews. Reviews grew in 2017 with the Switch/PS4 ports. Raijin: 156k copies. |
| 5 | Party Panic (Everglow, small) | Jul 2016 EA | 10.2 | $14.99-16.99 | WML; Switch, XB1 | 3,465 | $1.2M | STEADY | 5% / 0% / 53 | Reviews rose slowly to 2019-2020, then a tail. No outside trigger found. |
| 6 | Monster Prom (Beautiful Glitch; pub. Those Awesome Guys) | Apr 2018 | 8.5 | $11.99 | WML; Switch 2020, PS4/XB1 2020 | 14,347 | $3.4M + consoles | STEADY | 3% / 6% / 33 | Peak month 3%. Bumps line up with console ports and sequel launches (Nov 2020). Kickstarter was about $30k. |
| 7 | Tricky Towers (WeirdBeard) | Aug 2016 | 10.2 | $14.99 | WML; PS4 (PS Plus at launch), XB1, Switch | 16,524 | ~$5M (edge of band) | STEADY | 3% / 1% / 58 | Launched as a PS Plus title. Steam reviews climbed every year to 2021 (2,353), with no month above 3%. |
| 8 | We Were Here Too (Total Mayhem) | Feb 2018 | 8.7 | $9.99 | WM; consoles | 11,353 | $2.3M | STEADY | 5% / 7% / 58 | Funnelled by the free first game. Reviews were flat at about 700-1,460 a year through 2025. |
| 9 | Lethal League (Team Reptile) | Aug 2014 | 12.1 | $13.99 | WML; PS4/XB1 | 6,058 | $1.7M | STEADY (launch-led) | 12% / 12% / 19 | Front-loaded decay, then a slow tail. No outside spike. |
| 10 | Lethal League Blaze (Team Reptile) | Oct 2018 | 8 | $19.99 | WML; PS4/XB1/Switch | 6,707 | $2.7M | STEADY (launch-led) | 23% / 25% / 23 | Sequel to an existing fanbase. Launch-heavy, then 140-830 reviews a year. |
| 11 | Ship of Fools (Fika; pub. Team17) | Nov 2022 | 3.9 | $19.99 | W; all consoles | 6,306 | $2.5M | STEADY (launch-led) | 23% / 27% / 12 | Publisher launch, then a tail of 500-1,600 a year. No creator spike. |
| 12 | Operation: Tango (Clever Plays; co-pub. Team17) | Jun 2021 | 5.3 | $19.99-24.99 | W; PS4/PS5/XB | 8,950 | $3.6M | STEADY (launch-led) | 21% / 24% / 12 | Publisher launch and a 2-player "friend pass" model, then a decay. |
| 13 | FOREWARNED (Dreambyte, small) | Sep 2021 EA | 5.1 | $12.99 | W | 6,671 | $1.7M | STEADY (launch-led), low confidence | 14% / 26% / 13 | Rode the post-Phasmophobia genre wave. A retrospective calls the EA launch "average"; no creator spike found. |
| 14 | Death Squared (SMG Studio) | Mar 2017 | 9.6 | $14.99 | WM; Switch, PS4, XB1 | 725 | Steam about $0.2M; **300k units across all platforms** (GoNintendo), about $1.5-2.5M gross est. | STEADY (console-led) | 7% / 2% / 50 | A Steam flop that worked on Switch. Shows that ports can carry the whole $1M. |
| 15 | Mount Your Friends (Stegersaurus, solo) | Jul 2014 | 12.2 | $4.99 | W (XBLIG first) | 7,666 | $0.8M (VG Insights via SteamPulse: $3.3M, 1.1M units incl. bundles) | STEADY by curve; probably creator-fed, unproven | 6% / 10% / 28 | Flat at about 1,000 reviews a year from 2014-2016, then a decay. A "crowd-drawing" meme game, but no single spike and no dated creator wave found. |
| 16 | Barony (Turning Wheel, small) | Jun 2015 | 11.3 | $19.99 | WML; Switch, PS, XB, Epic crossplay | 18,265 | 1M copies (dev, Jun 2026), about $3-5M est. | LATE BLOOMER (update-driven, not viral) | 11% (Jul 2026) / 1% / 115 | Automaton 2026: 75% of players arrived after the 2023 "Quality of Death" update, plus crossplay. Reviews rose every year from 2022 to 2026. |
| 17 | Dale & Dawson Stationery Supplies (Striped Panda) | Aug 2024 | 2.1 | $7.99 | W; consoles later | 9,023 | $1.4M | VIRAL-AT-LAUNCH | 35% / 49% / 3 | 35% of lifetime reviews came in month 1 (Sep 2024). Wikipedia: "gained popularity through YouTube and Twitch". |
| 18 | LOCKDOWN Protocol (Mirage Creative Lab) | Jul 2024 EA | 2.2 | $9.99 | W | 20,035 | ~$4M | VIRAL-AT-LAUNCH | 14% / 23% / 5 | ChilledChaos was the top streamer in launch week (Streams Charts). Peak of 9.4k concurrent players in Sep 2024, then down 99%. 49% of reviews came Sep-Dec 2024. |
| 19 | Mage Arena (jrsjams, solo) | Jul 2025 EA | 1.2 | $2.99 | W | 20,463 | Raijin $2.1M; Alinea: 235k copies in 5 days | VIRAL-AT-LAUNCH | 56% / 56% / 2 | Alinea: 119k copies in week 1, 116k in one day. xQc stream, TikTok/Twitch virality (PCGH, Alinea). Developer nets about $1 per copy. |
| 20 | Bread & Fred (SandCastles; pub. Apogee) | May 2023 | 3.4 | $14.99 | W; consoles | 5,259 | $1.6M | VIRAL-AT-LAUNCH (TikTok) | 17% / 18% / 7 | TikTok clips with up to 3.3M likes. Developers say it "exploded" on TikTok and were surprised (GGRecon, Merahputih citing Polygon). |
| 21 | Ghost Watchers (Renderise) | Jul 2022 EA | 4.2 | $14.99 | W | 16,346 | ~$4.9M (edge of band) | VIRAL-AT-LAUNCH, medium-low confidence | 19% / 33% / 4 | Two sharp spikes (Aug and Nov 2022) make up 34% of lifetime reviews. A Phasmophobia-like in streamer season. No named creator found. |
| 22 | PICO PARK (TECOPARK, solo) | May 2021 (online Steam version) | 5.4 | $4.99 | W; Switch | 29,998 | $3M | VIRAL soon after launch, medium confidence | 11% / 6% / 17 | Concurrent players hit 16.8k in July 2021 (Automaton). Jul-Nov 2021 holds about 31% of lifetime reviews. Streamer-driven by inference. |
| 23 | Shotgun Farmers (Megastorm, solo) | Jun 2017 EA | 9.3 | $9.99 | W; XB1/PS4 Sep 2020 | 9,845 | $2M (Raijin $3.6M) | LATE-VIRAL, medium confidence | 7% / 2% / 40 | 2020 holds 50% of lifetime Steam reviews, three years after EA. PureXbox Sep 2020: #1 paid Xbox game in the US, solo developer celebrating on TikTok. |
| 24 | Shift Happens (Klonk; pub. Daedalic) | Sep 2015 EA | 11.1 | $15.99 | W; consoles | 4,391 | $1.4M | LATE spike, cause unexplained | 7% / 0% / 83 | 21-96 reviews a year until 2020, then 681-864 a year in 2021-23. The trigger was not found (giveaway or creator; low confidence). |
| 25 | Pacify (Shawn Hitchcock, solo) | Feb 2019 | 7.6 | $4.99 | W; Xbox | 42,831 | ~$4.3M | MIXED (creator-fed plateau) | 5% / 3% / 28 | 2020-21 holds 52% of reviews, spread over many months (no month above 5%). A horror co-op streamer staple (Twitch shows 2019 onward). |
| 26 | Hand Simulator (HFM, small) | Jul 2017 | 9.2 | $2.99 | W | 36,189 | ~$2.2M | MIXED (YouTube-fed climb) | 6% / 1% / 32 | Rose from 2,060 reviews (2017) to 6,100-6,500 a year in 2018-20. A YouTube-comedy staple, but no single spike. |
| 27 | Super Bunny Man (Catobyte, 2 people) | Sep 2017 EA | 9.1 | $14.99 | WML; Switch Nov 2024 | 12,496 | ~$3.7M (dev: 1.5M PC players) | MIXED | 10% (Nov 2023) / 0% / 74 | Coverage by Achievement Hunter and other YouTubers in 2018 (developer reply on the Steam forum). Slow EA climb, a 1.0 in 2023, and one late spike. |

## Split
| Path | Count | % | Games |
|---|---|---|---|
| STEADY (incl. launch-led decay and console-led) | 15 | 56% | Crawl, Nidhogg, TowerFall, Lovers, Party Panic, Monster Prom, Tricky Towers, We Were Here Too, Lethal League, LL Blaze, Ship of Fools, Operation Tango, Forewarned, Death Squared, Mount Your Friends |
| LATE BLOOMER (update-driven, not external) | 1 | 4% | Barony |
| VIRAL-AT-LAUNCH | 6 | 22% | Dale & Dawson, LOCKDOWN Protocol, Mage Arena, Bread & Fred, Ghost Watchers, PICO PARK |
| LATE-VIRAL / late spike | 2 | 7% | Shotgun Farmers, Shift Happens |
| MIXED | 3 | 11% | Pacify, Hand Simulator, Super Bunny Man |

**By era:**
- **First on Steam 2013-2018 (14 games):** 13 non-viral. Mount Your Friends is borderline.
- **2019-2020 (1 game):** Pacify, mixed.
- **2021+ (9 games):**
  - 6 viral. All of them are self-published or small-publisher titles at $3-15.
  - 3 steady: Ship of Fools, Operation Tango, Forewarned. Two were Team17-backed at $20-25.

**By price:**
- **List price ≤ $8 (6 games):** Mage Arena, Hand Simulator, Pacify, PICO PARK, Dale & Dawson and Mount Your Friends. 5 needed a creator wave or a creator-fed climb. The sixth, Mount Your Friends, is ambiguous.
- **List price $10-20 (21 games):** 15 steady, 1 late bloomer, 3 viral (Lockdown Protocol, Bread & Fred, Ghost Watchers), 2 late or mixed.

## What the steady ones had in common
1. **Price of $13-20 at list (median $14.99).** Then years of discounting. Crawl realised about $5.26 per copy on $14.99. The tail runs on 50-80%-off sales and bundles, so the list price is the ceiling the discounts work down from.
2. **Console ports, usually within 1-3 years.** 13 of 15 shipped on PS4, Xbox One or Switch. Death Squared made most of its $1M on consoles, and TowerFall did better on PS4 than on PC. Platform-holder deals (PS Plus at launch for Tricky Towers, Sony featuring for TowerFall) acted like a guaranteed floor.
3. **Local and couch multiplayer as well as online.** The 2014-2018 steady cohort is almost entirely couch-versus or couch-co-op games. Their sales came from word of mouth at parties, plus Switch.
4. **Long tails of 8-12 years** at roughly 200-800 Steam reviews a year, often with content updates (Barony's 2023 overhaul drove 75% of its players). The $1M accrued over a decade, not in a launch window.
5. **Critical or press prestige at launch** (IGF, PAX, Sony/Nintendo indie showcases) rather than streamer virality.
6. **Recent steady cases have a publisher** (Team17) and charge $20-25. No 2021+ self-published game under $15 in this sample reached the band without a viral wave.

## Implications for PANOPTICON's price ($7 vs $10-15)
- **Per-copy math.** At about 35-45% realised per copy (Crawl's ratio), a $7 game nets about $2.50-3.20 gross per copy. Reaching $1M gross needs roughly 310k-400k copies, against about 190k at $14.99. At ×20, $1M gross is about 7,100 reviews at $7 and about 3,300 at $15.
- **Every in-band game priced under $8 got there on a creator or virality wave.** The cheap price is what made that wave convert: impulse buys, buying for the friend group, $3-8 gifts for a squad. So $7 is effectively a bet on virality. If it hits, cheap is right. Liar's Bar ($7), WEBFISHING ($5) and Mage Arena ($3) show cheap plus viral can far overshoot $1M. If it doesn't hit, $7 has no steady path to $1M in this sample.
- **$10-15 is the price at which a steady tail can plausibly add up to $1M**, especially with a Switch, PS or Xbox port and years of 50-75%-off sales. It still leaves room for a virality wave, since Lockdown Protocol ($10) and Bread & Fred ($15) went viral.
- **For a friends-only online game, consider a 4-pack or friend-pass at $10-15.** Operation Tango's 2-player friend pass is one precedent. It keeps the group-buy friction low without anchoring at $7.
- **Caveat on PANOPTICON's fit.** It is online-only and asymmetric, with no couch or local play, which removes the main word-of-mouth channel of the 2014-2018 steady cohort. Online-only is also the profile of the recent viral cohort (Lockdown Protocol, Dale & Dawson, Mage Arena, Ghost Watchers, Forewarned). The closest comps to PANOPTICON's shape skew viral, which argues for designing for clips and streamers whatever the price.

## Excluded (out of band)
- **Above band (Steam gross well above about $5M):** Ultimate Chicken Horse (Raijin $8.5M), Bopl Battle ($8.3M), Duck Game, Move or Die (23k reviews), Who's Your Daddy, Stick Fight, ROUNDS, Pummel Party, Liar's Bar, WEBFISHING, Supermarket Together, Crab Champions, Witch It, Clone Drone, Golf It!, SpeedRunners, BattleBlock Theater, Keep Talking, Unrailed!, BIGFOOT.
- **Below band:** Samurai Gunn, Knight Squad, Regular Human Basketball (Powerhoof), Stikbold, Videoball, Toto Temple Deluxe, Sausage Sports Club, Catastronauts, Unspottable, Hidden in Plain Sight, Heave Ho (~$0.5M Steam), Nidhogg 2, Screencheat, Murderous Pursuits, Bloody Trapland, Embr.
- **Below-band local-multiplayer games are the base rate to remember.** Many critically liked games never got near $1M. This sample conditions on success.

## Sources
- Steam store API (appdetails, appreviews, appreviewhistogram) and SteamSpy appdetails, pulled 2026-10-08 (raw: scratchpad pull).
- Crawl: https://www.startupdaily.net/after-hours/gaming-how-game-of-the-year-winner-powerhoof-became-a-quiet-success/ ; Raijin https://raijin.gg/app/293780/Crawl ; SteamPulse https://steampulse.org/game/293780
- TowerFall: https://www.aol.com/news/2014-04-29-towerfall-tiny-sales-ouya.html ; https://cinemablend.com/games/TowerFall-Selling-PlayStation-4-PC-63760.html
- Nidhogg: https://raijin.gg/app/94400/Nidhogg
- Lovers: https://raijin.gg/app/252110/Lovers_in_a_Dangerous_Spacetime
- Move or Die GDC talk: https://gdcvault.com/play/1024982/-Move-or-Die-Why
- Ultimate Chicken Horse: https://raijin.gg/app/386940/Ultimate_Chicken_Horse ; Bopl Battle: https://raijin.gg/app/1686940/Bopl_Battle
- Mount Your Friends: https://steampulse.org/game/296470
- Who's Your Daddy: https://www.purexbox.com/news/2024/08/three-years-on-whos-your-daddy-is-still-dominating-the-xbox-charts
- Mage Arena: https://alineaanalytics.substack.com/p/indie-games-old-and-new-killed-it ; https://www.pcgameshardware.de/Indie-Games-Thema-239276/News/Steam-Hit-Koop-PVP-Spiel-Release-Bewertung-1478471/ ; https://raijin.gg/app/3716600/Mage_Arena
- Dale & Dawson: https://en.wikipedia.org/wiki/Dale_%26_Dawson_Stationery_Supplies
- LOCKDOWN Protocol: https://streamscharts.com/games/lockdown-protocol/release-stats ; https://steambase.io/apps/lockdown-protocol
- Bread & Fred: https://www.ggrecon.com/articles/secret-shelf-bread-and-fred/ ; https://www.merahputih.com/post/read/lagi-viral-nih-bread-fred-gim-co-op-platformer
- PICO PARK: https://automaton-media.com/en/news/20210906-1808
- Shotgun Farmers: https://www.purexbox.com/news/2020/09/indie_fps_shotgun_farmers_is_already_a_massive_success_on_xbox ; https://raijin.gg/app/604240/Shotgun_Farmers
- Barony: https://automaton-media.com/articles/newsjp/barony-20260626-452208/
- Super Bunny Man: https://nintendoeverything.com/super-bunny-man-dropping-on-nintendo-switch-next-week/ ; https://steamcommunity.com/app/673750/discussions/0/1710690018668107414/
- Death Squared: https://gonintendo.com/stories/364931-death-squared-hits-300k-sold-on-all-platforms-combined-over-150k
- Forewarned: https://www.gamenguide.com/articles/105147/20240429/forewarned-1-0-launches-encouraging-multiplayer-tomb-raids.htm
- Tricky Towers: https://ozbargain.com.au/product/tricky-towers
- Monster Prom: https://en.wikipedia.org/wiki/Monster_Prom
