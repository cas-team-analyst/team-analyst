"""
Robust Excel reading utilities for chain-ladder workbooks.
Tolerates variations in row layout, blank rows, and text in unexpected places.
"""
import re
import pandas as pd
import numpy as np

_INTERVAL_RE = re.compile(r'^\d+-\d+$')


def _is_interval_row(row_series) -> bool:
    """Return True if the row looks like an interval label row (e.g. '12-24', 'Tail')."""
    vals = [str(v).strip() for v in row_series.iloc[1:] if pd.notna(v) and str(v).strip()]
    matches = sum(1 for v in vals if _INTERVAL_RE.match(v) or v.lower() == 'tail')
    return matches >= 3


def find_row_by_label(df: pd.DataFrame, label: str):
    """Return (row_index, row_series) for the first row whose first cell matches label."""
    mask = df.iloc[:, 0].astype(str).str.strip() == label
    indices = df[mask].index
    if len(indices) == 0:
        return None, None
    idx = indices[0]
    return idx, df.iloc[idx]


def find_interval_row_above(df: pd.DataFrame, row_idx: int, max_scan: int = 20):
    """
    Scan upward from row_idx to find the nearest interval header row.
    Returns the row series or None.
    """
    for offset in range(1, min(max_scan, row_idx + 1)):
        candidate = df.iloc[row_idx - offset]
        if _is_interval_row(candidate):
            return candidate
    return None


def read_labeled_selections(df: pd.DataFrame, label: str) -> dict:
    """
    Read a selection row identified by its label in column 0.
    Finds the matching interval header by scanning upward.
    Returns {interval_str: float_value} or empty dict.
    """
    row_idx, sel_row = find_row_by_label(df, label)
    if sel_row is None:
        return {}

    interval_row = find_interval_row_above(df, row_idx)
    if interval_row is None:
        return {}

    selections = {}
    for col_idx in range(1, len(sel_row)):
        interval = interval_row.iloc[col_idx]
        ldf_value = sel_row.iloc[col_idx]
        if pd.notna(interval) and pd.notna(ldf_value):
            try:
                selections[str(interval).strip()] = float(ldf_value)
            except (ValueError, TypeError):
                continue
    return selections


def get_tail(selections: dict) -> float:
    """Return tail factor from selections dict, checking both 'Tail' and 'tail'."""
    return float(selections.get('Tail', selections.get('tail', 1.0)))
