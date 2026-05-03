import pandas as pd
from PySide6.QtCore import Qt

from app.state import AppState
from ui.table_model import DataFrameTableModel


def test_app_state_starts_empty():
    state = AppState()

    assert state.source_path is None
    assert state.sheet_name is None
    assert state.raw_frame is None
    assert state.result_frame is None


def test_app_state_tracks_status_and_source_summary():
    state = AppState()

    assert state.status_message == "未导入文件"
    assert state.source_summary == ""
    assert state.last_export_path is None


def test_dataframe_table_model_exposes_row_column_and_display_data(qtbot):
    frame = pd.DataFrame([
        {"name": "A", "value": 10},
        {"name": "B", "value": 12},
    ])

    model = DataFrameTableModel(frame)

    assert model.rowCount() == 2
    assert model.columnCount() == 2
    assert model.headerData(0, Qt.Horizontal, Qt.DisplayRole) == "name"
    assert model.data(model.index(1, 1), Qt.DisplayRole) == "12"
