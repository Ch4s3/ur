# Reefs, Sand Bars and Fish Populations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The sea gains seeded reefs and sand bars that the swell, ferries
and fisheries respond to. Fish become a living, overfishable stock with an
overlay, and rare long storms reshape the sand.

**Architecture:**
- **Strata** (`Strata.Seabed`):
  - allows dry sand (depth −2..−1);
  - carries a per-cell kind grid (`Features`);
  - places reefs and bars (primitives and seeded generators);
  - reworks sand under a storm's swell.
- **Ur, the field:** `Ur.Ocean.field` layers the base shelf, the generated
  features, the saved storm changes and the player's edits.
- **Ur, per-day inputs:** the ocean job also derives two per-parcel
  arrays, **shoals** (for the ferry draft) and **habitat** (for fish).
  Play hands them to the day worker in `SeaView`, as it already does
  with the swell. The pure sim reads them only as City arrays.
- **Ur, new modules:** `Ur.Fish` (growth, spread, harvest) and
  `Ur.Sand` (storm trigger, rework job) run beside `Ur.Sea` in the day
  roll.

**Tech Stack:** March (forge). Strata at `~/code/strata`. GLSL is not
expected to change.

**Spec:** `docs/superpowers/specs/2026-11-24-reefs-and-sand-bars-design.md`

## Global Constraints

- **Strata work:**
  - committed directly on Strata `main` (`~/code/strata`), shared with
    other sessions, as for earlier water slices;
  - every Strata commit must keep `scripts/golden.sh` passing: no
    features, no change.
- **Tests:**
  - `forge test test/<file>.march`, one file per invocation, in each
    repo.
  - In March, `||` and `&&` evaluate both sides, so put recursion
    inside `if`.
  - Use distinctive type names. Don't read Float fields of another
    module's record in test builds.
- **Depths:** in voxels (0.25 m). Field cells are 4 voxels (1 m). A depth
  of **−2..−1 is dry sand**, 0 is land, and 1..63 is water.
  `Ur.Ocean.depth` returns −2..63.
- **Feature kinds:** 0 open floor (movable), 1 reef (fixed), 2 sand bar
  (movable).
- **Generated feature shapes:**
  - reef tops 4–12 voxels down (1–3 m);
  - bar crests −2..2;
  - fringing reefs 6–20 m off the coast;
  - patch reefs in 3–15 m of water.
- **Placement targets:**
  - about 40% of islands get a fringing reef;
  - 0–3 patch reefs and 2–5 bars a map;
  - at least one island with neither;
  - the shoals island always gets a reef.
- **Reef type from `setup[2]` (temperature):** 3–4 coral, 2 mixed, 0–1
  rocky. Fish capacity is 100 / 85 / 70.
- **Fish capacity per parcel:**
  - shelf 2–20 m: 35;
  - shelf edge: +15;
  - within 3 parcels of a river mouth: +20;
  - deeper than 20 m: 10;
  - bar or shallow sand (< 2 m): shelf value at most;
  - dredged: stripped to 10;
  - then × (100 − `pollution_at`)%.
- **Fish catch:** `128 × sqrt(density)`, where density is the run's stock
  over (run parcels × full-shelf capacity). Then times the existing
  resources, pollution and blessing terms, halved on rough days. A full
  coral run gives about 216 (spec: about 224); deep water gives about 68.
- **Ferry draft:**
  - standard 6 voxels (1.5 m), larger 10 voxels (2.5 m);
  - only cells shallower than the base shelf count;
  - closed below the draft, slowed within 2 voxels (0.5 m) of it;
  - the worse of the draft status and the sea status wins.
- **Shaping storm:**
  - 3 or more consecutive days of counted open sea ≥ 300 cm;
  - the target is once every 2–4 years on Normal, never on Calm (counted
    height is halved and surge is off);
  - one rework step per storm day, capped at 6;
  - each cell changes by at most 4 voxels (1 m) a storm and never rises
    above −2;
  - sand is conserved;
  - reef, land and cells deeper than 24 voxels (6 m) stay fixed.
- **Old saves:** a save without `sea_features` loads with
  `sea_features = 0`: no natural features, and the old fixed
  `catch_yield` (224 included). New games write 1.

## Review Focus

