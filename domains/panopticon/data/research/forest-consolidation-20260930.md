# Forest texture consolidation 2026-09-30

Ryan: "without changing the lighting, give the same audit you did for hell and marble. it can be so massively
consolidated it's not even funny, there's like 20 wood, grass, and dirt textures." Hell's end state is one
texture per material; the forest gets the same.

## Phase 1: what the forest samples now (main c1929fb)

Method as texture-audit-20260930.md (scene graph from the entry points, every glb primitive, world area through
node + tscn transforms), extended per glb/material; atlas zones by each triangle's UV centroid. Linear means
over the whole tile (or zone).

### Texture files (maps/forest/textures, 16 + SHEET_forest)

| file | px | glb : material (live tris / m2) | linear mean RGB |
|---|---|---|---|
| forest_atlas_albedo | 256x128, 5 zones | forest_tree ForestAtlas 20356 / 19693; forest_canopy ForestAtlas 152638 / 63200; forest_bush_low 8272 / 164 (x11); forest_bush_tall 4784 / 195 (x4); forest_portal ForestPortalAtlas 1252 / 28; unreached: forest_thorns, forest_tree_prop_a/b/c | per zone below |
| forest_bark_albedo | 256 | forest forest_bark 16464 / 1898; forest_bars forest_bark 3327 / 151; hub_base ForestBark 240 / 7 | .0119 .0084 .0042 |
| forest_root_albedo | 256 | forest forest_root 760 / 537; forest_bars forest_root 1970 / 47 | .0139 .0075 .0034 |
| forest_grass_albedo | 256 | forest forest_grass 1286 / 1075; hub_base ForestGrass 858 / 504 | .0354 .0559 .0037 |
| forest_verge_albedo | 256 | forest forest_verge 960 / 1189 | .0360 .0473 .0038 |
| forest_edge_albedo | 256 | forest forest_edge 6382 / 499 | .0124 .0224 .0031 |
| forest_path_albedo | 256 | forest forest_path 960 / 981; hub_base ForestPath 102 / 69 | .0254 .0209 .0049 |
| forest_earth_albedo | 256 | forest forest_earth 9108 / 8712 | .0066 .0044 .0023 |
| forest_leaf_albedo | 256 | forest forest_leaf 10174 / 8766; forest_bars forest_leaf 423 / 8; hub_base ForestLeaf 378 / 626 | .0073 .0134 .0029 |
| forest_shade_albedo | 256 | forest forest_shade 5388 / 4676 (the lane roof) | .0044 .0093 .0028 |
| forest_sun_albedo | 256 | forest forest_sun 818 / 745 | .0294 .0479 .0052 |
| forest_fern_albedo | 256 | forest forest_fern 10140 / 121; hub_base ForestFern 564 / 6 | .0065 .0160 .0030 |
| forest_dark_albedo | 256 | forest forest_cell 8932 / 3749, forest_lamp 5058 / 4002; hub_base ForestDark 12 / 9 | .0005 .0005 .0003 |
| forest_rock_albedo | 128, 4 zones | forest_rock_boulder ForestGranite 2016 / 145 (x14); forest_rock_outcrop 140 / 10; unreached forest_rock_slab | per zone below |
| forest_lamp_emissive | 256 | forest forest_lamp (emission) 5058 / 4002 | emission: lighting, not touched |
| forest_portal_swirl_albedo | 64 | forest_portal ForestPortalSwirl 90 / 16 (albedo + emission) | its own art |

### Atlas zones (forest_atlas_albedo, forest_tree_build.ZONES) and rock zones (forest_rock_build.ZONES)

| zone | used by (tris / m2) | linear mean |
|---|---|---|
| atlas leaf | tree 9517 / 13482, canopy 53678 / 49956, bushes 448 / 21, portal 432 / 7, prop_a 315 / 70 | .0080 .0145 .0030 |
| atlas shade | tree 2355 / 1297, bushes 508 / 13, thorns 1638 / 30 | .0020 .0033 .0013 |
| atlas sun | tree 3160 / 2333, bushes 512 / 25 | .0304 .0490 .0053 |
| atlas bark | tree 4988 / 1802, canopy 98960 / 13244, bushes 480 / 5, portal 820 / 22, prop_a 535 / 23 | .0116 .0082 .0041 |
| atlas root | tree 336 / 779, thorns 68 / 6 | .0139 .0076 .0034 |
| rock granite | boulder 72 / 5, outcrop 48 / 2, slab 64 / 7 (per instance) | .0317 .0346 .0212 |
| rock shade | boulder 12 / 2, outcrop 22 / 3, slab 30 / 4 | .0132 .0152 .0106 |
| rock moss | boulder 38 / 2, outcrop 58 / 4, slab 14 / 1 | .0061 .0124 .0029 |
| rock lichen | boulder 22 / 1, outcrop 12 / 1, slab 12 / 1 | .0297 .0333 .0190 |

