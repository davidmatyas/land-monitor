from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class Listing:
    id: str
    url: str
    title: str
    price_czk: int | None
    price_per_m2_czk: int | None
    area_m2: float | None
    location: str | None
    region_id: int | None
    region: str | None
    latitude: float | None
    longitude: float | None
    description: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "price_czk": self.price_czk,
            "price_per_m2_czk": self.price_per_m2_czk,
            "area_m2": self.area_m2,
            "location": self.location,
            "region_id": self.region_id,
            "region": self.region,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "description": self.description,
        }
