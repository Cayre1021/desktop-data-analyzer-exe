# Desktop Data Analyzer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a runnable first-version Python desktop application that imports local Excel files, previews raw and transformed data, applies basic transformations, renders simple charts, and exports processed results.

**Architecture:** Build a PySide6 single-window workbench with a thin UI layer over focused services for Excel I/O, table transformations, and chart preparation. Keep the initial implementation local-only, use pandas DataFrames as the shared data model between services, and isolate UI state management in a small app model so future `.exe` packaging does not require restructuring.

**Tech Stack:** Python 3.11+, PySide6, pandas, openpyxl, matplotlib, pytest

---

## Planned file structure

- `requirements.txt` — runtime and test dependencies
- `main.py` — desktop app entrypoint
- `app/__init__.py` — package marker
- `app/bootstrap.py` — application startup helpers and main-window creation
- `app/state.py` — shared application state dataclass for source/result data and current file metadata
- `ui/__init__.py` — package marker
- `ui/main_window.py` — main workbench window and high-level event wiring
- `ui/table_model.py` — Qt table model adapter for pandas DataFrames
- `ui/panels.py` — left-side controls and right-side chart widget containers
- `services/__init__.py` — package marker
- `services/excel/__init__.py` — package marker
- `services/excel/io.py` — Excel load/export helpers
- `services/transform/__init__.py` — package marker
- `services/transform/operations.py` — data cleaning, filtering, sorting, and calculated-column functions
- `services/chart/__init__.py` — package marker
- `services/chart/render.py` — matplotlib chart rendering helpers for Qt embedding
- `tests/conftest.py` — shared pytest fixtures
- `tests/services/excel/test_io.py` — Excel service tests
- `tests/services/transform/test_operations.py` — transform service tests
- `tests/services/chart/test_render.py` — chart helper tests
- `tests/ui/test_table_model.py` — Qt table model tests
- `tests/ui/test_main_window.py` — main workflow UI tests
- `sample_data/demo_sales.xlsx` — demo workbook for manual verification

### Task 1: Create project skeleton and dependency manifest

**Files:**
- Create: `requirements.txt`
- Create: `main.py`
- Create: `app/__init__.py`
- Create: `ui/__init__.py`
- Create: `services/__init__.py`
- Create: `services/excel/__init__.py`
- Create: `services/transform/__init__.py`
- Create: `services/chart/__init__.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Write the failing environment smoke test**

```python
from pathlib import Path


def test_main_entrypoint_exists():
    assert Path("main.py").exists()


def test_requirements_file_exists():
    assert Path("requirements.txt").exists()
```

Save in `tests/conftest.py` temporarily as a bootstrap smoke check.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/conftest.py -v`
Expected: FAIL with `AssertionError` for missing files.

- [ ] **Step 3: Write minimal implementation**

`requirements.txt`
```text
PySide6>=6.7,<6.8
pandas>=2.2,<2.3
openpyxl>=3.1,<3.2
matplotlib>=3.9,<3.10
pytest>=8.3,<8.4
pytest-qt>=4.4,<4.5
```

`main.py`
```python
from app.bootstrap import run


if __name__ == "__main__":
    raise SystemExit(run())
```

Each `__init__.py`
```python
```

Replace `tests/conftest.py` with:
```python
from pathlib import Path


ROOT_FILES = [
    "main.py",
    "requirements.txt",
    "app/__init__.py",
    "ui/__init__.py",
    "services/__init__.py",
    "services/excel/__init__.py",
    "services/transform/__init__.py",
    "services/chart/__init__.py",
]


def test_project_skeleton_exists():
    for path in ROOT_FILES:
        assert Path(path).exists(), path
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/conftest.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add requirements.txt main.py app/__init__.py ui/__init__.py services/__init__.py services/excel/__init__.py services/transform/__init__.py services/chart/__init__.py tests/conftest.py
git commit -m "chore: scaffold desktop analyzer project"
```

### Task 2: Implement Excel import/export service

**Files:**
- Create: `services/excel/io.py`
- Test: `tests/services/excel/test_io.py`

