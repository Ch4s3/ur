# Economy depth: land value, household wealth, funding, debt and a stock market

Status: approved 2026-11-20.

## Intent

Running Ur's treasury should involve real money decisions, not a cash total
that only blocks construction. The player should borrow and owe, fund
services more or less generously, see what their choices do to the value of
land and to their residents' wealth, and watch local companies rise and fall
on a stock market they can influence but not trade. Booms and busts should
reach residents' savings, the kind of businesses the city attracts, and the
ballot box.

The five systems are one design because each feeds the next. Better
services raise land value. Land value sets rent and property tax. Household
wealth comes from what is left after rent and from shares. City debt and
spending move the market. The market moves wealth, business quality and
elections.

## Goals

- Loans and bonds, a credit rating, and a three-stage failure path that can
  end the game.
- Funding levels per service group that change cost and output.
- A land value per parcel that sets rent and property tax.
- Savings for each household, carried when it moves.
- A per-company stock market with reasonably realistic dynamics, a
  value-weighted index, and a chart of any stock's price over time.
- Two player levers on the market: tax breaks for listed firms and a listing
  incentive.

## Non-goals

- The player does not buy or sell shares, run a sovereign fund, or set
  interest rates.
- No regional neighbours, inter-city trade, or a central bank.
- No per-citizen wealth for the detailed walkers; wealth belongs to
  households, as other household state does.
- No mortgages or home ownership.

## Anti-goals (would make this a failure even if it worked)

- A market that is noise the player can ignore, or one with an obvious
  dominant strategy (for example, borrowing endlessly because debt is free).
- Insolvency that arrives without warning or without a way back.
- Breaking determinism: the same city and inputs must replay the same way.
  Tests, replays and `UR_BENCH` depend on it.
- Saves from before this change failing to load.
- A large drop in simulation speed. The monthly settlement is the hot path.

## Constraints

- Everything lives in `Ur.Sim.City` and is saved by `lib/ur/save.march`.
  New fields need encoders and decoders with defaults for older saves.
- State is kept per parcel in `NativeIntArr` arrays of 2,640 cells where it
  is per place, and as small records or lists where it is per entity.
- All randomness is derived from the city's seed, the month and an id with
  the existing hash style (see `weather_pattern` and `climate_seed`). No
  random state that advances.
- Time advances through `Ur.Clock` (day) and `Ur.Sim.settle_month` (month).
  Monthly work goes in settlement; daily work only if it must be daily.
- The HUD is drawn from rectangles and text (`Strata.Ui`); line charts are
  drawn with the existing `segment`/`line_mark` helpers in `lib/ur/hud.march`.
- Every suite run individually must pass, plus `forge lint --strict`.

## Approaches considered for the market

- **A. Every listed firm has its own stock (chosen).** Each listed business
  parcel carries shares, a price history, earnings and a dividend; the index
  is value-weighted. Firms boom, slump and fail individually, so tax breaks,
  listing incentives and closures act on real companies. Most state and the
  most balancing.
- **B. One citywide index** driven by total business earnings. Cheap, but no
  company stories, and incentives only nudge one number.
- **C. Sector indices** (retail, offices, workshops, processors,
  manufacturers). Middle cost, ties to land use, but loses individual firms.

The player chose A and wants to chart any individual stock over time.

## Build order

1. Land value
2. Household wealth
3. Funding levels
4. Debt: loans, bonds, credit rating, failure stages
5. Stock market

Each step should leave the game playable and all suites passing.

## 1. Land value

**What it is.** A value per parcel, recomputed in monthly settlement, that
summarises how desirable the land is.

