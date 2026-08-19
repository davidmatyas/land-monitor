# Land Monitor

Automated monitoring of land listings in the Czech Republic.

## Goal

Find land suitable for the long-term plan of placing a maringotka / tiny house, with good access to rail transport.

Initial target:

- Liberecky kraj
- Stredocesky kraj
- Plzensky kraj
- Ustecky kraj
- area: at least 1,000 m2
- total price: at most 1,000,000 CZK
- price: at most 1,000 CZK/m2
- rail station preferably within 3 km
- exclude obvious agricultural/forest land such as arable land and forest

The filters are configuration-driven and will evolve as we learn from real listings.

## Planned pipeline

1. Collect listings from supported real-estate portals.
2. Normalize and deduplicate listings.
3. Apply hard filters.
4. Calculate distance to the nearest railway station.
5. Store listing history and price changes.
6. Score listings into A / B / C categories.
7. Send only relevant new listings by email.
8. Later: cadastral data, zoning plans and AI-assisted evaluation.

## Status

Early MVP setup. No credentials or secrets belong in the repository.
