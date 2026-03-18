"""
goal: Step 1 of validate-triangles — convert incremental triangles to
      cumulative form and save the result alongside the original file.

Run this script only when the user confirmed that their triangles are in
INCREMENTAL format. If triangles are already cumulative, skip this step and
proceed directly to Step 7 (triangle validation).

Output file: {original_dir}/{original_stem}-cumulative.{ext}
  e.g.  C:/data/loss-triangles.xlsx  →  C:/data/loss-triangles-cumulative.xlsx

Each tab listed in resolved_tabs is read, converted to cumulative (row-wise
cumulative sum across development period columns), and written to the output
file. Tabs not in resolved_tabs are not included in the output.

"""

from pathlib import Path
from typing import Optional
import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# Triangle type detector — guess cumulative vs incremental before asking user
# ---------------------------------------------------------------------------

def detect_triangle_type(df: pd.DataFrame) -> tuple[str, str]:
    """
    Inspect the numeric data in a triangle DataFrame and guess whether the
    triangle is cumulative or incremental.

    A cumulative triangle has non-decreasing values from left to right across
    each row (ignoring trailing NaN cells, which represent unfilled development
    periods).  An incremental triangle has values that do *not* consistently
    increase across each row.

    Args:
        df: A triangle DataFrame where the first column is origin period
            labels and the remaining columns are development period values.
            Typically one sheet/tab loaded from the input file.

    Returns:
        (guess, confidence_note) where:
          guess           — "cumulative" or "incremental"
          confidence_note — "high"   (≥ 80 % of rows agree)
                           "medium" (60–79 %)
                           "low"    (< 60 %)
    """
    # Extract numeric portion (skip first column, which is origin labels)
    data = df.iloc[:, 1:].copy()
    for col in data.columns:
        data[col] = pd.to_numeric(
            data[col].astype(str).str.replace(r"[\$,\s]", "", regex=True),
            errors="coerce",
        )

    non_decreasing_rows = 0
    testable_rows = 0

    for _, row in data.iterrows():
        values = row.dropna().tolist()
        if len(values) < 2:
            continue  # not enough data to make a call
        testable_rows += 1
        # Non-decreasing: every adjacent pair satisfies values[i] <= values[i+1]
        if all(values[i] <= values[i + 1] for i in range(len(values) - 1)):
            non_decreasing_rows += 1

    if testable_rows == 0:
        return "cumulative", "low"  # can't tell; default to safer assumption

    pct_non_decreasing = non_decreasing_rows / testable_rows

    if pct_non_decreasing >= 0.8:
        guess = "cumulative"
    else:
        guess = "incremental"

    if pct_non_decreasing >= 0.8 or pct_non_decreasing <= 0.2:
        confidence = "high"
    elif pct_non_decreasing >= 0.6 or pct_non_decreasing <= 0.4:
        confidence = "medium"
    else:
        confidence = "low"

    return guess, confidence


# ---------------------------------------------------------------------------
# CSV triangle detection
# ---------------------------------------------------------------------------

def _split_csv_triangles(df: pd.DataFrame) -> list[tuple[str, pd.DataFrame]]:
    """
    Detect individual triangles stacked in a single CSV sheet by splitting on
    blank rows (rows where every cell is empty or NaN).

    Label inference (applied to each chunk before the data rows):
      - If the first row of a chunk has exactly one non-empty cell and no
        numeric content, that cell is treated as the triangle's label and
        stripped from the data before conversion.
      - Otherwise the triangle is labelled "Triangle_N" (1-indexed).

    Returns:
        List of (label, triangle_df) pairs in the order they appear in the CSV.
    """
    # Identify blank rows
    def _is_blank(row: pd.Series) -> bool:
        return row.isna().all() or row.astype(str).str.strip().eq("").all()

    blank_mask = df.apply(_is_blank, axis=1)

    # Slice into chunks between blank rows
    raw_chunks: list[pd.DataFrame] = []
    start = 0
    for i, is_blank in enumerate(blank_mask):
        if is_blank:
            chunk = df.iloc[start:i]
            if not chunk.dropna(how="all").empty:
                raw_chunks.append(chunk.reset_index(drop=True))
            start = i + 1
    # Final chunk
    final = df.iloc[start:]
    if not final.dropna(how="all").empty:
        raw_chunks.append(final.reset_index(drop=True))

    labeled: list[tuple[str, pd.DataFrame]] = []
    for idx, chunk in enumerate(raw_chunks):
        default_label = f"Triangle_{idx + 1}"
        # Attempt label inference from first row
        first_row_vals = (
            chunk.iloc[0].dropna().astype(str).str.strip()
        )
        non_empty = first_row_vals[first_row_vals != ""]
        if (
            len(non_empty) == 1
            and not non_empty.iloc[0].replace(".", "").replace("-", "").isdigit()
        ):
            label = non_empty.iloc[0]
            chunk = chunk.iloc[1:].reset_index(drop=True)  # drop label row
            # Promote next row to column headers if they look non-numeric
            if not chunk.empty:
                new_header = chunk.iloc[0].astype(str).str.strip()
                chunk.columns = new_header
                chunk = chunk.iloc[1:].reset_index(drop=True)
        else:
            label = default_label

        labeled.append((label, chunk))

    return labeled


# ---------------------------------------------------------------------------
# Helpers (shared with 4b-validate-triangle.py logic but self-contained here)
# ---------------------------------------------------------------------------

