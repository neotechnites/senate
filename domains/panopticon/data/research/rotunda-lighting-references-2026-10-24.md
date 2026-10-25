# Rotunda / circular stone interior lighting references (for the panopticon "marble" map)

**Research note on method:** This session's WebSearch quota was exhausted before this task started (200/200 used elsewhere in the environment), so this is built from WebFetch on specific pages (Wikipedia, official store pages, Halopedia) plus general, well-documented game-art knowledge where primary sources were thin or blocked (most Fandom/Zelda-wiki/DuckDuckGo pages returned 402/403 errors to the fetcher). Citations marked "(general knowledge, lightly sourced)" are consensus facts about these games' look that I'm confident in but could not pin to a fetched quote this session — flagging that rather than presenting it as equally verified.

---

## The examples

### 1. Ocarina of Time / Twilight Princess — Temple of Time
**URL:** https://en.wikipedia.org/wiki/The_Legend_of_Zelda:_Twilight_Princess (dev/tone context) + https://en.wikipedia.org/wiki/The_Legend_of_Zelda:_Ocarina_of_Time
- **Light sources:** tall stained-glass clerestory windows running down both long walls — not a single top-down oculus, a *row* of side lights at height, throwing angled color-tinted shafts onto the altar and floor.
- **Colour:** cool blue-grey stone base, broken by warm gold/amber light where the shafts land — the warm color only exists where the light is, everywhere else stays cool and desaturated.
- **Flatness fix:** the shafts are volumetric (visible dust/haze), so the "light" is an object in the room, not just a brightness value on a surface; huge vertical scale means the upper dark is allowed to recede while the lower altar area carries all the saturation and contrast.
- **Alcoves:** upper reaches and side recesses go dark but not black — Nintendo's "realistic but legible" N64/GCN lighting keeps a cool ambient floor under everything.

### 2. Majora's Mask — Stone Tower Temple
**URL:** https://en.wikipedia.org/wiki/The_Legend_of_Zelda:_Majora%27s_Mask
- **Light sources:** lava (an emissive practical light, not a rig light) + torches; no sky opening at all — it's a sealed underground structure.
- **Colour:** cool purple-grey stone vs hot orange lava is the entire palette; wiki confirms the broader design language ("textures... colorful and diverse, giving each area its own unique look," Imamura's team, Southeast-Asia-inspired Termina look vs OoT's medieval-Europe Hyrule).
- **Flatness fix:** the lava is a *colored area light* that bounces warm light up onto the lower walls while upper walls stay cool — one hue swap does the work a whole lighting rig would otherwise need.
- **Alcoves:** dark, but glowing runes/switches are placed as deliberate bright accent points so the eye has somewhere to land even in the gloom.

### 3. Super Mario 64 — Castle hub / courtyard
**URL:** https://en.wikipedia.org/wiki/Super_Mario_64
- **Light sources:** no real dynamic lighting at all — N64-era vertex-colored flat shading. The "sun mosaic" on the atrium floor and the Peach stained-glass window are *painted* light, not simulated.
- **Colour:** saturated blue walls with white cloud mural, warm red carpet, gold floor mosaic — large flat color blocks instead of light/shadow gradients.
- **Flatness fix:** confirmed on-wiki — the team even painted a "faux shadow directly beneath each object regardless of the area's lighting" because, as artist Yoshiaki Koizumi put it, it was an "iron-clad necessity" to prioritize legibility over realism. This is the cleanest precedent for *not* trying to simulate real light at all and instead hand-painting value/color contrast into the textures.
- **Alcoves:** side doors/rooms are painted a darker local color, never true black — color blocking carries the read, not light falloff.

### 4. Shadow of the Colossus — Shrine of Worship
**URL:** https://en.wikipedia.org/wiki/Shadow_of_the_Colossus
- **Light sources: a single large skylight/oculus-type opening is the dominant — arguably *only* — strong light source** in the hall; this isn't incidental, it's load-bearing gameplay (raising the sword in the beam is how you find colossi). Confirmed via wiki: the engine used "desaturated colors, motion blur and partial high dynamic range rendering," heavy bloom, and Ueda pushed the team to "reinforce the brightness and saturation of the textures" specifically where the light hits.
- **Colour:** near-monochrome grey-tan stone; the sunbeam is the *only* saturated, bright element in the frame, plus a cool blue-green pool at the back of the hall for a secondary reflected accent.
- **Flatness fix:** this is the key lesson for a single-oculus room — the stone itself is desaturated and the *light* carries all the saturation/brightness via bloom+HDR, so one shaft reads as dramatic rather than just "a bright patch on flat grey." The water pool adds a second light-interaction surface (reflection/caustics) so the room isn't lit by one flat source alone.
- **Alcoves:** far corners stay in a narrow dark-grey band, never crushed to black — nothing in the hall reads as a void, just "less lit."

