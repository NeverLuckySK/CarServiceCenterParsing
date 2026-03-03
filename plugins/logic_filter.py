from __future__ import annotations

from core.models import ServiceItem
from core.plugin_base import PluginBase


class PriceFilterPlugin(PluginBase):
    id = "594D33F0-3791-4253-94CD-65DA98DD3BD6"
    name = "Фильтр цен"
    plugin_type = "Processor"
    author = "Internal"
    version = "1.0"
    release_date = "2024-02-12"
    description = "Фильтрация услуг по диапазону цен"

    # Settings are now controlled via the Main Window UI when this plugin is active.
    # We keep an empty schema or remove it to avoid confusion in the settings dialog.
    settings_schema = {}

    def process(self, items):
        # This plugin enables the UI filter in the main window.
        # Ideally, it should not filter data here to avoid conflict/double filtering.
        # The actual filtering happens via the ProxyModel controlled by the UI.
        yield from items

def get_plugin() -> PluginBase:
    return PriceFilterPlugin()
