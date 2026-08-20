from __future__ import annotations

import re
from typing import Any

import requests

from .models import Listing

BASE_URL = "https://www.sreality.cz"
API_URL = f"{BASE_URL}/api/v1/estates/search"
LAND_CATEGORY = 3
SALE_TYPE = 1


class SrealityError(RuntimeError):
    pass


def _number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _first_value(item: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in item and item[key] not in (None, ""):
            return item[key]
    return None


def _nested_number(item: dict[str, Any], *keys: str) -> float | None:
    value = _first_value(item, *keys)
    if isinstance(value, dict):
        value = _first_value(value, "value_raw", "value")
    return _number(value)


def _area_from_title(title: str) -> float | None:
    # Search for a size written as e.g. "Prodej pozemku 1 632 m²" or "1632 m2".
    match = re.search(r"(?<!\d)(\d[\d\s.,]*)\s*m(?:²|2)\b", title, re.IGNORECASE)
    if not match:
        return None
    raw = re.sub(r"\s+", "", match.group(1)).replace(",", ".")
    try:
        return float(raw.replace(".", "", raw.count(".") - 1)) if raw.count(".") > 1 else float(raw)
    except ValueError:
        return None


def normalize_estate(estate: dict[str, Any]) -> Listing:
    hash_id = str(_first_value(estate, "hash_id", "id", "hashId") or "")
    title = str(_first_value(estate, "advert_name", "name", "title") or "")

    locality = estate.get("locality", {}) if isinstance(estate.get("locality"), dict) else {}
    gps = estate.get("gps", {}) if isinstance(estate.get("gps"), dict) else {}

    price = _nested_number(estate, "price_czk", "price_czk_value_raw", "price")
    price_per_m2 = _nested_number(estate, "price_czk_m2", "price_m2", "price_per_m2")

    area = _nested_number(
        estate,
        "estate_area",
        "land_area",
        "plot_area",
        "usable_area",
        "surface",
        "size",
    )
    if area is None:
        area = _area_from_title(title)

    latitude = _nested_number(locality, "gps_lat")
    longitude = _nested_number(locality, "gps_lon")
    if latitude is None:
        latitude = _nested_number(gps, "lat", "latitude")
    if longitude is None:
        longitude = _nested_number(gps, "lon", "lng", "longitude")

    city = _first_value(locality, "city", "municipality")
    citypart = _first_value(locality, "citypart")
    location = " - ".join(str(x) for x in (city, citypart) if x)

    region_id = _number(_first_value(locality, "region_id"))
    region = _first_value(locality, "region", "region_name")

    url = _first_value(estate, "estate_url", "url")
    if url and str(url).startswith("/"):
        url = BASE_URL + str(url)
    if not url and hash_id:
        url = f"{BASE_URL}/detail/prodej/pozemek/{hash_id}"

    return Listing(
        id=hash_id,
        url=str(url or ""),
        title=title,
        price_czk=int(price) if price is not None else None,
        price_per_m2_czk=int(price_per_m2) if price_per_m2 is not None else None,
        area_m2=area,
        location=location or None,
        region_id=int(region_id) if region_id is not None else None,
        region=str(region) if region else None,
        latitude=latitude,
        longitude=longitude,
        description=_first_value(estate, "description", "text"),
    )


def fetch_estates(*, category: int = LAND_CATEGORY, transaction_type: int = SALE_TYPE,
                  locality_region_id: int | None = None, page: int = 1, per_page: int = 60,
                  session: requests.Session | None = None) -> list[Listing]:
    page_size = min(per_page, 1000)
    params: dict[str, Any] = {
        "category_main_cb": category,
        "category_type_cb": transaction_type,
        "limit": page_size,
        "offset": max(page - 1, 0) * page_size,
        "lang": "cs",
    }
    if locality_region_id is not None:
        params["locality_region_id"] = locality_region_id

    client = session or requests.Session()
    response = client.get(API_URL, params=params, timeout=30, headers={
        "User-Agent": "Mozilla/5.0 (compatible; LandMonitor/0.1)",
        "Accept": "application/json",
        "Accept-Language": "cs,en;q=0.9",
    })
    if response.status_code >= 400:
        raise SrealityError(f"Sreality returned HTTP {response.status_code}: {response.url}")

    payload = response.json()
    estates = payload.get("results", [])
    if not isinstance(estates, list):
        raise SrealityError("Unexpected Sreality response: results is not a list")
    return [normalize_estate(item) for item in estates if isinstance(item, dict)]