- [ ] **Step 1: Write the failing tests**

`tests/services/excel/test_io.py`
```python
from pathlib import Path

import pandas as pd

from services.excel.io import export_dataframe, load_first_sheet


def test_load_first_sheet_reads_first_worksheet(tmp_path: Path):
    source = tmp_path / "input.xlsx"
    with pd.ExcelWriter(source, engine="openpyxl") as writer:
        pd.DataFrame({"A": [1, 2]}).to_excel(writer, sheet_name="Sheet1", index=False)
        pd.DataFrame({"B": [3, 4]}).to_excel(writer, sheet_name="Sheet2", index=False)

    frame, sheet_name = load_first_sheet(source)

    assert sheet_name == "Sheet1"
    assert frame.to_dict(orient="records") == [{"A": 1}, {"A": 2}]


def test_export_dataframe_writes_new_excel_file(tmp_path: Path):
    target = tmp_path / "output.xlsx"
    frame = pd.DataFrame({"name": ["A"], "value": [10]})

    export_dataframe(frame, target)

    loaded = pd.read_excel(target)
    assert loaded.to_dict(orient="records") == [{"name": "A", "value": 10}]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/services/excel/test_io.py -v`
Expected: FAIL with `ModuleNotFoundError` or missing function imports.

- [ ] **Step 3: Write minimal implementation**

`services/excel/io.py`
```python
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook


def load_first_sheet(path: Path) -> tuple[pd.DataFrame, str]:
    workbook = load_workbook(path, read_only=True, data_only=True)
    sheet_name = workbook.sheetnames[0]
    workbook.close()
    frame = pd.read_excel(path, sheet_name=sheet_name)
    return frame, sheet_name


def export_dataframe(frame: pd.DataFrame, target: Path) -> None:
    frame.to_excel(target, index=False)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/services/excel/test_io.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add services/excel/io.py tests/services/excel/test_io.py
git commit -m "feat: add Excel import and export service"
```

### Task 3: Implement transform operations service

**Files:**
- Create: `services/transform/operations.py`
- Test: `tests/services/transform/test_operations.py`

- [ ] **Step 1: Write the failing tests**

`tests/services/transform/test_operations.py`
```python
import pandas as pd

from services.transform.operations import (
    add_calculated_column,
    apply_contains_filter,
    apply_sort,
    drop_duplicate_rows,
    drop_empty_rows,
)


def test_drop_empty_rows_removes_fully_empty_rows():
    frame = pd.DataFrame(
        [
            {"category": "A", "value": 1},
            {"category": None, "value": None},
            {"category": "B", "value": 2},
        ]
    )

    result = drop_empty_rows(frame)

    assert result.to_dict(orient="records") == [
        {"category": "A", "value": 1.0},
        {"category": "B", "value": 2.0},
    ]


def test_drop_duplicate_rows_removes_duplicate_records():
    frame = pd.DataFrame([
        {"category": "A", "value": 1},
        {"category": "A", "value": 1},
        {"category": "B", "value": 2},
    ])

    result = drop_duplicate_rows(frame)

    assert result.to_dict(orient="records") == [
        {"category": "A", "value": 1},
        {"category": "B", "value": 2},
    ]


def test_apply_sort_orders_by_selected_column_descending():
    frame = pd.DataFrame([
        {"category": "A", "value": 1},
        {"category": "B", "value": 3},
        {"category": "C", "value": 2},
    ])

    result = apply_sort(frame, "value", ascending=False)

    assert result["value"].tolist() == [3, 2, 1]


def test_apply_contains_filter_keeps_matching_rows():
    frame = pd.DataFrame([
        {"category": "North", "value": 1},
        {"category": "South", "value": 2},
    ])

    result = apply_contains_filter(frame, "category", "nor")

    assert result.to_dict(orient="records") == [{"category": "North", "value": 1}]


def test_add_calculated_column_supports_multiply():
    frame = pd.DataFrame([
        {"price": 10, "qty": 2},
        {"price": 8, "qty": 3},
    ])

    result = add_calculated_column(frame, "total", "price", "qty", "*")

    assert result.to_dict(orient="records") == [
        {"price": 10, "qty": 2, "total": 20},
        {"price": 8, "qty": 3, "total": 24},
    ]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/services/transform/test_operations.py -v`
