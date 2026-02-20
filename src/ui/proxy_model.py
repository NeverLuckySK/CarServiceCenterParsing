from PyQt6.QtCore import QSortFilterProxyModel, Qt, QModelIndex

class SequentialHeaderProxyModel(QSortFilterProxyModel):
    """
    A proxy model that ensures vertical headers (row numbers) are always sequential (1, 2, 3...),
    ignoring the underlying source row index.
    Also supports filtering by price range (Min/Max).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._min_price = 0.0
        self._max_price = 999999999.0  # Large number as default max

    def setMinPrice(self, price: float):
        self._min_price = price
        self.invalidateFilter()

    def setMaxPrice(self, price: float):
        self._max_price = price
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        # 1. Standard text filtering (regex)
        if not super().filterAcceptsRow(source_row, source_parent):
            return False

        # 2. Price filtering
        model = self.sourceModel()
        if not model:
            return True

        # Price is column 2
        index = model.index(source_row, 2, source_parent)
        # EditRole returns the raw float price
        price_val = model.data(index, Qt.ItemDataRole.EditRole)

        try:
            price = float(price_val)
        except (ValueError, TypeError):
            # If price cannot be parsed, check if we're filtering strictly
            # Usually safe to show if no strict filter, but hide if range is specific
            # Let's hide non-numeric prices if we have a range set?
            # Or treat as 0?
            price = 0.0

        if price < self._min_price:
            return False
        if price > self._max_price:
            return False
            
        return True

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):
        # Override only vertical display role (row numbers)
        if orientation == Qt.Orientation.Vertical and role == Qt.ItemDataRole.DisplayRole:
            return str(section + 1)
            
        # For everything else (horizontal headers, other roles), pass to default implementation
        return super().headerData(section, orientation, role)
