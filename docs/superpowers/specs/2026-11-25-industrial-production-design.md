# Industrial buildings and production freight

## Goal

A player can recognize what an industrial site makes from its shape, see what keeps it running, and change its prospects by connecting suppliers, buyers, and freight infrastructure. A working farm or fishery, a nearby industrial zone, and a retail district should form an economic relationship the player can inspect and disrupt.

## Approaches

- A visual and economic pass could keep abstract trade and base industrial viability on reachable producers and buyers. It would improve map readability quickly, with no cargo to reroute when a link fails.
- A single food chain could prove production, inventories, sales, and disruption with crops and fish. Workshops and manufacturers would still use the existing abstract accounts.
- The selected scope is a full industrial production and freight system. Use one commodity ledger and common route capacity for several chains. Deliver the system in playable increments, starting with food because UR already has real crop yields, fish stocks, shops, and food freight. Extending the two existing freight paths independently would require reconciling two sources of stock and capacity on every shared route.

## Building catalog

Start with the existing zoning and resource systems. The following catalog and art direction are proposed defaults.

| Site | Inputs and outputs | Map silhouette |
| --- | --- | --- |
| Farm | Produces crops from existing irrigated yield | Field rows and a roadside produce shed |
| Fishery | Produces catch from existing fish stocks and weather | Quayside landing and sorting shed |
| Produce packer | Crops to packed produce, sold mainly by groceries | Broad low packing hall, intake canopy, pallet yard |
| Seafood processor | Catch to chilled seafood, sold by groceries and restaurants | Compact insulated halls with rooftop cooling equipment and recessed bays |
| Fabrication works | Bulk materials to parts, sold to workshops and assembly plants | Sawtooth-roof hall, overhead handling gear, stock yard |
| Workshop | Parts to workshop goods, sold to local businesses | Low gabled shop with shallow service yard and a wide vehicle door |
| Assembly plant | Parts to finished goods, sold to businesses and the export market | Long factory halls, roof monitors, and multiple loading bays |
| Depot | Receives, buffers, and dispatches cargo | Loading apron, repeated dock doors, covered storage |

Bulk materials start as regional imports through the harbour. Local primary production uses crops and fish from day one. The current oil prospecting layer supplies information for a later resource design. That keeps the playable chains grounded in resources the map already simulates.

Use the existing Strata voxel style, parcel orientation, and seeded variation. Give industry a consistent family of masonry or concrete bases, steel roofs, service doors, and loading markings. Keep the distinguishing roof and yard forms visible from the normal city camera. Use parcel growth for extra bays, taller halls, or more storage where each form supports it. Keep road-facing loading doors aligned with the same frontage used for freight access. Use the workshop entrance on mixed-use ground floors and retain residential massing above. Construction shows the shell as it rises. Operating, idle, and closed buildings use restrained lighting and door changes backed by their simulation status. Camera, lighting, and visibility never affect operations.

## Private investment and operation

A shared catalog supplies each site's name, recipe, credentials, nuisance, capacity, and visual type. Keep existing nuisance and utility gates. Workshops can open at the Neighborhood limit, food processors at Commercial, and fabrication and assembly at Industrial. Existing mixed-use workshop rules still apply. Give the player a forecast on empty industrial parcels showing plausible tenants and what is missing. Investors rank viable types by reachable compatible supply and demand, using seeded tie-breaking. The selected type persists for the life of the tenant and can change when a vacant site re-lets. The same type appears in inspection, company listings, and the map.

Production consumes delivered input according to integer recipe batches. Completed batches add output stock up to storage limits. Actual staffing and delivered utilities set the operating cap. A site with no room or missing inputs reduces output. Temporary disruptions show in the inspector. Existing sustained loss and closure rules handle longer failures. Active industrial pollution and noise follow operating throughput, with any fixed site load defined separately. Farms and fisheries post one authoritative yield each day. Raw sales remain available alongside processed food, and allocating catch to a processor draws on the same catch available to a shop or exporter.

Groceries and restaurants retain their existing food demand and purchasing constraints. Prepared products satisfy that demand in explicit food-equivalent units. Workshops sell general goods to operating local businesses. Assembly plants sell finished goods to local businesses and external buyers. Consumer demand is capped by purchasing power. Business demand is capped by staffed activity and available operating budget. Regional imports and exports have finite harbour handling and market demand. Imports provide a recovery path for small cities and resource disruptions at a landed cost. A city can start with imported materials or parts before it has a local supplier. New firms open with a bounded working-capital allowance sized for a short first delivery cycle. Treat it as private startup funding, record it at opening, and replenish purchasing power through actual receipts. Standing basic orders from local employers and the harbour provide an initial market. Migrate existing firms with the same one-time working-capital rule, accounting for any wallet already saved.

## Freight and settlement

