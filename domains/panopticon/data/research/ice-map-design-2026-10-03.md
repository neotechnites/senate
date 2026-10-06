# Map 4, ICE: design and seam contract (pass 2)

Pass 1 (a lathe-turned shell, flat colours, a plain drum for a tower) was rejected by Ryan:
"perfect cirlces. completely flat texture. tower inspired by nothing. roof looks like fucking nothing.
... make an actual map". Pass 2 replaces every model of pass 1. Nothing here is a placeholder.

Standing rulings: blue ice, snow only as contrast. N64 look (not PS1): soft, bilinear, low-res photo
textures, about 20 px/m. No see-through cover. The roof stays a blue, slightly transparent ice dome
"for now", but it must read as a made thing. The map's gimmick is ice sliding (separate code task).

## Where every idea comes from: Ryan's references, `~/Desktop/panopticon-refs/Map 4/`

LOOK AT THEM before modelling. Each element below names its source.

- `Ice_cavern_rupee_room.webp`, `015.jpg` (OoT Ice Cavern): thick blue glacier walls with vertical flow
  streaks; a bright blue lake-ice floor; clusters of tall white stalagmite pillars with flared feet;
  cut ice blocks with a grid of saw lines.
- `Ice_Cavern_Final_Room_OoT3D.webp`: huge faceted deep-blue crystal shards and curtains of long
  icicles against a black starry sky.
- `adventure_time_...jpg`, `images-1.jpg` (Ice Kingdom): the Ice King's mountain, a tall faceted peak
  of big flat planes in three blues with a snow cap; a GEODESIC faceted ice dome (top-left frames);
  ice-block doorways.
- `MK8-Course-GCN_SherbetLand.webp`: ice-brick walls and stacks, a frozen lake with snow banks and an
  open water hole, night sky with moons, snow-laden pines.
- `Screen_14.webp` (Shovel Knight): aurora curtains in the night sky; snow-capped ledges with icicles.
- `images.jpg` (Castle Crashers), `eIgOvW.webp` (Easy Delivery Co): teal snow, dark pines, haze.

## Shape rules (the reason pass 1 failed)

1. No lathe. Nothing is a perfect circle, cylinder, cone or sphere. Every ring wanders in plan and in
   height with low-frequency noise, and breaks with features (notches, buttresses, drifts, shards).
2. Everything is one sculpt against the real terrain: a pillar flows out of the floor, a buttress out of
   the wall. Joins are one flowing surface, no plane meeting a mass, no acute crevice.
3. Facets are a deliberate style here (Ice Kingdom): big flat planes, unequal, hard edges on ice;
   soft rounded forms on snow.
4. Each model is ONE contiguous mesh (components=1, no duplicate positions, no non-manifold edges).
5. Collision follows what is drawn to within 0.15 m wherever a body can stand or touch.

## Fixed numbers (map 1's; all models share them)

World coordinates, Godot y up, bearings as map 1 (`pol(bearing, r, z)`). Lane surface y 23.0, lane
centre r 52, run 5° → 335°, gate at 353°, portal at the finish. Tower datum y 25.35, guard room floor
+1.70 (eye y 28.7), room radius 6.86. Pit floor y -11.0. Kill box roof y -8, r 62.
Runner: 11 m/s, jump 1.11 m high and 7.0 m long, body 0.5 m radius, crouched 1.2 m, standing 1.8 m.
Walkable corridor on the lane never under 3.15 m.

## Models

### A. `ice.glb`, the map (lane, wall, cells, pit, dome)
- Lane: lake ice (slice `ice_lake`), nominal r 46.7..57.3, relief ±0.06 m (it is for sliding on).
  Inner lip WANDERS r 45.6..47.6: a broken ice shelf with calved notches (0.6..1.0 m deep, 3..7 m
  long), jutting floes, a 0.4 m rounded edge and icicles hanging under it into the pit.
  Outer foot WANDERS r 56.2..57.8: snow drifts banked on the wall (slice `snow`, soft), between them
  bare ice. Three open-water holes (Sherbet Land) cut through the lane in ONE stretch (bearings
  150..200), each 2.5..4 m across, irregular, dark water 0.6 m down, never touching the r 50.5..53.5
  band: a kill on touch (the scene puts a TrapVolume over each; export their outlines in the contract).
- Wall: glacier ice (`ice_wall`), from the lane up to a head that varies y 36..39. It leans and bulges
  ±0.6 m, with vertical flow flutes and 14 ice buttresses at jittered bearings standing up to 1.2 m
  proud, each flowing out of the wall and the floor. Collider: a conservative simple wall plus a prism
  per buttress.
