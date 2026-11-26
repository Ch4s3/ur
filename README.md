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
| 1 | Road ($60 per land parcel) |
| 2 / 3 | Housing / employment zoning |
| 4 | Power station; needs a connected road |
| 5 | Cycle the parcel height limit through one, two, and three storeys |
| 6 | Grade vacant land down by 2 m, to a minimum of 1 m |
| 7 | Clear a parcel (the harbour gateway is protected) |
| WASD or arrow keys | Pan relative to the camera |
| Q / E | Orbit the city |
| Scroll wheel or + / − | Zoom in / out |
| Space | Pause / resume |
| Tab | Cycle 1x / 2x / 3x speed |
| Left / right bracket | Lower / raise tax |
| Semicolon / apostrophe | Lower / raise energy price |
| F5 | Screenshot (`STRATA_SHOT`, default `strata_shot.ppm`) |
| Z | Undo the last construction gesture |
| Escape | Open or close the game menu |

Hover a parcel for a development explanation. Each simulation month takes one
second at 1x speed. Roads permit at most 3 m of elevation change between parcels.
The founding map is 480 x 352 m, with 8 m planning parcels and 0.25 m voxel geometry. Terrain contours are sampled on a 1 m grid with
quarter-metre elevation steps. Buildings use quarter-metre detail throughout.

## Planning streets and crossings

Choose a street type in **Roads → Streets**. **Straight** locks the route to
one map axis. Click the start and end, then press **Enter** to build and
start the next segment from the end. **Diagonal** uses the same controls for
any heading. **Curve** takes three pins: start, bend handle, and end.
Drag any pin to revise the curve. In **Freeform**, drag to sketch a route and
release to review it before building. The pavement, sidewalks, and vehicles
follow the off-grid route. The parcels it crosses still provide connections,
zoning frontage, and pricing. **Quick bend** builds on drag release.
In **Waypoints**, click to add pins and drag them to revise the route.
Hover a pin and press **R** to flip its incoming bend, or flip the live end
of the route. Hold **Alt** to preview the other bend. The guided tools snap
to existing streets and alignment guides. Hold **Shift** to bypass snapping,
or press **N** to toggle it.

The preview shows the proposed street footprint and flags blocked parcels.
Surface dead ends have rounded turning areas kept clear of curb parking.
Extending a dead end turns it into a through street or junction.

Use **Block** or **Grid** to drag a layout, then drag either corner to resize
it. Grid spacing is in parcels. The layout leaves frontage between the
outer road and the last interior street. Green markers identify new frontage.
**Replace** selects a corridor between junctions. Click farther along
a connected street to extend it. Orange markers identify attached infrastructure.

In **Roads → Crossings**, choose **Road bridge** for spans up to 256 m.
Pin two existing local streets or avenues on the same axis. Use **−** and
**+** to set the deck 2–16 m above the higher approach and inspect the
profile before building. Higher decks need longer ramps.

Choose **Suspension bridge** for spans up to 448 m and a deck rise of 12–32 m.
Ships need enough clearance below the deck and a route between the towers.
Choose **Drawbridge** for spans up to 80 m and a closed deck rise of 2–8 m.
Place the middle of the bridge over the channel. An approaching vessel
closes the road entrances. Once traffic clears, two leaves pivot up from
their hinges and open the channel at the middle. The road reopens when
the vessel has passed and the leaves meet again.

For shorter fixed crossings, choose an **Overpass**, **Underpass**, or
**Road tunnel**. Place two portals on the same axis, then drag either portal to move it.
Mountain tunnels meet the approach streets at grade. Tunnels under water
descend through recessed ramps. The profile shows where each road goes underground.
The Road crossings layer shows built routes through terrain or water.
Press **T** or choose **Layers → Crossings → Tunnel cutaway** to open the
terrain and water above built tunnels. Press **T** again to restore the surface.

Press **Enter** or click **Build** to confirm a draft. Right-click or press
**Backspace** to remove its last pin. **Escape** cancels the draft, and **Z**
undoes a confirmed project in one step.

```sh
UR_DEMO=29 UR_ROAD_DEMO=1 ./run.sh
```

Choose **1** for the harbour route, **2** for a grid, **3** for a mountain
tunnel, or **4** for a channel tunnel. Add `UR_ROAD_BUILT=1` to start with
the selected project built.

### Canals

