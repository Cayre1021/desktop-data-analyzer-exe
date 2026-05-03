# UI Polish and Directory EXE Packaging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the current first-version desktop data analyzer into a more polished desktop workbench with clearer states, better defaults, reset support, and reproducible directory-style Windows `.exe` packaging.

**Architecture:** Keep the current PySide6 single-window structure, but improve it by adding explicit view-state handling, richer control metadata, status feedback, and packaging scripts around the existing app. UI behavior remains centered in `ui/main_window.py`, while reusable widgets and chart helpers absorb the polish work so packaging can stay thin and mechanical.

**Tech Stack:** Python 3.14, PySide6, pandas, openpyxl, matplotlib, pytest, pytest-qt, PyInstaller

---

## Planned file structure

- `app/state.py` — expanded UI state for source metadata, status text, and reset behavior
- `app/bootstrap.py` — launch helpers, unchanged except for packaging-safe defaults if needed
- `ui/main_window.py` — main workbench layout, status bar, reset flow, default chart behavior, export feedback
- `ui/panels.py` — richer left-side cards for data source summary, controls, and action buttons
- `ui/table_model.py` — reused as-is unless a small display helper is required
- `services/chart/render.py` — chart drawing plus empty-state rendering helper
- `tests/ui/test_main_window.py` — workflow tests for status messages, reset behavior, and export feedback
- `tests/services/chart/test_render.py` — chart empty-state tests
- `tests/test_project_skeleton.py` — command docs assertions, updated for packaging commands
- `requirements.txt` — add PyInstaller runtime build dependency if chosen for repo-managed install flow
- `desktop-data-analyzer.spec` — PyInstaller spec for directory build
- `scripts/build_exe.py` — Python build helper that runs PyInstaller with the project spec
- `CLAUDE.md` — verified commands for run, test, and build

### Task 1: Add status-aware app state

**Files:**
- Modify: `app/state.py`
- Test: `tests/ui/test_table_model.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/ui/test_table_model.py`:

```python
def test_app_state_tracks_status_and_source_summary():
    state = AppState()

    assert state.status_message == "未导入文件"
    assert state.source_summary == ""
    assert state.last_export_path is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/ui/test_table_model.py::test_app_state_tracks_status_and_source_summary -v`
Expected: FAIL with `AttributeError` for missing `status_message`.

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
    status_message: str = "未导入文件"
    source_summary: str = ""
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/ui/test_table_model.py::test_app_state_tracks_status_and_source_summary -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/state.py tests/ui/test_table_model.py
git commit -m "feat: track polished UI state"
```

### Task 2: Add chart empty-state rendering helper

**Files:**
- Modify: `services/chart/render.py`
- Test: `tests/services/chart/test_render.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/services/chart/test_render.py`:

```python
def test_draw_empty_chart_state_shows_message_in_axes_text():
    figure = Figure()

    draw_empty_chart_state(figure, "暂无可用图表")

    assert len(figure.axes) == 1
    assert figure.axes[0].texts[0].get_text() == "暂无可用图表"
```

Also update the import line to:

```python
from services.chart.render import build_chart_series, draw_chart, draw_empty_chart_state
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/services/chart/test_render.py::test_draw_empty_chart_state_shows_message_in_axes_text -v`
Expected: FAIL with import error for `draw_empty_chart_state`.

- [ ] **Step 3: Write minimal implementation**

Append to `services/chart/render.py`:

```python
def draw_empty_chart_state(figure: Figure, message: str) -> None:
    figure.clear()
    axes = figure.add_subplot(111)
    axes.set_xticks([])
    axes.set_yticks([])
    for spine in axes.spines.values():
        spine.set_visible(False)
    axes.text(0.5, 0.5, message, ha="center", va="center", fontsize=12)
    figure.tight_layout()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/services/chart/test_render.py::test_draw_empty_chart_state_shows_message_in_axes_text -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add services/chart/render.py tests/services/chart/test_render.py
git commit -m "feat: add chart empty state rendering"
```

### Task 3: Polish left-side control panel and add reset action

**Files:**
- Modify: `ui/panels.py`
- Test: `tests/ui/test_main_window.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/ui/test_main_window.py`:

```python
def test_controls_panel_exposes_reset_button(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)

    assert window.controls.reset_button.text() == "重置工作区"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/ui/test_main_window.py::test_controls_panel_exposes_reset_button -v`
Expected: FAIL with `AttributeError` for missing `reset_button`.

- [ ] **Step 3: Write minimal implementation**

Update the button area in `ui/panels.py` so `ControlsPanel.__init__` includes:

```python
        self.reset_button = QPushButton("重置工作区")
