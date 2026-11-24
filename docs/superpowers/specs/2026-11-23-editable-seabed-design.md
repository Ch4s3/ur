# Editable seabed and land reclamation (water slice 2) — design

Date: 2026-11-23 · Status: approved scope (seabed and land), building

## Intent

Players reshape the water: dredge it deeper, build reefs, reclaim land
from the sea, and cut harbours into the coast. The waves (`Strata.Waves`,
slice 1) respond to every change. The sea floor model lives in **Strata**,
so a future sailing, sandbox or god game can use it; Ur adds the city's
tools and rules.

## Strata: `Strata.Seabed`

- **Floor model:** a floor grid (voxels, negative below sea level) over
  cells of a game's chosen size, plus a coastline-derived **base**:
  - a chamfer distance from land (moved here from `Ur.Ocean`, generalised to
    any land mask);
  - a shelf profile (shore depth, slope, maximum);
  - and the game's **edits** on top.
- **Edits:**
  - `dig(rect, depth, margin)`: never shallower than before;
  - `raise(rect, depth, margin)`: never deeper than before.
  - Each eases over `margin` cells, so you get channels and mounds rather
    than pits and pillars.
  - A game stores its own compact edit list and replays it over the
    regenerated base, so saves stay small and the base is identical every
    time.
- **Bridges:**
  - `depths_m(voxel_m)`: metres for `Strata.Waves.solve`;
  - `depth_at(x, z)` (voxels), for meshing or a ship's keel.
- **Tests:** shelf depths from a land mask; a dig deepens and eases; a raise
  makes a shoal; an edit never cuts the other way; replaying edits matches
  applying them; a reef shoals the waves (through `Strata.Waves`).

## Ur

- **Seabed edits per map parcel:** `City.seabed : NativeIntArr`.
  - 0 means none.
  - A positive value is a dredged depth in voxels.
  - A negative value is a reef whose top is at that depth below sea level.
  - It's saved with the city; old saves load as all zeros.
- **The ocean:** `Ur.Ocean.field` builds its cell depths through
  `Strata.Seabed`: the base from the coast, then each parcel's edit over its
  8 × 8 cells, eased into neighbours. Everything that reads `Ur.Ocean.depth`
  (seabed mesh, sea surface, waves, exposure) follows.
- **Re-solving:** a change to `City.seabed` re-solves the ocean and the waves
  on workers, like coast changes. `coast_touched` notices it.
- **Tools** (Terrain group; prices are first guesses, to be tuned):

| Tool | Where | Effect | Price |
|---|---|---|---|
| Dredge (118) | water parcel, no seawall or ferry | 4 m deep, then 2 m deeper a click, to 15 m | $600 |
| Build reef (119) | water parcel, no seawall or ferry | a shoal 1 m below the surface | $900 |
| Reclaim land (120) | water parcel beside land, clear of seawalls, ferries and the harbour | becomes land 1 m above the sea, seabed edit cleared | $3,500 |
| Cut harbour (121) | empty low land (≤ 2 m) beside water, not the harbour or a ferry terminal | becomes water, dredged to 2 m | $3,000 |

- **Ferries, flooding and seawalls** keep their rules: they read
  `heights`, so a reclaimed parcel is coast and a cut parcel is water.
- **Icons:** reused for now (water, fish, grade, outfall). Proper art is a
  follow-up.

## Approaches considered

- Seabed only, with reclamation later: rejected by the user. Land is
  included.
- **A full per-cell editable seabed saved as a grid:** heavier saves and
  more state. **Base plus parcel edits: chosen** for small saves and
  deterministic regeneration. The Strata model still supports per-cell edits
  for other games.

## Left for later

Proper icons, a brush finer than a parcel, seabed sediment (tides moving
sand), and costs that scale with depth.
