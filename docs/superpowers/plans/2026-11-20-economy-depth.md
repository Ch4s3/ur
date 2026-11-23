# Economy Depth Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add land value, household wealth, service funding levels, debt with a three-stage failure path, and a per-company stock market to Ur.

**Architecture:** All state lives on `Ur.Sim.City` and is updated in `settle_month`. The per-place quantities (land value, household savings) are per-parcel `NativeIntArr` like the rest of the simulation; debts and stocks are lists of small records. The market and debt maths go in two new modules so `sim.march` does not grow further. Player controls go through one entry point, `Ur.Sim.adjust_economy(c, row, delta)`, which the HUD reaches through `Ur.Hud.economy_at`.

**Tech Stack:** March, forge, Strata UI (`lib/ur/hud.march`), JSON saves (`lib/ur/save.march`).

**Spec:** `docs/superpowers/specs/2026-11-20-economy-depth-design.md`

## Global Constraints

- Deterministic: randomness only from `hash(climate_seed, month, id)` style functions, no advancing random state.
- Saves from before this change load, with defaults for every new field.
- A default city that never borrows or changes funding plays roughly as today; property tax at default rate is within 10% of today's `people * 2 / 3` on the default map.
- Cash never goes negative after settlement (the emergency overdraft covers it).
- Every suite passes when run on its own with `forge test test/<name>_test.march`, and `forge lint --strict` is clean.
- Monthly settlement time on `UR_BENCH=100` grows by no more than 25%.

## Review Focus

1. A save from before the change: loads, all new fields default, the next month settles without negative cash. Test in Task 1 (land value defaults) and Task 4 (debt fields).
2. A city that never borrows and runs a deficit: it gets an overdraft, not negative cash, and the warning appears. Test in Task 4.
3. Several loans in one bad month count as one missed payment, not three. Test in Task 4.
4. A listed firm whose building burns, closes or is rezoned delists and its holders lose value; no stock points at an empty parcel. Test in Task 5.
5. Funding at 50% across every group does not zero out a city's power or water entirely (staffing falls, output falls proportionally, not to nothing). Test in Task 3.

---

### Task 1: Land value

**Files:**
- Create: `lib/ur/land.march` (module `Ur.Land`)
- Modify: `lib/ur/sim.march` (City fields, `settle_month`, `budget`, `housing_rent`, business rent in `business_accounts`, `property_bill`, `adjust_policy` row 4 stays energy, new row 10 property rate)
- Modify: `lib/ur/save.march`, `lib/ur/hud.march` (parcel hover line, policy row, map layer), `lib/ur/layers.march`
- Test: `test/land_value_test.march`

**Interfaces:**
- Produces: `City.land_value : NativeIntArr` (dollars per parcel, 0 to 4000), `City.property_rate : Int` (tenths of a percent per year; default chosen to satisfy the Global Constraint), `Ur.Land.target(c : City, st : Stats, lot : Int) : Int`, `Ur.Land.update(c : City, st : Stats) : NativeIntArr` (moves each parcel a quarter of the way to its target), `Ur.Sim.property_tax_at(c : City, lot : Int) : Int` (monthly tax for an occupied built parcel, 0 otherwise), `Ur.Sim.adjust_policy` row 10 changes `property_rate` by 1 within 0..40.
- Rent: `housing_rent` and business rent add `property_tax_at` per dwelling or premises (pass-through).
- `property_bill` uses `land_value * property_rate` instead of `buildings * 4`.

- [ ] **Step 1: Write `test/land_value_test.march`** with assertions:
  - `Ur.Land.target` is higher for a parcel beside a park than the same parcel beside a gas plant.
  - `Ur.Land.target` is higher with a school and clinic in range than without.
  - After `Ur.Clock.advance(c, 1)`, `land_value` moves toward the target but not all the way.
  - Total `budget.property_tax` on `S.new()` is within 10% of `S.population(c) * 2 / 3`.
  - Raising `property_rate` raises `household_accounts(...).rent` on an occupied parcel.
  - An undeveloped zoned parcel has `land_value > 0` and `property_tax_at == 0`.
  - Save round-trip keeps `land_value` and `property_rate`; decoding a save without them yields the defaults.
