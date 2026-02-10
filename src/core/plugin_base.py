from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Any, Iterable

from .models import ServiceItem


class PluginBase(ABC):
    # Metadata
    id: str = str(uuid.UUID(int=0))  # Default invalid GUID, must be overridden
    name: str = "Unnamed"
    plugin_type: str = "Source"  # e.g. "Source", "Utility"
    author: str = "Unknown"
    version: str = "0.0"
    release_date: str = "1970-01-01"
    description: str = ""

    # Configuration storage (key -> value)
    settings: dict[str, Any] = {}

    # Configuration schema for UI generation
    # Format: {"key": {"type": "str|int|bool", "label": "Text", "default": value}}
    settings_schema: dict[str, dict[str, Any]] = {}

    def __init__(self) -> None:
        # Initialize default settings
        self.settings = {k: v.get("default") for k, v in self.settings_schema.items()}

    def load(self) -> Iterable[ServiceItem]:
        """Main logic to load data (for Source plugins)."""
        return []

    def process(self, items: Iterable[ServiceItem]) -> Iterable[ServiceItem]:
        """Main logic to process data (for Processor plugins). Default: pass-through."""
        return items

    def update_settings(self, new_settings: dict[str, Any]) -> None:
        """Update settings from UI."""
        self.settings.update(new_settings)