Open **Roads → Canals** and drag **Dig canal** through clear, unzoned land.
Connected parcels form a channel with sidewalks. Place a **Navigation lock**
on a straight reach where canal levels change. To start a **Water taxi**
route, select two connected canal banks. **Freight quay** routes also need an
adjacent street at both ends.

Storm surge can enter through a sea-level opening and spill onto nearby
low ground. Use **Flood barrier** at the opening to install a gate, then
click it again with the same tool to close or reopen it. Closing the gate
blocks both incoming surge and vessels using that reach.

## Founding a city

The default game starts with empty land and a landing survey. Click a cyan
shoreline plot to establish a harbour. The harbour supplies 64 water and
24 power to its connected networks and unlocks food imports. Extend roads,
pipes and power lines inland, then zone housing and jobs. The first regional
milestone is recovering the cost of a food expansion.

The western island offers a broad city plain and inland groundwater.
The volcanic island offers geothermal power, the farming island offers
freshwater and higher crop yields, and the eastern shoals offer better
fishing. Ferries connect local roads to harbour services. Water and power
still require their own connections. Oil is shown as a prospect.

### Earning back the first expansion

Connect the farming island or the fishing shoals with a ferry from your road
network. Place a **Fishing Dock** on road-connected shoreline using **Utilities → Food**.
The city maintains the pier, and a privately owned boat hires up to four
residents and casts its net offshore.
The crew, fish population, weather, and pollution determine the catch.
You can also connect farms to a piped well on the farming island. Shops and
local households get first claim on ferry capacity. Surplus cargo actually delivered to the founding harbour earns $3 per
unit, subject to available trade capacity. Imports use the same harbour trade allowance. Local food deliveries
share the ferry with export loads.

A ferry carries up to 32, 96, or 160 units per month at its three service levels. Use **Service
frequency** on either terminal to trade higher upkeep for more cargo capacity.
The development panel shows the first food island's construction spend,
cumulative net export receipts and last month's exports. Its ledger covers ferry
construction and upkeep, island roads, pipes, food facilities and their water
works. Try a working route in `UR_DEMO=4 ./run.sh`.

## Food, power, water, and waste

Use **Lay pipe** to drag a line from an existing pipe. The starter street has
pipes under it. Pipes can cross water and can share a parcel with a road or
building. **Remove pipe** leaves surface construction in place. Hover over a
parcel to inspect its pipe or local resource. Water facilities and farms need
both road and pipe access. Homes need pipe access before they can grow.

- **Freshwater wells** pump 192 water per month from mapped aquifers on the
  western island. **Rain collectors** produce 96 in wet months and 48 otherwise.
- **Water import terminals** buy up to 160 units each at $1 per unit. **Coastal
  desalination** produces 192 per plant, needs 12 spare power and has a running cost.
- **Recycling plants** treat up to 160 wastewater each, use 8 power and return
  three quarters of the treated volume. **Ocean outfalls** discharge up to 192
  untreated wastewater each. Unhandled waste incurs a monthly cost.
- Discharge builds up local coastal pollution. Nearby fisheries lose catch and
  revenue as pollution rises. Removing or disconnecting an outfall lets its
  plume decay over subsequent months.
- Farms use 24 water. The game selects sweet potato, taro, or breadfruit based
  on seed temperature, elevation, soil fertility, and regional rainfall.
  Soil fertility and moisture affect harvests. Open **Map Layers → Resources
  → Soil fertility** to survey a parcel, or select a farm to see its crop.
- Use **Utilities → Food** to paint open fishing, limited fishing, or protected
  waters. Limited waters allow half the usual fishing effort. Fishing boats can
  pass through protected waters, where catch is zero. **Map Layers → Resources**
  shows both the fish population and the fishing policy.
- The harbour imports any remaining food it can afford, up to 160 per month
  plus 192 per connected trade depot.
- Standard power stations supply 100 power. Geothermal stations supply 180 on
  the eastern volcanic field. The eastern island lacks mapped freshwater.

Power, water, and sewage have limits on individual segments. New homes must
reserve utility capacity and have access to food before construction starts.
Water and sewage use the same pipe assets and have separate flow limits.
Homes and businesses can ride out brief interruptions. The city checks for
severe shortfalls every five days. A check with adequate service halves the
running count, so supply that keeps failing still builds toward the limit.
Energy income and fuel are averaged over the month's checks, so the bill
reflects the whole month's weather. After 30 days of disruption, the next
monthly settlement closes affected businesses and sends affected households
looking for an affordable home with enough utility capacity. Families who
cannot find one have three months to search before leaving the region.

