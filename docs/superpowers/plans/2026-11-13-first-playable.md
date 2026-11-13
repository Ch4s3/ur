# First Playable Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** A runnable native island city-building slice with emergent growth.
**Architecture:** Pure aggregate simulation in Ur.Sim; Strata packed voxel meshes in Ur.Scene; input/UI/game clock in Ur. Simulation ticks are independent of rendered frames. Only changed parcels are uploaded.
**Tech Stack:** March, local Strata, Vulkan/GLFW, Strata text and UI.
**Spec:** docs/superpowers/specs/2026-11-13-first-playable.md

## Global Constraints
- Priority: fun, then Strata, then March performance.
- 0.25 m voxels; no voxel-by-voxel building.
- No player placement of private businesses.
- Work in the requested ~/code/ur checkout; preserve unrelated Strata changes.

## Review Focus
- Disconnected road islands must not grant economic access.
- Water/steep ground and insufficient funds reject construction without charging.
- UI clicks must not build behind panels; held input must not repeatedly charge.
- Pause, speed, and slow frames must not create unbounded simulation catch-up.
- Density, tax and energy bounds; growth constrained by power and jobs/housing.

### Task 1: Deterministic economy and construction
Files: lib/ur/sim.march, test/ur_test.march.
Interfaces: new() -> City; act(City, index, tool) -> City; tick(City) -> City; reason(City, index) -> String; access(City) -> NativeIntArr.
- [x] Write and run tests for rejected water/out-of-bounds/unaffordable building, connected vs disconnected roads, power, growth, high taxes and density.
- [x] Implement terrain, access flood fill, construction budget, growth and policy bounds.
- [x] Run forge test and a deterministic simulation benchmark.

### Task 2: Native playable scene
Files: lib/ur/scene.march, lib/ur/hud.march, lib/ur.march, forge.toml, run.sh; Strata absolute pointer bindings.
- [x] Render terrain, water, roads, zones and growing buildings with packed quarter-metre voxel quads.
- [x] Implement orthographic camera, picking, construction, policies, HUD and bounded clock.
- [x] Build and run scripted frame/screenshot smoke test; inspect the image and fix visible defects.

### Task 3: Verify and hand over
Files: README.md, docs/progress.md.
- [x] Independent code review and simplification; fix material findings.
- [x] Run tests, build, lint, scripted scene and simulation performance measurement.
- [x] Record controls, known limitations, results and next gameplay experiments.
