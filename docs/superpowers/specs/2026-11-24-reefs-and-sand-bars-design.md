# Reefs, sand bars and fish populations — design

Date: 2026-11-24 · Status: **for approval**. My calls are marked *(call)*;
everything else was decided in conversation.

## Intent

Today the sea floor around Ur's islands is a smooth shelf, identical round
every coast (`Strata.Seabed.shelf` from the coastline alone). The only reefs
are the ones the player builds (tool 119). This work gives the sea natural
features that the waves, the ferries and the fisheries all respond to:

- **Reefs** are generated with the islands. They hold fish, calm the water
  behind them, and can sit where they cause trouble.
- **Sand bars** are low ridges of seafloor near the shore. They don't hold
  fish, can't be built on, and are reshaped by rare big storms.
- **Fish populations** are a living stock on the water. You can see them as
  an overlay, like Groundwater and Oil potential on land, and you can
  overfish them.

When a feature lands somewhere awkward, like across a ferry crossing or in
front of the harbour, that's a problem for the player to solve. It's not
something generation steers around.

## Goals

- Reefs and sand bars generated from the map seed, deterministic, on
  seeded maps, plus a hand-placed set on the classic founding map.
- The swell (`Strata.Waves.solve_sea`) breaks over them and is calmer
  behind them. All existing sea rules follow automatically: ferry
  slowing and suspension, surge, rough-day fishing.
- A **ferry draft rule**: water too shallow along a crossing stops or slows
  the ferry. The player's fixes are dredging, moving a terminal, or a
  different route.
- **Sand bars** whose tops just break the surface or sit 1–2 voxels
  (25–50 cm) below it. You can't build on them.
- **Storm reshaping**: a storm that's strong and long enough, about once
  every few years on Normal, moves sand. Old bars flatten and new ones form.
  Dredged channels through sand partly silt up.
- **Fish**: a stock in every water parcel, with real-ish habitat rules,
  logistic regrowth, slow spread to neighbouring water, fisheries that
  draw from it, overfishing, a Fish overlay and inspector text.

## Non-goals

