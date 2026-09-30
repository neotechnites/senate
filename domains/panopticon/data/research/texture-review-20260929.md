# Texture review 2026-09-29 (repo main 041ffec; report only)

Colours = exact distinct RGB in the file. Decision 87 = 64-128 px tile, <=8-10 colours, one file per material. "Live" = a glb material using it is instanced by a live scene (bentham_ring.tscn, forest.tscn, marble.tscn, hub.tscn, ui/main_menu.tscn, player/rifle/speed_powerup scenes). Emissive role for a texture that is also its own emissive (crack_glow, hell_props, ornament, speed_orb, marble_albedo on MarbleGlow) is a self-mask, fine.

| file | px | colours | role | referenced by | live? | verdict |
|---|---|---|---|---|---|---|
| maps/bentham_ring/textures/hell_rock_albedo.png | 256x256 | 10 | albedo | HellRock/HellShade/HellEmber on map_base_s1-5, lips, gate, cover_s2/s4, portal, tower*, hub_base; block/boulder/slab/spire/rock_wall/rock_bars/demon_pad/lava_tile/torch glbs | live | oversize (2x the 128 cap) |
| maps/bentham_ring/textures/hell_rock_emissive.png | 256x256 | 6 | emissive | HellEmber emission on map_base_s1-5, cover_s2/s4, hub_base | live | emissive-not-a-mask, oversize |
| maps/bentham_ring/textures/lava_albedo.png | 256x256 | 3 | albedo (+ own emissive in hub) | LavaSea/LavaRiver map_base_s1-5; hub_base Lava | live | oversize |
| maps/bentham_ring/textures/map_base_lava_emissive.png | 256x256 | 3 | emissive | LavaSea/LavaRiver emission (map_base_s1-5) | live | oversize; duplicate of lava_albedo (mask ok) |
| maps/bentham_ring/textures/crack_glow_albedo.png | 64x32 | 6 | albedo+self emissive | HellGlow/LavaCrack on map_base_s1-5 | live | keep |
| maps/bentham_ring/textures/hell_props_albedo.png | 128x128 | 1309 | albedo+self emissive, 4 quadrants: torch flame, lava tile, pentagram (demon sigil), portal swirl | portal.glb (swirl, live); demon_pad, lava_tile, torch glbs (props never instanced) | portal quadrant only; other 3 dead | keep for swirl only; 3 quadrants dead; colours far over 10 |
| maps/bentham_ring/textures/SHEET_bentham_ring.png/.json | 735x530 | 1336 | edit sheet: crack_glow, hell_props, hell_rock, lava, hell_rock_emissive, map_base_lava_emissive | tools/textures/sheet.py only | not loaded | keep (dev aid); sigil visible in it via hell_props |
| maps/forest/textures/forest_bark_albedo.png | 64x64 | 7 | albedo | forest.glb, trees, bushes, canopy, bars, portal | live | keep |
| maps/forest/textures/forest_dark_albedo.png | 64x64 | 4 | albedo | forest.glb, thorns, hub_base | live | keep |
| maps/forest/textures/forest_fern_albedo.png | 64x64 | 6 | albedo | forest.glb, hub_base | live | keep |
| maps/forest/textures/forest_grass_albedo.png | 64x64 | 5 | albedo | forest.glb, hub_base | live | keep |
| maps/forest/textures/forest_leaf_albedo.png | 64x64 | 7 | albedo | forest.glb, trees, bushes, canopy, portal, hub_base | live | keep |
| maps/forest/textures/forest_ornament_albedo.png | 128x64 | 8 | albedo+self emissive | ForestLamp in forest.glb, portal swirl | live | keep |
| maps/forest/textures/forest_path_albedo.png | 64x64 | 5 | albedo | forest.glb, thorns, hub_base | live | keep |
| maps/forest/textures/forest_rock_albedo.png | 64x64 | 7 | albedo | rock_boulder, rock_outcrop (live); rock_slab (unused) | live | keep |
| maps/forest/textures/SHEET_forest.png/.json | 769x71 | 51 | edit sheet, 8 tiles | sheet.py only | not loaded | keep (dev aid) |
| maps/marble/textures/marble_albedo.png | 320x256 | 59 | albedo (+self emissive on MarbleGlow) | marble.glb, tower, bars, portal, hub_base; arch/column/spikes glbs | live | oversize (320 wide, 59 colours) |
| maps/marble/textures/marble_dark_albedo.png | 192x261 | 17 | albedo | marble.glb, bars, tower, hub_base | live | oversize (odd 192x261) |
| maps/marble/textures/marble_field_albedo.png | 256x256 | 7 | albedo | marble.glb marble_field | live | oversize |
| maps/marble/textures/marble_stone_albedo.png | 128x261 | 6 | albedo | marble.glb, bars, tower, hub_base | live | oversize (261 tall) |
| maps/marble/textures/SHEET_marble.png/.json | 908x268 | 75 | edit sheet, 4 tiles | sheet.py only | not loaded | keep (dev aid) |
| hub/textures/hub_stone_albedo.png | 128x128 | 26 | albedo | hub_base.glb (HubStone) | live | keep (colours over 10) |
| hub/textures/SHEET_hub.png/.json | 128x135 | 28 | edit sheet | sheet.py only | not loaded | keep (dev aid) |
| props/textures/speed_orb_albedo.png | 64x64 | 10 | albedo+self emissive | speed_orb.glb via props/speed_powerup.tscn (parked leftover placed in bentham_ring) | live | keep |
| props/textures/SHEET_props.png/.json | 79x71 | 12 | edit sheet | sheet.py only | not loaded | keep (dev aid) |
| weapons/textures/rifle_hell_albedo.png | 128x128 | 49 | albedo | rifle.glb (RifleWarden) via weapons/rifle.tscn | live | keep (colours over 10) |
| weapons/textures/SHEET_weapons.png/.json | 128x135 | 46 | edit sheet | sheet.py only | not loaded | keep (dev aid) |
| characters/textures/prisoner2_albedo.png | 32x32 | 5 | albedo | prisoner2.glb via player/prisoner_avatar.tscn | live | keep |
| characters/textures/creature_albedo.png | 32x32 | 37 | albedo | creature.glb (no scene/script references it) | no | dead |
| characters/textures/creature2_albedo.png | 32x32 | 36 | albedo | creature2.glb (unreferenced) | no | dead |
| characters/textures/creature3_albedo.png | 32x32 | 36 | albedo | creature3.glb (unreferenced) | no | dead |
| characters/textures/creature4_albedo.png | 32x32 | 30 | albedo | creature4.glb (unreferenced) | no | dead |
| characters/textures/husk_a_albedo.png | 32x32 | 30 | albedo | husk_a.glb (unreferenced) | no | dead |
| characters/textures/husk_b_albedo.png | 32x32 | 28 | albedo | husk_b.glb (unreferenced) | no | dead |
| characters/textures/husk_c_albedo.png | 32x32 | 30 | albedo | husk_c.glb (unreferenced) | no | dead |
| characters/textures/SHEET_characters.png/.json | 620x39 | 230 | edit sheet, 8 tiles (7 dead) | sheet.py only | not loaded | keep (dev aid); 7 of 8 sub-images dead |
| tower/textures/SHEET_tower.png.import | none | n/a | orphan .import, no PNG (sheet.py DEFAULT_HOMES has no tower) | nothing | no | dead (delete the .import and folder) |

