import pandas as pd
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt


class DataFrameTableModel(QAbstractTableModel):
    def __init__(self, frame: pd.DataFrame | None = None) -> None:
        super().__init__()
        self._frame = frame if frame is not None else pd.DataFrame()

    def set_frame(self, frame: pd.DataFrame) -> None:
        self.beginResetModel()
        self._frame = frame
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._frame.index)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._frame.columns)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        return str(self._frame.iat[index.row(), index.column()])

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return str(self._frame.columns[section])
        return str(section + 1)
