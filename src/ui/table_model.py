from __future__ import annotations

from typing import Any

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt

from core.models import ServiceItem


class ServiceTableModel(QAbstractTableModel):
    headers = ["Услуга", "Категория", "Цена", "Источник"]

    def __init__(self, items: list[ServiceItem] | None = None) -> None:
        super().__init__()
        self._items = items or []

    def rowCount(self, parent: QModelIndex | None = None) -> int:  # type: ignore[override]
        return len(self._items)

    def columnCount(self, parent: QModelIndex | None = None) -> int:  # type: ignore[override]
        return len(self.headers)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:  # type: ignore[override]
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None

        item = self._items[index.row()]
        column = index.column()

        if column == 0:
            return item.name
        if column == 1:
            return item.category or "-"
        if column == 2:
            return f"{item.price:.2f}"
        if column == 3:
            return item.source

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:  # type: ignore[override]
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return str(section + 1)

    def set_items(self, items: list[ServiceItem]) -> None:
        self.beginResetModel()
        self._items = items
        self.endResetModel()