1. **A player reef or dredge on a dry-sand or bar cell.** `raise` must not
   sink dry sand; `dig` through a bar must deepen it. *(Task 1 test.)*
2. **A ferry built across a bar after load, before the next day roll.**
   `sea_shoals` must already be filled at load, or the draft rule waits a
   day silently. *(Task 5 test: load, then `ferry_status` without a day
   roll.)*
3. **A fishery whose run is cut short by land or the map edge (one parcel
   or none).** The density's denominator is the run's own length; a
   zero-length run catches 0 without dividing by zero. *(Task 6 test.)*
4. **A sand job finishing after the player edited the city.** Only
   `sand_changes`, `sand_due` and `message` are taken from the job; every
   other edit survives. *(Task 9 test.)*
5. **The Calm setting.** No shaping storm ever, and the draft rule still
   applies. *(Task 9 test with `setup[7] = 0` over a replayed year of 4 m
   seas.)*

---

## Slice 1: reefs, starting bars and the ferry draft

### Task 1: Strata — dry sand and the feature grid

**Files:**
- Modify: `~/code/strata/lib/strata/seabed.march`
- Test: `~/code/strata/test/seabed_test.march`

**Interfaces:**
- Produces:
  - `type Features = { floor : Seafloor, kind : NativeIntArr }`
  - `fn features(f : Seafloor) : Features`: every cell kind 0.
  - `fn reef_band(ft : Features, land : NativeIntArr, x0 : Int, z0 : Int, x1 : Int, z1 : Int, near : Int, far : Int, top : Int) : Features`:
    cells inside the rect whose coast distance (chamfer, 3 a cell) is
    from `near` to `far` cells become kind 1, with depth `top` where that
    is shallower.
  - `fn patch_reef(ft : Features, cx : Int, cz : Int, radius : Int, top : Int) : Features`
  - `fn bar(ft : Features, ax : Int, az : Int, bx : Int, bz : Int, width : Int, crest : Int) : Features`:
    a ridge along segment a–b, `crest` (−2..2) at its spine, easing to
    the floor over `width` cells, tapering over the last quarter at each
    end, and kind 2 where it rose more than 2 voxels.
  - `fn kind_at(ft : Features, x : Int, z : Int) : Int`
- Changes:
  - `depth_at` returns −2..63; −2..−1 is dry sand. Off the floor stays 0.
  - `edit_go` leaves cells ≤ 0 untouched for `raise`. `dig` deepens dry
    sand like any water cell, and still never touches land (the original
    land mask).
  - `depths_m` gives dry sand ≤ 0 metres, so `Strata.Waves` treats it as
    land.

- [ ] **Step 1: Write the failing tests** in a new
  `describe "Seabed features"`:
  - `test "a bar's crest pokes out and its ends taper"`:
    - with `bar(features(beach()), 5, 12, 35, 12, 3, -2)`:
      - `depth_at(…, 20, 12) == -2`;
      - `depth_at(…, 6, 12) > 0`;
      - `kind_at(…, 20, 12) == 2`;
      - `kind_at(…, 20, 30) == 0`.
  - `test "a reef band hugs the coast and stays below the surface"`:
    - with `reef_band(…, land, 0, 0, 39, 39, 6, 20, 6)`:
      - every cell of kind 1 has depth in 1..6;
      - at least one cell of kind 1 exists in row z = 8;
      - no cell at coast distance > 20 is kind 1.
  - `test "raising over dry sand leaves it dry"`:
    - `raise` over the bar's crest rect gives `depth_at == -2` there.
  - `test "dredging through a bar deepens it"`:
    - `dig(bar_floor, 18, 10, 22, 14, 12, 1)` gives `depth_at(…, 20, 12) == 12`.
  - `test "dry sand is land to the waves"`:
    - `depths_m` at the crest ≤ 0.0.
- [ ] **Step 2: Run** `cd ~/code/strata && forge test test/seabed_test.march`.
  Expect FAIL: `features` is undefined.
- [ ] **Step 3: Implement** the interfaces above in `seabed.march`, with
  docstrings in the module's style.
- [ ] **Step 4: Run** the seabed and waves tests and `scripts/golden.sh`.
  Expect all PASS.
- [ ] **Step 5: Commit** to Strata `main`: "Seabed: dry sand, a feature
  grid, reef bands, patch reefs and sand bars".

### Task 2: Strata — seeded reef and bar generators

