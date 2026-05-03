import pandas as pd

from services.transform.operations import (
    add_calculated_column,
    apply_contains_filter,
    apply_sort,
    drop_duplicate_rows,
    drop_empty_rows,
)


def test_drop_empty_rows_removes_fully_empty_rows():
    frame = pd.DataFrame(
        [
            {"category": "A", "value": 1},
            {"category": None, "value": None},
            {"category": "B", "value": 2},
        ]
    )

    result = drop_empty_rows(frame)

    assert result.to_dict(orient="records") == [
        {"category": "A", "value": 1.0},
        {"category": "B", "value": 2.0},
    ]


def test_drop_duplicate_rows_removes_duplicate_records():
    frame = pd.DataFrame([
        {"category": "A", "value": 1},
        {"category": "A", "value": 1},
        {"category": "B", "value": 2},
    ])

    result = drop_duplicate_rows(frame)

    assert result.to_dict(orient="records") == [
        {"category": "A", "value": 1},
        {"category": "B", "value": 2},
    ]


def test_apply_sort_orders_by_selected_column_descending():
    frame = pd.DataFrame([
        {"category": "A", "value": 1},
        {"category": "B", "value": 3},
        {"category": "C", "value": 2},
    ])

    result = apply_sort(frame, "value", ascending=False)

    assert result["value"].tolist() == [3, 2, 1]


def test_apply_contains_filter_keeps_matching_rows():
    frame = pd.DataFrame([
        {"category": "North", "value": 1},
        {"category": "South", "value": 2},
    ])

    result = apply_contains_filter(frame, "category", "nor")

    assert result.to_dict(orient="records") == [{"category": "North", "value": 1}]


def test_add_calculated_column_supports_multiply():
    frame = pd.DataFrame([
        {"price": 10, "qty": 2},
        {"price": 8, "qty": 3},
    ])

    result = add_calculated_column(frame, "total", "price", "qty", "*")

    assert result.to_dict(orient="records") == [
        {"price": 10, "qty": 2, "total": 20},
        {"price": 8, "qty": 3, "total": 24},
    ]
