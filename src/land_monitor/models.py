from dataclasses import dataclass


@dataclass(frozen=True)
class Listing:
    source: str
    listing_id: str
    title: str
    url: str
    locality: str | None
    region: str | None
    price_czk: int | None
    area_m2: float | None
    latitude: float | None
    longitude: float | None

    @property
    def price_per_m2(self) -> float | None:
        if self.price_czk is None or self.area_m2 is None or self.area_m2 <= 0:
            return None
        return self.price_czk / self.area_m2
