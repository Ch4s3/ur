# Sea gameplay (water slice 3) — design draft

Date: 2026-11-23 · Status: **draft for discussion**; open questions are
marked ❓

## Intent

The sea becomes something the city plans around. Wind and storms produce a
daily sea state with real consequences: rough seas suspend ferries (on the
founding map that can cut the second island off) and storm surges flood
exposed coasts. The answer is investment the player can *see working* on
the water. Agreed so far: a sea state with consequences, "harsh with a
remedy", and the remedies are larger ferries, artificial reefs,
breakwaters and protected harbours.

## What already exists (slices 0–2)

- **Sea state** (`Ur.Sea.state_at`): wind speed and heading, wave height and
  whitecaps, from the daily wind and weather, eased through each day.
- **Exposure** (`Ur.Sea.exposure`): per padded parcel, from fetch.
- **Refracted swell** (`Strata.Waves`, through `Ur.Sea.swell`): per 2 m cell,
  phase and amplitude. It bends, shoals and breaks over the seabed, wraps
  round land, and is shadowed by breakwaters (seawalls) and reefs. It's
  solved on workers whenever the wind's sector, the coast, seawalls or the
  seabed change.
- **Sea query** (slice 1): the water's height and slope at any point and
  time, matching what is drawn. Ferries already ride it.
- **Seabed edits and land** (slice 2): dredge, reef, reclaim land, cut a
  harbour.
- **Flooding:** coastal surge (`S.floodplain_depth` / `coast_approach`)
  fires on severe-rain days, from all directions, blocked by seawalls and
  high ground.

## The design

**1. Wave height where it matters.** Each day (on the worker, with the
swell solve), sample the **significant wave height** at:
- every **ferry crossing**, taking the worst along the route between its
  terminals;
- every **shore parcel**, the water parcel beside it.

Each is the sea state's height × the swell field's amplitude there ×
exposure. These numbers drive everything below, so what the player sees on
the water is what the simulation uses.

**2. Ferries.**
- Each route has a **rating**, the wave height its ferry can run in:
  - standard: about 1.5 m;
  - **larger ferry** upgrade: about 3 m, with more capacity and upkeep.
- Above the rating, the route is **suspended** for the day. Its link
  leaves the road and transit networks, as `ground_closed` lots already do.
- Between 75% and 100% of the rating it runs **slowed**, with capacity
  reduced.
- A **protected harbour** (terminal upgrade) halves the wave height counted
  at that end (calm water to load in) and shields the terminal parcel from
  surge.
- Status shows in the parcel inspector, the transit panel and a
  notification: "Ferry to the east island suspended: 2.4 m seas".

**3. Coastal flooding becomes directional and sea-driven.**
- The surge at a shore parcel scales with the wave height arriving there
  and how squarely the shore faces the wind, instead of a fixed 16 from
  every direction on severe-rain days.
- Rain flooding (basins) stays as it is.
- Seawalls on land keep blocking. Breakwaters and reefs offshore lower the
  arriving height through the swell field, so their protection is
  emergent, and visible.
- ❓ Minor overtopping on windy dry days (only exposed shores without
  defences)?

**4. Forecast.** The weather panel's forecast adds the sea:
"Sea: 1.2 m, rising to 2.8 m in two days".
- Highlight routes and shores at risk.
- This keeps cut-offs from being a surprise, which is essential for
  "harsh".

**5. Remedies, summarised**

| Remedy | How it works | Built with |
|---|---|---|
| Breakwater | blocks the swell; calm lee | seawall on water (exists) |
| Artificial reef | waves break early; calmer shore behind | reef tool (slice 2) |
| Protected harbour | terminal end counts half the seas, shielded from surge | new terminal upgrade |
| Larger ferry | route runs in up to about 3 m seas, more capacity | new route upgrade |
| Dredged channel | lets a larger ferry use a shallow approach | dredge (slice 2) |

## Open questions

- ❓ **When does storm pressure start?** From the first season, growing with
  the city, or slowed-only at first with full suspensions later? This
  changes the early game most.
- ❓ Should larger ferries need a dredged approach (a minimum depth at both
  terminals), tying slices 2 and 3 together, or is that too fiddly?
- ❓ Do rough seas affect anything else, such as fishing (`island_catch`) or
  freight shipments?
- ❓ How often should cut-offs happen at the start? A target such as "an
  unprotected ferry is suspended a few days a season" sets the thresholds.

## Not in this slice

Ship navigation, waves damaging structures, tsunamis or god-game events,
tides.
