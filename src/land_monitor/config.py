from pathlib import Path
from typing import Any

import yaml


def load_settings(path: str | Path = "config/settings.yaml") -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}