**Files:**
- Modify: `~/code/strata/lib/strata/seabed.march`
- Test: `~/code/strata/test/seabed_test.march`

**Interfaces:**
- Consumes: Task 1.
- Produces:
  - `fn islands(land : NativeIntArr, w : Int, h : Int) : NativeIntArr`:
    4-connected land labels, 1.., with 0 for water.
  - `type FeatureRecipe = { reef_share : Int, patch_max : Int, bar_min : Int, bar_max : Int, forced : List((Int, Int)) }`
    - `reef_share` is a percent.
    - `forced` lists cells whose island always gets a fringing reef.
  - `fn default_recipe() : FeatureRecipe`: 40, 3, 2, 5, `[]`.
  - `fn generate(f : Seafloor, land : NativeIntArr, seed : Int, r : FeatureRecipe) : Features`

**Behaviour:**
- **Fringing reefs:**
  - each island gets one with chance `reef_share`, or always when forced;
  - it covers 1–3 noise-chosen stretches of the coast, each a
    `reef_band` with near 6, far 20 (in cells) and a seeded top of 4..12.
- **Patch reefs:** 0..`patch_max`, each on a shelf cell 12–60 voxels
  deep.
- **Bars:** `bar_min..bar_max` in total, placed by priority:
  1. bay mouths (water cells where land fills ≥ 45% of a 12-cell radius),
     spanning the mouth;
  2. gentle shores (coast distance to the 8-voxel depth line ≥ 8 cells),
     parallel to the coast;
  3. channels between two islands 6–24 cells apart.
  - Crests are seeded in −2..2.
- **At least one island has neither:** if every island got a reef or a
  bar, drop the features of the smallest island that isn't forced.
- **Seeding:** `Strata.Seed` throughout. No other randomness.

- [ ] **Step 1: Write the failing tests:**
  - `test "the same seed gives the same features"`: the floor and the
    kind arrays are equal, element by element.
  - `test "features stay in their ranges"`, for seeds 1..8 over a
    four-island fixture:
    - reef tops in 4..12;
    - bar crests in −2..2;
    - no kind > 0 on land.
  - `test "the counts land in the recipe"`, for seeds 1..8:
    - 2..5 bars, measured as connected kind-2 groups;
    - ≤ 3 patch reefs;
    - at least one island without kind 1 or 2 within 20 cells.
  - `test "a forced island always gets a reef"`, for seeds 1..8.
  - `test "no land, no features"`: an all-water grid gives all kind 0.
  - `test "a generated bar breaks the swell"`:
    - `Strata.Waves.solve_sea` over `depths_m` of a fixture with a bar;
    - the amplitude shoreward of the bar is < 0.8 × the amplitude at the
      same distance where there is no bar.
- [ ] **Step 2: Run** the test. Expect FAIL.
- [ ] **Step 3: Implement** `islands`, `default_recipe` and `generate`.
- [ ] **Step 4: Run** the seabed and waves tests and `scripts/golden.sh`.
  Expect all PASS.
- [ ] **Step 5: Commit** to Strata `main`: "Seabed: seeded reefs and sand
  bars round any coast".

### Task 3: Ur — the field carries natural features

**Files:**
- Modify: `lib/ur/ocean.march`, `lib/ur/sea.march` (`depths`,
  `water_mask`), `lib/ur/sim.march` (City fields, constructors),
  `lib/ur/save.march`, `lib/ur.march:228` (the `>= 12` depth test is
  unchanged but must read ≤ 0 as dry)
- Test: `test/ocean_test.march`, `test/save_test.march` (or the existing
  save round-trip test file)

**Interfaces:**
- Consumes: Tasks 1–2.
- Produces:
  - `Ur.Ocean.Field` becomes
    `{ floor : NativeIntArr, kind : NativeIntArr, shelf : NativeIntArr }`:
    `shelf` is the base shelf depth before features and edits.
  - `fn kind(f : Field, x : Int, z : Int) : Int`, in map voxels like
    `depth`.
  - `fn shelf_depth(f : Field, x : Int, z : Int) : Int`
  - `City.sea_features : Int`:
    - 0 none, 1 version 1;
    - new games (`unclaimed`, `unclaimed_setup`) set 1, as does the
      old `seed` map;
    - but `founding_map: false` gets no features regardless (see
      `natural`).
  - `City.sand_changes : NativeIntArr`: flat entries
    `cell * 256 + kind * 128 + (depth + 2)`. Empty in this task.