## Electricity and trash

Use **Lay power line** to extend the starter grid. Generators need grid access
and a service road. New development needs both road and grid access.

- Wind and solar output vary by month. Gas and nuclear need a monthly fuel
  budget. Geothermal uses the eastern volcanic field. Biogas consumes collected
  trash and supplies one unit of electricity per unit digested.
- In **Utilities / Waste**, place small trash cans or underground bins along
  streets. Underground bins hold more and load faster, but occupy one curb
  parking space. Overflow raises local pollution.
- A trash depot sends trucks to blocks with backlogs. Trucks need a connected
  road route and room at a disposal site. Landfills have finite storage, export
  docks charge for shipped waste, and ocean dumps stay disabled until enabled
  in their parcel popover. Ocean dumping damages nearby fisheries.
- Incinerators unlock at 500 residents with a trade school. They need a grid
  connection and produce air pollution and ash. Trucks take ash to landfill or
  export it.

The **Trash collection** layer colors parcels by backlog. Parcel popovers show
the last pickup or a facility's capacity. Run `UR_DEMO=16 ./run.sh` to see a
depot, landfill, and both bin sizes. Existing saves start using truck collection
when you add a bin or a new disposal facility.

## Density and nuisance policy

Zones can grow up to three storeys by default. The market starts at one storey
and supports taller construction as regional population and employment rise.
Road distance from the harbour limits attainable height. Development still
requires demand for its use and access to the applicable utilities. Use **Cycle
height limit** to preserve low-rise parcels.

Paint a maximum nuisance level with the four nuisance tools. Quiet parcels
permit housing. Neighbourhood parcels also allow mixed-use buildings and low
impact facilities. Commercial parcels admit employment zones and depots.
Neighborhood parcels permit industrial zoning for workshops; commercial
limits also allow processors. Industrial limits admit manufacturers, gas plants,
nuclear stations, landfills, and outfalls. The limits are cumulative. Lowering a limit leaves existing uses in
place and prevents incompatible new construction or expansion. Mixed-use
buildings add both households and jobs.

New mixed-use zoning starts at the Commercial limit, with a shop on the ground
floor. Raise a mixed-use parcel to the Industrial limit to allow a light
industrial workshop there instead: it takes over the ground floor on the next
construction, or when the ground-floor business is empty or closed. A workshop
employs more people than a shop and needs more power and water, but its noise
and pollution fall on the flats above and next door. Lowering the limit stops
a workshop building from growing until the limit is raised again.

Use **Zoning → Land use → Industrial zone** to reserve land for private
industry. Workshops, produce packers, seafood processors, fabrication works,
and assembly plants have their own building forms and loading bays. Nearby
farms and fisheries attract food processors. Heavy industry also needs trained
workers and the Industrial nuisance limit.

An operating factory needs workers, utilities, materials, and room for output.
Farms and fisheries supply raw food to processors and shops. Fabrication works
turn bulk materials into parts for workshops and assembly plants. Local
businesses buy manufactured goods, and the harbour imports inputs and provides
an export market. Warehouses buffer cargo closer to customers.

Inspect an industrial site to see input and output stock, why production
stopped, and the status of incoming cargo. Shipments use roads, ferries, and
cargo-capable canals. A delay can leave cargo in transit while a factory uses
up its stock. Industrial shipments share cargo capacity with food, fuel, and
waste on the configured freight service.

Run `UR_DEMO=9 UR_INDUSTRIAL_DEMO=1 ./run.sh` for the coastal production
district. Inspect the plants on the mainland road and the crossing at 18, 16.

## Civic services

The **Civic** toolbar button offers schools, clinics, fire stations and police stations.
Place them beside a street. Each charges monthly upkeep and serves a limited
distance along roads, so gaps, steep grades and ferry crossings can leave
nearby parcels uncovered.

Single-storey homes can start anywhere the market and utilities allow. A
school or clinic supports a second floor in housing and mixed-use buildings.
A third floor needs all four services. Covered residential parcels can also
start construction sooner. Demand, commutes, utility capacity and height
limits still apply.

Select **Layers → Civic services** to see coverage. Hover over a housing or
mixed-use parcel to see which of the four services reach it. Try a serviced
district with `UR_DEMO=5 ./run.sh`.