- Simulating past storms when a map is generated (rejected: "we aren't
  building Dwarf Fortress"). Starting bars come from a generator.
- Day-to-day sediment movement, tides, or bars that move outside rare storms.
- Fish species, migration seasons, or a fishing fleet you can see.
- Building on sand bars, or bars becoming land parcels.
- Storms changing reefs. Reefs change only through player edits.

## Anti-goals (failure even if it works)

- Bars or reefs that wander or pile up where nobody expects after a storm.
  Storm change must be bounded and readable.
- A new game or load that's noticeably slower. Generation runs where the
  ocean field is already built, on workers.
- Fishing that's crippled from day one. Stocks start full, and a
  fishery over full plain shelf lands today's base catch (128).
- Every island looking the same: some islands get no reef and no bar.

## What exists (on `main`)

- **Seabed**:
  - `Strata.Seabed`: `shelf`, `dig` and `raise` (with `raise` never going
    above depth 1, so water stays water), `depth_at` and `depths_m`.
  - `Ur.Ocean.field` builds a 4-voxel-cell floor over the map and its
    13-parcel ring: the shelf from the coast, then each parcel's
    `City.seabed` edit.
  - `Ur.Ocean.depth` uses 0..63, with 0 meaning land.
- **Waves**:
  - `Strata.Waves.solve_sea` refracts a sea of a given height over a 2 m
    depth grid. It already breaks on reefs and bars too shallow for it
    and passes less over them.
  - Depth ≤ 0 is land to the solver.
- **Today's sea**:
  - `City.sea_heights` (cm, per parcel) and `Ur.Sea.daily_seas` are
    computed with the day roll on its worker.
  - The Sea storms setting (`setup[7]`) scales what is counted.
- **Ferries**:
  - `crossing_sea` takes the worst sea along the straight line between
    two terminals.
  - `ferry_rating` is 220 cm, or 350 cm with a larger ferry.
  - `ferry_status` is running, slowed or suspended, and is stored in
    `ferry_works`.
- **Fishing**:
  - Fishery is plant kind 6, on a shoreline parcel.
  - `catch_yield` is fixed: 128, or 224 on the Fishing shoals island,
    times the resources setting, the pollution term and the blessing,
    and halved on rough days.
  - `Ur.Food.fishing_run` sends boats to the first water neighbour and
    up to 3 more parcels straight out: a run of up to 4 water parcels.
  - The 224 applies on seeded maps too (`food_island` kind 3, the
    outer shoals island).
- **Overlays**: `Ur.Layers` names, legends and the static `oil_at`;
  `Ur.OverlayField.deposits`.

## Approaches considered

- **A. Strata generates the features, Ur runs the rules.** Generators in
  `Strata.Seabed` at 1 m cell resolution, so bars are thin ridges. The fish,
  the draft rule and the triggers live in Ur.
- **B. Everything in Ur, as automatic `City.seabed` edits.** Quickest, but
  bars become 8 m blocks, nature gets mixed in with the player's edits, and
  Strata gains nothing.
- **C. A full sediment simulation.** Bars form and move on their own every
  stormy day. Most realistic, but costly and hard to tune to a rare event.
- **Chosen: a blend of A and C.** A generates reefs and starting bars at
  map creation. A small, bounded sand model (from C) runs **only on
  qualifying storms**. The user explicitly declined simulating past storms
  at generation.

## The design

### 1. Strata: natural features (`Strata.Seabed`)

**Allowing dry sand.** A cell's depth may be **−2..−1**: sand above the
surface, but not land.
- `shelf`, `dig` and `raise` keep their meaning. Everything that today
  treats exactly 0 as land must treat ≤ 0 as dry:
  - `edit_go` (behind `dig` and `raise`) must leave dry sand alone, or
    `raise` would push it under water (clamping with `most(1, …)`);
  - `depth_at` must tell "off the floor" apart from dry sand;
  - `coast_distance`'s land mask is still the true land mask, and dry
    sand isn't coast.
- Ur's `swell_depths` today reads one 1 m cell per 2 m swell cell. It must
  take the **shallowest** of the cells under each swell cell, so a bar one
  or two cells wide still breaks the swell. *(call, after the builder
  check)*
- A new `Features` record carries a per-cell **kind** grid alongside the
  floor:
  - 0 open floor (sand or mud, movable);
  - 1 reef (fixed);
  - 2 generated sand bar (movable; for drawing and habitat).
- **Reef generator** `reefs(floor, land, seed, warmth, …)`:
  - **Fringing reefs:** bands about 6–20 m off the coast, along
    noise-chosen stretches of some islands' coastline.
  - **Patch reefs:** a few blobs on the shelf in 3–15 m of water.
  - **Reef tops** sit 1–3 m below the surface (4–12 voxels). That's deeper
    than bars, so they read differently and refract rather than poke out.
  - `warmth` (0..4) sets the reef type: coral at 3–4, mixed at 2, rocky
    at 0–1. *(call)*
  - The type only affects drawing and fish capacity, not shape.
- **Sand bar generator** `bars(floor, land, seed, …)`:
  - Ridges roughly parallel to the coast, where the shelf is gentle (wide
    shallow water), and across **bay mouths** (concave coast, found by
    land fraction within a radius).
  - Sometimes in a shallow channel between two islands.
  - Ridge crests sit 2 to −2 voxels from the surface, so some poke out.
    They're a few cells wide and taper at the ends.
- **Placement targets** (tunable; a test pins them for a few seeds):
  *(call)*
  - About 40% of islands get a fringing reef stretch.
  - 0–3 patch reefs a map.
  - 2–5 bars a map.
  - At least one island has neither.
- **Storm rework** `rework(features, swell, height, steps)`: see §5.
- **Tests:**
  - deterministic for a seed;
  - reefs never on land and tops in range;
  - bar tops in −2..2;
  - an island-free seed gives no features;
  - a bar shoals and breaks a swell (through `Strata.Waves`);
  - dry sand counts as land to the solver.

### 2. Ur: building the field

- `Ur.Ocean.field` order:
  1. shelf from the coast;
  2. generated features (seeded maps: `world_seed`; classic map: a
     hand-placed set);
  3. **storm changes** (§5);
  4. the player's `City.seabed` edits.
- The field keeps the kind grid. It's needed for fish habitat and to know
  which cells the sand model may move.
- **Depth range:**
  - `Ur.Ocean.depth` becomes −2..63. Every reader that assumes 0 means
    land must treat ≤ 0 as dry: corner depth, foam, the seabed mesh,
    `swell_depths`.
  - Ur's own land rules read `heights`, so a dry bar is still a water
    parcel. It can't be built on and isn't a road.
- **Classic founding map** *(call)*:
  - a fringing reef off the **Fishing shoals** island (it's in the name),
    so its rich fishing comes from habitat instead of the hard-coded 224;
  - a bar across the main island's southern bay.
- **The old `seed` test map** (`founding_map: false`): no features. *(call)*
- **Old saves:**
  - A save without a `sea_features` version field loads **without
    natural features**, so existing cities don't suddenly gain a bar
    across their ferry. *(call)*
  - New games write version 1.
- **Drawing** *(updated during the build at the user's request: reefs look like coral, built by Strata's procedural generation)*:
  - **`Strata.Corals`** (new Strata module, beside `Strata.Trees`) bakes procedural corals into voxel templates from a seed: branching (staghorn), brain (a lumpy dome wound in ridges), table (a stalk under a ragged plate), sea fan (a flat lace in one plane) and tube sponge (open tubes). Each is one connected piece standing on its base, in a main and an accent colour.
  - **Reefs** are dotted with corals on a 2 m grid: each reef spot holds one with the reef type's chance (coral 60%, mixed 35%, rocky 20%), its species, variant and turn hashed from the spot. Coral reefs use every species, mixed reefs brains, fans and sponges among rock boulders, rocky reefs only boulders of reef rock. Corals are cut a voxel below the surface and meshed into the seabed chunk. The reef floor itself is dark reef rock.
  - Coral colours are saturated well past their colours in air so they show through the water's tint. Clearer water over reefs would be a Strata shader follow-up.
  - Bar cells use pale sand. Dry sand draws as a low sand column a voxel or two above the sea, in the seabed's second chunk slot (y 0..31), with foam round it from the shore depth.
  - Materials 37..43 are new texture layers (reef rock and six coral colours); `textures_create` takes 44 layers.

### 3. Ferry draft rule

- Each route has a **draft**: standard 1.5 m (6 voxels), larger ferry
  2.5 m (10 voxels). The larger ferry trades all-weather running for
  needing deeper water. *(call)*
- **Measuring:**
  - Take the straight crossing between terminals, sampled at cell
    resolution.
  - **Only cells shallower than the base shelf count.** That means
    generated reefs and bars, storm sand and player reefs. Terminals sit on
    land, and the base shelf is only 0.5 m deep at the shore (about 1.5 m
    some 7 m out, 2.5 m some 13 m out), so judging the bare shelf would
    close every route. The shelf near a slip is treated as the ferry's own
    approach. A cell counts with its own depth when that's below the
    draft and below the shelf there. *(call, after the builder check)*
- **Status:**
  - shallower than the draft → **closed: too shallow**, with the same
    network effect as suspended;
  - within 0.5 m of it → **slowed**;
  - otherwise the sea rule decides.
  - The worse of the draft status and the sea status wins.
- **Feedback:**
  - Inspector and notification: "Ferry route closed: 0.8 m over a sand
    bar. Dredge a channel or move a terminal."
  - The Landing survey or ferry tool highlights the shallowest cell.
- **Timing:** it's re-checked when the field changes (edits, storms), not
  daily.

### 4. Fish populations

- **State:** `City.fish : NativeIntArr`, a stock per **map** water parcel
  (0 on land), saved. *(call: map parcels only, since boats reach 3
  parcels out and the ring is never fished.)*
- **Capacity per parcel** is computed from the field whenever it is
  rebuilt, then times pollution:

  | Habitat | Capacity (relative) |
  |---|---|
  | Reef (coral / mixed / rocky) | 100 / 85 / 70 |
  | Shallow shelf, 2–20 m | 35 |
  | Shelf edge (steep drop within the parcel) | +15 |
  | Within 3 parcels of a river mouth (seeded islands with a river) | +20 |
  | Deep open water (> 20 m) | 10 |
  | Sand bar or bare sandy shallows (< 2 m) | 0 extra (shelf value at most) |
  | Dredged parcel | 0 extra; its habitat is stripped |
  | Pollution (`pollution_at`, 0..100) | × (100 − p)% |

  - A parcel's capacity is a cell-weighted mix of its 64 cells.
  - The player's reef tool counts as reef (mixed type). It starts empty
    and fills by growth and spread, so it takes about two years.
- **Growth:** logistic, with each day's growth r·N·(1 − N/K) on the day
  roll.
  - Tuned so a stock fished down to a third recovers to about 80% in 1–2
    in-game years with no fishing. *(call)*
  - Fastest at half full.
- **Sustainable pressure** (the tuning target for growth against
  harvest): *(call, after the builder check)*
  - one fishery alone over plain shelf holds steady indefinitely, at
    about 70–80% of capacity;
  - two fisheries sharing a run over shelf decline slowly, over a few
    years;
  - three or more overfish within about two years;
  - reef water carries about twice the pressure of plain shelf.
  - Stock is held in catch units, so one parcel's capacity is several
    months of one fishery's catch. The builder picks the scale.
- **Spread:** each month, a small share moves from fuller parcels to
  emptier water neighbours, by fill fraction. A protected patch refills
  its surroundings.
- **Fisheries:**
  - Each day a fishery harvests from the parcels on its fishing run,
    in proportion to their fill.
  - **Habitat sets catch** *(decided)*. The catch scales with the fish on
    the run, so it's set by both habitat and fill:
    - a run over full plain shelf lands today's base 128;
    - a full reef run lands more (about 224 for coral; mixed and rocky in
      proportion to their capacity);
    - deep water lands less.
    - The resources setting, pollution and blessing terms of
      `catch_yield` still apply on top.
  - Harvest is removed from the stock. Fisheries whose runs share parcels
    share the fish.
  - Rough days still halve the catch, and the Sea storms setting still
    applies as now.
- **The Fishing shoals island's 224** is replaced by habitat on the
  classic map (its hand-placed reef) and on seeded maps. There, the
  generator always gives the outer shoals island (`food_island` kind 2) a
  fringing reef, whatever the 40% target says. *(call)*
- **Old saves** load without natural features, so they keep today's
  fixed `catch_yield`, 224 included, until a new game. *(call)*
- **Starting state:** every stock starts at capacity.
- **Warnings:** a council or notification warning when a reef area (a
  connected run of reef parcels) falls below a third of capacity, and
  again when it recovers past two thirds.
- **The Fish overlay** (new layer, after Rainfall):
  - Water only, pale to deep teal by fill × capacity.
  - Legend: "Fish · pale few / deep teal rich · striped: overfished
    (under a third of capacity)".
  - Inspector on water: "Fish: 40% of capacity, recovering · Reef
    (coral)".

### 5. Storms reshape sand

- **Trigger:**
  - Track a run of consecutive days with today's counted open-sea height
    (the Sea storms setting applied) at or above a threshold, about 3 m.
  - A run of 4 or more days is a **shaping storm** *(tuned by replay: 3 days gave 1.3–4.5 storms a year at Normal; 4 gives about one every three years on average, from none to one a year depending on the map's climate)*.
  - Threshold and run length are tuned with a multi-year replay
    (`UR_SAND_REPLAY`, like `UR_RAIN_REPLAY`) to about once every 2–4
    years on Normal, more often on Rough and Harsh, and never on Calm.
    *(call)*
- **Where it runs:** when the storm ends, the day roll's worker (*built that way: no separate job, so nothing can race the player's edits*) runs `Strata.Seabed.rework`
  with the storm's dominant wind sector's swell (`solve_sea` at the storm's
  peak height). It takes one step per storm day, with a cap of about 6 steps.
- **The sand model**, each step:
  1. **Lifting:** sand is lifted from movable cells (kind 0 or 2, depth
     ≤ about 6 m) in proportion to local wave energy (amplitude²).
  2. **Carrying:** it moves along the wave direction (the phase gradient)
     and along the shore, a few cells per step.
  3. **Settling:** it settles where energy drops, mostly just shoreward
     of where the waves break.
  - **Bounds:**
    - sand is conserved;
    - no cell rises above −2 (never land) or changes by more than about
      1 m a storm;
    - reefs, land and deep water are untouched.
  - Deterministic for the same inputs.
- **Consequences:**
  - Dredged channels through sand partly refill.
  - Breakwaters and artificial reefs change the energy and so where
    sand settles.
  - The ferry draft and fish capacity are re-checked after a storm.
- **Saving:** the cells whose depth or kind changed are stored as a compact list `City.sand_changes` of **changes in depth** against the floor with its reefs, bars and the player's edits but no storms *(built that way: the field applies edits, then sand, so a silted channel stays silted and dredging it again digs deeper)*. Between storms it never changes.
- **Feedback:** one notification after a shaping storm: "The storm moved
  the sand: a new bar off the east coast; the channel at the harbour
  silted to 1.1 m." Changed cells briefly highlight on the Fish or
  Landing layer.
- **Tests:**
  - conservation;
  - bounds;
  - reef cells unchanged;
  - deterministic;
  - a dredged trench partly refills under a storm;
  - a breakwater's lee keeps its channel open better.

## Slices (each playable on its own)

1. **Reefs, starting bars and the draft rule.** Covers Strata generators
   and dry sand, the field order and drawing, the classic map's set, the
   save version and the ferry draft.
2. **Fish.** Covers stock, capacity, growth, spread, harvest, overlay,
   inspector and warnings. Replaces the fixed catch.
3. **Storms reshape sand.** Covers the trigger, `rework`, saved changes,
   notification and replay tuning.

## Left to the builder

- Exact generator parameters and noise, within the targets above.
- Texture-slot choices for reef and sand materials.
- Growth and spread constants, and sand model coefficients, within the
  tuning targets and bounds above.
- How dry-sand cells mesh (height and foam) as long as they read as sand
  just above the water.
- Where the Fish layer sits in the layer menu.
