# Industrial Production and Freight Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make industrial sites recognizable and let players change their output and earnings through actual resource supply, buyers, and freight access.

**Architecture:** Define a shared industrial catalog and a parcel freight ledger. The calendar advances that ledger once per simulated day, while settlement, diagnostics, rendering, and vehicle animation read its results. Replace the existing coarse food flow first, add manufacturing second, then migrate the managed island service to the same dispatch and accounts.

**Tech stack:** March, Forge, Strata voxel rendering, UR JSON saves.

**Spec:** `docs/superpowers/specs/2026-11-25-industrial-production-design.md`

## Global constraints

- Use the existing Strata voxel style, parcel orientation, and seeded variation.
- Keep existing nuisance and utility gates. Workshops can open at the Neighborhood limit, food processors at Commercial, and fabrication and assembly at Industrial.
- Shelf stock leaves the origin on loading and becomes usable at destination only after unloading.
- Title stays with the seller in transit and passes for each unit unloaded.
- During migration, assign each producer, buyer, and freight edge to a single accounting and dispatch path at a time.
- Resolve freight once per simulation day. Camera, lighting, and visibility never affect operations.
- Preserve the player's pending canal changes. Stage only task-owned changes and avoid rewriting unrelated files.

## Review focus

- An old or disabled shop, demolished lot, or replaced tenant cannot inherit a previous firm's reserved purchases or turn its inbound order into free inventory. Tasks 2 and 3 cover this.
- Partial unloading followed by spoilage must release the remainder of the budget reservation and count only the unloaded portion as sales. Task 2 covers this.
- Two cargo orders that use opposite directions of the same departure must share one capacity. Tasks 2 and 6 cover this.
- A founding map with no private shops still needs a viable first neighbourhood and processor. Task 4 covers this.
- A managed island voyage saved at cutover must keep its cargo, direction, remaining days, financial state, and route controls. Task 6 covers this.

## Task 1. Establish the catalog and distinguish industrial sites

**Files:** Add `lib/ur/industry.march`. Update `lib/ur/sim.march`, `lib/ur/landscape.march`, `lib/ur/market.march`, and `test/industrial_zone_test.march`.

**Interfaces:** `Ur.Industry.Kind` has `Workshop`, `ProducePacker`, `AssemblyPlant`, `SeafoodProcessor`, and `FabricationWorks`. `kind(code : Int) : Kind` and `code(kind : Kind) : Int` preserve saved codes 0, 1, and 2 for workshop, produce packer, and assembly respectively. Assign 3 to seafood and 4 to fabrication. `profile(kind : Kind) : Profile` supplies `name`, `nuisance`, `credential`, `power`, `water`, and baseline operating impact. Keep mixed-use code 1 interpreted by the zone before reading an industrial `Kind`. `Ur.Sim.industry_at(c : City, lot : Int) : Option(Ur.Industry.Kind)` is the common lookup for buildings and construction.

- [ ] In the industrial suite, exercise legacy codes 0–2 and round-trip the two new codes. Assert Neighborhood only permits the workshop, Commercial admits the two food plants, and only Industrial admits fabrication and assembly. Assert parcel and company names agree for built lots of each kind, including mixed use.
- [ ] Run `forge test --release test/industrial_zone_test.march` and confirm the added cases fail against the old catalog.
- [ ] Route labels, inputs, labor requirements, nuisance checks, utility loads, and market classification through the catalog. Preserve saved stock histories and the old market-sector meaning where historical names are required. Choose the two food types according to reachable farm versus fish supply and the two heavy types according to reachable downstream activity. Keep the existing delay between investment decisions.
- [ ] Make voxel models for all five kinds using the existing loading frontage and orientation. Share road-facing apron and service-door pieces across industrial forms. Give the workshop a coordinating mixed-use entrance. Orient the depot with the same access geometry and keep source-specific farm and fishery silhouettes. Keep worksite and repair overlays legible.
- [ ] Run the focused suite and `forge check`. Verify the native industrial scenario in Task 7. Commit the catalog and art changes together once the focused suite passes.

## Task 2. Implement deterministic commodity and freight operations

**Files:** Add `lib/ur/production_freight.march` and `test/production_freight_test.march`. Reuse weighted inventory arithmetic from `lib/ur/freight_network.march` where the required ownership behavior agrees.

**Interfaces:** `Commodity` covers `Crops`, `Catch`, `PackedProduce`, `ChilledSeafood`, `BulkMaterials`, `Parts`, `WorkshopGoods`, `FinishedGoods`, `Fuel`, `Waste`, and `LegacyFood` for stock without a saved commodity. Each has a stable saved ID, cargo-space factor, and shelf life. A separate `State` contains sites and their generation IDs, aged stock and carrying value, wallets and reservations, shipments, daily movements and loss, monthly accounts, last processed day, and next shipment ID. `empty() : State`, `site(state : State, lot : Int) : Option(Site)`, and `step(state : State, day : Int, conditions : Conditions) : State` are the public ledger interfaces. Conditions describe active site generations, yield, production limits, orders, and transport availability. Keep March game state and rendering out of the ledger module.

