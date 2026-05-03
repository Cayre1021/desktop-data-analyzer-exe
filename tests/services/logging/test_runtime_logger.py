from pathlib import Path

import pandas as pd

from services.logging.runtime_logger import format_log_size_mb, initialize_logging, log_user_action


def test_initialize_logging_creates_runtime_log(tmp_path, monkeypatch):
    monkeypatch.setattr("services.logging.runtime_logger.application_root", lambda: tmp_path)

    path = initialize_logging()
    log_user_action("test_action", result="ok")

    assert path == tmp_path / "logs" / "runtime.log"
    assert path.exists()
    assert "动作[test_action]" in path.read_text(encoding="utf-8")


def test_format_log_size_mb_returns_mb_suffix(tmp_path, monkeypatch):
    monkeypatch.setattr("services.logging.runtime_logger.application_root", lambda: tmp_path)
    log_path = initialize_logging()
    pd.DataFrame({"value": list(range(50))}).to_csv(log_path, index=False)

    result = format_log_size_mb()

    assert result.endswith(" MB")
    assert float(result.split()[0]) >= 0