The **Civic → Community** menu offers a community center and a library.
Staffed centers improve nearby civic-service access. A staffed, road-connected
library improves local access and makes further education more attractive;
course capacity, job opportunities, and tuition still influence enrollment.
Use **Civic → Expansions** to add classrooms, clinic or hospital beds, and
additional fire or police vehicle bays. These additions cost money to build
and operate. The vehicle bays need an additional worker and allow a second
crew to respond while the first is busy. **Civic → Disaster** includes a
staffed emergency shelter for displaced households.

A civic visual review scene is available with
`UR_DEMO=9 UR_COMMUNITY_DEMO=1 ./run.sh`.

## Public religion

Open **Details → Services → Religion** to compare five patrons and their
council supporters. Choose a patron, then use **Civic → Worship** to place
the first shrine and dedicate the city. Build a Shrine, Temple, and Large
Temple in order to unlock the Grand Temple. Shrines need one high-school
graduate, Temples need one college-educated priest, and Large Temples need
two. The city's single Grand Temple needs four seminary-trained clergy.
Add a **Seminary** beside a university through **Civic → Faculties**.
Inspect a worship site to see its staffing and whether it can operate.
Use **Layers → Neighborhoods → Religion** to see which homes have worship
coverage and which sites are open, understaffed, or closed for other reasons.

The Religion panel previews seasonal festivals and their food and trash
demands. Choose local observance, public holidays, or suspension. Festivals
use nearby stores' supplies and the sanitation network. Inspect an operating
Large or Grand Temple for offering fees and the chances of favor, silence,
and a curse. Each shrine closed for staffing adds 3 percentage points to
curse odds across the city, up to 15. The chance of silence falls by the same
amount. The cooldown and annual budget are shared across all temples.

Councillors favor particular gods. A new majority can request rededication
after an election. The Council panel shows the signatories, fee, closure,
and wrath risk. Declining costs goodwill with those councillors for the
rest of their tenure.

Try `UR_DEMO=27 ./run.sh` to inspect a city dedicated to Namar. Unpause to
reach the approaching election, or select a temple to inspect offerings.

## Streets

Choose **Local street**, **Avenue**, or **Pedestrian street** in **Roads**.
Paint over an existing street to change its type at the retrofit price.
Avenues cost more to maintain and have twice the traffic capacity of local
streets. Households drive to the nearest workplace, while goods and shop
trips run between each business and the harbour. Faster driving attracts some
extra trips from nearby development, so a new avenue can fill up. Traffic at
the freight quays slows cargo handling. Pedestrian streets keep walking access and
building frontage. Remove any bus route or toll before converting a street
to pedestrian use.

Two connected perpendicular segments round into a curve. Intersections and
tram track crossings use square geometry. Try the street showcase with
`UR_DEMO=6 ./run.sh`.

In **Roads → Crossings**, drag a straight span between two existing local
streets or avenues. Overpasses clear surface traffic; underpasses use shallow
cuts and run below streets in their path. Road tunnels can run under hills or
water. The portals are the only connections to the street network. Use the
**Road crossings** map layer to trace buried roads and **Remove crossing** to
remove a whole span without touching the surface street.

In **Civic → Parks → Paint park**, hold and drag over empty parcels to paint the shape.
Parks cost $45 per parcel and $1 per parcel each month. Connected parcels form
a single park with generated paths, trees, benches and, in larger parks,
occasional fountains. Larger parks encourage denser growth nearby where
commutes and services can support it. Clear an individual parcel to reshape a
park. **Upgrade park** improves the entire connected park. Garden upgrades
cost $65 per parcel and landmarks cost $110 per parcel. Each level adds $1
monthly upkeep per upgraded parcel.

**Civic → Street planting** offers shade, blossom, and columnar trees, plus
flower and hedge planters. Click or drag along streets to plant. Each street
parcel holds one planting. See the local score in Parcel details or
**Layers → Livability**. Switch between park walkability, commute, services,
safety, job access, and environment. Park access follows sidewalks,
pedestrian streets and walking paths, and citizens take leisure walks to
reachable parks. The Livability tab charts resident averages for the last 24
recorded months.

