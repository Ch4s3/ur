# Ocean Water Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the sea around Ur's islands look like the ocean: depth-coloured translucent water over a visible seabed, rolling voxel-stepped waves, glints, shore foam, out to the horizon.

**Architecture:** Strata gains an *ocean quad*: a translucent top face whose second word carries the flag code 249 and four 6-bit corner water depths, and `water.frag` shades it (colour and opacity by depth, waves, glitter, foam, moon glint). Ur computes a coast distance field over the map plus a 13-parcel ring around it. From it Ur derives seabed heights (drawn as terrain in two layers below sea level) and the depth samples for its sea surface quads.

**Deviation from the spec:** no new water material or texture layer. Ocean quads carry their own flag, and the shader gives them their own roughness and colour.

**Tech Stack:** March (forge), Strata (Vulkan, GLSL compiled by `native/build_shaders.sh` into `native/strata_shaders.h`).

**Spec:** `docs/superpowers/specs/2026-11-22-ocean-water-design.md`

## Global Constraints

- Voxels are 0.25 m; parcels are 32 voxels; the map is 60 x 44 parcels (`S.width()`, `S.depth()`).
- Sea level is voxel height 0. A ground cell is water when `L.height(c, x, z) == 0`. Simulation heights never change: the seabed is only drawn.
- Depth samples are whole voxels, 0..63. 63 means "deep" (15.75 m or more).
- Strata work is committed directly on Strata `main` (`~/code/strata`). Every Strata commit must leave existing water, overlays (250–253), heat strips and the viewer unchanged. Ocean mode only switches on for quads flagged 249.
- Budget, measured in the `UR_DEMO=1 UR_REGION_VIEW=1 UR_CLOCK_HOUR=14` view: `gpu_ms` must not rise by more than 1.0 over the 4.1 ms baseline, and `quads` must not rise by more than 60 000 over the 108 396 baseline.
- Every pattern (waves, foam) is stepped to the voxel grain: quantise world xz to quarter-voxel steps, as the existing ripple does.

## Review Focus

1. **Coast changes in play.** When the coast changes (a land parcel lowered to water, a pier or reclaimed parcel), the seabed and the foam must follow on the next sync with no stale chunks. Pinned by Task 3's `field_changes_when_land_added` and Task 5's re-mesh rule.
2. **Night and storms.** At hour 2 and in heavy rain (weather ≥ 3), the sea must read as dark water, not grey or black. Checked by Task 6's hour-2 and storm screenshots.
3. **Flood water and data overlays.** These share the translucent pass and must look exactly as before. Checked by Task 2's golden run and Task 6's flood-demo screenshot.
4. **Map edges and corners.** The seabed and the depth field must be continuous where the map meets the ring, with no cliff or seam at parcel 0 or 59. Pinned by Task 3's `depth_continuous_across_map_edge`.
5. **Slot collisions.** Incident markers must never free sea or seabed chunks. Pinned by Task 1's `slot_ranges_disjoint`.

---

### Task 1: Separate sea slots from incident markers

The crime-incident markers use slots 10560–10591 (`scene.march:858`, `:926`, `:954-955`), and the sea tiles use 10561–10576 (`scene.march:103`). So `clear_incidents` frees sea tiles. Give the ocean its own slot range after the citizen slots.

**Files:**
- Modify: `lib/ur/scene.march` (`sea`, `citizen_chunk_slots`, new slot functions)
- Modify: `lib/ur.march:733` (`Vk.open_slots` count)
- Test: `test/ur_test.march`

**Interfaces:**
- Produces: `Ur.Scene.ocean_base() : Int` (= the old `citizen_chunk_slots()` value), `Ur.Scene.far_sea_slot(i : Int) : Int` (`ocean_base() + i`, i 0..15), `Ur.Scene.ring_cells() : Int` (= `(S.width() + 26) * (S.depth() + 26)`), `Ur.Scene.seabed_slot(cell : Int, layer : Int) : Int` (layer 0 or 1, `ocean_base() + 16 + cell * 2 + layer`), `Ur.Scene.slot_count() : Int` (`ocean_base() + 16 + ring_cells() * 2`). The surface quads go in the seabed layer-0 chunk (part 2), so they need no slots of their own.

