from land_monitor.sreality import normalize_estate


def test_normalize_estate_v1_shape():
    estate = {
        "hash_id": 12345,
        "advert_name": "Prodej pozemku 1 632 m²",
        "price_czk": 1290000,
        "price_czk_m2": 791,
        "locality": {
            "city": "Testov",
            "citypart": "Centrum",
            "region_id": 15,
            "region": "Ústecký kraj",
            "gps_lat": 50.1,
            "gps_lon": 14.4,
        },
    }

    listing = normalize_estate(estate)

    assert listing.id == "12345"
    assert listing.price_czk == 1290000
    assert listing.price_per_m2_czk == 791
    assert listing.area_m2 == 1632
    assert listing.location == "Testov - Centrum"
    assert listing.region_id == 15
    assert listing.region == "Ústecký kraj"
    assert listing.latitude == 50.1
    assert listing.longitude == 14.4
