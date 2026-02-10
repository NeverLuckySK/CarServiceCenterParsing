from __future__ import annotations

import sys
from pathlib import Path

base_dir = Path(__file__).resolve().parents[1]
src_dir = base_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from core.plugin_loader import load_plugins


def test_load_plugins():
    plugins, errors = load_plugins(base_dir / "plugins")
    assert errors == []
    assert len(plugins) >= 2