def _extract_numeric_triangle(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """
    Split a raw triangle DataFrame into (numeric_data, origin_labels).
    First column is treated as origin period labels; remaining columns are data.
    All data values are coerced to float (currency symbols and commas stripped).
    """
    origin_labels = df.iloc[:, 0].astype(str).str.strip()
    data = df.iloc[:, 1:].copy()
    for col in data.columns:
        data[col] = pd.to_numeric(
            data[col].astype(str).str.replace(r"[\$,\s]", "", regex=True),
            errors="coerce",
        )
    return data, origin_labels


def _to_cumulative(data: pd.DataFrame) -> pd.DataFrame:
    """
    Convert an incremental triangle to cumulative by computing the row-wise
    cumulative sum across development period columns.
    NaN cells (upper-right triangle) are preserved as NaN.
    """
    return data.cumsum(axis=1)


def _rebuild_df(origin_labels: pd.Series, cumulative_data: pd.DataFrame) -> pd.DataFrame:
    """Re-attach origin labels as the first column of the cumulative data."""
    return pd.concat(
        [
            origin_labels.reset_index(drop=True).rename(origin_labels.name or "origin"),
            cumulative_data.reset_index(drop=True),
        ],
        axis=1,
    )


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

from dataclasses import dataclass

@dataclass
class ConversionResult:
    """Result of converting all measure triangles to cumulative form."""
    output_path: Path                       # path of the saved cumulative file
    converted_tabs: list[str]               # tab names successfully converted
    failed_tabs: dict[str, str]             # tab_name → error message


# ---------------------------------------------------------------------------
# Main conversion function
# ---------------------------------------------------------------------------

def convert_to_cumulative(
    file_path: str | Path,
    resolved_tabs: dict[str, str],
    output_path: Optional[str | Path] = None,
) -> ConversionResult:
    """
    Read each triangle tab in resolved_tabs, convert from incremental to
    cumulative, and write the result to a new Excel file.

    Args:
        file_path:     Path to the original triangle Excel file.
        resolved_tabs: Mapping of measure key → tab name, e.g.
                       {"incurred_losses": "Incurred", "paid_losses": "Paid"}.
                       Produced by check_measure_tab_mapping() in step 7.
        output_path:   Optional override for the output file path. If None, the
                       output is saved as {stem}-cumulative.xlsx in the same
                       directory as file_path.

    Returns:
        ConversionResult with the output path and a list of successfully
        converted tab names.

    Raises:
        ValueError:  If file_path is a CSV (CSV files cannot hold multiple tabs).
        FileNotFoundError: If file_path does not exist.
    """
    src = Path(file_path).expanduser().resolve()

    if not src.exists():
        raise FileNotFoundError(f"File not found: {src}")

    ext = src.suffix.lower()

    # ------------------------------------------------------------------
    # CSV path: detect stacked triangles separated by blank rows
    # ------------------------------------------------------------------
    if ext == ".csv":
        raw = pd.read_csv(src, header=0, dtype=str)
        triangles = _split_csv_triangles(raw)

        converted_tabs: list[str] = []
        failed_tabs: dict[str, str] = {}
        output_sheets: dict[str, pd.DataFrame] = {}

        for label, tri_df in triangles:
            try:
                data, origins = _extract_numeric_triangle(tri_df)
                cumulative    = _to_cumulative(data)
                df_cumulative = _rebuild_df(origins, cumulative)
                output_sheets[label] = df_cumulative
                converted_tabs.append(label)
            except Exception as exc:
                failed_tabs[label] = str(exc)

        if output_sheets:
            if len(output_sheets) == 1:
                # Single triangle → preserve as CSV
                if output_path is None:
                    dest = src.with_name(f"{src.stem}-cumulative.csv")
                else:
                    dest = Path(output_path).expanduser().resolve()
                list(output_sheets.values())[0].to_csv(dest, index=False)
            else:
                # Multiple triangles → one tab per triangle in Excel
                if output_path is None:
                    dest = src.with_name(f"{src.stem}-cumulative.xlsx")
                else:
                    dest = Path(output_path).expanduser().resolve()
                with pd.ExcelWriter(dest, engine="openpyxl") as writer:
                    for label, df_out in output_sheets.items():
                        df_out.to_excel(writer, sheet_name=label, index=False)
        else:
            dest = src  # nothing written; signal via failed_tabs

        return ConversionResult(
            output_path=dest,
            converted_tabs=converted_tabs,
            failed_tabs=failed_tabs,
        )

    # Determine output path
    if output_path is None:
        dest = src.with_name(f"{src.stem}-cumulative.xlsx")
    else:
        dest = Path(output_path).expanduser().resolve()

    engine_read  = "xlrd" if ext == ".xls" else "openpyxl"

    converted_tabs: list[str] = []
    failed_tabs: dict[str, str] = {}
    output_sheets: dict[str, pd.DataFrame] = {}

    for measure, tab_name in resolved_tabs.items():
        if not tab_name:
            continue
        try:
            df = pd.read_excel(src, sheet_name=tab_name, engine=engine_read)
            data, origins = _extract_numeric_triangle(df)
            cumulative    = _to_cumulative(data)
            df_cumulative = _rebuild_df(origins, cumulative)
            output_sheets[tab_name] = df_cumulative
            converted_tabs.append(tab_name)
        except Exception as exc:
            failed_tabs[tab_name] = str(exc)

    # Write all converted sheets to the output file
    if output_sheets:
        with pd.ExcelWriter(dest, engine="openpyxl") as writer:
            for tab_name, df_out in output_sheets.items():
                df_out.to_excel(writer, sheet_name=tab_name, index=False)

    return ConversionResult(
        output_path=dest,
        converted_tabs=converted_tabs,
        failed_tabs=failed_tabs,
    )
