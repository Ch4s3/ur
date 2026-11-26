# Procedural shield volcanoes

- [x] Generate one shield volcano on about one in eight seeded maps. Replace the main highland within a broad skirt that can build out the coastline. Shape an irregular summit rim around a sunken, flatter floor. Vary the rim and floor by seed and cut a shallow gully down one exterior flank.
- [x] Persist whether a region was generated with a volcano. Use its existing saved heights and world seed to restore the landform and vent. Old saves default to ordinary terrain.
- [x] Render the summit and upper flank with dark basalt and exposed rock. Start small effusive pulses at a flank vent outside the caldera. Choose each next lava cell from connected ground of equal or lower height, prefer the fall line, and stop at a basin, developed parcel, water, or the flow limit.
- [x] Verify seeded rarity, the closed rim and lower floor, the continuous shield profile, downhill flow, and save compatibility. Frame the entire volcano in the native preview.

The template follows the broad shield, summit collapse, and flank vents described in the [USGS geologic map of Kīlauea's summit](https://pubs.usgs.gov/imap/i2759/). The game compresses the landform to fit its island scale.

### Terrain profile

The seed sets the centre, rim radius, floor elevation, crest elevation, and
rift direction. The shield blends into the island over a radius of 12
parcels, about 96 metres in Ur. The caldera is about 50–60 metres across.
Its nearly level floor rises through a steep inner wall to a rim with
seeded irregularities. Outside the rim, the slope eases into the lower
flank and finally into the island. The volcano can build land outward where
its skirt reaches the coast.

An exterior gully biases the flow away from the basin, with the vent about
40 metres from the centre. Each flow step samples the rendered terrain
one metre away on the four-connected grid. It takes the lowest available
step, keeps its heading when grades tie, and stops when blocked or after an
extended level stretch. For this first simulation, a pulse has a maximum
reach of 52 metres and leaves a dark cooling crust. Smoke drifts with the
existing regional wind.

## Initial prototype

Build a small, recurring effusive eruption on mountainous islands. The summit has a dark, stepped crater with an open side. Lava fills the vent, creeps down the slope as a narrow glowing ribbon, and darkens into a crust. A few expanding ash puffs rise and drift with the regional wind.

## First playable pass

- [x] Select one high, undeveloped summit on roughly a quarter of generated maps. Use the world seed to decide which maps qualify and terrain height to place the vent above a visible drop of at least 1.5 metres. Keep it at that summit during play and suppress it if the parcel is developed or lowered. Add a close-up preview that selects a summit regardless of seed eligibility.
- [x] Trace up to twelve connected, four-voxel steps from the vent using the existing terrain surface. Give the downhill route preference and allow short level stretches. Stop at uphill terrain, developed parcels, water, or the map edge.
- [x] Render a basalt rim with a notch at the first step and clear intersecting wild vegetation. Advance the lava front over nine seconds, cool the flow from the tip back toward the crater, and let the smoke clear before the next pulse. Use the same pause behavior as the ocean animation.
- [x] Verify summit eligibility, flow bounds, downhill continuity, and eruption timing with a focused test.
- [x] Build the game and inspect a close-up screenshot.

A terrain-backed visual effect gives the first pass visible behavior using Ur's existing renderer and save formats. A full terrain and hazard simulation would make volcanic regions matter to city planning and needs its own balance pass.

## Later passes

1. Tune summit profiles and crater shapes across seeds. Add secondary vents or larger lava fields where the terrain supports them.
2. Add a map overlay or inspector entry for vent activity. Persist the vent's identity, eruption history, and deposits when those become gameplay state.
3. Prototype cooled lava as new basalt terrain and treat roads, vegetation, air quality, and sea entry as separate gameplay decisions.

## Lava spread and cooling

A pulse keeps a downhill spine. Each section samples the grade over nearby
steps and can occupy up to three connected cells on each side. Lateral lava
spreads only onto dry, open ground at or below its source cell. Low grades
allow a broader fan. Each cell belongs to one section, including at bends.
The generated flank gully curves so its fall line can turn.

The front reaches the spine first and then the outer lanes. Exposed lanes
form a dark crust early, sheltered lanes stay hot longer, and the fed core
cools last. Each patch sits on its sampled terrain height and connects to
the preceding patch across height changes. Vegetation clearing uses the
same footprint.

## Permanent basalt

When a pulse finishes cooling, each reached cell adds one 25 cm layer to
the one-metre terrain grid. The terrain mesher draws the exposed tops and
sides in black basalt, and later flows sample the raised terrain. The save
stores sparse deposits and the eruption phase. Deposits block natural
vegetation and keep their height across reloads and construction undo.

## Multiple vents and broad flows

A volcanic pulse feeds three staggered vents on separate flanks. Each vent
follows the rendered slope. The flows reserve their terrain cells so
crossings share one drawn surface and deposit at most one layer per pulse.

Steep terrain confines the flows. Gentler stretches allow wider pools and
rounded lobes, up to 21 metres across. A broad pool can overtop a 25 cm
lip, while the main channel always descends. The active surfaces keep
their dark crust and molten centres. The established eruption phase and
permanent basalt save format stay compatible with earlier saves.

## Lava lake, ash, and shoreline growth

Flood the low connected cells of the summit floor to form a lava lake.
Molten lava spreads out from its central upwelling during eruptions, with
crust around the shore. Warm local lights illuminate the basin and active
flows. Smoke rises from the lake and vents during pulses and drifts with
the regional wind. Its projected footprint shades terrain and reduces
output from solar plants beneath it.

Lava can run across low beach cells to open water. At settlement, eligible
water contacts create a small basalt shelf connected to the coast, using
the land height and deposit data already persisted in saves.

## Steam and weathered slopes

Use the first hot lava contact with seawater to time a brief burst of
expanding white steam. Give the steam its own translucent meshes and use
the regional wind to carry them away as they dissipate. Use the same contact
to determine where the basalt shelf forms.

Shade the cone by its grade and elevation, with varied bands of weathered
rock, scoria, ash, and scrub. Allow vegetation on sheltered patches and keep
black basalt on the actual deposits. Check contact timing, dispersal, and
the mix of terrain materials with the focused volcano tests and a native
preview.
