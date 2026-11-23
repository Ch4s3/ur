# Wind-driven Waves Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the ocean's waves follow Ur's wind and storms: swells run with the wind and grow with it, whitecaps appear, breakers roll in hardest on windward coasts, and sheltered water stays calm, using a wave map Ur uploads to Strata.

**Architecture:** Strata gains a *sea state*: a uniform (wind direction, open-sea wave height in metres, whitecaps) and a *sea map*, a per-cell exposure grid in a storage buffer. `water.frag` scales ocean waves by both. Ur adds a pure `Ur.Sea` module that turns wind and weather into a sea state, eased through the day, and builds the exposure map from fetch along the upwind ray over the coast field. `Ur.Scene` uploads the map when the wind's compass sector or the coast changes, and sets the sea state every frame.

**Tech Stack:** March (forge), Strata (Vulkan; GLSL built by `native/build_shaders.sh`).

**Spec:** `docs/superpowers/specs/2026-11-23-wind-waves-design.md` (builds on `docs/superpowers/specs/2026-11-22-ocean-water-design.md`).

## Global Constraints

- Strata work is committed directly on Strata `main` (`~/code/strata`), which other sessions share. Every Strata commit must leave the look unchanged when no game sets a sea state: `scripts/golden.sh` must PASS.
- Wind heading in Ur: radians, the direction the wind blows *toward*: (cos h, sin h) in (x, z). 0 is east, π/2 is south.
- Days last `S.day_seconds()` = 1.8 s at 1x, so nothing may be recomputed per day that costs more than about 1 ms.
- Patterns stay quarter-voxel stepped (`floor(xz / u.eye.w * 4.0) / 4.0`).
- GPU budget: median of 3 runs at most +0.5 ms over today, in the `UR_DEMO=1 UR_CLOCK_HOUR=14` region and channel views (as measured in the ocean plan).
- Tests: `forge test test/<file>.march`, one file per run (forge runs one `main` per invocation). In March, `||` and `&&` evaluate both sides: recursion goes in `if … do … else … end`.

## Review Focus

1. **Day changes:** wind heading and speed jump each 1.8 s day. Swell direction and height must ease, with no visible pop. Pinned by Task 3's `state_eases_between_days`.
2. **Unset sea state:** the viewer and every golden scene must look identical. Pinned by Task 2's golden run.
3. **Lee and channel shelter:** a parcel with land just upwind must read calmer than open coast. Pinned by Task 3's `lee_is_sheltered` and `open_sea_is_exposed`.
4. **Map edges:** exposure must not jump at the padded grid's edge or the map's edge. Pinned by Task 3's `exposure_continuous_at_ring_edge`.
5. **Calm days:** with light wind the sea must still move a little, never freeze flat. Checked by Task 5's light-wind screenshot.

---

### Task 1: Sea state and sea map in Strata (data path)

**Files:**
- Modify: `~/code/strata/native/strata_vk.c`: UBO slots `UBO_SEA 376`, `UBO_SEA_MAP 380`, `UBO_SEA_GRID 384`, with `UBO_FLOATS` raised to 388; descriptor binding 44 (a storage buffer for each frame in flight, `SV_SEA_CELLS 16384` floats); `sv_set_sea` and `sv_set_sea_map`.
- Modify: `~/code/strata/native/shaders/ubo.glsl` (add `vec4 sea; vec4 sea_map; vec4 sea_grid;` after `blobs`).
- Modify: `~/code/strata/lib/strata/ffi/vk.march` (externs and documented wrappers).
- Test: `~/code/strata/test/sea_test.march` (new).

**Interfaces:**
- Produces:
  - `Strata.Ffi.Vk.set_sea(wind_x : Float, wind_z : Float, height : Float, whitecaps : Float) : Unit`. It writes `u.sea`. A height of 0 means no sea state is set, which is the default, and the ocean looks exactly as before.
  - `Strata.Ffi.Vk.set_sea_map(exposure : NativeF32Arr, w : Int, h : Int, x0 : Float, z0 : Float, cell : Float) : Bool`. It is false, with nothing changed, when `w < 1`, `h < 1`, `w * h > 16384`, `cell <= 0`, or the array has fewer than `w * h` entries. Values are 0..1, row-major with x fastest. The low corner (x0, z0) and the cell size are in metres.
  - `u.sea_map = (x0, z0, cell, 0)` and `u.sea_grid = (w, h, 0, 0)`; `w == 0` means no map. The sea map is copied into each frame's buffer when its version changes. The pattern is: keep a CPU copy in `g`, bump a version number, and each frame copy into `F`'s mapped buffer when `F`'s version is behind.
  - The GLSL helper `float sea_exposure(vec2 xz)` (in `water.frag`) samples the map bilinearly with clamped edges, and returns 1.0 when there is no map.

