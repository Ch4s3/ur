# Ocean water — design

Date: 2026-11-22 · Status: approved

## Intent

The sea around Ur's islands should look like the ocean. Today it reads as fog:
an opaque, flat teal sheet 8 m below the coast (`Ur.Scene.sea`, opaque part 0,
material 3) that tonemaps to almost the sky's colour by day and flat grey at
night. The islands end in cliffs over nothing. Strata already has a water
shader (`native/shaders/water.frag`) with transparency, mirror reflections,
ripples and sun glints, but the sea does not use it.

"Looks like the ocean" means, in order of importance:

1. Deep blue that runs out to the horizon, clearly different from the sky.
2. Turquoise shallows near the coasts, with the seabed visible through them.
3. A surface that moves and catches the light: reflections, glints, ripples
   that read as small rolling waves from the city-builder camera.
4. White foam where the water meets land, seawalls and piers.

## Goals

- The sea is drawn by Strata's translucent water pass, not as opaque ground.
- Sea level meets the coast. Water parcels (height 0) and the area outside the
  480 x 352 m map have a seabed that slopes from the shore into deep water.
- Water colour follows depth: turquoise in the shallows, dark blue offshore,
  fading into the horizon haze far out.
- An ocean mode in `water.frag`: larger wave patterns (still stepped to the
  voxel grain), sun glitter, foam lines where depth approaches zero.
- Works by day, at dusk, at night (dark water with lamp and moon highlights,
  not grey) and in the rain.

## Non-goals

- Waves that move the surface (meshes redrawn per frame). Ruled out: it fights
  the voxel look and costs a remesh every frame.
- Changes to flood water, fluid simulation or the sea's role in the simulation.
- Boats' wakes, underwater views beyond what Strata already does.

## Anti-goals (a failure even if it works)

- Water that looks smooth or plasticky and out of place in the voxel world:
  every pattern keeps a voxel-sized step.
- A noticeable frame-rate cost. Today the region view runs about 4.1 ms of GPU
  time a frame; the ocean should add no more than about 1 ms there.
- Foam or shallows that flicker or swim when the camera moves.
- Breaking the existing flood-water, overlay and heat-strip uses of the
  translucent pass.

## Constraints

- 0.25 m voxels; parcels are 32 voxels (8 m); terrain heights are voxels.
  `L.ground_height` clamps at 0 and `L.sample` treats water parcels as -7.
- Chunks above level 0 (the far sea) are lit by sun and sky only and mirror
  only the sky (`far` in `water.frag`). That is fine for open sea.
- The translucent pass already packs per-patch scalar data into a quad's
  second word: overlay 252 carries four 6-bit corner samples (flood depth).
  The ocean reuses that pattern.
- Ur's materials fill all 32 texture layers (`textures_create(16, 32)`), so a
  new water material needs either a 33rd layer or a reused slot.
- Strata is a separate repository shared by several checkouts and sessions;
  its changes need their own branch (see Open question).

## Approaches considered

- **A. Strata's existing water plus a seabed (Ur only).** Most of the effect
  for least work, but the surface stays a calm lake with no waves or foam.
- **B. A, plus an ocean mode in Strata's water shader.** Chosen. About twice
  the work and touches Strata, but it delivers waves, foam and horizon, and
  advancing Strata is the project's second priority; the viewer's seas can
  use it too.
- **C. Moving wave geometry.** Ruled out (see Non-goals).

Built in two steps so each can be seen: step 1 is A, step 2 the ocean mode.

## Design

### Step 1 — the sea becomes water (Ur)

- **Sea surface.** Replace the opaque sea sheet with translucent quads at sea
  level (just above the clamped ground of water parcels), uploaded with
  `chunk_part(2, …)`. Near the map: level-0 chunks of modest quads so the
  surface gets near reflections and per-quad depth samples. Further out: the
  existing coarse level-5 tiles, translucent, out to the horizon.
- **Water material.** A see-through, translucent block class with low
  roughness (under 0.25, so `water.frag` mirrors it; material 3 today is 65/255
  and never mirrors) and a partly transparent texture.