- [ ] **Step 2: Run it, expect compile failure** (`Ur.Land` undefined).
- [ ] **Step 3: Implement** the fields, `Ur.Land`, the budget, rent and property bill changes, the policy row, hover line ("Land value $N"), and a land value layer (next free layer id).
- [ ] **Step 4: Run** `forge test test/land_value_test.march`, then every suite; update expected numbers that move only because property tax or rent changed, with a comment saying so.
- [ ] **Step 5: Commit** "Value land per parcel and tax it through rent".

### Task 2: Household wealth

**Files:**
- Create: `lib/ur/wealth.march` (module `Ur.Wealth`)
- Modify: `lib/ur/sim.march` (`settle_month`, `move_from_homes`, `place_households`, `HomeMoves`, `business_accounts` spending term, `advance_population` newcomer savings), `lib/ur/land.march` (neighbour wealth term), `lib/ur/council.march` (ward wealth change in `sentiment`), `lib/ur/save.march`, `lib/ur/hud.march` (population panel line, council ward line, wealth layer)
- Test: `test/household_wealth_test.march`

**Interfaces:**
- Consumes: `property_tax_at` (via rent in `household_accounts`).
- Produces: `City.savings : NativeIntArr` (total savings of the households on each parcel), `City.wealth_history : List(Int)` (citywide average per household, 24 months), `Ur.Wealth.per_home(c : City, lot : Int) : Int`, `Ur.Wealth.cushion(c : City, routes, commutes, labor, lot) : Int` (three months of the parcel's costs per home), `Ur.Wealth.invested_share(per_home : Int, cushion : Int) : Int` (percent, 0 when below the cushion, rising to 60), `Ur.Wealth.settle(c : City, routes, commutes, labor : Labor, index_return : Int) : City` where `index_return` is the market's monthly return in tenths of a percent (0 until Task 5).
- Moves: when `place_households` moves `n` households from `origin`, it moves `n * savings[origin] / occupied(origin)` with them; departures from the region remove theirs.
- Staying power: in `move_from_homes`, a losing month does not add to the streak when `per_home >= -home_offer`.
- Spending: `business_accounts` sales for shops gain `clamp(nearby_wealth / 400, 0, 8)`.

- [ ] **Step 1: Write `test/household_wealth_test.march`**: positive margins raise savings after a month; negative margins draw them down but not below zero; a household with savings above its shortfall keeps its streak at 0; moving households carry savings (sum of savings is conserved across a relocation except departures); `invested_share` is 0 below the cushion; save round-trip keeps `savings`.
- [ ] **Step 2: Run, expect failure.**
- [ ] **Step 3: Implement.** Spend-down: each month a parcel's households spend 2% of savings above their cushion.
- [ ] **Step 4: Run** the suite, then all suites.
- [ ] **Step 5: Commit** "Give households savings that follow them".

### Task 3: Funding levels

**Files:**
- Modify: `lib/ur/sim.march` (`City.funding`, `facility_staffed` target, upkeep in the `sum(..., 2, ...)` path and `budget` running cost lines, `adjust_economy`), `lib/ur/save.march`, `lib/ur/hud.march` (Funding page), `lib/ur.march` (page switching and clicks)
- Test: `test/funding_test.march`

**Interfaces:**
- Produces: `City.funding : NativeIntArr` (6 cells, percent 50..150, default 100), `Ur.Sim.service_group(kind : Int) : Int` (0 education, 1 health, 2 safety, 3 utilities, 4 transit, 5 parks; -1 none), `Ur.Sim.funding_level(c : City, group : Int) : Int`, `Ur.Sim.funded_positions(c : City, lot : Int) : Int` (positions scaled by level, at least 1 for a staffed kind), `Ur.Sim.adjust_economy(c : City, row : Int, delta : Int) : City` with rows 0..5 changing funding by 10 within 50..150 (later tasks add rows), `Ur.Hud.economy_at(mx, my, w, h, tab) : (Int, Int)`, sidebar tabs 17 (Funding), 18 (Debt), 19 (Stocks) opened from buttons on the Finance tab (4).
- Cost: group upkeep and running costs (transit: `bus_operations`; utilities: `utility_upkeep` network upkeep and treatment) times the level; fuel and imports unscaled.
- Above 100%: staffing reaches full sooner and, for education, school seats rise by `(level - 100) / 5` percent.

- [ ] **Step 1: Write `test/funding_test.march`**: `funding_level` defaults to 100 and survives save; education at 50% halves education upkeep in `budget` and lowers `facility_staffed` of a fully staffed school; transit at 150% raises `bus_operations` by half; every group at 50% leaves `stats.services` power above zero on `S.new()`; `adjust_economy` clamps at 50 and 150.
- [ ] **Step 2: Run, expect failure.**
- [ ] **Step 3: Implement**, including the Funding page (one row per group: name, level, monthly cost, minus/plus).
- [ ] **Step 4: Run** the suite, then all suites.
- [ ] **Step 5: Commit** "Fund services between half and one and a half times".

### Task 4: Debt

**Files:**
- Create: `lib/ur/debt.march` (module `Ur.Debt`)
- Modify: `lib/ur/sim.march` (City fields, `settle_month` after `budget`, construction blocking in `apply_tool`), `lib/ur/council.march` (administrator sentiment penalty), `lib/ur/save.march`, `lib/ur/hud.march` (Debt page, warnings), `lib/ur.march` (insolvency end screen via the existing menu path)
- Test: `test/debt_test.march`

**Interfaces:**
- Produces:
  - `type Ur.Sim.Debt = { id : Int, kind : Int, principal : Int, rate : Int, months : Int, resident : Int }` (kind 0 loan, 1 bond, 2 overdraft; `rate` in tenths of a percent per year; `months` remaining; `resident` = amount of a bond held by residents).
  - `City.debts : List(Debt)`, `City.arrears : Int`, `City.missed : List(Int)` (months with a missed payment), `City.administrator : Int` (month it began, -1 none), `City.insolvent : Bool`, `City.debt_history : List(NativeIntArr)` (24 months: month, debt, arrears, rating).
  - `Ur.Debt.rating(c : City) : Int` (0 AAA .. 7 D), `Ur.Debt.rating_name(r : Int) : String`, `Ur.Debt.rate_for(rating : Int, kind : Int) : Int`, `Ur.Debt.payment(d : Debt) : Int` (level instalment), `Ur.Debt.borrow(c : City, kind : Int, amount : Int) : City` (refused with a message in arrears, under the administrator, or for bonds below BB), `Ur.Debt.settle(c : City, net : Int) : City` (pays oldest first, records at most one miss per month, adds an overdraft when cash would go negative, advances stages), `Ur.Debt.stage(c : City) : Int` (0 fine, 1 penalties, 2 administrator, 3 insolvent).
  - `adjust_economy` rows 10..13: borrow loan steps of $5,000 / $20,000, issue bond $50,000, repay the oldest loan early; row 14 cycles bond size.
  - Bonds: resident share comes out of `savings` of the wealthiest parcels up to their invested amount; interest on it is paid into those savings monthly, principal at maturity.
- Stages exactly as the spec: stage 2 after three missed months within twelve; capped funding at 70% and player construction blocked except demolition; ends after arrears cleared and three paid months; stage 3 when arrears are uncleared and higher than twelve months earlier.

- [ ] **Step 1: Write `test/debt_test.march`**: borrowing a loan adds cash and a monthly payment; a city at cash 0 with a deficit ends the month with cash ≥ 0 and an overdraft; three loans unpaid in one month record one miss; rating falls after a miss and rates for new debt rise; three misses in twelve months start the administrator, cap funding at 70 and refuse a paid tool but allow demolition; clearing arrears and paying three months ends it; uncleared growing arrears for twelve months under the administrator set `insolvent`; a bond moves resident savings and pays interest back; old save without debt fields decodes with no debts and stage 0.
- [ ] **Step 2: Run, expect failure.**
- [ ] **Step 3: Implement**, including the Debt page (instruments, payment, rating and its reasons, stage and next trigger, borrow buttons) and the insolvency screen.
- [ ] **Step 4: Run** the suite, then all suites.
- [ ] **Step 5: Commit** "Borrow through loans and bonds, with credit and insolvency".

### Task 5: Stock market

**Files:**
- Create: `lib/ur/market.march` (module `Ur.Market`)
- Modify: `lib/ur/sim.march` (City fields, `settle_month`, business tax break in `business_receipts`, `open_specialists` bonus), `lib/ur/wealth.march` (index return and dividends), `lib/ur/council.march` (index term in `retention_odds`), `lib/ur/save.march`, `lib/ur/hud.march` (Stocks page with index chart, company list and selected stock chart), `lib/ur.march` (stock selection in `FinanceView`)
- Test: `test/stock_market_test.march`

**Interfaces:**
- Produces:
  - `type Ur.Sim.Stock = { id : Int, lot : Int, sector : Int, shares : Int, price : Int, earnings : Int, dividend : Int, history : List(Int), listed : Int, delisted : Int }` (price in cents; history newest first, 120 months; `delisted` month or -1; delisted stocks kept 24 months for charts).
  - `type Ur.Sim.MarketState = { index : Int, sentiment : Int, volatility : Int, history : List(Int), base : Int, next_id : Int }` (index ×100, sentiment and volatility in tenths of a percent).
  - `City.stocks : List(Stock)`, `City.market : MarketState`, `City.listing_incentive : Bool`, `City.listed_tax_break : Int` (percent off business tax for listed firms, 0..50).
  - `Ur.Market.cycle(c : City) : Int` (regional cycle, −100..100, seeded, period 60 to 120 months), `Ur.Market.noise(c : City, id : Int) : Int` (seeded shock), `Ur.Market.fair_value(earnings : Int, multiple : Int) : Int`, `Ur.Market.multiple(c : City) : Int`, `Ur.Market.settle(c : City, accounts_for : Int -> Accounts, spending_growth : Int, debt_ratio : Int) : City` (lists, prices, delists, recomputes index), `Ur.Market.monthly_return(c : City) : Int`, `Ur.Market.stock_at(c : City, id : Int) : Option(Stock)`.
  - `adjust_economy` row 20 toggles the listing incentive, row 21 changes the tax break by 5.
  - `FinanceView` gains `stock : Int` (selected stock id, -1 none).
- Price each month: `price += (fair - price) * 15% + price * shock`, where `shock = noise * volatility`; volatility moves toward 4% in calm and 12% in turbulent spells, switching when the cycle turns or the index falls 10% in three months; sentiment = cycle term + spending growth term − debt ratio term + momentum (last 3 months' index change) term, mean reverting; multiple = 12 + sentiment / 10 − (bond rate − 4%) × 1.5, clamped 4..30.
- Listing: business parcel with 12 profitable months and at least 12 jobs (6 months and 8 jobs with the incentive, which costs $200 a month).
- Effects: households' invested savings change by `monthly_return`; dividends are 40% of positive profit, credited to savings citywide by invested share; `open_specialists` and firm opening get a bonus when the index rose over 12 months; `retention_odds` adds `clamp(index change over term / 5, -8, 8)`.

- [ ] **Step 1: Write `test/stock_market_test.march`**: the same city advanced twice gives identical index histories (determinism); a profitable firm lists after 12 months, sooner with the incentive; a listed firm whose building is demolished delists with a near-zero last price; raising the city's debt ratio lowers `multiple`; raising `listed_tax_break` raises a listed firm's after-tax earnings and lowers business tax revenue; `retention_odds` is higher after an index rise than a fall, all else equal; a stock's `history` grows by one per month up to 120; save round-trip keeps stocks and market.
- [ ] **Step 2: Run, expect failure.**
- [ ] **Step 3: Implement**, including the Stocks page: index chart across the top, company list (name, sector, price, change, value) and a chart of the selected company's price history below, using the existing `segment`/`line_mark` helpers.
- [ ] **Step 4: Run** the suite, then all suites and `forge lint --strict`; time `UR_BENCH=100` against the pre-change commit.
- [ ] **Step 5: Commit** "List local companies on a stock market"; update README sections for all five systems in this commit.
