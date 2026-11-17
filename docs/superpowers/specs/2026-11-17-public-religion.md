# Public religion in Ur

Public religion gives the city a way to improve neighborhood happiness, celebrate holidays, and take calculated risks for temporary economic benefits. The city supports one patron at a time. Its choice matters to both residents and the elected councillors who represent them.

## Design approach

One citywide patron gives temple placement, offerings, and council elections a shared consequence. A permanent founding choice would give the city a strong identity at the cost of losing the political choice to rededicate. Ward-level patrons would let districts pursue different benefits at the cost of making patronage and temple coverage harder to read. The design uses a single patron with costly rededication. Religion is optional for city growth. Its scope is public worship, neighborhood access, and councillor preferences.

## The five patrons

The first shrine dedicates the city to a patron. Show each deity’s domain, favor, curse, and current council supporters before confirming. All public shrines and temples serve that patron. Demolishing the last site leaves the dedication in effect.

| Patron | Domain | Favor | Curse |
| --- | --- | --- | --- |
| **Idra** | Rivers and rain | Refill rain collectors and improve farm yields for 30 days. | **Unending Rain.** Heavy rain lasts 30 days, increasing runoff and the risk of flooding. |
| **Saren** | Sun and harvest | Increase farm output for 30 days. | **Scorching Sun.** A heat wave dries soil and increases electricity demand. |
| **Tarek** | Stone and building | Speed construction and repairs for 30 days. | **Earthquake.** A localized shock damages buildings and roads. |
| **Namar, Keeper of the Harbor** | Sea, fishing, and trade | Increase catches and cargo capacity per trip for 30 days. | **King Tide.** Three days of high tides flood exposed coastal roads and disrupt ferries. Seawalls can protect exposed routes. |
| **Ishara, Guardian of the Hearth** | Health, households, and healing | Increase clinic throughput and reduce illness-related absences for 30 days. | **The Fever.** A two-week surge in illness strains clinics and keeps workers home. Neighborhoods with good clinic access recover sooner. |

## Temples and seminary

Unlock the tiers in order. Each step increases construction cost, monthly upkeep, the local happiness bonus, and the number of people the site can serve. Use the existing walking network to determine reach. A household receives the strongest passive bonus from an operating site it can reach, so overlapping sites mainly help with festival capacity.

| Tier | Staffing | What it adds |
| --- | --- | --- |
| **Shrine** | One attendant with a high-school education | Low-upkeep neighborhood happiness and a small festival site. |
| **Temple** | One college-educated priest | Broader walkable coverage and larger celebrations. |
| **Large Temple** | Two college-educated priests | Greater coverage and capacity, plus the ability to accept offerings for favor. |
| **Grand Temple** | Four seminary-trained clergy | The strongest local bonus and largest festival capacity. Only one may exist across the city, including while closed. |

The **Seminary** is a university specialization that trains qualified clergy through the existing education and hiring systems. Each tier needs a full qualified staff to operate. An understaffed site retains its monthly upkeep and suspends happiness service, festivals, and any petitions. The building inspector shows staffing and the reason for closure. The Religion map layer shows homes with and without walkable worship coverage. Site markers distinguish operating sites, staffing closures, and other closures.

## Festivals and public policy

Start with four annual festival dates, one per season. All four tiers can host while operating. The city policy determines how many eligible sites host on each date. Favor sites that extend attendance to more households and respect each site’s walking access and capacity. Assign each attending household to one host per date.

| Festival policy | Effect |
| --- | --- |
| **Local Observance** | A limited number of sites host smaller celebrations. |
| **Public Holidays** | More sites host, with broader attendance and greater demands on local services. |
| **Suspend Festivals** | Cancel upcoming celebrations until the policy changes. Operating sites continue to provide passive happiness. |

Attending residents take one day off regular work. Essential services continue operating. Festivals consume extra food from local supply and add trash at their sites for the existing collection system. A well-supplied event gives attendees a short happiness boost. Food shortages weaken that boost, and excess trash follows the normal overflow rules. Display the next date, the participating sites, and estimated food, waste, and work impacts before the holiday.

## Offerings and divine favor

At an operating Large or Grand Temple, the player can pick an offering tier. The confirmation shows the fee, all three odds, the possible favor and curse, and any restrictions. Pay on confirmation and resolve one outcome: favor, silence, or curse. Silence consumes the offering. A shared citywide cooldown applies after every result and prevents chaining rolls across temples. Paid petitions are unavailable during reconsecration or while a divine effect is active.

