from PyQt6.QtCore import QSortFilterProxyModel, Qt

class SequentialHeaderProxyModel(QSortFilterProxyModel):
    """
    A proxy model that ensures vertical headers (row numbers) are always sequential (1, 2, 3...),
    ignoring the underlying source row index.
    """
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):
        # Override only vertical display role (row numbers)
        if orientation == Qt.Orientation.Vertical and role == Qt.ItemDataRole.DisplayRole:
            return str(section + 1)
            
        # For everything else (horizontal headers, other roles), pass to default implementation
        return super().headerData(section, orientation, role)
