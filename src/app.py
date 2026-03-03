from __future__ import annotations

import sys
from pathlib import Path

# Handle frozen executable mode (PyInstaller)
if getattr(sys, 'frozen', False):
    # Running as a bundle (executable)
    exe_dir = Path(sys.executable).parent
    base_dir = exe_dir

    # Fix: Ensure `core` and `ui` are importable from ANYWHERE they landed.
    # PyInstaller usually puts modules in valid path, but directory structure might be flat.
    # We add `exe_dir` (root of OneDir) and `exe_dir/src` (if preserved).
    if str(exe_dir) not in sys.path:
        sys.path.insert(0, str(exe_dir))
    
    src_check = exe_dir / "src"
    if src_check.exists() and str(src_check) not in sys.path:
        sys.path.insert(0, str(src_check))

else:
    # Running from source script
    base_dir = Path(__file__).resolve().parent.parent

# Force add 'src' folder itself to path for both cases
# This is critical for imports like `from core.models import ...` working inside `ui.main_window`
current_file_dir = Path(__file__).parent
if str(current_file_dir) not in sys.path:
    # Use insert(0) to prioritize local modules over site-packages
    sys.path.insert(0, str(current_file_dir))

from PyQt6.QtWidgets import QApplication

# Now try imports. 
# We need 'core' and 'ui' to take precedence.
try:
    # Attempt 1: Standard relative import if we are in expected environment
    from ui.main_window import MainWindow
except ImportError:
    try:
        # Attempt 2: If inside 'src' package structure (often happens in PyInstaller onefile/onedir)
        # We need to expose 'core' and 'ui' as top-level modules
        import src.core
        import src.ui
        sys.modules["core"] = src.core
        sys.modules["ui"] = src.ui
        
        # Also need submodules for direct 'from core.aggregator' imports inside ui
        from src.core import aggregator, plugin_loader, license_manager, models, plugin_base
        sys.modules["core.aggregator"] = aggregator
        sys.modules["core.plugin_loader"] = plugin_loader
        sys.modules["core.license_manager"] = license_manager
        sys.modules["core.models"] = models
        sys.modules["core.plugin_base"] = plugin_base
        
        from src.ui import main_window, table_model, plugin_dialog, proxy_model
        sys.modules["ui.main_window"] = main_window
        sys.modules["ui.table_model"] = table_model
        sys.modules["ui.plugin_dialog"] = plugin_dialog
        sys.modules["ui.proxy_model"] = proxy_model

        from src.ui.main_window import MainWindow
    except ImportError:
        # Attempt 3: Direct file import hack (Last Resort)
        import ui.main_window
        MainWindow = ui.main_window.MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow(base_dir=base_dir)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
