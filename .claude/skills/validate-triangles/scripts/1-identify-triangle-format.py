"""
goal: Step 1 of validate-triangles -- read each tab in sheets and determine if it is incremental or cumulative.

Incremental triangles: typically decreasing values by column (possibly negative).
Cumulative triangles: generally increasing by column and should never be negative.

"""

from dataclasses import dataclass
from pathlib import Path
import sys
import pandas as pd


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class TabTriangleFormat:
    """Per-tab result: whether the triangle has any negative values 
    and the percentage of values that are non-decreasing."""
    tab_name: str
    negative_count: int
    pct_non_decreasing: float


# ---------------------------------------------------------------------------
# Core logic: return raw results indicating likely triangle format
# ---------------------------------------------------------------------------

def _extract_numeric_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Treat first column as origin labels; remaining columns as numeric development values.
    Returns a DataFrame of numeric values only (same shape as df.iloc[:, 1:]).
    """
    data = df.iloc[:, 1:].copy()
    for col in data.columns:
        data[col] = pd.to_numeric(
            data[col].astype(str).str.replace(r"[\$,\s]", "", regex=True),
            errors="coerce",
        )
    return data


def identify_triangle_format(
    sheets: dict[str, pd.DataFrame],
    selected_triangles: dict[str, str],
) -> list[TabTriangleFormat]:
    """
    Read each tab in sheets and determine if it is incremental or cumulative.

    Expects the same structure as identify-format's load_data(): dict mapping
    tab/sheet name to pd.DataFrame. Each DataFrame is assumed to have first
    column = origin period labels, remaining columns = development period values.

    Rules:
    - Any negative value -> incremental (cumulative should never be negative).
    - Otherwise: rows non-decreasing by column -> cumulative; else incremental.

    Args:
        sheets: dict[str, pd.DataFrame] from identify-format skill.
        selected_triangles: dict[str, str] from validate-triangles skill.

    Returns:
        IdentifyTriangleFormatResult with per-tab classification and count of sheets processed.
    """
    if not sheets:
        raise ValueError("sheets is empty")
    if not selected_triangles:
        raise ValueError("selected_triangles is empty")
     if not all(len(selected_triangles[measure]) == 1):
        raise ValueError("selected_triangles must have one triangle for each measure")
    if not all(tab_name in sheets for tab_name in selected_triangles.values()):
        raise ValueError("selected_triangles must have valid triangle names")

    tab_results: list[TabTriangleFormat] = []
    for measure, tab_name in selected_triangles.items():
        df = sheets[tab_name]
        if df.empty or df.shape[1] < 2:
            raise ValueError(f"Triangle {tab_name} is empty or has less than 2 columns")

        data = _extract_numeric_data(df)
        if data.isna().all().all():
            raise ValueError(f"Triangle {tab_name} has no numeric data")

        negative_count = (data < 0).sum().sum()

        # Count rows that are non-decreasing left-to-right (cumulative) vs not
        non_decreasing_count = 0
        testable_count = 0
        for _, row in data.iterrows():
            values = row.dropna().tolist()
            if len(values) < 2:
                continue
            for i in range(len(values) - 1):
                testable_count += 1
                if values[i] > values[i + 1]:
                    non_decreasing_count += 1

        if testable_count == 0:
            raise ValueError(f"Triangle {tab_name} has no rows with at least 2 columns to compare")
        
        pct_non_decreasing = non_decreasing_count / testable_count

        tab_results.append(
            TabTriangleFormat(
                tab_name=tab_name,
                negative_count=negative_count,
                pct_non_decreasing=pct_non_decreasing,
            )
        )

    return tab_results
