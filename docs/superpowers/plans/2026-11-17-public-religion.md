# Public Religion Implementation Plan

**Goal** — Implement playable patronage, public worship, divine events, and election-driven rededication.

**Spec** — [Public religion](../specs/2026-11-17-public-religion.md)

**Architecture** — Keep religious state and daily simulation in Ur.Sim, reuse facilities and campus education, and let Ur.Council own political preferences and pending requests. Connect the civic toolbar and Details panel to those simulation commands.

## Work and verification

- [x] Pin dedication, temple prerequisites, grand-temple uniqueness, and offering odds in regression checks. Add temple tools and facilities, seminary credentials, local happiness, and save migration.
- [x] Pin festival and event timing across live days, bulk months, and save/load. Apply festival attendance, food consumption, sanitation, and temporary effects through their existing simulation paths.
- [x] Pin majority formation and both responses. Extend councillor relationships, election sentiment, ward requests and holds, and the separate rededication request.
- [x] Expose the religion panel, civic tools, staffing and costs, festival estimates, offering confirmation, council favorites, and rededication terms.
- [x] Run forge check, test, strict lint, and release build. Verify the ordinary player entry points.

## Review focus

- Dedication survives demolition and reload. The grand temple limit applies while closed.
- Confirmed divine outcomes persist across reloads and cannot be repeated across temples.
- Live and bulk dates process scheduled events once, including a partially elapsed month.
- An outstanding request coexists with ordinary ward business and refusal penalties attach only to its signatories.
- Existing saves load without a city patron and retain their current civic policy and facilities.
