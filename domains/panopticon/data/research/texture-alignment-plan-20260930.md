# Texture alignment plan 2026-09-30: forest and marble brought in line with hell

Read-only planning pass on main 6b9a551. Nothing changed. Inputs: the PNGs and SHEET_*.png of all three maps
(viewed, plus a 4 m x 4 m world patch of each tile at its measured density), texture-audit-20260930.md,
forest-consolidation-20260930.md, the marble/forest build scripts, and a per-material measurement of every map
glb (below). No number in this plan is a rule of its own: each is a hell measurement or derived from one.

## 1. What hell measures (the reference)

Texel density = sqrt(sum UV area x texture texels / sum world area) per material, glb node transforms applied;
every map instance in the .tscn files is rotation-only (no scale), so glb metres are world metres.

| hell tile | px | used at (texels/m) | colours (cover 90%) | flat shapes per tile | smallest mark | typical shape (area-weighted median) | isolated texels |
|---|---|---|---|---|---|---|---|
| hell_rock | 256 | 19-21 on 99% of its 209k m2 (rock, shade, ember, gate, lips) | 7 (5) | 75 | 25 texels = 5x5 = 0.25 m | 2886 texels = 2.7 m | 0 |
| lava | 256 | 51.2 (sea, river) | 3 (3) | 74 | vein ~8 texels = 0.16 m | 2213 texels = 0.9 m | 10 (edge AA only) |
| crack_glow | 64x32 | 5.2 (the 19k m2 glow floor) | 6 (4) | 1033 (speckle) | 1 texel = 0.19 m | 3 texels | 694 |
| hell_props (swirl) | 64 | 20.7 (portal disc) | 18 (13) | its own art | - | - | - |