| Offering | Relative cost | Favor | Silence | Curse |
| --- | --- | ---: | ---: | ---: |
| Modest | Low | 30% | 60% | 10% |
| Generous | Medium | 50% | 42% | 8% |
| Lavish | High | 70% | 25% | 5% |

Each shrine closed for staffing adds 3 percentage points to the citywide curse chance, up to 15 points. Subtract the increase from silence and keep the favor chance steady. Count shrines that would otherwise be ready to open. Show this adjustment in the offering panel and apply it to the roll.

The council can limit petitions to modest offerings, allow all tiers within a public budget, or suspend them. When a curse causes disruption, affected wards can request recovery based on local conditions. A councillor can also sponsor a temporary hold on petitions with a measurable recovery target. These rules use the existing agenda and hold mechanics.

Use the existing weather, flooding, food, freight, and service systems where they cover an event. Apply weather overrides to both the simulation and forecast. Earthquakes need a localized damage event. King Tide needs a temporary coastal flood input and ferry disruption. The Fever needs temporary illness and work-absence effects tied to clinic access. The activity log records who invoked each event, what it does, where it applies, and when it ends.

## Council relations and elections

Each councillor has a public favorite deity that stays fixed for their tenure. A match with the city patron gives that councillor a standing relationship bonus, improving cooperation through the existing council rules. Councillors still respond to serious ward problems and can request changes to temple coverage or festival policy when their ward’s experience warrants it.

Elections replace councillors and can change the balance of favorites. Give incoming councillors preferences shaped by their ward and a shared citywide shift so that majorities can form even on a large council. Keep the assignment deterministic for a given election result. Religious effects on voters enter through ward happiness. Average the direct happiness contribution of temple access and festivals over the final months of the term so one holiday has limited influence. The local consequences of favors and curses also feed into normal ward conditions, such as food affordability or flood disruption.

### Rededication requests

After an election, if the city has a patron and reconsecration is idle, open a rededication request if more than half of all seated councillors favor the same deity and that deity differs from the current patron. A tie, a plurality, or a majority for the current patron leaves the existing dedication in place. The supporting majority signs the request and supplies the council approval for the switch. Keep this request separate from ordinary ward business so recovery demands can proceed while it is pending. Allow one formal request per council term.

The council panel shows the requested patron, the signatories, the reconsecration fee, the closure duration, the outgoing patron’s wrath risk, and the response deadline. The fee increases with the number and tier of existing sites. Show when the treasury can afford acceptance and allow the player to leave the request pending while raising money. An unanswered request counts as a decline at the next election, before the new council takes office.

- **Accept.** Charge the fee once and temporarily close all sites for reconsecration. Roll once for wrath from the outgoing patron, using that deity’s curse. At the end of the closure, the sites reopen under the new patron as staffing and access allow. Apply the new alignment bonuses at that point. A curse already in progress runs to its scheduled end.
- **Decline.** Keep the patron. Each signatory receives a permanent, non-stacking relationship penalty for the rest of that councillor’s tenure. Ordinary relationship gains from serving their ward still apply. The penalty belongs to the signatory and leaves office with them.

For example, a city dedicated to Namar elects a council with a majority for Ishara. Keeping Namar preserves the city’s access to his fishing and trade favor, at a lasting cost to relations with the signatories. Accepting buys cooperation with the new majority but risks a king tide during the transition.

## Playtest targets and save behavior

The four festival dates, offering odds, and event durations above are starting values. Tune site costs, coverage and capacity, food and trash loads, the citywide cooldown, the rededication fee and closure length, the wrath chance, and the size of both relationship modifiers. A city should feel the difference between local observances and public holidays. Maintaining a preferred patron through an unfriendly council should remain viable when the player serves wards well.

Save the dedication, festival policy, petition cooldown and roll state, active effects and end dates, any reconsecration in progress, councillor favorites and refusal penalties, and the term’s request status. Reloading after a confirmed offering or rededication must preserve the committed outcome. Existing saves begin without a dedicated patron.

Check that live day advancement and bulk month advancement each process festival dates and effect expirations exactly once. Exercise an election that changes the council majority, then verify both responses, including a wrath outcome on acceptance and the removal of a refusal penalty when its councillor loses office.