**The build order in `field(c)`:**
1. shelf;
2. `natural(c, shelf)`;
3. apply `sand_changes`;
4. parcel `edits`.

**`natural(c, shelf)`:**
- none when `sea_features == 0` or `!founding_map`;
- the classic map (`world_seed < 0`): `classic_features`;
- otherwise `Strata.Seabed.generate` with `world_seed` and
  `default_recipe()`, with `forced` set to the centre cell of the outer
  shoals island (`food_island` kind 2 — the parcel at design (55, 23),
  passed through `outer_coordinates`).

**`classic_features`:**
- a `reef_band` round the Fishing shoals island: design rect x 50..59,
  z 18..28, near 6, far 18, top 6;
- a `bar` 10–14 m off the main island's south shore, spanning design
  x 15..25, crest −1, width 3.

**Readers:**
- `swell_depths` takes the **shallowest** of the four 1 m cells under
  each 2 m cell, with ≤ 0 giving 0.0.
- `water_mask` and the scene's `wet` tests already use `> 0`. Check
  that each other `O.depth` reader treats ≤ 0 as dry.

**Saving:**
- `sea_features` and `sand_changes` are saved.
- Loading defaults them to 0 and empty.
- `sand_changes` needs an array of any length, with values up to about
  1e8. If `optional_array` assumes `S.count()` entries, add an
  `optional_list_array`.

- [ ] **Step 1: Write the failing tests** in `test/ocean_test.march`:
  - `test "a new seeded city has reefs and bars in its field"`:
    - `unclaimed_seeded(7)`;
    - its field has ≥ 1 cell of kind 1 and ≥ 1 of kind 2.
  - `test "a city saved before features has none"`:
    - `{ unclaimed_seeded(7) with sea_features: 0 }` gives all kind 0;
    - its floor equals the old shelf-plus-edits floor.
  - `test "the classic map's shoals island has a reef"`:
    - `unclaimed()`;
    - kind 1 within 3 parcels of design (55, 23).
  - `test "a thin bar still breaks the swell grid"`:
    - a field with a 1-cell-wide dry crest;
    - `swell_depths` is 0.0 at the 2 m cell over it.
  - Save round-trip:
    - `sea_features` survives;
    - a save JSON without the key loads as 0.
- [ ] **Step 2: Run** `forge test test/ocean_test.march`. Expect FAIL.
- [ ] **Step 3: Implement** the field, the City fields, the readers and
  the save.
- [ ] **Step 4: Run** `forge test test/ocean_test.march`,
  `test/sea_test.march`, `test/sea_works_test.march` and the save test.
  Expect all PASS.
- [ ] **Step 5: Commit:** "Ocean: seeded reefs and sand bars in the sea
  floor; old saves keep a bare shelf".

### Task 4: Draw reefs, bars and dry sand

**Files:**
- Modify: `lib/ur/scene.march` (the seabed and sea-surface chunk
  builders around lines 880–1000)
- Possibly: Ur's material table

**Interfaces:**
- Consumes: `Ur.Ocean.kind` and `Ur.Ocean.depth` (Task 3).

**Behaviour:**
- **Seabed voxels:**
  - kind 1 uses a reef material: warm coral tones when `setup[2] ≥ 3`,
    grey-green rock when ≤ 1, a blend at 2;
  - kind 2 and dry sand use pale sand.
- **Dry sand:**
  - the ground column rises to −depth (1–2 voxels above sea level);
  - no sea surface over it;
  - foam where the corner depth reaches ≤ 0, as on any shore.
- **Texture slots:** all 32 are taken, so reuse or replace one or two.
  Name the slot in the commit message.