## Findings
1. Totals: 29 textures + 6 sheets. In use 21 (one of them, hell_props, only for its portal quadrant), dead 7 (creature x4, husk x3), oversize 8 (hell_rock, hell_rock_emissive, both lavas, four marble), bad emissive 1 (hell_rock_emissive); plus 1 orphan .import.
2. Demon sigil confirmed: the pentagram is the bottom-left quadrant of hell_props_albedo (128 px, 1309 colours, dithered), shown in SHEET_bentham_ring. Its only user, demon_pad.glb, has no live instance (demon_pad.tscn is used by tests/test_lava_crack.gd only); the torch flame and lava-tile quadrants are dead the same way (torch.tscn, lava_tile.tscn not instanced). Only the portal swirl quadrant is live.
3. hell_rock_emissive is unrelated to hell_rock_albedo (luminance correlation -0.01): sparse ember dots on black, wired as emission of every HellEmber rock (map_base s1-5, cover, hub).
4. Lava: map_base_lava_emissive is a same-pattern brighter/desaturated copy of lava_albedo (correlation 0.99, same 3 shapes): a true mask, but a duplicate file. Both are 256 px, 3 colours. The hub uses lava_albedo alone as its own emissive, so one lava file could serve all.
5. hell_rock at 256 px with 10 colours; it is also embedded in tower and hub glbs.
6. Marble breaks the 64-128 tile rule in all four files (320x256/59 colours, 192x261/17, 256, 128x261); hub_stone (26) and rifle (49) are 128 px but over the colour cap.
7. All character tiles except prisoner2 are 28-37 colours (dead anyway); sheets exist only for tools/textures/sheet.py, and Godot still imports them.
8. Unused glbs holding textures alive on paper only: tower2, block, boulder, slab, spire, rock_wall, rock_bars, forest_rock_slab, forest_tree_prop_a/b/c, marble_arch, marble_column(_broken), forest_thorns, marble_spikes(_strip).