- [ ] Write a fixture with 10 units valued at $40, eight reserved at $7, three unloaded, and the other five lost. Assert three deposited, $21 seller revenue, $21 buyer purchase cost before delivery charges, zero reservation, five recorded losses, and no duplicated settlement on the same day. Add a replaced destination generation, two opposite-direction orders on shared capacity six, and one-tick lead time for a road-only delivery.
- [ ] Run `forge test --release test/production_freight_test.march` and confirm the missing behavior fails.
- [ ] Implement bounded inventory and recipe batches, dispatch and unloading capacity, reservation and payment by loaded order and accepted quantity, aging, and cancellation. Track owner through reroutes. On destination removal, return cargo to an active seller or transfer store if reachable, and book a loss if neither can accept it within the cargo hold limit. Rotate equal-priority buyers by day and sort remaining ties by lot and commodity. Preserve day identity across replay.
- [ ] Run the ledger suite, then commit the standalone module and fixtures.

## Task 3. Save the ledger and connect streets

**Files:** Update `lib/ur/sim.march`, `lib/ur/save.march`, `lib/ur/build.march`, and `test/production_freight_test.march`. Keep the shipment animation projection on the existing `Ur.Sim.Shipment` interface.

**Interfaces:** `City.production_freight : Ur.ProductionFreight.State`, `Ur.Sim.production_day(c : City, traffic : NativeIntArr, day : Int) : City`, and `Ur.Sim.production_at(c : City, lot : Int) : Option(Ur.ProductionFreight.Site)`. State serialization uses one optional `production_freight` object. The simulated day is `waste_date(c)` at the `roll_calendar` boundary, before month settlement.

- [ ] Extend the fixture with a city save between dispatch and receipt. Compare next-day stock, cash reservations, next ID, and monthly counters for uninterrupted and loaded runs. Decode a pre-feature save and assert old shop stock survives until its cutover. Add a lot demolition and rebuild with pending cargo, and verify the replacement cannot accept the old order.
- [ ] Confirm the cases fail with `forge test --release test/production_freight_test.march`.
- [ ] Add optional decode and validate nonnegative quantities and values, unique IDs, valid day and lot references, and shipment progress bounds. Initialize legacy cities without importing legacy stock until the cutover that takes ownership. Add named road dispatch over the existing `freight_stop`, `freight_entrance`, and road grade links. Use one cached multi-source search per candidate commodity and re-search only for exhausted or blocked choices. Project active physical loads to trucks through the existing `Ur.Food` freight activity code. Commit after the ledger suite and `forge check` pass.

## Task 4. Put food through processors and shops

**Files:** Update `lib/ur/industry.march`, `lib/ur/sim.march`, `lib/ur/fish.march` if catch scheduling needs a shared operating predicate, `lib/ur/hud.march`, `lib/ur/scenario.march`, and `test/industrial_zone_test.march`.

**Interfaces:** `Ur.Industry.recipe(kind : Kind) : Recipe` supplies input/output units per batch. In this increment both food recipes convert two raw units to one processed unit worth two food-equivalent units. A `production_day` adapter posts `crop_yield` or `catch_yield` once for each migrated lot. Derive per-parcel food availability and monthly operating results from the production ledger. Existing configured island participants remain assigned to their managed route through Task 6.

- [ ] Add a street fixture that delivers crop and catch to separate processors, ships both processed products to shops, sells to households, and reduces processor revenue when the road is cut. Assert zero input consumption while unstaffed or without power or water, and lower output when actual catch falls. Assert a unit sold as raw food cannot also be consumed by a processor. Cover founding harbour sales before the first shop and a subsequent shift to private sales.
- [ ] Confirm focus-suite failure before replacing the ordinary food path.
- [ ] Migrate ordinary shop stock and ordinary producer flow together. Assign uncategorized legacy shop food to a distinct migration stock bucket that satisfies food demand and expires under normal rules. Suppress the old `deliver_food` and storefront consumption effects for migrated participants. Replace their gross food credit in `services_with` and `food_room` with realized sales and a short forecast bounded by stock, orders, and the founding harbour outlet. Confirm fish stock withdrawal and farm yield use the same daily production records. Reserve a private working-capital balance at first opening and preserve any saved managed-route wallet. Apply the existing loss grace period from the first expected delivery date.
- [ ] Feed `business_accounts`, month settlement, and the parcel food inspector from the ledger for migrated sites. Run both focused suites and the existing founding and food tests listed by `rg -l 'deliver_food|food_used|freight' test/*_test.march`. Commit the first playable increment once a street fixture works from harvest through sale.