- [ ] **Step 1: Run** with a seed known (from Task 3's test) to have a
  bar and a reef: `UR_SEED=7 ./run.sh` or the project's launch path.
  With the Strata MCP, point the camera at each and screenshot.
- [ ] **Step 2: Implement** the materials and the dry-sand column.
- [ ] **Step 3: Check against the screenshots:**
  - the bar reads as pale sand, partly above water, ringed by foam;
  - the reef reads as darker seabed under turquoise;
  - waves break along both.
  - Save `docs/reefs-and-bars.png`.
- [ ] **Step 4: Run** `forge test test/ocean_test.march`. Expect PASS.
- [ ] **Step 5: Commit:** "Draw reefs, sand bars and dry sand", with the
  screenshot.

### Task 5: Ferry draft rule

**Files:**
- Modify: `lib/ur/ocean.march` (`shoals`, and `Rebuild` gains `shoals`),
  `lib/ur.march` (`SeaView` gains `shoals`; `roll_day` writes it; the
  startup and load paths fill it), `lib/ur/sim.march`
  (`City.sea_shoals`, `ferry_status`, `ferry_day_go` text, inspector
  text at line ~2985)
- Test: `test/sea_rules_test.march`

**Interfaces:**
- Produces:
  - `fn Ur.Ocean.shoals(f : Field) : NativeIntArr`, per map parcel:
    - the shallowest depth (voxels, may be −2) among its 64 cells whose
      depth is less than `shelf_depth` there;
    - 63 where no cell qualifies.
  - `City.sea_shoals : NativeIntArr`:
    - all 63 in constructors;
    - not saved; filled from the field at load and startup, so the rule
      holds before the first day roll.
  - `fn ferry_draft(c : City, lot : Int) : Int`: 10 with a larger ferry
    at either end, else 6.
  - `fn crossing_shoal(c : City, a : Int, b : Int) : Int`: the minimum
    `sea_shoals` over the parcels `crossing_at` visits, or 63.
  - `ferry_status` returns 0 running, 1 slowed, 2 suspended (seas) or
    **3 closed (too shallow)**:
    - shoal < draft → 3;
    - shoal < draft + 2 → at least 1;
    - otherwise the sea status;
    - the larger value wins.
  - Every existing `ferry_status(…) < 2` test already treats 3 as cut.
    Check each call site listed by
    `grep -n "ferry_status(" lib/ur/*.march`.
- **Copy:**
  - Notification: "Ferry route closed: 0.8 m over a sand bar. Dredge a
    channel or move a terminal." Say "a reef" when the shallowest cell's
    kind is 1.
  - Inspector: "Closed: too shallow (0.8 m)".
  - **Landing survey layer (8):** water parcels with `sea_shoals` < 6
    show amber (shallower than a standard draft), so the player can see
    where a crossing will fail.

- [ ] **Step 1: Write the failing tests:**
  - `test "a bar across the crossing closes a standard ferry"`:
    - `ferry_route` fixture with `sea_shoals` = 2 on a middle parcel;
    - `ferry_status == 3`.
  - `test "water just over the draft slows it"`: shoal 7, status 1.
  - `test "a larger ferry needs deeper water"`:
    - shoal 8 with a larger ferry gives 3;
    - shoal 8 without one gives 1.
  - `test "the bare shelf never closes a route"`: all 63 gives the sea
    rule's status.
  - `test "rough seas and a shallow crossing: the worse wins"`.
  - `test "the rule holds right after load"`:
    - save and load a city with a shallow crossing;
    - `ferry_status == 3` without a day roll.
- [ ] **Step 2: Run** `forge test test/sea_rules_test.march`. Expect FAIL.
- [ ] **Step 3: Implement** `shoals`, the City field, the `SeaView`
  plumbing, the status and the copy.
- [ ] **Step 4: Run** `forge test test/sea_rules_test.march`, then
  `test/ocean_test.march`. Expect PASS.
- [ ] **Step 5: Commit:** "Ferries need water under them: reefs and bars
  close or slow shallow crossings".

---

## Slice 2: fish populations

### Task 6: Fish stock, growth, spread and catch

**Files:**
- Create: `lib/ur/fish.march` (`mod Ur.Fish`)
- Modify:
  - `lib/ur/sim.march`: City fields; `catch_yield`; move the fishing
    run here as `fishing_water`;
  - `lib/ur/food.march`: call `S.fishing_water`;
  - `lib/ur/ocean.march`: `Rebuild` gains `habitat`;
  - `lib/ur.march`: `SeaView.habitat`; `roll_day` calls `Ur.Fish.day`
    after `advance_day_with_traffic`;
  - `lib/ur/save.march`.
- Test: `test/fish_test.march` (new)

**Interfaces:**
- Produces:
  - `fn Ur.Fish.habitat(c : Ur.Sim.City, f : Ur.Ocean.Field) : NativeIntArr`:
    - per map parcel, the capacity before pollution, the 64-cell mean of
      the Global Constraints table;
    - stock units, with full shelf = 1000, so 35 → 1000;
    - river mouths from `S.river_mouths(c) : List(Int)` (new in sim):
      water parcels where a seeded island's river parcel meets the sea.
  - `City.fish : NativeIntArr`, `City.fish_capacity : NativeIntArr`:
    both saved; constructors zero.
    - On the first day roll with an all-zero `fish` and
      `sea_features ≥ 1`, stock is set to capacity.
  - `fn S.fishing_water(c : City, i : Int) : List(Int)`: the water
    parcels on fishery `i`'s run (the first water neighbour plus up to 3
    more, as `fishing_run` does now); `[]` when it has no open water.
  - `fn S.fish_density(c : City, i : Int) : Int`: percent (0..~300) of
    full shelf, over `fishing_water`; 0 for an empty run.
  - `catch_yield`:
    - when `sea_features == 0`, the old formula, untouched;
    - otherwise `128 × sqrt(density/100)` in place of the 128/224 base,
      with the other terms unchanged.
  - `fn Ur.Fish.day(c : Ur.Sim.City, habitat : NativeIntArr) : Ur.Sim.City`:
    1. `fish_capacity = habitat × (100 − pollution_at)/100`;
    2. each operating fishery removes `catch_yield × U` stock units,
       split across its run by stock share;
    3. logistic growth `r·N·(1 − N/K)` on every water parcel;
    4. on day 1 of each month, spread: each parcel passes
       `S% × (its fill − neighbour's fill)` to each fuller-to-emptier
       water neighbour.
    - `U`, `r` and `S` are module constants, tuned by the tests below.
    - Does nothing when `sea_features == 0`.

