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
)
from PyQt6.QtCore import Qt

from core.plugin_base import PluginBase


class PluginManagerDialog(QDialog):
    def __init__(self, plugins: list[PluginBase], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Управление плагинами")
        self.resize(800, 600)
        
        self.plugins = plugins
        self.current_plugin: PluginBase | None = None
        
        self.layout = QVBoxLayout(self)

        # Plugins List Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Название", "Тип", "Автор", "Версия", "Дата релиза"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.cellClicked.connect(self.on_plugin_selected)
        self.layout.addWidget(self.table)
        
        self._populate_table()

        # Settings Group Box
        self.settings_group = QGroupBox("Настройки плагина")
        self.settings_layout = QFormLayout(self.settings_group)
        self.layout.addWidget(self.settings_group)
        
        # Save Button
        self.save_btn = QPushButton("Применить настройки")
        self.save_btn.clicked.connect(self.save_settings)
        self.save_btn.setEnabled(False)
        self.layout.addWidget(self.save_btn)
        
        # Close Button
        self.close_btn = QPushButton("Закрыть")
        self.close_btn.clicked.connect(self.accept)
        self.layout.addWidget(self.close_btn)
        
        self.settings_inputs: dict[str, QWidget] = {}

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
        self.settings_group.setTitle(f"Настройки: {self.current_plugin.name} (GUID: {self.current_plugin.id})")
        self._generate_settings_form(self.current_plugin)
        self.save_btn.setEnabled(True)

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
