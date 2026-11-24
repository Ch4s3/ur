# Local Rain Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rain falls in storm cells that cross the island; flooding, runoff, road pace and evacuations follow the rain on each parcel, updated three times a game day, and the clouds and rain the player sees are drawn from the same cells.

**Architecture:** A new pure module `Ur.Rain` derives each day's cells from the climate seed, date, regional weather kind and wind. `Ur.Sim` keeps the current hour's rain per parcel (`rain_now`), and at the end of each eight-hour watch turns the watch's rain into routed runoff, standing water, collector intake and damage; midnight drains. A `rain_uniform` flag (and Idra's curse) keeps today's island-wide code path untouched. Strata gains a small rain-cell uniform so rain streaks, puddles and wetness fall only under the cells.

**Tech Stack:** March (forge), Strata (Vulkan, GLSL compiled by `native/build_shaders.sh`).

**Spec:** `docs/superpowers/specs/2026-11-23-local-rain-design.md`

## Global Constraints

- Rain levels use the existing scale: 0 none, 1 cloudy (no rain), 2 rain, 3 heavy, 4 severe.
- Patchiness: rain (2) → baseline 2 + 1–2 cells level 3, radius 120–180 m; heavy (3) → baseline 2 + 1 cell level 3, radius about 200 m; severe (4) → baseline 3 + 2–3 cells level 4, radius 60–90 m; clear/cloudy → baseline 0, no cells.
- A cell crosses the island in roughly 6–12 game hours.
- Watches: 0 night (00–08), 1 day (08–16), 2 evening (16–24); they end at 08:00, 16:00 and midnight.
- Uniform rain (`rain_uniform`, or Idra's curse `curse_god(c) == 1`) runs today's daily `weather_day` path unchanged and never runs watches, cells or routing.
- Water reaches low ground within the same watch it fell; nothing carries between watches.
- Older saves may break: new save fields are required, not defaulted.
- Map is 60 × 44 parcels of 8 m (`S.width()`, `S.depth()`, `S.count()` = 2640); parcel centre in metres is `(x * 8 + 4, z * 8 + 4)`; heights are in quarter metres.
- Ur builds against `../strata`. While Task 7 is in progress, point a local, uncommitted `forge.toml`/`run.sh` at the Strata worktree (`../strata-weather`); never commit that path change. Fast-forward Strata `main` to the Strata branch before the final Ur commit.
- Build: `. ../strata/scripts/env.sh && forge build --release`. Ur tests: `forge test` (prints `Citizen movement checks passed` last). Strata tests: in the Strata checkout, `forge test` (`Finished: N tests, 0 failures`).

## Review Focus

- A cell that never touches land (crosses only sea): no parcel changes, no flood alert. → Task 5 test `a storm over open sea wets no land`.
- Day rollover in the middle of a storm: the night watch starts from the new day's cells, and `rain_now` at 00:00 is the new day's. → Task 2 test `rain_now resets at midnight`.
- A hollow whose rim is the map edge or the sea: water drains to sea instead of pooling forever. → Task 4 test `a hollow open to the sea does not pool`.
- Pausing exactly on a watch boundary, or running at 3× so one frame jumps past 08:00: the watch fires exactly once. → Task 6 test `a frame that jumps past 08:00 ends the night watch once`.
- Loading a save taken mid-watch: the watch index and `rain_now` match the stamped clock. → Task 2 test `save keeps the watch and rebuilds rain_now`.

---

### Task 1: `Ur.Rain` — the day's storm cells

**Files:**
- Create: `lib/ur/rain.march`
- Test: `test/ur_test.march` (new `rain_cell_checks()` called from `main`)

**Interfaces:**
- Produces:
  - `type Cell = { x : Float, z : Float, vx : Float, vz : Float, radius : Float, level : Int, start : Float, stop : Float }` — centre at hour 0 in metres, velocity in metres per game hour, radius in metres, rain level, active from `start` to `stop` hours (outside that window the cell rains nowhere).
  - `fn baseline(kind : Int) : Int` — 0, 0, 2, 2, 3 for kinds 0–4.
  - `fn cells(seed : Int, month : Int, day : Int, kind : Int, wind_speed : Int, wind_heading : Float) : List(Cell)` — pure; `wind_speed` in km/h and `wind_heading` in radians as `S.regional_wind` gives them; cells move along the heading.
  - `fn centre(cell : Cell, hour : Float) : (Float, Float)`
  - `fn level_at(cells : List(Cell), base : Int, x : Float, z : Float, hour : Float) : Int` — the larger of `base` and every active cell whose disc covers (x, z).
- Consumes: `Strata.Seed.cell`, `Strata.Seed.unit` for seeded choices (no dependency on `Ur.Sim`, so `Ur.Sim` can call this module).

- [ ] **Step 1: Write the failing tests** in `rain_cell_checks()`:

```march
let wet = Ur.Rain.cells(77, 3, 12, 4, 30, 0.6)
Test.assert_true(Ur.Rain.cells(77, 3, 12, 4, 30, 0.6) == wet, "the same seed and date give the same storms")
Test.assert_true(List.is_empty(Ur.Rain.cells(77, 3, 12, 1, 30, 0.6)) && Ur.Rain.baseline(1) == 0, "cloudy days have no rain")
Test.assert_true(List.length(wet) >= 2 && List.length(wet) <= 3 && List.all(wet, fn c -> c.level == 4 && c.radius >= 60.0 && c.radius <= 90.0), "severe days bring two or three storm cells")
Test.assert_eq_int(Ur.Rain.baseline(4), 3, "severe days rain heavily everywhere")
let rainy = Ur.Rain.cells(77, 3, 12, 2, 30, 0.6)
Test.assert_true(List.length(rainy) >= 1 && List.length(rainy) <= 2 && List.all(rainy, fn c -> c.level == 3 && c.radius >= 120.0 && c.radius <= 180.0), "rainy days bring one or two heavier bands")
let heavy = Ur.Rain.cells(77, 3, 12, 3, 30, 0.6)
Test.assert_true(List.length(heavy) == 1 && List.all(heavy, fn c -> c.level == 3 && c.radius >= 180.0 && c.radius <= 220.0), "heavy days bring one broad band")
Test.assert_true(List.all(wet, fn c -> c.stop -. c.start >= 6.0 && c.stop -. c.start <= 12.0), "a storm crosses the island in six to twelve hours")
Test.assert_true(List.all(wet, mid_crossing_on_map), "storms cross the island")
let first = unwrap(List.head_opt(wet))
let (cx, cz) = Ur.Rain.centre(first, first.start +. 1.0)
Test.assert_eq_int(Ur.Rain.level_at(wet, 3, cx, cz, first.start +. 1.0), 4, "under a storm cell the rain is severe")
Test.assert_eq_int(Ur.Rain.level_at(wet, 3, cx, cz, first.stop +. 1.0), 3, "once it has passed, only the baseline is left")
Test.assert_eq_int(Ur.Rain.level_at(wet, 3, -2000.0, -2000.0, first.start +. 1.0), 3, "far from every cell, the baseline")
```

with a test helper `pfn mid_crossing_on_map(c : Ur.Rain.Cell) : Bool` — the centre at hour `(c.start +. c.stop) *. 0.5` lies inside 0 < x < 480, 0 < z < 352.

- [ ] **Step 2: Run** `forge test` — Expected: fails to compile (`Ur.Rain` unknown).

- [ ] **Step 3: Implement `lib/ur/rain.march`.** Seeded choices per cell from `Strata.Seed.cell(seed, 700 + k, month, day, kind)`: count, radius within the kind's range, start hour 0–14, crossing time 6–12 h, cross-wind offset within the map. Velocity = crossing distance / crossing time along the heading, where the crossing distance is the map's extent along the heading plus the cell's diameter; place the hour-0 centre so the cell sits at the map edge (upwind, outside by its radius) at `start` and past the far edge at `stop`.

- [ ] **Step 4: Run** `forge test` — Expected: `Citizen movement checks passed`, no failures.

- [ ] **Step 5: Commit** `git add lib/ur/rain.march test/ur_test.march && git commit -m "Rain: seeded storm cells for each day's weather"`

---

### Task 2: City rain state, uniform flag and save

**Files:**
- Modify: `lib/ur/sim.march` (City type; `new()`; `unclaimed_with_heights`; rain helpers near `weather_on`, sim.march:610–706)
- Modify: `lib/ur/save.march` (encode near sim.march's weather fields, save.march:625–640; decode near 824–872)
- Modify: `lib/ur/scenario.march` (`storm_site`, `flood_backup_start`, `evacuation_site` set `rain_uniform: true`)
- Test: `test/ur_test.march` (`rain_state_checks()`)

**Interfaces:**
- Consumes: Task 1's `Ur.Rain.cells`, `Ur.Rain.baseline`, `Ur.Rain.level_at`.
- Produces (all in `Ur.Sim`):
  - City fields `rain_uniform : Bool`, `watch : Int`, `rain_now : NativeIntArr` (count() entries).
  - `fn uniform_rain(c : City) : Bool` — `c.rain_uniform || curse_god(c) == 1`.
  - `fn day_cells(c : City) : List(Ur.Rain.Cell)` — today's cells (seed `c.climate_seed`, or 705 when 0; kind `current_weather(c)`; `regional_wind(c)`).
  - `fn rain_level(c : City, lot : Int, hour : Float) : Int` — uniform: `current_weather(c)`; else `level_at(day_cells(c), baseline(kind), parcel centre, hour)`.
  - `fn set_rain_hour(c : City, hour : Int) : City` — fills `rain_now` for that hour (uniform: every land parcel `current_weather(c)`).
  - `fn rain_here(c : City, lot : Int) : Int` — `get(c.rain_now, lot)`.
  - `fn severe_now(c : City) : Bool` — any parcel's `rain_now` is 4.
  - `fn watch_of(hour : Int) : Int` — `hour / 8`.
- `advance_day_with_traffic` and `tick` finish with `set_rain_hour(c, 0)` and `watch: 0`; decode rebuilds `rain_now` with `set_rain_hour(city, hour from clock_ms)`.

- [ ] **Step 1: Write the failing tests** in `rain_state_checks()`:
  - `rain_now resets at midnight`: a non-uniform `S.new()` on a severe day (find one with `S.weather_on`), `S.advance_day` → `next.watch == 0` and `next.rain_now` equals `S.set_rain_hour(next, 0).rain_now` at every parcel.
  - `uniform rain is today's weather everywhere`: `{ c with rain_uniform: true }` → `S.rain_here(S.set_rain_hour(u, 10), lot) == S.current_weather(u)` for land lots.
  - `local rain differs across the island`: on a severe non-uniform day, some hour has a parcel at 4 and a land parcel at 3.
  - `save keeps the watch and rebuilds rain_now`: encode/decode a city with `watch: 1`, `rain_uniform: true`, `clock_ms` at 10:00 → decoded `watch == 1`, `rain_uniform`, and `rain_now` equal to `set_rain_hour(decoded, 10)`.
  - `the flood scenarios rain uniformly`: `Ur.Scenario.storm_site().rain_uniform`, `flood_backup_start().rain_uniform`, `evacuation_site().rain_uniform`.
  - `Idra's curse rains everywhere`: a cursed city (as in the existing curse test at ur_test.march:962) has `S.uniform_rain(cursed)`.
- [ ] **Step 2: Run** `forge test` — Expected: compile errors for the new names.
- [ ] **Step 3: Implement** the fields, helpers, scenario flags and save fields (`rain_uniform` as a bool, `watch` as an int, both required in decode; `rain_now` not saved).
- [ ] **Step 4: Run** `forge test` — Expected: passes.
- [ ] **Step 5: Commit** `git commit -am "Rain: per-parcel rain now, uniform flag, watch state"`

---

### Task 3: Readers follow the rain on their parcel

**Files:**
- Modify: `lib/ur/sim.march` — `rain_road_pace` (698), `severe_rain` users, `surface_flood` (771), `delay_for` (2970)
- Modify: `lib/ur/citizens.march:452,988`, `lib/ur/fleet.march:184`, `lib/ur/scene.march:787,838–839,1498,2448`, `lib/ur/hud.march:1416`, `lib/ur.march:454,469`
- Test: `test/ur_test.march` (`rain_reader_checks()`)

**Interfaces:**
- Consumes: Task 2's `rain_here`, `severe_now`, `set_rain_hour`.
- Produces:
  - `fn rain_road_pace(c : City, lot : Int) : Float` — by `rain_here(c, lot)` with today's table (4 → 0.43, 3 → 0.62, 2 → 0.81, else 1.0).
  - `surface_flood(c, lot)` live term: `floodplain_depth` when `rain_here(c, lot) == 4` (uniform cities fill `rain_now` from `current_weather`, so they behave as today).
  - `delay_for` uses `rain_here(c, i)` in place of `current_weather(c)`.
  - Island-wide "severe now" call sites (evacuation trigger, scene water probe and rebuild, flood layer, HUD shelter text, frame-loop flood triggers) use `S.severe_now(c)`; the scene's per-parcel probe uses `S.rain_here(c, i) == 4`.
  - Unchanged (regional): `severe_rain(c)` in HUD/scenario messages and the forecast, `solar_output`, temperature.
  - Sanitation (scene.march:1498) uses the pace at the depot parcel.

- [ ] **Step 1: Write the failing tests** in `rain_reader_checks()`:
  - `streets slow only under the storm`: non-uniform severe city at an hour with a level-4 parcel A and a level-3 parcel B → `rain_road_pace(c, A) == 0.43`, `rain_road_pace(c, B) == 0.62`.
  - `live flooding follows the storm`: a low basin parcel moved under a cell vs outside it (set heights as `floodplain_checks` does) → `surface_flood` > 0 only under the cell.
  - `uniform cities flood as before`: `floodplain_checks()` still passes unchanged (it uses `storm_site`, now uniform).
- [ ] **Step 2: Run** `forge test` — Expected: compile errors (`rain_road_pace` arity) or assertion failures.
- [ ] **Step 3: Implement** the reader changes listed above.
- [ ] **Step 4: Run** `forge test` — Expected: passes. Re-baseline only tests whose numbers change because they land on rain days, and say which in the commit message.
- [ ] **Step 5: Commit** `git commit -am "Rain: road pace, delay and live flooding follow each parcel's rain"`

---

### Task 4: Runoff routing

**Files:**
- Modify: `lib/ur/sim.march` (new functions beside `surface_day`, sim.march:5794)
- Test: `test/ur_test.march` (`runoff_checks()`)

**Interfaces:**
- Produces:
  - `type Runoff = { rained : Int, absorbed : Int, drained : Int, to_sea : Int, pooled : Int }` — water units summed over the map.
  - `fn route_runoff(c : City, amounts : NativeIntArr) : (City, Runoff)` — `amounts` is each parcel's watch rain (sum of eight hourly levels, 0–32); raises `surface_water` and returns the totals. `rained == absorbed + drained + to_sea + pooled` always.
  - `fn runoff_scale() : Int` — rain amount per quarter metre of pooled water; tuned in Step 4.
- Algorithm (spec "Runoff"): parcels sorted by height, highest first (ties by index); each land parcel adds its own `amount`, keeps `soil_absorption(c, lot)` scaled to a watch, sends the rest plus inflow to its lowest strictly-lower neighbour of the four (`neighbour(i, d)`); a road parcel with a storm drain removes up to its capacity to `drained`; flow into a height-0 parcel or off the map goes `to_sea`; a parcel with no strictly lower neighbour pools: water rises to at most its rim depth (`basin_depth` rim, at most 16) at `runoff_scale()` units per quarter metre, the rest spills to its lowest neighbour (which may be higher) and continues; the pass ends when every unit is placed. Process spill with a work list so spill order is deterministic.

- [ ] **Step 1: Write the failing tests** in `runoff_checks()` on hand-built height fields:
  - `water runs to the valley`: a slope of three parcels into a hollow, rain only on the top parcel → only the hollow gains `surface_water`.
  - `water is conserved`: the returned `Runoff` sums.
  - `a hollow open to the sea does not pool`: a hollow next to a height-0 parcel → `to_sea` > 0, hollow unchanged.
  - `a full hollow spills over its rim`: small rim, large inflow → the hollow sits at its rim depth and the next parcel down gains water.
  - `storm drains carry water away`: a road with `storm_drains` on the path → `drained` > 0 and less pooled downstream.
  - `uniform severe rain floods the same places as today`: on `Ur.Scenario.storm_site()` heights with `rain_uniform: false` and amount 32 everywhere, the set of parcels with `surface_water > 0` equals the set with `floodplain_depth > 0` (excluding coastal parcels), and depths differ by at most 4.
- [ ] **Step 2: Run** `forge test` — Expected: compile errors.
- [ ] **Step 3: Implement** `route_runoff` and `runoff_scale`.
- [ ] **Step 4: Run** `forge test`; tune `runoff_scale()` until the calibration test passes — Expected: passes.
- [ ] **Step 5: Commit** `git commit -am "Rain: runoff runs downhill and pools in hollows each watch"`

---

### Task 5: Watches in the daily simulation

**Files:**
- Modify: `lib/ur/sim.march` — `weather_day` (5978), `surface_day` (5794), `collect_rain` (5829), `advance_day_with_traffic` (6004), `play_month`, `tick`
- Test: `test/ur_test.march` (`watch_checks()`)

**Interfaces:**
- Consumes: Tasks 2 and 4.
- Produces:
  - `fn watch_rain(c : City, watch : Int) : (NativeIntArr, NativeIntArr)` — per parcel (peak level, amount) over hours `8 * watch` to `8 * watch + 7`.
  - `fn end_watch(c : City, watch : Int) : City` — non-uniform only: soil recharge (island mean amount; three watches of uniform rain equal today's daily recharge), `rain_runoff` pollution for parcels peaking 3+, `route_runoff`, coastal surge (`floodplain_depth`'s coastal part) on coastal parcels peaking 4, flood damage from the new level, per-parcel collector intake (today's catchment ÷ 3 by peak) and subway flooding where the parcel peaked 4 (today's amount ÷ 3), `flood_active`, then `watch: (watch + 1) % 3`.
  - `fn watch_recharge(level : Int) : Int` — soil recharge for a watch at that island mean level: a third of today's daily recharge (`24 + 15 * (level - 2)` for level ≥ 2, else 0).
  - `fn night_drain(c : City) : City` — today's `surface_day` drain rules for every parcel except those whose peak was 4 in any of today's watches; repair days count down; soil drying; `operate_weather_sites` with today's regional level.
  - `advance_day_with_traffic`: uniform → today's `weather_day` exactly; otherwise `end_watch(c, 2)` then `night_drain`. `play_month` (bulk) runs `end_watch` 0, 1, 2 and `night_drain` per day when not uniform.

- [ ] **Step 1: Write the failing tests** in `watch_checks()`:
  - `a severe cell floods where it crosses`: non-uniform severe day on a city with hollows both under a cell's path and far from all cells → after `end_watch` for the watch the cell crosses, the near hollow has water and the far one none.
  - `rain on high ground floods the valley`: rain amounts only on the mountain parcels (call `route_runoff` through `end_watch` with a city whose cells sit on the mountain) → a dry hollow below gains water.
  - `an 08:00 flood records damage`: a building on the flooded hollow has `flood_repair_days > 0` straight after `end_watch(c, 0)`.
  - `parcels hit by severe rain do not drain that night`: `night_drain` keeps their water; an unhit flooded parcel drains.
  - `uniform days run the old daily step`: for `storm_site()`, `advance_day` equals the result of applying today's `weather_day` path (compare `surface_water`, `soil_moisture`, `rain_tanks`).
  - `three watches add today's recharge`: `S.watch_recharge(L) * 3 == 24 + 15 * (L - 2)` for L = 2, 3, 4, and `S.watch_recharge(0) == 0`.
  - `a storm over open sea wets no land`: heights all 0 except a far island; a severe day whose cells miss the island (pick the date with `S.day_cells`) → after `end_watch` for each watch, `surface_water` unchanged and `flood_active` false.
- [ ] **Step 2: Run** `forge test` — Expected: failures.
- [ ] **Step 3: Implement** `watch_rain`, `end_watch`, `night_drain` and the day/bulk wiring.
- [ ] **Step 4: Run** `forge test` — Expected: passes, including the existing flood, flood-recovery and evacuation checks unchanged.
- [ ] **Step 5: Commit** `git commit -am "Rain: three watches a day carry local rain into the water simulation"`

---

### Task 6: Watches in the game loop, rainfall layer, replay

**Files:**
- Modify: `lib/ur.march` — frame loop around 419–470 (clock), day plan (570–577), `restore`, new `UR_RAIN_REPLAY`
- Modify: `lib/ur/layers.march` (layer 35 "Rainfall": name, legend, material), `lib/ur/toolbar.march:59,160` (add 35 to the layers page and its icon `"rain"`), `lib/ur.march:791` (clamp layers to 35)
- Test: `test/ur_test.march` (`watch_clock_checks()`)

**Interfaces:**
- Consumes: Tasks 2 and 5.
- Produces:
  - `fn watches_crossed(before_hour : Float, after_hour : Float) : List(Int)` (in `Ur.Sim`) — watches whose end (8 or 16) lies in `(before, after]`; midnight is handled by the day roll.
  - Frame loop: when the hour changes, `S.set_rain_hour`; for each crossed watch, `S.end_watch` (non-uniform) and drop `day_plan` (it restarts from the new city).
  - `type WatchResult = { stats : Ur.Sim.Stats, people : List(Ur.Citizens.Citizen), flooded : Bool }` and a `watch_plan : Option(Task(WatchResult))` field in `Play`. After a watch, a background task computes `S.stats(c)` and, when the watch left standing water, `Ur.Citizens.refresh_with(c, snapshot, stats.routes, stats.people, stats.job_matches)` from the roster snapshot taken at the watch (spec: nothing heavy in the frame). When it is ready the frame applies the stats, indexes the people (`Ur.Citizens.index`), and records the flood alert and scene sync as a flood day does. A new watch or an edit discards a pending result.
  - Layer 35: each land parcel coloured by today's peak rain level; watches already past drawn solid, the rest of the day (from `day_cells` at the remaining hours) faded. Legend: `Rain today · darker is heavier · faded is still to come`.
  - `UR_RAIN_REPLAY=<days>`: headless; prints one line per watch: `day=<d> watch=<w> kind=<k> flooded=<parcels with water> deepest=<max level>`.

- [ ] **Step 1: Write the failing test** `a frame that jumps past 08:00 ends the night watch once`: `S.watches_crossed(7.9, 8.2) == [0]`, `S.watches_crossed(8.0, 8.5) == []`, `S.watches_crossed(7.0, 16.5) == [0, 1]`.
- [ ] **Step 2: Run** `forge test` — Expected: compile error.
- [ ] **Step 3: Implement** the loop wiring, layer, toolbar entry and replay.
- [ ] **Step 4: Verify**
  - `forge test` — passes.
  - `forge build --release && UR_RAIN_REPLAY=6 ./.march/build/release/ur` — six days, three lines each; on severe days `flooded` rises across the day's watches and differs between watches.
  - `STRATA_HIDDEN=1 UR_DEMO=11 UR_LAYER=35 UR_FRAMES=60 STRATA_SHOT=/tmp/rain_layer.ppm ./.march/build/release/ur` on a rain day — the layer shows a band of darker parcels.
- [ ] **Step 5: Commit** `git commit -am "Rain: watches run at 08:00 and 16:00, rainfall layer, rain replay"`

---

### Task 7: Strata — rain where the cells are

**Files (Strata worktree, branch `claude/weather-effects`):**
- Modify: `native/shaders/ubo.glsl` (append after `sea_grid`: `vec4 rain_meta; vec4 rain_cells[16];`)
- Modify: `native/strata_vk.c` (`UBO_RAIN_META 452`, `UBO_RAIN_CELLS 456`, `UBO_FLOATS 520`; `sv_set_rain_cells`)
- Modify: `native/shaders/reflect.glsl` (`weathered`), `native/shaders/composite.frag` (`rained`), then `sh native/build_shaders.sh`
- Modify: `lib/strata/ffi/vk.march` (binding + doc)
- Test: `test/weather_test.march` (FFI-free checks only; rendering verified by screenshot in Task 8)

**Interfaces:**
- Produces:
  - `void sv_set_rain_cells(void *f32, int64_t n, double baseline)` — `n` ≤ 8 cells, 8 floats each: `x, z, radius, intensity (0..1), trail_x, trail_z, 0, 0` (trail: the vector from the cell back along the path it came, in metres; ground under it stays wet). `rain_meta = (n, baseline 0..1, 1 when set, 0)`; `n == 0 && baseline < 0` clears (`rain_meta.z = 0`), restoring today's global behaviour.
  - `fn set_rain_cells(cells : NativeF32Arr, n : Int, baseline : Float) : Unit` in `Strata.Ffi.Vk`.
  - Shader helpers in `sky.glsl`: `float rain_here(vec2 xz)` = max(baseline, each cell's intensity × (1 − smoothstep(0.75r, r, distance))); `float wet_here(vec2 xz)` = max(`u.weather.y`, 0.9 × each cell's trail falloff (distance to the segment from centre to centre + trail)). With `rain_meta.z == 0` both return today's globals (`u.weather.w`, `u.weather.y`).
  - `weathered` uses `wet_here(world.xz)` and `rain_here(world.xz)` for puddle rings.
  - `rained` (composite) scales streak density by `rain_here` at the ground point under the pixel: intersect the ray from `world_at(uv, 0.0)` to `world_at(uv, 1.0)` with the plane y = 5 m (no depth read needed); `u.weather.w` remains the upper bound.

- [ ] **Step 1:** Add the uniforms, C entry point and binding; rebuild shaders. Expected: `sh native/build_shaders.sh` succeeds.
- [ ] **Step 2:** Implement the shader helpers and their use; rebuild shaders.
- [ ] **Step 3: Run** `forge test` in the Strata worktree — Expected: `Finished: N tests, 0 failures`.
- [ ] **Step 4: Commit** (Strata) `git commit -am "weather: rain and wet ground under rain cells (sv_set_rain_cells)"`

---

### Task 8: Ur draws rain and storm clouds from the cells

**Files:**
- Modify: `lib/ur/scene.march` — `sky_for` (rain from the day's baseline when not uniform), `place_clouds` (types 3 and 5 placed along cells), new `rain_cells_for`; `lib/ur.march` call sites of `Ur.Scene.clouds`/`daylight`
- Modify: `docs/` screenshots

**Interfaces:**
- Consumes: Task 2 `S.day_cells`, `S.uniform_rain`; Task 1 `Ur.Rain.centre`; Task 7 `Vk.set_rain_cells`.
- Produces:
  - `fn rain_cells_for(c : Ur.Sim.City, hour : Float) : (NativeF32Arr, Int, Float)` — up to 8 active cells packed as Task 7 expects (intensity = level / 4, trail = −velocity × 3 h), and the baseline (level / 4); uniform cities return no cells and the regional rain as baseline.
  - `sky_for(c, kind)` rain = baseline / 4 when not uniform (cells add the rest).
  - Nimbostratus and cumulonimbus bodies: when cells are active, the first two bodies of each type sit at the nearest cell's centre (offset by `i`), scaled so the body spans about the cell's diameter; others keep their current placement. Their presence follows the cell, not the type amount.
  - `Ur.Scene.clouds` takes the city and hour to do this; `daylight` calls `Vk.set_rain_cells` each frame.

- [ ] **Step 1:** Implement; build (local pointer at `../strata-weather`).
- [ ] **Step 2: Verify by screenshot:** on a severe non-uniform day (find with `UR_RAIN_REPLAY`), `UR_DEMO=11 UR_ZOOM=300 UR_CENTER_X=240 UR_CENTER_Z=176 UR_CLOCK_HOUR=<cell hour>` — dark clouds over a band of the island, rain streaks and wet streets under them, drier streets elsewhere; compare against `UR_LAYER=35` at the same hour.
- [ ] **Step 3:** Fast-forward Strata `main` to the Strata branch (rebase first if `main` moved; regenerate `strata_shaders.h` on conflict); restore `forge.toml`/`run.sh`; rebuild against `../strata`; `forge test` in both repos.
- [ ] **Step 4: Commit** (Ur) `git add lib docs && git commit -m "Rain: storm clouds and local rain drawn from the day's cells"`
