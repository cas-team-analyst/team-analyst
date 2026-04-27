import copy

import numpy as np
import pandas as pd


def _safe(v):
    """Convert NaN/NA to None so openpyxl writes a blank cell."""
    if v is None:
        return None
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    return v


def _to_py(v):
    """
    Coerce a value to a plain Python type so openpyxl writes a number, not text.
    - numpy scalars → int / float
    - numeric strings ('120', '1.05') → int / float
    - everything else unchanged
    """
    if isinstance(v, np.integer):
        return int(v)
    if isinstance(v, np.floating):
        return float(v)
    if isinstance(v, str):
        try:
            f = float(v)
            return int(f) if f == int(f) else f
        except (ValueError, TypeError):
            pass
    return v


def _period_int(v):
    """Display a period as int when it is a whole number, else return as-is."""
    try:
        f = float(v)
        if f == int(f):
            return int(f)
    except (ValueError, TypeError):
        pass
    return v


def _copy_ws(ws_src, ws_dst):
    """Copy all cells and styles from source to destination worksheet."""
    for row in ws_src.iter_rows():
        for cell in row:
            dst = ws_dst[cell.coordinate]
            dst.value = cell.value
            if cell.has_style:
                dst.font          = copy.copy(cell.font)
                dst.border        = copy.copy(cell.border)
                dst.fill          = copy.copy(cell.fill)
                dst.number_format = cell.number_format
                dst.protection    = copy.copy(cell.protection)
                dst.alignment     = copy.copy(cell.alignment)

    for col in ws_src.column_dimensions:
        ws_dst.column_dimensions[col].width = ws_src.column_dimensions[col].width
    for row_num in ws_src.row_dimensions:
        ws_dst.row_dimensions[row_num].height = ws_src.row_dimensions[row_num].height
    for rng in ws_src.merged_cells.ranges:
        ws_dst.merge_cells(str(rng))
    if ws_src.freeze_panes:
        ws_dst.freeze_panes = ws_src.freeze_panes