**Inputs** (weights are the builder's to tune, see "Left to the builder"):
- road access and commute time to work;
- civic coverage (school, clinic, fire, police), parks and their tier;
- transit within walking distance;
- the coast (the `coastal` test already exists);
- minus noise (`street_noise`) and land and air pollution;
- plus the average wealth of households in nearby parcels (step 2);
- a slow pull toward the regional market: land values move a fraction of the
  way toward their computed target each month, so they lag and trend rather
  than jump.

**What it drives.**
- **Rent.** `housing_rent` and business rent (`asking_rent` callers) take
  land value as their location term, replacing today's separate location
  premium where they overlap.
- **Property tax.** `budget` replaces `people * 2 / 3` with a property tax
  rate applied to the total land value of built, occupied parcels. Start the
  rate so a default city's property tax is about what it is today. Add a
  property tax rate control beside income and business tax in the policy
  panel.
- **Who pays (builder's call, approved).** Landlords pass property tax
  through in rent: the tax on a parcel is added to the rent its households
  and businesses pay, so raising the rate raises rents, squeezes margins and
  affects affordability and migration. It is never free revenue.
- **Vacant buildings (builder's call, approved).** The existing vacant
  property bill, arrears, condemnation and city sale path stays, with the
  bill re-based on the parcel's land value instead of `buildings * 4`.
  Undeveloped land keeps a value but pays nothing.

**Player view.** A land value map layer and the parcel's value on the
parcel hover.

## 2. Household wealth

**What it is.** Savings per household, kept in a map from household id to
savings, beside the existing `Households` address book. When a household
moves (outage relocation, eviction, housing search) its savings go with it.
Households that leave the region take their savings with them.

**Monthly change.** Each household adds its monthly margin (earnings minus
rent, tax and costs, already computed by `household_accounts` for its
parcel). Negative margins draw savings down. A household's share of index
gains or losses and its dividends (step 5) and bond interest (step 4) are
added.

**Investing.** Households with savings above a few months of costs hold a
fraction of the excess in the market index; the fraction rises with wealth.
The rest stays as cash savings. Holdings are a paper value that rises and
falls with the index; buying in moves no money elsewhere.

**Spending down (builder's call, approved).** Each month a household spends
a small share of savings above its cushion, which is what feeds the shop
spending term below and keeps wealth from inflating without limit.

**What wealth changes.**
- **Staying power.** A household with savings covering its shortfall does
  not count a losing month toward the four that start a housing search.
- **Spending.** Shop and restaurant sales in `business_accounts` gain a term
  from the average wealth of households in nearby parcels.
- **Land value** gains a neighbour-wealth term (step 1).
- **Ward mood.** Council sentiment gains a term from recent change in ward
  wealth, so a slump is felt even before jobs are lost.
- **Newcomers.** Arriving households bring starting savings that rise with
  the market index's recent performance.

**Player view.** Average household savings and the share invested, by ward
in the council panel and citywide in the population panel; a wealth map
layer.

## 3. Funding levels

**What it is.** A level from 50% to 150% in steps of 10%, one per service
group: education, health, safety (fire and police), utilities (power, water,
sewer, waste), transit, and parks. Default 100%.

**What a level changes.**
- **Cost.** The group's facility upkeep and its running costs are
  multiplied by the level: for example bus operations for transit, and
  network upkeep and treatment for utilities. Fuel and imports are not
  scaled (builder's call, approved).
- **Output.** Staffing targets scale with the level, through the existing
  `facility_staff` / `facility_staffed` path: underfunding leaves posts
  unfilled, overfunding fills them faster and adds a small output bonus above
  full staffing (for example faster response, more school seats). The
  builder decides the exact bonus per group within that shape.
- **Land value** follows service quality, so underfunding lowers it.

**Player view.** A funding panel in the finance area with a slider per
group, its monthly cost, and a one-line note of what changes.

## 4. Debt

**Loans.** From a regional bank. Available at any rating above default.
Fixed amounts (the builder picks sensible steps), paid out immediately, fixed
monthly rate set by the rating at signing, repaid in equal monthly
instalments over a few years. Early repayment allowed.

**Bonds.** Larger amounts over a longer term at a rate set by the rating.
Sold to residents: each bond's buyers are the wealthier households, so the
bond's value comes out of household savings at issue, interest is paid into
their savings, and the principal returns to them at maturity. If residents'
investable savings cannot cover an issue, the remainder sells to outside
buyers at a higher rate. The bond market closes below a rating threshold.

**Credit rating.** AAA, AA, A, BBB, BB, B, CCC, D. Recomputed monthly from:
- debt outstanding against yearly revenue;
- debt service against monthly revenue;
- the last year's deficits;
- missed payments in the last two years.
The rating sets the rate on new loans and bonds and feeds market sentiment.

**Payments.** Debt service is charged in monthly settlement as an expense
line, after operating costs. Instruments are paid oldest first. If cash
cannot cover the whole month's service, the month counts as one missed
payment (however many instruments are unpaid), and the unpaid amount goes to
arrears. A partial payment counts as missed.

**Running out of cash (approved).** When settlement would leave cash below
zero, the bank covers the shortfall with an automatic emergency overdraft: a
loan at the highest current rate, repaid like any loan. A city that never
borrows therefore enters debt, and the same stages apply, when it runs out
of money. Cash never goes negative.

**Borrowing in trouble (builder's call, approved).** No new loans or bonds
while there are arrears. Being under the administrator counts as rating D.
The emergency overdraft still covers operating shortfalls in every stage.

**Failure stages** (the player's escalation):
1. **Credit penalties.** Any missed payment drops the rating at least one
   step, raises rates on new borrowing, and closes the bond market below BB.
   The HUD warns on the first miss.
2. **Forced cuts.** After three missed payments within twelve months, an
   administrator takes over: every funding level is capped at 70%, new
   construction the player pays for is blocked except demolition (private
   development, zoning growth and storefronts continue so the city can
   recover), and council sentiment takes a penalty. It ends when arrears are cleared and three consecutive payments
   are made.
3. **Insolvency.** If, under the administrator, arrears have not been
   cleared and are higher than they were twelve months earlier, the game ends with an insolvency screen summarising debt,
   rating history and the months that led there. The player can load a save
   or start over.

**Player view.** The finance panel lists loans and bonds (amount, rate,
remaining term, monthly payment), total debt service, the rating with its
reasons, the current stage and what triggers the next.

## 5. Stock market

**Listing.** A business parcel (zones 2 and 4, and live-work workshops)
lists after a run of profitable months and a minimum size. The **listing
incentive** is a policy the player switches on for a monthly cost; it
shortens the run and lowers the size needed. A listed company keeps its
identity while its business trades; it delists when the business closes,
the building is demolished, or the parcel is rezoned.

**Per company state.** Shares outstanding, last price, trailing earnings,
dividend, sector (retail, office, specialist office, workshop, processor,
manufacturer), and a price history long enough to chart (the builder picks
a length, at least 120 months).

**Price model** (monthly, deterministic):
- **Fundamentals.** Earnings come from the firm's existing monthly accounts
  (`business_accounts`). Fair value is earnings times a valuation multiple.
- **Multiple.** Falls when interest rates rise (the city's bond rate and a
  regional base rate from the business cycle), rises with market sentiment.
- **Sentiment** moves with: the regional business cycle (a slow seeded cycle
  of booms and recessions lasting years), city spending growth (lifts
  returns), city debt against revenue (drags returns), and momentum (recent
  index gains feed sentiment, which overshoots and later corrects).
- **Price.** Moves part of the way toward fair value each month plus a
  seeded shock. Shock size follows a volatility that clusters: calm and
  turbulent spells.
- **Dividends.** Paid only from positive monthly profit, after the margin
  that drives losing months and closure, to holders (households through the
  index).
- **Failure.** A firm that closes delists near zero and its holders lose
  that value.
- **Tax breaks.** The player sets a business tax break for listed firms
  (a percentage off the business tax rate). It raises their after-tax
  earnings and therefore their value, and costs business tax revenue.

**Index.** Value-weighted across listed firms, rebased to 100 at the first
listing.

**What the market changes.**
- **Household wealth** through holdings and dividends (step 2).
- **Business quality.** A rising index draws more and better-qualified firms:
  `open_specialists` and new-firm decisions get a bonus when the index has
  risen over the last year, and fewer firms open in a slump.
- **Elections.** At an election, each ward's support for the incumbent gains
  a term from the index's change over the term, alongside the existing
  happiness-based support.

**Strength in a passive city (approved).** The business cycle should be felt
like weather: noticeable booms and slumps every few years that shift wealth,
spending, new firms and elections, but small enough that a well-run city
that never borrows rides them out.
- **Land value** indirectly, through wealth.

**Player view.** A Markets panel with the index chart, a list of listed
companies (name, sector, price, change, market value), and selecting one
shows its price chart over time with its earnings and dividend. The
incentive and tax break controls sit in the same panel.

## Left to the builder

- All weights, rates, thresholds and curve shapes, within the shapes above,
  tuned so a default city plays roughly as it does today until the player
  borrows or changes funding.
- Exact layout of new panels and layers, following the existing finance and
  market panels.
- How household ids map to savings in storage, as long as savings follow
  the household.
- History lengths and save format details, with backward-compatible
  defaults.
- Which existing tests need their expected numbers updated because property
  tax and rent change, provided each change is explained in the commit.
