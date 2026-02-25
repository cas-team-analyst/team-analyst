"""
goal: Step 2 of reserving-workflow — convert validated triangle data into a
      canonical long format and save the result as a CSV alongside the source file.

Input:
  file_path   — path to the validated triangle file.  Use the original file if
                the triangles were already cumulative, or the *-cumulative.xlsx
                file produced by Step 6 of validate-data if they were incremental.
  resolved_tabs — mapping of measure key → tab name confirmed during validation,
                e.g. {"incurred_losses": "Incurred", "paid_losses": "Paid"}.
                Produced by check_measure_tab_mapping() in validate-data Step 7a.

Output file: {original_dir}/{original_stem}-canonical.csv
  e.g.  C:/data/loss-triangles-cumulative.xlsx
     →  C:/data/loss-triangles-canonical.csv

The output CSV has four columns:
  origin_period    — accident / origin period label (as it appears in the triangle)
  development_age  — development period label (column header from the triangle)
  measure          — data type, one of:
                       "paid_losses", "incurred_losses",
                       "reported_counts", "closed_counts"
  value            — numeric cell value (NaN cells are excluded)

All triangles are stacked into a single DataFrame in the order supplied by
resolved_tabs.  The file contains no user interaction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import pandas as pd


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _read_triangle_tab(src: Path, tab_name: str) -> pd.DataFrame:
    """
    Read a single triangle tab from an Excel file.
    First column = origin period labels; remaining columns = development periods.
    """
    ext = src.suffix.lower()
    engine = "xlrd" if ext == ".xls" else "openpyxl"
    return pd.read_excel(src, sheet_name=tab_name, engine=engine, dtype=str)


def _melt_triangle(df: pd.DataFrame, measure: str) -> pd.DataFrame:
    """
    Convert a wide triangle DataFrame into long (canonical) format.

    First column is treated as origin period labels.
    Remaining columns are development age labels.
    NaN cells are dropped.

    Returns a DataFrame with columns:
        origin_period, development_age, measure, value
    """
    # Identify origin column (first column) and dev columns (rest)
    origin_col = df.columns[0]
    dev_cols = list(df.columns[1:])

    # Coerce numeric values
    for col in dev_cols:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(r"[\$,\s]", "", regex=True),
            errors="coerce",
        )

    long = df.melt(
        id_vars=[origin_col],
        value_vars=dev_cols,
        var_name="development_age",
        value_name="value",
    )

    long = long.rename(columns={origin_col: "origin_period"})
    long["origin_period"] = long["origin_period"].astype(str).str.strip()
    long["development_age"] = long["development_age"].astype(str).str.strip()
    long.insert(2, "measure", measure)

    # Drop rows with no value (upper-right NaN cells)
    long = long.dropna(subset=["value"]).reset_index(drop=True)

    return long


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class ExtractionResult:
    """Result of extracting all measure triangles to canonical long format."""
    output_path: Path                    # path of the saved canonical CSV
    extracted_measures: list[str]        # measure keys successfully extracted
    failed_measures: dict[str, str] = field(default_factory=dict)  # key → error


# ---------------------------------------------------------------------------
# Main extraction function
# ---------------------------------------------------------------------------

MEASURE_DISPLAY_NAMES: dict[str, str] = {
    "incurred_losses":  "incurred_losses",
    "paid_losses":      "paid_losses",
    "reported_counts":  "reported_counts",
    "closed_counts":    "closed_counts",
}


def extract_canonical_from_triangles(
    file_path: str | Path,
    resolved_tabs: dict[str, str],
    output_path: Optional[str | Path] = None,
) -> ExtractionResult:
    """
    Read each triangle tab identified in resolved_tabs, melt it into long format,
    and stack all measures into a single canonical CSV.

    Args:
        file_path:     Path to the validated (cumulative) triangle file.
                       Supports .xlsx, .xlsm, .xls, and .csv.
        resolved_tabs: Mapping of measure key → tab name confirmed during
                       validate-data Step 7a, e.g.:
                           {"incurred_losses": "Incurred", "paid_losses": "Paid"}
                       Valid measure keys:
                           "incurred_losses", "paid_losses",
                           "reported_counts", "closed_counts"
        output_path:   Optional override for the output file path. If None, the
                       CSV is saved as {stem}-canonical.csv in the same directory
                       as file_path.

    Returns:
        ExtractionResult with the output path, list of successfully extracted
        measures, and any failed measures with their error messages.

    Raises:
        FileNotFoundError: If file_path does not exist.
        ValueError:        If resolved_tabs is empty.
    """
    src = Path(file_path).expanduser().resolve()

    if not src.exists():
        raise FileNotFoundError(f"File not found: {src}")
    if not resolved_tabs:
        raise ValueError("resolved_tabs must not be empty.")

    dest: Path
    if output_path is None:
        dest = src.with_name(f"{src.stem}-canonical.csv")
    else:
        dest = Path(output_path).expanduser().resolve()

    ext = src.suffix.lower()
    extracted_measures: list[str] = []
    failed_measures: dict[str, str] = {}
    long_frames: list[pd.DataFrame] = []

    for measure, tab_name in resolved_tabs.items():
        if not tab_name:
            continue
        try:
            if ext == ".csv":
                # CSV: assume a single triangle; tab_name is only used for the
                # measure label
                raw = pd.read_csv(src, dtype=str)
                long = _melt_triangle(raw, measure)
            else:
                raw = _read_triangle_tab(src, tab_name)
                long = _melt_triangle(raw, measure)

            long_frames.append(long)
            extracted_measures.append(measure)

        except Exception as exc:
            failed_measures[measure] = str(exc)

    if long_frames:
        canonical = pd.concat(long_frames, ignore_index=True)
        canonical.to_csv(dest, index=False)
    else:
        # Nothing extracted; still return a valid result — caller handles failures
        dest = src  # sentinel: nothing was written

    return ExtractionResult(
        output_path=dest,
        extracted_measures=extracted_measures,
        failed_measures=failed_measures,
    )