Use a shared commodity and inventory model for producers, processors, retailers, depots, and gateway stock. Each item has a cargo-space factor. Stock is tracked in commodity units with its carrying value. A shipment identifies the owner, item, quantity, origin, destination, reserved route, and progress. Reserve compatible road, dock, and ferry capacity before loading. Shelf stock leaves the origin on loading and becomes usable at destination only after unloading. Port departures, handling, and storage impose real limits. Keep active routes and eligible lots indexed, and reuse freight graph searches by commodity and topology so updates scale with activity. Reserve capacity in deterministic order with stable tie-breaking and rotate equivalent claims across days.

Resolve freight once per simulation day. Receive previously dispatched cargo, record new raw yield, run eligible production against available input, sell from on-hand stock, and dispatch against the remaining shipment and storage capacity. A shipment whose destination fills waits for unloading. If a route closes, hold at a valid transfer point until a route returns or reroute it while preserving ownership and capacity. Perishables age while waiting and in transit. If a terminal disappears, reroute to compatible storage or book a loss. Road shipments use the existing road graph and freight truck animation. Ferry and canal routes use existing vessels, sailing conditions, and cargo eligibility. Private freight automatically uses cargo-capable links. Existing player-configured island services become published services on their current link. Their priority and suspension apply to that service’s departures, and their backup imports and reserve storage apply to their configured market. Automatic freight uses remaining departure capacity and honors link closures.

A sale posts supplier revenue and buyer inventory cost once. Carry delivery, handling, and duty in landed inventory value and charge that cost as inventory is consumed or sold. Monthly parcel accounts use realized sales and matched input costs for modeled commodities. Reserve the buyer’s quoted purchase amount when the order ships. Title stays with the seller in transit and passes for each unit unloaded. Settle that unit once, release the corresponding reservation, and release the unused amount if cargo spoils or is cancelled. The seller carries the transit loss. Import stock at the gateway follows the same acceptance rule at customs. The treasury receives actual taxes, duties, and public fees, and pays for public freight purchases. Keep municipal transfers and private trade distinct. Reserve shared space in compatible units for existing food, fuel, waste, and industrial freight so capacity cannot be booked twice.

The first playable increment proves farm and fishery to processor to shop over an existing street network, with plain raw sales and imports still available. The next adds materials, fabrication, workshops, and assembly with local and external buyers. The final increment migrates shared ferry and canal dispatch and surfaces capacity and shipment state in the existing freight UI. During migration, assign each producer, buyer, and freight edge to a single accounting and dispatch path at a time. At cutover, map old shop stock and active island voyages into the shared ledger, preserve quantities, carried values where available, and days remaining, and prevent duplicate dispatch or payment. Switch food coverage and growth in the same cutover as ordinary shops. Base coverage on food reaching household buyers through actual retail sales, with the existing founding harbour supplying a bounded starter retail market until private storefronts can take over. Use available stock and expected deliveries for the growth forecast. Remove the old credit for direct gross farm and fish yield at cutover, so a disconnected producer cannot feed a household on paper. Existing industrial sectors keep their accrued economic history and acquire their matching new type deterministically. Save the simulation day marker, shipment IDs, inventories, routes, and accounting totals so reload continues without replaying transactions.

## What the player sees

An inspection panel follows the same lot from shortage to recovery. Example labels below are illustrative. The displayed values come from dispatch and production state.

```text
Seafood processor · Idle
Catch                 0 on hand · 8 due tomorrow
Chilled seafood       4 on hand · 6 ordered by local shops
Supplier              West Quay Fishery
Route                 Ferry suspended due to rough seas
```

Select a supplier, buyer, or shipment to locate it on the map. Freight views identify waiting cargo, storage limits, and the saturated link. Construction previews, the parcel inspector, and company listings use the same names and status definitions.

## Acceptance

- At the normal camera distance, a player can distinguish workshops, both food processors, fabrication works, and assembly plants by shape. Loading bays face the accessible street, including on rotated parcels. Verify daytime, dusk, construction, idle, and closed states in the native game.
- A repeatable coastal scenario demonstrates crops and fish entering two processors, processed food reaching shops, and an imported-materials chain supplying workshops and assembly plants. A change in buyer demand leaves stock unsold and changes site earnings. A fall in fish stocks lowers catch and then constrains seafood output. A tariff or harbour bottleneck makes imports less competitive.
- Interrupt a road, a ferry, and a cargo-capable canal route. The same inventory remains at origin, in transit, or at destination at every step, allowing for recorded conversions and losses. Verify shared freight capacity and inspect the reason for each delay. Reopen each link and verify recovery and settlement.
- Reconcile opening stock, yield, conversions, imports, arrivals, dispatches, sales or final consumption, exports, losses, and closing stock per commodity. Verify matched buyer and seller entries and municipal receipts. Compare uninterrupted and save/reload runs, including an in-flight voyage, and exercise a pre-industry save and the existing founding path.
- Run the March suite and native render check. Compare daily step time on a small starter save and an established port region against the current build.
