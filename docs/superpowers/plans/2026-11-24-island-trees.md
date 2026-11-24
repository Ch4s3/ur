# Island Trees Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wild trees chosen by zone (coast, lowland, mid, upper, top), by windward or lee slope, with many kinds that vary tree to tree, mangroves on about one map in three and a lee pine stand on about one in three.

**Architecture:** A new `Ur.Flora` module decides, from the city alone, what grows at a spot: map traits from the seed, the spot's zone from height relative to the local massif, its wind side, its shelter. A new `Ur.Trees` module draws each kind as `Ur.Architecture.Piece` boxes. `Ur.Landscape.vegetation` and `park` call them in place of `Ur.Architecture.tree`.

**Tech Stack:** March, forge (`source ~/code/strata/scripts/env.sh` first), Strata.Seed.

**Spec:** `docs/superpowers/specs/2026-11-24-island-trees-design.md`

## Global Constraints

- No save-file change; no new `City` field; everything a pure function of city, parcel, spot, seed.
- No new palette entries: colours from `Ur.Scene.colour` ids (1 light wood, 13 dark wood, 14 deep green, 21 green, 22 pale green, 25 mid green, 11 fern green, 16 sand, 15/18 blossom).
- A tree is at most 12 pieces; at most three trees a parcel (as now); pieces stay inside the parcel (x, z in 0..31).
- No temperate fir/spruce shapes. No gameplay effect.
- Founding map (`world_seed < 0`): mangroves on, pine stand off, prevailing heading 0.42 rad (the daily wind's base).

## Review Focus

- A tiny island (peak h 8–12): must still show coast then lowland trees, never top scrub on its beach.
- A parcel regraded or flattened by the player: trees follow its new height (no stale zone).
- Water parcels on non-mangrove maps: no pieces at all (no stray trunks in the sea).
- Map edge parcels: neighbour and ray lookups out of range count as open sea, never crash.
- Parks: still one tree, now a lowland kind; its pieces still pass `A.orient`.

---

### Task 1: Map traits

**Files:**
- Create: `lib/ur/flora.march` (module `Ur.Flora`)
- Test: `test/island_trees_test.march` (module `IslandTreesTest`, same header style as `test/sea_rules_test.march`)

**Interfaces:**
- Produces: `Ur.Flora.prevailing(c : Ur.Sim.City) : Float` (radians the trade wind blows toward, 0 east, pi/2 south); `Ur.Flora.mangrove_map(c) : Bool`; `Ur.Flora.pine_map(c) : Bool`.

- [ ] **Step 1: Write the failing tests** — `mangroves on about a third of seeds`: over world seeds 1..300, `mangrove_map` true for 70..130; same bounds for `pine_map`; the two agree on at most 60% of seeds (independent draws). `founding map defaults`: a city with `world_seed: -1` gives mangroves true, pines false, prevailing 0.42. `prevailing is fixed by seed`: equal for the same seed on two different days.
- [ ] **Step 2: Run, expect FAIL** — `forge test test/island_trees_test.march` → unknown module `Ur.Flora`.
- [ ] **Step 3: Implement** with `Strata.Seed.mix(c.world_seed, 1301)` (mangroves, `% 3 == 0`), `mix(…, 1302)` (pines), `unit(mix(…, 1303)) * tau` (heading).
- [ ] **Step 4: Run, expect PASS.**
- [ ] **Step 5: Commit** `Flora: map traits — prevailing wind, mangrove and pine maps`.

### Task 2: The spot — zone, wind side, shelter

**Files:** Modify `lib/ur/flora.march`; test `test/island_trees_test.march`.

**Interfaces:**
- Produces:
  - `Ur.Flora.massif_peak(c, lot : Int) : Int` — highest `c.heights` over land reachable from `lot` through 4-connected land parcels within 8 parcels (Chebyshev); 0 for water.
  - `Ur.Flora.zone(h : Int, peak : Int, wet : Int, jitter : Int) : Int` — 0 coast, 1 lowland, 2 mid, 3 upper, 4 top. Coast when `h <= 6`. Otherwise share = h·100 / max(peak, 24) (a low island is never "top"), shifted by `wet` (−1 lee: +8 points; +1 windward: −8 points) and `jitter` (−6..6, the per-tree blend). Bounds: lowland < 30, mid < 60, upper < 85, else top.
  - `Ur.Flora.wind_side(c, lot) : Int` — +1 windward, −1 lee, 0 flat: slope vector from the four neighbours' heights (out of range = 0); windward when the downhill direction points against `prevailing` (dot < −0.3 of the unit vectors) and the slope is ≥ 4 voxels across a parcel.
  - `Ur.Flora.sheltered(c, lot) : Bool` — of 16 rays from the parcel, each up to 8 parcels, at most 5 reach the map edge without meeting land (`c.heights > 0`).

- [ ] **Step 1: Failing tests** with hand-built heights (helper `fill` as in `sea_rules_test`): `massif peak stops at water` (two islands, peaks 20 and 60, the small one reads 20); `massif peak is local` (a ridge 12 parcels long, its far end out of reach); `small island zones` (`zone(10, 12, 0, 0) == 1`, never 4 for any h ≤ 12); `windward reaches lower` (`zone(h, 60, 1, 0) >= zone(h, 60, -1, 0)` for h 7..60, strictly greater somewhere); `coast below sand line` (`zone(5, 60, 1, 6) == 0`); `wind side` (a slope rising toward the wind's source is +1, the far side −1, flat 0); `sheltered bay vs open coast`; `edge parcels do not crash` (all four corners).
- [ ] **Step 2: Run, expect FAIL.**
- [ ] **Step 3: Implement** (bounded flood fill over a `NativeIntArr` visited mask; rays stepping by the 16 sector headings).
- [ ] **Step 4: Run, expect PASS.**
- [ ] **Step 5: Commit** `Flora: zone by the local massif, wind side, shelter`.

### Task 3: Tree shapes

**Files:** Create `lib/ur/trees.march` (module `Ur.Trees`); test `test/island_trees_test.march`.

**Interfaces:**
- Produces `Ur.Trees.kinds() : Int` (= 12) and `Ur.Trees.shape(kind : Int, x : Int, z : Int, base : Int, seed : Int) : List(Ur.Architecture.Piece)` with kinds: 0 coconut palm (curved 2-segment trunk leaning by seed, 4–6 drooping frond boxes, sometimes a nut cluster), 1 columnar araucaria (thin tall trunk, many short level tiers), 2 mangrove (3–4 arched prop roots from y = base, low dense flat canopy), 3 broad rainforest tree (tall bare trunk, wide flat canopy, sometimes buttress boxes), 4 banana clump (2–3 short stems, broad paddle leaves), 5 ʻōhiʻa evergreen (twisted trunk offset, dense rounded crown, blossom spots 15/18 on some seeds), 6 tree fern (slim trunk, flat rosette of fronds), 7 cloud-forest tree (short, crooked, wide crown, moss 22), 8 elfin tree (1–2 m gnarled), 9 bush, 10 Hispaniola pine (long bare trunk, tufted crown near the top), 11 koa-like open tree (spreading sparse crown, lee). Each varies by seed in size, lean, crown offset, leaf shade.

- [ ] **Step 1: Failing tests** — for every kind and seeds 0..199 at (16, 16, base 20): 1 ≤ pieces ≤ 12; every piece within x, z 0..31 and y ≥ 20; `shape` equal for equal arguments; at least 8 distinct piece lists across the 200 seeds for every kind; palm and araucaria taller than banana on average; elfin no taller than 8 voxels above base.
- [ ] **Step 2: Run, expect FAIL.**
- [ ] **Step 3: Implement** the twelve shapes (helpers like the existing `leaf_tier`; spots near a parcel edge clamp so pieces stay inside).
- [ ] **Step 4: Run, expect PASS.**
- [ ] **Step 5: Commit** `Trees: twelve island tree kinds, each varying by seed`.

### Task 4: Choose and plant

**Files:** Modify `lib/ur/flora.march`, `lib/ur/landscape.march` (`vegetation`, `park`); test `test/island_trees_test.march`.

**Interfaces:**
- Consumes Tasks 1–3.
- Produces `Ur.Flora.pick(c, lot : Int, h : Int, seed : Int) : Int` — a kind, or −1 for none; computes massif peak and wind side once per call (the caller computes them once per parcel via `Ur.Flora.site(c, lot) : (Int, Int, Bool)` = (peak, wind side, sheltered) and passes into `pick_at(site, c, h, seed)`).

Choice table (by zone, then seed share): coast — palm 60%, araucaria 25%, broad 15% (land spots); lowland — broad 45%, palm 25%, banana 20%, ʻōhiʻa 10%; mid — ʻōhiʻa 60%, fern 30% windward / koa 30% lee and flat, broad 10%; upper — cloud tree 60%, fern 30% windward / ʻōhiʻa 30% otherwise, elfin 10%; top — elfin 55%, bush 45%. On pine maps, lee mid and upper spots: pine 60% replaces that zone's picks. `jitter = seed / 41 % 13 − 6`.

- [ ] **Step 1: Failing tests** — on a built island: coast land spots give only kinds {0, 1, 3}; top spots give only {8, 9}; windward upper spots include ferns (6), lee upper spots none; a pine-map lee mid spot gives kind 10 for some seeds and a non-pine map never; no kind outside 0..11; `structures` of a wild parcel still holds ≤ 3 trees (count trunk pieces of material 13 or 1 at ground level).
- [ ] **Step 2: Run, expect FAIL.**
- [ ] **Step 3: Implement** `pick`; in `vegetation` replace the `form` choice and `A.tree` call with `Ur.Trees.shape(pick_at(site, c, h, seed), x, z, h, seed)` when not −1, keeping today's spot draws, height limits (`h > 6 && h < 57`) and the grade check; `park` uses a lowland pick (broad/palm/banana/ʻōhiʻa by seed). Remove `Ur.Architecture.tree` and `leaf_tier` if unused.
- [ ] **Step 4: Run, expect PASS**; also `forge test test/ocean_test.march` and `test/road_planning_test.march` (they read `Landscape.structures`).
- [ ] **Step 5: Commit** `Wild trees follow zone and wind; parks plant lowland trees`.

### Task 5: Mangroves

**Files:** Modify `lib/ur/flora.march`, `lib/ur/landscape.march`; test `test/island_trees_test.march`.

**Interfaces:**
- Produces `Ur.Flora.mangrove_spot(c, lot, h) : Bool` — mangrove map, the parcel sheltered, and the spot water (h ≤ 0) in a parcel with a land neighbour, or sand (1 ≤ h ≤ 4).

- [ ] **Step 1: Failing tests** — mangrove map, a sheltered water parcel beside land: `structures` contains mangrove pieces (kind 2's root material 13 at y 0); the same parcel on a non-mangrove map: no pieces; an exposed coastal water parcel on a mangrove map: none; a water parcel with no land neighbour: none.
- [ ] **Step 2: Run, expect FAIL.**
- [ ] **Step 3: Implement**: in `vegetation`, before the land tree rule, spots that pass `mangrove_spot` plant kind 2 (up to three a parcel, `seed % 11 < 7`), base `max(h, 0)`. Confirm water parcels reach `vegetation` (zone 0, no building); if not, route them there.
- [ ] **Step 4: Run, expect PASS.**
- [ ] **Step 5: Commit** `Mangroves on sheltered shores of mangrove maps`.

### Task 6: Tune and verify

- [ ] **Step 1:** `forge build --release`; screenshots (`MARCH_PIN_MAIN=1 UR_DEMO=1 UR_FERRY_VIEW=1 UR_FRAMES=150 UR_CLOCK_HOUR=10 UR_ZOOM=…`) of the founding map: a coast close-up (palms, mangroves), a mountain side windward and lee, and a far view; plus a new-region seed with a pine stand. Tune shapes, colours and zone bounds by eye; commit tuning.
- [ ] **Step 2:** Check frame time is not worse than before (FPS readout in the HUD at the far view, before and after).
- [ ] **Step 3:** Run `test/island_trees_test.march`, `ocean_test`, `road_planning_test`, `ur_test` (the last ~15 min, in the background); all pass.
- [ ] **Step 4:** Merge to `main` and push (the owner's standing instruction: merge when green).
