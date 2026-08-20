"""CLI entry point for Land Monitor."""

from .filters import filter_listings
from .report import write_json
from .sreality import fetch_estates


def main() -> None:
    print("Land Monitor: collecting Sreality pages...")
    all_listings = []
    for page in range(1, 6):
        listings = fetch_estates(page=page)
        print(f"Page {page}: {len(listings)} listings")
        all_listings.extend(listings)
        if len(listings) < 60:
            break

    filtered = filter_listings(all_listings)
    path = write_json(filtered)
    print(f"Fetched {len(all_listings)} listings")
    print(f"Matching filters: {len(filtered)}")
    print(f"Report: {path}")


if __name__ == "__main__":
    main()
