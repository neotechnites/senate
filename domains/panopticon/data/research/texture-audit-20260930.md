# Texture audit 2026-09-30: live geometry, zero-texel ruling applied

Supersedes texture-audit-20260929.md. Same method, re-run on the current tree (main 62af3f2: hell back at
ad52b9c minus the rock emissive, forest back at d0af996 with its 16 texture files), then Ryan's ruling applied:
anything with zero live texels is deleted, whole files and partial regions alike, and a sheet shows only the
albedo tiles Ryan draws.

## Method

1. Scene graph walked from the entry points: `project.godot` main scene `ui/main_menu.tscn`; `hub/hub.tscn` and
   `match/match.tscn` (`change_scene_to_file` in main_menu.gd / hub_lobby.gd / multiplayer_screen.gd); the three
   maps from `maps/map_catalog.tres` as roots of their own (match.tscn's Arena is swapped for the chosen map);
   `characters/bots/ring_runner.tscn` once. Inherited scenes (prisoner_avatar.tscn = prisoner2.glb,
   ring_runner.tscn = player.tscn), nodes added under an instance (match's Rifle under Player/Head) and property
   overrides on instanced children (`visible = false` on a glb node) are followed. `tower_variant.gd` hides
   `Rock` (variant 1, the default) or `RockArches` (variant 0). Hub map wedges hold the map scenes as an exported
   property, not as instances: nothing of the maps is drawn in the hub.
2. Every `.glb` reached is parsed (JSON + BIN). Per primitive: material textures by slot (baseColor, emissive,
   normal, occlusion, metallicRoughness), triangle count, world area through the glTF node chain and every `.tscn`
   transform up to the root (`Transform3D` read as basis rows; `position`/`rotation`(YXZ)/`scale` otherwise),
   UV bbox, and texel coverage (each triangle rasterised into the texture's texel grid, repeat-wrapped, with
   KHR_texture_transform applied when present; no glb in the repo uses it). `-colonly`/`-boxcol` nodes and
   anything under `visible = false` are not drawn: listed as hidden, not live.
3. Non-glb texture use checked by hand: `.tscn`/`.tres` materials reference only generated GradientTexture2D
   sub-resources; `lava_wave.gdshader` samples the albedo/emission textures handed over from the LavaSea/LavaRiver/
   LavaCrack materials by `tools/import/mipmap_textures.gd` (counted under those materials); `lava_haze` and
   `mac_lift` sample the screen; UI uses no PNG (icon.svg); `prisoner_avatar.gd` sets `emission_texture =
   albedo_texture` on Prisoner2Skin (a self-mask of prisoner2_albedo).
4. Emissive "sampled" = the material has an emissiveTexture and a nonzero emissiveFactor.
5. Verdict: DEAD = zero live texels (file, sheet tile, or named region); LIVE otherwise. Nothing is "near-dead"
   any more: size in metres is not a criterion.
6. Sub-tile regions: every file is also read in 4x4 blocks, hell_props_albedo by its PROPS_QUARTER quarters and
   forest_atlas_albedo by forest_tree_build.py's 12 named ZONES.

Script kept out of the repo (one-off). Numbers cross-checked against the 2026-09-29 audit on the files both
trees share (prisoner2 1602 tris / 5.27 m2, hell_rock 83225 / 209466.99, lava 15800 / 11335.74, speed_orb 20 /
3.45, rifle 566 / 0.37): identical.

## Summary

Texture files (`*/textures/*.png`, sheets excluded): 30 before, 30 after. None has zero live texels.

- Whole files: all 30 LIVE. The three near-dead files of the first audit (hell_props 26 tris, speed_orb 20 tris,
  rifle 566 tris) are live by the ruling: they have texels on screen.
- Dead regions found: `maps/bentham_ring/textures/hell_props_albedo.png` -- the demon_pad, torch and lava_tile
  quarters, 0 / 4096 texels each; only the portal quarter is touched (3501 / 4096). Their props (demon_pad.glb,
  torch.glb, lava_tile.glb via demon_pad.tscn / torch.tscn / lava_tile.tscn) are instanced by no scene the game
  loads. **Cropped and deleted (below).**
- Sheet tiles: every albedo tile on every sheet is LIVE. Two emissive tiles were on sheets
  (`map_base_lava_emissive.png` on SHEET_bentham_ring, `forest_lamp_emissive.png` on SHEET_forest): build output,
  not drawn by Ryan. **Off the sheets, kept as files** (both are live: the lava's and the lamps' emission).
- Sub-tile dead areas inside live tiles, reported and NOT acted on (interpretation: the ruling's "region" is a
  sheet tile or a named quarter, and the brief forbids resizing or redrawing a live tile; cropping these would
  re-lay-out a shared atlas or change a world-tiled texture's repeat and rebuild every glb on it):
  - `forest_atlas_albedo.png` (256x256, shared by forest_tree, forest_bush_low/tall, forest_canopy,
    forest_portal): 7 of its 12 named zones have 0 live texels -- grass, verge, path, cell, earth, fern, edge
    (the map mesh draws those classes from their own files instead). Live zones: leaf, shade, sun, bark, root.
    30951 / 65536 texels live. Packing the five live zones into a smaller atlas means new ZONES in
    forest_tree_build.py and five glb rebuilds; `forest_thorns.glb` (unreached) also reads this atlas.
  - World-tiled files whose geometry only spans part of the v range: forest_edge (bottom quarter 0 texels,
    34.7% live), forest_verge (one 64 px row 0, 28.9% live), forest_fern 44.2%, marble_albedo (two 80x64 corners
    0, 66.1% live), marble_dark (one 48x65 block 0, 59.0%), rifle_hell (two 32x32 blocks 0, 69.8%).
- Hidden geometry (drawn by nothing): tower.glb under bentham_ring and hub (Rock, variant=arches) and
  marble.tscn's hidden Tower/Rock: 2336 hell_rock, 1566 / 1344 / 2096 marble triangles. Not live.
- Emissive slots sampled: crack_glow (HellGlow, LavaCrack), hell_props (PortalGlow), lava_albedo (hub's Lava,
  self-mask), map_base_lava_emissive (LavaSea, LavaRiver), forest_lamp_emissive (forest_lamp),
  forest_portal_swirl (ForestPortalSwirl), marble_albedo (MarbleGlow), speed_orb (SpeedOrb).
- glbs no live scene reaches, kept because every texture they hold is live elsewhere: block, boulder, slab,
  spire, rock_wall, rock_bars (hell_rock); forest_rock_slab (forest_rock); forest_thorns, forest_tree_prop_a/b/c
  (forest_atlas); marble_arch, marble_column(_broken), marble_spikes(_strip) (marble, marble_stone); tower2
  (hell_rock); runner.glb (no textures).

## Actions taken

Commit `9cee4f2` on main (rebased onto 0b7bf92, a match_controller.gd change with no texture effect) ("Texture audit 2: hell_props cropped to the portal swirl, dead pad/torch/lava tile
props gone, sheets albedo-only"):

- `maps/bentham_ring/textures/hell_props_albedo.png`: cropped 128x128 -> 64x64, the portal-swirl quarter
  (image rect 64,64..128,128), pixels untouched. `portal.glb` rebuilt with `tools/modelling/model build portal`
  (`tools/modelling/lib/texel.py`: PROPS_QUARTER gone, `props_image(painted, zone)` and `retile(glow=(zone,
  material))` map the swirl zone onto the whole file; `portal_build.py` calls updated). PortalGlow now reads
  u 0.02..0.98 v 0.03..0.98 of the file: 3501 / 4096 texels, 26 tris, 15.90 m2, one instance in bentham_ring.
- Deleted: `maps/bentham_ring/models/demon_pad.glb`, `torch.glb`, `lava_tile.glb` (+ `.import`),
  `maps/bentham_ring/props/demon_pad.tscn`, `torch.tscn`, `lava_tile.tscn`,
  `tools/modelling/maps/bentham_ring/{demon_pad,torch,lava_tile}_build.py` and `.contract.json`. No scene, script
  or uid references them. `tests/test_lava_crack.gd` tests the crack alone (its comment named demon_pad.tscn as
  the footprint's origin): comment shortened, test kept. `scripts/match/trap_volume.gd`'s `feet_only` doc no
  longer names lava_tile.tscn.
- `tools/textures/sheet.py` packs `*_albedo.png` only (the emissive block is gone). `SHEET_bentham_ring` repacked:
  crack_glow, hell_props (64x64), hell_rock, lava (690x263, was 735x530). `SHEET_forest` repacked: 15 albedo
  tiles (3631x263, was 3631x530). `sheet.py unpack` on both: 0 written, 4 + 15 unchanged.
- `godot --headless --path . --import` twice on the Mac (fresh `.godot`): 13 pre-existing "p_position > length"
  seek errors on the first pass (same count as the untouched tree), 0 on the second; no `.import` rewritten.
- Nothing resized, recoloured or redrawn; no light touched. The remaining file count per home is in the last
  section.

## Measurement after the commit (generated)

Roots walked: main_menu=res://ui/main_menu.tscn, hub=res://hub/hub.tscn, match=res://match/match.tscn,
bentham_ring=res://maps/bentham_ring/bentham_ring.tscn, forest=res://maps/forest/forest.tscn,
marble=res://maps/marble/marble.tscn, bots=res://characters/bots/ring_runner.tscn.

### Per texture file and slot

| texture | slot | live tris | live area m2 | hidden tris | scenes (primitives) | materials | glbs (live) | UV bbox | texels touched | coverage | emissive sampled? | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| characters/textures/prisoner2_albedo.png | albedo | 1602 | 5.27 | 0 | bots(2), hub(2), match(2) | Prisoner2Skin, Shirt | characters/models/prisoner2.glb | u 0.02..0.98 v 0.05..0.98 | 594 / 1024 | 58.0% | n/a | LIVE |
| hub/textures/hub_stone_albedo.png | albedo | 9980 | 15959.66 | 0 | hub(1) | HubStone | hub/models/hub_base.glb | u 0.01..0.99 v 0.01..0.99 | 14862 / 16384 | 90.7% | n/a | LIVE |
| maps/bentham_ring/textures/crack_glow_albedo.png | albedo | 9782 | 19357.22 | 0 | bentham_ring(7) | HellGlow, LavaCrack | maps/bentham_ring/models/map_base_s1.glb, maps/bentham_ring/models/map_base_s2.glb, maps/bentham_ring/models/map_base_s3.glb, maps/bentham_ring/models/map_base_s4.glb, maps/bentham_ring/models/map_base_s5.glb | u 0.02..0.98 v 0.05..0.95 | 1860 / 2048 | 90.8% | n/a | LIVE |
| maps/bentham_ring/textures/crack_glow_albedo.png | emissive | 9782 | 19357.22 | 0 | bentham_ring(7) | HellGlow, LavaCrack | maps/bentham_ring/models/map_base_s1.glb, maps/bentham_ring/models/map_base_s2.glb, maps/bentham_ring/models/map_base_s3.glb, maps/bentham_ring/models/map_base_s4.glb, maps/bentham_ring/models/map_base_s5.glb | u 0.02..0.98 v 0.05..0.95 | 1860 / 2048 | 90.8% | yes (HellGlow,LavaCrack) | LIVE |
| maps/bentham_ring/textures/hell_props_albedo.png | albedo | 26 | 15.90 | 0 | bentham_ring(1) | PortalGlow | maps/bentham_ring/models/portal.glb | u 0.02..0.98 v 0.03..0.98 | 3501 / 4096 | 85.5% | n/a | LIVE |
| maps/bentham_ring/textures/hell_props_albedo.png | emissive | 26 | 15.90 | 0 | bentham_ring(1) | PortalGlow | maps/bentham_ring/models/portal.glb | u 0.02..0.98 v 0.03..0.98 | 3501 / 4096 | 85.5% | yes (PortalGlow) | LIVE |
| maps/bentham_ring/textures/hell_rock_albedo.png | albedo | 83225 | 209466.99 | 2336 | bentham_ring(33), hub(3), main_menu(1) | HellEmber, HellRock, HellRock.001, HellShade, HellShade.001 | hub/models/hub_base.glb, maps/bentham_ring/models/map_base_cover_s2.glb, maps/bentham_ring/models/map_base_cover_s4.glb, maps/bentham_ring/models/map_base_gate.glb, maps/bentham_ring/models/map_base_lip013.glb, maps/bentham_ring/models/map_base_lip066.glb, maps/bentham_ring/models/map_base_lip139.glb, maps/bentham_ring/models/map_base_lip204.glb, maps/bentham_ring/models/map_base_lip286.glb, maps/bentham_ring/models/map_base_s1.glb, maps/bentham_ring/models/map_base_s2.glb, maps/bentham_ring/models/map_base_s3.glb, maps/bentham_ring/models/map_base_s4.glb, maps/bentham_ring/models/map_base_s5.glb, maps/bentham_ring/models/portal.glb, tower/models/tower.glb, tower/models/tower_arches.glb, tower/models/tower_hollow.glb, tower/models/tower_interior.glb | u -16.24..15.76 v -24.87..1.86 | 65536 / 65536 | 100.0% | n/a | LIVE |
| maps/bentham_ring/textures/lava_albedo.png | albedo | 15800 | 11335.74 | 0 | bentham_ring(8), hub(1) | Lava, LavaRiver, LavaSea | hub/models/hub_base.glb, maps/bentham_ring/models/map_base_s1.glb, maps/bentham_ring/models/map_base_s2.glb, maps/bentham_ring/models/map_base_s3.glb, maps/bentham_ring/models/map_base_s4.glb, maps/bentham_ring/models/map_base_s5.glb | u -24.27..11.00 v -10.44..12.39 | 65536 / 65536 | 100.0% | n/a | LIVE |
| maps/bentham_ring/textures/lava_albedo.png | emissive | 40 | 9.59 | 0 | hub(1) | Lava | hub/models/hub_base.glb | u 0.29..0.71 v 0.34..0.66 | 6373 / 65536 | 9.7% | yes (Lava) | LIVE |
| maps/bentham_ring/textures/map_base_lava_emissive.png | emissive | 15760 | 11326.15 | 0 | bentham_ring(8) | LavaRiver, LavaSea | maps/bentham_ring/models/map_base_s1.glb, maps/bentham_ring/models/map_base_s2.glb, maps/bentham_ring/models/map_base_s3.glb, maps/bentham_ring/models/map_base_s4.glb, maps/bentham_ring/models/map_base_s5.glb | u -24.27..11.00 v -10.44..12.39 | 65536 / 65536 | 100.0% | yes (LavaRiver,LavaSea) | LIVE |
| maps/forest/textures/forest_atlas_albedo.png | albedo | 187302 | 78062.00 | 0 | forest(18) | ForestAtlas, ForestPortalAtlas | maps/forest/models/forest_bush_low.glb, maps/forest/models/forest_bush_tall.glb, maps/forest/models/forest_canopy.glb, maps/forest/models/forest_portal.glb, maps/forest/models/forest_tree.glb | u 0.01..0.99 v 0.01..0.99 | 30951 / 65536 | 47.2% | n/a | LIVE |
| maps/forest/textures/forest_bark_albedo.png | albedo | 20031 | 2055.60 | 0 | forest(2), hub(1) | ForestBark, forest_bark | hub/models/hub_base.glb, maps/forest/models/forest.glb, maps/forest/models/forest_bars.glb | u -14.38..15.65 v -14.66..1.68 | 65230 / 65536 | 99.5% | n/a | LIVE |
| maps/forest/textures/forest_dark_albedo.png | albedo | 59820 | 20672.63 | 0 | forest(2), hub(1) | ForestDark, forest_cell, forest_lamp | hub/models/hub_base.glb, maps/forest/models/forest.glb | u -13.77..14.50 v -3.85..1.86 | 65536 / 65536 | 100.0% | n/a | LIVE |
| maps/forest/textures/forest_earth_albedo.png | albedo | 9108 | 8712.08 | 0 | forest(1) | forest_earth | maps/forest/models/forest.glb | u -13.00..13.00 v -2.62..1.86 | 65536 / 65536 | 100.0% | n/a | LIVE |
| maps/forest/textures/forest_edge_albedo.png | albedo | 6382 | 498.64 | 0 | forest(1) | forest_edge | maps/forest/models/forest.glb | u -14.50..14.50 v -3.68..-0.80 | 22765 / 65536 | 34.7% | n/a | LIVE |
| maps/forest/textures/forest_fern_albedo.png | albedo | 10704 | 126.68 | 0 | forest(1), hub(1) | ForestFern, forest_fern | hub/models/hub_base.glb, maps/forest/models/forest.glb | u -13.60..14.10 v -13.02..1.00 | 28984 / 65536 | 44.2% | n/a | LIVE |
| maps/forest/textures/forest_grass_albedo.png | albedo | 2144 | 1579.07 | 0 | forest(1), hub(1) | ForestGrass, forest_grass | hub/models/hub_base.glb, maps/forest/models/forest.glb | u -13.00..13.00 v -15.20..-2.65 | 65536 / 65536 | 100.0% | n/a | LIVE |
| maps/forest/textures/forest_lamp_emissive.png | emissive | 5058 | 4002.00 | 0 | forest(1) | forest_lamp | maps/forest/models/forest.glb | u -13.77..14.50 v -3.85..1.68 | 65536 / 65536 | 100.0% | yes (forest_lamp) | LIVE |
| maps/forest/textures/forest_leaf_albedo.png | albedo | 10975 | 9399.69 | 0 | forest(2), hub(1) | ForestLeaf, forest_leaf | hub/models/hub_base.glb, maps/forest/models/forest.glb, maps/forest/models/forest_bars.glb | u -14.50..16.20 v -15.40..1.62 | 65536 / 65536 | 100.0% | n/a | LIVE |
| maps/forest/textures/forest_path_albedo.png | albedo | 1062 | 1050.06 | 0 | forest(1), hub(1) | ForestPath, forest_path | hub/models/hub_base.glb, maps/forest/models/forest.glb | u -13.00..13.00 v -12.00..-2.95 | 65536 / 65536 | 100.0% | n/a | LIVE |
| maps/forest/textures/forest_portal_swirl_albedo.png | albedo | 90 | 16.38 | 0 | forest(1) | ForestPortalSwirl | maps/forest/models/forest_portal.glb | u 0.02..0.98 v 0.02..0.98 | 3666 / 4096 | 89.5% | n/a | LIVE |
| maps/forest/textures/forest_portal_swirl_albedo.png | emissive | 90 | 16.38 | 0 | forest(1) | ForestPortalSwirl | maps/forest/models/forest_portal.glb | u 0.02..0.98 v 0.02..0.98 | 3666 / 4096 | 89.5% | yes (ForestPortalSwirl) | LIVE |
| maps/forest/textures/forest_rock_albedo.png | albedo | 2156 | 154.74 | 0 | forest(15) | ForestGranite | maps/forest/models/forest_rock_boulder.glb, maps/forest/models/forest_rock_outcrop.glb | u 0.01..0.98 v 0.02..0.98 | 10137 / 16384 | 61.9% | n/a | LIVE |
| maps/forest/textures/forest_root_albedo.png | albedo | 2730 | 583.84 | 0 | forest(2) | forest_root | maps/forest/models/forest.glb, maps/forest/models/forest_bars.glb | u -8.88..9.04 v -2.57..1.68 | 52339 / 65536 | 79.9% | n/a | LIVE |
| maps/forest/textures/forest_shade_albedo.png | albedo | 5388 | 4676.34 | 0 | forest(1) | forest_shade | maps/forest/models/forest.glb | u -13.00..13.00 v -3.48..-1.66 | 58814 / 65536 | 89.7% | n/a | LIVE |
| maps/forest/textures/forest_sun_albedo.png | albedo | 818 | 745.31 | 0 | forest(1) | forest_sun | maps/forest/models/forest.glb | u -12.46..13.00 v -3.51..-1.69 | 56396 / 65536 | 86.1% | n/a | LIVE |
| maps/forest/textures/forest_verge_albedo.png | albedo | 960 | 1189.05 | 0 | forest(1) | forest_verge | maps/forest/models/forest.glb | u -13.00..13.00 v -3.34..-2.83 | 18952 / 65536 | 28.9% | n/a | LIVE |
| maps/marble/textures/marble_albedo.png | albedo | 12044 | 21397.37 | 1566 | hub(1), marble(15) | Marble, MarbleGlow, marble_band, marble_bars_band, marble_bars_column, marble_column, marble_dome, marble_floor, marble_frieze, marble_spike, marble_tower_band, marble_tower_coffer, marble_tower_column, marble_tower_floor, marble_tower_medallion | hub/models/hub_base.glb, maps/marble/models/marble.glb, maps/marble/models/marble_bars.glb, maps/marble/models/marble_portal.glb, maps/marble/models/marble_tower.glb | u 0.00..1.00 v 0.01..1.00 | 54150 / 81920 | 66.1% | n/a | LIVE |
| maps/marble/textures/marble_albedo.png | emissive | 18 | 16.02 | 0 | marble(1) | MarbleGlow | maps/marble/models/marble_portal.glb | u 0.41..0.59 v 0.01..0.24 | 3595 / 81920 | 4.4% | yes (MarbleGlow) | LIVE |
| maps/marble/textures/marble_dark_albedo.png | albedo | 18858 | 13772.66 | 1344 | hub(1), marble(4) | MarbleDark, marble_bars_iron, marble_cellin, marble_iron, marble_tower_iron | hub/models/hub_base.glb, maps/marble/models/marble.glb, maps/marble/models/marble_bars.glb, maps/marble/models/marble_tower.glb | u 0.01..1.00 v -3.54..1.01 | 29591 / 50112 | 59.0% | n/a | LIVE |
| maps/marble/textures/marble_field_albedo.png | albedo | 7104 | 11049.71 | 0 | marble(1) | marble_field | maps/marble/models/marble.glb | u -4.69..4.69 v -3.69..5.69 | 65536 / 65536 | 100.0% | n/a | LIVE |
| maps/marble/textures/marble_stone_albedo.png | albedo | 43812 | 49390.05 | 2096 | hub(4), marble(16) | Marble_marble, Marble_marble2, Marble_plinth, Marble_shade, marble_bars_marble, marble_bars_marble2, marble_bars_plinth, marble_bars_shade, marble_marble, marble_plinth, marble_shade, marble_tower_dome, marble_tower_marble2, marble_tower_plinth, marble_tower_shade, marble_tower_stone | hub/models/hub_base.glb, maps/marble/models/marble.glb, maps/marble/models/marble_bars.glb, maps/marble/models/marble_portal.glb, maps/marble/models/marble_tower.glb | u -32.53..32.53 v -7.16..1.04 | 33408 / 33408 | 100.0% | n/a | LIVE |
| props/textures/speed_orb_albedo.png | albedo | 20 | 3.45 | 0 | bentham_ring(1) | SpeedOrb | props/models/speed_orb.glb | u 0.03..0.96 v 0.03..0.94 | 2823 / 4096 | 68.9% | n/a | LIVE |
| props/textures/speed_orb_albedo.png | emissive | 20 | 3.45 | 0 | bentham_ring(1) | SpeedOrb | props/models/speed_orb.glb | u 0.03..0.96 v 0.03..0.94 | 2823 / 4096 | 68.9% | yes (SpeedOrb) | LIVE |
| weapons/textures/rifle_hell_albedo.png | albedo | 566 | 0.37 | 0 | match(1) | RifleWarden | weapons/models/rifle.glb | u 0.01..0.99 v 0.01..0.98 | 11441 / 16384 | 69.8% | n/a | LIVE |

### File verdicts

| texture | live tris | live area m2 | hidden tris | texels touched | verdict |
|---|---|---|---|---|---|
| characters/textures/prisoner2_albedo.png | 1602 | 5.27 | 0 | 594 / 1024 (58.0%) | **LIVE** |
| hub/textures/hub_stone_albedo.png | 9980 | 15959.66 | 0 | 14862 / 16384 (90.7%) | **LIVE** |
| maps/bentham_ring/textures/crack_glow_albedo.png | 9782 | 19357.22 | 0 | 1860 / 2048 (90.8%) | **LIVE** |
| maps/bentham_ring/textures/hell_props_albedo.png | 26 | 15.90 | 0 | 3501 / 4096 (85.5%) | **LIVE** |
| maps/bentham_ring/textures/hell_rock_albedo.png | 83225 | 209466.99 | 2336 | 65536 / 65536 (100.0%) | **LIVE** |
| maps/bentham_ring/textures/lava_albedo.png | 15800 | 11335.74 | 0 | 65536 / 65536 (100.0%) | **LIVE** |
| maps/bentham_ring/textures/map_base_lava_emissive.png | 15760 | 11326.15 | 0 | 65536 / 65536 (100.0%) | **LIVE** |
| maps/forest/textures/forest_atlas_albedo.png | 187302 | 78062.00 | 0 | 30951 / 65536 (47.2%) | **LIVE** |
| maps/forest/textures/forest_bark_albedo.png | 20031 | 2055.60 | 0 | 65230 / 65536 (99.5%) | **LIVE** |
| maps/forest/textures/forest_dark_albedo.png | 59820 | 20672.63 | 0 | 65536 / 65536 (100.0%) | **LIVE** |
| maps/forest/textures/forest_earth_albedo.png | 9108 | 8712.08 | 0 | 65536 / 65536 (100.0%) | **LIVE** |
| maps/forest/textures/forest_edge_albedo.png | 6382 | 498.64 | 0 | 22765 / 65536 (34.7%) | **LIVE** |
| maps/forest/textures/forest_fern_albedo.png | 10704 | 126.68 | 0 | 28984 / 65536 (44.2%) | **LIVE** |
| maps/forest/textures/forest_grass_albedo.png | 2144 | 1579.07 | 0 | 65536 / 65536 (100.0%) | **LIVE** |
| maps/forest/textures/forest_lamp_emissive.png | 5058 | 4002.00 | 0 | 65536 / 65536 (100.0%) | **LIVE** |
| maps/forest/textures/forest_leaf_albedo.png | 10975 | 9399.69 | 0 | 65536 / 65536 (100.0%) | **LIVE** |
| maps/forest/textures/forest_path_albedo.png | 1062 | 1050.06 | 0 | 65536 / 65536 (100.0%) | **LIVE** |
| maps/forest/textures/forest_portal_swirl_albedo.png | 90 | 16.38 | 0 | 3666 / 4096 (89.5%) | **LIVE** |
| maps/forest/textures/forest_rock_albedo.png | 2156 | 154.74 | 0 | 10137 / 16384 (61.9%) | **LIVE** |
| maps/forest/textures/forest_root_albedo.png | 2730 | 583.84 | 0 | 52339 / 65536 (79.9%) | **LIVE** |
| maps/forest/textures/forest_shade_albedo.png | 5388 | 4676.34 | 0 | 58814 / 65536 (89.7%) | **LIVE** |
| maps/forest/textures/forest_sun_albedo.png | 818 | 745.31 | 0 | 56396 / 65536 (86.1%) | **LIVE** |
| maps/forest/textures/forest_verge_albedo.png | 960 | 1189.05 | 0 | 18952 / 65536 (28.9%) | **LIVE** |
| maps/marble/textures/marble_albedo.png | 12044 | 21397.37 | 1566 | 54150 / 81920 (66.1%) | **LIVE** |
| maps/marble/textures/marble_dark_albedo.png | 18858 | 13772.66 | 1344 | 29591 / 50112 (59.0%) | **LIVE** |
| maps/marble/textures/marble_field_albedo.png | 7104 | 11049.71 | 0 | 65536 / 65536 (100.0%) | **LIVE** |
| maps/marble/textures/marble_stone_albedo.png | 43812 | 49390.05 | 2096 | 33408 / 33408 (100.0%) | **LIVE** |
| props/textures/speed_orb_albedo.png | 20 | 3.45 | 0 | 2823 / 4096 (68.9%) | **LIVE** |
| weapons/textures/rifle_hell_albedo.png | 566 | 0.37 | 0 | 11441 / 16384 (69.8%) | **LIVE** |

### Sheet regions (SHEET_*.json)

| sheet | region file | kind | rect | texels touched | verdict |
|---|---|---|---|---|---|
| characters/textures/SHEET_characters.json | prisoner2_albedo.png | albedo | [0, 7, 32, 32] | 594 | LIVE |
| hub/textures/SHEET_hub.json | hub_stone_albedo.png | albedo | [0, 7, 128, 128] | 14862 | LIVE |
| maps/bentham_ring/textures/SHEET_bentham_ring.json | crack_glow_albedo.png | albedo | [0, 7, 64, 32] | 1860 | LIVE |
| maps/bentham_ring/textures/SHEET_bentham_ring.json | hell_props_albedo.png | albedo | [87, 7, 64, 64] | 3501 | LIVE |
| maps/bentham_ring/textures/SHEET_bentham_ring.json | hell_rock_albedo.png | albedo | [174, 7, 256, 256] | 65536 | LIVE |
| maps/bentham_ring/textures/SHEET_bentham_ring.json | lava_albedo.png | albedo | [434, 7, 256, 256] | 65536 | LIVE |
| maps/forest/textures/SHEET_forest.json | forest_atlas_albedo.png | albedo | [0, 7, 256, 256] | 30951 | LIVE |
| maps/forest/textures/SHEET_forest.json | forest_bark_albedo.png | albedo | [260, 7, 256, 256] | 65230 | LIVE |
| maps/forest/textures/SHEET_forest.json | forest_dark_albedo.png | albedo | [520, 7, 256, 256] | 65536 | LIVE |
| maps/forest/textures/SHEET_forest.json | forest_earth_albedo.png | albedo | [780, 7, 256, 256] | 65536 | LIVE |
| maps/forest/textures/SHEET_forest.json | forest_edge_albedo.png | albedo | [1040, 7, 256, 256] | 22765 | LIVE |
| maps/forest/textures/SHEET_forest.json | forest_fern_albedo.png | albedo | [1300, 7, 256, 256] | 28984 | LIVE |
| maps/forest/textures/SHEET_forest.json | forest_grass_albedo.png | albedo | [1560, 7, 256, 256] | 65536 | LIVE |
| maps/forest/textures/SHEET_forest.json | forest_leaf_albedo.png | albedo | [1820, 7, 256, 256] | 65536 | LIVE |
| maps/forest/textures/SHEET_forest.json | forest_path_albedo.png | albedo | [2080, 7, 256, 256] | 65536 | LIVE |
| maps/forest/textures/SHEET_forest.json | forest_portal_swirl_albedo.png | albedo | [2340, 7, 64, 64] | 3666 | LIVE |
| maps/forest/textures/SHEET_forest.json | forest_rock_albedo.png | albedo | [2463, 7, 128, 128] | 10137 | LIVE |
| maps/forest/textures/SHEET_forest.json | forest_root_albedo.png | albedo | [2595, 7, 256, 256] | 52339 | LIVE |
| maps/forest/textures/SHEET_forest.json | forest_shade_albedo.png | albedo | [2855, 7, 256, 256] | 58814 | LIVE |
| maps/forest/textures/SHEET_forest.json | forest_sun_albedo.png | albedo | [3115, 7, 256, 256] | 56396 | LIVE |
| maps/forest/textures/SHEET_forest.json | forest_verge_albedo.png | albedo | [3375, 7, 256, 256] | 18952 | LIVE |
| maps/marble/textures/SHEET_marble.json | marble_albedo.png | albedo | [0, 7, 320, 256] | 54150 | LIVE |
| maps/marble/textures/SHEET_marble.json | marble_dark_albedo.png | albedo | [324, 7, 192, 261] | 29591 | LIVE |
| maps/marble/textures/SHEET_marble.json | marble_field_albedo.png | albedo | [520, 7, 256, 256] | 65536 | LIVE |
| maps/marble/textures/SHEET_marble.json | marble_stone_albedo.png | albedo | [780, 7, 128, 261] | 33408 | LIVE |
| props/textures/SHEET_props.json | speed_orb_albedo.png | albedo | [0, 7, 64, 64] | 2823 | LIVE |
| weapons/textures/SHEET_weapons.json | rifle_hell_albedo.png | albedo | [0, 7, 128, 128] | 11441 | LIVE |

### Sub-regions within files (4x4 blocks of each file, texels touched / block; any slot)

| texture | block (x0,y0,x1,y1 px) | texels touched | coverage |
|---|---|---|---|
| characters/textures/prisoner2_albedo.png | (0,0,8,8) | 32 / 64 | 50.0% |
| characters/textures/prisoner2_albedo.png | (8,0,16,8) | 38 / 64 | 59.4% |
| characters/textures/prisoner2_albedo.png | (16,0,24,8) | 23 / 64 | 35.9% |
| characters/textures/prisoner2_albedo.png | (24,0,32,8) | 19 / 64 | 29.7% |
| characters/textures/prisoner2_albedo.png | (0,8,8,16) | 45 / 64 | 70.3% |
| characters/textures/prisoner2_albedo.png | (8,8,16,16) | 26 / 64 | 40.6% |
| characters/textures/prisoner2_albedo.png | (16,8,24,16) | 33 / 64 | 51.6% |
| characters/textures/prisoner2_albedo.png | (24,8,32,16) | 28 / 64 | 43.8% |
| characters/textures/prisoner2_albedo.png | (0,16,8,24) | 42 / 64 | 65.6% |
| characters/textures/prisoner2_albedo.png | (8,16,16,24) | 40 / 64 | 62.5% |
| characters/textures/prisoner2_albedo.png | (16,16,24,24) | 47 / 64 | 73.4% |
| characters/textures/prisoner2_albedo.png | (24,16,32,24) | 43 / 64 | 67.2% |
| characters/textures/prisoner2_albedo.png | (0,24,8,32) | 44 / 64 | 68.8% |
| characters/textures/prisoner2_albedo.png | (8,24,16,32) | 47 / 64 | 73.4% |
| characters/textures/prisoner2_albedo.png | (16,24,24,32) | 45 / 64 | 70.3% |
| characters/textures/prisoner2_albedo.png | (24,24,32,32) | 42 / 64 | 65.6% |
| hub/textures/hub_stone_albedo.png | (0,0,32,32) | 953 / 1024 | 93.1% |
| hub/textures/hub_stone_albedo.png | (32,0,64,32) | 949 / 1024 | 92.7% |
| hub/textures/hub_stone_albedo.png | (64,0,96,32) | 883 / 1024 | 86.2% |
| hub/textures/hub_stone_albedo.png | (96,0,128,32) | 897 / 1024 | 87.6% |
| hub/textures/hub_stone_albedo.png | (0,32,32,64) | 936 / 1024 | 91.4% |
| hub/textures/hub_stone_albedo.png | (32,32,64,64) | 947 / 1024 | 92.5% |
| hub/textures/hub_stone_albedo.png | (64,32,96,64) | 886 / 1024 | 86.5% |
| hub/textures/hub_stone_albedo.png | (96,32,128,64) | 894 / 1024 | 87.3% |
| hub/textures/hub_stone_albedo.png | (0,64,32,96) | 926 / 1024 | 90.4% |
| hub/textures/hub_stone_albedo.png | (32,64,64,96) | 933 / 1024 | 91.1% |
| hub/textures/hub_stone_albedo.png | (64,64,96,96) | 961 / 1024 | 93.8% |
| hub/textures/hub_stone_albedo.png | (96,64,128,96) | 955 / 1024 | 93.3% |
| hub/textures/hub_stone_albedo.png | (0,96,32,128) | 910 / 1024 | 88.9% |
| hub/textures/hub_stone_albedo.png | (32,96,64,128) | 910 / 1024 | 88.9% |
| hub/textures/hub_stone_albedo.png | (64,96,96,128) | 961 / 1024 | 93.8% |
| hub/textures/hub_stone_albedo.png | (96,96,128,128) | 961 / 1024 | 93.8% |
| maps/bentham_ring/textures/crack_glow_albedo.png | (0,0,16,8) | 105 / 128 | 82.0% |
| maps/bentham_ring/textures/crack_glow_albedo.png | (16,0,32,8) | 112 / 128 | 87.5% |
| maps/bentham_ring/textures/crack_glow_albedo.png | (32,0,48,8) | 112 / 128 | 87.5% |
| maps/bentham_ring/textures/crack_glow_albedo.png | (48,0,64,8) | 105 / 128 | 82.0% |
| maps/bentham_ring/textures/crack_glow_albedo.png | (0,8,16,16) | 120 / 128 | 93.8% |
| maps/bentham_ring/textures/crack_glow_albedo.png | (16,8,32,16) | 128 / 128 | 100.0% |
| maps/bentham_ring/textures/crack_glow_albedo.png | (32,8,48,16) | 128 / 128 | 100.0% |
| maps/bentham_ring/textures/crack_glow_albedo.png | (48,8,64,16) | 120 / 128 | 93.8% |
| maps/bentham_ring/textures/crack_glow_albedo.png | (0,16,16,24) | 120 / 128 | 93.8% |
| maps/bentham_ring/textures/crack_glow_albedo.png | (16,16,32,24) | 128 / 128 | 100.0% |
| maps/bentham_ring/textures/crack_glow_albedo.png | (32,16,48,24) | 128 / 128 | 100.0% |
| maps/bentham_ring/textures/crack_glow_albedo.png | (48,16,64,24) | 120 / 128 | 93.8% |
| maps/bentham_ring/textures/crack_glow_albedo.png | (0,24,16,32) | 105 / 128 | 82.0% |
| maps/bentham_ring/textures/crack_glow_albedo.png | (16,24,32,32) | 112 / 128 | 87.5% |
| maps/bentham_ring/textures/crack_glow_albedo.png | (32,24,48,32) | 112 / 128 | 87.5% |
| maps/bentham_ring/textures/crack_glow_albedo.png | (48,24,64,32) | 105 / 128 | 82.0% |
| maps/bentham_ring/textures/hell_props_albedo.png | (0,0,16,16) | 131 / 256 | 51.2% |
| maps/bentham_ring/textures/hell_props_albedo.png | (16,0,32,16) | 222 / 256 | 86.7% |
| maps/bentham_ring/textures/hell_props_albedo.png | (32,0,48,16) | 199 / 256 | 77.7% |
| maps/bentham_ring/textures/hell_props_albedo.png | (48,0,64,16) | 108 / 256 | 42.2% |
| maps/bentham_ring/textures/hell_props_albedo.png | (0,16,16,32) | 217 / 256 | 84.8% |
| maps/bentham_ring/textures/hell_props_albedo.png | (16,16,32,32) | 256 / 256 | 100.0% |
| maps/bentham_ring/textures/hell_props_albedo.png | (32,16,48,32) | 256 / 256 | 100.0% |
| maps/bentham_ring/textures/hell_props_albedo.png | (48,16,64,32) | 220 / 256 | 85.9% |
| maps/bentham_ring/textures/hell_props_albedo.png | (0,32,16,48) | 217 / 256 | 84.8% |
| maps/bentham_ring/textures/hell_props_albedo.png | (16,32,32,48) | 256 / 256 | 100.0% |
| maps/bentham_ring/textures/hell_props_albedo.png | (32,32,48,48) | 256 / 256 | 100.0% |
| maps/bentham_ring/textures/hell_props_albedo.png | (48,32,64,48) | 240 / 256 | 93.8% |
| maps/bentham_ring/textures/hell_props_albedo.png | (0,48,16,64) | 218 / 256 | 85.2% |
| maps/bentham_ring/textures/hell_props_albedo.png | (16,48,32,64) | 240 / 256 | 93.8% |
| maps/bentham_ring/textures/hell_props_albedo.png | (32,48,48,64) | 240 / 256 | 93.8% |
| maps/bentham_ring/textures/hell_props_albedo.png | (48,48,64,64) | 225 / 256 | 87.9% |
| maps/bentham_ring/textures/hell_rock_albedo.png | (0,0,64,64) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/hell_rock_albedo.png | (64,0,128,64) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/hell_rock_albedo.png | (128,0,192,64) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/hell_rock_albedo.png | (192,0,256,64) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/hell_rock_albedo.png | (0,64,64,128) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/hell_rock_albedo.png | (64,64,128,128) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/hell_rock_albedo.png | (128,64,192,128) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/hell_rock_albedo.png | (192,64,256,128) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/hell_rock_albedo.png | (0,128,64,192) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/hell_rock_albedo.png | (64,128,128,192) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/hell_rock_albedo.png | (128,128,192,192) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/hell_rock_albedo.png | (192,128,256,192) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/hell_rock_albedo.png | (0,192,64,256) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/hell_rock_albedo.png | (64,192,128,256) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/hell_rock_albedo.png | (128,192,192,256) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/hell_rock_albedo.png | (192,192,256,256) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/lava_albedo.png | (0,0,64,64) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/lava_albedo.png | (64,0,128,64) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/lava_albedo.png | (128,0,192,64) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/lava_albedo.png | (192,0,256,64) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/lava_albedo.png | (0,64,64,128) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/lava_albedo.png | (64,64,128,128) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/lava_albedo.png | (128,64,192,128) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/lava_albedo.png | (192,64,256,128) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/lava_albedo.png | (0,128,64,192) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/lava_albedo.png | (64,128,128,192) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/lava_albedo.png | (128,128,192,192) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/lava_albedo.png | (192,128,256,192) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/lava_albedo.png | (0,192,64,256) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/lava_albedo.png | (64,192,128,256) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/lava_albedo.png | (128,192,192,256) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/lava_albedo.png | (192,192,256,256) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/map_base_lava_emissive.png | (0,0,64,64) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/map_base_lava_emissive.png | (64,0,128,64) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/map_base_lava_emissive.png | (128,0,192,64) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/map_base_lava_emissive.png | (192,0,256,64) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/map_base_lava_emissive.png | (0,64,64,128) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/map_base_lava_emissive.png | (64,64,128,128) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/map_base_lava_emissive.png | (128,64,192,128) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/map_base_lava_emissive.png | (192,64,256,128) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/map_base_lava_emissive.png | (0,128,64,192) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/map_base_lava_emissive.png | (64,128,128,192) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/map_base_lava_emissive.png | (128,128,192,192) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/map_base_lava_emissive.png | (192,128,256,192) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/map_base_lava_emissive.png | (0,192,64,256) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/map_base_lava_emissive.png | (64,192,128,256) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/map_base_lava_emissive.png | (128,192,192,256) | 4096 / 4096 | 100.0% |
| maps/bentham_ring/textures/map_base_lava_emissive.png | (192,192,256,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_atlas_albedo.png | (0,0,64,64) | 0 / 4096 | 0.0% |
| maps/forest/textures/forest_atlas_albedo.png | (64,0,128,64) | 0 / 4096 | 0.0% |
| maps/forest/textures/forest_atlas_albedo.png | (128,0,192,64) | 3968 / 4096 | 96.9% |
| maps/forest/textures/forest_atlas_albedo.png | (192,0,256,64) | 3967 / 4096 | 96.9% |
| maps/forest/textures/forest_atlas_albedo.png | (0,64,64,128) | 3712 / 4096 | 90.6% |
| maps/forest/textures/forest_atlas_albedo.png | (64,64,128,128) | 3737 / 4096 | 91.2% |
| maps/forest/textures/forest_atlas_albedo.png | (128,64,192,128) | 3965 / 4096 | 96.8% |
| maps/forest/textures/forest_atlas_albedo.png | (192,64,256,128) | 3966 / 4096 | 96.8% |
| maps/forest/textures/forest_atlas_albedo.png | (0,128,64,192) | 0 / 4096 | 0.0% |
| maps/forest/textures/forest_atlas_albedo.png | (64,128,128,192) | 0 / 4096 | 0.0% |
| maps/forest/textures/forest_atlas_albedo.png | (128,128,192,192) | 0 / 4096 | 0.0% |
| maps/forest/textures/forest_atlas_albedo.png | (192,128,256,192) | 3792 / 4096 | 92.6% |
| maps/forest/textures/forest_atlas_albedo.png | (0,192,64,256) | 0 / 4096 | 0.0% |
| maps/forest/textures/forest_atlas_albedo.png | (64,192,128,256) | 0 / 4096 | 0.0% |
| maps/forest/textures/forest_atlas_albedo.png | (128,192,192,256) | 3844 / 4096 | 93.8% |
| maps/forest/textures/forest_atlas_albedo.png | (192,192,256,256) | 0 / 4096 | 0.0% |
| maps/forest/textures/forest_bark_albedo.png | (0,0,64,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_bark_albedo.png | (64,0,128,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_bark_albedo.png | (128,0,192,64) | 3979 / 4096 | 97.1% |
| maps/forest/textures/forest_bark_albedo.png | (192,0,256,64) | 3947 / 4096 | 96.4% |
| maps/forest/textures/forest_bark_albedo.png | (0,64,64,128) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_bark_albedo.png | (64,64,128,128) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_bark_albedo.png | (128,64,192,128) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_bark_albedo.png | (192,64,256,128) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_bark_albedo.png | (0,128,64,192) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_bark_albedo.png | (64,128,128,192) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_bark_albedo.png | (128,128,192,192) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_bark_albedo.png | (192,128,256,192) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_bark_albedo.png | (0,192,64,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_bark_albedo.png | (64,192,128,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_bark_albedo.png | (128,192,192,256) | 4090 / 4096 | 99.9% |
| maps/forest/textures/forest_bark_albedo.png | (192,192,256,256) | 4062 / 4096 | 99.2% |
| maps/forest/textures/forest_dark_albedo.png | (0,0,64,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_dark_albedo.png | (64,0,128,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_dark_albedo.png | (128,0,192,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_dark_albedo.png | (192,0,256,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_dark_albedo.png | (0,64,64,128) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_dark_albedo.png | (64,64,128,128) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_dark_albedo.png | (128,64,192,128) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_dark_albedo.png | (192,64,256,128) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_dark_albedo.png | (0,128,64,192) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_dark_albedo.png | (64,128,128,192) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_dark_albedo.png | (128,128,192,192) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_dark_albedo.png | (192,128,256,192) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_dark_albedo.png | (0,192,64,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_dark_albedo.png | (64,192,128,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_dark_albedo.png | (128,192,192,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_dark_albedo.png | (192,192,256,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_earth_albedo.png | (0,0,64,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_earth_albedo.png | (64,0,128,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_earth_albedo.png | (128,0,192,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_earth_albedo.png | (192,0,256,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_earth_albedo.png | (0,64,64,128) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_earth_albedo.png | (64,64,128,128) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_earth_albedo.png | (128,64,192,128) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_earth_albedo.png | (192,64,256,128) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_earth_albedo.png | (0,128,64,192) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_earth_albedo.png | (64,128,128,192) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_earth_albedo.png | (128,128,192,192) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_earth_albedo.png | (192,128,256,192) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_earth_albedo.png | (0,192,64,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_earth_albedo.png | (64,192,128,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_earth_albedo.png | (128,192,192,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_earth_albedo.png | (192,192,256,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_edge_albedo.png | (0,0,64,64) | 448 / 4096 | 10.9% |
| maps/forest/textures/forest_edge_albedo.png | (64,0,128,64) | 448 / 4096 | 10.9% |
| maps/forest/textures/forest_edge_albedo.png | (128,0,192,64) | 448 / 4096 | 10.9% |
| maps/forest/textures/forest_edge_albedo.png | (192,0,256,64) | 448 / 4096 | 10.9% |
| maps/forest/textures/forest_edge_albedo.png | (0,64,64,128) | 2624 / 4096 | 64.1% |
| maps/forest/textures/forest_edge_albedo.png | (64,64,128,128) | 2624 / 4096 | 64.1% |
| maps/forest/textures/forest_edge_albedo.png | (128,64,192,128) | 2624 / 4096 | 64.1% |
| maps/forest/textures/forest_edge_albedo.png | (192,64,256,128) | 2624 / 4096 | 64.1% |
| maps/forest/textures/forest_edge_albedo.png | (0,128,64,192) | 2624 / 4096 | 64.1% |
| maps/forest/textures/forest_edge_albedo.png | (64,128,128,192) | 2622 / 4096 | 64.0% |
| maps/forest/textures/forest_edge_albedo.png | (128,128,192,192) | 2607 / 4096 | 63.6% |
| maps/forest/textures/forest_edge_albedo.png | (192,128,256,192) | 2624 / 4096 | 64.1% |
| maps/forest/textures/forest_edge_albedo.png | (0,192,64,256) | 0 / 4096 | 0.0% |
| maps/forest/textures/forest_edge_albedo.png | (64,192,128,256) | 0 / 4096 | 0.0% |
| maps/forest/textures/forest_edge_albedo.png | (128,192,192,256) | 0 / 4096 | 0.0% |
| maps/forest/textures/forest_edge_albedo.png | (192,192,256,256) | 0 / 4096 | 0.0% |
| maps/forest/textures/forest_fern_albedo.png | (0,0,64,64) | 1256 / 4096 | 30.7% |
| maps/forest/textures/forest_fern_albedo.png | (64,0,128,64) | 1419 / 4096 | 34.6% |
| maps/forest/textures/forest_fern_albedo.png | (128,0,192,64) | 914 / 4096 | 22.3% |
| maps/forest/textures/forest_fern_albedo.png | (192,0,256,64) | 2018 / 4096 | 49.3% |
| maps/forest/textures/forest_fern_albedo.png | (0,64,64,128) | 1487 / 4096 | 36.3% |
| maps/forest/textures/forest_fern_albedo.png | (64,64,128,128) | 2616 / 4096 | 63.9% |
| maps/forest/textures/forest_fern_albedo.png | (128,64,192,128) | 1433 / 4096 | 35.0% |
| maps/forest/textures/forest_fern_albedo.png | (192,64,256,128) | 1976 / 4096 | 48.2% |
| maps/forest/textures/forest_fern_albedo.png | (0,128,64,192) | 1544 / 4096 | 37.7% |
| maps/forest/textures/forest_fern_albedo.png | (64,128,128,192) | 1669 / 4096 | 40.7% |
| maps/forest/textures/forest_fern_albedo.png | (128,128,192,192) | 1998 / 4096 | 48.8% |
| maps/forest/textures/forest_fern_albedo.png | (192,128,256,192) | 2754 / 4096 | 67.2% |
| maps/forest/textures/forest_fern_albedo.png | (0,192,64,256) | 1282 / 4096 | 31.3% |
| maps/forest/textures/forest_fern_albedo.png | (64,192,128,256) | 1794 / 4096 | 43.8% |
| maps/forest/textures/forest_fern_albedo.png | (128,192,192,256) | 1957 / 4096 | 47.8% |
| maps/forest/textures/forest_fern_albedo.png | (192,192,256,256) | 2867 / 4096 | 70.0% |
| maps/forest/textures/forest_grass_albedo.png | (0,0,64,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_grass_albedo.png | (64,0,128,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_grass_albedo.png | (128,0,192,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_grass_albedo.png | (192,0,256,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_grass_albedo.png | (0,64,64,128) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_grass_albedo.png | (64,64,128,128) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_grass_albedo.png | (128,64,192,128) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_grass_albedo.png | (192,64,256,128) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_grass_albedo.png | (0,128,64,192) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_grass_albedo.png | (64,128,128,192) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_grass_albedo.png | (128,128,192,192) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_grass_albedo.png | (192,128,256,192) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_grass_albedo.png | (0,192,64,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_grass_albedo.png | (64,192,128,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_grass_albedo.png | (128,192,192,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_grass_albedo.png | (192,192,256,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_lamp_emissive.png | (0,0,64,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_lamp_emissive.png | (64,0,128,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_lamp_emissive.png | (128,0,192,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_lamp_emissive.png | (192,0,256,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_lamp_emissive.png | (0,64,64,128) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_lamp_emissive.png | (64,64,128,128) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_lamp_emissive.png | (128,64,192,128) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_lamp_emissive.png | (192,64,256,128) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_lamp_emissive.png | (0,128,64,192) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_lamp_emissive.png | (64,128,128,192) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_lamp_emissive.png | (128,128,192,192) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_lamp_emissive.png | (192,128,256,192) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_lamp_emissive.png | (0,192,64,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_lamp_emissive.png | (64,192,128,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_lamp_emissive.png | (128,192,192,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_lamp_emissive.png | (192,192,256,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_leaf_albedo.png | (0,0,64,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_leaf_albedo.png | (64,0,128,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_leaf_albedo.png | (128,0,192,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_leaf_albedo.png | (192,0,256,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_leaf_albedo.png | (0,64,64,128) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_leaf_albedo.png | (64,64,128,128) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_leaf_albedo.png | (128,64,192,128) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_leaf_albedo.png | (192,64,256,128) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_leaf_albedo.png | (0,128,64,192) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_leaf_albedo.png | (64,128,128,192) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_leaf_albedo.png | (128,128,192,192) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_leaf_albedo.png | (192,128,256,192) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_leaf_albedo.png | (0,192,64,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_leaf_albedo.png | (64,192,128,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_leaf_albedo.png | (128,192,192,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_leaf_albedo.png | (192,192,256,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_path_albedo.png | (0,0,64,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_path_albedo.png | (64,0,128,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_path_albedo.png | (128,0,192,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_path_albedo.png | (192,0,256,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_path_albedo.png | (0,64,64,128) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_path_albedo.png | (64,64,128,128) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_path_albedo.png | (128,64,192,128) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_path_albedo.png | (192,64,256,128) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_path_albedo.png | (0,128,64,192) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_path_albedo.png | (64,128,128,192) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_path_albedo.png | (128,128,192,192) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_path_albedo.png | (192,128,256,192) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_path_albedo.png | (0,192,64,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_path_albedo.png | (64,192,128,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_path_albedo.png | (128,192,192,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_path_albedo.png | (192,192,256,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_portal_swirl_albedo.png | (0,0,16,16) | 161 / 256 | 62.9% |
| maps/forest/textures/forest_portal_swirl_albedo.png | (16,0,32,16) | 217 / 256 | 84.8% |
| maps/forest/textures/forest_portal_swirl_albedo.png | (32,0,48,16) | 216 / 256 | 84.4% |
| maps/forest/textures/forest_portal_swirl_albedo.png | (48,0,64,16) | 158 / 256 | 61.7% |
| maps/forest/textures/forest_portal_swirl_albedo.png | (0,16,16,32) | 240 / 256 | 93.8% |
| maps/forest/textures/forest_portal_swirl_albedo.png | (16,16,32,32) | 256 / 256 | 100.0% |
| maps/forest/textures/forest_portal_swirl_albedo.png | (32,16,48,32) | 256 / 256 | 100.0% |
| maps/forest/textures/forest_portal_swirl_albedo.png | (48,16,64,32) | 240 / 256 | 93.8% |
| maps/forest/textures/forest_portal_swirl_albedo.png | (0,32,16,48) | 240 / 256 | 93.8% |
| maps/forest/textures/forest_portal_swirl_albedo.png | (16,32,32,48) | 256 / 256 | 100.0% |
| maps/forest/textures/forest_portal_swirl_albedo.png | (32,32,48,48) | 256 / 256 | 100.0% |
| maps/forest/textures/forest_portal_swirl_albedo.png | (48,32,64,48) | 240 / 256 | 93.8% |
| maps/forest/textures/forest_portal_swirl_albedo.png | (0,48,16,64) | 225 / 256 | 87.9% |
| maps/forest/textures/forest_portal_swirl_albedo.png | (16,48,32,64) | 240 / 256 | 93.8% |
| maps/forest/textures/forest_portal_swirl_albedo.png | (32,48,48,64) | 240 / 256 | 93.8% |
| maps/forest/textures/forest_portal_swirl_albedo.png | (48,48,64,64) | 225 / 256 | 87.9% |
| maps/forest/textures/forest_rock_albedo.png | (0,0,32,32) | 775 / 1024 | 75.7% |
| maps/forest/textures/forest_rock_albedo.png | (32,0,64,32) | 678 / 1024 | 66.2% |
| maps/forest/textures/forest_rock_albedo.png | (64,0,96,32) | 470 / 1024 | 45.9% |
| maps/forest/textures/forest_rock_albedo.png | (96,0,128,32) | 400 / 1024 | 39.1% |
| maps/forest/textures/forest_rock_albedo.png | (0,32,32,64) | 680 / 1024 | 66.4% |
| maps/forest/textures/forest_rock_albedo.png | (32,32,64,64) | 731 / 1024 | 71.4% |
| maps/forest/textures/forest_rock_albedo.png | (64,32,96,64) | 388 / 1024 | 37.9% |
| maps/forest/textures/forest_rock_albedo.png | (96,32,128,64) | 392 / 1024 | 38.3% |
| maps/forest/textures/forest_rock_albedo.png | (0,64,32,96) | 736 / 1024 | 71.9% |
| maps/forest/textures/forest_rock_albedo.png | (32,64,64,96) | 795 / 1024 | 77.6% |
| maps/forest/textures/forest_rock_albedo.png | (64,64,96,96) | 692 / 1024 | 67.6% |
| maps/forest/textures/forest_rock_albedo.png | (96,64,128,96) | 618 / 1024 | 60.4% |
| maps/forest/textures/forest_rock_albedo.png | (0,96,32,128) | 722 / 1024 | 70.5% |
| maps/forest/textures/forest_rock_albedo.png | (32,96,64,128) | 754 / 1024 | 73.6% |
| maps/forest/textures/forest_rock_albedo.png | (64,96,96,128) | 704 / 1024 | 68.8% |
| maps/forest/textures/forest_rock_albedo.png | (96,96,128,128) | 602 / 1024 | 58.8% |
| maps/forest/textures/forest_root_albedo.png | (0,0,64,64) | 3557 / 4096 | 86.8% |
| maps/forest/textures/forest_root_albedo.png | (64,0,128,64) | 3900 / 4096 | 95.2% |
| maps/forest/textures/forest_root_albedo.png | (128,0,192,64) | 3410 / 4096 | 83.3% |
| maps/forest/textures/forest_root_albedo.png | (192,0,256,64) | 2282 / 4096 | 55.7% |
| maps/forest/textures/forest_root_albedo.png | (0,64,64,128) | 3519 / 4096 | 85.9% |
| maps/forest/textures/forest_root_albedo.png | (64,64,128,128) | 4006 / 4096 | 97.8% |
| maps/forest/textures/forest_root_albedo.png | (128,64,192,128) | 3200 / 4096 | 78.1% |
| maps/forest/textures/forest_root_albedo.png | (192,64,256,128) | 2834 / 4096 | 69.2% |
| maps/forest/textures/forest_root_albedo.png | (0,128,64,192) | 3440 / 4096 | 84.0% |
| maps/forest/textures/forest_root_albedo.png | (64,128,128,192) | 3888 / 4096 | 94.9% |
| maps/forest/textures/forest_root_albedo.png | (128,128,192,192) | 3200 / 4096 | 78.1% |
| maps/forest/textures/forest_root_albedo.png | (192,128,256,192) | 2456 / 4096 | 60.0% |
| maps/forest/textures/forest_root_albedo.png | (0,192,64,256) | 3496 / 4096 | 85.4% |
| maps/forest/textures/forest_root_albedo.png | (64,192,128,256) | 3880 / 4096 | 94.7% |
| maps/forest/textures/forest_root_albedo.png | (128,192,192,256) | 3279 / 4096 | 80.1% |
| maps/forest/textures/forest_root_albedo.png | (192,192,256,256) | 1992 / 4096 | 48.6% |
| maps/forest/textures/forest_shade_albedo.png | (0,0,64,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_shade_albedo.png | (64,0,128,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_shade_albedo.png | (128,0,192,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_shade_albedo.png | (192,0,256,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_shade_albedo.png | (0,64,64,128) | 2659 / 4096 | 64.9% |
| maps/forest/textures/forest_shade_albedo.png | (64,64,128,128) | 2744 / 4096 | 67.0% |
| maps/forest/textures/forest_shade_albedo.png | (128,64,192,128) | 2886 / 4096 | 70.5% |
| maps/forest/textures/forest_shade_albedo.png | (192,64,256,128) | 2597 / 4096 | 63.4% |
| maps/forest/textures/forest_shade_albedo.png | (0,128,64,192) | 3776 / 4096 | 92.2% |
| maps/forest/textures/forest_shade_albedo.png | (64,128,128,192) | 3803 / 4096 | 92.8% |
| maps/forest/textures/forest_shade_albedo.png | (128,128,192,192) | 3752 / 4096 | 91.6% |
| maps/forest/textures/forest_shade_albedo.png | (192,128,256,192) | 3829 / 4096 | 93.5% |
| maps/forest/textures/forest_shade_albedo.png | (0,192,64,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_shade_albedo.png | (64,192,128,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_shade_albedo.png | (128,192,192,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_shade_albedo.png | (192,192,256,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_sun_albedo.png | (0,0,64,64) | 4094 / 4096 | 100.0% |
| maps/forest/textures/forest_sun_albedo.png | (64,0,128,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_sun_albedo.png | (128,0,192,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_sun_albedo.png | (192,0,256,64) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_sun_albedo.png | (0,64,64,128) | 1656 / 4096 | 40.4% |
| maps/forest/textures/forest_sun_albedo.png | (64,64,128,128) | 2108 / 4096 | 51.5% |
| maps/forest/textures/forest_sun_albedo.png | (128,64,192,128) | 2213 / 4096 | 54.0% |
| maps/forest/textures/forest_sun_albedo.png | (192,64,256,128) | 2027 / 4096 | 49.5% |
| maps/forest/textures/forest_sun_albedo.png | (0,128,64,192) | 3831 / 4096 | 93.5% |
| maps/forest/textures/forest_sun_albedo.png | (64,128,128,192) | 3782 / 4096 | 92.3% |
| maps/forest/textures/forest_sun_albedo.png | (128,128,192,192) | 4041 / 4096 | 98.7% |
| maps/forest/textures/forest_sun_albedo.png | (192,128,256,192) | 4002 / 4096 | 97.7% |
| maps/forest/textures/forest_sun_albedo.png | (0,192,64,256) | 4096 / 4096 | 100.0% |
| maps/forest/textures/forest_sun_albedo.png | (64,192,128,256) | 4085 / 4096 | 99.7% |
| maps/forest/textures/forest_sun_albedo.png | (128,192,192,256) | 4082 / 4096 | 99.7% |
| maps/forest/textures/forest_sun_albedo.png | (192,192,256,256) | 4091 / 4096 | 99.9% |
| maps/forest/textures/forest_verge_albedo.png | (0,0,64,64) | 1986 / 4096 | 48.5% |
| maps/forest/textures/forest_verge_albedo.png | (64,0,128,64) | 1986 / 4096 | 48.5% |
| maps/forest/textures/forest_verge_albedo.png | (128,0,192,64) | 1986 / 4096 | 48.5% |
| maps/forest/textures/forest_verge_albedo.png | (192,0,256,64) | 1986 / 4096 | 48.5% |
| maps/forest/textures/forest_verge_albedo.png | (0,64,64,128) | 0 / 4096 | 0.0% |
| maps/forest/textures/forest_verge_albedo.png | (64,64,128,128) | 0 / 4096 | 0.0% |
| maps/forest/textures/forest_verge_albedo.png | (128,64,192,128) | 0 / 4096 | 0.0% |
| maps/forest/textures/forest_verge_albedo.png | (192,64,256,128) | 0 / 4096 | 0.0% |
| maps/forest/textures/forest_verge_albedo.png | (0,128,64,192) | 1536 / 4096 | 37.5% |
| maps/forest/textures/forest_verge_albedo.png | (64,128,128,192) | 1536 / 4096 | 37.5% |
| maps/forest/textures/forest_verge_albedo.png | (128,128,192,192) | 1536 / 4096 | 37.5% |
| maps/forest/textures/forest_verge_albedo.png | (192,128,256,192) | 1536 / 4096 | 37.5% |
| maps/forest/textures/forest_verge_albedo.png | (0,192,64,256) | 1216 / 4096 | 29.7% |
| maps/forest/textures/forest_verge_albedo.png | (64,192,128,256) | 1216 / 4096 | 29.7% |
| maps/forest/textures/forest_verge_albedo.png | (128,192,192,256) | 1216 / 4096 | 29.7% |
| maps/forest/textures/forest_verge_albedo.png | (192,192,256,256) | 1216 / 4096 | 29.7% |
| maps/marble/textures/marble_albedo.png | (0,0,80,64) | 0 / 5120 | 0.0% |
| maps/marble/textures/marble_albedo.png | (80,0,160,64) | 1797 / 5120 | 35.1% |
| maps/marble/textures/marble_albedo.png | (160,0,240,64) | 1798 / 5120 | 35.1% |
| maps/marble/textures/marble_albedo.png | (240,0,320,64) | 0 / 5120 | 0.0% |
| maps/marble/textures/marble_albedo.png | (0,64,80,128) | 1024 / 5120 | 20.0% |
| maps/marble/textures/marble_albedo.png | (80,64,160,128) | 4916 / 5120 | 96.0% |
| maps/marble/textures/marble_albedo.png | (160,64,240,128) | 4623 / 5120 | 90.3% |
| maps/marble/textures/marble_albedo.png | (240,64,320,128) | 1199 / 5120 | 23.4% |
| maps/marble/textures/marble_albedo.png | (0,128,80,192) | 5120 / 5120 | 100.0% |
| maps/marble/textures/marble_albedo.png | (80,128,160,192) | 4160 / 5120 | 81.2% |
| maps/marble/textures/marble_albedo.png | (160,128,240,192) | 3979 / 5120 | 77.7% |
| maps/marble/textures/marble_albedo.png | (240,128,320,192) | 5054 / 5120 | 98.7% |
| maps/marble/textures/marble_albedo.png | (0,192,80,256) | 5120 / 5120 | 100.0% |
| maps/marble/textures/marble_albedo.png | (80,192,160,256) | 5120 / 5120 | 100.0% |
| maps/marble/textures/marble_albedo.png | (160,192,240,256) | 5120 / 5120 | 100.0% |
| maps/marble/textures/marble_albedo.png | (240,192,320,256) | 5120 / 5120 | 100.0% |
| maps/marble/textures/marble_dark_albedo.png | (0,0,48,65) | 1690 / 3120 | 54.2% |
| maps/marble/textures/marble_dark_albedo.png | (48,0,96,65) | 3120 / 3120 | 100.0% |
| maps/marble/textures/marble_dark_albedo.png | (96,0,144,65) | 658 / 3120 | 21.1% |
| maps/marble/textures/marble_dark_albedo.png | (144,0,192,65) | 78 / 3120 | 2.5% |
| maps/marble/textures/marble_dark_albedo.png | (0,65,48,130) | 1675 / 3120 | 53.7% |
| maps/marble/textures/marble_dark_albedo.png | (48,65,96,130) | 3120 / 3120 | 100.0% |
| maps/marble/textures/marble_dark_albedo.png | (96,65,144,130) | 635 / 3120 | 20.4% |
| maps/marble/textures/marble_dark_albedo.png | (144,65,192,130) | 0 / 3120 | 0.0% |
| maps/marble/textures/marble_dark_albedo.png | (0,130,48,195) | 1678 / 3120 | 53.8% |
| maps/marble/textures/marble_dark_albedo.png | (48,130,96,195) | 3120 / 3120 | 100.0% |
| maps/marble/textures/marble_dark_albedo.png | (96,130,144,195) | 1406 / 3120 | 45.1% |
| maps/marble/textures/marble_dark_albedo.png | (144,130,192,195) | 2304 / 3120 | 73.8% |
| maps/marble/textures/marble_dark_albedo.png | (0,195,48,261) | 2067 / 3168 | 65.2% |
| maps/marble/textures/marble_dark_albedo.png | (48,195,96,261) | 3168 / 3168 | 100.0% |
| maps/marble/textures/marble_dark_albedo.png | (96,195,144,261) | 1704 / 3168 | 53.8% |
| maps/marble/textures/marble_dark_albedo.png | (144,195,192,261) | 3168 / 3168 | 100.0% |
| maps/marble/textures/marble_field_albedo.png | (0,0,64,64) | 4096 / 4096 | 100.0% |
| maps/marble/textures/marble_field_albedo.png | (64,0,128,64) | 4096 / 4096 | 100.0% |
| maps/marble/textures/marble_field_albedo.png | (128,0,192,64) | 4096 / 4096 | 100.0% |
| maps/marble/textures/marble_field_albedo.png | (192,0,256,64) | 4096 / 4096 | 100.0% |
| maps/marble/textures/marble_field_albedo.png | (0,64,64,128) | 4096 / 4096 | 100.0% |
| maps/marble/textures/marble_field_albedo.png | (64,64,128,128) | 4096 / 4096 | 100.0% |
| maps/marble/textures/marble_field_albedo.png | (128,64,192,128) | 4096 / 4096 | 100.0% |
| maps/marble/textures/marble_field_albedo.png | (192,64,256,128) | 4096 / 4096 | 100.0% |
| maps/marble/textures/marble_field_albedo.png | (0,128,64,192) | 4096 / 4096 | 100.0% |
| maps/marble/textures/marble_field_albedo.png | (64,128,128,192) | 4096 / 4096 | 100.0% |
| maps/marble/textures/marble_field_albedo.png | (128,128,192,192) | 4096 / 4096 | 100.0% |
| maps/marble/textures/marble_field_albedo.png | (192,128,256,192) | 4096 / 4096 | 100.0% |
| maps/marble/textures/marble_field_albedo.png | (0,192,64,256) | 4096 / 4096 | 100.0% |
| maps/marble/textures/marble_field_albedo.png | (64,192,128,256) | 4096 / 4096 | 100.0% |
| maps/marble/textures/marble_field_albedo.png | (128,192,192,256) | 4096 / 4096 | 100.0% |
| maps/marble/textures/marble_field_albedo.png | (192,192,256,256) | 4096 / 4096 | 100.0% |
| maps/marble/textures/marble_stone_albedo.png | (0,0,32,65) | 2080 / 2080 | 100.0% |
| maps/marble/textures/marble_stone_albedo.png | (32,0,64,65) | 2080 / 2080 | 100.0% |
| maps/marble/textures/marble_stone_albedo.png | (64,0,96,65) | 2080 / 2080 | 100.0% |
| maps/marble/textures/marble_stone_albedo.png | (96,0,128,65) | 2080 / 2080 | 100.0% |
| maps/marble/textures/marble_stone_albedo.png | (0,65,32,130) | 2080 / 2080 | 100.0% |
| maps/marble/textures/marble_stone_albedo.png | (32,65,64,130) | 2080 / 2080 | 100.0% |
| maps/marble/textures/marble_stone_albedo.png | (64,65,96,130) | 2080 / 2080 | 100.0% |
| maps/marble/textures/marble_stone_albedo.png | (96,65,128,130) | 2080 / 2080 | 100.0% |
| maps/marble/textures/marble_stone_albedo.png | (0,130,32,195) | 2080 / 2080 | 100.0% |
| maps/marble/textures/marble_stone_albedo.png | (32,130,64,195) | 2080 / 2080 | 100.0% |
| maps/marble/textures/marble_stone_albedo.png | (64,130,96,195) | 2080 / 2080 | 100.0% |
| maps/marble/textures/marble_stone_albedo.png | (96,130,128,195) | 2080 / 2080 | 100.0% |
| maps/marble/textures/marble_stone_albedo.png | (0,195,32,261) | 2112 / 2112 | 100.0% |
| maps/marble/textures/marble_stone_albedo.png | (32,195,64,261) | 2112 / 2112 | 100.0% |
| maps/marble/textures/marble_stone_albedo.png | (64,195,96,261) | 2112 / 2112 | 100.0% |
| maps/marble/textures/marble_stone_albedo.png | (96,195,128,261) | 2112 / 2112 | 100.0% |
| props/textures/speed_orb_albedo.png | (0,0,16,16) | 32 / 256 | 12.5% |
| props/textures/speed_orb_albedo.png | (16,0,32,16) | 181 / 256 | 70.7% |
| props/textures/speed_orb_albedo.png | (32,0,48,16) | 240 / 256 | 93.8% |
| props/textures/speed_orb_albedo.png | (48,0,64,16) | 154 / 256 | 60.2% |
| props/textures/speed_orb_albedo.png | (0,16,16,32) | 203 / 256 | 79.3% |
| props/textures/speed_orb_albedo.png | (16,16,32,32) | 256 / 256 | 100.0% |
| props/textures/speed_orb_albedo.png | (32,16,48,32) | 256 / 256 | 100.0% |
| props/textures/speed_orb_albedo.png | (48,16,64,32) | 224 / 256 | 87.5% |
| props/textures/speed_orb_albedo.png | (0,32,16,48) | 212 / 256 | 82.8% |
| props/textures/speed_orb_albedo.png | (16,32,32,48) | 256 / 256 | 100.0% |
| props/textures/speed_orb_albedo.png | (32,32,48,48) | 256 / 256 | 100.0% |
| props/textures/speed_orb_albedo.png | (48,32,64,48) | 182 / 256 | 71.1% |
| props/textures/speed_orb_albedo.png | (0,48,16,64) | 119 / 256 | 46.5% |
| props/textures/speed_orb_albedo.png | (16,48,32,64) | 116 / 256 | 45.3% |
| props/textures/speed_orb_albedo.png | (32,48,48,64) | 97 / 256 | 37.9% |
| props/textures/speed_orb_albedo.png | (48,48,64,64) | 39 / 256 | 15.2% |
| weapons/textures/rifle_hell_albedo.png | (0,0,32,32) | 961 / 1024 | 93.8% |
| weapons/textures/rifle_hell_albedo.png | (32,0,64,32) | 961 / 1024 | 93.8% |
| weapons/textures/rifle_hell_albedo.png | (64,0,96,32) | 961 / 1024 | 93.8% |
| weapons/textures/rifle_hell_albedo.png | (96,0,128,32) | 961 / 1024 | 93.8% |
| weapons/textures/rifle_hell_albedo.png | (0,32,32,64) | 922 / 1024 | 90.0% |
| weapons/textures/rifle_hell_albedo.png | (32,32,64,64) | 810 / 1024 | 79.1% |
| weapons/textures/rifle_hell_albedo.png | (64,32,96,64) | 961 / 1024 | 93.8% |
| weapons/textures/rifle_hell_albedo.png | (96,32,128,64) | 961 / 1024 | 93.8% |
| weapons/textures/rifle_hell_albedo.png | (0,64,32,96) | 0 / 1024 | 0.0% |
| weapons/textures/rifle_hell_albedo.png | (32,64,64,96) | 658 / 1024 | 64.3% |
| weapons/textures/rifle_hell_albedo.png | (64,64,96,96) | 896 / 1024 | 87.5% |
| weapons/textures/rifle_hell_albedo.png | (96,64,128,96) | 480 / 1024 | 46.9% |
| weapons/textures/rifle_hell_albedo.png | (0,96,32,128) | 0 / 1024 | 0.0% |
| weapons/textures/rifle_hell_albedo.png | (32,96,64,128) | 629 / 1024 | 61.4% |
| weapons/textures/rifle_hell_albedo.png | (64,96,96,128) | 896 / 1024 | 87.5% |
| weapons/textures/rifle_hell_albedo.png | (96,96,128,128) | 384 / 1024 | 37.5% |

### hell_props_albedo quarters (PROPS_QUARTER, Blender u0,v0; image rows are flipped v)

| quarter | image rect (x0,y0,x1,y1) | texels touched |
|---|---|---|
| demon_pad | (0,32,32,64) | 931 / 1024 |
| portal | (32,32,64,64) | 961 / 1024 |
| torch | (0,0,32,32) | 826 / 1024 |
| lava_tile | (32,0,64,32) | 783 / 1024 |

### forest_atlas_albedo zones (forest_tree_build.py ZONES, Blender u0,v0,u1,v1; image rows are flipped v)

| zone | image rect (x0,y0,x1,y1) | texels touched | verdict |
|---|---|---|---|
| grass | (0,192,128,256) | 0 / 8192 | DEAD |
| verge | (0,160,128,192) | 0 / 4096 | DEAD |
| path | (0,128,128,160) | 0 / 4096 | DEAD |
| leaf | (128,0,256,128) | 15866 / 16384 | LIVE |
| shade | (0,64,64,128) | 3712 / 4096 | LIVE |
| sun | (64,64,128,128) | 3737 / 4096 | LIVE |
| fern | (0,0,64,64) | 0 / 4096 | DEAD |
| edge | (64,0,128,64) | 0 / 4096 | DEAD |
| bark | (128,192,192,256) | 3844 / 4096 | LIVE |
| earth | (192,192,256,256) | 0 / 4096 | DEAD |
| cell | (128,128,192,192) | 0 / 4096 | DEAD |
| root | (192,128,256,192) | 3792 / 4096 | LIVE |

### glb instances reached

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

glbs not reached by any live scene: characters/models/runner.glb, maps/bentham_ring/models/block.glb, maps/bentham_ring/models/boulder.glb, maps/bentham_ring/models/rock_bars.glb, maps/bentham_ring/models/rock_wall.glb, maps/bentham_ring/models/slab.glb, maps/bentham_ring/models/spire.glb, maps/forest/models/forest_rock_slab.glb, maps/forest/models/forest_thorns.glb, maps/forest/models/forest_tree_prop_a.glb, maps/forest/models/forest_tree_prop_b.glb, maps/forest/models/forest_tree_prop_c.glb, maps/marble/models/marble_arch.glb, maps/marble/models/marble_column.glb, maps/marble/models/marble_column_broken.glb, maps/marble/models/marble_spikes.glb, maps/marble/models/marble_spikes_strip.glb, tower/models/tower2.glb

### Texture users (every glb/material/slot that references the file, reached or not)

- `characters/textures/prisoner2_albedo.png`: characters/models/prisoner2.glb:Prisoner2Skin[albedo]; characters/models/prisoner2.glb:Shirt[albedo]
- `hub/textures/hub_stone_albedo.png`: hub/models/hub_base.glb:HubStone[albedo]
- `maps/bentham_ring/textures/crack_glow_albedo.png`: maps/bentham_ring/models/map_base_s1.glb:HellGlow[albedo]; maps/bentham_ring/models/map_base_s1.glb:HellGlow[emissive]; maps/bentham_ring/models/map_base_s2.glb:HellGlow[albedo]; maps/bentham_ring/models/map_base_s2.glb:HellGlow[emissive]; maps/bentham_ring/models/map_base_s3.glb:HellGlow[albedo]; maps/bentham_ring/models/map_base_s3.glb:HellGlow[emissive]; maps/bentham_ring/models/map_base_s3.glb:LavaCrack[albedo]; maps/bentham_ring/models/map_base_s3.glb:LavaCrack[emissive]; maps/bentham_ring/models/map_base_s4.glb:HellGlow[albedo]; maps/bentham_ring/models/map_base_s4.glb:HellGlow[emissive]; maps/bentham_ring/models/map_base_s4.glb:LavaCrack[albedo]; maps/bentham_ring/models/map_base_s4.glb:LavaCrack[emissive]; maps/bentham_ring/models/map_base_s5.glb:HellGlow[albedo]; maps/bentham_ring/models/map_base_s5.glb:HellGlow[emissive]
- `maps/bentham_ring/textures/hell_props_albedo.png`: maps/bentham_ring/models/portal.glb:PortalGlow[albedo]; maps/bentham_ring/models/portal.glb:PortalGlow[emissive]
- `maps/bentham_ring/textures/hell_rock_albedo.png`: hub/models/hub_base.glb:HellRock[albedo]; maps/bentham_ring/models/map_base_cover_s2.glb:HellEmber[albedo]; maps/bentham_ring/models/map_base_cover_s2.glb:HellShade[albedo]; maps/bentham_ring/models/map_base_cover_s4.glb:HellEmber[albedo]; maps/bentham_ring/models/map_base_cover_s4.glb:HellShade[albedo]; maps/bentham_ring/models/map_base_gate.glb:HellRock.001[albedo]; maps/bentham_ring/models/map_base_gate.glb:HellShade.001[albedo]; maps/bentham_ring/models/map_base_lip013.glb:HellRock[albedo]; maps/bentham_ring/models/map_base_lip013.glb:HellShade[albedo]; maps/bentham_ring/models/map_base_lip066.glb:HellRock[albedo]; maps/bentham_ring/models/map_base_lip066.glb:HellShade[albedo]; maps/bentham_ring/models/map_base_lip139.glb:HellRock[albedo]; maps/bentham_ring/models/map_base_lip139.glb:HellShade[albedo]; maps/bentham_ring/models/map_base_lip204.glb:HellRock[albedo]; maps/bentham_ring/models/map_base_lip204.glb:HellShade[albedo]; maps/bentham_ring/models/map_base_lip286.glb:HellRock[albedo]; maps/bentham_ring/models/map_base_lip286.glb:HellShade[albedo]; maps/bentham_ring/models/map_base_s1.glb:HellEmber[albedo]; maps/bentham_ring/models/map_base_s1.glb:HellRock[albedo]; maps/bentham_ring/models/map_base_s1.glb:HellShade[albedo]; maps/bentham_ring/models/map_base_s2.glb:HellEmber[albedo]; maps/bentham_ring/models/map_base_s2.glb:HellRock[albedo]; maps/bentham_ring/models/map_base_s2.glb:HellShade[albedo]; maps/bentham_ring/models/map_base_s3.glb:HellEmber[albedo]; maps/bentham_ring/models/map_base_s3.glb:HellRock[albedo]; maps/bentham_ring/models/map_base_s3.glb:HellShade[albedo]; maps/bentham_ring/models/map_base_s4.glb:HellEmber[albedo]; maps/bentham_ring/models/map_base_s4.glb:HellRock[albedo]; maps/bentham_ring/models/map_base_s4.glb:HellShade[albedo]; maps/bentham_ring/models/map_base_s5.glb:HellEmber[albedo]; maps/bentham_ring/models/map_base_s5.glb:HellRock[albedo]; maps/bentham_ring/models/map_base_s5.glb:HellShade[albedo]; maps/bentham_ring/models/portal.glb:HellRock[albedo]; tower/models/tower.glb:HellRock[albedo]; tower/models/tower_arches.glb:HellRock[albedo]; tower/models/tower_hollow.glb:HellRock[albedo]; tower/models/tower_interior.glb:HellRock.001[albedo]
- `maps/bentham_ring/textures/lava_albedo.png`: hub/models/hub_base.glb:Lava[albedo]; hub/models/hub_base.glb:Lava[emissive]; maps/bentham_ring/models/map_base_s1.glb:LavaSea[albedo]; maps/bentham_ring/models/map_base_s2.glb:LavaRiver[albedo]; maps/bentham_ring/models/map_base_s2.glb:LavaSea[albedo]; maps/bentham_ring/models/map_base_s3.glb:LavaSea[albedo]; maps/bentham_ring/models/map_base_s4.glb:LavaRiver[albedo]; maps/bentham_ring/models/map_base_s4.glb:LavaSea[albedo]; maps/bentham_ring/models/map_base_s5.glb:LavaRiver[albedo]; maps/bentham_ring/models/map_base_s5.glb:LavaSea[albedo]
- `maps/bentham_ring/textures/map_base_lava_emissive.png`: maps/bentham_ring/models/map_base_s1.glb:LavaSea[emissive]; maps/bentham_ring/models/map_base_s2.glb:LavaRiver[emissive]; maps/bentham_ring/models/map_base_s2.glb:LavaSea[emissive]; maps/bentham_ring/models/map_base_s3.glb:LavaSea[emissive]; maps/bentham_ring/models/map_base_s4.glb:LavaRiver[emissive]; maps/bentham_ring/models/map_base_s4.glb:LavaSea[emissive]; maps/bentham_ring/models/map_base_s5.glb:LavaRiver[emissive]; maps/bentham_ring/models/map_base_s5.glb:LavaSea[emissive]
- `maps/forest/textures/forest_atlas_albedo.png`: maps/forest/models/forest_bush_low.glb:ForestAtlas[albedo]; maps/forest/models/forest_bush_tall.glb:ForestAtlas[albedo]; maps/forest/models/forest_canopy.glb:ForestAtlas[albedo]; maps/forest/models/forest_portal.glb:ForestPortalAtlas[albedo]; maps/forest/models/forest_tree.glb:ForestAtlas[albedo]
- `maps/forest/textures/forest_bark_albedo.png`: hub/models/hub_base.glb:ForestBark[albedo]; maps/forest/models/forest.glb:forest_bark[albedo]; maps/forest/models/forest_bars.glb:forest_bark[albedo]
- `maps/forest/textures/forest_dark_albedo.png`: hub/models/hub_base.glb:ForestDark[albedo]; maps/forest/models/forest.glb:forest_cell[albedo]; maps/forest/models/forest.glb:forest_lamp[albedo]
- `maps/forest/textures/forest_earth_albedo.png`: maps/forest/models/forest.glb:forest_earth[albedo]
- `maps/forest/textures/forest_edge_albedo.png`: maps/forest/models/forest.glb:forest_edge[albedo]
- `maps/forest/textures/forest_fern_albedo.png`: hub/models/hub_base.glb:ForestFern[albedo]; maps/forest/models/forest.glb:forest_fern[albedo]
- `maps/forest/textures/forest_grass_albedo.png`: hub/models/hub_base.glb:ForestGrass[albedo]; maps/forest/models/forest.glb:forest_grass[albedo]
- `maps/forest/textures/forest_lamp_emissive.png`: maps/forest/models/forest.glb:forest_lamp[emissive]
- `maps/forest/textures/forest_leaf_albedo.png`: hub/models/hub_base.glb:ForestLeaf[albedo]; maps/forest/models/forest.glb:forest_leaf[albedo]; maps/forest/models/forest_bars.glb:forest_leaf[albedo]
- `maps/forest/textures/forest_path_albedo.png`: hub/models/hub_base.glb:ForestPath[albedo]; maps/forest/models/forest.glb:forest_path[albedo]
- `maps/forest/textures/forest_portal_swirl_albedo.png`: maps/forest/models/forest_portal.glb:ForestPortalSwirl[albedo]; maps/forest/models/forest_portal.glb:ForestPortalSwirl[emissive]
- `maps/forest/textures/forest_rock_albedo.png`: maps/forest/models/forest_rock_boulder.glb:ForestGranite[albedo]; maps/forest/models/forest_rock_outcrop.glb:ForestGranite[albedo]
- `maps/forest/textures/forest_root_albedo.png`: maps/forest/models/forest.glb:forest_root[albedo]; maps/forest/models/forest_bars.glb:forest_root[albedo]
- `maps/forest/textures/forest_shade_albedo.png`: maps/forest/models/forest.glb:forest_shade[albedo]
- `maps/forest/textures/forest_sun_albedo.png`: maps/forest/models/forest.glb:forest_sun[albedo]
- `maps/forest/textures/forest_verge_albedo.png`: maps/forest/models/forest.glb:forest_verge[albedo]
- `maps/marble/textures/marble_albedo.png`: hub/models/hub_base.glb:Marble[albedo]; maps/marble/models/marble.glb:marble_band[albedo]; maps/marble/models/marble.glb:marble_column[albedo]; maps/marble/models/marble.glb:marble_dome[albedo]; maps/marble/models/marble.glb:marble_floor[albedo]; maps/marble/models/marble.glb:marble_frieze[albedo]; maps/marble/models/marble.glb:marble_spike[albedo]; maps/marble/models/marble_bars.glb:marble_bars_band[albedo]; maps/marble/models/marble_bars.glb:marble_bars_column[albedo]; maps/marble/models/marble_portal.glb:Marble[albedo]; maps/marble/models/marble_portal.glb:MarbleGlow[albedo]; maps/marble/models/marble_portal.glb:MarbleGlow[emissive]; maps/marble/models/marble_tower.glb:marble_tower_band[albedo]; maps/marble/models/marble_tower.glb:marble_tower_coffer[albedo]; maps/marble/models/marble_tower.glb:marble_tower_column[albedo]; maps/marble/models/marble_tower.glb:marble_tower_floor[albedo]; maps/marble/models/marble_tower.glb:marble_tower_medallion[albedo]
- `maps/marble/textures/marble_dark_albedo.png`: hub/models/hub_base.glb:MarbleDark[albedo]; maps/marble/models/marble.glb:marble_cellin[albedo]; maps/marble/models/marble.glb:marble_iron[albedo]; maps/marble/models/marble_bars.glb:marble_bars_iron[albedo]; maps/marble/models/marble_tower.glb:marble_tower_iron[albedo]
- `maps/marble/textures/marble_field_albedo.png`: maps/marble/models/marble.glb:marble_field[albedo]
- `maps/marble/textures/marble_stone_albedo.png`: hub/models/hub_base.glb:Marble_marble[albedo]; hub/models/hub_base.glb:Marble_marble2[albedo]; hub/models/hub_base.glb:Marble_plinth[albedo]; hub/models/hub_base.glb:Marble_shade[albedo]; maps/marble/models/marble.glb:marble_marble[albedo]; maps/marble/models/marble.glb:marble_plinth[albedo]; maps/marble/models/marble.glb:marble_shade[albedo]; maps/marble/models/marble_bars.glb:marble_bars_marble[albedo]; maps/marble/models/marble_bars.glb:marble_bars_marble2[albedo]; maps/marble/models/marble_bars.glb:marble_bars_plinth[albedo]; maps/marble/models/marble_bars.glb:marble_bars_shade[albedo]; maps/marble/models/marble_portal.glb:Marble_marble[albedo]; maps/marble/models/marble_portal.glb:Marble_marble2[albedo]; maps/marble/models/marble_portal.glb:Marble_plinth[albedo]; maps/marble/models/marble_portal.glb:Marble_shade[albedo]; maps/marble/models/marble_tower.glb:marble_tower_dome[albedo]; maps/marble/models/marble_tower.glb:marble_tower_marble2[albedo]; maps/marble/models/marble_tower.glb:marble_tower_plinth[albedo]; maps/marble/models/marble_tower.glb:marble_tower_shade[albedo]; maps/marble/models/marble_tower.glb:marble_tower_stone[albedo]
- `props/textures/speed_orb_albedo.png`: props/models/speed_orb.glb:SpeedOrb[albedo]; props/models/speed_orb.glb:SpeedOrb[emissive]
- `weapons/textures/rifle_hell_albedo.png`: weapons/models/rifle.glb:RifleWarden[albedo]

### Unreached glbs and the textures they reference

- `characters/models/runner.glb`: no textures
- `maps/bentham_ring/models/block.glb`: maps/bentham_ring/textures/hell_rock_albedo.png
- `maps/bentham_ring/models/boulder.glb`: maps/bentham_ring/textures/hell_rock_albedo.png
- `maps/bentham_ring/models/rock_bars.glb`: maps/bentham_ring/textures/hell_rock_albedo.png
- `maps/bentham_ring/models/rock_wall.glb`: maps/bentham_ring/textures/hell_rock_albedo.png
- `maps/bentham_ring/models/slab.glb`: maps/bentham_ring/textures/hell_rock_albedo.png
- `maps/bentham_ring/models/spire.glb`: maps/bentham_ring/textures/hell_rock_albedo.png
- `maps/forest/models/forest_rock_slab.glb`: maps/forest/textures/forest_rock_albedo.png
- `maps/forest/models/forest_thorns.glb`: maps/forest/textures/forest_atlas_albedo.png
- `maps/forest/models/forest_tree_prop_a.glb`: maps/forest/textures/forest_atlas_albedo.png
- `maps/forest/models/forest_tree_prop_b.glb`: maps/forest/textures/forest_atlas_albedo.png
- `maps/forest/models/forest_tree_prop_c.glb`: maps/forest/textures/forest_atlas_albedo.png
- `maps/marble/models/marble_arch.glb`: maps/marble/textures/marble_albedo.png, maps/marble/textures/marble_stone_albedo.png
- `maps/marble/models/marble_column.glb`: maps/marble/textures/marble_albedo.png, maps/marble/textures/marble_stone_albedo.png
- `maps/marble/models/marble_column_broken.glb`: maps/marble/textures/marble_albedo.png, maps/marble/textures/marble_stone_albedo.png
- `maps/marble/models/marble_spikes.glb`: maps/marble/textures/marble_albedo.png, maps/marble/textures/marble_stone_albedo.png
- `maps/marble/models/marble_spikes_strip.glb`: maps/marble/textures/marble_albedo.png, maps/marble/textures/marble_stone_albedo.png
- `tower/models/tower2.glb`: maps/bentham_ring/textures/hell_rock_albedo.png

Triangles whose UV bbox spans a whole tile in both axes were counted as covering the whole file: maps/bentham_ring/textures/hell_rock_albedo.png[albedo]=68, maps/bentham_ring/textures/lava_albedo.png[albedo]=2, maps/bentham_ring/textures/map_base_lava_emissive.png[emissive]=2, maps/marble/textures/marble_stone_albedo.png[albedo]=160

### Every texture file the game ships, per home, and what uses it

### characters (1 files; sheet SHEET_characters.png)

- `prisoner2_albedo.png` (albedo): 1602 tris, 5 m2, 594/1024 texels -- Prisoner2Skin, Shirt in prisoner2.glb; scenes bots, hub, match

### hub (1 files; sheet SHEET_hub.png)

- `hub_stone_albedo.png` (albedo): 9980 tris, 15960 m2, 14862/16384 texels -- HubStone in hub_base.glb; scenes hub

### maps/bentham_ring (5 files; sheet SHEET_bentham_ring.png)

- `crack_glow_albedo.png` (albedo+emissive): 9782 tris, 19357 m2, 1860/2048 texels -- HellGlow, LavaCrack in map_base_s1.glb, map_base_s2.glb, map_base_s3.glb, map_base_s4.glb, map_base_s5.glb; scenes bentham_ring
- `hell_props_albedo.png` (albedo+emissive): 26 tris, 16 m2, 3501/4096 texels -- PortalGlow in portal.glb; scenes bentham_ring
- `hell_rock_albedo.png` (albedo): 83225 tris, 209467 m2, 65536/65536 texels -- HellEmber, HellRock, HellRock.001, HellShade, HellShade.001 in hub_base.glb, map_base_cover_s2.glb, map_base_cover_s4.glb, map_base_gate.glb, map_base_lip013.glb, map_base_lip066.glb, map_base_lip139.glb, map_base_lip204.glb, map_base_lip286.glb, map_base_s1.glb, map_base_s2.glb, map_base_s3.glb, map_base_s4.glb, map_base_s5.glb, portal.glb, tower.glb, tower_arches.glb, tower_hollow.glb, tower_interior.glb; scenes bentham_ring, hub, main_menu
- `lava_albedo.png` (albedo+emissive): 15800 tris, 11336 m2, 65536/65536 texels -- Lava, LavaRiver, LavaSea in hub_base.glb, map_base_s1.glb, map_base_s2.glb, map_base_s3.glb, map_base_s4.glb, map_base_s5.glb; scenes bentham_ring, hub
- `map_base_lava_emissive.png` (emissive): 15760 tris, 11326 m2, 65536/65536 texels -- LavaRiver, LavaSea in map_base_s1.glb, map_base_s2.glb, map_base_s3.glb, map_base_s4.glb, map_base_s5.glb; scenes bentham_ring

### maps/forest (16 files; sheet SHEET_forest.png)

- `forest_atlas_albedo.png` (albedo): 187302 tris, 78062 m2, 30951/65536 texels -- ForestAtlas, ForestPortalAtlas in forest_bush_low.glb, forest_bush_tall.glb, forest_canopy.glb, forest_portal.glb, forest_tree.glb; scenes forest
- `forest_bark_albedo.png` (albedo): 20031 tris, 2056 m2, 65230/65536 texels -- ForestBark, forest_bark in hub_base.glb, forest.glb, forest_bars.glb; scenes forest, hub
- `forest_dark_albedo.png` (albedo): 59820 tris, 20673 m2, 65536/65536 texels -- ForestDark, forest_cell, forest_lamp in hub_base.glb, forest.glb; scenes forest, hub
- `forest_earth_albedo.png` (albedo): 9108 tris, 8712 m2, 65536/65536 texels -- forest_earth in forest.glb; scenes forest
- `forest_edge_albedo.png` (albedo): 6382 tris, 499 m2, 22765/65536 texels -- forest_edge in forest.glb; scenes forest
- `forest_fern_albedo.png` (albedo): 10704 tris, 127 m2, 28984/65536 texels -- ForestFern, forest_fern in hub_base.glb, forest.glb; scenes forest, hub
- `forest_grass_albedo.png` (albedo): 2144 tris, 1579 m2, 65536/65536 texels -- ForestGrass, forest_grass in hub_base.glb, forest.glb; scenes forest, hub
- `forest_lamp_emissive.png` (emissive): 5058 tris, 4002 m2, 65536/65536 texels -- forest_lamp in forest.glb; scenes forest
- `forest_leaf_albedo.png` (albedo): 10975 tris, 9400 m2, 65536/65536 texels -- ForestLeaf, forest_leaf in hub_base.glb, forest.glb, forest_bars.glb; scenes forest, hub
- `forest_path_albedo.png` (albedo): 1062 tris, 1050 m2, 65536/65536 texels -- ForestPath, forest_path in hub_base.glb, forest.glb; scenes forest, hub
- `forest_portal_swirl_albedo.png` (albedo+emissive): 90 tris, 16 m2, 3666/4096 texels -- ForestPortalSwirl in forest_portal.glb; scenes forest
- `forest_rock_albedo.png` (albedo): 2156 tris, 155 m2, 10137/16384 texels -- ForestGranite in forest_rock_boulder.glb, forest_rock_outcrop.glb; scenes forest
- `forest_root_albedo.png` (albedo): 2730 tris, 584 m2, 52339/65536 texels -- forest_root in forest.glb, forest_bars.glb; scenes forest
- `forest_shade_albedo.png` (albedo): 5388 tris, 4676 m2, 58814/65536 texels -- forest_shade in forest.glb; scenes forest
- `forest_sun_albedo.png` (albedo): 818 tris, 745 m2, 56396/65536 texels -- forest_sun in forest.glb; scenes forest
- `forest_verge_albedo.png` (albedo): 960 tris, 1189 m2, 18952/65536 texels -- forest_verge in forest.glb; scenes forest

### maps/marble (4 files; sheet SHEET_marble.png)

- `marble_albedo.png` (albedo+emissive): 12044 tris, 21397 m2, 54150/81920 texels -- Marble, MarbleGlow, marble_band, marble_bars_band, marble_bars_column, marble_column, marble_dome, marble_floor, marble_frieze, marble_spike, marble_tower_band, marble_tower_coffer, marble_tower_column, marble_tower_floor, marble_tower_medallion in hub_base.glb, marble.glb, marble_bars.glb, marble_portal.glb, marble_tower.glb; scenes hub, marble
- `marble_dark_albedo.png` (albedo): 18858 tris, 13773 m2, 29591/50112 texels -- MarbleDark, marble_bars_iron, marble_cellin, marble_iron, marble_tower_iron in hub_base.glb, marble.glb, marble_bars.glb, marble_tower.glb; scenes hub, marble
- `marble_field_albedo.png` (albedo): 7104 tris, 11050 m2, 65536/65536 texels -- marble_field in marble.glb; scenes marble
- `marble_stone_albedo.png` (albedo): 43812 tris, 49390 m2, 33408/33408 texels -- Marble_marble, Marble_marble2, Marble_plinth, Marble_shade, marble_bars_marble, marble_bars_marble2, marble_bars_plinth, marble_bars_shade, marble_marble, marble_plinth, marble_shade, marble_tower_dome, marble_tower_marble2, marble_tower_plinth, marble_tower_shade, marble_tower_stone in hub_base.glb, marble.glb, marble_bars.glb, marble_portal.glb, marble_tower.glb; scenes hub, marble

### props (1 files; sheet SHEET_props.png)

- `speed_orb_albedo.png` (albedo+emissive): 20 tris, 3 m2, 2823/4096 texels -- SpeedOrb in speed_orb.glb; scenes bentham_ring

### weapons (1 files; sheet SHEET_weapons.png)

- `rifle_hell_albedo.png` (albedo): 566 tris, 0 m2, 11441/16384 texels -- RifleWarden in rifle.glb; scenes match

### Before the crop: hell_props_albedo quarters (PROPS_QUARTER, Blender u0,v0; image rows are flipped v)

| quarter | image rect (x0,y0,x1,y1) | texels touched |
|---|---|---|
| demon_pad | (0,64,64,128) | 0 / 4096 |
| portal | (64,64,128,128) | 3501 / 4096 |
| torch | (0,0,64,64) | 0 / 4096 |
| lava_tile | (64,0,128,64) | 0 / 4096 |