- **Seabed.** Let ground under water go below 0: water parcels and the ring
  outside the map get a seabed whose depth grows with distance from the
  nearest land (a few metres in the first parcel, tens of metres within
  ~100 m), with sand near shore and darker rock and silt deeper. Inside the
  map it is part of the existing terrain chunks; outside, coarser chunks.
  Buildable and simulation heights do not change: this is only what is drawn.
- **Depth colour (interim).** Until step 2, the depth tint comes from the
  water's own transparency over the seabed.

### Step 2 — ocean mode (Strata `water.frag`)

- **Ocean quads.** A new translucent code (like overlays 250–253) for ocean
  surface quads whose second word carries four 6-bit corner samples of water
  depth. Ur fills them from the seabed when meshing. Strata gets a small API
  for packing them (alongside `Strata.Quad`), so the viewer can use it too.
- **Colour by depth.** Interpolated depth picks the water colour: turquoise
  at 0–2 m, through teal, to dark blue past ~15 m; transparency falls with
  depth so the seabed shows only in the shallows.
- **Waves.** Larger, slower crossing wave normals than today's ripple (which
  stays for lakes and flood water), stepped to the voxel grain, stronger in
  deep water and calmer in the shallows, so glints and reflections break up
  into small rolling waves from the default camera.
- **Light.** Fresnel mirror as today (near: traced reflections; far: sky),
  plus sun glitter on wave crests. At night, dark blue-black water with
  highlights from the moon and lamps.
- **Foam.** Where interpolated depth approaches zero: a soft white band along
  shore lines, broken by a voxel-stepped noise pattern that drifts in and out
  with time. The same around seawalls and piers (their quads read as depth 0).
- **Horizon.** Far ocean fades into the sky's haze colour at the horizon
  rather than into flat grey, so the islands sit in open sea.

## Calls made while writing this up (check these)

- **Night.** There is no moon in Strata or Ur. At night the ocean uses a
  fake moon glint inside the ocean shader (a fixed direction opposite the
  sun), plus the lamps that already show up in near reflections. No new
  light source and no reading of lamp light from the translucent pass.
- **Viewer.** Strata gets the ocean shader mode and the API that packs depth
  into quads. The viewer's own seas stay as they are, so its golden scenes
  don't change. Moving the viewer over is a later piece of work.
- **Step 1 is a checkpoint, not a release.** It's there so you can see the sea
  turn into water. Step 2 replaces its surface material. Both land together,
  so step 1's material and texture-layer choice only need to be good enough
  to look at.
- **The coast can change in play** (seawalls, piers, harbour). Seabed depth
  comes from distance to land on the 60 x 44 parcel grid, which is cheap to
  recompute. When the coast changes, only chunks whose depth samples changed
  get re-meshed. Outside the map, the coast is fixed and its seabed is built
  once at load.

## Verification

- Before/after screenshots from fixed views (`UR_DEMO=1` with
  `UR_CHANNEL_VIEW` and `UR_REGION_VIEW`, `UR_CLOCK_HOUR` 7, 14, 19 and 2,
  `UR_FRAMES`, `STRATA_SHOT`).
- GPU time from the `ur:` stats line in the same views, against the 4.1 ms
  baseline.
- Flood demo (`UR_FLOOD_BACKUP`) and data layers still look as before.
- Strata's own shader checks and viewer golden scenes still pass.

## Left to the builder

- Exact colours, wave frequencies and foam width, tuned against screenshots.
- Quad sizes for the near sea and how far out level-0 sea chunks reach.
- Whether the water material takes a 33rd texture layer or a reused slot.
- The seabed's depth curve and materials.

## Where Strata's changes live

Decided: directly on Strata `main` (`~/code/strata`), which this Ur
worktree already builds against. Because other checkouts and sessions share
it, every Strata commit must leave the existing water, overlays and viewer
working: the ocean mode is additive and inactive until a quad uses the new
ocean code.
