# Local rain

Rain in Ur falls on the whole island at once today: one weather value a day
(`S.current_weather`) floods, slows and fills every parcel alike, and the
clouds drawn overhead are decoration. This design makes rain fall where its
clouds are. Storms cross the island along paths, heavier in some districts
than others; flooding, road closures, rain collectors and evacuations follow
the rain that actually fell on each parcel; and the clouds, rain streaks and
wet streets the player sees are drawn from the same storms.

## Why

The player should be able to read the sky. A dark storm crossing the north
of the island should be the storm that floods the north, and a district that
stayed dry should stay dry. Flood protection becomes a question of *where*
storms tend to cross, not only how much rain the island gets.

## Goals

- Rain varies across the island within a day, and storms visibly move.
- The simulation and the picture agree: every parcel's flooding, runoff,
  collector intake and road slowdown follow the rain drawn over it.
- Deterministic: the same city, seed and date give the same storms, on
  replay and after loading a save.
- Rain reaches the simulation three times a game day, so floods rise while
  a storm is still crossing rather than all at midnight.

## Non-goals

- Hourly or continuous water simulation.
- Changing what kind of weather a day has. The regional weather (clear,
  cloudy, rain, heavy, severe; 3-day spells from the climate seed; curses)
  stays exactly as it is, and the 7-day forecast reads it as before.
- Local temperature, wind or cloud cover in the simulation (solar output and
  heat stay regional).
- Wind-driven changes to the cloud field outside rain (separate follow-up).

## Anti-goals

- A district floods while the picture over it showed no storm (or the
  reverse).
- Weather updates hitch the frame. The 08:00 and 16:00 updates must stay
  cheap; heavy work stays in the midnight roll that already runs off the
  main thread.
- The existing flood scenarios, flood drill and tests change behaviour.

## Approaches considered

- **Rain only in the picture.** Clouds rain locally, the simulation stays
  island-wide. Cheap, but the picture and the simulation disagree, which is
  the anti-goal above.
- **Storm cells in the simulation, applied once a day.** Agreement without
  touching the day's structure, but floods appear only at midnight, hours
  after the storm passed.
- **Storm cells applied three times a day (chosen).** The day is split into
  three watches of eight game hours: night (00–08), day (08–16), evening
  (16–24). At the end of each, the rain that fell on each parcel during it
  reaches the water simulation. Floods follow a storm across the day without
  restructuring the rest of the daily simulation. Chosen by the user.

## How rain falls

Each day's storms are a pure function of the city's climate seed, the date,
that day's regional weather kind (`S.weather_on`, so curses count) and the
regional wind. Nothing about them is saved; they are recomputed whenever
needed.

A day's rain is a **baseline** level that falls everywhere plus a few
**cells**, each a disc that crosses the map in a straight line with the wind:
a start position upwind of the map, a velocity (metres per game hour), a
radius and a level. Rain levels use the existing scale: 0 none, 2 rain,
3 heavy, 4 severe (1 is unused, as today). A parcel's level at an hour is the
larger of the baseline and every cell covering its centre.

Patchiness by regional weather kind (as proposed and approved):

| Regional kind | Baseline | Cells |
|---|---|---|
| clear, cloudy | 0 | none |
| rain (2) | 2, light everywhere | 1–2 bands at level 3, radius 120–180 m |
| heavy (3) | 2 | one broad band at level 3, radius about 200 m, crossing the island |
| severe (4) | 3, heavy everywhere | 2–3 storm cells at level 4, radius 60–90 m |

Cells are timed so each crosses the island within the day: a cell starts
upwind of the map edge at a seeded hour and moves at a speed derived from the
regional wind, scaled so a crossing takes roughly 6–12 game hours. Their
cross-wind offset is seeded so storms cross different districts on different
days.

**Uniform rain.** A city flag, `rain_uniform`, runs today's code unchanged:
the single daily `weather_day`, `severe_rain(c)` everywhere, no watches and
no cells. The flood scenarios (`storm_site`, `flood_backup_*`,
`evacuation_site`) and the flood drill set it, so their behaviour and tests
cannot drift. New cities leave it off. It is saved.

**Idra's curse stays island-wide.** While Unending Rain lasts, rain is
uniform: every parcel takes the curse's severe rain, as today (decided by
the user). The other curses are unaffected.

**Older saves may break.** Saves from before this change need not load
(decided by the user); the new fields are required, not defaulted.

## The three watches

The city records which watch it is in (`watch`: 0 night, 1 day, 2 evening),
saved. A watch ends at 08:00, 16:00 and midnight.

**Rain now (my call).** Separately from watches, the city keeps each
parcel's rain level at the current game hour (`rain_now`), recomputed
whenever the hour changes: one cheap pass over the map's parcels and the
day's few cells. Everything that reacts to rain while it falls reads this,
so streets slow and flood as a storm crosses them on screen. It is not
saved; it is recomputed from the date and the stamped clock on load.

At the end of each watch the city computes, for every parcel, its **watch
rain**: the peak level and the amount (sum of hourly levels, eight samples)
that fell on it during the watch. These are kept in two city arrays, used by
everything below, and recomputed rather than saved (they are a pure function
of date, watch and seed).

What happens at the end of a watch:

