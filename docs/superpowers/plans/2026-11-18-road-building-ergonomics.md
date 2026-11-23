# Road Building Ergonomics Implementation Plan

> For implementation, use the executing-plans skill and work through the checkboxes in order.

**Goal** — Make it quick to lay out a neighborhood and easy to revise a route around hills, shorelines, and developed blocks before spending money.

**Architecture** — Keep the existing parcel road network. Turn a player’s road draft into an explicit set of connected parcels, validate it using the current build rules, and use the validated result for both the preview and the commit. Keep drafts in the current play session.

**Tech stack** — March, Strata, the existing construction tools, and the existing save format.

**Design basis** — The road survey in this conversation. SimCity’s guides and block tools, Cities: Skylines II’s snapping and grid tools, and Transport Fever 2’s editable proposals inform the first three passes. [SimCity manual](https://akamai.cdn.ea.com/eadownloads/u/f/manuals/GAME-SIMCITY/SimCity_2013.pdf) · [Cities: Skylines II road tools](https://www.paradoxinteractive.com/games/cities-skylines-ii/features/road-tools) · [Transport Fever 2 street construction](https://wiki.transportfever2.com/gamemanual/streetstracks.html)

## Constraints

- Keep click-drag-release for a simple street. A guided build starts only when the player selects that mode.
- Surface streets stay on land. Keep the existing maximum of 3 m of elevation change between adjacent parcels. Keep the existing portal and span rules for overpasses, underpasses, and tunnels.
- A confirmed build charges once and takes one undo entry. Cancellation, invalid placements, and rejected council actions leave the city and treasury intact. Apply the same rules to single streets, grids, and replacements.
- Keep current lane routing, crossing behavior, utilities, and zoning frontage on the existing parcel network. Preview affected systems using the same checks used by the committed build.
- Resolve draft geometry and local validation as input changes. Run the city’s traffic, utility, and population updates through the existing commit path. Keep the 100,000-resident 3× performance target.

## File map

| File | Responsibility |
|---|---|
| `lib/ur/build.march` | Road plan footprints, validation, cost and upkeep quotes, and diagnostics shared by preview and placement |
| `lib/ur.march` | Draft lifecycle, mouse and keyboard controls, confirmation, council checks, and undo |
| `lib/ur/toolbar.march`, `lib/ur/hud.march`, `lib/ur/scene.march` | Tools, alignment guides, proposed streets and junctions, and impact readouts |
| `lib/ur/sim.march` | Existing road and crossing rules, including a shared crossing validation result |
| `lib/ur/scenario.march`, `test/road_planning_test.march` | Repeatable road-building playtest and planner regressions |

## 1. Put road drafts on one build path

- [x] Add a road-specific entry point in `Ur.Build` that accepts the proposed, ordered road parcels. Return the existing build result plus the first blocking parcel or edge, route length, maximum grade, and net monthly upkeep change. A shared junction or unchanged road tile contributes no extra purchase cost.
- [x] Route the existing quick drag through this entry point. Preserve the current bend and cost for an ordinary drag. Show the precise reason at the obstruction, with a distinct marker for water, a steep edge, or an occupied parcel. Keep citywide reasons such as insufficient funds visible in the quote.
- [x] Make confirmation revalidate the current draft against the current city. Exercise a $180 three-tile local street on flat land, a route with exactly 3 m of grade change and one over the limit, and a route whose final tile is blocked. The blocked route leaves every tile and dollar intact. Confirm and undo the valid route once.
- [x] Add a road-building district to the demo scenario with a small harbour approach, one ridge, and room for city blocks. Record the input count, build cost, and preview timing for the baseline routes.

## 2. Let players edit a route before committing

- [x] Offer **Quick street** and **Plan street** in Roads. In Plan street, select a start, add waypoints to go around obstructions, and drag a waypoint or endpoint to revise it. Allow either axis order for each bend and show the alternative before switching. Confirm with the HUD button or Enter. Escape or right-click discards the draft. Camera movement leaves the draft in place.
- [x] Add optional snapping to street ends, intersections, and straight alignments. Show the snap target before applying it. Use distance in screen space so snapping stays predictable across zoom levels, with a temporary bypass and deterministic selection when candidates tie.
- [ ] Exercise a shoreline route blocked in one bend order and valid in the other. Move a waypoint around a ridge, join an existing street end, bypass an unwanted snap, and cancel while a road tool is active. Verify that a stationary draft produces no repeated simulation work. The harbour-to-hill playtest should be completable in a single draft.

## 3. Make blocks and frontage easy to lay out

- [x] Add **Block** and **Grid** tools. Drag the outer rectangle and set block spacing in parcels. Align to a selected street when available. Preview the perimeter, interior streets, junctions, and adjacent parcels that gain road frontage. Treat frontage as road access in the preview, with utility and zoning eligibility shown separately.
- [x] Quote the cost of the unique set of road parcels and support fitting the layout to clear land by resizing before confirmation. A blocked interior street marks its obstruction and leaves the grid available to edit.
- [ ] Test one block, a two-by-two grid, and a grid sharing an edge with an existing street. Verify shared edges and intersections are charged once. Put a water tile inside the plan, resize around it, confirm, and undo. Playtest a neighbourhood around a pedestrian main street with two different block spacings.

## 4. Plan road tunnels and other crossings in three dimensions

- [x] Extract crossing validation in `Ur.Sim` so `build_grade` and the preview use the same portal, obstruction, and cost checks. Keep **Road tunnel** as a dedicated choice alongside **Overpass** and **Underpass**. Let the player reposition either portal before committing and explain unavailable crossing types at the proposed span.
- [x] Show both portals, span length, elevation difference, and total price. For a tunnel, use the Road crossings layer to show the buried route through terrain or under water, and draw the approach profile at each portal. For an overpass or underpass, show the ramp profile and clearance at the crossed street.
- [ ] Build and drive through two tunnel fixtures, one under a mountain ridge and one under a channel between islands. Both ends must be on land and connect to existing local streets or avenues. Verify vehicles enter and exit only at the portals, surface streets and buildings along the route remain intact, and both approaches join without an abrupt seam.
- [x] Exercise an invalid portal at a ferry terminal, overlapping crossing footprints, and a shallow crossing beyond its allowed span. Verify the preview identifies the blocker and a failed build leaves the treasury intact. Confirm that a valid tunnel matches its quote, persists across save and load, and can be undone or removed without tearing up the surface.

## 5. Upgrade streets by corridor

- [x] Add **Replace street** as a distinct tool. Select from one intersection to the next by default and let the player extend the selection. Preview road type, retrofit cost, maintenance change, and curb space affected. Keep the existing rules for road type, sidewalk objects, and incompatible features.
- [x] Highlight affected bus or tram infrastructure, stops, tolls, car-free schedules, and drainage. Preserve compatible features. When an existing rule blocks the conversion, identify the exact feature and location so the player can resolve it before re-previewing.
- [ ] Replace a local corridor with an avenue, then try converting a bus corridor to a pedestrian street. Verify the bus conflict is visible, resolve it, commit the eligible conversion, and confirm undo restores the original corridor and its attached features.

## Ship checks

- [x] Run `forge test test/road_planning_test.march`, `forge test test/ur_test.march`, `forge test test/citizen_movement_test.march`, and `forge build --release` from the Ur checkout with the Strata environment loaded.
- [x] Replay the harbour approach, neighbourhood grid, mountain tunnel, and underwater tunnel. Capture the editable preview and the built route for each. Compare gestures and redraws with the baseline.
- [x] Measure frame time while dragging and editing a large plan on the 100,000-resident 3× benchmark. Record p95 and worst frame time alongside idle and quick-drag baselines. Check that changing the cursor leaves full-city updates on the commit path.
- [ ] Load an existing city, confirm a road project, save, and reopen it. Verify network access, attached features, and treasury balance.

**Later work** — True diagonals and adjustable curves need a separate road-geometry design covering junction topology, frontage and zoning, sidewalks and parking, utilities, vehicle lane paths, and save compatibility. Reusable neighbourhood templates and parallel roads can build on the grid tools once the first five passes are playable. [Anno 117 road geometry diary](https://www.anno-union.com/devblog-all-roads-lead-to-anno/)


## Verification notes

The four road demos open with editable drafts. The harbour route quotes $540,
the grid $1,920, the mountain tunnel $3,410, and the channel tunnel $1,550.
Each has screenshots before and after construction in `.march/road-planning`.
The grid playtest exercised the spacing button, confirmation, and one-step
undo. Resizing now omits interior streets that would touch the perimeter
and leave no frontage between the two streets.

The in-game channel test started with $22,980, built the tunnel for $1,550,
saved, and undid the build in one step. Undo restored $22,980 and both
surface approaches. Reloading restored the $21,430 balance and linked portals.
The focused tests verified the vehicle route from either portal, the lack of
an entry from an interior parcel, and preservation of buildings above a tunnel.
They also exercised both bend orders, grid sizing and frontage, and a
corridor upgrade that preserves drainage and rejects a bus conflict.

The offscreen 100,000-resident run used 3× speed for all three cases. The
table excludes the first 30 frames and the screenshot frame. Preview
time measures validation and marker redraws. The idle and quick-drag runs
used the release before the last preview drawing changes. The in-game grid
spacing check then led to the frontage adjustment described above.

| Case | Frame p95 | Worst frame | Preview p95 | Worst preview |
|---|---:|---:|---:|---:|
| Idle | 477.41 ms | 2,779.02 ms | <0.01 ms | <0.01 ms |
| Quick drag | 505.28 ms | 2,717.65 ms | 0.39 ms | 0.46 ms |
| Grid edit | 503.88 ms | 2,963.01 ms | 1.94 ms | 3.35 ms |
| Final grid edit | 465.83 ms | 515.76 ms | 1.95 ms | 2.02 ms |

The FPS readout was 3 in the first three cases and 2 in the final grid
rerun. The final rerun supplied 69 frames after warmup and screenshot
exclusions. The 90 FPS target remains open.