- [ ] **Step 1: Write the failing test `sea_test.march`.** Before `open_slots`, `Vk.set_sea_map` returns false for every input (`g.ok` is 0). Assert that it is false for `w = 0`, for `w * h = 16385`, and for a short array. The test runs without a window, like `quad_test`.
- [ ] **Step 2: Run `forge test test/sea_test.march` and confirm it fails** (unknown function).
- [ ] **Step 3: Implement the externs, `sv_set_sea`, `sv_set_sea_map`, the UBO slots, binding 44 and the per-frame copy.** Declare `layout(std430, set = 0, binding = 44) readonly buffer SeaMap { float v[]; } sea_map_buf;` in `water.frag` only.
- [ ] **Step 4: Run `forge test test/sea_test.march` and confirm it passes.** Then run `native/build_shaders.sh` (exit 0) and `scripts/golden.sh` (PASS).
- [ ] **Step 5: Commit to Strata `main`:** "Sea state: a wind, wave height and whitecap uniform and a per-cell exposure map for ocean quads".

### Task 2: Wind-driven ocean shading in Strata

**Files:**
- Modify: `~/code/strata/native/shaders/water.frag` (`ocean_normal`, the foam block, a new breaker block).
- Regenerate: `native/strata_shaders.h` and the stamp in `strata_vk.c`.