**Show details → Safety** charts incidents, responses, and average response
times. With the tab open, click a parcel to see its neighborhood
history and safety score. Theft and vandalism reports count against safety
for six months. A delayed or missed response increases the impact.
The **Reported incidents** layer marks the latest month's cases.
Fire stations and clinics dispatch trucks and ambulances across roads and
wide pedestrian streets. Traffic slows all responders. Voxel flames shed
embers and smoke, and the pollution layer shows the plume as wind carries
it across the city. Rain shortens fires and reduces their smoke and spread.
Earthquakes can ignite fires, especially at gas plants and nearby buildings.
Fires that burn for 12 minutes can reach adjoining buildings, with further spread possible if
crews take longer. Buildings close for one or two months of repair. After
30 minutes of local fire exposure a building burns down and requires four
months of reconstruction. Work proceeds when the site is dry and connected
to the harbor by road. Households keep their homes reserved and walk to
available shelters while they wait. The parcel inspector shows how repairs
are progressing and where residents are sheltered. **Layers → Emergencies →
Fire recovery** maps closures. Try `UR_DEMO=10 ./run.sh` and unpause to watch
the evacuation.
The **Fires** and **Medical calls** layers also filter the Safety chart.
Ambulances pick patients up and deliver them to the clinic or hospital that
can start treatment soonest. Clinics have one treatment bed and hospitals
have four; a clinic wing adds one, and a hospital ward adds two when fully staffed. Pickup, traffic, and bed waits can cause complications. Medical
charts show admissions, time to treatment, and stabilized patients.
Try the dispatch showcase with `UR_DEMO=9 ./run.sh` or the planted district
with `UR_DEMO=8 ./run.sh`.

## Transport

Open **Transit** on the bottom construction toolbar to find bus, tram, subway,
ferry and service management tools. Use **Roads** for streets, walking paths
and tolls, **Zoning** for land use and nuisance limits, and **Utilities** for
power, water, food and waste. The tool cards show construction costs and civic
upkeep. Click the active category again to collapse its tray.

- Drag **Draw bus route** along connected roads, then place **Bus stop** on
  at least two route parcels.
- Drag **Lay tram tracks** or **Dig subway tunnel** to build a line. Add
  **Tram stop** or **Subway station** on at least two land parcels along it.
  Rail service requires two stops or stations with grid access and live
  generation. Tunnels can cross water. Select **Layers → Transit & jobs**
  to see running service in cyan and unfinished lines in amber.
- Paint **walking paths** between roads, stops, and terminals. Walking paths
  need land or a bridge and follow the same slope limit as roads.
- Select **Ferry route** and click two unused shoreline parcels across water.
  Connect each terminal to its town with a road or walking path. Use **Remove
  transport** on either terminal to remove the route.

Hover over a parcel to see travel time to the nearest existing jobs. Short
trips can support taller buildings as regional demand grows. Passenger routes
help development reach jobs. Freight, power and water use their own networks.
Trips include local road congestion and transit waiting and crowding. Use
**Cycle service frequency** on a stop or ferry terminal to set one,
two, or three departures per interval. Higher frequency adds capacity and
operating cost. Buses share road congestion. Bus, tram, and ferry models move
along representative segments. The simulation estimates load from nearby
development and does not assign individual passengers to vehicles.

Run `UR_DEMO=2 ./run.sh` for the transport showcase. Add
`UR_CHANNEL_VIEW=1` for the ferry crossing or `UR_REGION_VIEW=1` for both islands.

## Volcanoes

About one in eight seeds generates a shield volcano. Its broad slopes rise
to a sunken summit caldera with exposed rock, ash and rusty scoria. Scrub
and trees grow on gentler slopes between old lava deposits. During an eruption,
the lava pool spreads across the caldera floor and staggered vents open on
three flanks. The pool and hot flows light nearby terrain. Lava follows
gullies downhill and spreads into broad lobes where the grade eases. The
edges form a dark crust around the molten core. Smoke drifts with the wind,
casting moving shadows that temporarily reduce solar output below.
Lava burns trees and damages structures when it reaches them.

Each completed eruption adds a permanent 25 cm layer of black basalt
where the flow reached. Lava hitting the sea sends up a cloud of white
steam that drifts downwind and can leave a permanent basalt shelf. Later
eruptions follow the raised surface.

Run `UR_VOLCANO_VIEW=1 ./run.sh` to see an active eruption,
`UR_VOLCANO_VIEW=2 ./run.sh` to see the deposits after three eruptions, or
`UR_VOLCANO_VIEW=3 ./run.sh` for a close-up of steam at the coast.

## Map layers

Open **Layers** and select a map view. Click the active view again or choose
**Off** under **Networks** to clear it. The selected view stays visible as you
return to construction. Each view shows a colour legend in the footer.

Water and electricity highlight connected and isolated segments. Transit
shows corridors and access to jobs. Pollution shows land and coastal
contamination. Groundwater and geothermal show where those resources occur.
Oil potential is a prospecting view for the starter map. Oil extraction is
not simulated. These views mark parcels above the map surface.

