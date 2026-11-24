# Lift map: storms that grow from land and sea temperature

Date: 2026-11-23. Builds on the local-rain design (`2026-11-23-local-rain-design.md`).

## Intent

Verisimilitude. Today every piece of Ur's weather is rolled independently:
the weather kind per three-day spell (`weather_pattern`), the wind as a sine of
the day number, temperature as season + noise (rain cools it — the only link),
and storm cells that enter from the upwind map edge at a random spot and hour
(`Ur.Rain.make`). The player should instead see weather that behaves the way
real island weather does, and be able to nudge it a little by how they manage
heat:

- summer afternoon thunderstorms over hot inland ground, clear sea;
- winter showers over the (then warmer) sea, hugging the coast, often at night or early morning;
- storms where sea breezes from opposite coasts meet, and on the mountain's windward side;
- a drier lee behind the mountain (rain shadow);
- a heavily paved city core seeding slightly more storms than a leafy one.

The user chose: rain follows the model (it moves where floods happen), and
heat management affects storms "a little".

## Goals

1. A simple, deterministic air model (`Ur.Air`): sea temperature, land
   temperature through the day, a land–sea contrast, sea/land breezes, and a
   per-area **lift** value.
2. Storm cells are **born** where lift is high, at the hours lift is high,
   then drift and die, replacing edge-entering cells for convective rain.
3. Rain shadow thins the day's baseline rain in the mountain's lee.
4. City heat (paving, buildings) adds lift; parks and trees remove it;
   the city's whole effect is capped near ±15 % on local storm odds.
5. Clouds follow: fair-weather cumulus builds over high-lift land on
   clear/cloudy afternoons; at night low cloud sits over the sea.
6. The island-wide amount of rain per regional weather kind stays within
   ±20 % of today's, so flood balance and its tests hold.

## Non-goals

- No fluid simulation, moisture advection, or per-hour re-rolling (that was
  approach B).
- The three-day regional roll (`weather_on`) stays the authority on how wet a
  day is; the model only decides *where* and *when* within the day, plus the
  occasional shower on a hot cloudy day (below).
- Forecast stays island-wide (local-rain decision). No new HUD panel.
- `temperature(c)` (daily °C used by utilities, walking, the heat layer)
  keeps its meaning and values. `wind_at` keeps its daily meaning, so wind
  turbines and their economy are unchanged.
- The sea shader / `Ur.Sea` swell keep using the regional wind.
- Uniform-rain cities (`rain_uniform`, the storm scenario) and Idra's curse
  are untouched: they keep the old daily path.

## Anti-goals

- Weather that looks random again (storms appearing over the cold summer sea
  at noon, or uniformly across the island).
- The player's heat management dominating weather — it is a nudge.
- Day-to-day replays or reloads that redraw a day's storms.
- Noticeably slower frames or tests (`ur_test` is already ~4¼ min).

## Constraints

- Map: 60×44 parcels of 8 m (480×352 m); sea is `heights == 0`.
- Months: 12 × 30 days; `temperature_on` peaks in month 6.
- Rain levels 0 / 2 / 3 / 4; `Ur.Rain.Cell` record and `level_at` stay.
- Everything is a pure function of seed, date and the city as it was at dawn.
- Older saves may break (the user said so for local rain; same here).
- March: arrays don't grow; no `Eq` on records; tail recursion via `if`, not `&&`/`||`.

## Approaches considered

- **A. Lift map, storms born from it (chosen).** Coarse lift grid from
  land–sea contrast, soil moisture, breeze convergence and windward slopes;
  cells born at lift peaks. Cheap, deterministic, flood code untouched.
- **B. Advected moisture field.** Most emergent; several times the work,
  hard to tune, flood risk swings unpredictably, hard to test. Rejected.
- **C. Nudge today's edge-entering cells.** Cheapest; storms never form over
  land, which is the part that reads as real. Rejected.

## Design

### `Ur.Air` (new module, pure)

Inputs: the city's heights, month, day, regional weather kind, regional wind,
soil moisture, and a per-parcel **city heat** array. Output, computed once at
dawn and stored on the city as `air`:

- `sea_temp(month)` — °C, follows the season one month late with a smaller
  swing than land: peak month 7, amplitude about two thirds of land's.
- `land_temp(daily, kind, soil, hour)` — `temperature(c)` is taken as the
  day's mean; a diurnal swing (low near 05:00, high near 15:00) whose size
  falls with cloud (clear ≈ 6 °C, cloudy ≈ 3, rain ≈ 1.5) and with soil
  moisture.
- **Coast field** — for each parcel, distance to the sea (in parcels, capped)
  and a unit vector pointing inland (from the gradient of that distance).
  Computed from heights.
- **Breeze** at hour h — onshore (along the inland vector) with strength
  ∝ (land − sea) contrast, fading with distance inland; offshore and weaker
  at night. Local wind = regional wind + breeze.
- **Lift** on a coarse grid of 15×11 areas (4×4 parcels, 32 m) at five
  snapshot hours (02, 06, 10, 14, 18 — each stands for the following four
  hours; 22 reuses 02). Per area, a sum of:
  - *heating*: land area's (land − sea) contrast when positive; over sea, (sea − land) when positive (winter/night sea showers), sea areas only
    within ~3 areas of land;
  - *moisture*: scales heating by soil moisture over land (dry ground lifts
    less);
  - *convergence*: how much the breeze vectors of neighbouring areas point
    into this area (inland meeting zones);
  - *orographic*: upslope component of the local wind × height gradient
    (windward slopes positive, lee negative);
  - *city heat*: the area's mean city heat (below).
  Stored as ints (fixed point) in one native array of 5×165.
