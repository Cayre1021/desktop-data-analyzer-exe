import operator

import pandas as pd


OPERATORS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
}


def drop_empty_rows(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.dropna(how="all").reset_index(drop=True)


def drop_duplicate_rows(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.drop_duplicates().reset_index(drop=True)


def apply_sort(frame: pd.DataFrame, column: str, ascending: bool) -> pd.DataFrame:
    return frame.sort_values(by=column, ascending=ascending).reset_index(drop=True)


def apply_contains_filter(frame: pd.DataFrame, column: str, keyword: str) -> pd.DataFrame:
    mask = frame[column].fillna("").astype(str).str.contains(keyword, case=False, na=False)
    return frame.loc[mask].reset_index(drop=True)


def add_calculated_column(
    frame: pd.DataFrame,
    new_column: str,
    left_column: str,
    right_column: str,
    operator_symbol: str,
) -> pd.DataFrame:
    result = frame.copy()
    result[new_column] = OPERATORS[operator_symbol](result[left_column], result[right_column])
    return result