## Verification and measurement

Run `./scripts/verify.sh` for all code checks, or
`UR_VERIFY_RENDER=1 ./scripts/verify.sh` to include the native rendering test.

```sh
source ../strata/scripts/env.sh
forge check
for suite in test/*_test.march; do forge test --release "$suite"; done
forge lint --strict
forge build --release
UR_BENCH=1000 .march/build/release/ur
MARCH_PIN_MAIN=1 UR_DEMO=1 UR_FRAMES=90 STRATA_SHOT=/tmp/ur.ppm .march/build/release/ur
```

`UR_DEMO=1` constructs a connected two-island expansion through ordinary player
actions, then advances it for 600 months. `UR_FRAMES` bounds a visual smoke test
and requests a screenshot on its final frame. Set `UR_REGION_VIEW=1` to start
with a wider view of both islands. `UR_INPUT_LOG=1` prints sampled
pointer state for diagnosing native input.

## Architecture and current limits

- `Ur.Sim`: deterministic parcel aggregates, road flood fill, power, construction
  budget, demand and policy-dependent private growth.
- `Ur.Scene`, `Ur.Landscape`, and `Ur.Architecture`: detailed building meshes,
  terrain contours, vegetation, and Strata voxel shadows. Updates remesh edited
  parcels and neighbours affected by their edges.
- `Ur.Hud`, `Ur.Input`, `Ur`: interface, gesture ownership and bounded simulation
  clock. Idle frames reuse cached population, jobs, power and road access.
- `Ur.Scenario`: reproducible expansion for integration tests and screenshots.
- Strata gains absolute cursor-coordinate bindings in window points. The changes
  are applied in the adjacent checkout and recorded in
  `docs/engine/strata-cursor.patch` for reproducibility.

## People and investment

The monthly resident survey sets how the city is regarded. A well-liked city
draws more newcomers than ordinary demand; a disliked one draws fewer and
loses residents. Some arriving workers come to fill open posts that need a
secondary or trade qualification, and more of them come to a better-liked
city. University degrees and specialisms are only earned in the city.

Ready parcels wait for investors, who look at each parcel every few turns.
Income tax, business tax above 10%, energy prices, and a long commute each
add turns; civic services take one off homes. Hover a ready parcel to see its
wait. A larger city has more investors, so more projects start per turn; the
extra ones avoid housing while a tenth of workers are without a job.

During a campaign the Council panel shows each incumbent's odds, which follow
how residents of that ward feel, whom you endorse, and how the share index did
over the term.

## Land, wealth and the treasury

**Land value.** Every parcel has a value set by its livability, road access,
the coast and its neighbours' wealth. Values drift a quarter of the way to
their target each month. Property tax is a rate on land value for each storey
of an occupied building; set it under **Details → Policy**. Landlords pass it
on in rent, so raising it costs tenants. A vacant building's owner still owes
the tax its land would carry. The **Land value** layer is under Neighborhoods.

**Household savings.** Each household saves what is left of its income after
rent, tax and costs, and carries its savings when it moves. Savings above
three months of costs go partly into the share index. A household whose
savings cover a bad month does not count it toward leaving. Wealthy
neighbourhoods spend more in shops and raise land values, and savings soften
how wards feel about hard times. The **Household savings** layer and the
Population and Council panels show it.

**Funding.** **Details → Finance → Funding** sets education, health, safety,
utilities, transit, and parks and community between 50% and 150%. Costs follow
the level. Below 100% posts go unfilled and output falls; above 100% schools
add seats.

**Borrowing.** **Details → Finance → Debt** takes loans of $5,000 or $20,000
over three years, issues bonds over ten years, and repays a loan early. Bonds
sell to residents first, from savings above a cushion, and pay them interest;
outside buyers take the rest at a higher rate. The credit rating, from AAA to
D, follows debt against revenue, debt service, deficits and missed payments,
and sets new rates. Below BB the bond market closes. If a month would end with
negative cash, the bank covers it with an emergency overdraft. A month whose
debt service cannot be paid counts as one missed payment and the shortfall
becomes arrears. There is no new borrowing while in arrears. Three missed
months in a year bring an administrator, who caps every service at 70%,
freezes paid construction except demolition and angers voters; clearing the
arrears and paying three months ends it. If arrears are still higher after a
year under administration, the city is insolvent and the game ends.