```

And change the button layout block to:

```python
        buttons = QVBoxLayout()
        buttons.addWidget(self.run_button)
        buttons.addWidget(self.export_button)
        buttons.addWidget(self.reset_button)
```

Also add a source summary label after `self.file_label`:

```python
        self.source_summary_label = QLabel("")
        self.source_summary_label.setWordWrap(True)
```

And add it into `source_layout`:

```python
        source_layout.addWidget(self.source_summary_label)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/ui/test_main_window.py::test_controls_panel_exposes_reset_button -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add ui/panels.py tests/ui/test_main_window.py
git commit -m "feat: add reset control and source summary panel"
```

### Task 4: Add status bar, source summary, and reset workflow to main window

**Files:**
- Modify: `ui/main_window.py`
- Test: `tests/ui/test_main_window.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/ui/test_main_window.py`:

```python
def test_main_window_updates_status_and_summary_after_loading(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)

    frame = pd.DataFrame([
        {"分类": "A类", "数值": 1},
        {"分类": "B类", "数值": 2},
    ])
    window.load_dataframe(frame, "Sheet1")

    assert window.statusBar().currentMessage() == "已导入 2 行 × 2 列"
    assert "Sheet1" in window.controls.source_summary_label.text()


def test_main_window_reset_workspace_clears_models_and_state(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    window.load_dataframe(pd.DataFrame([{"分类": "A类", "数值": 1}]), "Sheet1")

    window.reset_workspace()

    assert window.state.raw_frame is None
    assert window.state.result_frame is None
    assert window.raw_model.rowCount() == 0
    assert window.result_model.rowCount() == 0
    assert window.statusBar().currentMessage() == "工作区已重置"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/ui/test_main_window.py::test_main_window_updates_status_and_summary_after_loading tests/ui/test_main_window.py::test_main_window_reset_workspace_clears_models_and_state -v`
Expected: FAIL with missing summary/status/reset behavior.

- [ ] **Step 3: Write minimal implementation**

Make these focused updates in `ui/main_window.py`:

1. Update imports to include `QStatusBar` only if you choose to instantiate it directly; otherwise use `self.statusBar()`.

2. In `__init__` after toolbar setup add:

```python
        self.statusBar().showMessage(self.state.status_message)
```

3. In `_create_actions()` add:

```python
        self.controls.reset_button.clicked.connect(self.reset_workspace)
```

4. In `load_dataframe()` after setting `source_path` add:

```python
        rows, columns = frame.shape
        self.state.source_summary = f"工作表：{sheet_name} | 行数：{rows} | 列数：{columns}"
        self.state.status_message = f"已导入 {rows} 行 × {columns} 列"
```

Then after `self.controls.file_label.setText(...)` add:

```python
        self.controls.source_summary_label.setText(self.state.source_summary)
        self.statusBar().showMessage(self.state.status_message)
```

5. Add a new method to `MainWindow`:

```python
    def reset_workspace(self) -> None:
        self.state = AppState(status_message="工作区已重置")
        empty_frame = pd.DataFrame()
        self.raw_model.set_frame(empty_frame)
        self.result_model.set_frame(empty_frame)
        self.controls.file_label.setText("未导入文件")
        self.controls.source_summary_label.setText("")
        for combo in [
            self.controls.sort_column_combo,
            self.controls.filter_column_combo,
            self.controls.calc_left_combo,
            self.controls.calc_right_combo,
            self.controls.chart_category_combo,
            self.controls.chart_value_combo,
        ]:
            combo.clear()
            combo.addItem("")
        self.controls.filter_keyword_input.clear()
        self.controls.calc_name_input.clear()
        self.chart_panel.figure.clear()
        self.chart_panel.canvas.draw_idle()
        self.statusBar().showMessage(self.state.status_message)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/ui/test_main_window.py::test_main_window_updates_status_and_summary_after_loading tests/ui/test_main_window.py::test_main_window_reset_workspace_clears_models_and_state -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add ui/main_window.py tests/ui/test_main_window.py
 git commit -m "feat: add status bar and reset workflow"
```

### Task 5: Add better default chart behavior and export feedback

**Files:**
- Modify: `ui/main_window.py`
- Test: `tests/ui/test_main_window.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/ui/test_main_window.py`:

```python
def test_main_window_selects_default_chart_columns_after_loading(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)

    frame = pd.DataFrame([
        {"日期": "2026-05-01", "数值": 10},
        {"日期": "2026-05-02", "数值": 20},
    ])
    window.load_dataframe(frame, "Sheet1")

    assert window.controls.chart_category_combo.currentText() == "日期"
    assert window.controls.chart_value_combo.currentText() == "数值"


def test_main_window_export_updates_status_bar(monkeypatch, qtbot, tmp_path):
    output = tmp_path / "export.xlsx"
    window = MainWindow()
    qtbot.addWidget(window)
    window.load_dataframe(pd.DataFrame([{"分类": "A类", "数值": 3}]), "Sheet1")

    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args, **kwargs: (str(output), ""))

    window.export_result()

    assert "导出成功" in window.statusBar().currentMessage()
    assert str(output) in window.statusBar().currentMessage()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/ui/test_main_window.py::test_main_window_selects_default_chart_columns_after_loading tests/ui/test_main_window.py::test_main_window_export_updates_status_bar -v`
Expected: FAIL because defaults/status are not set.

- [ ] **Step 3: Write minimal implementation**

In `ui/main_window.py`, add this helper method inside `MainWindow`:

```python
    def _set_default_chart_columns(self, frame: pd.DataFrame) -> None:
        if frame.empty:
            return
        columns = [str(column) for column in frame.columns]
        numeric_columns = [str(column) for column in frame.select_dtypes(include="number").columns]
        if columns:
            self.controls.chart_category_combo.setCurrentText(columns[0])
        if numeric_columns:
            self.controls.chart_value_combo.setCurrentText(numeric_columns[0])
