from __future__ import annotations

import json
from pathlib import Path

from .models import Listing


def write_json(listings: list[Listing], path: str = "reports/latest.json") -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps([item.to_dict() for item in listings], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return target