**Stock market.** A business with twelve profitable months and at least
twelve jobs lists on the market; the **listing incentive** halves that for
$200 a month. Prices move toward earnings times a valuation multiple with
seeded shocks that come in calm and turbulent spells. The multiple rises with
market sentiment and falls with interest rates. Sentiment follows a regional
business cycle, growth in city spending, momentum, and falls with city debt.
Listed firms pay dividends to households, and a firm that closes or is
demolished delists near zero. A **tax break** for listed firms raises their
value at the cost of business tax. A rising index draws better firms and
speeds commercial investment; a falling one slows it. **Details → Finance →
Stocks** charts the index and any company's price.

This is the first gameplay slice, with procedural voxel architecture and landscaping. It does not
simulate the eventual tens of thousands of individual residents. Households and
employment are aggregates; differentiated
industries, trade chains, ferries and full-region streaming
are future work. Power currently follows the harbour
road network. Terrain grading is a parcel operation, not a voxel brush.

Start a new city or load your saved city from the title menu. During play,
open **Game menu** or press Escape to save, load, or start over. Ur keeps one
save slot at `~/.ur-save.json`. Set `UR_SAVE_PATH` to use a different file.

Construction previews show a cost and outline before release. Drag roads and
utilities along a route, or drag out a zoning rectangle. A blocked parcel
rejects the whole gesture. Undo restores the city to the moment before the
gesture, including the treasury and simulation month.

Placing a public building pays for and reserves its site. The preview shows
the work days required. Resident crews take the oldest reachable projects
first, and each crew advances one project per game day. Buildings open and
unlock their milestones when construction finishes. Inspect any site to see
its progress or why it is waiting. Bulldozing a site cancels the order.

See the [design](docs/superpowers/specs/2026-11-13-first-playable.md),
[implementation plan](docs/superpowers/plans/2026-11-13-first-playable.md), and
[progress and measurements](docs/progress.md).

The [building and decoration style guide](docs/building-style.md) covers
materials, model scale, frontages, and in-game review.


Busy transit stops can attract shops and bars to paved frontage nearby.
**Show details → Policy** sets citywide ground-floor and quiet-hour rules.
Under **Zoning**, use **Ground floors** or **Quiet hours** to paint overrides;
use the inherit tools to return to the citywide rule. Required storefronts
can sit vacant if commercial demand is weak. Compare foot traffic and noise
under **Layers → Neighborhoods**.

**Roads → Car-free days** schedules closures on weekends, weekdays, Saturday
or Sunday. Buses, pedestrians and emergency vehicles keep access. The street
calendar advances at one day per five seconds of running simulation, alongside
the monthly economy. Try the transit corridor with `UR_DEMO=11 ./run.sh`.

### Transit and employment corridor

Launch with `UR_DEMO=18 ./run.sh`. The demo starts paused. Select the bus
stop at parcel **10, 18** with no construction tool selected. Its popup shows
the operating frequency, headway, riders left waiting, fares, and service
cost. Cycle to three departures with the popup button, then unpause. The
west housing parcel being tested is **10, 19**, and the east workplace is
**25, 19**. The fare button changes the citywide price. An expensive fare
can price workers out of a route even when seats are available.

For a reproducible comparison, build with `forge build --release` and run
`UR_CORRIDOR_REPLAY=4 .march/build/release/ur`. Both cities begin with the
same road network, zoning, utilities, and households. The replay changes
only the service setting. Each month it prints the commute, jobs filled,
visible residents assigned to those jobs, operating accounts, and the
target parcel's construction state.

### Utility capacity demo

Launch with `UR_DEMO=19 ./run.sh`. The game starts paused on the Electricity
layer. The red feeder at **9, 18** is full. Inspect the empty residential
parcel at **16, 17** to see why construction is waiting. Choose **Utilities →
Upgrades → Upgrade power feeder** and select the red feeder. The in-place
upgrade costs $120 and adds $4 per month in upkeep. The same power plants
then have a path to serve the new building.

**Layers → Networks** shows Electricity, Water supply, and Sewage collection
separately. Point at a segment to see its load and limit or at a building to
see how much service it receives. **Utilities → Upgrades → Upgrade water and
sewer main** increases both pipe limits. A connected pump, desalination
plant, or recycler also needs local power to run.

For the deterministic comparison, run
`UR_UTILITY_REPLAY=4 .march/build/release/ur` after a release build. Set
`UR_UTILITY_UPGRADED=1` with demo 19 to open the upgraded district in month four.


### Island freight demo