- [ ] **Step 1: Write the failing test `slot_ranges_disjoint`.** Assert that `far_sea_slot(0) > 10591`, `far_sea_slot(15) < seabed_slot(0, 0)`, `seabed_slot(ring_cells() - 1, 1) < slot_count()`, and `far_sea_slot(0) >= Ur.Scene.citizen_walker_slot(199999)` (walkers keep their range).
- [ ] **Step 2: Run `forge test` and confirm it fails** (unknown functions).
- [ ] **Step 3: Implement the slot functions.** Use `far_sea_slot` in `sea`, and pass `Ur.Scene.slot_count()` to `Vk.open_slots` in `lib/ur.march`.
- [ ] **Step 4: Run `forge test` and confirm it passes.** Then take a screenshot with `UR_DEMO=1 UR_REGION_VIEW=1 UR_CLOCK_HOUR=14 UR_FRAMES=240 STRATA_SHOT=…`: the opaque teal sea sheet should now be visible.
- [ ] **Step 5: Commit** "Give the sea its own chunk slots".

### Task 2: Ocean quads in Strata

**Files:**
- Modify: `~/code/strata/lib/strata/quad.march` (header comment and the new functions)
- Modify: `~/code/strata/native/shaders/water.frag`
- Regenerate: `~/code/strata/native/strata_shaders.h` with `native/build_shaders.sh`
- Test: `~/code/strata/test/quad_test.march`

**Interfaces:**
- Produces: `Strata.Quad.ocean_flag() : Int` (= 249) and `Strata.Quad.ocean1(d00 : Int, d10 : Int, d01 : Int, d11 : Int) : Int`. The result is word 1: corner depths in voxels, each clamped to 0..63, at bits 0, 6, 12 and 18 (corners (0,0), (1,0), (0,1), (1,1) along u and v), and flag 249 in bits 24–31. Use it with `pack0(…, face 0)` in a translucent part. `ocean_depths(w1 : Int) : (Int, Int, Int, Int)` decodes it.

- [ ] **Step 1: Write the failing test.** `ocean1` round-trips (0,0,0,0), (63,0,63,0) and (1,2,3,4) through `ocean_depths` and through a `NativeI32Arr`. A depth of 80 comes back as 63 and -5 as 0. `flags_of(ocean1(…)) == 249`.
- [ ] **Step 2: Run `forge test` in `~/code/strata` and confirm it fails.**
- [ ] **Step 3: Implement `ocean_flag`, `ocean1` and `ocean_depths` in `quad.march`, and document the format in the header comment.**
- [ ] **Step 4: Run `forge test` and confirm it passes.**
- [ ] **Step 5: Add the ocean branch to `water.frag`.** It goes after the overlay-250 branch and before the 251–253 branch, and runs when `overlay == 249u && face == 0u`. It doesn't read the texture and doesn't use `class_roughness`.
  - **Depth.** `d` (metres) is the bilinear mix of the four samples, using `fract(v_uv / chunk-local quad size)`; follow how the overlay-252 branch maps `v_uv` to 0..1. Multiply by `u.eye.w`.
  - **Colour and opacity.** Colour mixes from shallow `vec3(0.16, 0.74, 0.70)` through mid `vec3(0.05, 0.42, 0.55)` (at 4 m) to deep `vec3(0.02, 0.13, 0.30)` (at 12 m). Opacity is `alpha = mix(0.35, 0.97, 1.0 - exp(-0.35 * d))`.
  - **Waves.** The normal tilt is two crossing wave sums, on xz quantised to 0.25 voxel. Use wavelengths about 6 m and 2.5 m and speeds about 0.6 and 1.1 rad/s. The amplitude is 0.06 in deep water, scaled by `smoothstep(0.0, 3.0, d)` so the shallows are calm. The existing 0.010 ripple stays for lakes and flood water.
  - **Mirror and lighting.** Use the same path as the existing smooth-surface code, with roughness 0.03: `mirror_share`, `reflected`/`sky_color`, the memory images (`wh_now`/`wd_now`), and `sun_highlight`.
  - **Glitter.** Add `u.sun_color.rgb * pow(max(dot(reflect(-toward, m), u.sun.xyz), 0.0), 400.0) * 2.5 * sun_vis`.
  - **Moon.** When `u.sun.y < 0`, add a glint from `normalize(vec3(-u.sun.x, 0.45, -u.sun.z))` in colour `vec3(0.55, 0.62, 0.80) * 0.6`, and lift the water colour by at least `vec3(0.010, 0.020, 0.040)` so night water isn't black.
  - **Foam.** `foam = (1 - smoothstep(0.15, 0.9, d)) * step(0.45, noise)`, where `noise` is a value noise on xz quantised to 0.25 voxel, drifting with `u.light.y * 0.4` along the depth gradient. Foam mixes the colour toward `vec3(0.93, 0.96, 0.97)` and raises alpha to at least 0.9.
  - **Output.** The result goes through `tonemap(fogged(col, v_world))`, as now.
