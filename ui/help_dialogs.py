from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
)


GUIDE_STEPS = [
    ("导入 Excel", "从主工具栏点击“导入 Excel”，选择 .xlsx 或 .xls 文件，系统会默认读取首个工作表。"),
    ("查看数据源", "左侧“数据源”区域会显示文件名、工作表名、行数和列数，方便确认导入是否正确。"),
    ("配置处理", "在“处理配置”中可以去空行、去重、筛选、排序，或按两列做加减乘除生成新列。"),
    ("执行处理", "点击“执行处理”后，处理结果会切换到右侧“处理结果”标签页。"),
    ("查看图表", "在“图表配置”中选择分类列和数值列后，右侧图表会自动刷新为柱状图或折线图。"),
    ("导出结果", "点击“导出结果”可把当前处理结果保存为新的 Excel 文件。"),
    ("重置工作区", "点击“重置工作区”会清空当前数据、配置和图表，重新开始一次分析。"),
    ("查看日志", "程序运行时会在应用目录下生成 logs/runtime.log，可用于排查导入、处理、导出或图表问题。"),
]


def user_guide_path() -> Path:
    return Path(__file__).resolve().parents[1] / "docs" / "user-guide.md"


def guide_markdown() -> str:
    path = user_guide_path()
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "# 使用说明\n\n未找到使用说明文件。"


class GuideModeDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("新手引导")
        self.selected_mode: str | None = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("请选择查看方式："))

        step_button = QPushButton("分步引导")
        full_button = QPushButton("完整说明")
        cancel_buttons = QDialogButtonBox(QDialogButtonBox.Cancel)

        step_button.clicked.connect(self._select_step_mode)
        full_button.clicked.connect(self._select_full_mode)
        cancel_buttons.rejected.connect(self.reject)

        layout.addWidget(step_button)
        layout.addWidget(full_button)
        layout.addWidget(cancel_buttons)

    def _select_step_mode(self) -> None:
        self.selected_mode = "step"
        self.accept()

    def _select_full_mode(self) -> None:
        self.selected_mode = "full"
        self.accept()


class StepGuideDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("分步引导")
        self.current_index = 0

        layout = QVBoxLayout(self)
        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-weight: bold; font-size: 15px;")
        self.content_label = QLabel()
        self.content_label.setWordWrap(True)
        self.content_label.setMinimumWidth(420)

        self.next_button = QPushButton("下一步")
        self.close_button = QPushButton("关闭")

        self.next_button.clicked.connect(self.next_step)
        self.close_button.clicked.connect(self.accept)

        layout.addWidget(self.title_label)
        layout.addWidget(self.content_label)
        layout.addWidget(self.next_button)
        layout.addWidget(self.close_button)

        self._render_step()

    def _render_step(self) -> None:
        title, content = GUIDE_STEPS[self.current_index]
        step_number = self.current_index + 1
        total = len(GUIDE_STEPS)
        self.title_label.setText(f"第 {step_number}/{total} 步：{title}")
        self.content_label.setText(content)
        self.next_button.setText("完成" if self.current_index == total - 1 else "下一步")

    def next_step(self) -> None:
        if self.current_index >= len(GUIDE_STEPS) - 1:
            self.accept()
            return
        self.current_index += 1
        self._render_step()


class FullGuideDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("完整说明")
        layout = QVBoxLayout(self)
        browser = QTextBrowser()
        browser.setMarkdown(guide_markdown())
        browser.setOpenExternalLinks(False)
        browser.setMinimumSize(700, 560)
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        layout.addWidget(browser)
        layout.addWidget(close_button)


def open_novice_guide(parent=None) -> None:
    mode_dialog = GuideModeDialog(parent)
    if mode_dialog.exec() != QDialog.Accepted or not mode_dialog.selected_mode:
        return
    if mode_dialog.selected_mode == "step":
        StepGuideDialog(parent).exec()
        return
    FullGuideDialog(parent).exec()


def open_full_guide_message(parent=None) -> None:
    QMessageBox.information(parent, "使用说明", guide_markdown())