- [ ] **Step 1: Write the failing tests** in `test/fish_test.march`, each
  driving `Ur.Fish.day` over a fixture with fisheries placed through the
  sim's builders:
  - `test "full shelf catches today's base"`: one fishery over 4 full
    shelf parcels gives `catch_yield` equal to the old formula's 128-based
    value, ±1.
  - `test "a full coral run catches about 216"`: base 205..230.
  - `test "one fishery on shelf holds steady"`: after 3 × 360 days, the
    run's mean fill is in 65..85% and still within 5 points of the year
    before.
  - `test "two sharing a run decline slowly"`: after 1 year > 55%; after
    4 years < 50%.
  - `test "three overfish within two years"`: after 720 days < 33%.
  - `test "reef water carries twice the pressure"`: two fisheries on a
    reef run hold within 65..85% after 3 years.
  - `test "recovery"`: a run at 33% with no fishing reaches ≥ 80% within
    360..720 days.
  - `test "a protected patch refills its neighbour"`: an empty parcel
    beside full ones gains stock on the month's first day.
  - `test "a fishery with no open water catches nothing"`.
  - `test "old saves fish as before"`: `sea_features: 0` gives
    `catch_yield` equal to the old value (224 on the shoals island), and
    `day` leaves `fish` untouched.
- [ ] **Step 2: Run** `forge test test/fish_test.march`. Expect FAIL.
- [ ] **Step 3: Implement** as above. Tune `U`, `r` and `S` until the
  pressure tests pass. Record the values and the reason in a comment by
  the constants.
- [ ] **Step 4: Run** `forge test test/fish_test.march`, then
  `test/sea_rules_test.march` and the food or freight tests that touch
  `catch_yield` (`grep -ln catch test/`). Expect PASS.
- [ ] **Step 5: Commit:** "Fish: a stock in every water parcel that grows,
  spreads and can be overfished; habitat sets the catch".

### Task 7: Fish overlay, inspector and warnings

**Files:**
- Modify: `lib/ur/layers.march`, `lib/ur/overlay_field.march` (or the
  per-parcel material path), `lib/ur/toolbar.march`, `lib/ur/hud.march`
  (inspector), `lib/ur/fish.march` (warnings)
- Test: `test/fish_test.march`

**Interfaces:**
- **Layer 39:**
  - name "Fish";
  - legend "Fish · pale few / deep teal rich · striped: overfished
    (under a third of capacity)";
  - in the Resources page beside Groundwater and Oil potential:
    `1 -> [5, 6, 7, 8, 39]`;
  - icon "fish".
