# Sea Gameplay (water slice 3) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Rough seas suspend or slow ferries and drive directional coastal surge, from the start of a game, with a Sea storms setting (new game and in play), a sea forecast, and four remedies that visibly work (breakwaters, reefs, protected harbours, larger ferries).

**Architecture:**
- Each day, while the day is rolled on its worker, Ur computes **today's sea**: a significant wave height in centimetres for every water parcel. It's the sea state's height × the refracted swell's amplitude (cached in Play from the sea job) × exposure, written to `City.sea_heights`.
- The simulation (pure) reads only that array, times the Sea storms multiplier. That drives ferry status per route, coastal surge per shore parcel, and the fish catch.
- The menu and HUD show the setting, the forecast and route status.

**Tech Stack:** March (forge); Ur only. Strata is unchanged.

**Spec:** `docs/superpowers/specs/2026-11-23-sea-gameplay-design.md`

## Global Constraints

- Sea storms is `setup[7]`, levels 0..4, default 2. The multipliers are Calm 0.5, Mild 0.75, Normal 1.0, Rough 1.25 and Harsh 1.6, and Calm turns surge off. Old saves with a 7-entry setup load as Normal.
- Ferry ratings: standard 150 cm, larger 300 cm. Slowed from 75% of the rating; suspended above 100%. A protected harbour halves the height counted at its end.
- Surge replaces the fixed severe-rain `16 - loss` coastal term. Rain basins are unchanged.
- Everything the city counts comes from `City.sea_heights`, so the drawn sea and the rules agree. The setting scales what's counted, never what's drawn.
- The day roll stays on its worker. The main thread only hands it the cached swell and exposure.
- Tests: `forge test test/<file>.march`, one file per invocation. In March, `||` and `&&` evaluate both sides, so put recursion in `if`. Use distinctive type names. Don't read Float fields of another module's record in test builds.

## Review Focus

1. **A ferry whose route crosses land-locked or unmeasured parcels:** count only the water along the straight crossing. A route with no water samples stays running.
2. **A save made before this slice:** no `sea_heights`, and a 7-entry setup. It loads at Normal and calm seas until the first new day, with no suspended ferries at load.
3. **Changing Sea storms in play:** ferry status and surge follow on the next day roll. Nothing jumps mid-day.
4. **The founding map's second island:** a suspended ferry cuts the road link (`founding_map` treats ferries as roads). It must reconnect when the seas drop, with no stuck state.
5. **Calm setting:** no ferry ever suspends below 300 cm of true sea, and no surge.

---

### Task 1: Today's sea in the simulation's data

**Files:** `lib/ur/sim.march` (City field, setup default, `sea_factor`, `sea_at`), `lib/ur/save.march`, `test/sea_rules_test.march` (new).

- Add `City.sea_heights : NativeIntArr` (`S.count()`; cm; 0 on land). Constructors get zeros. Save and load it as an optional array (limit 2000).
- `default_setup()` grows to 8 entries, with `[7] = 2`. `fn sea_storms(c) : Int` reads `setup[7]`, or 2 when the setup is shorter. `fn sea_factor(c) : Int` gives percent: 50, 75, 100, 125 or 160.
- `fn sea_at(c, lot) : Int` is the counted height in cm, `sea_heights[lot] * sea_factor / 100`.
- Tests: the factor at each level; `sea_at` scales; a short (old) setup reads Normal; save and load round-trip the array.
- Commit: "Today's sea: a counted wave height for every water parcel, and the Sea storms setting".

### Task 2: Ferries feel the sea

**Files:** `lib/ur/sim.march`, `test/sea_rules_test.march`.

