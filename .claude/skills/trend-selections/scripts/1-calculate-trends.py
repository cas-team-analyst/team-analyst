"""
goal: Step 1 of trend-selections — fit least-squares annual trend lines for
      frequency, severity, and exposure across user-selected rolling time windows,
      to inform trend factor selection in Step 2.

inputs:
    ultimates_path  — path to {stem}-chain-ladder-ultimates.csv (ultimate-projections Step 2 output)
    canonical_path  — path to {stem}-canonical.csv (extract-canonical Step 1 output)
                      used to derive exposure per origin period
    periods         — list of rolling window sizes, any subset of [3, 4, 5, "all_year"]
    loss_measure    — which loss measure to use: "incurred_losses" or "paid_losses" (default: "incurred_losses")
    count_measure   — which count measure to use: "reported_counts" or "closed_counts" (default: "reported_counts")

Trend series derived per component:
    frequency     — {count_measure}_ultimate / exposure  (only if count measures present)
    severity      — {loss_measure}_ultimate / {count_measure}_ultimate  (only if count measures present)
    loss_ratio    — {loss_measure}_ultimate / exposure  (when count measures are absent)
    exposure      — diagonal value from canonical CSV (measure = "exposure")

Output file: {stem}-trends.csv saved alongside the ultimates CSV.
  e.g.  trip-canonical-chain-ladder-ultimates.csv
     →  trip-canonical-trends.csv

This script contains no user interaction.
"""

from __future__ import annotations

import warnings as _warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class CalculateTrendsResult:
    """Outcome of calculate_trends()."""
    output_path: Path            # path to the saved trends CSV
    trends_df: pd.DataFrame      # the trends DataFrame (in memory)
    components: list[str]        # components successfully fitted
    periods_used: list[str]      # period labels used (e.g. ["3_year", "all_year"])
    warnings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_PERIOD_LABEL = {3: "3_year", 4: "4_year", 5: "5_year", "all_year": "all_year"}
_COMPONENT_ORDER = {"frequency": 0, "severity": 1, "loss_ratio": 2, "exposure": 3}


def _period_label(period: Union[int, str]) -> str:
    return _PERIOD_LABEL.get(period, str(period))


def _fit_trend(series: pd.Series) -> tuple[float, float]:
    """
    Fit a least-squares log-linear trend to an ordered numeric series.

    Returns (annual_trend_factor, r_squared).
    annual_trend_factor is expressed as a factor, e.g. 1.05 for +5% per year.

    Uses log-linear regression: ln(y) = a + b*t, so b is the continuous
    annual rate; we convert to discrete: annual_factor = exp(b).
    """
    y = series.dropna().values
    if len(y) < 2:
        return float("nan"), float("nan")

    # Guard against non-positive values before taking log
    if np.any(y <= 0):
        return float("nan"), float("nan")

    t = np.arange(len(y), dtype=float)
    log_y = np.log(y)

    # OLS: log_y = a + b*t
    b, a = np.polyfit(t, log_y, 1)
    fitted = a + b * t
    ss_res = np.sum((log_y - fitted) ** 2)
    ss_tot = np.sum((log_y - log_y.mean()) ** 2)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")

    annual_trend_factor = round(np.exp(b), 4)
    r2 = round(r2, 4)
    return annual_trend_factor, r2


def _window_rows(
    series: pd.Series,
    period: Union[int, str],
) -> tuple[pd.Series, int, Optional[int]]:
    """
    Slice the tail of `series` to the requested rolling window.

    Returns (sliced_series, n_requested_or_None, n_used).
    """
    n_available = len(series.dropna())
    if period == "all_year":
        return series, None, n_available
    n_req = int(period)
    n_used = min(n_req, n_available)
    sliced = series.dropna().iloc[-n_used:]
    return sliced, n_req, n_used


def _sort_origin_periods(origin_periods: pd.Series) -> list:
    """Return origin period labels sorted chronologically (numeric or lexicographic)."""
    labels = origin_periods.unique().tolist()

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


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

