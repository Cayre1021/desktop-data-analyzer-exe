from __future__ import annotations

import logging
import platform
import sys
from pathlib import Path
from types import TracebackType

LOGGER_NAME = "desktop_data_analyzer"
LOG_FILE_NAME = "runtime.log"


def application_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def logs_directory() -> Path:
    return application_root() / "logs"


def log_file_path() -> Path:
    return logs_directory() / LOG_FILE_NAME


def initialize_logging() -> Path:
    path = log_file_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    for handler in list(logger.handlers):
        if isinstance(handler, logging.FileHandler) and Path(handler.baseFilename) == path:
            return path
        logger.removeHandler(handler)
        handler.close()

    handler = logging.FileHandler(path, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(handler)
    return path


def get_logger() -> logging.Logger:
    initialize_logging()
    return logging.getLogger(LOGGER_NAME)


def current_log_size_mb() -> float:
    path = log_file_path()
    if not path.exists():
        return 0.0
    return path.stat().st_size / (1024 * 1024)


def format_log_size_mb() -> str:
    return f"{current_log_size_mb():.2f} MB"


def _details_text(**details: object) -> str:
    parts: list[str] = []
    for key, value in details.items():
        if value is None:
            continue
        text = str(value).strip()
        if not text:
            continue
        parts.append(f"{key}={text}")
    if not parts:
        return ""
    return " | " + " | ".join(parts)


def log_startup() -> None:
    get_logger().info(
        "应用启动 | python=%s | frozen=%s | log_file=%s | log_size_mb=%s",
        platform.python_version(),
        getattr(sys, "frozen", False),
        log_file_path(),
        format_log_size_mb(),
    )


def log_user_action(action: str, **details: object) -> None:
    get_logger().info("动作[%s]%s | log_size_mb=%s", action, _details_text(**details), format_log_size_mb())


def log_warning(action: str, message: str, **details: object) -> None:
    get_logger().warning(
        "警告[%s] %s%s | log_size_mb=%s",
        action,
        message,
        _details_text(**details),
        format_log_size_mb(),
    )


def log_exception(action: str, exc: BaseException, **details: object) -> None:
    get_logger().exception(
        "异常[%s] %s%s | log_size_mb=%s",
        action,
        exc,
        _details_text(**details),
        format_log_size_mb(),
    )


def log_unhandled_exception(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: TracebackType | None,
) -> None:
    get_logger().error(
        "未捕获异常[%s] %s | log_size_mb=%s",
        exc_type.__name__,
        exc_value,
        format_log_size_mb(),
        exc_info=(exc_type, exc_value, exc_traceback),
    )


def install_exception_hook() -> None:
    current_hook = sys.excepthook
    if getattr(current_hook, "__name__", "") == "handle_exception":
        return

    def handle_exception(
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_traceback: TracebackType | None,
    ) -> None:
        log_unhandled_exception(exc_type, exc_value, exc_traceback)
        current_hook(exc_type, exc_value, exc_traceback)

    sys.excepthook = handle_exception
