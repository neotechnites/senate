# Steam Games Pricing/Data Research — Checkpoint (2026-09-09)

Status: PARTIAL. Sections for Pummel Party, Among Us, Dead by Daylight are marked INCOMPLETE below and still need research (a background agent for these was in progress; result not yet returned at time of this checkpoint write). All other sections below are complete and sourced.

Method used: Steam Storefront/reviews/news APIs, official ISteamUserStats CCU API, SteamSpy API, SteamCharts, and Wayback Machine snapshots of Steam store pages (used for historical launch/EA prices, since SteamSpy's `initialprice` field reflects only current list price, not historical launch price). SteamDB (steamdb.info) was Cloudflare-blocked (HTTP 403) on every attempt for every game checked — no SteamDB data used anywhere in this file.

---

## Hide or Die (Steam AppID [731620](https://store.steampowered.com/app/731620/Hide_Or_Die/), dev VecFour Digital)

- **Current USD price**: N/A — DELISTED, not purchasable. Confirmed live 2026-09-09: store page shows "Notice: Hide Or Die is no longer available on the Steam store." https://store.steampowered.com/app/731620/Hide_Or_Die/
- **Launch/original USD price**: $24.99 (Early Access list price, archived US-region snapshot Nov 17, 2019) http://web.archive.org/web/20191117173205/http://store.steampowered.com/app/731620
- **Release date (1.0)**: May 1, 2020 https://store.steampowered.com/api/appdetails?appids=731620 (exited EA by this date per archived snapshot showing no EA badge, price $19.99) http://web.archive.org/web/20200612170017/https://store.steampowered.com/app/731620/
- **Early Access**: Yes. EA launch date: Aug 1, 2019 (per "Release Date" field on archived store page) http://web.archive.org/web/20191005044421/http://store.steampowered.com/app/731620. EA price: $24.99 http://web.archive.org/web/20191117173205/http://store.steampowered.com/app/731620. 1.0 exit-EA date/price: May 1, 2020 / $19.99 http://web.archive.org/web/20200612170017/https://store.steampowered.com/app/731620/
- **Reviews**: Mixed, 1,496 reviews (843 positive / 653 negative) https://store.steampowered.com/appreviews/731620?json=1&language=all&purchase_type=all
- **Owners**: 50,000 – 100,000 (SteamSpy) https://steamspy.com/api.php?request=appdetails&appid=731620
- **Price change**: Decreased from $24.99 (EA) to $19.99 at 1.0 launch, May 1, 2020 — sources above. Still $19.99 on Nov 7, 2020 http://web.archive.org/web/20201107223511/https://store.steampowered.com/app/731620. No further changes documented.
- **Peak/current CCU**: All-time peak 717 (reached March 2018, per SteamCharts data archived Nov 12, 2020 — SteamCharts.com now errors for this app since it's delisted) http://web.archive.org/web/20201112024837/https://steamcharts.com/app/731620. Current CCU: 0 (2026-09-09) https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid=731620
- **Status**: Confirmed delisted/removed from sale. Still on sale Nov 7, 2020; already "no longer available" by Oct 23, 2021 http://web.archive.org/web/20211023044010/https://store.steampowered.com/app/731620/ — exact delisting date: NO SOURCE FOUND.

## Midnight Ghost Hunt (Steam AppID [915810](https://store.steampowered.com/app/915810/), dev Vaulted Sky Games, publisher Coffee Stain Publishing)

- **Current USD price**: $19.99 https://store.steampowered.com/api/appdetails?appids=915810
- **Launch/original USD price**: $19.99 (Early Access launch price) http://web.archive.org/web/20220515074416/https://store.steampowered.com/app/915810
- **Release date (1.0)**: Mar 21, 2024 https://store.steampowered.com/api/appdetails?appids=915810
- **Early Access**: Yes. EA launch date: Mar 31, 2022, price $19.99 http://web.archive.org/web/20220515074416/https://store.steampowered.com/app/915810 (still "TBA"/unreleased as late as Nov 1, 2021 http://web.archive.org/web/20211101192832/https://store.steampowered.com/app/915810). 1.0 date/price: Mar 21, 2024 / $19.99 (unchanged) https://store.steampowered.com/api/appdetails?appids=915810
- **Reviews**: Mostly Positive, 7,537 reviews (5,765 positive / 1,772 negative) https://store.steampowered.com/appreviews/915810?json=1&language=all&purchase_type=all
- **Owners**: 200,000 – 500,000 (SteamSpy) https://steamspy.com/api.php?request=appdetails&appid=915810
- **Price change**: None found — $19.99 constant from EA launch (Mar 2022) through 1.0 (Mar 2024) to today, confirmed across multiple archived snapshots (Feb 2023 http://web.archive.org/web/20230204140834/https://store.steampowered.com/app/915810 and live API today). A temporary "Free Weekend" promo ran ~Mar 22, 2024 http://web.archive.org/web/20240322134428/https://store.steampowered.com/app/915810 — not a permanent change.
- **Peak/current CCU**: All-time peak 4,801 https://steamcharts.com/app/915810. Current CCU: 3 (2026-09-09) https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid=915810; last-30-days average 3.34, peak 13 https://steamcharts.com/app/915810

## Damned (2014 asymmetrical horror, Steam AppID [251170](https://store.steampowered.com/app/251170/Damned/), dev 9heads Game Studios)

- Confirmed correct game (hotel setting, 4 survivors vs. 1 monster) via Steam appdetails description https://store.steampowered.com/api/appdetails?appids=251170 matching a contemporaneous 2013 preview https://web.archive.org/web/20130824170539/http://www.indiegamemag.com/damned-preview/. Not to be confused with "Damned 2" (AppID 2221390, 2025 game, same dev/franchise).
- **Current USD price**: N/A — DELISTED, not purchasable. Confirmed live 2026-09-09: "Notice: Damned is no longer available on the Steam store." https://store.steampowered.com/app/251170/Damned/
- **Launch/original USD price**: $9.99 (Early Access launch price, earliest archived snapshot) http://web.archive.org/web/20130927221657/http://store.steampowered.com/app/251170/
- **Release date (1.0)**: Oct 6, 2014 https://store.steampowered.com/api/appdetails?appids=251170 (transitioned out of EA between Oct 1, 2014, still EA http://web.archive.org/web/20141001135912/http://store.steampowered.com/app/251170/ and Oct 10, 2014, EA badge gone http://web.archive.org/web/20141010134845/http://store.steampowered.com/app/251170)
- **Early Access**: Yes. EA launch: on or before Sept 27, 2013 (earliest Wayback capture, already live in EA) http://web.archive.org/web/20130927221657/http://store.steampowered.com/app/251170/, price $9.99. 1.0 date/price: Oct 6, 2014 / $19.99 (see price-change history below).
- **Reviews**: Mostly Positive, 3,841 reviews (2,707 positive / 1,134 negative) https://store.steampowered.com/appreviews/251170?json=1&language=all&purchase_type=all
- **Owners**: 200,000 – 500,000 (SteamSpy) https://steamspy.com/api.php?request=appdetails&appid=251170
- **Price changes** (multiple, confirmed via Wayback snapshots of actual displayed price):
  - $9.99 → $14.99: between Oct 7, 2013 ($9.99) http://web.archive.org/web/20131007222154/http://store.steampowered.com/app/251170 and Oct 16, 2013 ($14.99) http://web.archive.org/web/20131016213729/http://store.steampowered.com/app/251170
  - $14.99 → $19.99: between Apr 26, 2014 ($14.99) http://web.archive.org/web/20140426204530/http://store.steampowered.com/app/251170/ and Oct 1, 2014 ($19.99) http://web.archive.org/web/20141001135912/http://store.steampowered.com/app/251170/ — held at $19.99 through at least May 2, 2017 http://web.archive.org/web/20170502004928/http://store.steampowered.com/app/251170/Damned
  - $19.99 → $8.99: at some later, unconfirmed date before delisting — SteamSpy's last-cached price is $8.99 https://steamspy.com/api.php?request=appdetails&appid=251170 (exact date: NO SOURCE FOUND)
- **Peak/current CCU**: All-time peak 976 https://steamcharts.com/app/251170 (tracking ends ~March 2024, consistent with delisting). Current CCU: 0 (2026-09-09) https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid=251170
- **Status**: Confirmed delisted. Developer 9heads Game Studios' official site is now a dead/expired domain redirecting to a hosting-provider 404 page, consistent with the studio being defunct https://www.9heads.com/games/damned/ (checked live 2026-09-09).

---

## White Noise 2 (Steam AppID [503350](https://store.steampowered.com/app/503350/White_Noise_2/))

- **Current USD price**: $3.99 (60% off; list price $9.99), part of a "WEEK LONG DEAL" ending Sept 14, 2026 — https://store.steampowered.com/app/503350/White_Noise_2/
- **Launch/original USD price**: $9.99, confirmed via archived store page 6 days post-launch — http://web.archive.org/web/20170413191531/http://store.steampowered.com/app/503350/
- **Release date**: Apr 7, 2017 — https://store.steampowered.com/app/503350/White_Noise_2/
- **Early Access**: No evidence it launched into Early Access — store page shows a plain "Released" date with no EA labeling; Steam's appdetails API confirms `is_free: false` and no EA flag — https://store.steampowered.com/api/appdetails?appids=503350. Confirmed **NOT free-to-play** (rumor is false): base price is $9.99, not $0.
- **Reviews**: Mostly Positive, 2,859 reviews (2,279 positive / 580 negative) — https://store.steampowered.com/appreviews/503350?json=1&language=all&purchase_type=all
- **Owners**: 200,000 – 500,000 (SteamSpy) — https://steamspy.com/api.php?request=appdetails&appid=503350
- **Price change**: None found — $9.99 base price in 2017 matches today's $9.99 base price; only temporary sales observed. Sources: http://web.archive.org/web/20170413191531/http://store.steampowered.com/app/503350/ , https://store.steampowered.com/app/503350/White_Noise_2/
- **Peak CCU**: NO SOURCE FOUND — SteamCharts returned an HTTP 500 server error for this app on repeated attempts (https://steamcharts.com/app/503350); SteamDB blocked by Cloudflare. Current/live CCU: 1 player via official Steam API — https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid=503350; SteamSpy reports ccu:2 — https://steamspy.com/api.php?request=appdetails&appid=503350

## Barotrauma (Steam AppID [602960](https://store.steampowered.com/app/602960/Barotrauma/))

- **Current USD price**: $34.99 — https://store.steampowered.com/app/602960/Barotrauma/
- **Launch/original USD price**: $29.99 (Early Access launch price, June 2019) — http://web.archive.org/web/20190611053128/https://store.steampowered.com/app/602960
- **Release date (1.0)**: Mar 13, 2023 — https://store.steampowered.com/app/602960/Barotrauma/ , corroborated by https://en.wikipedia.org/wiki/Barotrauma_(video_game)
- **Early Access**: Yes. EA launch date: June 5, 2019 — https://en.wikipedia.org/wiki/Barotrauma_(video_game). EA price: $29.99 — http://web.archive.org/web/20190611053128/https://store.steampowered.com/app/602960. 1.0 exit-EA date: Mar 13, 2023, at $34.99 — http://web.archive.org/web/20230315100938/https://store.steampowered.com/app/602960/ (pre-1.0 snapshot showing $29.99 still: http://web.archive.org/web/20221208031512/https://store.steampowered.com/app/602960).
- **Reviews**: Very Positive, 89,639 reviews (84,273 positive / 5,366 negative) — https://store.steampowered.com/appreviews/602960?json=1&language=all&purchase_type=all
- **Owners**: 2,000,000 – 5,000,000 (SteamSpy) — https://steamspy.com/api.php?request=appdetails&appid=602960
- **Price change**: Confirmed — base price rose from $29.99 (EA, 2019–2022) to $34.99 at/around the Mar 13, 2023 1.0 launch (~17% permanent increase). Sources: http://web.archive.org/web/20221208031512/https://store.steampowered.com/app/602960 vs http://web.archive.org/web/20230315100938/https://store.steampowered.com/app/602960/
- **Peak CCU**: 19,528 all-time — https://steamcharts.com/app/602960. Recent 30-day average: 2,972.41; 24-hour peak: 5,627 — https://steamcharts.com/app/602960. Current live CCU: 2,398 — https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid=602960

## Gang Beasts (Steam AppID [285900](https://store.steampowered.com/app/285900/Gang_Beasts/))

- **Current USD price**: $19.99 — https://store.steampowered.com/app/285900/Gang_Beasts/
- **Launch/original USD price**: $19.99 (Early Access launch price, Aug 2014) — http://web.archive.org/web/20140830201302/http://store.steampowered.com/app/285900/
- **Release date (1.0)**: Dec 12, 2017 — https://store.steampowered.com/app/285900/Gang_Beasts/
- **Early Access**: Yes. EA began August 2014 — https://en.wikipedia.org/wiki/Gang_Beasts (exact day NO SOURCE FOUND; earliest Wayback snapshot Aug 30, 2014). EA price: $19.99 — http://web.archive.org/web/20140830201302/http://store.steampowered.com/app/285900/. 1.0 exit-EA date/price: Dec 12, 2017 / $19.99 — https://store.steampowered.com/app/285900/Gang_Beasts/ , confirmed via http://web.archive.org/web/20171214041635/http://store.steampowered.com/app/285900 (still $19.99).
- **Reviews**: Very Positive, 67,423 reviews (57,677 positive / 9,746 negative) — https://store.steampowered.com/appreviews/285900?json=1&language=all&purchase_type=all
- **Owners**: 2,000,000 – 5,000,000 (SteamSpy) — https://steamspy.com/api.php?request=appdetails&appid=285900
- **Price change**: None found — $19.99 constant from EA launch (Aug 2014) through 1.0 (Dec 2017) through today. Sources: http://web.archive.org/web/20140830201302/http://store.steampowered.com/app/285900/ , http://web.archive.org/web/20171214041635/http://store.steampowered.com/app/285900 , https://store.steampowered.com/app/285900/Gang_Beasts/
- **Peak CCU**: 2,983, reached June 2026 — https://steamcharts.com/app/285900. Recent 30-day average: 418.20; 24-hour peak: 531 — https://steamcharts.com/app/285900. Current live CCU: 466 — https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid=285900

---

## Pummel Party

**INCOMPLETE — background research agent for this game was in progress; result not yet returned at time of this checkpoint write.** Partial cross-reference found in a separate PANOPTICON pricing brief (data/research/pricing-20260909.md, produced by a different agent run, not independently verified by this task): current/list price $14.99, released Sep 20, 2018, Very Positive reviews (~57,829 reviews per that brief's count, which used `language=all&purchase_type=all` — higher than the storefront-displayed count), SteamSpy owners 2,000,000–5,000,000, `early_access: false` in Steam API (i.e. not EA), $14.99 confirmed 3 months post-launch via archive.org snapshot 2018-12-23 (http://web.archive.org/web/20181223225002/https://store.steampowered.com/app/880940/), no price change detected. Treat this paragraph as unverified-by-this-task until the dedicated research pass returns.

## Among Us

**INCOMPLETE — background research agent for this game was in progress; result not yet returned at time of this checkpoint write.** Partial cross-reference found in the separate PANOPTICON pricing brief noted above (not independently verified by this task): current/list price $4.99, released Nov 16, 2018, not Early Access, SteamSpy owners 20,000,000–50,000,000, $4.99 confirmed from a 2020-08-24 archive.org snapshot (http://web.archive.org/web/20200824030911/https://store.steampowered.com/app/945360/); exact 2018 launch-day USD figure was NO SOURCE FOUND in that brief; no base-game price change found (map DLC — not the base game — went $4→$2 on 2020-01-06 then free 2020-06-11). Free-to-play status applies to mobile only, not confirmed independently here. Treat as unverified-by-this-task until the dedicated research pass returns.

## Dead by Daylight

**INCOMPLETE — background research agent for this game was in progress; result not yet returned at time of this checkpoint write.** Partial cross-reference found in the separate PANOPTICON pricing brief noted above (not independently verified by this task): current/list price $19.99, released Jun 14, 2016, not Early Access, SteamSpy owners 20,000,000–50,000,000. That brief found NO clean direct confirmation of the base-game launch price (Steam's age gate blocked 2016–2018 Wayback crawls of the store page) but a pre-launch snapshot (2016-06-09) shows a $17.99 pre-order price, consistent with a $19.99 list price at a conventional 10% pre-purchase discount; ~19 snapshots sampled Oct 2018–Aug 2026 show $19.99 in every clean non-sale capture, i.e. that brief found NO documented base-game price increase, contradicting this task's premise that one exists. Treat as unverified-by-this-task until the dedicated research pass returns.

---

## STRAFTAT (Steam AppID [2386720](https://store.steampowered.com/app/2386720/STRAFTAT/))

- **Current USD price (2026-09-09):** Free to Play — $0.00. https://store.steampowered.com/api/appdetails?appids=2386720 and https://store.steampowered.com/app/2386720/STRAFTAT/
- **Launch/original USD price:** $0.00 (Free to Play) from earliest indexed capture (pre-release, June 2, 2023) through post-launch (Oct 27, 2024): http://web.archive.org/web/20241027104743/https://store.steampowered.com/app/2386720/ — **Note:** the premise that STRAFTAT is "a notably cheap 1v1 arena shooter" (implying a small paid price) appears incorrect — it has been Free to Play at every checkable point, not a low-cost paid title. Sells optional cosmetic DLC ("Maps, Weapons and Hats" $6.99, "Supporter Edition" $9.99) per https://store.steampowered.com/app/2386720/STRAFTAT/
- **Release date (1.0):** October 24, 2024. https://store.steampowered.com/api/appdetails?appids=2386720 (confirmed on http://web.archive.org/web/20241027104743/https://store.steampowered.com/app/2386720/)
- **Early Access:** No — Free to Play from pre-release through 1.0, no EA tag found in any checked archived snapshot (2023-06-02, 2024-08-15, 2024-10-03, 2024-10-27, 2024-12-03). Current storefront also shows no EA designation.
- **Reviews:** Overwhelmingly Positive, 23,286 total reviews (22,380 positive / 906 negative), review_score 9/9 — https://store.steampowered.com/appreviews/2386720?json=1&language=all&purchase_type=all&num_per_page=0
- **Owners:** NO SOURCE FOUND (reliable). SteamSpy's API returns a stale/unreliable "0..20,000" with 0 tracked reviews, contradicting the real 23,286-review count above — not presented as fact. https://steamspy.com/api.php?request=appdetails&appid=2386720
- **Price change:** None found — $0.00 continuously from June 2023 through Aug 2026 archive snapshot and live today. http://web.archive.org/web/20230602123404/https://store.steampowered.com/app/2386720/ , http://web.archive.org/web/20260814112651/https://store.steampowered.com/app/2386720 , https://store.steampowered.com/app/2386720/STRAFTAT/
- **Peak/current CCU:** All-time peak 2,156, July 2025. Currently ~770 (2026-09-09T20:09 UTC), 24h peak 838, 30-day avg 477.16. https://steamcharts.com/app/2386720

## Oh Deer (Steam AppID [2708450](https://store.steampowered.com/app/2708450/Oh_Deer/))

- **Current USD price (2026-09-09):** $9.99, no discount. https://store.steampowered.com/api/appdetails?appids=2708450 and https://store.steampowered.com/app/2708450/Oh_Deer/
- **Launch/original USD price:** Entered Early Access at $9.99 USD (archived snapshot Apr 8, 2024, "Early Access Game" tag present): http://web.archive.org/web/20240408030155/https://store.steampowered.com/app/2708450
- **Release date (1.0 full release):** June 27, 2024. Corroborated by Steam Store API and the developer's own Steam news post "Full Release Update" dated June 27, 2024 (epoch 1719506587), via https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=2708450
- **Early Access history:** Yes. EA launch date: March 15, 2024, confirmed via archived store page captured one day pre-launch (March 14, 2024) showing "Release Date: 15 Mar, 2024" and "Early Access Game" tag: http://web.archive.org/web/20240314094104/https://store.steampowered.com/app/2708450/ . EA price: $9.99 USD (Apr 8, 2024 snapshot). Exited EA June 27, 2024 (EA tag gone by July 2, 2024 snapshot: http://web.archive.org/web/20240702175433/https://store.steampowered.com/app/2708450). 1.0 exit price: $9.99 USD (unchanged) — current live listing still $9.99.
- **Reviews:** Very Positive, 2,584 total reviews (2,192 positive / 392 negative), review_score 8/9, 84.8% positive — https://store.steampowered.com/appreviews/2708450?json=1&language=all&purchase_type=all&num_per_page=0
- **Owners:** 100,000 – 200,000 (SteamSpy) — https://steamspy.com/api.php?request=appdetails&appid=2708450 and https://steamspy.com/app/2708450 (also shows 21,477 Steam followers). No developer-announced sales/player milestone found (full Steam news hub checked — 12 posts, all patch notes; general web search turned up nothing relevant). Beyond the SteamSpy range: NO SOURCE FOUND for any developer-stated sales/player milestone.
- **Price change:** None found. EA price ($9.99, Apr 2024) = 1.0 exit price = current price ($9.99, Sept 2026) across every checked snapshot. http://web.archive.org/web/20240408030155/https://store.steampowered.com/app/2708450 , http://web.archive.org/web/20250815164613/https://store.steampowered.com/app/2708450 , https://store.steampowered.com/app/2708450/Oh_Deer/
- **Peak/current CCU:** All-time peak 1,316, March 2024 (EA launch month). Currently very low — 10 (2026-09-09T20:47 UTC), 24h peak 22, 30-day avg 11.01 (down 5.37% from prior period). https://steamcharts.com/app/2708450

---

## Remaining work

Pummel Party, Among Us, Dead by Daylight still need a dedicated, independently-verified research pass (marked INCOMPLETE above, with unverified cross-reference figures noted for context only). A separate, much larger file already exists in this same directory — `data/research/pricing-20260909.md` — produced by a different agent run for a related but distinct task (a PANOPTICON game pricing-strategy brief with recommendations), which happens to cover the same 11 games plus many more comparables; its figures for the three INCOMPLETE games above were used only as an unverified cross-reference pending this task's own sourcing.
