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
    # Attempt 1: If 'src' is in path (it is now), `import ui` should work
    from ui.main_window import MainWindow
except ImportError:
    try:
        # Attempt 2: If structure is `src.ui`, try that
        from src.ui.main_window import MainWindow
    except ImportError:
        # Attempt 3: If running from root without src package context (rare)
        import ui.main_window
        MainWindow = ui.main_window.MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow(base_dir=base_dir)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