Expected: FAIL with import errors.

- [ ] **Step 3: Write minimal implementation**

`services/transform/operations.py`
```python
import operator

import pandas as pd


OPERATORS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
}


def drop_empty_rows(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.dropna(how="all").reset_index(drop=True)


def drop_duplicate_rows(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.drop_duplicates().reset_index(drop=True)


def apply_sort(frame: pd.DataFrame, column: str, ascending: bool) -> pd.DataFrame:
    return frame.sort_values(by=column, ascending=ascending).reset_index(drop=True)


def apply_contains_filter(frame: pd.DataFrame, column: str, keyword: str) -> pd.DataFrame:
    mask = frame[column].fillna("").astype(str).str.contains(keyword, case=False, na=False)
    return frame.loc[mask].reset_index(drop=True)


def add_calculated_column(
    frame: pd.DataFrame,
    new_column: str,
    left_column: str,
    right_column: str,
    operator_symbol: str,
) -> pd.DataFrame:
    result = frame.copy()
    result[new_column] = OPERATORS[operator_symbol](result[left_column], result[right_column])
    return result
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/services/transform/test_operations.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add services/transform/operations.py tests/services/transform/test_operations.py
git commit -m "feat: add dataframe transformation service"
```

### Task 4: Implement chart configuration and rendering helpers

**Files:**
- Create: `services/chart/render.py`
- Test: `tests/services/chart/test_render.py`

- [ ] **Step 1: Write the failing tests**

`tests/services/chart/test_render.py`
```python
import pandas as pd

from services.chart.render import build_chart_series


def test_build_chart_series_for_bar_chart_returns_x_and_y_lists():
    frame = pd.DataFrame([
        {"month": "Jan", "sales": 10},
        {"month": "Feb", "sales": 12},
    ])

    result = build_chart_series(frame, "month", "sales")

    assert result == {
        "x": ["Jan", "Feb"],
        "y": [10, 12],
    }
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/services/chart/test_render.py -v`
Expected: FAIL with import errors.

- [ ] **Step 3: Write minimal implementation**

`services/chart/render.py`
```python
import pandas as pd


def build_chart_series(frame: pd.DataFrame, category_column: str, value_column: str) -> dict[str, list]:
    return {
        "x": frame[category_column].astype(str).tolist(),
        "y": frame[value_column].tolist(),
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/services/chart/test_render.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add services/chart/render.py tests/services/chart/test_render.py
git commit -m "feat: add chart series builder"
```

### Task 5: Implement application state and table model

**Files:**
- Create: `app/state.py`
- Create: `ui/table_model.py`
- Test: `tests/ui/test_table_model.py`

- [ ] **Step 1: Write the failing tests**

`tests/ui/test_table_model.py`
```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/ui/test_table_model.py -v`
Expected: FAIL with import errors.

- [ ] **Step 3: Write minimal implementation**

`app/state.py`
```python
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class AppState:
    source_path: Path | None = None
    sheet_name: str | None = None
    raw_frame: pd.DataFrame | None = None
    result_frame: pd.DataFrame | None = None
```

`ui/table_model.py`
```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/ui/test_table_model.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/state.py ui/table_model.py tests/ui/test_table_model.py
git commit -m "feat: add app state and dataframe table model"
```

### Task 6: Build reusable control panels and chart canvas

**Files:**
- Create: `ui/panels.py`
- Modify: `services/chart/render.py`
- Test: `tests/services/chart/test_render.py`

- [ ] **Step 1: Extend tests with chart drawing expectation**

Append to `tests/services/chart/test_render.py`:
```python
from matplotlib.figure import Figure

from services.chart.render import draw_chart


def test_draw_chart_adds_one_axes_with_requested_title():
    figure = Figure()
    data = {"x": ["Jan", "Feb"], "y": [10, 12]}

    draw_chart(figure, data, "bar", "Monthly Sales")

    assert len(figure.axes) == 1
    assert figure.axes[0].get_title() == "Monthly Sales"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/services/chart/test_render.py -v`
