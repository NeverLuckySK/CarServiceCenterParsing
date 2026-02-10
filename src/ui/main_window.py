from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QUrl, QModelIndex
from PyQt6.QtGui import QAction, QDesktopServices
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
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
from ui.plugin_dialog import PluginManagerDialog


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
        # Store GUIDs of active processors in order
        self._active_chain_ids: list[str] = []
        self._plugin_errors: list[str] = []

        self._table = QTableView()
        self._table.setModel(self._model)
        self._table.setSortingEnabled(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self._table.clicked.connect(self._on_table_clicked)

        self._status_label = QLabel("Готово")
        self.statusBar().addWidget(self._status_label)

        self._init_layout()
        self._init_menu()
        self._load_plugins()
        self._refresh_data()

    def _init_layout(self) -> None:
        container = QWidget()
        layout = QVBoxLayout(container)

        # Removed toolbar buttons as requested
        
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
        
        plugins_action = QAction("Управление плагинами...", self)
        plugins_action.triggered.connect(self._open_plugin_manager)
        menu.addAction(plugins_action)

    def _load_plugins(self) -> None:
        self._plugins, self._plugin_errors = load_plugins(self._plugin_dir)
        status = f"Плагины: {len(self._plugins)}"
        if self._plugin_errors:
            status += f", ошибки: {len(self._plugin_errors)}"
        self._status_label.setText(status)

        if self._plugin_errors:
            QMessageBox.warning(self, "Ошибки загрузки", "\n".join(self._plugin_errors))

    def _refresh_data(self) -> None:
        # Resolve chain objects
        processors = []
        for pid in self._active_chain_ids:
            p_obj = next((p for p in self._plugins if p.id == pid), None)
            if p_obj:
                processors.append(p_obj)

        if self._active_chain_ids and not processors:
             # Just a safety check if IDs outlived plugins
             pass

        items, errors = aggregate(self._plugins, processors=processors)
        self._model.set_items(items)
        status = f"Услуг: {len(items)}"
        if errors:
            status += f", ошибки: {len(errors)}"
        self._status_label.setText(status)

        if errors:
            QMessageBox.warning(self, "Ошибки обработки", "\n".join(errors))

    def _open_plugins_folder(self) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._plugin_dir)))
        
    def _on_table_clicked(self, index: QModelIndex) -> None:
        # Check if "Source" column (index 3) is clicked
        if index.isValid() and index.column() == 3:
            # Map index to source model because of sorting
            source_index = self._table.model().mapToSource(index) if hasattr(self._table.model(), "mapToSource") else index
            
            # Since we use simple model without proxy for now:
            row = index.row()
            if 0 <= row < len(self._model._items):
                item = self._model._items[row]
                if item.url:
                    QDesktopServices.openUrl(QUrl(item.url))

    def _open_plugin_manager(self) -> None:
        if not self._plugins:
            QMessageBox.information(self, "Информация", "Сначала загрузите плагины")
            return
            
        dialog = PluginManagerDialog(self._plugins, self._active_chain_ids, self)
        if dialog.exec():
            # Apply new chain
            self._active_chain_ids = dialog.get_chain_result()
            # Auto-refresh to show changes
            self._refresh_data()