## Task 5. Add manufacturing, business purchasing, and gateway trade

**Files:** Update `lib/ur/industry.march`, `lib/ur/production_freight.march`, `lib/ur/sim.march`, `lib/ur/hud.march`, `lib/ur/market.march`, and `test/industrial_zone_test.march`.

**Interfaces:** Recipes convert two bulk materials to one part, one part to one workshop good, and two parts to one finished good. Freight gateway lots give import stock and external buyers explicit, shared daily handling and purchase limits. Parcel diagnostics read `production_at`, current shipments, and available supplier and buyer listings.

- [ ] Extend the city fixture with imports to fabrication, parts to a mixed-use workshop and an assembly plant, and sales to other businesses and the harbour. Assert a tariff affects landed input value, constrained handling limits purchases, withdrawn demand leaves stock unsold, and exhausted purchasing power prevents phantom orders. Assert plant emissions and loading activity subside when production stops.
- [ ] Confirm failure before wiring the input and demand adapters for the industrial chains.
- [ ] Add finite demand using staffing, business type, capacity, and regular turnover. Introduce employer orders for workshop and finished goods and finite external demand for finished goods. Set import/duty and export receipts at acceptance. Remove generic import cost and generic revenue for modeled goods at cutover. Cap orders by stock room, travel lead time, and accessible operating funds. Refresh the empty-lot forecast from reachable suppliers and buyers and partition idle reasons among utilities, staffing, inputs, buyer demand, and output room.
- [ ] Run focused and market suites, compare town startup against the baseline, and commit the second playable increment.

## Task 6. Bring managed service, ferries, and cargo canals into the ledger

**Files:** Update `lib/ur/freight_network.march`, `lib/ur/production_freight.march`, `lib/ur/sim.march`, `lib/ur/save.march`, `lib/ur/fleet.march`, `lib/ur/hud.march`, and `test/production_freight_test.march`.

**Interfaces:** The freight dispatcher uses departures identified by service and sailing day. Link capacity is shared in cargo-space units, with managed allocations first and residual space available to compatible private orders. Read active route, handling, and closure rules from the existing service helpers. Save migration takes the existing `Ur.FreightNetwork.Route` once and leaves a configured service with its original endpoints, priority, backup, and reserve settings.

- [ ] Save a managed food, fuel, and waste voyage with one day left. Migrate, run both uninterrupted and save/load paths, and assert equal arrival day, stock, municipal expenses, and monthly totals with no duplicate dispatch. Test regular ferry and cargo canal routing, passenger-only rejection, two-direction capacity contention, suspension and restart, and stranded perishable cargo.
- [ ] Confirm the expanded fixtures fail against the road-only integration.
- [ ] Move legacy producer, dock, shop, fuel, and waste stock, in-flight progress, and balances to the shared ledger. Keep precharged legacy voyage amounts marked settled and preserve lineage for in-flight goods. Replace the legacy managed step on the migration boundary. Fuel and waste facilities read usable arrived cargo. Feed the existing priorities and backup controls into the unified dispatcher. Show waiting cargo, estimated arrival, and the blocked or saturated link in the freight UI.
- [ ] Run the ledger, industrial, and canal suites. Compare the existing managed island scenario before and after migration and commit the third playable increment.

## Task 7. Verify the coastal scenario, appearance, and performance

**Files:** Update `lib/ur/scenario.march`, the existing demo entry points, and `README.md`. Use `scripts/verify.sh` and the new focused fixtures.

- [ ] Add a reproducible demo with road-facing farms, fisheries, processors, workshops, a heavy industrial block, and an active cargo link. Put industrial types on multiple frontage directions and include operating, construction, idle, and closed examples. Assert the demo's declared chains actually ship and sell as observed by the ledger.
- [ ] Make parcel and freight panels link or jump to related lots through existing selection or navigation actions. Record the demo setting and which road or cargo link to interrupt. Update the industrial zoning and freight sections of the README to describe observable behavior.
- [ ] Run `UR_VERIFY_RENDER=1 ./scripts/verify.sh`. Capture the industrial demo at base camera zoom by daylight and dusk, inspect it, and verify each loading frontage. Compare a fixed 90-day headless replay on starter and port saves against the same replay from before the change, recording wall time and peak memory. The existing `UR_BENCH` measures months on its own fixture and remains part of the verification script. Compare save/reload replay, inventory reconciliation, and private and municipal amounts across the complete demo. Commit after the checks pass.