What that means, read as rules:
- **Density.** Hell's solid surfaces are 20 texels/m (texel.MPT 0.05 m): the rock tile wears it everywhere,
  and the swirl lands at 20.7. Hell's two exceptions are its liquid (lava 51) and its distant glow floor (5.2);
  neither is copied as a target, but the glow floor is the precedent that a huge, far surface can go coarse.
  (hell's own portal.glb HellRock is at 45; noted, out of scope.)
- **Detail.** The unit that is constant across all three hell tiles is the smallest mark in WORLD size:
  0.16-0.25 m (rock's 5x5 ember, lava's vein, the glow's 1-texel speck at 5.2/m). At 20 texels/m that is
  4-5 texels. Hell never paints a 1-texel (0.05 m) mark on a surface; its rock and lava have no dither.
- **Palette.** 3-7 colours a tile, 90% of the tile in <= 5 of them; flat fills, value steps carry the shapes.
- **Variety.** One rock file covers rock, shade, ember and carve: the variation is the material factor
  (HELL_TINT: shade .116/.085/.130, ember .036) and the COLOR_0 bake, not more files.

## 2. What forest and marble measure

| tile | px | used at (texels/m) | colours (90%) | flat shapes per 256 sq | singletons | smallest mark |
|---|---|---|---|---|---|---|
| forest_bark | 256 | 18-20 (median 17.5-20) | 8 (4) | 23419 | 12479 | 1 texel = 0.05 m |
| forest_grass | 256 | 20 | 30 (24) | 57859 | 51617 | 0.05 m |
| forest_path | 256 | 20 | 29 (20) | 56354 | 49315 | 0.05 m |
| forest_sun (the leaf keeper) | 256 | 18-20 | 7 (5) | 8647 | 3575 | 0.05 m |
| forest_rock | 64 | 18-20 (boulders); 4.8 lamp, 27.9 cell (both x.014) | 59 (41) | 59936 | 3440 of 4096 | 0.05 m |
| forest_portal_swirl | 64 | 20.9 | 18 (13) | own art | - | - |
| marble_stone | 128x261 | 21.7 walls; 30.7 plinth; 30.5 bars; 32-43 tower; 5.5 portal | 6 (5) | 15526 | 10610 | 0.05 m |
| marble_field | 256 | 20 | 7 (5) | 6592 | 4237 | 0.05 m (blades) |
| marble_dark | 192x261 | 21 cellin; **100 iron** (66-93 tower/bars iron) | 17 (9) | 20228 | 10395 | 0.05 m |
| marble_albedo (ornament atlas) | 320x256 | 4.9 dome, 19 band/spike, 25 floor, 26 coffer, 43 frieze, **52 column**, 64 medallion, 71 tower column | 59 (25) | 13890 | 9804 | 0.05 m |

Findings:
- **Forest density is already hell's** (18-20 everywhere that shows). Forest's misalignment is DETAIL: grass,
  path and rock are per-texel dither (75-84% of texels isolated, 29-59 colours); bark is dither under its
  streaks. Their smallest mark is 0.05 m, 4-5x finer than anything hell paints, so they read higher-fidelity
  (and shimmer) beside a hell-style tile. Leaf (forest_sun) is closest to hell: 7 colours, blocky leaf squares,
  but on a dithered ground.
- **Marble's misalignment is DENSITY first.** One map spans 4.9 to 100 texels/m, a 20x range: iron bars at 100
  (fit_u squeezes the 64-texel iron column across a 0.13 m bar), column flutes at 52-71, frieze 43, medallion
  64, tower stone 32-43 (the tower's ashlar_sheet spans), plinth 30.7 (mpt_v halved for 0.5 m courses), and
  the portal's bricks at 5.5 (PROP_MPT draws 3.97 m courses). Hell holds one density on every solid surface.
- **Marble also paints geometry and duplicates material.** marble_field and the atlas's `field` cell are the
  same drawing; the atlas `floor`, `band`, `column`, `spike`, `medallion` cells paint slab joints, moulding
  stripes, flutes and streaks onto surfaces that are themselves modelled (deck facet rings, the proud cornice,
  the pilaster facets, 0.8 m2 of medallion disc). Three 64x64 atlas cells are spare plain stone (66% live).
- **Near-invisible:** forest_cell / forest_lamp wear the rock tile at x.014; hell's HellShade/HellEmber wear rock
  at .116/.036, so this is hell's own pattern (kept). marble's cellin is a separate 128x261 file of near-black
  (sRGB mean 7) whose painted slits are the only thing that reads: the HellShade pattern says it is the stone
  file x a dark factor, not a file.

## 3. Forest

Real materials (6): **bark** (trunks, roots, canopy branches, bars), **leaf** (canopy, foliage, fern, bushes,
lane roof), **grass** (ground, verge, edge), **dirt** (path, earth), **stone** (boulders, outcrops; moss and
lichen are its factors), plus the portal's own swirl art. Lamp glow and mist are lighting, not materials.

| file | verdict | why |
|---|---|---|
| forest_bark_albedo 256 | **redraw** at 256 | density already 18-20 = hell. Detail: 8 colours but 12479 singleton texels (dither ground). Redraw to hell's budget: <= 7 colours, flat fills, bark plates/streaks >= 4-5 texels wide (hell's 0.16-0.25 m smallest mark), no 1-texel marks. Size kept: 256 at 20/m = 12.8 m period, hell rock's. |
| forest_grass_albedo 256 | **redraw** at 256 | 30 colours, 51617 singletons: the worst-aligned tile. Redraw as ~75 flat tufts/patches (hell's shape count per 256), 5-7 greens, smallest tuft 5x5. Keep distinct from leaf by SHAPE (blade tufts vs leaf squares): their means are close (51/66/12 vs 43/58/15), so shape is what keeps them two materials and not near-duplicates. |
| forest_path_albedo 256 | **redraw** at 256 | 29 colours, 49315 singletons. Same budget as grass; the grass-in-dirt green flecks become a few 5x5+ patches. Earth stays this file x its factor (.261/.211/.475), the hell shade pattern. |
| forest_sun_albedo 256 | **keep, clean ground; rename forest_leaf_albedo** | 7 colours and blocky leaf squares already match hell's language; only its ground is dithered (3575 singletons): flatten it. The name: it is the leaf material for every green-leaf class (leaf, shade, fern, sun via factors). |
| forest_rock_albedo 64 | **redraw** at 64 | 59 colours, 3440 of 4096 texels isolated: pure noise. Redraw as hell_rock's language at 64: 5-7 greys, flat facets >= 5x5. Size kept 64: at 19/m that is a 3.2 m period, bigger than any boulder face (boulder 5.2 m2 total over 14 instances), and 64 is hell's own small-tile size (hell_props). Moss/lichen/shade stay factors. |
| forest_portal_swirl_albedo 64 | **keep** | own art, 20.9/m = hell_props' 20.7, same 18-colour budget as hell's swirl. |
| forest_lamp_emissive 256 | **keep** | emission (lighting). |
| forest_mist_albedo 64 (L) | **keep; rename forest_mist_noise.png** | the fog's drift noise, not a surface; the `_albedo` suffix puts it on SHEET_forest, which shows only tiles Ryan draws (the emissives were taken off the sheet for the same reason). |

Forest before -> after: bark, grass, lamp_emissive, mist, path, portal_swirl, rock, sun (8) ->
bark*, grass*, path*, leaf (was sun, cleaned), rock*, portal_swirl, lamp_emissive, mist_noise (8; * redrawn).
Sheet: 6 albedo tiles (mist off). No build-script density change; forest_build / forest_tree_build KEEPERS
rename sun -> leaf.

Variety from factor/vertex shade, not files (already so; keep): leaf/shade/fern/sun = leaf x factor;
verge/edge = grass x factor; earth = dirt x factor; root = bark x factor; moss/lichen/shade = stone x factor;
cell/lamp = stone x .014 (HellShade pattern).

## 4. Marble

Real materials (2 + art): **marble** (all masonry, the deck, the rotunda floor, cornices, pilasters, spikes,
the tower, the cells' back walls) and **iron** (the bars). Plus two drawings the geometry cannot carry: the
**ornament** Ryan designed (Greek-key frieze, the seven dome flutes, the tower coffer) and the portal **swirl**.

| file / atlas cell | verdict | why |
|---|---|---|
| marble_stone 128x261 | **keep size, redraw faces** | 128 across one 5.89 m bay = 21.7/m (hell's 20; the size is set by the bay so joints land on geometry). Its joints and blocks are hell-like, but the brick faces are a 4-colour +-4 sRGB dither (10610 singletons): flatten to flat faces with a few >= 5x5 patches. Becomes the ONE marble file every masonry class wears. |
| marble_stone users off-density | **fix UV scale, not file** | tower stone/dome/marble2/plinth (32-43) and bars marble (30.5) -> WALL_MPT; portal bricks (5.5, PROP_MPT's 3.97 m courses) -> WALL_MPT; plinth's halved mpt_v (30.7) -> WALL_MPT, its 0.5 m courses from the plinth's own geometry/vertex shade (interpretation: hell has no anisotropic class). |
| marble_field 256 | **merge into marble_stone** (x factor) | same material as the walls (marble paving); hell's floor and walls are one rock file. Factor = field linear mean / stone linear mean, the forest-earth pattern. Its 0.8 m grid is lost; the stone's 1 m courses read as paving top-down. |
| marble_dark: cellin column (128x261) | **merge into marble_stone** (x dark factor) | the cell's back wall is stone in shadow: HellShade is rock x .116, not a file. The painted pale slits ("a figure, a cot, a window") go; if Ryan wants them they are geometry. |
| marble_dark: iron column (64x261) | **split out -> marble_iron_albedo 64x64, redraw, world-project at 20/m** | iron is a real material and keeps a file. But fit_u puts it at 100/m (5x hell): it paints a bevel highlight across a 0.13 m bar that the bar's own faces and lighting already give. At 20/m a bar shows ~3 texels across and ~110 along: a 64 tile (3.2 m period, hell_props' size) with 3-5 iron values and flat scale patches >= 5 texels long. |
| atlas `frieze` 256x64 (43/m) | **keep, resize 118x36** | Greek key is a drawing no geometry carries. 256 x 20/43 = 119, 64 x 20/43 = 30; 118x36 is one 5.89 m bay x 1.8 m at 20/m so the key repeats once a bay as now. |
| atlas `dome` 128x64 (4.9/m) | **keep at its size** | Ryan's seven solid flutes. Its marks are whole flutes (metres wide), above the smallest-mark rule; the far, huge surface at ~5/m has hell's own precedent (crack glow 5.2 on the glow floor). |
| atlas `coffer` 60x34 (26/m) | **keep, resize 46x26** | 60 x 20/26 = 46, 34 x 20/26 = 26: one coffer facet at 20/m. |
| atlas `column` strip 64x256 (52-71/m) | **delete -> marble_stone** | painted flutes repeated per facet on pilasters/columns whose facets are modelled; the strip is 20% of the atlas at 2.6-3.5x hell density. Flute shading from the facets + vertex shade. |
| atlas `band` 64x64 | **delete -> marble_stone x factor** | moulding stripes painted on a cornice that is modelled proud (BAND_PROUD 0.45); the cornice's edges carry it. |
| atlas `floor` 64x64 (25/m) | **delete -> marble_stone** | the deck is marble; its slab layout is the DECK_RS rings and DECK_SUB facets already modelled: per-facet vertex shade gives the slab-to-slab variation. (Judgement call: the most-seen surface changes look; the alternative is keep the cell resized to 54x54 = 2.7 m at 20/m.) |
| atlas `spike` 64x64 (19/m) | **delete -> marble_stone x factor** | spikes are marble; hell's spires wear the rock. Interpretation: 1 m courses put 1-2 joint lines on a 1.4-2.8 m spike (reads as drums); the alternative is the stone redraw keeping one joint-free 64 px column for monoliths. |
| atlas `medallion` 64x64 (64/m, 0.8 m2) | **delete -> marble_stone** | earns no screen presence: 0.8 m2 at the tower crown at 3x hell density. The disc is geometry; vertex shade it. |
| atlas `field` 64x64 | **delete** | near-duplicate of marble_field (same drawing), itself merged. |
| atlas `portal` 64x64 | **split out -> marble_portal_swirl_albedo 64x64** | own art + glow, exactly hell_props and forest_portal_swirl (20.8/m here vs 20.7 hell). |
| atlas spare plain cells (3 x 64x64) | **delete** | unused plain stone. |
| marble_albedo as a file | **becomes marble_ornament_albedo 128x128** | frieze 118x36 + dome 128x64 + coffer 46x26 stack into 128 x 126. |

Marble before -> after: marble (320x256), marble_dark (192x261), marble_field (256), marble_stone (128x261)
(4 files, 230,976 texels) -> marble_stone (128x261, redrawn faces), marble_iron (64, new from marble_dark's
iron), marble_ornament (128, frieze/dome/coffer resized), marble_portal_swirl (64, from the atlas)
(4 files, 57,984 texels). Every class but the dome at 20-22 texels/m.

Variety from factor/vertex shade instead of a texture: shade, plinth, marble2, tower, field (rotunda floor),
cellin (cell backs), band, spike = marble_stone x factor (as HELL_TINT); deck slabs, column flutes, medallion,
plinth's 0.5 m courses = facet vertex shade on geometry that already exists.

## 5. Build work this implies (for the builder, not done here)

- forest: redraw 4 tiles (bark, grass, path, rock) + clean leaf's ground; rename sun -> leaf, mist -> noise;
  rebuild every forest glb that names forest_sun (tree, canopy, bushes, portal, props, thorns, forest, bars).
  No UV change.
- marble: marble_build SHEETS/ATLAS/DARK/prop_finish/marble_tower ashlar spans re-pointed; rebuild marble,
  marble_tower, marble_bars, marble_portal (+ the unreached props). Chunked as each glb.
- hub (out of scope, noted): hub_base's map wedges wear forest tiles at 74-80/m and marble at 5-51/m; if the
  wedges are scale models that is the scale, and the file renames above must follow there too.
- Hell untouched. Every new tile drawn to section 1's budget: <= 7 colours (90% in <= 5), ~75 flat shapes per
  256 tile, smallest mark 4-5 texels at 20/m (0.16-0.25 m), no dither.
