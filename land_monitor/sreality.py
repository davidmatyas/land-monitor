from __future__ import annotations

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


def normalize_estate(estate: dict[str, Any]) -> Listing:
    hash_id = str(_first_value(estate, "hash_id", "id", "hashId") or "")
    title = str(_first_value(estate, "name", "advert_name", "title") or "")
    locality = estate.get("locality", {}) if isinstance(estate.get("locality"), dict) else {}
    gps = estate.get("gps", {}) if isinstance(estate.get("gps"), dict) else {}
    price = estate.get("price")
    if isinstance(price, dict):
        price = _first_value(price, "value_raw", "value")
    price = price if price is not None else _first_value(estate, "price_czk", "price_czk_value_raw")
    area = _first_value(estate, "usable_area", "area", "surface", "estate_area", "plot_area", "size")
    if isinstance(area, dict):
        area = _first_value(area, "value_raw", "value")
    latitude = _number(_first_value(gps, "lat", "latitude"))
    longitude = _number(_first_value(gps, "lon", "lng", "longitude"))
    url = _first_value(estate, "estate_url", "url")
    if url and str(url).startswith("/"):
        url = BASE_URL + str(url)
    if not url and hash_id:
        url = f"{BASE_URL}/detail/prodej/pozemek/{hash_id}"
    location = _first_value(locality, "value", "name", "city", "municipality")
    return Listing(
        id=hash_id,
        url=str(url or ""),
        title=title,
        price_czk=int(_number(price)) if _number(price) is not None else None,
        area_m2=_number(area),
        location=str(location) if location else None,
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
