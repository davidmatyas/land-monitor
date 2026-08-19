from land_monitor.sreality import normalize_estate


def test_normalize_estate():
    estate = {
        "hash_id": 12345,
        "name": "Prodej pozemku 1200 m²",
        "locality": {"value": "Testov"},
        "gps": {"lat": 50.1, "lon": 14.4},
        "price": {"value_raw": 900000},
        "usable_area": 1200,
    }
    listing = normalize_estate(estate)
    assert listing.id == "12345"
    assert listing.price_czk == 900000
    assert listing.area_m2 == 1200
    assert listing.latitude == 50.1
    assert listing.longitude == 14.4