```

Call it in `load_dataframe()` after `_populate_column_controls()`:

```python
        self._set_default_chart_columns(frame)
```

Update `export_result()` after `self.state.last_export_path = target`:

```python
        self.state.status_message = f"导出成功：{target}"
        self.statusBar().showMessage(self.state.status_message)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/ui/test_main_window.py::test_main_window_selects_default_chart_columns_after_loading tests/ui/test_main_window.py::test_main_window_export_updates_status_bar -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add ui/main_window.py tests/ui/test_main_window.py
 git commit -m "feat: improve default chart behavior and export feedback"
```

### Task 6: Show an explicit empty chart state in the workbench

**Files:**
- Modify: `ui/main_window.py`
- Test: `tests/ui/test_main_window.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/ui/test_main_window.py`:

```python
def test_main_window_shows_empty_chart_message_without_chart_columns(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)

    window.reset_workspace()

    assert window.chart_panel.figure.axes[0].texts[0].get_text() == "暂无可用图表"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/ui/test_main_window.py::test_main_window_shows_empty_chart_message_without_chart_columns -v`
Expected: FAIL because no explicit chart message exists.

- [ ] **Step 3: Write minimal implementation**

Update the import line in `ui/main_window.py` to:

```python
from services.chart.render import build_chart_series, draw_chart, draw_empty_chart_state
```

Replace the empty-state branch in `_refresh_chart()` with:

```python
        if not category_column or not value_column or frame.empty:
            draw_empty_chart_state(self.chart_panel.figure, "暂无可用图表")
            self.chart_panel.canvas.draw_idle()
            return
```

Also update `reset_workspace()` so the chart branch becomes:

```python
        draw_empty_chart_state(self.chart_panel.figure, "暂无可用图表")
        self.chart_panel.canvas.draw_idle()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/ui/test_main_window.py::test_main_window_shows_empty_chart_message_without_chart_columns -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add ui/main_window.py tests/ui/test_main_window.py
 git commit -m "feat: show explicit empty chart state"
