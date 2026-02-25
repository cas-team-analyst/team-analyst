"""
goal: Step 2 of reserving-analysis — read the historical LDF CSV produced by
      Step 1 and calculate average LDFs for each (measure, age_from→age_to)
      development interval using user-specified time periods and average types.

Average types supported:
    straight  — simple arithmetic mean of the n most-recent LDFs
    olympic   — straight mean after dropping the single highest and lowest value
                (falls back to straight when n <= 2)
    weighted  — volume-weighted mean: sum(value_to) / sum(value_from) for the
                n most-recent observations, sorted by origin_period ascending

Time period options:
    3, 4, 5   — use only the n most-recent origin periods (by sort order)
    all_year  — use all available origin periods

For each (measure, age_from→age_to) interval the *available* n is capped at
the number of LDF observations present.  If the user requested, say, a 5-year
average for an interval that only has 3 observations, the output will show a
3-observation average (not NaN) and the `n_used` column will reflect the
actual count.

Output columns:
    measure       — triangle / measure name
    age_from      — "from" development age
    age_to        — "to" development age
    period        — time-period label: "3_year", "4_year", "5_year", "all_year"
    avg_type      — average type: "straight", "olympic", "weighted"
    n_available   — total LDF observations for this interval
    n_requested   — n passed by the user (or None for all_year)
    n_used        — min(n_requested, n_available)
    average_ldf   — the computed average (rounded to 3 decimal places)

Rows are sorted by (measure, age_from, period, avg_type).

Output file: {ldf_stem}-averages.csv
  e.g.  C:/data/triangles-canonical-ldfs.csv
     →  C:/data/triangles-canonical-ldfs-averages.csv

This script contains no user interaction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
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


def _straight(ldfs: pd.Series) -> float:
    """Simple arithmetic mean."""
    return float(ldfs.mean())


def _olympic(ldfs: pd.Series) -> float:
    """
    Arithmetic mean after dropping one highest and one lowest.
    Falls back to straight mean when len <= 2.
    """
    if len(ldfs) <= 2:
        return _straight(ldfs)
    trimmed = ldfs.sort_values().iloc[1:-1]
    return float(trimmed.mean())


def _weighted(ldfs: pd.Series, value_from: pd.Series, value_to: pd.Series) -> float:
    """
    Volume-weighted mean: sum(value_to) / sum(value_from).
    Returns NaN if sum(value_from) == 0.
    """
    denom = value_from.sum()
    if denom == 0:
        return float("nan")
    return float(value_to.sum() / denom)


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

_PERIOD_ORDER = {"3_year": 0, "4_year": 1, "5_year": 2, "all_year": 3}
_AVG_TYPE_ORDER = {"straight": 0, "olympic": 1, "weighted": 2}


@dataclass
class AverageLDFResult:
    """Outcome of calculate_average_ldfs()."""
    output_path: Path               # path to the saved averages CSV
    averages_df: pd.DataFrame       # the averages DataFrame (in memory)
    measures: list[str]             # measures present in the output
    periods_used: list[str]         # period labels computed (e.g. ["3_year", "all_year"])
    avg_types_used: list[str]       # average type labels computed
    warnings: list[str] = field(default_factory=list)
    # e.g. "3_year requested but only 2 obs available for paid_losses 12→24; used 2"


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

_VALID_PERIODS = {3, 4, 5, "all_year"}
_VALID_AVG_TYPES = {"straight", "olympic", "weighted"}


def calculate_average_ldfs(
    ldf_path: str | Path,
    periods: list,
    avg_types: list[str],
    output_path: Optional[str | Path] = None,
) -> AverageLDFResult:
    """
    Calculate average LDFs from the historical LDF CSV produced by Step 1.

    Args:
        ldf_path:    Path to the *-ldfs.csv file from Step 1.
        periods:     List of desired time periods.  Each element must be one of:
                     3, 4, 5 (int or str), or "all_year".
                     Duplicates are ignored.  Order doesn't matter.
        avg_types:   List of average type strings, each one of:
                     "straight", "olympic", "weighted".
                     Duplicates are ignored.
        output_path: Override output location. Defaults to
                     {ldf_stem}-averages.csv in the same directory.

    Returns:
        AverageLDFResult with output path, the averages DataFrame, and metadata.

    Raises:
        FileNotFoundError: If ldf_path does not exist.
        ValueError:        If the LDF CSV is missing required columns,
                           or if any period / avg_type value is invalid.
    """
    src = Path(ldf_path).expanduser().resolve()
    if not src.exists():
        raise FileNotFoundError(f"LDF file not found: {src}")

    if output_path is None:
        dest = src.with_name(f"{src.stem}-averages.csv")
    else:
        dest = Path(output_path).expanduser().resolve()

    # --- Validate inputs ---
    normalized_periods: list = []
    for p in periods:
        try:
            p_int = int(p)
            if p_int not in (3, 4, 5):
                raise ValueError(f"Invalid period '{p}': must be 3, 4, 5, or 'all_year'.")
            if p_int not in normalized_periods:
                normalized_periods.append(p_int)
        except (TypeError, ValueError):
            if str(p).lower() == "all_year":
                if "all_year" not in normalized_periods:
                    normalized_periods.append("all_year")
            else:
                raise ValueError(f"Invalid period '{p}': must be 3, 4, 5, or 'all_year'.")

    normalized_avg_types = []
    for t in avg_types:
        t_lower = str(t).lower()
        if t_lower not in _VALID_AVG_TYPES:
            raise ValueError(
                f"Invalid avg_type '{t}': must be one of {sorted(_VALID_AVG_TYPES)}."
            )
        if t_lower not in normalized_avg_types:
            normalized_avg_types.append(t_lower)

    if not normalized_periods:
        raise ValueError("At least one period must be specified.")
    if not normalized_avg_types:
        raise ValueError("At least one avg_type must be specified.")

    # --- Load LDF file ---
    df = pd.read_csv(src)
    required = {"measure", "origin_period", "age_from", "age_to",
                "value_from", "value_to", "ldf"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"LDF CSV is missing required columns: {missing}. "
            f"Found: {list(df.columns)}"
        )
    for col in ("value_from", "value_to", "ldf"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["ldf"]).copy()
    df["origin_period"] = df["origin_period"].astype(str)
    df["age_from"] = df["age_from"].astype(str)
    df["age_to"] = df["age_to"].astype(str)
    df["measure"] = df["measure"].astype(str)

    # --- Stable sort order for origin periods (ascending = oldest first) ---
    all_origins = df["origin_period"].unique().tolist()
    origin_rank = {op: i for i, op in enumerate(sorted(all_origins, key=_sort_key))}
    df["_origin_rank"] = df["origin_period"].map(origin_rank)

    # --- Stable sort order for age_from (ascending = youngest first) ---
    all_age_from = df["age_from"].unique().tolist()
    age_from_rank = {a: i for i, a in enumerate(sorted(all_age_from, key=_sort_key))}

    measures = sorted(df["measure"].unique().tolist())

    rows: list[dict] = []
    warnings: list[str] = []

    for measure in measures:
        mdf = df[df["measure"] == measure].copy()
        intervals = (
            mdf[["age_from", "age_to"]]
            .drop_duplicates()
            .assign(_rank=lambda x: x["age_from"].map(age_from_rank))
            .sort_values("_rank")
            .drop(columns="_rank")
        )

        for _, interval_row in intervals.iterrows():
            age_from = interval_row["age_from"]
            age_to = interval_row["age_to"]

            idf = (
                mdf[(mdf["age_from"] == age_from) & (mdf["age_to"] == age_to)]
                .sort_values("_origin_rank")
                .reset_index(drop=True)
            )
            n_available = len(idf)

            for period in normalized_periods:
                if period == "all_year":
                    period_label = "all_year"
                    n_requested = None
                    n_used = n_available
                    subset = idf
                else:
                    period_label = f"{period}_year"
                    n_requested = period
                    n_used = min(period, n_available)
                    subset = idf.tail(n_used)  # most-recent n origin periods

                    if n_used < period:
                        warnings.append(
                            f"{period}_year requested but only {n_available} obs available "
                            f"for {measure} {age_from}→{age_to}; used {n_used}."
                        )

                ldf_series = subset["ldf"].reset_index(drop=True)
                vf_series = subset["value_from"].reset_index(drop=True)
                vt_series = subset["value_to"].reset_index(drop=True)

                for avg_type in normalized_avg_types:
                    if avg_type == "straight":
                        avg_val = _straight(ldf_series)
                    elif avg_type == "olympic":
                        avg_val = _olympic(ldf_series)
                    else:  # weighted
                        avg_val = _weighted(ldf_series, vf_series, vt_series)

                    rows.append({
                        "measure": measure,
                        "age_from": age_from,
                        "age_to": age_to,
                        "period": period_label,
                        "avg_type": avg_type,
                        "n_available": n_available,
                        "n_requested": n_requested,
                        "n_used": n_used,
                        "average_ldf": round(avg_val, 3),
                    })

    # --- Assemble and sort output ---
    if rows:
        out = pd.DataFrame(rows)
        out["_age_rank"] = out["age_from"].map(age_from_rank)
        out["_period_rank"] = out["period"].map(_PERIOD_ORDER)
        out["_avg_rank"] = out["avg_type"].map(_AVG_TYPE_ORDER)
        out = (
            out
            .sort_values(["measure", "_age_rank", "_period_rank", "_avg_rank"])
            .drop(columns=["_age_rank", "_period_rank", "_avg_rank"])
            .reset_index(drop=True)
        )
    else:
        out = pd.DataFrame(
            columns=["measure", "age_from", "age_to", "period", "avg_type",
                     "n_available", "n_requested", "n_used", "average_ldf"]
        )

    out.to_csv(dest, index=False)

    period_labels = sorted(
        {r["period"] for r in rows},
        key=lambda p: _PERIOD_ORDER.get(p, 99),
    )

    return AverageLDFResult(
        output_path=dest,
        averages_df=out,
        measures=measures,
        periods_used=period_labels,
        avg_types_used=list(normalized_avg_types),
        warnings=warnings,
    )
