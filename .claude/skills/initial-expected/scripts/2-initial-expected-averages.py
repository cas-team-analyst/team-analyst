"""
goal: Step 3 of initial-expected — compute averages of initial expected loss ratio
      and (optionally) frequency across origin periods using user-selected rolling time
      windows and average types from Step 5.

Mirrors the averaging logic of ldfs-diagnostics Step 2 (straight, olympic, weighted)
applied to origin-period rows instead of LDF observations.

inputs:
    initial_expected_path   — path to {stem}-initial-expected.csv (Step 5 / script 3 output)
    elr_periods             — list of rolling windows for ELR averaging; subset of [3, 4, 5, "all_year"]
    elr_avg_types           — list of average types for ELR; subset of ["straight", "olympic", "weighted"]
    freq_periods            — list of rolling windows for frequency averaging (same options)
                              required only when frequency rows are present
    freq_avg_types          — list of average types for frequency (same options)
                              required only when frequency rows are present

Average types
-------------
    straight  — simple arithmetic mean of the most recent N initial_values
    olympic   — straight mean after dropping the single highest and single lowest value
                (requires at least 3 observations; falls back to straight if fewer)
    weighted  — exposure-weighted mean: sum(initial_value * exposure) / sum(exposure)
                for the most recent N origin periods

Rolling windows
---------------
    3, 4, 5   — use the N most recent origin periods (capped at n_available if fewer exist)
    "all_year" — use all available origin periods

output columns:
    measure_type   — "loss_ratio" or "frequency"
    period         — "3_year", "4_year", "5_year", "all_year"
    avg_type       — "straight", "olympic", "weighted"
    n_available    — total origin period observations available for this measure_type
    n_requested    — window size requested (null for all_year)
    n_used         — actual n used (capped at n_available when fewer obs exist)
    average        — computed average initial expected value (6 decimal places)

Output file: {stem}-initial-expected-averages.csv saved alongside the initial-expected CSV.
  e.g.  trip-canonical-initial-expected.csv
     →  trip-canonical-initial-expected-averages.csv

This script contains no user interaction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class ComputeInitialExpectedAveragesResult:
    """Outcome of compute_initial_expected_averages()."""
    output_path: Path               # path to the saved averages CSV
    averages_df: pd.DataFrame       # the output DataFrame (in memory)
    measure_types: list[str]        # measure types present: "loss_ratio" and/or "frequency"
    warnings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_PERIOD_LABEL: dict = {3: "3_year", 4: "4_year", 5: "5_year", "all_year": "all_year"}


def _period_label(period: Union[int, str]) -> str:
    return _PERIOD_LABEL.get(period, str(period))


def _sort_origin_periods(labels: list) -> list:
    """Return origin period labels sorted chronologically (numeric or lexicographic)."""
    def _key(lbl):
        try:
            return (0, pd.to_datetime(lbl, infer_datetime_format=True).timestamp())
        except Exception:
            pass
        try:
            return (1, float(str(lbl).replace("Q", ".").replace("-", "")))
        except Exception:
            pass
        return (2, str(lbl))

    return sorted(labels, key=_key)


def _window_slice(
    values: pd.Series,
    exposures: pd.Series,
    period: Union[int, str],
) -> tuple[pd.Series, pd.Series, Optional[int], int]:
    """
    Select the tail of `values`/`exposures` to the requested rolling window.

    Returns (sliced_values, sliced_exposures, n_requested, n_used).
    n_requested is None for all_year.
    """
    n_available = len(values)
    if period == "all_year":
        return values, exposures, None, n_available
    n_req = int(period)
    n_used = min(n_req, n_available)
    return values.iloc[-n_used:], exposures.iloc[-n_used:], n_req, n_used


def _straight_avg(values: pd.Series) -> float:
    """Simple arithmetic mean."""
    v = values.dropna()
    if len(v) == 0:
        return float("nan")
    return float(v.mean())


def _olympic_avg(values: pd.Series) -> float:
    """
    Arithmetic mean after dropping the single highest and single lowest value.
    Falls back to straight mean when fewer than 3 observations are present.
    """
    v = values.dropna().values
    if len(v) < 3:
        # Not enough points to drop outliers — fall back to straight
        return float(np.mean(v)) if len(v) > 0 else float("nan")
    trimmed = sorted(v)[1:-1]  # drop one lowest and one highest
    return float(np.mean(trimmed))


def _weighted_avg(values: pd.Series, weights: pd.Series) -> float:
    """
    Exposure-weighted arithmetic mean.
    Uses paired (value, weight) rows where neither is NaN and weight > 0.
    """
    df = pd.DataFrame({"v": values, "w": weights}).dropna()
    df = df[df["w"] > 0]
    if df.empty:
        return float("nan")
    return float((df["v"] * df["w"]).sum() / df["w"].sum())


def _compute_averages(
    measure_df: pd.DataFrame,       # rows for one measure_type, sorted oldest→newest
    periods: list[Union[int, str]],
    avg_types: list[str],
    measure_type: str,
    warn: list[str],
) -> list[dict]:
    """
    Compute straight/olympic/weighted averages for each (period, avg_type) combination.
    Returns a list of row dicts.
    """
    rows: list[dict] = []

    # Ensure chronological order
    all_origins = _sort_origin_periods(measure_df["origin_period"].tolist())
    measure_df = measure_df.set_index("origin_period").reindex(all_origins)

    values = measure_df["initial_value"].astype(float)
    exposures = measure_df["exposure"].astype(float)
    n_available = len(values.dropna())

    for period in periods:
        sliced_vals, sliced_exp, n_req, n_used = _window_slice(values, exposures, period)
        plabel = _period_label(period)

        for avg_type in avg_types:
            if avg_type == "straight":
                avg = _straight_avg(sliced_vals)
            elif avg_type == "olympic":
                avg = _olympic_avg(sliced_vals)
                if n_used < 3:
                    warn.append(
                        f"{measure_type} | {plabel} | olympic: only {n_used} observation(s) available; "
                        "fell back to straight mean."
                    )
            elif avg_type == "weighted":
                avg = _weighted_avg(sliced_vals, sliced_exp)
            else:
                warn.append(f"Unknown avg_type '{avg_type}'; skipping.")
                continue

            if np.isnan(avg):
                warn.append(
                    f"{measure_type} | {plabel} | {avg_type}: could not compute average "
                    f"(no valid observations in window)."
                )

            rows.append({
                "measure_type": measure_type,
                "period": plabel,
                "avg_type": avg_type,
                "n_available": n_available,
                "n_requested": n_req,
                "n_used": n_used,
                "average": round(avg, 6) if not np.isnan(avg) else float("nan"),
            })

    return rows


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

def compute_initial_expected_averages(
    initial_expected_path: str | Path,
    elr_periods: list[Union[int, str]],
    elr_avg_types: list[str],
    freq_periods: Optional[list[Union[int, str]]] = None,
    freq_avg_types: Optional[list[str]] = None,
    output_path: Optional[str | Path] = None,
) -> ComputeInitialExpectedAveragesResult:
    """
    Compute rolling averages of initial expected loss ratio and frequency values.

    Args:
        initial_expected_path: Path to {stem}-initial-expected.csv (script 3 output).
        elr_periods:           Rolling window sizes for ELR — any subset of [3, 4, 5, "all_year"].
        elr_avg_types:         Average types for ELR — any subset of ["straight", "olympic", "weighted"].
        freq_periods:          Rolling window sizes for frequency (same options).
                               Required when frequency rows are present; ignored otherwise.
        freq_avg_types:        Average types for frequency (same options).
                               Required when frequency rows are present; ignored otherwise.
        output_path:           Override output location. Defaults to
                               {initial_expected_stem}-averages.csv alongside the input CSV.

    Returns:
        ComputeInitialExpectedAveragesResult with output path, DataFrame, measure types, warnings.

    Raises:
        FileNotFoundError: If the initial-expected CSV does not exist.
        ValueError:        If required columns are missing or invalid avg_types/periods provided.
    """
    ie_path = Path(initial_expected_path).expanduser().resolve()
    if not ie_path.exists():
        raise FileNotFoundError(f"Initial expected CSV not found: {ie_path}")

    if output_path is None:
        dest = ie_path.with_name(f"{ie_path.stem}-averages.csv")
    else:
        dest = Path(output_path).expanduser().resolve()

    # Validate inputs
    valid_periods = {3, 4, 5, "all_year"}
    valid_avg_types = {"straight", "olympic", "weighted"}

    for p in elr_periods:
        if p not in valid_periods:
            raise ValueError(f"Invalid elr_period '{p}'. Must be one of {valid_periods}.")
    for a in elr_avg_types:
        if a not in valid_avg_types:
            raise ValueError(f"Invalid elr_avg_type '{a}'. Must be one of {valid_avg_types}.")

    warn: list[str] = []

    # -----------------------------------------------------------------------
    # Load initial expected CSV
    # -----------------------------------------------------------------------
    ie_df = pd.read_csv(ie_path)
    required_cols = {"measure_type", "origin_period", "initial_value", "exposure"}
    missing = required_cols - set(ie_df.columns)
    if missing:
        raise ValueError(
            f"{ie_path} is missing required columns: {missing}. "
            f"Found: {list(ie_df.columns)}"
        )
    ie_df["initial_value"] = pd.to_numeric(ie_df["initial_value"], errors="coerce")
    ie_df["exposure"] = pd.to_numeric(ie_df["exposure"], errors="coerce")
    ie_df["measure_type"] = ie_df["measure_type"].astype(str)
    ie_df["origin_period"] = ie_df["origin_period"].astype(str)

    available_measure_types = set(ie_df["measure_type"].unique())
    has_frequency = "frequency" in available_measure_types

    # -----------------------------------------------------------------------
    # Compute averages per measure_type
    # -----------------------------------------------------------------------
    all_rows: list[dict] = []
    measure_types_seen: list[str] = []

    # --- ELR ---
    if "loss_ratio" in available_measure_types:
        elr_df = ie_df[ie_df["measure_type"] == "loss_ratio"].copy()
        elr_rows = _compute_averages(elr_df, elr_periods, elr_avg_types, "loss_ratio", warn)
        all_rows.extend(elr_rows)
        if elr_rows:
            measure_types_seen.append("loss_ratio")
    else:
        warn.append("No 'loss_ratio' rows found in initial-expected CSV; ELR averages skipped.")

    # --- Frequency ---
    if has_frequency:
        if not freq_periods:
            warn.append(
                "Frequency rows are present but freq_periods was not supplied; "
                "frequency averages skipped."
            )
        elif not freq_avg_types:
            warn.append(
                "Frequency rows are present but freq_avg_types was not supplied; "
                "frequency averages skipped."
            )
        else:
            # Validate frequency inputs
            for p in freq_periods:
                if p not in valid_periods:
                    raise ValueError(
                        f"Invalid freq_period '{p}'. Must be one of {valid_periods}."
                    )
            for a in freq_avg_types:
                if a not in valid_avg_types:
                    raise ValueError(
                        f"Invalid freq_avg_type '{a}'. Must be one of {valid_avg_types}."
                    )

            freq_df = ie_df[ie_df["measure_type"] == "frequency"].copy()
            freq_rows = _compute_averages(
                freq_df, freq_periods, freq_avg_types, "frequency", warn
            )
            all_rows.extend(freq_rows)
            if freq_rows:
                measure_types_seen.append("frequency")

    # -----------------------------------------------------------------------
    # Build and save output
    # -----------------------------------------------------------------------
    col_order = [
        "measure_type", "period", "avg_type",
        "n_available", "n_requested", "n_used",
        "average",
    ]
    if all_rows:
        out = pd.DataFrame(all_rows)[col_order]
        # Sort: loss_ratio first, then frequency; within each by period then avg_type
        type_order = {"loss_ratio": 0, "frequency": 1}
        out["_type_ord"] = out["measure_type"].map(type_order).fillna(99)
        out = (
            out.sort_values(["_type_ord", "period", "avg_type"])
            .drop(columns=["_type_ord"])
            .reset_index(drop=True)
        )
    else:
        out = pd.DataFrame(columns=col_order)

    out.to_csv(dest, index=False)

    return ComputeInitialExpectedAveragesResult(
        output_path=dest,
        averages_df=out,
        measure_types=measure_types_seen,
        warnings=warn,
    )