- **Colour:** water only, from `fish` (absolute, so reefs read richest).
  Land gets −1. Parcels under a third of capacity get a stripe material.
- **Inspector on water parcels:** "Fish: 40% of capacity, recovering ·
  Reef (coral)".
  - "recovering", "steady" or "falling" compares with the previous
    month's fill. Keep `City.fish_last : NativeIntArr`, written on
    month day 1. It needn't be saved; a missing value reads "steady".
  - Habitat name: Reef (coral, mixed or rocky), Shelf, Open sea, Sand.
- **Warnings** in `Ur.Fish.day`:
  - when a reef area (4-connected parcels whose habitat comes mostly
    from reef) drops below 33% mean fill: "The reef fishery off
    <compass side> is overfished: 30% of its fish remain.";
  - when it recovers past 67%: "The reef fishery off <side> has
    recovered.";
  - once each way, tracked per area in `City.fish_alerts`.

- [ ] **Step 1: Write the failing tests:**
  - `test "the fish layer colours water and skips land"`;
  - `test "an overfished reef warns once, and again on recovery"`.
- [ ] **Step 2: Run** `forge test test/fish_test.march`. Expect FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** the test, then the game: open Resources → Fish and
  screenshot to `docs/fish-layer.png`. Expect PASS, with reefs reading
  deep teal.
- [ ] **Step 5: Commit:** "A Fish layer, inspector line and overfishing
  warnings".

---

## Slice 3: storms reshape sand

### Task 8: Strata — sand rework under a swell

**Files:**
- Modify: `~/code/strata/lib/strata/seabed.march`
- Test: `~/code/strata/test/seabed_test.march`

**Interfaces:**
- Produces:
  `fn rework(ft : Features, swell : Strata.Waves.Swell, height : Float, steps : Int, mobile_depth : Int, max_change : Int) : Features`.
  - The swell is on a 2 m grid over the same area. Each floor cell reads
    its swell cell, and the floor's cell size is passed through the
    swell's own `cell` and `x0`/`z0`.

**Each step:**
1. **Energy:** E = (height × amp)² per movable cell (kind 0 or 2, depth
   −2..`mobile_depth`).
2. **Lifting:** a cell lifts sand ∝ E above a threshold (0 in calm
   water).
3. **Carrying:** lifted sand travels 1–3 cells along the wave direction
   (the unit gradient of `phase`), with a longshore share.
4. **Settling:** it settles first where E falls below half of its source
   cell's E. Otherwise it settles at the end of its travel.
- **Bounds:**
  - every cell's change over the whole call is within ±`max_change`;
  - never above −2;
  - sand that can't settle within bounds returns to its source;
  - total sand (the sum of depth changes) is exactly 0.
- **Kinds:** a cell that ends ≥ 3 voxels shallower than the shelf becomes
  kind 2. A kind-2 cell flattened to within 1 voxel of where it started
  becomes kind 0. Reef kind never changes.
- **Determinism:** same inputs, same output, with fixed iteration order.

- [ ] **Step 1: Write the failing tests:**
  - `test "sand is conserved"`: the sum of depths before equals the sum
    after over movable cells.
  - `test "no cell moves more than the bound or rises above -2"`.
  - `test "reefs and land never change"`.
  - `test "deterministic"`.
  - `test "a dredged trench across the surf partly refills"`: its depth
    after `rework(…, steps = 4)` is between the surrounding floor and the
    dredged depth, strictly.
  - `test "a breakwater's lee keeps its channel deeper"`: the same trench
    behind a land block (as a breakwater) ends deeper than the exposed
    one.
  - `test "calm water moves nothing"`: height 0.2 m leaves the floor
    unchanged.
- [ ] **Step 2: Run** the test. Expect FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** the seabed and waves tests and `scripts/golden.sh`.
  Expect PASS.
- [ ] **Step 5: Commit** to Strata `main`: "Seabed: a storm reworks sand
  under its swell, bounded and conserved".

### Task 9: Ur — the shaping storm, its job and its saved changes

