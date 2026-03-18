"""
goal: Step 3 of extract-canonical — read the canonical long-format CSV produced
      by Step 1 and extract the *latest diagonal*: for each (origin_period, measure)
      pair, keep only the row whose development_age is the most mature (maximum).

The result represents the most-developed known value per origin period — the
actuarial "diagonal" used as the starting point for loss development projections.

Output columns (same schema as the canonical CSV, subset of rows):
    origin_period     — accident/origin period label
    development_age   — the most mature development age for that origin period
    measure           — measure name (e.g. "paid", "incurred")
    value             — value at that development age

Rows are sorted by (measure, origin_period ascending).

Output file: {canonical_stem}-diagonal.csv
  e.g.  C:/data/triangles-canonical.csv
     →  C:/data/triangles-canonical-diagonal.csv

"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _try_parse_date(label: str) -> Optional[pd.Timestamp]:
    try:
        return pd.to_datetime(label, infer_datetime_format=True)
    except Exception:
        return None


def _try_parse_numeric(label: str) -> Optional[float]:
    import re
    m = re.search(r"(\d+(?:\.\d+)?)", str(label))
    return float(m.group(1)) if m else None


def _sort_key(label: str):
    """Unified sort key: prefer date, then numeric, then string."""
    dt = _try_parse_date(label)
    if dt is not None:
        return (0, dt.timestamp(), "")
    num = _try_parse_numeric(label)
    if num is not None:
        return (1, num, "")
    return (2, 0.0, label)


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class DiagonalResult:
    """Outcome of extract_diagonal()."""
    output_path: Path           # path to the saved diagonal CSV
    diagonal_df: pd.DataFrame   # the diagonal DataFrame (in memory)
    measures: list[str]         # measures present in the diagonal


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

def extract_diagonal(
    canonical_path: str | Path,
    output_path: Optional[str | Path] = None,
) -> DiagonalResult:
    """
    Extract the latest diagonal from a canonical long-format CSV.

    For each (origin_period, measure) pair, selects the row with the
    most mature (maximum) development age.

    Args:
        canonical_path: Path to the canonical long-format CSV produced by Step 1.
        output_path:    Override for output CSV location. Defaults to
                        {canonical_stem}-diagonal.csv in the same directory.

    Returns:
        DiagonalResult with the output path, the diagonal DataFrame, and
        the list of measures included.

    Raises:
        FileNotFoundError: If canonical_path does not exist.
        ValueError:        If the canonical CSV is missing required columns.
    """
    src = Path(canonical_path).expanduser().resolve()
    if not src.exists():
        raise FileNotFoundError(f"Canonical file not found: {src}")

    dest: Path
    if output_path is None:
        dest = src.with_name(f"{src.stem}-diagonal.csv")
    else:
        dest = Path(output_path).expanduser().resolve()

    # --- Load ---
    df = pd.read_csv(src)
    required = {"origin_period", "development_age", "measure", "value"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Canonical CSV is missing required columns: {missing}. "
            f"Found: {list(df.columns)}"
        )
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])

    # --- Sort development ages so the last one is the most mature ---
    all_dev_ages = df["development_age"].dropna().astype(str).unique().tolist()
    dev_age_order = {age: i for i, age in enumerate(
        sorted(all_dev_ages, key=_sort_key)
    )}
    df["_dev_rank"] = df["development_age"].map(dev_age_order)

    # --- For each (origin_period, measure), keep the row with the highest rank ---
    idx = (
        df.groupby(["origin_period", "measure"])["_dev_rank"]
        .idxmax()
    )
    diagonal = df.loc[idx, ["origin_period", "development_age", "measure", "value"]].copy()

    # --- Sort output: by measure, then origin_period ascending ---
    origin_order = {op: i for i, op in enumerate(
        sorted(df["origin_period"].astype(str).unique(), key=_sort_key)
    )}
    diagonal["_origin_rank"] = diagonal["origin_period"].map(origin_order)
    diagonal = (
        diagonal
        .sort_values(["measure", "_origin_rank"])
        .drop(columns=["_origin_rank"])
        .reset_index(drop=True)
    )

    measures = sorted(diagonal["measure"].unique().tolist())

    diagonal.to_csv(dest, index=False)

    return DiagonalResult(output_path=dest, diagonal_df=diagonal, measures=measures)
