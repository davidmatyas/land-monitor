from __future__ import annotations

from dataclasses import dataclass

from .models import Listing

TARGET_REGIONS = {"Liberecký kraj", "Středočeský kraj", "Plzeňský kraj", "Ústecký kraj"}
# Use phrases rather than the bare word "les", which would also match
# unrelated Czech words containing that character sequence.
EXCLUDED_PHRASES = ("orná půda", "lesní pozemek", "lesní půda", "les")


@dataclass(frozen=True, slots=True)
class FilterConfig:
    min_area_m2: float = 1000
    max_price_czk: int = 1_000_000
    max_price_per_m2_czk: int = 1000


def matches(listing: Listing, config: FilterConfig = FilterConfig()) -> bool:
    # A missing region cannot be considered a match because the requested
    # search is explicitly limited to four regions.
    if listing.region not in TARGET_REGIONS:
        return False
    if listing.area_m2 is None or listing.area_m2 < config.min_area_m2:
        return False
    if listing.price_czk is None or listing.price_czk > config.max_price_czk:
        return False
    if listing.price_per_m2_czk is not None and listing.price_per_m2_czk > config.max_price_per_m2_czk:
        return False

    text = " ".join(x for x in (listing.title, listing.description) if x).casefold()
    return not any(phrase in text for phrase in EXCLUDED_PHRASES)


def filter_listings(listings: list[Listing], config: FilterConfig = FilterConfig()) -> list[Listing]:
    return [listing for listing in listings if matches(listing, config)]
