# Mangroves absorb storm surge; pollution kills them

Follows `2026-11-24-island-trees-design.md`, which made mangroves scenery on
about one map in three. The owner wants them to matter: a living sea defence
that pollution can destroy.

## Why the strength is fair

Ur's surge comes from the day's wave height at a water parcel (`surge_at`,
from `sea_at`), not from a slow rise in still water. Mangroves are strongest
against waves: field studies find wave height cut by roughly half to two
thirds within the first 100 m of forest. Their effect on the still-water part
of a surge is small (a few cm per km). So a stand halving the surge that walks
in through it is defensible for this model.

## Behaviour

- **One rule for where mangroves stand.** `Ur.Sim.mangrove_water(c, lot)`: a
  mangrove map, a sheltered water parcel beside land, and clear water (no
  seawall, ferry route, transit, grade cover or player seabed edit; not the
  harbour). Drawing and surge both use it, so what you see is what defends.
  This also closes the review finding that mangroves grew through crossings
  and dredged harbours.
- **Surge.** When surge walks in from a water parcel holding a living stand,
  it arrives at half height (a thinned stand: three quarters). The long-run
  flood-risk display (the geometric reach) is unchanged: it shows potential.
- **Pollution.** A new per-parcel `mangrove_harm` (0..100, saved, optional,
  old saves load as 0). At each month's end, a stand's harm rises by
  (pollution − 30) / 2 where the coastal water pollution (`pollution_at`) is
  over 30, and falls by 2 where it is 15 or under (slow regrowth: a dead stand
  in clean water takes about four years to recover). Harm 50+ is a thinned
  stand (fewer, paler trees; three-quarter surge); 100 is dead (bare grey
  snags; no protection) until harm falls back under 50.
- **Telling the player.** The month a stand dies, the message line says so:
  "Mangroves died in polluted water — the shore behind them has lost its
  storm buffer."

## Non-goals

A planting tool (possible later step); mangroves changing fishing or land
value; pollution from anything new.

## Calls made here (owner may change)

The thresholds 30/15, the rates, half and three-quarter surge, four-year
regrowth, the dead stand's look.