- [ ] **Step 6: Run `native/build_shaders.sh` and confirm it exits 0** with no glslang errors.
- [ ] **Step 7: Run `scripts/golden.sh` and confirm every scene passes** unchanged. No scene uses flag 249, so any difference is a regression.
- [ ] **Step 8: Commit to Strata `main`** "Add ocean quads: depth-coloured water with waves, glitter and foam".

### Task 3: Coast distance field and seabed depths (Ur)

**Files:**
- Create: `lib/ur/ocean.march` (`mod Ur.Ocean`)
- Test: `test/ocean_test.march`

**Interfaces:**
- Produces:
  - `type Ur.Ocean.Field = { dist : NativeIntArr }`. Distances are in voxels, held on 4-voxel cells over the padded grid. The grid runs from parcel -13 to 72 in x (`(S.width() + 26) * 8` cells) and from parcel -13 to 56 in z.
  - `Ur.Ocean.field(c : Ur.Sim.City) : Field`. A cell is land when `L.height(c, cx * 4 + 2, cz * 4 + 2) > 0` inside the map. Ring cells are always water. Use a two-pass 3-4 chamfer distance transform, scaled to voxels (a step of 4 voxels per orthogonal cell).
  - `Ur.Ocean.depth(f : Field, x : Int, z : Int) : Int` returns voxels 0..63. Land is 0. Water is `S.clamp(2 + dist * 3 / 20, 2, 63)`, plus a deterministic ±1 ripple of `(x * 7 + z * 13) / 4 % 3 - 1` for texture, clamped to 2..63.
  - `Ur.Ocean.seabed(f : Field, x : Int, z : Int) : Int` returns `-depth`.
  - `Ur.Ocean.parcel_changed(a : Field, b : Field, cell : Int) : Bool` says whether any cell of padded parcel `cell` differs.

- [ ] **Step 1: Write the failing tests:**
  - `land_is_dry`: depth is 0 at a known land point of `S.new()`.
  - `shore_is_shallow`: a water cell beside land has depth 2.
  - `open_sea_is_deep`: depth is 63 at parcel (-12, -12).
  - `depth_never_drops_away_from_shore`: along a line from a coast cell outward, depth never decreases by more than the ±1 ripple.
  - `depth_continuous_across_map_edge`: next to the boundary between map parcel 0 and ring parcel -1, neighbouring cells differ by at most 2.
  - `field_changes_when_land_added`: set a water parcel's height to 8; `parcel_changed` is true for that parcel and its neighbours, and false 15 parcels away.
- [ ] **Step 2: Run `forge test` and confirm the tests fail.**
- [ ] **Step 3: Implement `lib/ur/ocean.march`.**
- [ ] **Step 4: Run `forge test` and confirm the tests pass.** Then time `Ur.Ocean.field(S.new())` in a test with `IO.Clock`: it must run in under 100 ms in a release build. If it doesn't, store `dist` per 8-voxel cell instead.
- [ ] **Step 5: Commit** "Add a coast distance field for the ocean".

### Task 4: Seabed meshes

**Files:**
- Modify: `lib/ur/scene.march` (a new `seabed` mesher beside `surface`, and new `seabed_parcel`/`seabed_all` functions)
- Modify: `lib/ur.march` (build the field at load and keep it in the play state)

