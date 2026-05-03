from pathlib import Path

import pandas as pd
from PySide6.QtGui import QAction
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
from services.chart.render import build_chart_series, draw_chart, draw_empty_chart_state
from services.excel.io import export_dataframe, load_first_sheet
from services.logging import format_log_size_mb, log_exception, log_user_action, log_warning
from services.transform.operations import (
    add_calculated_column,
    apply_contains_filter,
    apply_sort,
    drop_duplicate_rows,
    drop_empty_rows,
)
from ui.help_dialogs import open_novice_guide
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
        toolbar = self.addToolBar("主工具栏")
        load_action = QAction("导入 Excel", self)
        load_action.triggered.connect(self.load_excel_file)
        toolbar.addAction(load_action)
        guide_action = QAction("新手引导", self)
        guide_action.triggered.connect(self.show_novice_guide)
        toolbar.addAction(guide_action)
        self._show_status(self.state.status_message)
        draw_empty_chart_state(self.chart_panel.figure, "暂无可用图表")
        self.chart_panel.canvas.draw_idle()
        log_user_action("main_window_ready", title=self.windowTitle())

    def _create_actions(self) -> None:
        self.controls.run_button.clicked.connect(self.run_transformations)
        self.controls.export_button.clicked.connect(self.export_result)
        self.controls.reset_button.clicked.connect(self.reset_workspace)

    def _show_status(self, message: str) -> None:
        self.statusBar().showMessage(f"{message}（日志 {format_log_size_mb()}）")

    def _show_error(self, title: str, message: str) -> None:
        QMessageBox.critical(self, title, message)
        self.state.status_message = message
        self._show_status(message)

    def show_novice_guide(self) -> None:
        log_user_action("guide_opened")
        open_novice_guide(self)

    def load_excel_file(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(self, "选择 Excel 文件", "", "Excel Files (*.xlsx *.xls)")
        if not file_name:
            log_warning("import_cancelled", "用户取消导入")
            return
        source_path = Path(file_name)
        log_user_action("import_selected", file_name=source_path.name)
        try:
            frame, sheet_name = load_first_sheet(source_path)
        except Exception as exc:
            log_exception("import_failed", exc, file_name=source_path.name)
            self._show_error("导入失败", f"导入失败：{exc}")
            return
        self.load_dataframe(frame, sheet_name, source_path)

    def load_dataframe(self, frame: pd.DataFrame, sheet_name: str, source_path: Path | None = None) -> None:
        self.state.raw_frame = frame.copy()
        self.state.result_frame = frame.copy()
        self.state.sheet_name = sheet_name
        self.state.source_path = source_path
        self.state.available_columns = [str(column) for column in frame.columns]
        rows, columns = frame.shape
        self.state.source_summary = f"工作表：{sheet_name} | 行数：{rows} | 列数：{columns}"
        self.state.status_message = f"已导入 {rows} 行 × {columns} 列"
        self.raw_model.set_frame(frame)
        self.result_model.set_frame(frame)
        self.controls.file_label.setText(source_path.name if source_path else sheet_name)
        self.controls.source_summary_label.setText(self.state.source_summary)
        self._populate_column_controls()
        self._set_default_chart_columns(frame)
        self._refresh_chart(frame)
        self._show_status(self.state.status_message)
        log_user_action(
            "import_completed",
            file_name=source_path.name if source_path else sheet_name,
            sheet_name=sheet_name,
            rows=rows,
            columns=columns,
        )

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

    def _set_default_chart_columns(self, frame: pd.DataFrame) -> None:
        if frame.empty:
            return
        columns = [str(column) for column in frame.columns]
        numeric_columns = [str(column) for column in frame.select_dtypes(include="number").columns]
        if columns:
            self.controls.chart_category_combo.setCurrentText(columns[0])
        if numeric_columns:
            self.controls.chart_value_combo.setCurrentText(numeric_columns[0])

    def run_transformations(self) -> None:
        if self.state.raw_frame is None:
            log_warning("run_transformations_skipped", "处理前未导入文件")
            QMessageBox.warning(self, "提示", "请先导入 Excel 文件")
            return

        frame = self.state.raw_frame.copy()
        details = {
            "drop_empty": self.controls.drop_empty_checkbox.isChecked(),
            "drop_duplicates": self.controls.drop_duplicates_checkbox.isChecked(),
            "filter_column": self.controls.filter_column_combo.currentText(),
            "sort_column": self.controls.sort_column_combo.currentText(),
            "calc_name": self.controls.calc_name_input.text().strip(),
        }
        log_user_action("transform_started", **details)

        try:
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
        except Exception as exc:
            log_exception("transform_failed", exc)
            self._show_error("处理失败", f"处理失败：{exc}")
            return

        self.state.result_frame = frame
        self.state.available_columns = [str(column) for column in frame.columns]
        self.state.status_message = f"处理完成：{len(frame)} 行"
        self.result_model.set_frame(frame)
        self._populate_column_controls_from_result(frame)
        self._refresh_chart(frame)
        self.tabs.setCurrentIndex(1)
        self._show_status(self.state.status_message)
        log_user_action("transform_completed", rows=len(frame), columns=len(frame.columns))

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
            draw_empty_chart_state(self.chart_panel.figure, "暂无可用图表")
            self.chart_panel.canvas.draw_idle()
            return
        try:
            data = build_chart_series(frame, category_column, value_column)
        except Exception as exc:
            log_exception("chart_prepare_failed", exc, category_column=category_column, value_column=value_column)
            draw_empty_chart_state(self.chart_panel.figure, "图表生成失败")
            self.chart_panel.canvas.draw_idle()
            return
        if not data["x"] or not data["y"]:
            log_warning("chart_empty", "图表数据为空", category_column=category_column, value_column=value_column)
            draw_empty_chart_state(self.chart_panel.figure, "暂无可用图表")
            self.chart_panel.canvas.draw_idle()
            return
        try:
            draw_chart(self.chart_panel.figure, data, self.controls.chart_type_combo.currentText(), "数据图表")
        except Exception as exc:
            log_exception("chart_render_failed", exc, chart_type=self.controls.chart_type_combo.currentText())
            draw_empty_chart_state(self.chart_panel.figure, "图表生成失败")
        self.chart_panel.canvas.draw_idle()

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
        draw_empty_chart_state(self.chart_panel.figure, "暂无可用图表")
        self.chart_panel.canvas.draw_idle()
        self._show_status(self.state.status_message)
        log_user_action("workspace_reset")

    def export_result(self) -> None:
        if self.state.result_frame is None or self.state.result_frame.empty:
            log_warning("export_skipped", "没有可导出的处理结果")
            QMessageBox.warning(self, "提示", "没有可导出的处理结果")
            return
        file_name, _ = QFileDialog.getSaveFileName(self, "导出结果", "processed_output.xlsx", "Excel Files (*.xlsx)")
        if not file_name:
            log_warning("export_cancelled", "用户取消导出")
            return
        target = Path(file_name)
        try:
            export_dataframe(self.state.result_frame, target)
        except Exception as exc:
            log_exception("export_failed", exc, file_name=target.name)
            self._show_error("导出失败", f"导出失败：{exc}")
            return
        self.state.last_export_path = target
        self.state.status_message = f"导出成功：{target.name}"
        self._show_status(self.state.status_message)
        log_user_action("export_completed", file_name=target.name, rows=len(self.state.result_frame))
