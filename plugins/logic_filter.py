from __future__ import annotations

from core.models import ServiceItem
from core.plugin_base import PluginBase


class PriceFilterPlugin(PluginBase):
    id = "44444444-4444-4444-4444-444444444444"
    name = "Фильтр цен"
    plugin_type = "Processor"
    author = "Internal"
    version = "1.0"
    release_date = "2024-02-12"
    description = "Фильтрация услуг по диапазону цен"

    settings_schema = {
        "min_price": {"type": "float", "label": "Мин. цена", "default": 0.0},
        "max_price": {"type": "float", "label": "Макс. цена", "default": 10000.0},
    }

    def process(self, items):
        min_p = float(self.settings.get("min_price", 0.0))
        max_p = float(self.settings.get("max_price", 10000.0))
        
        for item in items:
            if min_p <= item.price <= max_p:
                yield item

def get_plugin() -> PluginBase:
    return PriceFilterPlugin()