```

### Task 7: Add PyInstaller build config and build helper

**Files:**
- Create: `desktop-data-analyzer.spec`
- Create: `scripts/build_exe.py`
- Test: `tests/test_project_skeleton.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_project_skeleton.py`:

```python
def test_packaging_files_exist():
    assert Path("desktop-data-analyzer.spec").exists()
    assert Path("scripts/build_exe.py").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_project_skeleton.py::test_packaging_files_exist -v`
Expected: FAIL because packaging files do not exist.

- [ ] **Step 3: Write minimal implementation**

Create `desktop-data-analyzer.spec` with:

```python
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

project_root = Path(__file__).resolve().parent
hiddenimports = collect_submodules("matplotlib.backends")


a = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=[(str(project_root / "sample_data"), "sample_data")],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="desktop-data-analyzer",
    console=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="desktop-data-analyzer",
)
```

Create `scripts/build_exe.py` with:

```python
from pathlib import Path
import subprocess
import sys


def main() -> int:
    project_root = Path(__file__).resolve().parent.parent
    spec_path = project_root / "desktop-data-analyzer.spec"
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        str(spec_path),
    ]
    return subprocess.call(command, cwd=project_root)


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_project_skeleton.py::test_packaging_files_exist -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add desktop-data-analyzer.spec scripts/build_exe.py tests/test_project_skeleton.py
 git commit -m "build: add PyInstaller directory build config"
```

### Task 8: Document build commands and add repo-managed PyInstaller dependency

**Files:**
- Modify: `requirements.txt`
- Modify: `CLAUDE.md`
- Test: `tests/test_project_skeleton.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_project_skeleton.py`:

```python
def test_claude_md_mentions_build_command():
    content = Path("CLAUDE.md").read_text(encoding="utf-8")
    assert "python scripts/build_exe.py" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_project_skeleton.py::test_claude_md_mentions_build_command -v`
Expected: FAIL because build command is undocumented.

- [ ] **Step 3: Write minimal implementation**

Append this line to `requirements.txt`:

```text
pyinstaller>=6.15,<6.16
```

Update `CLAUDE.md` command section so it includes:

```md
### 构建目录版 exe
```powershell
python scripts/build_exe.py
```
```

Also add one short sentence under the command block stating that the output directory will be created under `dist/desktop-data-analyzer/`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_project_skeleton.py::test_claude_md_mentions_build_command -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add requirements.txt CLAUDE.md tests/test_project_skeleton.py
 git commit -m "docs: add build command and packaging dependency"
```

### Task 9: Run full verification and produce a directory build

**Files:**
- Modify: `CLAUDE.md` only if commands or output path need correction after verification

- [ ] **Step 1: Run full test suite**

Run: `python -m pytest -v`
Expected: PASS

- [ ] **Step 2: Install repo-managed dependencies if needed**

Run: `python -m pip install -r requirements.txt`
Expected: PASS with PyInstaller installed.

- [ ] **Step 3: Run the directory build**

Run: `python scripts/build_exe.py`
Expected: PASS with build output under `dist/desktop-data-analyzer/`.

- [ ] **Step 4: Verify built app can construct the main window**

Run: `dist\desktop-data-analyzer\desktop-data-analyzer.exe`
Expected: app launches successfully.

If non-interactive verification is safer first, run:

```powershell
python -c "from app.bootstrap import create_window; from PySide6.QtWidgets import QApplication; app = QApplication.instance() or QApplication([]); window = create_window(); print(window.windowTitle())"
```

Expected output: `桌面数据分析器`

- [ ] **Step 5: Commit**

```bash
git add requirements.txt CLAUDE.md desktop-data-analyzer.spec scripts/build_exe.py app/state.py services/chart/render.py ui/panels.py ui/main_window.py tests/test_project_skeleton.py tests/services/chart/test_render.py tests/ui/test_main_window.py
 git commit -m "feat: polish desktop UI and package directory build"
```

## Self-review

- Spec coverage check:
  - Status bar, source summary, reset workflow: Tasks 1, 3, 4, 5
  - Better empty states and default chart behavior: Tasks 2, 5, 6
  - Stronger polished desktop interactions: Tasks 3, 4, 5, 6
  - PyInstaller directory packaging: Tasks 7, 8, 9
  - Updated docs and verified commands: Tasks 8, 9
- Placeholder scan: no `TODO`, `TBD`, or incomplete task references remain.
- Type consistency check:
  - `status_message`, `source_summary`, `reset_workspace`, `_set_default_chart_columns`, and `draw_empty_chart_state` are defined before later tasks reference them.