### 5. Ico — castle light-shaft rooms
**URL:** https://en.wikipedia.org/wiki/Ico
- **Light sources:** single sunbeams through high, narrow windows — functionally oculus beams, repeated room to room. Wiki: Ico was "one of the first video games to use a bloom lighting effect," and the design philosophy was explicit "subtracting design" — removing anything (HUD, clutter, extra geometry) that would compete with the one lit element in a room.
- **Colour:** warm gold beam against cool blue-grey weathered stone.
- **Flatness fix:** because the geometry and palette are so stripped-back (minimalism as an *art* choice, described by NME's Alan Wen as "ethereal timelessness"), the single light shaft has nothing to visually compete with — this only works because everything else in the shot was deliberately simplified first. Hard architectural silhouettes (arches/columns) throw crisp cast shadows that break up the floor.
- **Alcoves:** background recedes dark and desaturated on purpose (painterly, de Chirico-inspired), but always has faint bounce fill — never pure black.

### 6. Dark Souls — Anor Londo (cathedral/rotunda) and Firelink Shrine
**URL:** https://en.wikipedia.org/wiki/Dark_Souls
- **Light sources:** Anor Londo — a single huge, low, off-screen "eternal sunset" directional key pours through giant arched openings; Firelink Shrine — a single warm bonfire point-light at the circular pit, against cool blue dusk ambient everywhere else. (Wiki confirms the locations and the series' "gloomy and decrepit... centering around fire and extinguishment" thematic frame; the specific lighting description here is general knowledge, lightly sourced.)
- **Colour:** Anor Londo = warm gold/orange key against pale cream/gold-leaf stone, almost a monochrome-warm palette; Firelink = warm orange vs cool blue-grey, a textbook complementary split.
- **Flatness fix:** Anor Londo's gold-leafed statues and architecture act as giant reflective "fill cards" that catch and visibly re-bounce the warm key light, so value variation comes from *material response* to one light, not from adding more lights; gargoyle silhouettes read as pure black cutouts against bright sky for hard value contrast. Firelink's bonfire is a small, intensely warm pool deliberately surrounded by a much larger cool/dark ruin — the contrast in scale between the one warm pool and everything else is what sells it.
- **Alcoves:** side chapels and side paths go cooler/darker than the lit main space on purpose — but the *center* of each space is never black.

### 7. Halo: Combat Evolved — Silent Cartographer / Library (Forerunner rotunda structures)
**URLs:** https://en.wikipedia.org/wiki/Halo:_Combat_Evolved and https://www.halopedia.org/The_Silent_Cartographer
- **Light sources:** the Silent Cartographer vault interior combines soft overcast tropical daylight through a circular opening with *emissive architecture* — glowing blue/purple panel lines built into the Forerunner geometry itself, not separate lamp props. The Library's tall ring-stacked shafts run on cool ambient plus the same embedded glow-lines.
- **Colour:** cool blue/purple Forerunner material against warm tropical daylight (Cartographer) or against dark, murky green Flood-infestation grime (Library) — wiki confirms Forerunner material/geometry was deliberately distinguished by "angular constructions" with influences from Aztec patterning, separate from the warm, blocky human UNSC look and the organic green/purple Covenant look.
- **Flatness fix:** because the *material itself* glows (light is baked into the geometry's identity, not bounced onto it), rooms stay legible even where ambient light is low — there's always a graphic line of brightness to read shape by, independent of whatever overhead light exists.
- **Alcoves:** side chambers go dark but are never unlit — the glowing seam-lines are the fallback light everywhere.

### 8. Metroid Prime — Chozo Ruins
**URL:** https://en.wikipedia.org/wiki/Metroid_Prime
- **Light sources:** dappled sunbeams through broken/overgrown ceiling gaps in outer ruin rooms, plus warm amber bioluminescent glow built into Chozo statues/architecture in interior chamber rooms (e.g. the "Tower of Light" style vertical shafts). Wiki confirms the game won an award specifically for "exceptional achievement in Art Direction" and was praised for "detailed graphics, special effects, varied environments."
- **Colour:** warm amber/gold Chozo stone-glow vs cool blue-green jungle overgrowth — another warm/cool split, further broken up by the player's visor overlay tint.
- **Flatness fix:** the moss/vine/rubble detail is essentially a full-coverage decal pass — there is no clean flat wall anywhere, every surface has overlapping texture-level value breaks regardless of the light rig; most rooms also have a visible light-emitting *prop* (crystal, statue eye, vent) rather than depending on ambient alone.
- **Alcoves:** dark recesses stay heavily detailed/textured even when dim, so they read as "unlit space" rather than "missing geometry."

### 9. Thief: The Dark Project — Cathedral level
**URL:** https://en.wikipedia.org/wiki/Thief:_The_Dark_Project
- **Light sources:** many small practical sources — torches, braziers, candles, stained glass — rather than one big fill. Wiki confirms light/shadow is the explicit *core mechanic* (a visibility gem: "the brighter it is, the more easily they can be visually detected"), and designer Randy Smith is quoted: "the safe boundary is often between light and shadow [...] these boundaries are [...] not stable or secure."
- **Colour:** warm torch-orange pools inside a predominantly cool blue-black Gothic stone palette.
- **Flatness fix:** the whole level is architected as a patchwork of small warm pools separated by near-black shadow — the contrast is extreme and deliberate, room to room and even wall to wall within one room, instead of one even ambient wash.
- **Alcoves:** many alcoves are *meant* to be near-black (that's the stealth gameplay) — but silhouette/architecture stays readable even in the dark patches, it's never geometry-less void.

### 10. Prince of Persia: The Sands of Time — palace halls
**URL:** https://en.wikipedia.org/wiki/Prince_of_Persia:_The_Sands_of_Time
- **Light sources:** art director Raphaël Lacoste's team built custom "glow"/"substance" systems specifically to give light effects "a magical feel," using **blue-tinted key lights** against warm practical torch/brazier fill.
- **Colour:** cool blue magic-light key vs warm Arabian-Nights sandstone and gold fill — a strong, consistent complementary split reinforced by heavy set dressing (banners, rugs, metalwork) rather than bare walls.
- **Flatness fix:** the whole game is architecturally built around verticality (floors "stratified by rank," inspired by *The King and the Mockingbird*) so almost every room has a real diagonal value gradient from floor to ceiling, and every wall has dressing props breaking up the surface — light contrast and prop/decal contrast are doing the work together, not light alone.
- **Alcoves:** upper/lower extremes of vertical shafts fade into dark blue haze, not black — consistent with the cool key.

### 11. Dark Messiah of Might and Magic — Source-engine dungeons/castles
**URL:** https://en.wikipedia.org/wiki/Dark_Messiah_of_Might_and_Magic *(general knowledge, lightly sourced — Wikipedia's own art-direction coverage is thin; press reaction only confirms "beautiful graphics" on PC)*
- **Light sources:** dense placement of many small practical lights (torches, braziers, magic glyphs) using Source engine colored dynamic lights plus baked radiosity bounce.
- **Colour:** warm torchlight against cool stone, with spell-effect colors (ice blue, fire orange) as saturated accents.
- **Flatness fix:** Source's baked radiosity gives genuine visible color bounce — torchlight actually tints the stone near it — combined with very high environmental prop density (chains, banners, rubble) that breaks up every wall independent of the lighting.
- **Alcoves:** generally lit low-but-not-black, since Source-era level design relied on light volumes for navigation.

### 12. ULTRAKILL — Layer 7 ("Violence")
**URL:** https://store.steampowered.com/app/1229490/ULTRAKILL/ (confirms Dante's Inferno framing, "ultraviolent" visual identity) + general knowledge for layer-specific detail (not independently re-verified this session)
- **Light sources:** large-scale cathedral/colosseum rooms lit by one or two strong, hard-edged colored key lights (hot pink/red/gold) with heavy bloom, set against large areas of near-black unlit negative space — explicitly non-physical, non-naturalistic lighting.
- **Colour:** saturated, almost neon warm hues (red, hot pink, gold) against near-black void and blown-out white highlights — a huge, compressed value range with very little midtone detail.
- **Flatness fix:** the blood-decal mechanic literally paints saturated red onto the floor as you play, constantly injecting color variation into otherwise static geometry; unlit areas are *allowed* to go to black because the lit surfaces are pushed so bright/saturated that the contrast itself reads as drama, not as "the rest of the room is just dark." This is the most stylised, least physically-justified example on this list — the opposite end of the spectrum from SotC's desaturated realism-adjacent approach.

### 13. Pseudoregalia — Castle Sansa
**URL:** https://en.wikipedia.org/wiki/Pseudoregalia
- **Light sources:** committed low-poly PS1-era look — no modern GI or dynamic shadow; wiki confirms it's "stylistically influenced by fifth generation era video games" with deliberate low-poly graphics (and that uniform/low-variation texturing was flagged by Hardcore Gaming 101 as a minor weakness: "repetitive textures made individual rooms hard to tell apart").
- **Colour:** each area commits to one or two dominant saturated hues (e.g. lavender stone, teal fog) instead of naturalistic grey stone + white light.
- **Flatness fix:** color *replaces* lighting as the main depth cue — strongly tinted flat-shaded surfaces plus a fog gradient from the camera do what a lighting rig would otherwise do. This is the most relevant example of "if your light rig can't carry the room, let color blocking carry it instead."
- **Alcoves:** distant geometry fades into the fog's tint rather than into flat grey ambient or black — worth noting as the one place this game is called out as a slight weakness (repetitive texturing) even though the color/fog solution itself works.

### Bonus — Breath of the Wild Sheikah Shrines (not in the seed list, but the cleanest modern "single top-down light is the entire room" case)
**URL:** https://en.wikipedia.org/wiki/The_Legend_of_Zelda:_Breath_of_the_Wild (confirms Sheikah architecture was designed around Jōmon-period inspiration; shrine-interior lighting specifics below are general knowledge)
- **Light sources:** one vertical blue light column from floor to ceiling at the room's center is the *entire* explicit light source, plus glowing cyan circuit-pattern lines inlaid in the dark stone walls/floor and warm amber accent lights at key triangle slots.
- **Colour:** near-black/dark-blue-grey stone base, cool cyan glow lines, one warm amber accent color reserved for interactive elements only.
- **Flatness fix:** the glowing circuit-pattern decal lines are baked directly into every wall/floor/ceiling surface, so there is graphic contrast everywhere independent of the one light column; the amber accent is used *sparingly and consistently* so it reads instantly as "this is interactive," adding a second hue without muddying the cool-dominant palette.

---

## Patterns: what the good ones share that a single-spot + flat-ambient rotunda lacks

1. **The light source is never alone — it has a second, different-temperature light to react against.** Every example pairs a cool stone/ambient base with one warm accent (or vice versa: Ultrakill's warm neon against near-black, or Pseudoregalia's cool fog against a saturated wall hue). A rotunda lit by one oculus beam *and otherwise flat, uncolored ambient* has no second temperature to create contrast with — the beam and the walls are both "neutral," so nothing pops.

2. **The light interacts with a surface that visibly responds to it (bounce, bloom, reflection, emissive decal), not just a lux value on flat geometry.** SotC's bloom+HDR beam, Dark Souls' gold-leaf bounce, Halo's embedded glow-seams, Ultrakill's blood decals, BotW's inlaid circuit lines — in every case the *material* is doing work, not just the light. A flat grey rotunda wall under a spotlight only gets brighter; it never gets more interesting.

3. **Desaturated base + saturated accent, not uniform mid-saturation everywhere.** The common failure mode ("flat") usually means everything is roughly the same saturation and value. SotC, Ico, and Dark Souls all deliberately desaturate 90% of the room so the 10% that's lit can carry real color punch.

4. **Something besides the light breaks up the walls: decals, moss/vine/rubble texture passes, vertex-painted "fake" light, or dense prop dressing.** Mario 64's painted fake shadow, Metroid Prime's full-coverage grime/moss decals, PoP's heavy set dressing, Pseudoregalia's deliberate color blocking — all of these are explicitly *not* relying on the light rig to create wall-surface variation. This is probably the single biggest lever available cheaply in an N64/PS2-style engine: baked vertex color / texture variation can do most of the "non-flat" work that dynamic lighting can't.

5. **Shadows and unlit zones are allowed to go dark, but almost never to true flat black** — they recede into a cool, low-but-nonzero value band (grey-blue gloom, not void), except in Thief and Ultrakill, which both go to real black *on purpose* as a stylistic/gameplay choice (stealth visibility, ultraviolent contrast) — and even then the silhouette/architecture stays legible against it.

6. **Scale and silhouette do a lot of the "readability" work a lighting rig usually does.** Anor Londo's gargoyle silhouettes, Ico's hard architectural cast shadows, Halo's glowing seam-lines tracing the geometry's shape — in a circular room, strong architectural silhouette (columns, barred cells, tier edges) against a brighter background will read as "interesting" even with simple lighting, because the eye is parsing shape-contrast, not light-quality.

7. **The single-oculus examples (SotC, Ico, BotW shrines) all keep everything else in the room extremely simple so the one light has nothing to compete with.** This is the most directly actionable lesson for the marble map: a single top-down oculus light reads as "good" specifically in rooms where the rest of the palette/geometry has already been pared back — ornate cell bars, lots of mid-tone stone detail, and a flat ambient fill are the opposite of that, and are probably why a single spot currently reads as either "too dark" (not enough to see the detail) or "flat" (ambient fill cancels out the one light's contrast) rather than dramatic.

8. **Warm color is reserved for "important"/interactive surfaces, cool color is the default resting state of the architecture** (BotW's amber key-slots, Metroid's amber Chozo glow-props, Dark Souls' gold statues) — this gives the eye a hierarchy to follow even in a dim room, which a uniform-material rotunda doesn't have unless the barred cells themselves are given an accent color (e.g. warm lamps/glow inside a subset of cells) distinct from the cool stone ring.
