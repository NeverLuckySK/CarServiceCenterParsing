from __future__ import annotations

import json
from pathlib import Path

from core.plugin_base import PluginBase


class JsonServicePlugin(PluginBase):
    id = "22222222-2222-2222-2222-222222222222"
    name = "JSON прайс"
    plugin_type = "Source"
    author = "Internal"
    version = "1.0"
    release_date = "2023-10-05"
    description = "Загрузка услуг из JSON"
    
    settings_schema = {
        "filename": {"type": "str", "label": "Имя файла", "default": "services.json"}
    }

    def load(self):
        filename = self.settings.get("filename", "services.json")
        data_path = Path(__file__).resolve().parent.parent / "data" / filename
        if not data_path.exists():
            # Fallback to default if configured file doesn't exist
             data_path = Path(__file__).resolve().parent.parent / "data" / "services.json"

        with data_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return payload


def get_plugin() -> PluginBase:
    return JsonServicePlugin()
