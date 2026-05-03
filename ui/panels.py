from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
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
        self.source_summary_label = QLabel("")
        self.source_summary_label.setWordWrap(True)
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
        self.reset_button = QPushButton("重置工作区")

        source_group = QGroupBox("数据源")
        source_layout = QVBoxLayout(source_group)
        source_layout.addWidget(self.file_label)
        source_layout.addWidget(self.source_summary_label)

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

        buttons = QVBoxLayout()
        buttons.addWidget(self.run_button)
        buttons.addWidget(self.export_button)
        buttons.addWidget(self.reset_button)

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
