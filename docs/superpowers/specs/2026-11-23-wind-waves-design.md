# Wind-driven waves (visual) — design

Date: 2026-11-23 · Status: draft for approval

## Intent

The ocean (docs/superpowers/specs/2026-11-22-ocean-water-design.md) is in
place but its waves ignore the weather. This is the first, visual step of a
larger "sea state" feature: wind and storms produce a daily sea state that
later disrupts ferries and drives coastal flooding, with player remedies
(larger ferries, artificial reefs, breakwaters, protected harbours). This
step makes the sea *look* like that sea state: waves follow Ur's wind, grow
with it and with storms, and are big on exposed coasts and calm in
sheltered water.

## Goals

- Swells run with the wind (Ur's `S.regional_wind`: speed km/h, heading),
  grow with wind speed and in storms (weather 3–4), and calm in light wind.
- Whitecaps appear on open water as the wind rises.
- Breakers roll in toward the shore — bands of white water that travel
  shoreward and break — strongest on coasts facing the wind.
- A **wave map**: wave height per padded parcel (the map and its 13-parcel
  ring), from wind and *fetch* (open water upwind), so the channel between
  the islands and the lee of a headland are visibly calmer. The later
  simulation step will compute the same map for gameplay and add the
  remedies' effects to it.

## Non-goals

- Gameplay effects (ferries, flooding), remedies, forecast UI: later steps.
- Moving geometry; ferries pitching and rolling (left for the simulation
  step, where ferry state will exist).

## Anti-goals

- A visible pop when the day (and so the wind) changes.
- Losing the voxel grain: every pattern stays quarter-voxel stepped.
- A GPU cost beyond +0.5 ms over today in the region and channel views.
- Any change to Strata's look when a game sets no sea state (the viewer and
  golden scenes stay identical).

## Approaches considered

- A. One global sea setting plus a windward test in the shader. Cheapest;
  cannot show sheltering by distance.
- **B. A plus a wave map uploaded to Strata. Chosen** — shows sheltering now
  and is where the remedies will act later.
- C. Moving geometry. Ruled out (cost, voxel look).

## Design

- **Strata sea state** (new, additive): `Vk.set_sea(wind_x, wind_z, height,
  whitecaps)` — wind direction (unit, xz), open-sea wave height in metres,
  whitecap amount 0..1 — and `Vk.set_sea_map(heights, w, h, x0, z0, cell)`:
  a wave-height scale 0..1 per cell of a `w × h` grid whose low corner is at
  (x0, z0) metres with `cell`-metre cells. Unset (all zero) keeps today's
  ocean exactly.
- **Shader** (`water.frag`, ocean quads only): swell direction from the
  wind; amplitude = global height × the map sample (bilinear, 1 outside the
  map); whitecaps on crests by wind; breaker bands travelling shoreward along
  the depth gradient, scaled by how squarely the shore faces the wind and by
  the local map height.
- **Ur sea state** (new pure module `Ur.Sea`): from `regional_wind` and the
  weather, eased between today and tomorrow by the clock so nothing pops;
  wave map per padded parcel from fetch along the upwind ray (water parcels
  of the coast field; leaving the padded grid over water counts as open
  ocean), recomputed when the day or the coast changes.

## Calls made (check these)

- Ferries' motion deferred to the simulation step (question left open).
- Wave height formula: fully developed height from wind speed over water,
  scaled by `sqrt(fetch / 5 km)` clamped to 0.15..1; storms ×1.6 (weather 4)
  and ×1.25 (weather 3). Tuned by screenshot, not physics.
- Wave map resolution: one value per parcel (8 m), bilinear in the shader.

## Revision (2026-11-23): voxel ocean, blended

After a prototype (branch `spike/voxel-ocean`) modelled on a Reddit
r/VoxelGameDev post (multi-layer Gerstner sum voxelised into a height field),
the wind shading becomes a **voxel ocean, blended with the clear coast**:

- **Waves:** a seeded sum of nine waves in three layers (swell, chop,
  ripples) spread round the wind. The peak wavelength follows
  Pierson–Moskowitz from the sea's wave height (λ ≈ 2πU²/g with
  U²/g ≈ Hs/0.21) and shortens with low exposure (fetch). Choppiness
  rises with the wind and sharpens the crests.
- **Look:** the height snaps to quarter-metre steps over two-voxel columns,
  coloured in five bands from trough navy to crest cyan with per-column
  jitter. Risers up to a higher neighbour are shaded as dark step lines, and
  foam clumps sit where the terraces steepen near crests. All of it animates
  with time.
- **Blend:** shallower than about 1 m stays clear turquoise water over the
  visible seabed, with glints and breakers. The terraced sea takes over by
  about 5 m. Reflections remain, toned down over the terraces.
- **Replaces** the noise-bent swells and random whitecap blotches from the
  first version. Breakers on windward shores stay.
- **Unset sea state:** unchanged (viewer and goldens identical).
- **Budget:** at most +0.5 ms GPU over the no-wind baseline in the region
  view. The prototype costs about +1.0 to +1.3 ms. Per-wave constants move to
  the CPU, and if that's not enough, a per-frame height tile in a compute
  pass.
- **Approaches considered:** replace (opaque and matte everywhere, the
  video's look), rejected because the clear shallows and glints carry the
  coastline the gameplay phase depends on; real moving geometry, deferred.
