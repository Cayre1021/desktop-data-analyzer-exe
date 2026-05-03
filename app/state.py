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
