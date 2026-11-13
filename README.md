# Ur

An early native March city-builder using the local Strata voxel engine.

**Priorities:** a fun game, then advancing Strata, then improving March performance.

## Play

```sh
cd ~/code/ur
./run.sh
```

`run.sh` selects the same toolchain as Strata, builds a release executable, and
runs it on the macOS main thread. The dependency is `../strata`. Strata's
Vulkan/GLFW/FreeType/HarfBuzz prerequisites must already be installed.

For a local macOS application wrapper after building:

```sh
./scripts/package.sh
open .march/Ur.app
```

The wrapper stays attached to this checkout; it is not a distributable bundle.

## First playable loop

Extend the harbour road. Zone housing and employment beside connected roads.
Households and businesses build automatically when there are jobs/customers,
affordable taxes and energy, and spare connected power. Extend across the channel
to the second island. Increase density to grow vertically. Aim for 500 residents
and a positive monthly budget.

| Control | Action |
| --- | --- |
| Click or drag | Apply the selected tool |
| 1 | Road; over water, a more expensive bridge |
| 2 / 3 | Housing / employment zoning |
| 4 | Power station; needs a connected road |
| 5 | Increase permitted density, up to three levels |
| 6 | Grade vacant land down by 2 m, to a minimum of 1 m |
| 7 | Clear a parcel (the harbour gateway is protected) |
| Arrow keys | Pan |
| Minus / equals | Zoom out / in |
| Space | Pause / resume |
| Tab | Toggle 1x / 4x speed |
| Left / right bracket | Lower / raise tax |
| Semicolon / apostrophe | Lower / raise energy price |
| F5 | Screenshot (`STRATA_SHOT`, default `strata_shot.ppm`) |
| Escape | Quit |

Hover a parcel for a development explanation. Each simulation month takes one
second at 1x speed. Roads permit at most 3 m of elevation change between parcels.
The initial map is 288 x 224 m, with 8 m planning parcels and 0.25 m voxel geometry.

## Verification and measurement

Run `./scripts/verify.sh` for all code checks, or
`UR_VERIFY_RENDER=1 ./scripts/verify.sh` to include the native rendering test.

```sh
source ../strata/scripts/env.sh
forge check
forge test
forge lint --strict
forge build --release
UR_BENCH=1000 .march/build/release/ur
MARCH_PIN_MAIN=1 UR_DEMO=1 UR_FRAMES=90 STRATA_SHOT=/tmp/ur.ppm .march/build/release/ur
```

`UR_DEMO=1` constructs a connected two-island expansion through ordinary player
actions, then advances it for 600 months. `UR_FRAMES` bounds a visual smoke test
and requests a screenshot on its final frame. `UR_INPUT_LOG=1` prints sampled
pointer state for diagnosing native input.

## Architecture and current limits

- `Ur.Sim`: deterministic parcel aggregates, road flood fill, power, construction
  budget, demand and policy-dependent private growth.
- `Ur.Scene`: packed Strata voxel quads; only changed parcels are reuploaded.
- `Ur.Hud`, `Ur.Input`, `Ur`: interface, gesture ownership and bounded simulation
  clock. Idle frames reuse cached population, jobs, power and road access.
- `Ur.Scenario`: reproducible expansion for integration tests and screenshots.
- Strata gains absolute cursor-coordinate bindings in window points. The changes
  are applied in the adjacent checkout and recorded in
  `docs/engine/strata-cursor.patch` for reproducibility.

This is the first gameplay slice, with placeholder procedural art. It does not
simulate the eventual tens of thousands of individual residents. Households and
employment are aggregates; wages, area income, land markets, differentiated
industries, trade chains, ferries, full-region streaming and most civic services
are future work. Existing buildings do not yet abandon when conditions worsen;
those conditions restrict new investment. Power currently follows the harbour
road network. Terrain grading is a parcel operation, not a voxel brush.

**There is no save/load yet.** Closing the app starts a fresh region next time.

See the [design](docs/superpowers/specs/2026-11-13-first-playable.md),
[implementation plan](docs/superpowers/plans/2026-11-13-first-playable.md), and
[progress and measurements](docs/progress.md).
