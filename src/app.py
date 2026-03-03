from __future__ import annotations

import sys
from pathlib import Path

# Handle frozen executable mode (PyInstaller)
if getattr(sys, 'frozen', False):
    # Running as a bundle (executable)
    # The application is running from the directory where the exe is located
    base_dir = Path(sys.executable).parent
    
    # In frozen mode, PyInstaller unpacks temporary files to sys._MEIPASS
    # or keeps them in the dist folder.
    # We need to make sure Python can find 'ui' and 'core' modules.
    # Usually, if we use 'onedir' mode, imports work relatively.
    # But if we use 'onefile', they are in MEIPASS.
    # For 'onedir', the modules are often compiled into `base_library.zip` or `src` folder.
    
    # Let's ensure 'src' is importable if it was included in datas
    # Or simply add current directory to path
    if str(base_dir) not in sys.path:
        sys.path.insert(0, str(base_dir))
        
else:
    # Running from source script
    base_dir = Path(__file__).resolve().parent.parent

src_dir = base_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from PyQt6.QtWidgets import QApplication

# Try importing directly first (standard)
try:
    from ui.main_window import MainWindow
except ImportError:
    # Fallback: maybe 'src.ui' if packaged differently or path issue
    try:
        from src.ui.main_window import MainWindow
    except ImportError:
         # Last resort: add directory of this file (src folder) to path
        sys.path.append(str(Path(__file__).parent))
        from ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow(base_dir=base_dir)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
