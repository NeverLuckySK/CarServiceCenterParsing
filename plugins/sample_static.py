from __future__ import annotations

from core.models import ServiceItem
from core.plugin_base import PluginBase


class StaticServicePlugin(PluginBase):
    name = "Базовый прайс"
    version = "1.0"
    description = "Фиксированный список услуг"

    def load(self):
        return [
            ServiceItem(name="Диагностика двигателя", price=1200.0, category="Диагностика", source=self.name),
            ServiceItem(name="Замена масла", price=1800.0, category="ТО", source=self.name),
            ServiceItem(name="Развал-схождение", price=2500.0, category="Ходовая", source=self.name),
        ]


def get_plugin() -> PluginBase:
    return StaticServicePlugin()