**Interfaces:**
- Consumes: `Ur.Ocean.field/seabed/depth`, `Ur.Scene.seabed_slot`, `Ur.Scene.ring_cells`.
- Produces: `Ur.Scene.seabed_parcel(f : Ur.Ocean.Field, cell : Int) : Unit` uploads layers y = -32 and y = -64 for padded parcel `cell`. It frees them when the parcel has no water cell. `Ur.Scene.ocean_all(f : Ur.Ocean.Field) : Unit` does every cell.

- [ ] **Step 1: Write `seabed`.** It builds, like `surface`, from a 10 x 10 grid of `Ur.Ocean.seabed` heights with one cell of padding. Only water cells get a top face. Walls follow the `wall` rule.
  - **Materials:** sand 16 down to depth 10, then 1 (earth brown) down to depth 30, then 4 (dark slate) below that.
  - **Light:** `terrain_light` from the same heights, so the seabed shades and darkens with depth.
  - **Ring chunks:** these sit at padded positions outside the map, and their chunk origin is `(px * 32, y, pz * 32)` with negative px/pz allowed.
- [ ] **Step 2: Build the field when a city loads or is restored.** Store it as `ocean : Ur.Ocean.Field` in the play state, and call `ocean_all`.
- [ ] **Step 3: Build and take screenshots** at the channel and region views, hour 14. The seabed should be visible under the existing sheet if it's toggled off: temporarily skip `sea`.
- [ ] **Step 4: Commit** "Draw a seabed below sea level".

### Task 5: Sea surface of ocean quads, kept in step with the coast

**Files:**
- Modify: `lib/ur/scene.march` (`sea` → translucent ocean quads; surface quads in the seabed layer-0 chunk; `sync` re-meshes)

**Interfaces:**
- Consumes: `Strata.Quad.ocean1`, `Ur.Ocean.depth`, `Ur.Ocean.parcel_changed`.

- [ ] **Step 1: Add the near surface.** In `seabed_parcel`, the layer-0 chunk (y = -32) gets a part 2 of ocean quads at local y 31, so their top sits at sea level 0.
  - **Shore parcels:** one quad per 8 x 8-voxel patch that has any water cell, with corner depths sampled at the patch corners.
  - **All-deep parcels:** a parcel whose samples are all 63 gets one 32 x 32 quad.
  - **Land cells inside a patch:** they give depth 0, so foam meets the shore.
  - Also upload a layer-0 chunk for ring parcels that are all deep, with just the surface quad and no seabed.
- [ ] **Step 2: Make the far sea translucent ocean.** `sea` uploads its 16 level-5 tiles as part 2, `ocean1(63, 63, 63, 63)`, with the 4 x 4 tiles at y = -1. Skip any tile region already covered by the padded grid, so near and far surfaces don't overlap (no double alpha). Cut a hole at level 5 by emitting quads only for the parts of the 32 x 32 grid outside the padded rectangle.
- [ ] **Step 3: Re-mesh when the coast changes.** In `sync`, on a structural change where `old.heights` differs from `c.heights`, rebuild the field and call `seabed_parcel` for every padded cell where `parcel_changed(old_field, new_field, cell)` is true. Store the new field.
- [ ] **Step 4: Build and run the default views.** `quads` must stay within the 60 000 budget. If it doesn't, merge all-deep ring parcels into 2 x 2 groups.
- [ ] **Step 5: Commit** "Draw the sea as ocean water".

### Task 6: Tune and verify

- [ ] **Step 1: Take screenshots** at hours 7, 14, 19 and 2, in the channel and region views. Add one with weather ≥ 3 (use the scenario/env switch that forces a storm, or `UR_FLOOD_BACKUP=1`) and one of the flood demo. Save them beside the "before" shots in the session scratchpad.
- [ ] **Step 2: Tune and compare.** Adjust the colours, wave amplitude, foam width and depth curve within the shapes above until the sea reads as ocean: turquoise shallows, deep blue offshore, foam on every coast, glints by day, a visible moon glint at night. Compare the flood demo and the data layers with the before shots: they must be unchanged.
- [ ] **Step 3: Check the budget.** `gpu_ms` and `quads` in the region view must be within the budget.
- [ ] **Step 4: Run `forge test` in Ur and in Strata, and `scripts/golden.sh` in Strata.** Everything must pass.
- [ ] **Step 5: Commit the tuning,** in each repository that changed.
