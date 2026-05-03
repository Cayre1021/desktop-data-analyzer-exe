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


def test_load_first_sheet_reads_xls_using_pandas_only(monkeypatch, tmp_path: Path):
    source = tmp_path / "input.xls"
    calls: list[tuple[Path, str | None, str | None]] = []

    def fake_read_excel(path: Path, sheet_name=None, engine=None, *args, **kwargs):
        calls.append((path, sheet_name, engine))
        return {"Sheet1": pd.DataFrame({"A": [1, 2]})}

    monkeypatch.setattr(pd, "read_excel", fake_read_excel)

    frame, sheet_name = load_first_sheet(source)

    assert sheet_name == "Sheet1"
    assert frame.to_dict(orient="records") == [{"A": 1}, {"A": 2}]
    assert calls == [(source, None, "xlrd")]


def test_export_dataframe_writes_new_excel_file(tmp_path: Path):
    target = tmp_path / "output.xlsx"
    frame = pd.DataFrame({"name": ["A"], "value": [10]})

    export_dataframe(frame, target)

    loaded = pd.read_excel(target)
    assert loaded.to_dict(orient="records") == [{"name": "A", "value": 10}]


def test_demo_workbook_exists():
    assert Path("sample_data/demo_sales.xlsx").exists()
