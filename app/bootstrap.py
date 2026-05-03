from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from services.logging import initialize_logging, install_exception_hook, log_startup
from ui.main_window import MainWindow


DEFAULT_UI_FONT_FAMILIES = ["Microsoft YaHei", "SimHei"]


def create_window() -> MainWindow:
    return MainWindow()


def run() -> int:
    initialize_logging()
    install_exception_hook()
    log_startup()
    app = QApplication.instance() or QApplication([])
    app.setFont(QFont(DEFAULT_UI_FONT_FAMILIES[0], 10))
    window = create_window()
    window.show()
    return app.exec()
