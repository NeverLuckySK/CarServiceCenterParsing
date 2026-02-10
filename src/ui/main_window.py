from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QAction, QDesktopServices
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from core.aggregator import aggregate
from core.plugin_loader import load_plugins
from ui.table_model import ServiceTableModel


class MainWindow(QMainWindow):
    def __init__(self, base_dir: Path) -> None:
        super().__init__()
        self.setWindowTitle("Агрегатор услуг автотехцентров")
        self.resize(980, 620)

        self._base_dir = base_dir
        self._plugin_dir = base_dir / "plugins"
        self._data_dir = base_dir / "data"

        self._model = ServiceTableModel()
        self._plugins = []
        self._plugin_errors: list[str] = []

        self._table = QTableView()
        self._table.setModel(self._model)
        self._table.setSortingEnabled(True)

        self._status_label = QLabel("Готово")
        self.statusBar().addWidget(self._status_label)

        self._init_layout()
        self._init_menu()
        self._load_plugins()
        self._refresh_data()

    def _init_layout(self) -> None:
        container = QWidget()
        layout = QVBoxLayout(container)

        toolbar = QHBoxLayout()
        self._reload_btn = QPushButton("Перезагрузить плагины")
        self._reload_btn.clicked.connect(self._load_plugins)
        self._refresh_btn = QPushButton("Обновить данные")
        self._refresh_btn.clicked.connect(self._refresh_data)
        self._open_btn = QPushButton("Открыть папку плагинов")
        self._open_btn.clicked.connect(self._open_plugins_folder)

        toolbar.addWidget(self._reload_btn)
        toolbar.addWidget(self._refresh_btn)
        toolbar.addWidget(self._open_btn)
        toolbar.addStretch()

        layout.addLayout(toolbar)
        layout.addWidget(self._table)

        self.setCentralWidget(container)

    def _init_menu(self) -> None:
        open_plugins_action = QAction("Открыть папку плагинов", self)
        open_plugins_action.triggered.connect(self._open_plugins_folder)

        reload_action = QAction("Перезагрузить плагины", self)
        reload_action.triggered.connect(self._load_plugins)

        refresh_action = QAction("Обновить данные", self)
        refresh_action.triggered.connect(self._refresh_data)

        menu = self.menuBar().addMenu("Действия")
        menu.addAction(open_plugins_action)
        menu.addAction(reload_action)
        menu.addAction(refresh_action)

    def _load_plugins(self) -> None:
        self._plugins, self._plugin_errors = load_plugins(self._plugin_dir)
        status = f"Плагины: {len(self._plugins)}"
        if self._plugin_errors:
            status += f", ошибки: {len(self._plugin_errors)}"
        self._status_label.setText(status)

        if self._plugin_errors:
            QMessageBox.warning(self, "Ошибки загрузки", "\n".join(self._plugin_errors))

    def _refresh_data(self) -> None:
        items, errors = aggregate(self._plugins)
        self._model.set_items(items)
        status = f"Услуг: {len(items)}"
        if errors:
            status += f", ошибки: {len(errors)}"
        self._status_label.setText(status)

        if errors:
            QMessageBox.warning(self, "Ошибки обработки", "\n".join(errors))

    def _open_plugins_folder(self) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._plugin_dir)))
