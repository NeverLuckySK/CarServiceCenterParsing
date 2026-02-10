from __future__ import annotations

import sys
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
src_dir = base_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow(base_dir=base_dir)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
