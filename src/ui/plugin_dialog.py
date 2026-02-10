from __future__ import annotations

from typing import Any, Callable

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QGroupBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QCheckBox,
    QDoubleSpinBox,
    QSpinBox,
    QPushButton,
    QWidget,
    QMessageBox,
    QTabWidget,
    QListWidget,
    QListWidgetItem,
)
from PyQt6.QtCore import Qt

from core.plugin_base import PluginBase


class PluginManagerDialog(QDialog):
    def __init__(self, plugins: list[PluginBase], active_processors: list[str], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Управление плагинами")
        self.resize(800, 600)
        
        self.plugins = plugins
        self.active_processors_ids = active_processors # List of GUIDs in order
        self.current_plugin: PluginBase | None = None
        
        self.layout_main = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        self.layout_main.addWidget(self.tabs)
        
        # TAB 1: General List & Settings
        self.tab_general = QWidget()
        self._init_general_tab()
        self.tabs.addTab(self.tab_general, "Список и Настройки")

        # TAB 2: Process Chain
        self.tab_chain = QWidget()
        self._init_chain_tab()
        self.tabs.addTab(self.tab_chain, "Цепочка обработки")
        
        # Close Button
        self.close_btn = QPushButton("Закрыть и сохранить цепочку")
        self.close_btn.clicked.connect(self.accept)
        self.layout_main.addWidget(self.close_btn)

    def _init_general_tab(self):
        layout = QVBoxLayout(self.tab_general)
        
        # Plugins List Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Название", "Тип", "Автор", "Версия", "Дата"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.cellClicked.connect(self.on_plugin_selected)
        layout.addWidget(self.table)
        
        self._populate_table()

        # Settings Group Box
        self.settings_group = QGroupBox("Настройки выбранного плагина")
        self.settings_layout = QFormLayout(self.settings_group)
        layout.addWidget(self.settings_group)
        
        # Save Settings Button
        self.save_settings_btn = QPushButton("Применить настройки плагина")
        self.save_settings_btn.clicked.connect(self.save_settings)
        self.save_settings_btn.setEnabled(False)
        layout.addWidget(self.save_settings_btn)
        
        self.settings_inputs: dict[str, QWidget] = {}

    def _init_chain_tab(self):
        layout = QVBoxLayout(self.tab_chain)
        
        layout.addWidget(QLabel("Укажите активные плагины обработки и их порядок:"))
        
        self.chain_list = QListWidget()
        self.chain_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        layout.addWidget(self.chain_list)
        
        # Find all processor plugins
        processors = [p for p in self.plugins if p.plugin_type == "Processor"]
        
        # First add those that are already active in the correct order
        added_ids = set()
        for pid in self.active_processors_ids:
            plugin = next((p for p in processors if p.id == pid), None)
            if plugin:
                self._add_chain_item(plugin, checked=True)
                added_ids.add(pid)
        
        # Then add the rest as unchecked
        for plugin in processors:
            if plugin.id not in added_ids:
                self._add_chain_item(plugin, checked=False)

    def _add_chain_item(self, plugin: PluginBase, checked: bool):
        item = QListWidgetItem(f"{plugin.name} ({plugin.id})")
        item.setData(Qt.ItemDataRole.UserRole, plugin.id)
        item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
        self.chain_list.addItem(item)
    
    def get_chain_result(self) -> list[str]:
        """Returns the list of GUIDs for the configured chain."""
        chain = []
        for i in range(self.chain_list.count()):
            item = self.chain_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                chain.append(item.data(Qt.ItemDataRole.UserRole))
        return chain

    def _populate_table(self):
        self.table.setRowCount(len(self.plugins))
        for i, plugin in enumerate(self.plugins):
            self.table.setItem(i, 0, QTableWidgetItem(plugin.name))
            self.table.setItem(i, 1, QTableWidgetItem(plugin.plugin_type))
            self.table.setItem(i, 2, QTableWidgetItem(plugin.author))
            self.table.setItem(i, 3, QTableWidgetItem(plugin.version))
            self.table.setItem(i, 4, QTableWidgetItem(plugin.release_date))

    def on_plugin_selected(self, row: int, column: int):
        self.current_plugin = self.plugins[row]
        self.settings_group.setTitle(f"Настройки: {self.current_plugin.name}")
        self._generate_settings_form(self.current_plugin)
        self.save_settings_btn.setEnabled(True)

    def _generate_settings_form(self, plugin: PluginBase):
        # Clear existing layout
        while self.settings_layout.count():
            item = self.settings_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        self.settings_inputs = {}
        
        if not plugin.settings_schema:
            self.settings_layout.addRow(QLabel("Нет доступных настроек"))
            return

        for key, schema in plugin.settings_schema.items():
            label_text = schema.get("label", key)
            val_type = schema.get("type", "str")
            current_value = plugin.settings.get(key, schema.get("default"))
            
            if val_type == "bool":
                widget = QCheckBox()
                widget.setChecked(bool(current_value))
            elif val_type == "int":
                widget = QSpinBox()
                widget.setRange(-999999, 999999)
                widget.setValue(int(current_value))
            elif val_type == "float":
                widget = QDoubleSpinBox()
                widget.setRange(-999999.0, 999999.0)
                widget.setDecimals(2)
                widget.setValue(float(current_value))
            else:
                widget = QLineEdit()
                widget.setText(str(current_value))
            
            self.settings_layout.addRow(label_text, widget)
            self.settings_inputs[key] = widget

    def save_settings(self):
        if not self.current_plugin:
            return

        new_settings = {}
        for key, widget in self.settings_inputs.items():
            if isinstance(widget, QCheckBox):
                new_settings[key] = widget.isChecked()
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                new_settings[key] = widget.value()
            elif isinstance(widget, QLineEdit):
                new_settings[key] = widget.text()
        
        self.current_plugin.update_settings(new_settings)
        QMessageBox.information(self, "Успех", "Настройки обновлены!")