**Files:**
- Create: `lib/ur/sand.march` (`mod Ur.Sand`)
- Modify:
  - `lib/ur/sim.march`: City fields `sea_run`, `sand_due`, `sand_peak`,
    `sand_sector`, `sand_day`;
  - `lib/ur.march`: `roll_day` calls `Ur.Sand.day`; a `SandJob` is
    polled like `OceanJob`;
  - `lib/ur/ocean.march`: `sand_touched` joins `rebuild`'s triggers;
  - `lib/ur/save.march`: saves the five fields.
- Test: `test/sand_test.march` (new)

**Interfaces:**
- Consumes: Task 8, `Ur.Sea.counted_on`, `Ur.Sea.sector`, and the City's
  daily wind.
- Produces:
  - `fn Ur.Sand.day(c : Ur.Sim.City) : Ur.Sim.City`:
    - if today's counted open sea is ≥ 300 cm, `sea_run + 1`, tracking
      the peak cm and the sector of the peak day;
    - otherwise, if `sea_run ≥ 3`, set `sand_due = min(sea_run, 6)`;
    - then reset `sea_run`.
    - Calm (`setup[7] == 0`) never sets `sand_due`.
    - Does nothing when `sea_features == 0`.
  - `fn Ur.Sand.storm(c : Ur.Sim.City, f : Ur.Ocean.Field) : SandResult`,
    pure, on a worker:
    1. `Strata.Waves.solve_sea` at `sand_peak` and `sand_sector`'s
       heading over `Ur.Sea.swell_depths`;
    2. `rework` over the field's features, with mobile depth 24 and max
       change 4;
    3. diff against the generated features (no `sand_changes`) to make
       the new `sand_changes`;
    4. compose the message.
  - `type SandResult = { changes : NativeIntArr, message : String }`
  - **Applying a result** to the *current* city sets only
    `sand_changes`, `sand_due: 0`, `sand_day` (today's absolute day) and
    `message`. For 30 days after `sand_day`, the Landing survey marks
    parcels holding changed cells in cyan. The ocean rebuild
    follows through `sand_touched`, and the shoals and habitat refresh
    with it.
  - **Message:** "The storm moved the sand: new shallows off the
    <side> coast." When a ferry crossing's `crossing_shoal` dropped,
    add "; the <terminal> crossing silted to 1.1 m". When it rose, add
    "; the <terminal> crossing deepened to 2.0 m". `<side>` is the
    compass side of the map with the most changed cells.

- [ ] **Step 1: Write the failing tests:**
  - `test "three days of 3 m seas make a shaping storm"`:
    - drive `Ur.Sand.day` with stubbed counted seas 310, 320, 305, then
      120;
    - `sand_due == 3`.
  - `test "two days do not"`.
  - `test "Calm never shapes"`: a replayed year of 400 cm seas at
    `setup[7] = 0` gives `sand_due == 0` throughout.
  - `test "a storm result keeps the player's edits"`:
    - apply a `SandResult` to a city whose roads changed after the job
      started;
    - the roads are kept, and `sand_changes` is the result's.
  - `test "sand changes survive save and load and rebuild the same field"`.
  - `test "after a storm the field differs only on movable cells"`.
- [ ] **Step 2: Run** `forge test test/sand_test.march`. Expect FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `forge test test/sand_test.march`, then
  `test/ocean_test.march` and `test/sea_rules_test.march`. Expect PASS.
- [ ] **Step 5: Commit:** "Long storms reshape the sand bars; the changes
  are saved and the ferries and fish follow".

### Task 10: Tune the storm's frequency by replay

**Files:**
- Modify: `lib/ur.march` (a `UR_SAND_REPLAY` mode beside
  `UR_RAIN_REPLAY`), `lib/ur/sand.march` (threshold constants)

**Behaviour:** `UR_SAND_REPLAY=<years>` rolls seas for that many years on
the classic map and seeds 1..4. It prints the shaping storms per year at
each Sea storms level, and the largest single-storm change in cells.

- [ ] **Step 1: Run** `UR_SAND_REPLAY=20 ./run.sh`. Record the
  frequencies.
- [ ] **Step 2: Adjust** the 300 cm threshold and the 3-day run until
  Normal gives one storm every 2–4 years. Expect Rough and Harsh more
  often and Calm never.
- [ ] **Step 3: Re-run** the replay and `forge test test/sand_test.march`.
  Expect the frequencies in range and PASS.
- [ ] **Step 4: Commit:** "Tune shaping storms to every 2–4 years at
  Normal", with the replay table in the message.
