from __future__ import annotations

from typing import Any, Iterator

import requests

from ..models import Listing

BASE_URL = "https://www.sreality.cz/api/cs/v2/estates"


def _first_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _first_int(value: Any) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _extract_coordinates(estate: dict[str, Any]) -> tuple[float | None, float | None]:
    coords = estate.get("map") or {}
    return _first_float(coords.get("lat")), _first_float(coords.get("lon"))


def _extract_area(estate: dict[str, Any]) -> float | None:
    # Sreality search results expose the area in several versions of the API.
    for key in ("surface", "area"):
        value = _first_float(estate.get(key))
        if value is not None:
            return value

    name = str(estate.get("name") or "")
    # Deliberately do not parse arbitrary numbers from the title. Detail
    # responses will be used later for robust area extraction.
    return None


def _to_listing(estate: dict[str, Any]) -> Listing:
    listing_id = str(estate.get("hash_id"))
    return Listing(
        source="sreality",
        listing_id=listing_id,
        title=str(estate.get("name") or ""),
        url=f"https://www.sreality.cz/detail/{listing_id}",
        locality=estate.get("locality"),
        region=estate.get("locality_region"),
        price_czk=_first_int(estate.get("price")),
        area_m2=_extract_area(estate),
        latitude=_extract_coordinates(estate)[0],
        longitude=_extract_coordinates(estate)[1],
    )


def fetch_page(
    region_id: int,
    page: int = 1,
    per_page: int = 60,
    session: requests.Session | None = None,
) -> list[Listing]:
    params = {
        "category_main_cb": 3,  # Pozemky
        "category_type_cb": 1,  # Prodej
        "locality_region_id": region_id,
        "page": page,
        "per_page": per_page,
    }
    client = session or requests.Session()
    response = client.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    estates = data.get("_embedded", {}).get("estates", [])
    return [_to_listing(estate) for estate in estates]


def iter_pages(region_id: int, max_pages: int = 1) -> Iterator[Listing]:
    with requests.Session() as session:
        for page in range(1, max_pages + 1):
            yield from fetch_page(region_id, page=page, session=session)
