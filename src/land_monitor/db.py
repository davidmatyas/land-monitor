from __future__ import annotations

import sqlite3
from pathlib import Path

from .models import Listing

SCHEMA = """
CREATE TABLE IF NOT EXISTS listings (
    source TEXT NOT NULL,
    listing_id TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    locality TEXT,
    region TEXT,
    price_czk INTEGER,
    area_m2 REAL,
    latitude REAL,
    longitude REAL,
    first_seen TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (source, listing_id)
)
"""


def connect(path: str | Path = "data/land_monitor.sqlite") -> sqlite3.Connection:
    db_path = Path(path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.execute(SCHEMA)
    connection.commit()
    return connection


def upsert_listing(connection: sqlite3.Connection, listing: Listing) -> None:
    connection.execute(
        """
        INSERT INTO listings (
            source, listing_id, title, url, locality, region,
            price_czk, area_m2, latitude, longitude
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(source, listing_id) DO UPDATE SET
            title=excluded.title,
            url=excluded.url,
            locality=excluded.locality,
            region=excluded.region,
            price_czk=excluded.price_czk,
            area_m2=excluded.area_m2,
            latitude=excluded.latitude,
            longitude=excluded.longitude,
            last_seen=CURRENT_TIMESTAMP
        """,
        (
            listing.source,
            listing.listing_id,
            listing.title,
            listing.url,
            listing.locality,
            listing.region,
            listing.price_czk,
            listing.area_m2,
            listing.latitude,
            listing.longitude,
        ),
    )
    connection.commit()