Launch `UR_DEMO=20 ./run.sh` and inspect **18, 16**. This starts paused at
the upgraded feeder district with a stocked market and a sailing underway.
Suspend sailings, unpause, and watch the shelves and the island gas plant
run down their separate inventories. Enable backup imports to keep food
coming through the mainland port at a higher private cost. The housing parcel
at **16, 17** shows when food shortages block construction.

To open a freight service in another city, inspect a ferry dock connected by
road to the founding harbour. The other bank needs a road to a fishery or
farm, and the mainland needs a grocery or restaurant. A gas plant or waste
export dock on the island adds fuel or waste bookings. The dock lets you
choose which cargo gets space first and buy extra market storage. The freight
service currently manages one ferry link and one receiving market per city.

After a release build, run `UR_FREIGHT_REPLAY=8 .march/build/release/ur` for
an identical disruption with backup imports off and on, followed by a recovery.

### Council district conditions demo

Launch `UR_DEMO=21 ./run.sh` to open **Details → Council** on the ward map.
Use **Next ward** to compare the affected district with its neighbor and
**Show affected homes** to find the site behind the current agenda item.
Councillors review occupied homes for service shortfalls, food prices and
availability, job access, pollution, noise, budgets, and walkable amenities.
Displaced households stay in their home ward's report. A councillor can
request recovery and verify that homes are safe again over two monthly reviews.
They can issue a request or place a targeted hold. The panel shows the filing
baseline, the latest monthly reading, and the target. Two consecutive reviews
at the target close the item. Unresolved items expire after eight months.

Run `UR_COUNCIL_REPLAY=1 .march/build/release/ur` after a release build to compare
both wards before and after a localized plume, then see the hold clear after
two monthly reviews with clean air.

### Weather and local heat

The weather readout shows air temperature and soil moisture. Inspect a parcel
to see its local temperature. Street trees and parks cool nearby parcels,
reduce air conditioning demand, and make walking easier during hot spells.

Rain collectors store water and supply the pipe network until their tanks run
dry. Rain restores soil moisture, reduces solar output, and slows traffic.
Heavy rain can carry land pollution downstream to the sea. Severe rain closes
low coastal roads and can flood low subway stations. Their pumps run after
severe rain, need eight units of spare local electrical capacity, and cost
$2 per day of pumping. Those charges appear under power operations.

Launch `UR_DEMO=22 ./run.sh` for a storm in progress. Inspect the subway station
at **9, 16** and the rain collector at **8, 18**.

Open **Layers → Environment → Heat** to compare local air temperatures.
Point at land for the parcel reading. Click the weather badge or open
**Details → Overview → Weather** for seven days of forecasts and recent
weather history.

**Layers → Environment → Floodplain** shows estimated depth in severe rain on
dry days and active flooding during severe rain. Stormwater pools in low
ground. Parks and open land absorb runoff, especially when their soil is dry.
Low coastal areas can also flood from nearby open water.

Use **Roads → Flood protection** to upgrade drainage on existing streets
($180 per parcel, $5/month) or draw seawalls on water ($4,200 per parcel,
$26/month). Seawalls block coastal approaches, so exposed approaches and gaps
can still admit seawater. The weather panel shows the seeded map's rainfall
and temperature tendencies. The seed is preserved in the save.

Floodwater follows the terrain and lingers after storms. Coastal outflow,
evaporation, and absorption lower it over time. Deep floodwater closes roads
and walking paths, takes submerged generators offline, and damages buildings.
Repairs start after the parcel dries.

**Roads → Flood protection → Toggle emergency pumping** marks any land parcel
for pumping once severe rain eases. Removing 25 cm of water costs $2 and one
unit of spare local electricity. Unpowered pumps wait without charging.

For a flood and recovery comparison, launch
`UR_DEMO=22 UR_LAYER=33 ./run.sh`. Add `UR_FLOOD_DAYS=6` to open several days
later with the same terrain and storm.

`UR_DEMO=22 UR_LAYER=33 UR_FLOOD_BACKUP=1 ./run.sh` opens the flood recovery
drill, paused at 3× before the storm. The drill connects hilltop solar after
the first recovery day, so you can watch the subway pumps restart.

Add `UR_EVAC_DEMO=1` to the flood recovery drill to watch residents from low
houses walk to the uphill elementary school and return once repairs finish.
In any city, dry elementary schools, secondary schools, and the harbor can
house evacuees. Open the parcel inspector for shelter capacity. Households wait
when all reachable shelters are full or the approach is flooded.