Expected: FAIL with missing `draw_chart`.

- [ ] **Step 3: Write minimal implementation**

Append to `services/chart/render.py`
```python
from matplotlib.figure import Figure


def draw_chart(figure: Figure, data: dict[str, list], chart_type: str, title: str) -> None:
    figure.clear()
    axes = figure.add_subplot(111)
    if chart_type == "line":
        axes.plot(data["x"], data["y"], marker="o")
    else:
        axes.bar(data["x"], data["y"])
    axes.set_title(title)
    axes.tick_params(axis="x", rotation=30)
    figure.tight_layout()
```

`ui/panels.py`
```python
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ControlsPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)

        self.file_label = QLabel("未导入文件")
        self.drop_empty_checkbox = QCheckBox("去除全空行")
        self.drop_duplicates_checkbox = QCheckBox("去除重复行")
        self.sort_column_combo = QComboBox()
        self.sort_order_combo = QComboBox()
        self.sort_order_combo.addItems(["升序", "降序"])
        self.filter_column_combo = QComboBox()
        self.filter_keyword_input = QLineEdit()
        self.calc_name_input = QLineEdit()
        self.calc_left_combo = QComboBox()
        self.calc_operator_combo = QComboBox()
        self.calc_operator_combo.addItems(["+", "-", "*", "/"])
        self.calc_right_combo = QComboBox()
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["bar", "line"])
        self.chart_category_combo = QComboBox()
        self.chart_value_combo = QComboBox()
        self.run_button = QPushButton("执行处理")
        self.export_button = QPushButton("导出结果")

        source_group = QGroupBox("数据源")
        source_layout = QVBoxLayout(source_group)
        source_layout.addWidget(self.file_label)

        transform_group = QGroupBox("处理配置")
        transform_form = QFormLayout(transform_group)
        transform_form.addRow(self.drop_empty_checkbox)
        transform_form.addRow(self.drop_duplicates_checkbox)
        transform_form.addRow("排序列", self.sort_column_combo)
        transform_form.addRow("排序方式", self.sort_order_combo)
        transform_form.addRow("筛选列", self.filter_column_combo)
        transform_form.addRow("筛选关键词", self.filter_keyword_input)
        transform_form.addRow("新列名称", self.calc_name_input)
        transform_form.addRow("左侧列", self.calc_left_combo)
        transform_form.addRow("运算符", self.calc_operator_combo)
        transform_form.addRow("右侧列", self.calc_right_combo)

        chart_group = QGroupBox("图表配置")
        chart_form = QFormLayout(chart_group)
        chart_form.addRow("图表类型", self.chart_type_combo)
        chart_form.addRow("分类列", self.chart_category_combo)
        chart_form.addRow("数值列", self.chart_value_combo)

        buttons = QHBoxLayout()
        buttons.addWidget(self.run_button)
        buttons.addWidget(self.export_button)

        layout.addWidget(source_group)
        layout.addWidget(transform_group)
        layout.addWidget(chart_group)
        layout.addLayout(buttons)
        layout.addStretch()


class ChartPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/services/chart/test_render.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add ui/panels.py services/chart/render.py tests/services/chart/test_render.py
git commit -m "feat: add chart canvas and control panels"
```

### Task 7: Build main window workflow

**Files:**
- Create: `ui/main_window.py`
- Modify: `app/state.py`
- Test: `tests/ui/test_main_window.py`

- [ ] **Step 1: Write the failing UI workflow tests**

