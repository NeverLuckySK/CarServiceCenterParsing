from __future__ import annotations

from core.models import ServiceItem
from core.plugin_base import PluginBase


class DiscountPlugin(PluginBase):
    id = "55555555-5555-5555-5555-555555555555"
    name = "Скидка/Наценка"
    plugin_type = "Processor"
    author = "Marketing Dept"
    version = "1.0"
    release_date = "2024-02-12"
    description = "Применение скидки или наценки ко всем услугам"

    settings_schema = {
        "adjustment_percent": {"type": "int", "label": "Корректировка % (ex. -10 or 20)", "default": 0},
        "suffix": {"type": "str", "label": "Метка в название", "default": "(акция)"}
    }

    def process(self, items):
        percent = int(self.settings.get("adjustment_percent", 0))
        suffix = str(self.settings.get("suffix", ""))
        factor = 1 + (percent / 100.0)

        for item in items:
            new_price = item.price * factor
            new_name = f"{item.name} {suffix}" if suffix else item.name
            
            yield ServiceItem(
                name=new_name,
                price=new_price,
                category=item.category,
                source=item.source
            )

def get_plugin() -> PluginBase:
    return DiscountPlugin()
