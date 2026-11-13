# First playable progress

Plan: docs/superpowers/plans/2026-11-13-first-playable.md

## Delivered

Native March/Strata app with an angled overhead camera, 0.25 m voxel meshes,
two islands and mountain terrain, roads and bridges, housing and employment
zoning, emergent private growth, density, power stations, tax and energy policies,
limited grading, demolition, budget, development explanations and a 500-resident
milestone. Construction, pause, keyboard tools, and disconnected-plot feedback
were exercised in the running macOS app.

Simulation uses deterministic aggregates on 1,008 planning parcels. Rendering
uploads only changed parcels; idle frames reuse statistics and road access.

## Verification (2026-11-13)

- `forge check`: passed for seven application source files.
- `forge test`: all assertions passed, including an ordinary-construction
  expansion that reaches 500 residents and stays cash-flow positive.
- `forge lint --strict`: no issues found.
- `forge build --release`: passed.
- Native scenario: 180 frames drawn, 512 residents, 9,138 live quads, zero refused
  mesh uploads; screenshot inspected for world, buildings and UI.
- Simulation benchmark: 10,000 ticks in 274 ms (about 27 microseconds per tick)
  on this machine. This is a small, mostly saturated starter region, not proof
  of performance at the eventual tens-of-thousands scale.
- The final screenshot frame reported about 181 ms CPU including synchronous
  screenshot readback; it is not representative frame timing. Its reported GPU
  time was about 0.74 ms. A dedicated steady-state benchmark remains future work.

## Independent review and fixes

A fresh reviewer found three issues: bridge demolition was incorrectly rejected
on water, a drag beginning on the toolbar could paint the map, and picking a
high roof could target the next parcel. All three were corrected with regression
coverage. A simplification review prompted cached HUD statistics, gated mesh
synchronization, shared access calculations and typed development statuses.

Live testing found that polling the physical Cocoa cursor position misses
synthetic cursor-event positions. Strata's new pointer accessors now use its
cursor-event cache, with a physical-pointer fallback before the first event.
The complete engine diff is preserved in `engine/strata-cursor.patch` and is
already applied to `~/code/strata`; do not apply it twice. Existing unrelated
Strata changes were left untouched.

## March feedback

Reproduced Strata's documented S9: binding the result of the foreign frame call
to an unused name caused March to remove the rendering call. Ur consumes the
result in its drawn-frame counter. This warrants a focused compiler regression
and effect-preservation fix; this slice does not claim to fix March itself.

## Decisions and limits

Ruling: build directly in the requested new checkout, without another approval
step. Keep the first slice small enough to play and assess; its cost is that full
regional scale and differentiated economic behaviour remain future work.

Use aggregate demand and simple costs first. No save/load, abandonment, ferry
routing, individual citizens, area-income model, differentiated production chains
or full streaming region yet. Procedural buildings and terrain are placeholder
art. The fixed starting region and simple economy are tuning material, not a
finished balance model. The local app wrapper remains tied to its checkout.

Next gameplay experiments: make routes and building orientation easier to read;
add neighbourhood income and business specialisation; compare a ferry investment
against a bridge; then measure the expanded region before compiler optimization.
