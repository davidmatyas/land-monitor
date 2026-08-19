"""CLI entry point for the first live Sreality collector."""

from .report import write_json
from .sreality import fetch_estates


def main() -> None:
    print("Land Monitor: fetching first Sreality page...")
    listings = fetch_estates()
    path = write_json(listings)
    print(f"Fetched {len(listings)} listings")
    print(f"Report: {path}")


if __name__ == "__main__":
    main()