`tests/ui/test_main_window.py`
```python
import pandas as pd
from PySide6.QtWidgets import QFileDialog

from ui.main_window import MainWindow


def test_main_window_loads_dataframe_into_table(monkeypatch, qtbot, tmp_path):
    source = tmp_path / "demo.xlsx"
    pd.DataFrame({"name": ["A"], "value": [10]}).to_excel(source, index=False)

    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args, **kwargs: (str(source), ""))

    window = MainWindow()
    qtbot.addWidget(window)

    window.load_excel_file()

    assert window.state.source_path == source
    assert window.raw_model.rowCount() == 1
    assert window.controls.file_label.text().endswith("demo.xlsx")


def test_main_window_runs_processing_and_updates_result_model(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    window.load_dataframe(pd.DataFrame([
        {"category": "A", "value": 1},
        {"category": "A", "value": 1},
        {"category": None, "value": None},
    ]), "Sheet1")

    window.controls.drop_empty_checkbox.setChecked(True)
    window.controls.drop_duplicates_checkbox.setChecked(True)

    window.run_transformations()

    assert window.result_model.rowCount() == 1
    assert window.tabs.tabText(1) == "处理结果"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/ui/test_main_window.py -v`
Expected: FAIL with import errors.

- [ ] **Step 3: Write minimal implementation**

Replace `app/state.py` with:
```python
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd


@dataclass
class AppState:
    source_path: Path | None = None
    sheet_name: str | None = None
    raw_frame: pd.DataFrame | None = None
    result_frame: pd.DataFrame | None = None
    selected_chart_type: str = "bar"
    last_export_path: Path | None = None
    available_columns: list[str] = field(default_factory=list)
```

