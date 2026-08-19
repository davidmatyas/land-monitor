from __future__ import annotations

from typing import Any

import requests

from .models import Listing

BASE_URL = "https://www.sreality.cz"
API_URL = f"{BASE_URL}/api/cs/v2/estates"


class SrealityError(RuntimeError):
    pass


def _number(value: Any) -> float | None:
    if value is None:
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
    # Sreality has changed field names between API versions, so keep
    # normalization deliberately defensive.
    hash_id = str(_first_value(estate, "hash_id", "id", "hashId") or "")
    title = str(_first_value(estate, "name", "title") or "")
    seo = estate.get("seo", {}) if isinstance(estate.get("seo"), dict) else {}
    locality = estate.get("locality", {}) if isinstance(estate.get("locality"), dict) else {}
    gps = estate.get("gps", {}) if isinstance(estate.get("gps"), dict) else {}
    price = estate.get("price", {}) if isinstance(estate.get("price"), dict) else {}

    url = _first_value(estate, "estate_url", "url")
    if not url and hash_id:
        slug = seo.get("locality") or locality.get("seo_name") or ""
        url = f"{BASE_URL}/detail/prodej/pozemek/{slug}/{hash_id}"

    area = _first_value(estate, "usable_area", "area", "surface")
    if area is None:
        area = _first_value(estate, "estate_area", "plot_area")

    price_value = _first_value(price, "value_raw", "value")
    if price_value is None:
        price_value = _first_value(estate, "price_czk", "price")

    latitude = _number(_first_value(gps, "lat", "latitude"))
    longitude = _number(_first_value(gps, "lon", "lng", "longitude"))
    area_number = _number(area)

    return Listing(
        id=hash_id,
        url=str(url or ""),
        title=title,
        price_czk=int(price_value) if price_value is not None and str(price_value).replace(".", "", 1).isdigit() else None,
        area_m2=area_number,
        location=str(_first_value(locality, "value", "name") or "") or None,
        latitude=latitude,
        longitude=longitude,
        description=_first_value(estate, "description", "text"),
    )


def fetch_estates(*, category: int = 19, locality_region_id: int | None = None,
                  page: int = 1, per_page: int = 60,
                  session: requests.Session | None = None) -> list[Listing]:
    params: dict[str, Any] = {
        "category_main_cb": category,
        "page": page,
        "per_page": per_page,
    }
    if locality_region_id is not None:
        params["locality_region_id"] = locality_region_id

    client = session or requests.Session()
    response = client.get(API_URL, params=params, timeout=30, headers={"User-Agent": "land-monitor/0.1"})
    if response.status_code >= 400:
        raise SrealityError(f"Sreality returned HTTP {response.status_code}")

    payload = response.json()
    estates = payload.get("_embedded", {}).get("estates", [])
    if not isinstance(estates, list):
        raise SrealityError("Unexpected Sreality response: estates is not a list")

    return [normalize_estate(item) for item in estates if isinstance(item, dict)]