def calculate_trends(
    ultimates_path: str | Path,
    canonical_path: str | Path,
    periods: list[Union[int, str]],
    loss_measure: str = "incurred_losses",
    count_measure: str = "reported_counts",
    output_path: Optional[str | Path] = None,
) -> CalculateTrendsResult:
    """
    Fit annual trend lines for exposure and loss ratio (if only loss measures present)
    or frequency and severity (if both count and loss measures present).

    Args:
        ultimates_path: Path to {stem}-chain-ladder-ultimates.csv (ultimate-projections Step 2 output).
        canonical_path: Path to {stem}-canonical.csv (extract-canonical Step 1 output).
        periods:        Rolling window sizes — any subset of [3, 4, 5, "all_year"].
        loss_measure:   Loss measure to use for severity/loss_ratio:
                        "incurred_losses" (default) or "paid_losses".
        count_measure:  Count measure to use for frequency and for severity denominator:
                        "reported_counts" (default) or "closed_counts".
        output_path:    Override output location. Defaults to
                        {ultimates_stem}-trends.csv alongside the ultimates CSV.

    Returns:
        CalculateTrendsResult with output path, trends DataFrame, and metadata.

    Raises:
        FileNotFoundError: If either input file does not exist.
        ValueError:        If required columns are missing.
    """
    ult_path = Path(ultimates_path).expanduser().resolve()
    can_path = Path(canonical_path).expanduser().resolve()

    if not ult_path.exists():
        raise FileNotFoundError(f"Ultimates CSV not found: {ult_path}")
    if not can_path.exists():
        raise FileNotFoundError(f"Canonical CSV not found: {can_path}")

    if output_path is None:
        dest = ult_path.with_name(f"{ult_path.stem}-trends.csv")
    else:
        dest = Path(output_path).expanduser().resolve()

    warn: list[str] = []

    # --- Load ultimates ---
    ult_df = pd.read_csv(ult_path)
    required_ult = {"measure", "origin_period", "ultimate"}
    missing = required_ult - set(ult_df.columns)
    if missing:
        raise ValueError(f"{ult_path} is missing required columns: {missing}. Found: {list(ult_df.columns)}")
    ult_df["ultimate"] = pd.to_numeric(ult_df["ultimate"], errors="coerce")
    ult_df["measure"] = ult_df["measure"].astype(str)
    ult_df["origin_period"] = ult_df["origin_period"].astype(str)

    available_measures = set(ult_df["measure"].unique())

    # --- Load canonical (for exposure) ---
    can_df = pd.read_csv(can_path)
    required_can = {"measure", "origin_period", "development_age", "value"}
    missing_can = required_can - set(can_df.columns)
    if missing_can:
        raise ValueError(f"{can_path} is missing required columns: {missing_can}. Found: {list(can_df.columns)}")
    can_df["value"] = pd.to_numeric(can_df["value"], errors="coerce")
    can_df["measure"] = can_df["measure"].astype(str)
    can_df["origin_period"] = can_df["origin_period"].astype(str)

    # --- Build pivot: measure × origin_period → ultimate ---
    # Use the union of all origin periods, sorted chronologically
    pivot = (
        ult_df
        .pivot_table(index="origin_period", columns="measure", values="ultimate", aggfunc="first")
        .reindex(_sort_origin_periods(ult_df["origin_period"]))
    )

    # --- Derive exposure series from canonical diagonal ---
    exp_available = "exposure" in can_df["measure"].values
    if exp_available:
        can_df["development_age"] = pd.to_numeric(can_df["development_age"], errors="coerce")
        exp_df = can_df[can_df["measure"] == "exposure"].copy()
        exp_diag_idx = (
            exp_df.dropna(subset=["development_age", "value"])
            .groupby("origin_period")["development_age"]
            .idxmax()
        )
        exp_diag = (
            exp_df.loc[exp_diag_idx, ["origin_period", "value"]]
            .set_index("origin_period")["value"]
            .reindex(_sort_origin_periods(exp_df["origin_period"]))
        )
    else:
        exp_diag = None
        warn.append("Measure 'exposure' not found in canonical CSV; exposure trend will be skipped.")

    # --- Determine which components to fit ---
    has_selected_loss = loss_measure in available_measures
    has_selected_count = count_measure in available_measures

    components_to_fit: dict[str, pd.Series] = {}

    if has_selected_loss and has_selected_count:
        # Severity = selected loss / selected count
        loss_col  = next((c for c in pivot.columns if c == loss_measure), None)
        count_col = next((c for c in pivot.columns if c == count_measure), None)
        if loss_col and count_col:
            sev = pivot[loss_col] / pivot[count_col]
            components_to_fit["severity"] = sev.dropna()
        else:
            warn.append(f"Could not derive severity — '{loss_measure}' or '{count_measure}' not found in ultimates.")
    elif has_selected_loss and not has_selected_count and exp_diag is not None:
        # No counts available — fall back to loss ratio = loss / exposure
        loss_col = next((c for c in pivot.columns if c == loss_measure), None)
        if loss_col:
            lr = pivot[loss_col] / exp_diag.reindex(pivot.index)
            components_to_fit["loss_ratio"] = lr.dropna()
        else:
            warn.append(f"Could not derive loss ratio — '{loss_measure}' not found in ultimates.")
    else:
        warn.append(
            f"Severity/loss ratio trend skipped — '{loss_measure}' not found in ultimates."
        )

    if has_selected_count and exp_diag is not None:
        count_col = next((c for c in pivot.columns if c == count_measure), None)
        if count_col:
            freq = pivot[count_col] / exp_diag.reindex(pivot.index)
            components_to_fit["frequency"] = freq.dropna()
        else:
            warn.append(f"Frequency trend skipped — '{count_measure}' not found in ultimates.")
    elif not has_selected_count:
        warn.append("Frequency trend skipped — count measures not present in ultimates.")

    if exp_diag is not None:
        components_to_fit["exposure"] = exp_diag.dropna()

    # --- Fit trend for each component × period ---
    rows: list[dict] = []

    for component, series in components_to_fit.items():
        n_available = len(series)
        for period in periods:
            sliced, n_req, n_used = _window_rows(series, period)
            annual_trend_factor, r2 = _fit_trend(sliced)
            if np.isnan(annual_trend_factor):
                warn.append(
                    f"Could not fit trend for '{component}', period '{_period_label(period)}' — "
                    f"fewer than 2 valid observations."
                )
            rows.append({
                "component": component,
                "period": _period_label(period),
                "n_available": n_available,
                "n_requested": n_req,
                "n_used": n_used,
                "annual_trend_factor": annual_trend_factor,
                "r_squared": r2,
            })

    if rows:
        out = pd.DataFrame(rows)
        out["_comp_order"] = out["component"].map(_COMPONENT_ORDER).fillna(99)
        out = out.sort_values(["_comp_order", "period"]).drop(columns=["_comp_order"]).reset_index(drop=True)
    else:
        out = pd.DataFrame(columns=[
            "component", "period", "n_available", "n_requested",
            "n_used", "annual_trend_factor", "r_squared",
        ])

    out.to_csv(dest, index=False)

    periods_used = [_period_label(p) for p in periods]
    components_fitted = list(components_to_fit.keys())

    return CalculateTrendsResult(
        output_path=dest,
        trends_df=out,
        components=components_fitted,
        periods_used=periods_used,
        warnings=warn,
    )