`ui/main_window.py`
```python
from pathlib import Path

import pandas as pd
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QTabWidget,
    QTableView,
    QWidget,
)

from app.state import AppState
from services.chart.render import build_chart_series, draw_chart
from services.excel.io import export_dataframe, load_first_sheet
from services.transform.operations import (
    add_calculated_column,
    apply_contains_filter,
    apply_sort,
    drop_duplicate_rows,
    drop_empty_rows,
)
from ui.panels import ChartPanel, ControlsPanel
from ui.table_model import DataFrameTableModel


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("桌面数据分析器")
        self.resize(1400, 900)
        self.state = AppState()

        self.controls = ControlsPanel()
        self.chart_panel = ChartPanel()
        self.raw_model = DataFrameTableModel()
        self.result_model = DataFrameTableModel()

        self.raw_table = QTableView()
        self.raw_table.setModel(self.raw_model)
        self.result_table = QTableView()
        self.result_table.setModel(self.result_model)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.raw_table, "原始数据")
        self.tabs.addTab(self.result_table, "处理结果")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.addWidget(self.controls, 2)
        layout.addWidget(self.tabs, 5)
        layout.addWidget(self.chart_panel, 4)

        self._create_actions()

    def _create_actions(self) -> None:
        self.controls.run_button.clicked.connect(self.run_transformations)
        self.controls.export_button.clicked.connect(self.export_result)

    def load_excel_file(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(self, "选择 Excel 文件", "", "Excel Files (*.xlsx *.xls)")
        if not file_name:
            return
        frame, sheet_name = load_first_sheet(Path(file_name))
        self.load_dataframe(frame, sheet_name, Path(file_name))

    def load_dataframe(self, frame: pd.DataFrame, sheet_name: str, source_path: Path | None = None) -> None:
        self.state.raw_frame = frame.copy()
        self.state.result_frame = frame.copy()
        self.state.sheet_name = sheet_name
        self.state.source_path = source_path
        self.state.available_columns = [str(column) for column in frame.columns]
        self.raw_model.set_frame(frame)
        self.result_model.set_frame(frame)
        self.controls.file_label.setText(source_path.name if source_path else sheet_name)
        self._populate_column_controls()
        self._refresh_chart(frame)

    def _populate_column_controls(self) -> None:
        combos = [
            self.controls.sort_column_combo,
            self.controls.filter_column_combo,
            self.controls.calc_left_combo,
            self.controls.calc_right_combo,
            self.controls.chart_category_combo,
            self.controls.chart_value_combo,
        ]
        for combo in combos:
            combo.clear()
            combo.addItem("")
            combo.addItems(self.state.available_columns)

    def run_transformations(self) -> None:
        if self.state.raw_frame is None:
            QMessageBox.warning(self, "提示", "请先导入 Excel 文件")
            return
        frame = self.state.raw_frame.copy()
        if self.controls.drop_empty_checkbox.isChecked():
            frame = drop_empty_rows(frame)
        if self.controls.drop_duplicates_checkbox.isChecked():
            frame = drop_duplicate_rows(frame)
        if self.controls.filter_column_combo.currentText() and self.controls.filter_keyword_input.text().strip():
            frame = apply_contains_filter(
                frame,
                self.controls.filter_column_combo.currentText(),
                self.controls.filter_keyword_input.text().strip(),
            )
        if self.controls.sort_column_combo.currentText():
            frame = apply_sort(
                frame,
                self.controls.sort_column_combo.currentText(),
                self.controls.sort_order_combo.currentText() == "升序",
            )
        if all([
            self.controls.calc_name_input.text().strip(),
            self.controls.calc_left_combo.currentText(),
            self.controls.calc_right_combo.currentText(),
        ]):
            frame = add_calculated_column(
                frame,
                self.controls.calc_name_input.text().strip(),
                self.controls.calc_left_combo.currentText(),
                self.controls.calc_right_combo.currentText(),
                self.controls.calc_operator_combo.currentText(),
            )

        self.state.result_frame = frame
        self.result_model.set_frame(frame)
        self._populate_column_controls_from_result(frame)
        self._refresh_chart(frame)
        self.tabs.setCurrentIndex(1)

    def _populate_column_controls_from_result(self, frame: pd.DataFrame) -> None:
        self.state.available_columns = [str(column) for column in frame.columns]
        current_category = self.controls.chart_category_combo.currentText()
        current_value = self.controls.chart_value_combo.currentText()
        self._populate_column_controls()
        if current_category in self.state.available_columns:
            self.controls.chart_category_combo.setCurrentText(current_category)
        if current_value in self.state.available_columns:
            self.controls.chart_value_combo.setCurrentText(current_value)

    def _refresh_chart(self, frame: pd.DataFrame) -> None:
        category_column = self.controls.chart_category_combo.currentText()
        value_column = self.controls.chart_value_combo.currentText()
        if not category_column or not value_column or frame.empty:
            self.chart_panel.figure.clear()
            self.chart_panel.canvas.draw_idle()
            return
        data = build_chart_series(frame, category_column, value_column)
        draw_chart(self.chart_panel.figure, data, self.controls.chart_type_combo.currentText(), "数据图表")
        self.chart_panel.canvas.draw_idle()

    def export_result(self) -> None:
        if self.state.result_frame is None or self.state.result_frame.empty:
            QMessageBox.warning(self, "提示", "没有可导出的处理结果")
            return
        file_name, _ = QFileDialog.getSaveFileName(self, "导出结果", "processed_output.xlsx", "Excel Files (*.xlsx)")
        if not file_name:
            return
        target = Path(file_name)
        export_dataframe(self.state.result_frame, target)
        self.state.last_export_path = target
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/ui/test_main_window.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/state.py ui/main_window.py tests/ui/test_main_window.py
git commit -m "feat: add main workbench window"
```

### Task 8: Add app bootstrap and launch wiring

**Files:**
- Create: `app/bootstrap.py`
- Modify: `ui/main_window.py`
- Test: `tests/ui/test_main_window.py`

- [ ] **Step 1: Extend tests with app bootstrap assertion**

Append to `tests/ui/test_main_window.py`:
```python
from app.bootstrap import create_window


def test_create_window_returns_visible_main_window(qtbot):
    window = create_window()
    qtbot.addWidget(window)

    assert window.windowTitle() == "桌面数据分析器"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/ui/test_main_window.py -v`
Expected: FAIL with missing `create_window`.

- [ ] **Step 3: Write minimal implementation**

`app/bootstrap.py`
```python
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow


def create_window() -> MainWindow:
    return MainWindow()


def run() -> int:
    app = QApplication.instance() or QApplication([])
    window = create_window()
    window.show()
    return app.exec()
```

