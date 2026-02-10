from __future__ import annotations

from typing import Iterable

from .models import ServiceItem
from .plugin_base import PluginBase


def aggregate(plugins: Iterable[PluginBase], processors: Iterable[PluginBase] | None = None) -> tuple[list[ServiceItem], list[str]]:
    items: list[ServiceItem] = []
    errors: list[str] = []

    # 1. Load data from Sources
    for plugin in plugins:
        if plugin.plugin_type != "Source" and plugin.plugin_type != "Parser":
            continue
            
        try:
            for raw in plugin.load():
                item, item_errors = _normalize_item(raw, plugin.name)
                if item is not None:
                    items.append(item)
                errors.extend(item_errors)
        except Exception as exc:  # pragma: no cover - defensive
            errors.append(f"{plugin.name}: {exc}")

    # 2. Apply Processing Chain
    if processors:
        for proc in processors:
            try:
                 # consume the generator to create a list for the next step/final output
                 items = list(proc.process(items))
            except Exception as exc:
                 errors.append(f"Processor {proc.name}: {exc}")

    return items, errors


def _normalize_item(raw: object, source: str) -> tuple[ServiceItem | None, list[str]]:
    errors: list[str] = []
    
    # Pre-check attributes for raw object if it's not dict/ServiceItem but structurally similar? 
    # Current implementation handles dict and ServiceItem.

    if isinstance(raw, ServiceItem):
        item = ServiceItem(
            name=raw.name.strip(),
            price=float(raw.price),
            category=raw.category.strip() if raw.category else None,
            source=source,
            url=raw.url
        )
    elif isinstance(raw, dict):
        name = str(raw.get("name", "")).strip()
        price = raw.get("price", None)
        category = raw.get("category", None)
        url = raw.get("url", None)
        item = ServiceItem(
            name=name,
            price=float(price) if price is not None else float("nan"),
            category=str(category).strip() if category else None,
            source=source,
            url=str(url) if url else None
        )
    else:
        errors.append(f"{source}: unsupported item type {type(raw).__name__}")
        return None, errors

    if not item.name:
        errors.append(f"{source}: empty service name")
        return None, errors

    if not _is_valid_price(item.price):
        errors.append(f"{source}: invalid price for {item.name}")
        return None, errors

    return item, errors


def _is_valid_price(value: float) -> bool:
    return value >= 0 and value == value
