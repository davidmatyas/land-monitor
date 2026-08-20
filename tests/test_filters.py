from land_monitor.filters import FilterConfig, matches
from land_monitor.models import Listing


def listing(**kwargs):
    values = dict(id="1", url="https://example.test", title="Pozemek", price_czk=800000,
                  price_per_m2_czk=800, area_m2=1000, location="Test", region_id=1,
                  region="Liberecký kraj", latitude=50.8, longitude=15.1, description=None)
    values.update(kwargs)
    return Listing(**values)


def test_matches_target_listing():
    assert matches(listing())


def test_rejects_large_total_price():
    assert not matches(listing(price_czk=1_000_001))


def test_rejects_small_area():
    assert not matches(listing(area_m2=999))


def test_rejects_wrong_region():
    assert not matches(listing(region="Jihomoravský kraj"))


def test_rejects_arable_land():
    assert not matches(listing(title="Prodej orné půdy 1500 m²"))


def test_rejects_forest():
    assert not matches(listing(title="Lesní pozemek 3000 m²"))
