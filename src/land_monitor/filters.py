from .models import Listing


def passes_basic_filters(listing: Listing, settings: dict) -> bool:
    search = settings["search"]

    if listing.area_m2 is None or listing.area_m2 < search["min_area_m2"]:
        return False
    if listing.price_czk is None or listing.price_czk > search["max_price_czk"]:
        return False

    price_per_m2 = listing.price_per_m2
    if price_per_m2 is None or price_per_m2 > search["max_price_per_m2_czk"]:
        return False

    regions = set(search["regions"])
    if listing.region and listing.region not in regions:
        return False

    return True
