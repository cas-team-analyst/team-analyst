"""
goal: Step 1 of reserving-analysis — read the canonical long-format CSV produced
      by extract-canonical and calculate historical link development factors (LDFs)
      for every available (origin_period, development_age) age pair for each
      measure (triangle).

A historical LDF for (origin_period O, development_age D) is defined as:

    LDF(O, D) = value(O, D_next) / value(O, D)

where D_next is the next older development age in the ordered sequence of
development ages present in the canonical data.

Only pairs where both value(O, D) and value(O, D_next) are non-null and the
denominator is non-zero are included in the output.

Output columns:
    measure           — triangle / measure name (e.g. "paid_losses")
    origin_period     — accident/origin period label
    age_from          — the "from" age (younger) in the LDF ratio
    age_to            — the "to" age (older/next) in the LDF ratio
    value_from        — value at age_from
    value_to          — value at age_to
    ldf               — value_to / value_from (rounded to 3 decimal places)

Rows are sorted by (measure, age_from, origin_period).

Output file: {canonical_stem}-ldfs.csv
  e.g.  C:/data/triangles-canonical.csv
     →  C:/data/triangles-canonical-ldfs.csv

This script contains no user interaction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
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
    """Unified sort key: prefer date parse, then numeric, then string."""
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
class LDFResult:
    """Outcome of calculate_historical_ldfs()."""
    output_path: Path               # path to the saved LDF CSV
    ldf_df: pd.DataFrame            # the LDF DataFrame (in memory)
    measures: list[str]             # measures present in the output
    development_age_pairs: list[tuple]  # sorted list of (age_from, age_to) pairs
    skipped_pairs: list[dict] = field(default_factory=list)
    # each entry: {measure, origin_period, development_age, reason}


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

def calculate_historical_ldfs(
    canonical_path: str | Path,
    output_path: Optional[str | Path] = None,
) -> LDFResult:
    """
    Calculate historical LDFs from a canonical long-format CSV.

    For each measure (triangle) and each consecutive pair of development ages
    (D, D_next), compute:

        LDF(origin_period, D) = value(origin_period, D_next)
                               / value(origin_period, D)

    Only (origin_period, D) pairs where both values are present, non-null,
    and the denominator is non-zero are included.

    Args:
        canonical_path: Path to the canonical long-format CSV produced by
                        extract-canonical Step 1.
        output_path:    Override for output CSV location. Defaults to
                        {canonical_stem}-ldfs.csv in the same directory.

    Returns:
        LDFResult with output path, the LDF DataFrame, the list of measures,
        the list of (age_from, age_to) pairs, and any skipped pairs.

    Raises:
        FileNotFoundError: If canonical_path does not exist.
        ValueError:        If the canonical CSV is missing required columns.
    """
    src = Path(canonical_path).expanduser().resolve()
    if not src.exists():
        raise FileNotFoundError(f"Canonical file not found: {src}")

    if output_path is None:
        dest = src.with_name(f"{src.stem}-ldfs.csv")
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
    df = df.dropna(subset=["value"]).copy()
    df["origin_period"] = df["origin_period"].astype(str)
    df["development_age"] = df["development_age"].astype(str)
    df["measure"] = df["measure"].astype(str)

    # --- Determine sorted development age sequence (shared across all measures) ---
    all_dev_ages = df["development_age"].unique().tolist()
    sorted_dev_ages: list[str] = sorted(all_dev_ages, key=_sort_key)

    # Consecutive age pairs: (younger, older)
    age_pairs: list[tuple[str, str]] = [
        (sorted_dev_ages[i], sorted_dev_ages[i + 1])
        for i in range(len(sorted_dev_ages) - 1)
    ]

    # --- Build pivot per measure for fast lookups ---
    measures = sorted(df["measure"].unique().tolist())
    rows: list[dict] = []
    skipped: list[dict] = []

    for measure in measures:
        mdf = df[df["measure"] == measure]
        # pivot: index = origin_period, columns = development_age
        pivot = mdf.pivot_table(
            index="origin_period",
            columns="development_age",
            values="value",
            aggfunc="first",   # canonical data has at most one value per cell
        )

        for age_from, age_to in age_pairs:
            # Only process if both ages exist as columns in this measure's pivot
            if age_from not in pivot.columns or age_to not in pivot.columns:
                continue

            col_from = pivot[age_from]
            col_to = pivot[age_to]

            for origin in pivot.index:
                v_from = col_from.get(origin)
                v_to = col_to.get(origin)

                # Skip if either value is missing
                if pd.isna(v_from) or pd.isna(v_to):
                    continue

                # Skip if denominator is zero
                if v_from == 0:
                    skipped.append({
                        "measure": measure,
                        "origin_period": origin,
                        "development_age": age_from,
                        "age_to": age_to,
                        "reason": "zero denominator",
                    })
                    continue

                rows.append({
                    "measure": measure,
                    "origin_period": origin,
                    "age_from": age_from,
                    "age_to": age_to,
                    "value_from": v_from,
                    "value_to": v_to,
                    "ldf": round(v_to / v_from, 3),
                })

    # --- Assemble output DataFrame ---
    if rows:
        out = pd.DataFrame(rows)

        # Sort: measure, then development_age (by sorted order), then origin_period
        age_from_rank = {age: i for i, (age, _) in enumerate(age_pairs)}
        out["_age_rank"] = out["age_from"].map(age_from_rank)
        origin_rank = {
            op: i
            for i, op in enumerate(
                sorted(df["origin_period"].unique().tolist(), key=_sort_key)
            )
        }
        out["_origin_rank"] = out["origin_period"].map(origin_rank)
        out = (
            out
            .sort_values(["measure", "_age_rank", "_origin_rank"])
            .drop(columns=["_age_rank", "_origin_rank"])
            .reset_index(drop=True)
        )
    else:
        out = pd.DataFrame(
            columns=["measure", "origin_period", "age_from", "age_to",
                     "value_from", "value_to", "ldf"]
        )

    out.to_csv(dest, index=False)

    return LDFResult(
        output_path=dest,
        ldf_df=out,
        measures=measures,
        development_age_pairs=age_pairs,
        skipped_pairs=skipped,
    )
