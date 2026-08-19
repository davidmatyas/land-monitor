from __future__ import annotations

from .config import load_settings
from .db import connect, upsert_listing
from .filters import passes_basic_filters
from .collectors.sreality import iter_pages

# Temporary mapping. We will discover these IDs from Sreality metadata in the
# next step instead of hard-coding them permanently.
REGION_IDS = {
    "Stredocesky kraj": 11,
    "Ustecky kraj": 13,
    "Liberecky kraj": 14,
    "Plzensky kraj": 12,
}


def run() -> int:
    settings = load_settings()
    connection = connect()
    accepted = 0

    for region_name in settings["search"]["regions"]:
        region_id = REGION_IDS[region_name]
        for listing in iter_pages(region_id, max_pages=1):
            upsert_listing(connection, listing)
            if passes_basic_filters(listing, settings):
                accepted += 1
                print(
                    f"{listing.title} | {listing.price_czk} CZK | "
                    f"{listing.area_m2} m2 | {listing.url}"
                )

    print(f"Accepted listings: {accepted}")
    return accepted


if __name__ == "__main__":
    run()
