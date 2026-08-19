from __future__ import annotations

from typing import Any

import requests

from .models import Listing

BASE_URL = "https://www.sreality.cz"
API_URL = f"{BASE_URL}/api/cs/v2/estates"
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
        value = _first_value(value, "value_raw", "value", "lat", "lon", "latitude", "longitude")
    return _number(value)


def normalize_estate(estate: dict[str, Any]) -> Listing:
    hash_id = str(_first_value(estate, "hash_id", "id", "hashId") or "")
    title = str(_first_value(estate, "name", "advert_name", "title") or "")

    locality = estate.get("locality", {}) if isinstance(estate.get("locality"), dict) else {}
    gps = estate.get("gps", {}) if isinstance(estate.get("gps"), dict) else {}
    map_data = estate.get("map", {}) if isinstance(estate.get("map"), dict) else {}
    price = estate.get("price")
    if isinstance(price, dict):
        price = _first_value(price, "value_raw", "value")
    if price is None:
        price = _first_value(estate, "price_czk", "price_czk_value_raw")

    area = _first_value(estate, "usable_area", "area", "surface", "estate_area", "plot_area")
    if isinstance(area, dict):
        area = _first_value(area, "value_raw", "value")

    latitude = _nested_number(gps, "lat", "latitude") or _nested_number(map_data, "lat", "latitude")
    longitude = _nested_number(gps, "lon", "lng", "longitude") or _nested_number(map_data, "lon", "lng", "longitude")

    url = _first_value(estate, "estate_url", "url")
    links = estate.get("_links", {}) if isinstance(estate.get("_links"), dict) else {}
    self_link = links.get("self", {}) if isinstance(links.get("self"), dict) else {}
    url = url or self_link.get("href")
    if url and str(url).startswith("/"):
        url = BASE_URL + str(url)
    if not url and hash_id:
        url = f"{BASE_URL}/detail/prodej/pozemek/{hash_id}"

    location = _first_value(locality, "value", "name", "city", "municipality")
    if not location:
        location = ", ".join(str(locality[k]) for k in ("city", "citypart", "district") if locality.get(k)) or None

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
    params: dict[str, Any] = {
        "category_main_cb": category,
        "category_type_cb": transaction_type,
        "page": page,
        "per_page": per_page,
    }
    if locality_region_id is not None:
        params["locality_region_id"] = locality_region_id

    client = session or requests.Session()
    response = client.get(
        API_URL,
        params=params,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; LandMonitor/0.1)",
            "Accept": "application/json",
            "Accept-Language": "cs,en;q=0.9",
        },
    )
    if response.status_code >= 400:
        raise SrealityError(f"Sreality returned HTTP {response.status_code}: {response.url}")

    payload = response.json()
    estates = payload.get("_embedded", {}).get("estates", [])
    if not isinstance(estates, list):
        estates = payload.get("results", [])
    if not isinstance(estates, list):
        raise SrealityError("Unexpected Sreality response: estates is not a list")

    return [normalize_estate(item) for item in estates if isinstance(item, dict)]
