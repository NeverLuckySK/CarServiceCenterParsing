from __future__ import annotations

from core.models import ServiceItem
from core.plugin_base import PluginBase


class DiscountPlugin(PluginBase):
    id = "55555555-5555-5555-5555-555555555555"
    name = "Скидка/Наценка"
    plugin_type = "Processor"
    author = "Marketing Dept"
    version = "1.1" # Incremented version
    release_date = "2024-02-12"
    description = "Автоматическое применение скидки (при отрицательном %) или наценки (при положительном)"

    settings_schema = {
        "adjustment_percent": {"type": "int", "label": "Корректировка % (ex. -10 or 20)", "default": 0}
        # "suffix" removed, calculated automatically
    }

    def process(self, items):
        try:
            percent = int(self.settings.get("adjustment_percent", 0))
        except (ValueError, TypeError):
            percent = 0
            
        if percent == 0:
            # No change, just return items as is (or yield them)
            yield from items
            return
            
        factor = 1 + (percent / 100.0)

        # Determine label automatically
        if percent < 0:
            suffix = f"(скидка {abs(percent)}%)"
        else:
            suffix = f"(+{percent}%)"

        for item in items:
            new_price = item.price * factor
            # Ensure price is at least 0
            if new_price < 0:
                new_price = 0.0
                
            new_name = f"{item.name} {suffix}"
            
            yield ServiceItem(
                name=new_name,
                price=new_price,
                category=item.category,
                source=item.source,
                url=item.url
            )

def get_plugin() -> PluginBase:
    return DiscountPlugin()