## Groups, keepers, and what maps onto them

Keeper = the best-looking existing tile, and the brightest of its group so every duplicate is the keeper times a
factor <= 1 (glTF clamps baseColorFactor). A duplicate keeps its own colour as the material's baseColorFactor =
duplicate mean / keeper mean (linear, clamped at 1): the hell rock's pattern (HELL_TINT). COLOR_0 is untouched.
One world density for all: texel.MPT = 0.05 m/texel, sampled REPEAT, no atlas windows.

| group | keeper (px, period) | duplicates -> factor (R G B) |
|---|---|---|
| leaf | forest_sun_albedo (256, 12.8 m) | leaf .249 .279 .554; shade .151 .194 .530; fern .220 .333 .568; atlas leaf .273 .303 .576; atlas shade .067 .070 .249; atlas sun 1 1 1 |
| grass | forest_grass_albedo (256, 12.8 m) | verge 1 .846 1 (raw 1.017 / 1.03 clamped); edge .352 .402 .841 |
| dirt | forest_path_albedo (256, 12.8 m) | earth .261 .211 .475 |
| wood | forest_bark_albedo (256, 12.8 m) | root 1 .889 .801 (raw R 1.166 clamped); atlas bark .974 .978 .978; atlas root 1 .900 .810 (raw R 1.17 clamped) |
| stone | forest_rock_albedo cropped to its granite quarter (64, 3.2 m) | rock shade .416 .440 .501; moss .191 .359 .135; lichen .937 .961 .898; dark (cell, lamp) .014 .014 .015 |
| own | forest_portal_swirl_albedo (64), forest_lamp_emissive (256) | none: the swirl is its own art, the lamp is emission (lighting) |

forest_mist_albedo (64, the fog agent's drift noise, landed 3de71b3) is the fog: lighting, kept as its own.

## Phase 2: landed (main 68e4b74)

- Files: 17 -> 8 (maps/forest/textures: bark, grass, path, sun, rock 64x64, portal_swirl, lamp_emissive, mist).
  Deleted (+ .import): forest_atlas, forest_leaf, forest_shade, forest_fern, forest_verge, forest_edge,
  forest_earth, forest_root, forest_dark. forest_rock cropped 128 -> 64 (its granite quarter, pixels untouched).
  SHEET_forest repacked albedo-only: 7 tiles, 1341x263 (was 3631x263).
- Build scripts: forest_tree_build holds KEEPERS / TILES / tile_materials / tile_period and a world-tiled
  unwrap (no atlas windows, no painters); forest_build's SHEETS name the keeper as `stem` with the factor as
  `tint`; canopy, bush, props, thorns, portal and rock unwrap at TILE_MPT onto the keepers, one material per
  zone. Canopy leaves were at 4 texels/m, now at the one density (20 texels/m).
- Lamp: its albedo is the stone keeper x .014 at the lamp's own 256-texel period, because the glow file
  shares its UVs; the emission is sampled exactly as before.
- Rebuilt on the PC: forest, forest_tree, forest_canopy, forest_bush low/tall, forest_portal, forest_rock
  boulder/slab/outcrop, forest_thorns, forest_tree_prop_a/b/c. forest_bars_build.py is broken on main before
  this change (ft.orient and other helpers gone since d389dc6), so forest_bars.glb had its two deleted images
  repointed in the glb JSON (leaf -> forest_sun x factor, root -> forest_bark x factor); hub_base.glb likewise
  (ForestLeaf, ForestFern -> forest_sun, ForestDark -> forest_rock, factors added), since hub_forest_build
  imports the deleted forest_tiles module. UVs of both untouched.
- Contracts: surfaces tree 5, canopy 2, bushes 4, portal 3, rock 4, thorns 4, props 2; forest 17, bars 3 unchanged.
- forest_build.py --check passes. Mac import twice: 13 pre-existing seek errors, then 0; no .import rewritten.
  PC (pc_sync): first import 44 (stale-uid first pass), second 0; PC tree clean.
- Renders (PC, 1600x900): ~/Desktop/panopticon-renders/forest-consolidate/{before,after}/
  {lane_along,lane_wall,deck_across,deck_down}.png.
- Untouched: forest.tscn lights and environment, every COLOR_0 bake, the lamp and swirl emission, the mist.
