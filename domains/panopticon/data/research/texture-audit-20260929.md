# Texture audit 2026-09-29: usage measured on live geometry

Supersedes texture-review-20260929.md (a reference grep). This one parses every glTF the game reaches
(positions, indices, materials, UVs) and every `.tscn` instance transform, and counts what is actually drawn.

## Method

1. Scene graph walked from the entry points: `project.godot` main scene `ui/main_menu.tscn`; `hub/hub.tscn`
   and `match/match.tscn` (`change_scene_to_file` in main_menu.gd / hub_lobby.gd / multiplayer_screen.gd);
   the three maps from `maps/map_catalog.tres` (MatchController._install_chosen_map swaps the chosen one in
   for match.tscn's Arena, so each map is walked as its own root); `characters/bots/ring_runner.tscn` (runtime
   spawned bots, counted once); plus everything those scenes instance (player → prisoner_avatar → prisoner2.glb,
   rifle.tscn → rifle.glb, watching_eye → eye.glb, portals, lava cracks, speed powerup, forest props...).
   Scenes nothing loads (hub_test, tower_interior_test, movement_playground, shirt_lineup, demon_pad/torch/lava_tile
   props, thorns, spike patches) are not roots and contribute nothing.
2. Every `.glb` reached is parsed in Python (JSON chunk + BIN chunk). Per primitive: material textures by slot
   (baseColor, emissive, normal, ...), triangle count, world-space area with glTF node transforms x every `.tscn`
   instance transform up to the root (each instance counted; `.tscn` Transform3D read as basis rows),
   UV bbox and texel coverage (triangles rasterised into the texture's texel grid, repeat-wrapped).
   No glb in the repo uses KHR_texture_transform. `-colonly`/`-boxcol` nodes and anything under
   `visible = false` are not drawn and are excluded (hidden triangles listed separately).
3. Non-glb texture use checked by hand: `.tscn`/`.tres` materials reference only generated GradientTexture2D
   sub-resources; `lava_wave.gdshader` samples the albedo/emission textures handed over from the glTF
   LavaSea/LavaRiver/LavaCrack materials by `tools/import/mipmap_textures.gd` (counted under those materials);
   `lava_haze`, `mac_lift` sample the screen; UI uses no PNG (icon.svg only); `prisoner_avatar.gd` sets
   `emission_texture = albedo_texture` on Prisoner2Skin at runtime (a self-mask of prisoner2_albedo).
4. Emissive "sampled" = the material has an emissiveTexture and a nonzero emissiveFactor (Godot's importer enables
   emission only then; the wave shader receives `emission_color = BLACK` otherwise).
5. Verdicts (the launcher's rule): DEAD = 0 live triangles; NEAR-DEAD = < 50 triangles or < 2 m2; LIVE otherwise.

Script: kept out of the repo (one-off audit); numbers below are from the commit named in the summary.

## Summary

Measured at repo main e3658a4 (Hell: no emissive maps, one lava texture) plus this audit's deletions.
Texture files in the game (`*/textures/*.png`, sheets excluded): 20 after the audit, 27 before.

- LIVE: 17 (prisoner2, hub_stone, crack_glow, hell_rock, lava, forest x8, marble x4).
- NEAR-DEAD: 3, by the launcher's rule (<50 tris or <2 m2), exact numbers:
  - `maps/bentham_ring/textures/hell_props_albedo.png`: 26 tris, 15.90 m2, one instance (bentham_ring portal
    swirl, PortalGlow albedo+emissive). Only the portal quarter of the file is touched (84.6 % of that quarter);
    the demon_pad, torch and lava_tile quarters have 0 live texels (their props are not instanced by any scene).
  - `props/textures/speed_orb_albedo.png`: 20 tris, 3.45 m2, one instance (bentham_ring SpeedPowerup, albedo+emissive).
  - `weapons/textures/rifle_hell_albedo.png`: 566 tris, 0.37 m2, one instance (match Rifle view model; small
    in world units because it is the first-person gun held at the camera). Near-dead by area only.
  Nothing deleted or resized for these three; no tile redrawn.
- DEAD: 7 -- `characters/textures/{creature,creature2,creature3,creature4,husk_a,husk_b,husk_c}_albedo.png`.
  0 live triangles: their glbs are instanced by no scene, and no live model's build script imports them.
- Hidden geometry (drawn by nothing): tower.glb under bentham_ring (variant=arches) and hub (Rock hidden, Interior/Hollow live),
  marble.tscn's hidden Tower/Rock -- 2336 hell_rock, 1566/1344/2096 marble triangles. Not counted as live.
- Emissive slots still sampled after e3658a4: crack_glow (HellGlow/LavaCrack), forest_ornament (ForestLamp/ForestPortalSwirl),
  hell_props (PortalGlow), speed_orb (SpeedOrb), marble_albedo (MarbleGlow, 18 tris / 16.02 m2 on the marble portal) --
  each a self-mask of its own albedo. hell_rock_emissive and map_base_lava_emissive were removed by e3658a4 (Ryan's ruling,
  not this audit); at ad52b9c they measured 7498 tris / 1570.79 m2 and 15760 tris / 11326.15 m2 respectively.
- Sheets (SHEET_*.png/.json): dev aids for tools/textures/sheet.py, loaded by no scene; every region's verdict is its file's.
  SHEET_characters is repacked to its one remaining tile. The orphan `tower/textures/SHEET_tower.png.import` named in the
  earlier review no longer exists on main.
- Other PNGs outside textures/: docs/sketches/*.png (docs, not game textures). Not touched.
- glbs no live scene reaches (kept; they hold no dead texture): block, boulder, slab, spire, rock_wall, rock_bars, demon_pad,
  lava_tile, torch (bentham_ring); forest_rock_slab, forest_thorns, forest_tree_prop_a/b/c; marble_arch, marble_column(_broken),
  marble_spikes(_strip); tower2; runner.glb (no textures).

## Actions taken (DEAD only)

Commit "Texture audit by live use: drop the seven dead character tiles" on main. Deleted:

- `characters/textures/creature_albedo.png` (+ `.import`), `creature2_albedo.png`, `creature3_albedo.png`, `creature4_albedo.png`,
  `husk_a_albedo.png`, `husk_b_albedo.png`, `husk_c_albedo.png` (each + `.import`).
- `characters/models/creature.glb`, `creature2.glb`, `creature3.glb`, `creature4.glb`, `husk_a.glb`, `husk_b.glb`, `husk_c.glb`
  (each + `.import`): their only purpose was those tiles; no scene instances them (measured), no live build script imports them (grepped).
- `tools/modelling/characters/{creature,creature2,creature3,creature4,husk_a,husk_b,husk_c}_build.py` and their `.contract.json`.
- `characters/textures/SHEET_characters.json` regions for the seven files removed; sheet repacked with
  `tools/textures/sheet.py pack characters` in the same commit (now one tile: prisoner2_albedo, 79x39).

No `.blend` belonged to them (the only blends are tower*.blend, ryans_prisoner.blend, prisoner_joined.blend).
`godot --headless --path . --import`: a first import into an empty `.godot` prints 13 "Condition p_position > length" seek
errors on unrelated wav/png files -- identical count on an untouched ad52b9c checkout, so pre-existing; a second pass prints 0.

## Measurement (generated)

Roots walked: main_menu=res://ui/main_menu.tscn, hub=res://hub/hub.tscn, match=res://match/match.tscn, bentham_ring=res://maps/bentham_ring/bentham_ring.tscn, forest=res://maps/forest/forest.tscn, marble=res://maps/marble/marble.tscn, bots=res://characters/bots/ring_runner.tscn.
match.tscn's Arena is skipped (MatchController._install_chosen_map swaps in the chosen map); the three maps are roots of their own. 'bots' = one ring_runner.tscn (runtime-spawned; multiply by bot count).
Nodes with `visible = false` (and their subtrees) and `-colonly`/`-boxcol` collision nodes are not rendered and are excluded from live counts (hidden counts shown separately).
Emissive 'sampled' = material has an emissiveTexture AND a nonzero emissiveFactor (Godot only lights emission then; lava_wave.gdshader passes emission_color = BLACK otherwise).
UV coverage = % of the file's texels touched by live triangles (repeat-wrapped). KHR_texture_transform: none present in any glb.

## Per texture file and slot

| texture | slot | live tris | live area m2 | hidden tris | scenes (primitives) | materials | glbs (live) | UV bbox | texel coverage | emissive sampled? | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| characters/textures/prisoner2_albedo.png | albedo | 1602 | 5.27 | 0 | bots(2), hub(2), match(2) | Prisoner2Skin, Shirt | characters/models/prisoner2.glb | u 0.02..0.98 v 0.05..0.98 | 57.8% | n/a | LIVE |
| hub/textures/hub_stone_albedo.png | albedo | 9980 | 15959.66 | 0 | hub(1) | HubStone | hub/models/hub_base.glb | u 0.01..0.99 v 0.01..0.99 | 82.5% | n/a | LIVE |
| maps/bentham_ring/textures/crack_glow_albedo.png | albedo | 9782 | 19357.22 | 0 | bentham_ring(7) | HellGlow, LavaCrack | maps/bentham_ring/models/map_base_s1.glb, maps/bentham_ring/models/map_base_s2.glb, maps/bentham_ring/models/map_base_s3.glb, maps/bentham_ring/models/map_base_s4.glb, maps/bentham_ring/models/map_base_s5.glb | u 0.02..0.98 v 0.05..0.95 | 89.7% | n/a | LIVE |
| maps/bentham_ring/textures/hell_props_albedo.png | albedo | 26 | 15.90 | 0 | bentham_ring(1) | PortalGlow | maps/bentham_ring/models/portal.glb | u 0.51..0.99 v 0.51..0.99 | 21.1% | n/a | NEAR-DEAD (slot) |
| maps/bentham_ring/textures/hell_rock_albedo.png | albedo | 83225 | 209466.99 | 2336 | bentham_ring(33), hub(3), main_menu(1) | HellEmber, HellRock, HellShade | hub/models/hub_base.glb, maps/bentham_ring/models/map_base_cover_s2.glb, maps/bentham_ring/models/map_base_cover_s4.glb, maps/bentham_ring/models/map_base_gate.glb, maps/bentham_ring/models/map_base_lip013.glb, maps/bentham_ring/models/map_base_lip066.glb, maps/bentham_ring/models/map_base_lip139.glb, maps/bentham_ring/models/map_base_lip204.glb, maps/bentham_ring/models/map_base_lip286.glb, maps/bentham_ring/models/map_base_s1.glb, maps/bentham_ring/models/map_base_s2.glb, maps/bentham_ring/models/map_base_s3.glb, maps/bentham_ring/models/map_base_s4.glb, maps/bentham_ring/models/map_base_s5.glb, maps/bentham_ring/models/portal.glb, tower/models/tower.glb, tower/models/tower_arches.glb, tower/models/tower_hollow.glb, tower/models/tower_interior.glb | u -16.24..15.76 v -24.87..1.86 | 100.0% | n/a | LIVE |
| maps/bentham_ring/textures/lava_albedo.png | albedo | 15800 | 11335.74 | 0 | bentham_ring(8), hub(1) | Lava, LavaRiver, LavaSea | hub/models/hub_base.glb, maps/bentham_ring/models/map_base_s1.glb, maps/bentham_ring/models/map_base_s2.glb, maps/bentham_ring/models/map_base_s3.glb, maps/bentham_ring/models/map_base_s4.glb, maps/bentham_ring/models/map_base_s5.glb | u -24.27..11.00 v -10.44..12.39 | 100.0% | n/a | LIVE |
| maps/forest/textures/forest_bark_albedo.png | albedo | 131045 | 13046.13 | 0 | forest(20), hub(1) | ForestBark, ForestPortalBark | hub/models/hub_base.glb, maps/forest/models/forest.glb, maps/forest/models/forest_bars.glb, maps/forest/models/forest_bush_low.glb, maps/forest/models/forest_bush_tall.glb, maps/forest/models/forest_canopy.glb, maps/forest/models/forest_portal.glb, maps/forest/models/forest_tree.glb | u -57.02..57.50 v -17.70..18.99 | 100.0% | n/a | LIVE |
| maps/forest/textures/forest_dark_albedo.png | albedo | 54762 | 16670.63 | 0 | forest(1), hub(1) | ForestDark | hub/models/hub_base.glb, maps/forest/models/forest.glb | u -54.62..57.50 v -17.78..4.45 | 100.0% | n/a | LIVE |
| maps/forest/textures/forest_fern_albedo.png | albedo | 10704 | 126.68 | 0 | forest(1), hub(1) | ForestFern | hub/models/hub_base.glb, maps/forest/models/forest.glb | u -53.92..55.90 v -17.00..1.00 | 83.5% | n/a | LIVE |
| maps/forest/textures/forest_grass_albedo.png | albedo | 9486 | 3266.76 | 0 | forest(1), hub(1) | ForestGrass | hub/models/hub_base.glb, maps/forest/models/forest.glb | u -57.50..57.50 v -17.72..-6.18 | 100.0% | n/a | LIVE |
| maps/forest/textures/forest_leaf_albedo.png | albedo | 96199 | 82476.65 | 0 | forest(20), hub(1) | ForestLeaf, ForestPortalLeaf | hub/models/hub_base.glb, maps/forest/models/forest.glb, maps/forest/models/forest_bars.glb, maps/forest/models/forest_bush_low.glb, maps/forest/models/forest_bush_tall.glb, maps/forest/models/forest_canopy.glb, maps/forest/models/forest_portal.glb, maps/forest/models/forest_tree.glb | u -57.50..57.50 v -17.54..19.43 | 100.0% | n/a | LIVE |
| maps/forest/textures/forest_ornament_albedo.png | albedo | 5148 | 4018.38 | 0 | forest(2) | ForestLamp, ForestPortalSwirl | maps/forest/models/forest.glb, maps/forest/models/forest_portal.glb | u 0.00..1.00 v 0.01..0.99 | 97.7% | n/a | LIVE |
| maps/forest/textures/forest_ornament_albedo.png | emissive | 5148 | 4018.38 | 0 | forest(2) | ForestLamp, ForestPortalSwirl | maps/forest/models/forest.glb, maps/forest/models/forest_portal.glb | u 0.00..1.00 v 0.01..0.99 | 97.7% | yes (ForestLamp,ForestPortalSwirl) | LIVE |
| maps/forest/textures/forest_path_albedo.png | albedo | 10170 | 9762.14 | 0 | forest(1), hub(1) | ForestPath | hub/models/hub_base.glb, maps/forest/models/forest.glb | u -51.00..51.00 v -15.72..4.45 | 100.0% | n/a | LIVE |
| maps/forest/textures/forest_rock_albedo.png | albedo | 2156 | 154.74 | 0 | forest(15) | ForestGraniteRock | maps/forest/models/forest_rock_boulder.glb, maps/forest/models/forest_rock_outcrop.glb | u -0.40..0.36 v 0.59..1.30 | 37.1% | n/a | LIVE |
| maps/marble/textures/marble_albedo.png | albedo | 12044 | 21397.37 | 1566 | hub(1), marble(15) | Marble, MarbleGlow, marble_band, marble_bars_band, marble_bars_column, marble_column, marble_dome, marble_floor, marble_frieze, marble_spike, marble_tower_band, marble_tower_coffer, marble_tower_column, marble_tower_floor, marble_tower_medallion | hub/models/hub_base.glb, maps/marble/models/marble.glb, maps/marble/models/marble_bars.glb, maps/marble/models/marble_portal.glb, maps/marble/models/marble_tower.glb | u 0.00..1.00 v 0.01..1.00 | 65.7% | n/a | LIVE |
| maps/marble/textures/marble_albedo.png | emissive | 18 | 16.02 | 0 | marble(1) | MarbleGlow | maps/marble/models/marble_portal.glb | u 0.41..0.59 v 0.01..0.24 | 4.2% | yes (MarbleGlow) | NEAR-DEAD (slot) |
| maps/marble/textures/marble_dark_albedo.png | albedo | 18858 | 13772.66 | 1344 | hub(1), marble(4) | MarbleDark, marble_bars_iron, marble_cellin, marble_iron, marble_tower_iron | hub/models/hub_base.glb, maps/marble/models/marble.glb, maps/marble/models/marble_bars.glb, maps/marble/models/marble_tower.glb | u 0.01..1.00 v -3.54..1.01 | 58.6% | n/a | LIVE |
| maps/marble/textures/marble_field_albedo.png | albedo | 7104 | 11049.71 | 0 | marble(1) | marble_field | maps/marble/models/marble.glb | u -4.69..4.69 v -3.69..5.69 | 100.0% | n/a | LIVE |
| maps/marble/textures/marble_stone_albedo.png | albedo | 43812 | 49390.05 | 2096 | hub(4), marble(16) | Marble_marble, Marble_marble2, Marble_plinth, Marble_shade, marble_bars_marble, marble_bars_marble2, marble_bars_plinth, marble_bars_shade, marble_marble, marble_plinth, marble_shade, marble_tower_dome, marble_tower_marble2, marble_tower_plinth, marble_tower_shade, marble_tower_stone | hub/models/hub_base.glb, maps/marble/models/marble.glb, maps/marble/models/marble_bars.glb, maps/marble/models/marble_portal.glb, maps/marble/models/marble_tower.glb | u -32.53..32.53 v -7.16..1.04 | 100.0% | n/a | LIVE |
| props/textures/speed_orb_albedo.png | albedo | 20 | 3.45 | 0 | bentham_ring(1) | SpeedOrb | props/models/speed_orb.glb | u 0.03..0.96 v 0.03..0.94 | 67.4% | n/a | NEAR-DEAD (slot) |
| props/textures/speed_orb_albedo.png | emissive | 20 | 3.45 | 0 | bentham_ring(1) | SpeedOrb | props/models/speed_orb.glb | u 0.03..0.96 v 0.03..0.94 | 67.4% | yes (SpeedOrb) | NEAR-DEAD (slot) |
| weapons/textures/rifle_hell_albedo.png | albedo | 566 | 0.37 | 0 | match(1) | RifleWarden | weapons/models/rifle.glb | u 0.01..0.99 v 0.01..0.98 | 69.2% | n/a | NEAR-DEAD (slot) |

## File verdicts

Triangles counted once per file (a triangle whose material uses the file as albedo and emissive is one triangle).

| texture | live tris | live area m2 | hidden tris | verdict |
|---|---|---|---|---|
| characters/textures/prisoner2_albedo.png | 1602 | 5.27 | 0 | **LIVE** |
| hub/textures/hub_stone_albedo.png | 9980 | 15959.66 | 0 | **LIVE** |
| maps/bentham_ring/textures/crack_glow_albedo.png | 9782 | 19357.22 | 0 | **LIVE** |
| maps/bentham_ring/textures/hell_rock_albedo.png | 83225 | 209466.99 | 2336 | **LIVE** |
| maps/bentham_ring/textures/lava_albedo.png | 15800 | 11335.74 | 0 | **LIVE** |
| maps/forest/textures/forest_bark_albedo.png | 131045 | 13046.13 | 0 | **LIVE** |
| maps/forest/textures/forest_dark_albedo.png | 54762 | 16670.63 | 0 | **LIVE** |
| maps/forest/textures/forest_fern_albedo.png | 10704 | 126.68 | 0 | **LIVE** |
| maps/forest/textures/forest_grass_albedo.png | 9486 | 3266.76 | 0 | **LIVE** |
| maps/forest/textures/forest_leaf_albedo.png | 96199 | 82476.65 | 0 | **LIVE** |
| maps/forest/textures/forest_ornament_albedo.png | 5148 | 4018.38 | 0 | **LIVE** |
| maps/forest/textures/forest_path_albedo.png | 10170 | 9762.14 | 0 | **LIVE** |
| maps/forest/textures/forest_rock_albedo.png | 2156 | 154.74 | 0 | **LIVE** |
| maps/marble/textures/marble_albedo.png | 12044 | 21397.37 | 1566 | **LIVE** |
| maps/marble/textures/marble_dark_albedo.png | 18858 | 13772.66 | 1344 | **LIVE** |
| maps/marble/textures/marble_field_albedo.png | 7104 | 11049.71 | 0 | **LIVE** |
| maps/marble/textures/marble_stone_albedo.png | 43812 | 49390.05 | 2096 | **LIVE** |
| maps/bentham_ring/textures/hell_props_albedo.png | 26 | 15.90 | 0 | **NEAR-DEAD** |
| props/textures/speed_orb_albedo.png | 20 | 3.45 | 0 | **NEAR-DEAD** |
| weapons/textures/rifle_hell_albedo.png | 566 | 0.37 | 0 | **NEAR-DEAD** |

## Sheet regions (SHEET_*.json)

Sheets are dev aids packed by tools/textures/sheet.py from the per-file PNGs; no scene loads a SHEET_*.png. A region's verdict is its file's verdict.

| sheet | region file | rect | verdict |
|---|---|---|---|
| maps/forest/textures/SHEET_forest.json | forest_bark_albedo.png | [0, 7, 64, 64] | LIVE |
| maps/forest/textures/SHEET_forest.json | forest_dark_albedo.png | [91, 7, 64, 64] | LIVE |
| maps/forest/textures/SHEET_forest.json | forest_fern_albedo.png | [182, 7, 64, 64] | LIVE |
| maps/forest/textures/SHEET_forest.json | forest_grass_albedo.png | [273, 7, 64, 64] | LIVE |
| maps/forest/textures/SHEET_forest.json | forest_leaf_albedo.png | [368, 7, 64, 64] | LIVE |
| maps/forest/textures/SHEET_forest.json | forest_ornament_albedo.png | [459, 7, 128, 64] | LIVE |
| maps/forest/textures/SHEET_forest.json | forest_path_albedo.png | [591, 7, 64, 64] | LIVE |
| maps/forest/textures/SHEET_forest.json | forest_rock_albedo.png | [682, 7, 64, 64] | LIVE |
| maps/marble/textures/SHEET_marble.json | marble_albedo.png | [0, 7, 320, 256] | LIVE |
| maps/marble/textures/SHEET_marble.json | marble_dark_albedo.png | [324, 7, 192, 261] | LIVE |
| maps/marble/textures/SHEET_marble.json | marble_field_albedo.png | [520, 7, 256, 256] | LIVE |
| maps/marble/textures/SHEET_marble.json | marble_stone_albedo.png | [780, 7, 128, 261] | LIVE |
| maps/bentham_ring/textures/SHEET_bentham_ring.json | crack_glow_albedo.png | [0, 7, 64, 32] | LIVE |
| maps/bentham_ring/textures/SHEET_bentham_ring.json | hell_props_albedo.png | [87, 7, 128, 128] | NEAR-DEAD |
| maps/bentham_ring/textures/SHEET_bentham_ring.json | hell_rock_albedo.png | [219, 7, 256, 256] | LIVE |
| maps/bentham_ring/textures/SHEET_bentham_ring.json | lava_albedo.png | [479, 7, 256, 256] | LIVE |
| props/textures/SHEET_props.json | speed_orb_albedo.png | [0, 7, 64, 64] | NEAR-DEAD |
| weapons/textures/SHEET_weapons.json | rifle_hell_albedo.png | [0, 7, 128, 128] | NEAR-DEAD |
| characters/textures/SHEET_characters.json | prisoner2_albedo.png | [0, 7, 32, 32] | LIVE |
| hub/textures/SHEET_hub.json | hub_stone_albedo.png | [0, 7, 128, 128] | LIVE |

## Sub-regions within one file (hell_props_albedo quarters, PROPS_QUARTER in tools/modelling/lib/texel.py)

| quarter (Blender u0,v0) | slot | texels touched | coverage of quarter |
|---|---|---|---|
| demon_pad (0.0,0.0) | albedo | 0 / 4096 | 0.0% |
| portal (0.5,0.0) | albedo | 3464 / 4096 | 84.6% |
| torch (0.0,0.5) | albedo | 0 / 4096 | 0.0% |
| lava_tile (0.5,0.5) | albedo | 0 / 4096 | 0.0% |

## glb instances reached

| glb | scene | live instances | hidden instances |
|---|---|---|---|
| characters/models/prisoner2.glb | bots | 1 | 0 |
| characters/models/prisoner2.glb | hub | 1 | 0 |
| characters/models/prisoner2.glb | match | 1 | 0 |
| hub/models/hub_base.glb | hub | 1 | 0 |
| maps/bentham_ring/models/map_base_cover_s2.glb | bentham_ring | 1 | 0 |
| maps/bentham_ring/models/map_base_cover_s4.glb | bentham_ring | 1 | 0 |
| maps/bentham_ring/models/map_base_gate.glb | bentham_ring | 1 | 0 |
| maps/bentham_ring/models/map_base_lip013.glb | bentham_ring | 1 | 0 |
| maps/bentham_ring/models/map_base_lip066.glb | bentham_ring | 1 | 0 |
| maps/bentham_ring/models/map_base_lip139.glb | bentham_ring | 1 | 0 |
| maps/bentham_ring/models/map_base_lip204.glb | bentham_ring | 1 | 0 |
| maps/bentham_ring/models/map_base_lip286.glb | bentham_ring | 1 | 0 |
| maps/bentham_ring/models/map_base_s1.glb | bentham_ring | 1 | 0 |
| maps/bentham_ring/models/map_base_s2.glb | bentham_ring | 1 | 0 |
| maps/bentham_ring/models/map_base_s3.glb | bentham_ring | 1 | 0 |
| maps/bentham_ring/models/map_base_s4.glb | bentham_ring | 1 | 0 |
| maps/bentham_ring/models/map_base_s5.glb | bentham_ring | 1 | 0 |
| maps/bentham_ring/models/portal.glb | bentham_ring | 1 | 0 |
| maps/forest/models/forest.glb | forest | 1 | 0 |
| maps/forest/models/forest_bars.glb | forest | 1 | 0 |
| maps/forest/models/forest_bush_low.glb | forest | 11 | 0 |
| maps/forest/models/forest_bush_tall.glb | forest | 4 | 0 |
| maps/forest/models/forest_canopy.glb | forest | 1 | 0 |
| maps/forest/models/forest_portal.glb | forest | 1 | 0 |
| maps/forest/models/forest_rock_boulder.glb | forest | 14 | 0 |
| maps/forest/models/forest_rock_outcrop.glb | forest | 1 | 0 |
| maps/forest/models/forest_tree.glb | forest | 1 | 0 |
| maps/marble/models/marble.glb | marble | 1 | 0 |
| maps/marble/models/marble_bars.glb | marble | 1 | 0 |
| maps/marble/models/marble_portal.glb | marble | 1 | 0 |
| maps/marble/models/marble_tower.glb | marble | 1 | 1 |
| props/models/speed_orb.glb | bentham_ring | 1 | 0 |
| tower/models/eye.glb | main_menu | 1 | 0 |
| tower/models/tower.glb | bentham_ring | 0 | 1 |
| tower/models/tower.glb | hub | 0 | 1 |
| tower/models/tower.glb | main_menu | 1 | 0 |
| tower/models/tower_arches.glb | bentham_ring | 1 | 0 |
| tower/models/tower_hollow.glb | hub | 1 | 0 |
| tower/models/tower_interior.glb | hub | 1 | 0 |
| weapons/models/rifle.glb | match | 1 | 0 |

glbs not reached by any live scene: maps/bentham_ring/models/block.glb, maps/bentham_ring/models/boulder.glb, maps/bentham_ring/models/demon_pad.glb, maps/bentham_ring/models/lava_tile.glb, maps/bentham_ring/models/rock_bars.glb, maps/bentham_ring/models/rock_wall.glb, maps/bentham_ring/models/slab.glb, maps/bentham_ring/models/spire.glb, maps/bentham_ring/models/torch.glb, maps/forest/models/forest_rock_slab.glb, maps/forest/models/forest_thorns.glb, maps/forest/models/forest_tree_prop_a.glb, maps/forest/models/forest_tree_prop_b.glb, maps/forest/models/forest_tree_prop_c.glb, maps/marble/models/marble_arch.glb, maps/marble/models/marble_column.glb, maps/marble/models/marble_column_broken.glb, maps/marble/models/marble_spikes.glb, maps/marble/models/marble_spikes_strip.glb, tower/models/tower2.glb

## Other PNGs (not in a textures/ dir; not game textures)

- docs/sketches/tower outside.png
- docs/sketches/tower_good_bad.png

## Textures used outside glbs

- .tscn/.tres materials: only generated GradientTexture2D sub-resources (lava_crack.tscn, portal_motes.tscn); no PNG.
- Shaders: lava_wave.gdshader samples albedo_texture/emission_texture handed over from the glTF LavaSea/LavaRiver/LavaCrack materials (counted above under those materials); lava_haze and mac_lift sample the screen only; scope_vignette has no sampler.
- UI: no PNG; icon.svg is the app icon.
- Runtime: prisoner_avatar.gd sets emission_texture = albedo_texture on Prisoner2Skin (self-mask of prisoner2_albedo).
