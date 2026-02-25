"""
goal: Step 1b of extract-canonical — convert a validated loss run into the same
      canonical long-format CSV produced by Step 1a (extract-triangle).

This script pivots a long-format loss run into cumulative development triangles,
then stacks them into the identical four-column output:

    origin_period    — accident / origin period label
    development_age  — development period label (age at each evaluation)
    measure          — data type key (see CANONICAL_MEASURES below)
    value            — cumulative numeric value at that (origin, age) cell

Input:
    df              — validated loss run DataFrame (one row per claim per eval)
    origin_col      — name of the accident / origin period column
    eval_col        — name of the evaluation date / age column
    resolved_columns — mapping of measure key → column name in the loss run,
                       as resolved during validate-data Step 5
                       e.g. {"paid_losses": "Paid", "incurred_losses": "Incurred"}
    output_path     — optional override; if None, saved as {stem}-canonical.csv
                      beside the source file

Output file: {original_dir}/{original_stem}-canonical.csv

The file contains no user interaction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import pandas as pd


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Valid measure keys — must match 1a-extract-triangle.py exactly
CANONICAL_MEASURES: set[str] = {
    "paid_losses",
    "incurred_losses",
    "reported_counts",
    "closed_counts",
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_period(series: pd.Series) -> pd.Series:
    """
    Attempt to parse a period column into a sortable representation.
    Tries datetime first, falls back to the raw string value.
    Returns a Series suitable for sorting.
    """
    try:
        return pd.to_datetime(series, infer_datetime_format=True)
    except Exception:
        return series.astype(str).str.strip()


def _build_triangle(
    df: pd.DataFrame,
    origin_col: str,
    eval_col: str,
    measure_col: str,
    measure_key: str,
) -> pd.DataFrame:
    """
    Pivot a loss run into a canonical long-format triangle for one measure.

    Steps:
    1. Aggregate values by (origin_period, eval_date) — sum duplicates.
    2. Pivot to wide: rows = origin periods, columns = eval dates (dev ages).
    3. Melt back to long format with standard column names.
    4. Return only populated (non-NaN) rows.

    Args:
        df:          Loss run DataFrame, already filtered to rows where
                     measure_col is non-null.
        origin_col:  Column containing origin / accident period labels.
        eval_col:    Column containing evaluation date / age labels.
        measure_col: Column containing the numeric measure values.
        measure_key: Canonical measure key string, e.g. "paid_losses".

    Returns:
        DataFrame with columns: origin_period, development_age, measure, value
    """
    # Coerce measure to numeric
    work = df[[origin_col, eval_col, measure_col]].copy()
    work[measure_col] = pd.to_numeric(
        work[measure_col].astype(str).str.replace(r"[\$,\s]", "", regex=True),
        errors="coerce",
    )
    work = work.dropna(subset=[measure_col])

    # Normalise labels
    work[origin_col] = work[origin_col].astype(str).str.strip()
    work[eval_col]   = work[eval_col].astype(str).str.strip()

    # Aggregate: multiple claims in same (origin, eval) cell → sum
    agg = (
        work
        .groupby([origin_col, eval_col], sort=False)[measure_col]
        .sum()
        .reset_index()
    )

    # Determine sorted order for origins and eval dates
    origin_order = sorted(
        agg[origin_col].unique(),
        key=lambda v: _parse_period(pd.Series([v])).iloc[0],
    )
    eval_order = sorted(
        agg[eval_col].unique(),
        key=lambda v: _parse_period(pd.Series([v])).iloc[0],
    )

    # Pivot to wide
    wide = agg.pivot(index=origin_col, columns=eval_col, values=measure_col)
    wide = wide.reindex(index=origin_order, columns=eval_order)

    # Melt back to canonical long format
    wide = wide.reset_index()
    long = wide.melt(
        id_vars=[origin_col],
        value_vars=eval_order,
        var_name="development_age",
        value_name="value",
    )
    long = long.rename(columns={origin_col: "origin_period"})
    long.insert(2, "measure", measure_key)

    # Drop unpopulated cells
    long = long.dropna(subset=["value"]).reset_index(drop=True)

    return long[["origin_period", "development_age", "measure", "value"]]


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class LossRunExtractionResult:
    """Result of converting a loss run to canonical long format."""
    output_path: Path                    # path of the saved canonical CSV
    extracted_measures: list[str]        # measure keys successfully extracted
    failed_measures: dict[str, str] = field(default_factory=dict)  # key → error msg


# ---------------------------------------------------------------------------
# Main extraction function
# ---------------------------------------------------------------------------

def extract_canonical_from_loss_run(
    df: pd.DataFrame,
    origin_col: str,
    eval_col: str,
    resolved_columns: dict[str, str],
    source_file_path: str | Path,
    output_path: Optional[str | Path] = None,
) -> LossRunExtractionResult:
    """
    Convert a validated loss run into a canonical four-column CSV identical
    in structure to the output of 1a-extract-triangle.py.

    Args:
        df:                The validated loss run DataFrame.
        origin_col:        Name of the column that holds accident / origin
                           period labels (resolved during validate-data Step 5).
        eval_col:          Name of the column that holds evaluation dates or
                           development age labels.
        resolved_columns:  Mapping of canonical measure key → column name in df,
                           as confirmed during validate-data Step 5.
                           Example: {"paid_losses": "Paid_Loss",
                                     "incurred_losses": "Incurred_Loss"}
                           Valid keys: "paid_losses", "incurred_losses",
                                       "reported_counts", "closed_counts"
        source_file_path:  Path to the original source file; used only to derive
                           the default output path.
        output_path:       Optional override for the output file path.  If None,
                           saved as {stem}-canonical.csv in the same directory
                           as source_file_path.

    Returns:
        LossRunExtractionResult with output_path, extracted_measures, and
        any failed_measures with their error messages.

    Raises:
        ValueError: If resolved_columns is empty or contains no valid measure keys.
    """
    if not resolved_columns:
        raise ValueError("resolved_columns must not be empty.")

    unknown = set(resolved_columns) - CANONICAL_MEASURES
    if unknown:
        raise ValueError(
            f"Unknown measure key(s): {unknown}. "
            f"Valid keys: {CANONICAL_MEASURES}"
        )

    # Derive output path
    src = Path(source_file_path).expanduser().resolve()
    if output_path is None:
        dest = src.with_name(f"{src.stem}-canonical.csv")
    else:
        dest = Path(output_path).expanduser().resolve()

    extracted_measures: list[str] = []
    failed_measures: dict[str, str] = {}
    long_frames: list[pd.DataFrame] = []

    for measure_key, col_name in resolved_columns.items():
        try:
            if col_name not in df.columns:
                raise KeyError(
                    f"Column '{col_name}' not found in DataFrame. "
                    f"Available columns: {list(df.columns)}"
                )

            long = _build_triangle(
                df=df,
                origin_col=origin_col,
                eval_col=eval_col,
                measure_col=col_name,
                measure_key=measure_key,
            )
            if long.empty:
                raise ValueError(
                    f"No populated rows produced for measure '{measure_key}'. "
                    "Check that the column contains numeric data."
                )

            long_frames.append(long)
            extracted_measures.append(measure_key)

        except Exception as exc:
            failed_measures[measure_key] = str(exc)

    if long_frames:
        canonical = pd.concat(long_frames, ignore_index=True)
        # Ensure column order matches 1a output exactly
        canonical = canonical[["origin_period", "development_age", "measure", "value"]]
        canonical.to_csv(dest, index=False)
    else:
        dest = src  # sentinel: nothing was written

    return LossRunExtractionResult(
        output_path=dest,
        extracted_measures=extracted_measures,
        failed_measures=failed_measures,
    )
