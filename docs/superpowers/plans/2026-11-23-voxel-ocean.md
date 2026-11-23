# Voxel Ocean (blended) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Turn the `spike/voxel-ocean` prototype into the real ocean shading on Strata `main`: a wind-driven voxel-terraced sea offshore, blended into the clear coast, within the GPU budget.

**Architecture:**
- Strata `sv_set_sea` additionally computes the nine waves' parameters on the CPU into the uniform block: direction, wavenumber, angular speed, amplitude share.
- `water.frag` evaluates the height sum per two-voxel column, with three evaluations per pixel (the column, +x, +z). It draws terraces, bands, step shading and foam, and blends with the clear shallows.
- Ur needs no changes beyond the sea state it already sends.

**Spec:** `docs/superpowers/specs/2026-11-23-wind-waves-design.md` (Revision section).

## Global Constraints
- Strata commits go on `main`, shared with other sessions. Every commit must leave `scripts/golden.sh` passing (no game sets a sea state there).
- Budget: per-frame GPU median, region view (`UR_DEMO=1 UR_SEA_DAY=17996 UR_CLOCK_HOUR=14 UR_REGION_VIEW=1 UR_PERF=1 UR_FRAMES=600`): at most +0.5 ms over the `wind-baseline` worktree (Ur `27ba58b`). Leave out runs pinned at 8.3 ms (GPU low-power), and use three valid runs each.
- Nothing from the prototype's `UR_SEA_STYLE` switch survives.

## Review Focus
1. **Unset sea:** no visible change in the viewer and the goldens.
2. **Near/far seam:** the straight diagonal seam seen in the prototype, where the level-0 sea meets the level-5 far tiles, must be gone. The far tiles use the same bands without terraces.
3. **Shimmer:** terraces must not crawl or alias when zoomed out (region view, moving camera). Fade the step lines and foam with pixel footprint.
4. **Day change:** the swell must not jump when the day's wind eases into tomorrow's (Ur already eases the sea state, so the shader must not add its own discontinuities).
5. **Night and storm:** banded water must stay readable at hour 2 and in storms, never grey or black.

---

### Task 1: Wave parameters on the CPU (Strata)
**Files:** `native/strata_vk.c` (`sv_set_sea`, UBO slots), `native/shaders/ubo.glsl`.
- [ ] Add `UBO_SEA_WAVES`: 9 × vec4 (dir.x, dir.z, k, ω) plus 3 vec4 of amplitude shares, holding the layer table from the prototype (`VOX_LAYER`). `sv_set_sea` fills it from the wind and height (λ = clamp(29.9·Hs, 6, 60) m). Exposure scaling stays in the shader.
- [ ] Raise `UBO_FLOATS` accordingly.
- [ ] Run `native/build_shaders.sh` and `scripts/golden.sh`: both must pass. Commit: "Sea state: the wind's wave spectrum computed once per frame".

### Task 2: Voxel ocean shading (Strata)
**Files:** `native/shaders/water.frag`.
- [ ] Port the prototype's `vox_height`, reading the precomputed waves (no per-pixel `atan`, `cos`, `sin` or `sqrt` per wave). Then port `vox_band`, the step shading, foam clumps and the blend into clear shallows (`smoothstep(1, 5, depth)`), plus the toned-down mirror over terraces.
- [ ] Remove the noise-based swell bend, wave groups and whitecap blotches. Keep the windward breakers in the shallows.
- [ ] On far tiles (`v_face >= 8`): bands from one height evaluation, no terraces, no neighbours.
- [ ] Fade step lines and foam with `fwidth(v_world.xz)` once a column is under about 2 pixels.
- [ ] Run `build_shaders.sh` and the goldens: both must pass. Commit: "Ocean: a wind-driven voxel sea of terraced, banded swells and crest foam".

### Task 3: Verify and tune (Ur and Strata)
- [ ] Take screenshots: windy, calm, storm (`UR_DEMO=22`) and night, in the region and channel views. Then a short frame sequence (8 shots, 0.25 s apart) to check that the terraces move and don't shimmer.
- [ ] Measure the budget as above. If it's over, store the terrace height per column in a compute-built tile (a follow-up task, not in this plan); report the numbers first.
- [ ] Run every Ur test file. Commit the tuning.
- [ ] Remove the `ocean-spike` worktrees and the `spike/voxel-ocean` branch, and the `wind-baseline` worktree after the last measurement.