**Interfaces:**
- Consumes: `u.sea`, `sea_exposure` (Task 1).
- Behaviour, when `u.sea.z > 0`:
  - **Wind and amplitude.** `wind = normalize(u.sea.xy)`. The local scale is `s = clamp(u.sea.z / 3.0, 0.15, 1.0) * mix(0.25, 1.0, sea_exposure(xz))`, where 3 m is a full sea.
  - **Swells.** The primary swell runs along `wind` (wavelength 6 m → 9 m as `s` grows; speed about `0.6 + 0.4 * s` rad/s). The secondary swell is ±35° off the wind. Normal amplitude is `0.03 + 0.07 * s`, and the shallows calm it as today.
  - **Whitecaps.** On crests (where the primary swell's phase is near its peak) mark a quarter-voxel cell with `step(1.0 - 0.35 * u.sea.w * s, hash)`. Mix it toward foam white at 0.8.
  - **Breakers.** The shoreward direction is the negative depth gradient, worked out from the four corners. `facing = clamp(dot(shoreward, wind), 0, 1)`. Bands travel shoreward: `fract(dot(xz, shoreward) / 5.0 + t * (0.25 + 0.2 * s))` gives a white band about 0.6 m wide where the depth is 0.2–2.5 m. Its strength is `facing * s`, and it widens into the existing shore foam where depth < 0.9 m.
  - **When `u.sea.z == 0`,** every branch keeps today's code path exactly.

- [ ] **Step 1: Implement in `water.frag`.**
- [ ] **Step 2: Run `native/build_shaders.sh`; confirm exit 0.**
- [ ] **Step 3: Run `scripts/golden.sh`; confirm PASS** (no scene sets a sea state).
- [ ] **Step 4: Commit to Strata `main`:** "Ocean: swells follow the wind, whitecaps, and breakers rolling in on windward shores".

### Task 3: `Ur.Sea`, the sea state and the exposure map (pure)

**Files:**
- Create: `lib/ur/sea.march` (`mod Ur.Sea`)
- Test: `test/sea_test.march` (Ur)

**Interfaces:**
- Consumes: `S.regional_wind(c)`, `S.weather_on(c, month, day)`, `Ur.Ocean.Field`, `Ur.Ocean.depth`, `Ur.Ocean.ring`, `padded_width`, `padded_depth`, `ring_cells`.
- Produces:
  - `type Ur.Sea.State = { wind_x : Float, wind_z : Float, speed : Float, height : Float, whitecaps : Float }`. Speed is km/h over water; height is in metres.
  - `Ur.Sea.state(c : Ur.Sim.City, phase : Float) : State`. `phase` is the time into the current day in seconds, 0..`S.day_seconds()`.
    - It eases from today's to tomorrow's wind with a smoothstep over the last 30% of the day. Heading eases by angle (shortest way round).
    - Speed over water is `regional speed * 1.5`.
    - `height = clamp(0.0012 * speed^2, 0.2, 3.5) * storm`, where storm is 1.6 for weather 4, 1.25 for weather 3, and 1 otherwise.
    - `whitecaps = smoothstep(25, 55, speed) * storm`, clamped to 0..1.
  - `Ur.Sea.sector(heading : Float) : Int` returns 0..15 (16 equal sectors, with sector 0 centred on east).
  - `Ur.Sea.exposure(f : Ur.Ocean.Field, sector : Int) : NativeF32Arr`. There is one value per padded parcel, row-major (`ring_cells()` entries).
    - A parcel is water when `Ur.Ocean.depth` at its centre is > 0; land parcels get 0.
    - For water, step from the parcel centre *upwind* (against the sector's centre direction) 8 m at a time, up to 100 steps. Count the metres of water until a land parcel. If the ray leaves the padded grid over water, the fetch is 5000 m.
    - Exposure is `clamp(sqrt(fetch / 5000), 0.15, 1)`, averaged over the sector's centre and its two edges (±11.25°) so sector changes are gentle.

- [ ] **Step 1: Write the failing tests:**
  - `state_eases_between_days`: at phase 0 and phase 0.69 × day, the state equals today's (within 1e-6). At the very end of the day it equals tomorrow's. Midway through the blend it lies between the two.
  - `storm_raises_the_sea`: on the first severe-rain day of `Ur.Scenario.storm_site()` (weather 4), the height is ≥ 1.6 × the same wind's calm height.
  - `open_sea_is_exposed`: a ring corner parcel has exposure 1.0 in every sector.
  - `lee_is_sheltered`: find a water parcel next to land on its west side. With the wind blowing east (sector 0), its exposure is ≤ 0.3. With the wind blowing west (sector 8), it is greater than that.
  - `exposure_continuous_at_ring_edge`: along the padded grid's outer row, neighbouring water parcels differ by ≤ 0.2.
  - `sector_wraps`: `sector(0) == 0`, `sector(6.2832) == 0`, `sector(-0.2) == 0`, and `sector(3.1416) == 8`.
  - `exposure_is_cheap`: `exposure(field, 0)` builds in under 30 ms in the test build.
- [ ] **Step 2: Run `forge test test/sea_test.march`; confirm it fails** (unknown module).
- [ ] **Step 3: Implement `lib/ur/sea.march`.**
- [ ] **Step 4: Run `forge test test/sea_test.march`; confirm `Sea checks passed`.**
- [ ] **Step 5: Commit** "Add a sea state and wave exposure map from wind and fetch".

### Task 4: Drive Strata from Ur

**Files:**
- Modify: `lib/ur/scene.march` (a new `sea_state(state : Ur.Sea.State) : Unit` and `sea_map(exposure : NativeF32Arr) : Unit`)
- Modify: `lib/ur.march` (Play gains `sea_sector : Int`; it starts at -1 so the first frame uploads)

**Interfaces:**
- Consumes: Task 1's `Vk.set_sea` and `Vk.set_sea_map`; Task 3's `Ur.Sea.state`, `sector` and `exposure`; Play's `ocean` field.
- `sea_map` uploads with `w = padded_width()`, `h = padded_depth()`, `x0 = z0 = -ring() * 8.0` metres (parcel 0 starts at 0 m; a parcel is 8 m) and `cell = 8.0`.

- [ ] **Step 1: Every frame, call `Ur.Scene.sea_state(Ur.Sea.state(c, phase))` next to `Ur.Scene.daylight`** (both call sites, `lib/ur.march:168` and `:541`). When `sector(heading)` differs from `p.sea_sector`, or the ocean field was rebuilt this frame, call `sea_map(Ur.Sea.exposure(ocean, sector))` and store the sector.
- [ ] **Step 2: Build with `forge build --release`; confirm exit 0.** Then run `UR_PERF=1 UR_DEMO=1 UR_REGION_VIEW=1 UR_FRAMES=900`. The median of the `update_ms` lines must stay within 0.05 ms of 0.50.
- [ ] **Step 3: Commit** "Drive the ocean's waves from Ur's wind and weather".

### Task 5: Tune and verify

- [ ] **Step 1: Take screenshots** in the channel and region views at hour 14:
  - a light-wind day and a strong-wind day (choose the dates with `UR_CLOCK_HOUR` and an env switch added for the demo: `UR_SEA_DAY=<absolute day>` advances the demo city's calendar to that day);
  - the storm site (`UR_DEMO=22 UR_FLOOD_DAYS=2`);
  - night (hour 2).
- [ ] **Step 2: Tune the constants within the shapes above until the sea reads right.** Swells must clearly follow the wind; the channel and lee shores must be calmer; breakers must be visible on windward coasts only; a light-wind sea must still move.
- [ ] **Step 3: Check the GPU budget.** Run 3 times each, baseline (HEAD before Task 1) against new, in the region and channel views. The median rise must be ≤ 0.5 ms.
- [ ] **Step 4: Run every Ur test file and Strata's `test/quad_test.march`, `test/sea_test.march` and `scripts/golden.sh`.** All must pass.
- [ ] **Step 5: Commit the tuning** in each repository that changed.