- **Shadow** per parcel: true when the terrain upwind (along the regional
  wind, within ~10 parcels) rises well above the parcel — the mountain's lee.

### City heat

Per parcel, in tenths of °C added to land temperature for lift only:
`+` for a road or building on the parcel (paved/built), `−` the existing
`parcel_cooling` (trees, parks). Clamp so the island-wide city term can shift
any area's lift by at most the amount that changes its storm odds ~15 %.
It does **not** change `local_temperature` or anything that reads it.

### Storm birth (`Ur.Rain`)

`Ur.Rain.cells` gains the lift snapshots and the coast/shadow facts as plain
arrays (still no city record) and keeps its seeded `pick`:

- **Budget** — `cell_count` per kind stays the day's budget, ±1 from the
  day's total lift (strong-lift days one more, weak-lift days one fewer, never
  below today's minimum for kind 4).
- **Hot cloudy days** (kind 1): one short level-2 shower when the day's peak
  lift passes a high threshold (summer afternoon, wet soil). Clear days
  (kind 0) never rain. *(My call)* the shower is new rain, so it is outside
  the ±20 % calibration (which covers kinds 2–4); it runs through runoff
  like any rain, and soil recharge is left on the regional kind as today
  (a short level-2 shower barely matters to island-wide soil). The test
  "cloudy days have no rain" becomes "cloudy days rain only under strong
  lift".
- **Convective cells** (kinds 1–3, and all but one cell of kind 4): each
  picks a snapshot weighted by that snapshot's total positive lift, then an
  area weighted by lift² in that snapshot; birth hour inside the snapshot's
  four hours; small radius (kind 4: 60–90 m as now; kinds 2–3: 70–120 m),
  lifespan 2–5 h scaled by birth lift, drifting with the regional wind at
  about half its speed. Radius ramps up over the first hour and down over
  the last (level stays fixed; `covers` uses the ramped radius).
- **Fronts** (kind 4 keeps exactly one): the existing edge-crossing cell,
  so severe days still sweep the island. *(My call)* its radius is
  band-sized, 100–150 m, so it covers a real swath; the convective kind-4
  cells stay 60–90 m.
- **Baseline** — `baseline(kind)` as now; a parcel in shadow is thinned, not
  dried. *(My call)* level 3 drops to 2; level 2 stays 2 but falls only in
  alternate hours (a seeded per-parcel parity), so the lee gets about half
  the baseline rain. `level_at` takes the parcel's shadow flag and the hour.
  Shadow should cover roughly 10–20 % of land on a typical map; the
  calibration test counts shadowed parcels at their reduced rain, and cell
  sizes/counts are tuned so kinds 2–4 still land within ±20 %.

### City state and save

- `City` gains `storms : List(Ur.Rain.Cell)` and `air : Ur.Air.Air`
  (coast field, shadow flags, lift snapshots, sea temp). `fresh_day`
  computes both at dawn from the city as it stands; `day_cells(c)` returns
  `c.storms` (cheaper than today, where scene recomputes cells every frame).
- *(My call)* the save stores both `storms` and the whole dawn `air`
  (shadow flags, coast field, lift snapshots — a few thousand ints), so a
  load reproduces the day exactly even after mid-day grading. Older saves
  break, as agreed for local rain. Shadow depends on heights and the
  regional wind only, not city heat.
- A mid-day edit (grading, paving) changes tomorrow's storms, not today's.

### Clouds and visuals

- Storm and band bodies keep following `storms` (`cell_spot`), unchanged.
- Cumulus bodies (fair-weather types) on clear/cloudy days: their `presence`
  is weighted by the current snapshot's lift under them, so they gather over
  hot land in the afternoon and over the coast/sea at night.
- The wind layer and wind arrows show local wind (regional + breeze) at the
  current hour; turbines keep `wind_at`.

### Debug

`UR_RAIN_REPLAY` reports, per watch, the number of cells born over land vs
sea and the shadow parcels' rain, alongside flooded counts.

## Tests (each fails before its code)

- `Ur.Air`: sea warmer than land in month 0 at 05:00; land warmer than sea in
  month 6 at 15:00; breeze onshore on a coastal parcel at 15:00 in summer and
  offshore at 03:00; the windward slope of a test mountain has positive lift
  and its lee negative; a lee parcel is in shadow, a windward one isn't.
- `Ur.Rain`: same inputs → same cells; summer (month 6) convective cells born
  mostly over land (>70 % over many days) and mostly 11:00–19:00; winter
  (month 0) cells mostly over sea or coast; kind 4 always has exactly one
  edge-crossing front; kind 0 never rains; kind 1 rains only with strong lift.
- City heat: a paved city's island-wide storm-birth odds near the core are
  higher than a parked one's, by less than 20 %.
- Shadow: over many severe days the lee parcels average less rain than
  windward ones.
- Calibration: averaged over a year of days, island-wide rain units per kind
  are within ±20 % of the pre-change average (the number is taken from the
  current code before the change and written into the test).
- Determinism: a city saved and loaded mid-day has identical `rain_now` at
  every remaining hour.
- Existing `rain_cell_checks` updated to the new API and expectations.

## Left to the builder

Exact coefficients, thresholds and fixed-point scales; the precise diurnal
curve; how convergence is discretised; the city-heat weights per road/building
kind — tuned against the tests above and a look in the game.
