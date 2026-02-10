from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Iterable

from .plugin_base import PluginBase


def load_plugins(plugin_dir: Path) -> tuple[list[PluginBase], list[str]]:
    plugins: list[PluginBase] = []
    errors: list[str] = []

    if not plugin_dir.exists():
        errors.append(f"Plugin directory not found: {plugin_dir}")
        return plugins, errors

    for plugin_file in sorted(plugin_dir.glob("*.py")):
        if plugin_file.name.startswith("_"):
            continue

        module = _load_module(plugin_file, errors)
        if module is None:
            continue

        plugin = _create_plugin(module, errors)
        if plugin is None:
            errors.append(f"{plugin_file.name}: no plugin class found")
            continue

        plugins.append(plugin)

    return plugins, errors


def _load_module(plugin_file: Path, errors: list[str]) -> ModuleType | None:
    spec = importlib.util.spec_from_file_location(f"plugins.{plugin_file.stem}", plugin_file)
    if spec is None or spec.loader is None:
        errors.append(f"{plugin_file.name}: unable to load")
        return None

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # pragma: no cover - defensive
        errors.append(f"{plugin_file.name}: {exc}")
        return None

    return module


def _create_plugin(module: ModuleType, errors: list[str]) -> PluginBase | None:
    if hasattr(module, "get_plugin"):
        try:
            candidate = module.get_plugin()
        except Exception as exc:
            errors.append(f"{module.__name__}: get_plugin failed: {exc}")
            return None

        return _coerce_plugin(candidate)

    if hasattr(module, "PLUGIN_CLASS"):
        try:
            return _coerce_plugin(module.PLUGIN_CLASS())
        except Exception as exc:
            errors.append(f"{module.__name__}: PLUGIN_CLASS init failed: {exc}")
            return None

    for value in module.__dict__.values():
        if isinstance(value, type) and issubclass(value, PluginBase) and value is not PluginBase:
            try:
                return _coerce_plugin(value())
            except Exception as exc:
                errors.append(f"{module.__name__}: plugin init failed: {exc}")
                return None

    return None


def _coerce_plugin(candidate: object) -> PluginBase | None:
    if isinstance(candidate, PluginBase):
        return candidate
    return None
