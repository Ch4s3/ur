# Island trees: zoned by height, wind and coast

## Why

Ur's wild trees are three stacked-block shapes (`Ur.Architecture.tree`,
forms 0–2) picked mostly by ground height, varying only in trunk height,
canopy size and two leaf shades. A forest reads as three trees repeated. The
owner wants variety, and wants it to look like a real tropical island: the
mountain sides should carry what grows on island mountains, tropical trees
lower down and on the coast, and some maps should have mangroves.

## What real island mountains carry (research)

- Lowland rainforest (tall, wide-crowned) gives way to montane rainforest
  (shorter evergreens: Hawaiian ʻōhiʻa, koa, tree ferns beneath), then cloud
  forest on wind-facing upper slopes (short, twisted, mossy), then elfin
  forest at the top (gnarled trees 1–5 m).
- Small islands compress the zones (Massenerhebung effect): cloud forest from
  ~300 m on Kosrae against ~1,600 m on Hispaniola. So zones follow each
  island's own peak, not fixed heights.
- Conifers on tropical islands come in stands, not as the rule: Hispaniola's
  pine forests (*Pinus occidentalis*) and Podocarpus; New Caledonia's columnar
  *Araucaria* along the shore.
- The windward side is far wetter (Hawaii: tree ferns, cloud forest); the lee
  is drier and more open (koa-like woods, pines).

## Goals

- Trees chosen by zone: coast, lowland, mid-slope, upper slope, top, with
  zone edges blended (a tree near an edge may come from either side).
- Windward slopes wetter (tree ferns, cloud forest reaching lower), lee
  slopes drier (open koa-like woods; pine stands where a map has them).
- Each kind varies tree to tree: size, lean, crown offset, leaf shade.
- About one map in three has mangroves on low, sheltered shores; about one in
  three has a pine stand on its mountains (independent draws from the map
  seed).

## Non-goals

- No gameplay effect: mangroves do not damp surge, trees do not change
  rainfall or land value. (A later step could make mangroves soften surge.)
- No change to where trees may stand (the same parcels as today), to save
  files, or to park trees beyond their picking from the new kinds.
- Not Strata's branching tree generator (approach B below).

## Anti-goals

- Temperate firs and spruces filling the mountains: wrong for a tropical
  island.
- A visible line where one zone stops and the next begins.
- A frame-time or mesh-size regression: a tree stays about as many pieces as
  today's (≤ ~12), at most three trees a parcel as now.

## Approaches

- **A. More kinds of Ur's block trees (chosen).** New shapes in the existing
  piece style, zoned by height, wind and coast. Keeps the island's one chunky
  style; cheap everywhere. A palm is a stylised palm.
- **B. Strata's branching trees (`Strata.Trees`) with palm and mangrove
  species added.** More natural, but much finer than the buildings, and
  variety would come from a fixed pool of prebuilt templates (memory and load
  time). Not chosen.

The owner chose A, with the windward/lee distinction.

## The design

**Kinds** (each a function of seed for its variation; colours from the
existing palette ids):

| Zone | Kinds |
|---|---|
| Coast (sand band and next parcel in) | coconut palm (curved trunk, frond crown), columnar araucaria, mangrove (mangrove maps) |
| Lowland | broad flat-crowned rainforest tree, palm, banana-like clump |
| Mid-slope | ʻōhiʻa-style rounded evergreen; tree fern (windward) |
| Upper slope | short twisted cloud-forest tree; tree fern (windward) |
| Top | elfin scrub: small gnarled tree, bush |
| Lee mid/upper on pine maps | tall pine (Hispaniola-style: long bare trunk, tufted crown) |

**Zone from relative height.** A parcel's height as a share of the peak of
the island it stands on (its connected land), so a low island still runs
coast → lowland → a little slope, and a big one shows every zone. Shares
(builder may tune by eye): coast below the sand line (h ≤ 6) or next to sea;
lowland to ~30%; mid-slope to ~60%; upper to ~85%; top above. Rock above the
tree line stays bare as today (h ≥ 57 no trees).

**Windward or lee.** Each map gets a fixed prevailing wind heading from its
seed (the trade wind). The daily wind in `Ur.Sim.wind_heading_on_day` turns
all the way round over the months, so it cannot set a forest; the trees use
the prevailing heading only. A parcel is windward when its ground slopes down
toward the wind's source (the slope faces into the wind), lee when it faces
away, neutral on flat ground. Windward shifts zones down (cloud forest and
tree ferns reach lower); lee shifts them up and thins the forest.

**Mangroves.** On mangrove maps: in shallow water next to land and on the
lowest sand, where the sea is sheltered (low swell exposure,
`Ur.Sea.exposure`), a band of mangroves: a low dense canopy on arched prop
roots, roots standing in the water. Exposed surf coasts get none.

**Determinism.** Everything is a function of the parcel, its position and
the map seed, as today: the same map always grows the same forest.

## Left to the builder

- Exact piece layouts and colours of each kind, tuned by screenshots.
- The zone shares and the windward shift, tuned by eye on a few seeds.
- How the island's peak is found (a flood fill of land parcels at map build,
  or an equivalent) and where it is kept, as long as nothing is added to save
  files.
- How mangroves are drawn on water parcels (water parcels draw no vegetation
  today).
