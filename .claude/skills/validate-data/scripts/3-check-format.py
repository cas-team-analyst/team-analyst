"""
goal: Step 3 of validate-data — run diagnostic tests that produce raw, factual
      findings about the loaded data.

These tests do NOT calculate scores or synthesize a conclusion. They return
concrete, observable facts that the agent uses to flag discrepancies between
what the user said their data format is and what the data actually looks like.

Tests:
    1. check_column_names   — looks for claim-ID and origin/dev-period column patterns
    2. check_data_shape     — row/col ratio, per-claim record counts, null-corner pattern
    3. check_tab_count      — number of sheets and their names (Excel only)
    4. check_date_columns   — count and names of date-typed or date-named columns
    5. check_numeric_density — ratio of numeric vs non-numeric columns

This script contains no user interaction. The agent (SKILL.md) is responsible
for interpreting results and presenting discrepancies to the user.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Column-name regex patterns
# ---------------------------------------------------------------------------

_CLAIM_ID_RE = re.compile(
    r"\b(claim|clm|loss|file|policy|pol|case|suit|ref|id|number|num|no\.?)\b",
    re.IGNORECASE,
)

_ORIGIN_PERIOD_RE = re.compile(
    r"\b(org(in)?|origin|accident|acc(ident)?|ay|oy|period|yr|year|\d{4})\b",
    re.IGNORECASE,
)

_DEV_PERIOD_RE = re.compile(
    r"\b(dev(elopment)?[\s_\-]?(pd?|period|age|mon|mo|month|yr|year|\d+)"
    r"|(\d+\s*(mo|month|yr|year|mos|yrs))|age[\s_\-]?\d+)\b",
    re.IGNORECASE,
)

_DATE_NAME_RE = re.compile(
    r"\b(eval|evaluation|as.?of|report|accident|acc|loss_date|"
    r"occurrence|occ|open|close|date|dt)\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Result dataclasses — raw findings only, no interpretation
# ---------------------------------------------------------------------------

@dataclass
class ColumnNameFindings:
    """Test 1: Column name patterns."""
    claim_id_columns: list[str]        # columns matching claim-ID patterns
    origin_period_columns: list[str]   # columns matching origin-period patterns
    dev_period_columns: list[str]      # columns matching dev-period patterns
    all_columns: list[str]


@dataclass
class DataShapeFindings:
    """Test 2: Data shape and null pattern."""
    n_rows: int
    n_cols: int
    row_col_ratio: float               # n_rows / n_cols
    claim_id_col: Optional[str]        # first claim-ID column found, if any
    unique_claim_count: Optional[int]  # distinct values in claim_id_col
    avg_records_per_claim: Optional[float]  # n_rows / unique_claim_count
    null_corner_pct: Optional[float]   # % null in bottom-right quadrant of numeric data
    first_col_null_pct: float          # % null in first numeric column (should be 0 for triangle)
    last_col_null_pct: float           # % null in last numeric column (high for triangle)


@dataclass
class TabCountFindings:
    """Test 3: Excel sheet / tab count."""
    is_excel: bool
    tab_count: Optional[int]           # None for CSV
    tab_names: Optional[list[str]]     # None for CSV


@dataclass
class DateColumnFindings:
    """Test 4: Date-typed or date-named columns."""
    date_named_columns: list[str]      # columns whose names match date patterns
    date_typed_columns: list[str]      # columns whose values parse as dates
    total_date_columns: list[str]      # union of the above two lists


@dataclass
class NumericDensityFindings:
    """Test 5: Ratio of numeric vs non-numeric columns."""
    n_numeric_cols: int
    n_total_cols: int
    numeric_ratio: float               # n_numeric / n_total
    non_numeric_columns: list[str]     # names of non-numeric columns


@dataclass
class FormatCheckResults:
    """Container for all five test results."""
    column_names: ColumnNameFindings
    data_shape: DataShapeFindings
    tab_count: TabCountFindings
    date_columns: DateColumnFindings
    numeric_density: NumericDensityFindings


# ---------------------------------------------------------------------------
# Individual test functions
# ---------------------------------------------------------------------------

def check_column_names(df: pd.DataFrame) -> ColumnNameFindings:
    """
    Test 1 — Scan column names for claim-ID, origin-period, and dev-period patterns.
    """
    cols = df.columns.tolist()
    claim_cols  = [c for c in cols if _CLAIM_ID_RE.search(str(c))]
    origin_cols = [c for c in cols if _ORIGIN_PERIOD_RE.search(str(c))]
    dev_cols    = [c for c in cols if _DEV_PERIOD_RE.search(str(c))]
    return ColumnNameFindings(
        claim_id_columns=claim_cols,
        origin_period_columns=origin_cols,
        dev_period_columns=dev_cols,
        all_columns=cols,
    )


def check_data_shape(df: pd.DataFrame) -> DataShapeFindings:
    """
    Test 2 — Report row/column ratio, per-claim record density, and null-corner pattern.
    """
    n_rows, n_cols = df.shape
    ratio = n_rows / n_cols if n_cols > 0 else float("inf")

    # Find first claim-ID column for per-claim record counts
    claim_col: Optional[str] = None
    unique_count: Optional[int] = None
    avg_records: Optional[float] = None

    for col in df.columns:
        if _CLAIM_ID_RE.search(str(col)):
            claim_col = col
            unique_count = int(df[col].nunique())
            avg_records = round(n_rows / unique_count, 1) if unique_count > 0 else None
            break

    # Null-corner pattern (bottom-right quadrant of numeric data)
    numeric_df = df.select_dtypes(include=[np.number])
    null_corner_pct: Optional[float] = None
    first_col_null_pct = 0.0
    last_col_null_pct = 0.0

    if numeric_df.shape[1] >= 2 and numeric_df.shape[0] >= 2:
        half_row = max(1, n_rows // 2)
        half_col = max(1, numeric_df.shape[1] // 2)
        corner = numeric_df.iloc[half_row:, half_col:]
        null_corner_pct = round(corner.isna().values.mean() * 100, 1)
        first_col_null_pct = round(numeric_df.iloc[:, 0].isna().mean() * 100, 1)
        last_col_null_pct  = round(numeric_df.iloc[:, -1].isna().mean() * 100, 1)

    return DataShapeFindings(
        n_rows=n_rows,
        n_cols=n_cols,
        row_col_ratio=round(ratio, 1),
        claim_id_col=claim_col,
        unique_claim_count=unique_count,
        avg_records_per_claim=avg_records,
        null_corner_pct=null_corner_pct,
        first_col_null_pct=first_col_null_pct,
        last_col_null_pct=last_col_null_pct,
    )


def check_tab_count(file_path: str | Path) -> TabCountFindings:
    """
    Test 3 — Return the number of sheets and their names for Excel files.
    Returns is_excel=False and None values for CSV files.
    """
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".csv":
        return TabCountFindings(is_excel=False, tab_count=None, tab_names=None)

    xl = pd.ExcelFile(path, engine="xlrd" if ext == ".xls" else "openpyxl")
    names = xl.sheet_names
    return TabCountFindings(is_excel=True, tab_count=len(names), tab_names=names)


def check_date_columns(df: pd.DataFrame) -> DateColumnFindings:
    """
    Test 4 — Identify columns whose names or values look like dates.
    """
    cols = df.columns.tolist()
    named = [c for c in cols if _DATE_NAME_RE.search(str(c))]

    typed: list[str] = []
    for col in df.columns:
        ser = df[col].dropna()
        if len(ser) == 0:
            continue
        if pd.api.types.is_datetime64_any_dtype(ser):
            typed.append(str(col))
        elif pd.api.types.is_object_dtype(ser):
            sample = ser.head(20).astype(str)
            parsed = pd.to_datetime(sample, errors="coerce")
            if parsed.notna().mean() > 0.7:
                typed.append(str(col))

    total = list(dict.fromkeys(named + typed))  # union, preserving order
    return DateColumnFindings(
        date_named_columns=named,
        date_typed_columns=typed,
        total_date_columns=total,
    )


def check_numeric_density(df: pd.DataFrame) -> NumericDensityFindings:
    """
    Test 5 — Report the ratio of numeric to total columns.
    """
    n_total = df.shape[1]
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    n_numeric = len(numeric_cols)
    non_numeric = [c for c in df.columns if c not in numeric_cols]
    return NumericDensityFindings(
        n_numeric_cols=n_numeric,
        n_total_cols=n_total,
        numeric_ratio=round(n_numeric / n_total, 2) if n_total > 0 else 0.0,
        non_numeric_columns=non_numeric,
    )


# ---------------------------------------------------------------------------
# Convenience wrapper — run all five tests at once
# ---------------------------------------------------------------------------

def run_all_checks(df: pd.DataFrame, file_path: str | Path) -> FormatCheckResults:
    """
    Run all five format-diagnostic tests and return a FormatCheckResults container.

    Args:
        df:        The DataFrame loaded in step 1.
        file_path: The original file path (needed for tab-count test).

    Returns:
        FormatCheckResults with raw findings from all five tests.
    """
    return FormatCheckResults(
        column_names    = check_column_names(df),
        data_shape      = check_data_shape(df),
        tab_count       = check_tab_count(file_path),
        date_columns    = check_date_columns(df),
        numeric_density = check_numeric_density(df),
    )