- **Every watch (cheap):** soil moisture recharge (from the island's mean
  watch rain, a third of today's daily recharge at the same level);
  polluted runoff from parcels whose peak was heavy or severe; standing
  water rising to `floodplain_depth` on parcels whose peak was severe (the
  rule `surface_day` uses today, per parcel instead of island-wide); flood
  damage recorded from the new level straight away, so an 08:00 flood
  counts (my call); rain collector intake and subway flooding per parcel,
  scaled so three watches of uniform rain add what one day does today;
  `flood_active` recomputed.
- **Midnight only (already off the main thread):** draining of standing
  water at today's daily rates; parcels whose peak was severe in any watch
  today skip draining, the per-parcel form of today's rule that nothing
  drains on a severe day (my call); repair days counting down, soil drying,
  and the work that needs the utility network (pumps, collector use).

**Live flooding.** Today, on a severe day, `surface_flood` adds
`floodplain_depth` to every parcel all day, and road closures, inundated
buildings, utilities going offline, harbour access, routing and the scene's
water all read it. That live term becomes per parcel: a parcel under severe
`rain_now` gets it, others don't (my call). The watch then makes the water
stay after the storm has passed.

The midnight watch runs inside `advance_day_with_traffic`, replacing the
single `weather_day` call. The 08:00 and 16:00 watches run in the frame loop
when the day's clock crosses those hours. Bulk advances (`tick`,
`play_month`, benchmarks, replays) run all three watches for each day.

**The prepared day.** The next day is prepared in the background from a
snapshot of the city taken after midnight (`start_day_plan`). A watch that
changes the city must discard that plan so it is prepared again from the
updated city; otherwise the 08:00 and 16:00 rain would be lost. The plan is
already restarted when discarded, so this costs background work, not frames.

**After a daytime watch (my call).** The 08:00 and 16:00 watches change
only city arrays on the main thread. What follows from them, refreshing
stats (offline utilities, closed roads), rebuilding the citizen roster so
evacuations can start, the activity log's flood alert, and the scene's water
and map layer, is prepared in the background like the day plan and applied
when ready, a frame or two later. Nothing heavy runs in the frame.

## What reads rain

Everything that asks "is it raining here?" reads the parcel's `rain_now`
instead of the island's weather:

- road pace for vehicles and walkers (`rain_road_pace`, used by citizens,
  fleet and sanitation) by the parcel being travelled;
- traffic delay (`delay_for`) by road parcel;
- storm road closures, which already follow standing water per parcel;
- the flood probe and water meshes in the scene, by parcel;
- evacuations: they begin when any parcel's `rain_now` is severe or the
  city has standing water, and evacuate only homes the existing plan finds
  threatened, which is already per parcel.

Stays regional: the weather badge, forecast and its text, solar output,
temperature, the "Severe rain forecast" scenario messages, and
`severe_rain(c)` where it means "today is a severe day" (HUD and messages).
Flood alerts in the activity log are raised by any watch that leaves standing
water, not only at midnight.

## What the player sees

- **Rainfall map layer.** A new layer shows today's rain per parcel: watches
  already past as they fell, the rest of the day as forecast (lighter), so a
  player can see a storm coming toward a district. Legend: "Rain today ·
  darker is heavier · faded is still to come".
- **Clouds follow the cells.** Nimbostratus and cumulonimbus bodies are
  placed along the cells' current positions (one or two per cell, scaled to
  its radius) instead of scattered; the baseline's light rain keeps the
  existing spread-out layer. Other cloud types are unchanged.
- **Rain falls under the storms.** The renderer gets the cells (position,
  radius, level, velocity) and the baseline each frame. Rain streaks, puddle
  rings and how wet surfaces are follow the rain at each point: heavier
  under cells, the baseline elsewhere, none where none falls. Ground stays
  wet behind a cell for a while along the path it travelled, drying as the
  global wetness does today.
- **Same hour.** The picture uses the exact time; the simulation's live
  rain uses the hour. A storm over a district slows and floods it while it
  is there; the watch decides how much water stays after it leaves.

## Engine (Strata) work

- A small uniform block of rain cells (at most 8: centre, radius, level,
  velocity) plus the baseline, set each frame (`sv_set_rain_cells`, bound in
  `Strata.Ffi.Vk` and driven from `Strata.Weather`).
- The light pass computes rain and wetness at each surface point from the
  baseline and cells (wetness includes a trail behind each cell), replacing
  the single global wetness where cells are set; with no cells set, today's
  global behaviour is unchanged.
- Rain streaks need the rain at each pixel's world position. How the
  composite pass learns it (the light pass handing it over in the lit
  image's spare channel, or the composite reading depth) is the builder's
  call.

## Decided by the user

- Three watches a day, not hourly.
- Patchiness as in the table.
- Forecast stays island-wide; a rainfall layer shows today's storms; flood
  alerts and evacuations happen only where heavy rain falls.
- Idra's Unending Rain stays island-wide.
- Older saves may break.
- Ordinary cities switch to local rain; existing tests that land on rainy
  days may be re-baselined.

## Left to the builder

- Exact cell counts, radii, speeds and start hours within the stated ranges,
  and the seeded functions that pick them.
- How hourly levels are sampled within a watch (eight samples is the
  intent).
- Exact recharge and runoff scaling per watch, provided a day of uniform
  rain over three watches gives the same soil moisture and runoff as today's
  single daily update.
- Layer colours, and where the rainfall layer sits in the toolbar.
- How streaks learn local rain (see Engine).
- Tests: storms are deterministic for a seed and date; parcels outside every
  cell get only the baseline; uniform rain reproduces today's daily totals;
  a severe cell floods the parcels it crosses and not the others; the
  flood scenario, drill and evacuation tests pass unchanged (uniform);
  other tests may be re-baselined where rain days change their numbers.