- Cells (this is a prison): two tiers of barred alcoves carved into the wall, facing the tower. Lower
  tier 14, sill 0.3 m over the lane; upper tier 20, sill y 28.6. Mouths 3.0 m wide, arched, 2.5 m
  deep, dark inside, the back face a dim cold lamp (emissive slice `ice_lamp_emissive`). Each mouth is
  framed by a course of cut ice blocks (`ice_block`, Sherbet Land's ice brick), so the cells read as
  built into the glacier. Icicle bars over each mouth (thin tapered icicles top and bottom, meeting or
  nearly). Irregular spacing, none between 328° and 12° (gate, portal).
- Pit: a crevasse, not a cone. From the lip, sheer blue ice (`ice_wall` darkening to `ice_dark`)
  drops in steps and ledges; big crystal shards (`ice_crystal`, final-room crystals, 3..8 m) jut from
  the walls and the floor; the floor is black water / black ice. Leave the tower's foot clear to r 10.
- Dome (separate transparent surface in the same file, node `IceDome`): the Ice Kingdom's geodesic
  dome. Triangulated panels 5..8 m on a side, jittered so no two rows match, FLAT shaded, tinted in
  three blues through vertex colour, with a frost-white rib along every panel edge (thin geometry
  0.2 m proud on the inside, opaque, slice `ice_white`). It springs from the wall head through a
  broad cove with no corner; apex about y 66. A curtain of icicles (1..4 m, in clusters, opaque) hangs
  from the spring ring. Panels alpha 0.78..0.9 (blend_mix, never blend_add), single-sided facing in.
  `generate_lods=false` on the import.
- Budget: 120k triangles drawn at most, collider under 2.5k.

### B. `ice_tower.glb`, the tower: the Ice King's mountain
A faceted ice peak grown for the purpose, on map 1's guard datum. An irregular 7..9-sided
cross-section, never regular, of big flat planes in three blues (`ice_crystal`, `ice_wall`,
`ice_white`), with crack lines where planes meet. It rises from the pit floor (r about 9 at the foot,
with fallen ice blocks and shards round it), narrows to the guard room, and carries on up above it to
a snow-capped summit at about y 52 that leans a little. The guard room is a cavern broken through the
peak: floor +1.70 over the datum, radius 6.86, eight jagged window openings between eight ice piers
(each opening at least 40° wide and clear from 0.65 m to 3.2 m over the floor so the guard's view and
shots match map 1), a 1.25 m collider kerb as map 1. Icicles hang from the brow over each opening and
under the sill. The summit opens into a cradle of five to seven crystal shards that hold the Watching
Eye (Watcher at the map's eye profile height; keep it visible from the lane). Snow lies on the cap
and on every ledge. Budget 15k triangles, collider under 800.

### C. Props (each its own .glb, origin at base centre, own `-colonly` collider)
- `ice_stalagmite_a`, `_b`, `_c`: OoT clusters of 3..7 white pillars (`ice_white`), 3..5.5 m, flared
  feet, small ones at the foot. Hide a standing runner.
- `ice_block` (one cut block 2.4 × 2.4 × 1.3 m, saw-line grid, crouch cover) and `ice_block_stack`
  (Sherbet Land stack, 3.2 wide × 2.3 tall, stepped and chipped, standing cover). Slice `ice_block`.
- `ice_crystal_a`, `_b`: leaning faceted shard clusters 2..4 m (`ice_crystal`).
- `ice_drift`: a snow drift 3 × 2 × 1.3 m (`snow`), soft, crouch cover.
- `ice_pine_a`, `_b`: snow-laden pines 5..7 m (`pine_needles`, `pine_bark`, `snow`), for the snow
  banks at the wall foot only.
- `ice_spikes_round`, `ice_spikes_strip`: icicle spike patches, 0.9 m tall, the hazard (TrapVolume in
  a `maps/ice/props/*.tscn`, as `forest_thorns_*`).
- `ice_bars`: the gate at 353°, an icicle portcullis in a cut-block frame, lane edge to wall.
- `ice_portal`: a crystal arch round the shared portal opening (`portal_wave.gdshader`, swirl from
  `lib/portal_disc.py`).

## Texture slices: `maps/ice/textures/ice.ase` (one agent owns this file)

128 px unless noted, 20 px/m, tiling, made from CC0 photographs (ambientCG or Poly Haven only; record
each source URL and licence in `docs/TEXTURES.md`) through `tools/textures/photo_to_texture.py` and
the forest's N64 soft prep (lifted black point, lower contrast, 1 px blur, a shared palette of about
32 colours). No procedural or drawn pixels except the saw lines of `ice_block` and the portal swirl.
Slices: `ice_lake`, `ice_wall`, `ice_block`, `ice_white`, `ice_crystal`, `ice_dark`, `ice_dome`,
`snow`, `water`, `pine_needles`, `pine_bark`, `ice_lamp_emissive` (32 px), `ice_portal_swirl` (64 px).
The source photographs also go to `~/Desktop/panopticon-renders/textures/photos/ice/` so Ryan can
redo any slice in Aseprite.

## Scene, light, course (after the models)

- Sky: night, stars, slow aurora curtains (teal-green into magenta), bold enough to read through the
  dome. Light: cool ambient, one soft key from above, a dim cyan glow from the crystals and cell lamps.
  Runners must stand out against the ice. Blue-white mist in the pit, as the forest's layered fog.
- Course, first pass for Ryan to re-place (props as scene instances, never baked): pockets and four
  stretches round the run: S1 stalagmite slalom; S2 block yard (crouch and standing cover alternating
  sides); S3 thin ice (the water holes, crystals for cover); S4 crystal field with spike patches.
  Cover inside the lane shades the corridor outside it (the guard is on the axis). Drifts and pines
  at the wall foot.

## Review (the head looks before Ryan does)

Each model agent renders its model bright, at eye level, from the guard's eye and from above, into
`~/Desktop/panopticon-renders/proofs/ice/<model>/`, LOOKS at the renders, and fixes what reads as
lathe-turned, flat, blocky or pasted on before reporting. EEVEE only.