- `City.ferry_works : NativeIntArr` per terminal lot (bit 1: larger ferry; bit 2: protected harbour), saved like `sea_heights`.
- `fn crossing_sea(c, a, b) : Int` is the worst `sea_at` over the water parcels on the straight line between terminals `a` and `b`. Each terminal's own end is halved if that terminal is protected. Returns 0 if there's no water.
- `fn ferry_status(c, lot) : Int` gives 0 running, 1 slowed or 2 suspended, against the rating: 150, or 300 if either terminal has a larger ferry.
- Suspended links close. Every place that treats `c.ferries` as a link checks `ferry_open(c, lot)` too (`sim.march` around lines 1123, 3211, 3274, 3280, and freight `ferry_leg` / `use_ferry_space`).
- Slowed routes halve ferry cargo capacity (`ferry_cargo_capacity`).
- Day-roll message on a status change: "Ferry to <terminal> suspended: <h> m seas" / "resumed".
- Tools: 122 Larger ferry ($6,000, terminal lot) and 123 Protected harbour ($4,500, terminal lot or the harbour), routed through `sea_work` and the toolbar's Transit ferry page.
- Tests:
  - running, slowed and suspended at 100, 120 and 160 cm;
  - a larger ferry runs at 250;
  - a protected end halves its sample;
  - a suspended founding-map ferry disconnects the island's roads, and they reconnect when the sea drops.
- Commit: "Ferries feel the sea: slowed, suspended, and the remedies".

### Task 3: Directional surge and the catch

**Files:** `lib/ur/sim.march`, `test/sea_rules_test.march`.

- In `coast_approach`, when the walk reaches open water, the surge is the counted sea there: `S.clamp(sea_at(c, lot) / 12, 0, 16)` voxels, minus distance loss as now, instead of the fixed 16. Seawalls and the offshore barrier keep blocking.
- `surface_flood` takes the coastal surge every day (not only on severe rain), and the basin term only on severe rain. Calm (level 0) takes no surge.
- Fish plants (plant 6) count half their catch on days when the sea at their parcel, or the nearest water, is over 200 cm.
- Tests: no surge at 0 cm; surge grows with the sea; a seawall blocks it; Calm has none; the catch halves at 250 cm.
- Commit: "Surge and fishing follow the sea".

### Task 4: Ur computes today's sea on the day worker

**Files:** `lib/ur/sea.march` (`daily_seas`), `lib/ur.march` (`roll_day` gains the cached swell and exposure; Play keeps the last swell and exposure from the sea job), `test/sea_test.march`.

- `fn daily_seas(c, ocean, exposure, swell : Option(Strata.Waves.Swell)) : NativeIntArr`, per map water parcel, in cm:
  - `state_at(c, 0).height × exposure(parcel) × swell amplitude at the parcel centre` (1 without a swell);
  - land is 0.
- `roll_day` writes it to the new day's city before `S.advance_day_with_traffic`.
- Tests: land 0; open water near the sea state's height; a lee parcel lower than an exposed one.
- Commit: "Today's sea is measured from the water you see".

### Task 5: Setting, forecast and status in the interface

**Files:** `lib/ur/menu.march` (setup row 7 "Sea storms" with names Calm..Harsh; a Sea page in the game menu with − / + changing `setup[7]`), `lib/ur/hud.march` (forecast panel line "Sea: 1.2 m, rising to 2.8 m" from `Ur.Sea.state_at` over the next days × the factor; transit and parcel inspector ferry status), `lib/ur.march` (the Sea page action).

- Check by screenshot: the setup screen row, the Sea page, the forecast line, a suspended ferry's inspector.
- Commit: "Sea storms setting, sea forecast and ferry status".

### Task 6: Tune and verify

- Add a `UR_SEA_REPLAY=<level>` headless replay. It advances a season on the founding demo and prints suspended days per route and surge days per shore.
- Tune the surge divisor and confirm the ratings hit the target (Normal: an unprotected, exposed ferry suspended about 3–5 days a season).
- Run all Ur test files. Take screenshots of a storm with a suspended ferry, and of a breakwater protecting a route.
- Merge into `main` when green.
