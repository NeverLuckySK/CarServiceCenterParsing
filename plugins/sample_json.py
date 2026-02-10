from __future__ import annotations

import json
from pathlib import Path

from core.plugin_base import PluginBase


class JsonServicePlugin(PluginBase):
    name = "JSON прайс"
    version = "1.0"
    description = "Загрузка услуг из JSON"

    def load(self):
        data_path = Path(__file__).resolve().parent.parent / "data" / "services.json"
        with data_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return payload


def get_plugin() -> PluginBase:
    return JsonServicePlugin()