Modify `ui/main_window.py` to add a toolbar import and load button wiring:
```python
from PySide6.QtGui import QAction
```

Inside `__init__` after `self._create_actions()` add:
```python
        toolbar = self.addToolBar("主工具栏")
        load_action = QAction("导入 Excel", self)
        load_action.triggered.connect(self.load_excel_file)
        toolbar.addAction(load_action)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/ui/test_main_window.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/bootstrap.py ui/main_window.py tests/ui/test_main_window.py
git commit -m "feat: wire app bootstrap and import action"
```

### Task 9: Add manual demo workbook and end-to-end verification test

**Files:**
- Create: `sample_data/demo_sales.xlsx`
- Modify: `tests/services/excel/test_io.py`
- Modify: `tests/ui/test_main_window.py`

- [ ] **Step 1: Write the failing integration-style tests**

Append to `tests/services/excel/test_io.py`:
```python
from pathlib import Path


def test_demo_workbook_exists():
    assert Path("sample_data/demo_sales.xlsx").exists()
```

Append to `tests/ui/test_main_window.py`:
```python
import pandas as pd


def test_main_window_can_export_processed_results(monkeypatch, qtbot, tmp_path):
    output = tmp_path / "result.xlsx"
    window = MainWindow()
    qtbot.addWidget(window)
    window.load_dataframe(pd.DataFrame([{"category": "A", "value": 2}]), "Sheet1")

    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args, **kwargs: (str(output), ""))

    window.export_result()

    assert output.exists()
    assert window.state.last_export_path == output
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/services/excel/test_io.py tests/ui/test_main_window.py -v`
Expected: FAIL with missing demo workbook or export flow issues.

- [ ] **Step 3: Write minimal implementation**

Create `sample_data/demo_sales.xlsx` with one worksheet named `Sheet1` containing:

| 日期 | 分类 | 数值 |
|---|---|---|
| 2026-05-01 | A类 | 100 |
| 2026-05-02 | A类 | 120 |
| 2026-05-03 | B类 | 90 |
| 2026-05-03 | B类 | 90 |
| 2026-05-04 | 空白 | *(empty value)* |

No code changes required if export flow already passes.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/services/excel/test_io.py tests/ui/test_main_window.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add sample_data/demo_sales.xlsx tests/services/excel/test_io.py tests/ui/test_main_window.py
git commit -m "test: add demo workbook and export coverage"
```

### Task 10: Run full verification and document execution commands in CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Write the failing documentation test**

Append to `tests/conftest.py`:
```python

def test_claude_md_mentions_run_and_test_commands():
    content = Path("CLAUDE.md").read_text(encoding="utf-8")
    assert "python main.py" in content
    assert "pytest" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/conftest.py -v`
Expected: FAIL because `CLAUDE.md` does not yet mention actual commands.

- [ ] **Step 3: Write minimal implementation**

Update `CLAUDE.md` command section to include:

```md
## 常用命令

### 安装依赖
```powershell
pip install -r requirements.txt
```

### 启动桌面程序
```powershell
python main.py
```

### 运行全部测试
```powershell
pytest
```

### 运行单个测试
```powershell
pytest tests/ui/test_main_window.py -v
```
```

- [ ] **Step 4: Run full verification**

Run: `pytest -v`
Expected: PASS

Run: `python main.py`
Expected: application window opens with title `桌面数据分析器`

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md tests/conftest.py
git commit -m "docs: add verified commands for desktop analyzer"
```

## Self-review

- Spec coverage check:
  - Excel import/export: Task 2 and Task 9
  - Basic transformations: Task 3 and Task 7
  - Bar/line charts: Task 4 and Task 6
  - Single-window workbench UI: Task 6, Task 7, Task 8
  - Source-runnable first version: Task 1, Task 8, Task 10
  - Export workflow: Task 2 and Task 9
- Placeholder scan: no `TODO`, `TBD`, or unresolved references remain.
- Type consistency check:
  - `AppState`, `MainWindow`, `build_chart_series`, `draw_chart`, `load_first_sheet`, and `export_dataframe` are defined once and referenced consistently.
