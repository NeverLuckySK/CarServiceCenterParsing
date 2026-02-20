from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QUrl, QModelIndex, Qt, QSortFilterProxyModel
from PyQt6.QtGui import QAction, QDesktopServices
from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
    QInputDialog,
)

from core.aggregator import aggregate
from core.plugin_loader import load_plugins
from core.license_manager import LicenseManager
from ui.table_model import ServiceTableModel
from ui.plugin_dialog import PluginManagerDialog
from ui.proxy_model import SequentialHeaderProxyModel


class MainWindow(QMainWindow):
    def __init__(self, base_dir: Path) -> None:
        super().__init__()
        self._base_dir = base_dir
        self._plugin_dir = base_dir / "plugins"
        self._data_dir = base_dir / "data"
        
        # Initialize License Manager
        self._license_manager = LicenseManager(self._data_dir)
        lic_status = self._license_manager.get_status_text()
        self.setWindowTitle(f"Агрегатор услуг автотехцентров [{lic_status}]")

        self.resize(1050, 650)

        self._model = ServiceTableModel()
        self._proxy_model = SequentialHeaderProxyModel()
        self._proxy_model.setSourceModel(self._model)
        self._proxy_model.setSortRole(Qt.ItemDataRole.EditRole) # Use EditRole for sorting (allows numeric sort for prices)
        self._proxy_model.setFilterKeyColumn(-1)
        self._proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        
        self._plugins = []
        # Store GUIDs of active processors in order
        self._active_chain_ids: list[str] = []
        self._plugin_errors: list[str] = []

        self._table = QTableView()
        self._table.setModel(self._proxy_model)
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

        # Filters layout (Search + Price)
        filters_layout = QHBoxLayout()

        # Search bar
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Поиск услуг...")
        self._search_input.textChanged.connect(self._on_search_text_changed)
        filters_layout.addWidget(self._search_input, stretch=2)
        
        # Price filters
        filters_layout.addSpacing(10)
        filters_layout.addWidget(QLabel("Цена от:"))
        
        self._min_price_spin = QDoubleSpinBox()
        self._min_price_spin.setRange(0, 10_000_000)
        self._min_price_spin.setValue(0)
        self._min_price_spin.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        self._min_price_spin.setFixedWidth(80)
        self._min_price_spin.valueChanged.connect(self._on_min_price_changed)
        filters_layout.addWidget(self._min_price_spin)

        filters_layout.addWidget(QLabel("до:"))

        self._max_price_spin = QDoubleSpinBox()
        self._max_price_spin.setRange(0, 10_000_000)
        self._max_price_spin.setValue(10_000_000) # Default to max
        self._max_price_spin.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        self._max_price_spin.setFixedWidth(80)
        self._max_price_spin.valueChanged.connect(self._on_max_price_changed)
        filters_layout.addWidget(self._max_price_spin)

        layout.addLayout(filters_layout)
        layout.addWidget(self._table)

        self.setCentralWidget(container)

    def _on_search_text_changed(self, text: str) -> None:
        self._proxy_model.setFilterRegularExpression(text)

    def _on_min_price_changed(self, val: float) -> None:
        self._proxy_model.setMinPrice(val)

    def _on_max_price_changed(self, val: float) -> None:
        # If value is maximum configured range, treat as infinite? 
        # Or just use the value. 10 million is effectively infinite for car services.
        self._proxy_model.setMaxPrice(val)


    def _init_menu(self) -> None:
        # File Menu
        file_menu = self.menuBar().addMenu("Файл")
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Plugins Menu
        open_plugins_action = QAction("Открыть папку плагинов", self)
        open_plugins_action.triggered.connect(self._open_plugins_folder)

        reload_action = QAction("Перезагрузить плагины", self)
        reload_action.triggered.connect(self._load_plugins)

        refresh_action = QAction("Обновить данные", self)
        refresh_action.triggered.connect(self._refresh_data)

        menu = self.menuBar().addMenu("Плагины")
        menu.addAction(open_plugins_action)
        menu.addAction(reload_action)
        menu.addAction(refresh_action)
        
        plugins_action = QAction("Управление плагинами...", self)
        plugins_action.triggered.connect(self._open_plugin_manager)
        menu.addAction(plugins_action)

        item_help = self.menuBar().addMenu("Справка")
        
        activate_action = QAction("Активация", self)
        activate_action.triggered.connect(self._show_activation_dialog)
        item_help.addAction(activate_action)
        
        about_action = QAction("О приложении", self)
        about_action.triggered.connect(self._show_about_dialog)
        item_help.addAction(about_action)

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
        if index.isValid():
            # Map index to source model because of sorting/filtering
            source_index = self._proxy_model.mapToSource(index)
            
            # Check if "Source" column (index 3) is clicked
            # Note: We check the column on the original index as column order is preserved by proxy
            if source_index.column() == 3:
                row = source_index.row()
                if 0 <= row < len(self._model._items):
                    item = self._model._items[row]
                    if item.url:
                        QDesktopServices.openUrl(QUrl(item.url))

    def _open_plugin_manager(self) -> None:
        # Check License
        if not self._license_manager.check_license():
            QMessageBox.warning(self, "Ограничение бесплатной версии", 
                              "Управление плагинами доступно только в полной версии.\n"
                              "Пожалуйста, приобретите лицензию.")
            return

        if not self._plugins:
            QMessageBox.information(self, "Информация", "Сначала загрузите плагины")
            return
            
        dialog = PluginManagerDialog(self._plugins, self._active_chain_ids, self)
        if dialog.exec():
            # Apply new chain
            self._active_chain_ids = dialog.get_chain_result()
            # Auto-refresh to show changes
            self._refresh_data()
            
    def _show_about_dialog(self) -> None:
        text = (
            "Автор: Давыдов Андрей Васильевич\n"
            "Группа: БПИ22-01\n"
            "Версия приложения: 1.0"
        )
        QMessageBox.about(self, "О приложении", text)

    def _show_activation_dialog(self) -> None:
        text, ok = QInputDialog.getText(self, "Активация", "Введите ключ активации:")
        if ok and text:
            success = self._license_manager.activate(text)
            if success:
                lic = self._license_manager.check_license()
                if lic:
                    msg = f"Активация успешна!\nВладелец: {lic.get('owner')}\nДо: {lic.get('end_date')}"
                    QMessageBox.information(self, "Успех", msg)
                    
                    # Update Window Title
                    lic_status = self._license_manager.get_status_text()
                    self.setWindowTitle(f"Агрегатор услуг автотехцентров [{lic_status}]")
                else:
                    QMessageBox.warning(self, "Ошибка", "Ключ принят, но лицензия недействительна (возможно истек срок).")
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный ключ активации.")
