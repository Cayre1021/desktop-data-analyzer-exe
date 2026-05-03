import pandas as pd
from PySide6.QtWidgets import QFileDialog, QMessageBox

from app.bootstrap import create_window
from ui.help_dialogs import FullGuideDialog, GuideModeDialog, StepGuideDialog
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


def test_create_window_returns_visible_main_window(qtbot):
    window = create_window()
    qtbot.addWidget(window)

    assert window.windowTitle() == "桌面数据分析器"


def test_main_window_can_export_processed_results(monkeypatch, qtbot, tmp_path):
    output = tmp_path / "result.xlsx"
    window = MainWindow()
    qtbot.addWidget(window)
    window.load_dataframe(pd.DataFrame([{"category": "A", "value": 2}]), "Sheet1")

    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args, **kwargs: (str(output), ""))

    window.export_result()

    assert output.exists()
    assert window.state.last_export_path == output


def test_controls_panel_exposes_reset_button(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)

    assert window.controls.reset_button.text() == "重置工作区"


def test_main_window_exposes_novice_guide_action(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)

    toolbar_actions = [action.text() for action in window.findChildren(type(window.addToolBar("tmp").toggleViewAction())) if action.text()]

    assert "新手引导" in toolbar_actions


def test_main_window_updates_status_and_summary_after_loading(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)

    frame = pd.DataFrame([
        {"分类": "A类", "数值": 1},
        {"分类": "B类", "数值": 2},
    ])
    window.load_dataframe(frame, "Sheet1")

    assert "已导入 2 行 × 2 列" in window.statusBar().currentMessage()
    assert "日志" in window.statusBar().currentMessage()
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
    assert "工作区已重置" in window.statusBar().currentMessage()


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
    assert "export.xlsx" in window.statusBar().currentMessage()


def test_main_window_shows_empty_chart_message_without_chart_columns(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)

    window.reset_workspace()

    assert window.chart_panel.figure.axes[0].texts[0].get_text() == "暂无可用图表"


def test_main_window_shows_message_when_excel_load_fails(monkeypatch, qtbot, tmp_path):
    source = tmp_path / "broken.xls"
    source.write_text("broken", encoding="utf-8")
    messages: list[tuple[str, str]] = []

    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args, **kwargs: (str(source), ""))
    monkeypatch.setattr("ui.main_window.load_first_sheet", lambda path: (_ for _ in ()).throw(ValueError("无法读取该 Excel 文件")))
    monkeypatch.setattr(QMessageBox, "critical", lambda parent, title, text: messages.append((title, text)))

    window = MainWindow()
    qtbot.addWidget(window)

    window.load_excel_file()

    assert messages == [("导入失败", "导入失败：无法读取该 Excel 文件")]
    assert window.state.raw_frame is None


def test_main_window_shows_processing_error_when_calculation_fails(monkeypatch, qtbot):
    messages: list[tuple[str, str]] = []
    window = MainWindow()
    qtbot.addWidget(window)
    window.load_dataframe(pd.DataFrame([{"A": "bad", "B": 0}]), "Sheet1")
    window.controls.calc_name_input.setText("结果")
    window.controls.calc_left_combo.setCurrentText("A")
    window.controls.calc_right_combo.setCurrentText("B")
    window.controls.calc_operator_combo.setCurrentText("/")

    monkeypatch.setattr(QMessageBox, "critical", lambda parent, title, text: messages.append((title, text)))

    window.run_transformations()

    assert messages
    assert messages[0][0] == "处理失败"
    assert "处理失败：" in messages[0][1]


def test_main_window_shows_chart_failure_message_when_chart_build_breaks(monkeypatch, qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    window.load_dataframe(pd.DataFrame([{"分类": "A", "数值": 1}]), "Sheet1")

    monkeypatch.setattr("ui.main_window.build_chart_series", lambda *args, **kwargs: (_ for _ in ()).throw(ValueError("图表坏了")))

    window._refresh_chart(window.state.result_frame)

    assert window.chart_panel.figure.axes[0].texts[0].get_text() == "图表生成失败"


def test_guide_mode_dialog_defaults_to_manual_choice(qtbot):
    dialog = GuideModeDialog()
    qtbot.addWidget(dialog)

    assert dialog.selected_mode is None


def test_step_guide_dialog_moves_to_next_step_and_finishes(qtbot):
    dialog = StepGuideDialog()
    qtbot.addWidget(dialog)

    assert "第 1/8 步" in dialog.title_label.text()
    for _ in range(7):
        dialog.next_step()
    assert dialog.next_button.text() == "完成"


def test_full_guide_dialog_loads_markdown_content(qtbot):
    dialog = FullGuideDialog()
    qtbot.addWidget(dialog)

    browser = dialog.findChild(type(dialog.findChildren(object)[1]))
    assert dialog.windowTitle() == "完整说明"
