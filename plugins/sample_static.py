from __future__ import annotations

from core.models import ServiceItem
from core.plugin_base import PluginBase


class StaticServicePlugin(PluginBase):
    id = "11111111-1111-1111-1111-111111111111"
    name = "Базовый прайс"
    plugin_type = "Source"
    author = "Internal"
    version = "1.0"
    release_date = "2023-10-01"
    description = "Фиксированный список услуг"

    settings_schema = {
        "multiplier": {"type": "float", "label": "Множитель цены", "default": 1.0}
    }

    def load(self):
        mult = float(self.settings.get("multiplier", 1.0))
        return [
            ServiceItem(name="Диагностика двигателя", price=1200.0 * mult, category="Диагностика", source=self.name),
            ServiceItem(name="Замена масла", price=1800.0 * mult, category="ТО", source=self.name),
            ServiceItem(name="Развал-схождение", price=2500.0 * mult, category="Ходовая", source=self.name),
        ]


def get_plugin() -> PluginBase:
    return StaticServicePlugin()
