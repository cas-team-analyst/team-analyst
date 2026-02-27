"""
goal: Step 2 of initial-expected — compute initial expected loss ratio and
      (optionally) initial expected frequency per origin period from blended
      chain-ladder ultimates and selected trend factors.

Formulas
--------
Trend compounding
-----------------
Each component's annual trend factor is compounded by the number of years between
the origin period and the most recent origin period (the "trend step").

    trend_step(origin) = n_origin_periods - 1 - rank(origin)   # rank 0 = most recent

So if the annual severity trend is 1.05 and there are 3 origin periods:
    most recent  → 1.05^0 = 1.0000
    one year old → 1.05^1 = 1.0500
    two years old→ 1.05^2 = 1.1025

Initial expected loss ratio (per origin period) — when counts ARE present:
    blended_loss_ult  = paid_weight * paid_cl_ult + (1 - paid_weight) * incurred_cl_ult
    initial_elr       = blended_loss_ult
                        * severity_trend_annual ^ trend_step
                        * frequency_trend_annual ^ trend_step
                        / (exposure * exposure_trend_annual ^ trend_step)

Initial expected loss ratio (per origin period) — when NO counts are present:
    initial_elr       = blended_loss_ult
                        * loss_ratio_trend_annual ^ trend_step
                        / (exposure * exposure_trend_annual ^ trend_step)
    (severity_trend = 1.0; frequency_trend column stores the compounded loss_ratio_trend)

Initial expected frequency (per origin period, only when count measures present):
    blended_count_ult = rptd_weight * rptd_cl_ult + (1 - rptd_weight) * closed_cl_ult
    initial_freq      = blended_count_ult
                        * frequency_trend_annual ^ trend_step
                        / (exposure * exposure_trend_annual ^ trend_step)

inputs:
    ultimates_path          — path to {stem}-chain-ladder-ultimates.csv (Step 2 output)
    trend_selections_path   — path to {stem}-trend-selections.json (Step 4 output)
    canonical_path          — path to {stem}-canonical.csv (extract-canonical Step 1 output)
                              used to derive exposure per origin period
    elr_paid_weight         — float [0, 1]; weight on paid loss CL ultimate for the ELR
                              (0.0 → 100% incurred, 1.0 → 100% paid).
                              Defaults to 1.0 if only paid is available, 0.0 if only incurred.
    freq_rptd_weight        — float [0, 1]; weight on reported counts CL ultimate for frequency
                              (0.0 → 100% closed, 1.0 → 100% reported).
                              Defaults to 1.0 if only reported is available, 0.0 if only closed.
                              Ignored (and frequency rows omitted) when no count measures present.

output columns:
    measure_type            — "loss_ratio" or "frequency"
    origin_period           — accident / origin period label
    blended_ult             — weighted average of CL ultimates (loss or count, per measure_type)
    exposure                — exposure for this origin period (from canonical diagonal)
    trend_step              — number of years from this origin period to the most recent one (most recent = 0)
    severity_trend          — compounded severity annual factor ^ trend_step
                              (loss_ratio rows only; null for frequency rows;
                               always 1.0 when no count measures present — severity not separately fitted)
    frequency_trend         — compounded frequency annual factor ^ trend_step when counts are present;
                              compounded loss_ratio annual factor ^ trend_step when no counts present
    exposure_trend          — compounded exposure annual factor ^ trend_step
    initial_value           — computed initial ELR or initial frequency

Output file: {stem}-initial-expected.csv saved alongside the ultimates CSV.
  e.g.  trip-canonical-chain-ladder-ultimates.csv
     →  trip-canonical-initial-expected.csv

This script contains no user interaction.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import pandas as pd


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class ComputeInitialExpectedResult:
    """Outcome of compute_initial_expected()."""
    output_path: Path              # path to the saved initial-expected CSV
    initial_expected_df: pd.DataFrame  # the output DataFrame (in memory)
    measure_types: list[str]       # measure types present: "loss_ratio" and/or "frequency"
    warnings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

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


def _get_trend_factor(trend_selections: dict, component: str, fallback: float = 1.0) -> float:
    """
    Extract selected_factor for a component from trend-selections.json.
    Returns fallback if the component is absent.
    """
    block = trend_selections.get(component)
    if block is None:
        return fallback
    return float(block.get("selected_factor", fallback))


def _get_diagonal_exposure(can_df: pd.DataFrame) -> Optional[pd.Series]:
    """
    Derive exposure per origin period from the canonical diagonal
    (latest development age for measure == "exposure").
    Returns a Series indexed by origin_period, or None if not present.
    """
    if "exposure" not in can_df["measure"].values:
        return None
    exp_df = can_df[can_df["measure"] == "exposure"].copy()
    exp_df["development_age"] = pd.to_numeric(exp_df["development_age"], errors="coerce")
    idx = (
        exp_df.dropna(subset=["development_age", "value"])
        .groupby("origin_period")["development_age"]
        .idxmax()
    )
    return (
        exp_df.loc[idx, ["origin_period", "value"]]
        .set_index("origin_period")["value"]
    )


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

def compute_initial_expected(
    ultimates_path: str | Path,
    trend_selections_path: str | Path,
    canonical_path: str | Path,
    elr_paid_weight: Optional[float] = None,
    freq_rptd_weight: Optional[float] = None,
    output_path: Optional[str | Path] = None,
) -> ComputeInitialExpectedResult:
    """
    Compute initial expected loss ratio and frequency per origin period.

    Args:
        ultimates_path:        Path to {stem}-chain-ladder-ultimates.csv (Step 2 output).
        trend_selections_path: Path to {stem}-trend-selections.json (Step 4 output).
        canonical_path:        Path to {stem}-canonical.csv (extract-canonical Step 1 output).
        elr_paid_weight:       Weight on paid loss CL ultimate for the blended ELR numerator.
                               Must be in [0, 1]. Defaults to 1.0 if only paid is available,
                               0.0 if only incurred is available, and is required if both are.
        freq_rptd_weight:      Weight on reported counts CL ultimate for the blended frequency
                               numerator. Must be in [0, 1]. Defaults to 1.0 if only reported
                               is available, 0.0 if only closed is available, and is required
                               if both are. Ignored when no count measures are present.
        output_path:           Override output location. Defaults to
                               {stem}-initial-expected.csv alongside the ultimates CSV.

    Returns:
        ComputeInitialExpectedResult with output path, DataFrame, measure types, and warnings.

    Raises:
        FileNotFoundError: If any input file does not exist.
        ValueError:        If required columns are missing, weights are out of range,
                           or required weights are not supplied when both measures are available.
    """
    ult_path = Path(ultimates_path).expanduser().resolve()
    trend_path = Path(trend_selections_path).expanduser().resolve()
    can_path = Path(canonical_path).expanduser().resolve()

    for p in (ult_path, trend_path, can_path):
        if not p.exists():
            raise FileNotFoundError(f"File not found: {p}")

    if output_path is None:
        dest = can_path.with_name(f"{can_path.stem}-initial-expected.csv")
    else:
        dest = Path(output_path).expanduser().resolve()

    warn: list[str] = []

    # -----------------------------------------------------------------------
    # Load ultimates
    # -----------------------------------------------------------------------
    ult_df = pd.read_csv(ult_path)
    required_ult = {"measure", "origin_period", "ultimate"}
    missing = required_ult - set(ult_df.columns)
    if missing:
        raise ValueError(
            f"{ult_path} is missing required columns: {missing}. "
            f"Found: {list(ult_df.columns)}"
        )
    ult_df["ultimate"] = pd.to_numeric(ult_df["ultimate"], errors="coerce")
    ult_df["measure"] = ult_df["measure"].astype(str)
    ult_df["origin_period"] = ult_df["origin_period"].astype(str)

    available_measures = set(ult_df["measure"].unique())

    # -----------------------------------------------------------------------
    # Load trend selections
    # -----------------------------------------------------------------------
    with open(trend_path, "r") as f:
        trend_sel: dict = json.load(f)
    if not isinstance(trend_sel, dict):
        raise ValueError(f"{trend_path} must be a JSON object keyed by component name.")

    # -----------------------------------------------------------------------
    # Load canonical (exposure)
    # -----------------------------------------------------------------------
    can_df = pd.read_csv(can_path)
    required_can = {"measure", "origin_period", "development_age", "value"}
    missing_can = required_can - set(can_df.columns)
    if missing_can:
        raise ValueError(
            f"{can_path} is missing required columns: {missing_can}. "
            f"Found: {list(can_df.columns)}"
        )
    can_df["value"] = pd.to_numeric(can_df["value"], errors="coerce")
    can_df["measure"] = can_df["measure"].astype(str)
    can_df["origin_period"] = can_df["origin_period"].astype(str)

    exp_series = _get_diagonal_exposure(can_df)
    if exp_series is None:
        raise ValueError(
            "Measure 'exposure' not found in canonical CSV. "
            "Exposure is required to compute initial ELR and frequency."
        )

    # -----------------------------------------------------------------------
    # Pivot ultimates: origin_period × measure → ultimate
    # -----------------------------------------------------------------------
    all_origins = _sort_origin_periods(ult_df["origin_period"].unique().tolist())
    pivot = (
        ult_df
        .pivot_table(index="origin_period", columns="measure", values="ultimate", aggfunc="first")
        .reindex(all_origins)
    )

    # -----------------------------------------------------------------------
    # Detect presence of loss and count measures
    # -----------------------------------------------------------------------
    has_paid = "paid_losses" in available_measures
    has_incurred = "incurred_losses" in available_measures
    has_reported = "reported_counts" in available_measures
    has_closed = "closed_counts" in available_measures
    has_counts = has_reported or has_closed

    # -----------------------------------------------------------------------
    # Resolve ELR paid weight
    # -----------------------------------------------------------------------
    if has_paid and has_incurred:
        if elr_paid_weight is None:
            raise ValueError(
                "Both 'paid_losses' and 'incurred_losses' ultimates are present. "
                "Supply elr_paid_weight (float in [0, 1])."
            )
        if not (0.0 <= elr_paid_weight <= 1.0):
            raise ValueError(f"elr_paid_weight must be in [0, 1]; got {elr_paid_weight}.")
    elif has_paid:
        if elr_paid_weight is not None and elr_paid_weight != 1.0:
            warn.append(
                "Only 'paid_losses' is available; elr_paid_weight overridden to 1.0."
            )
        elr_paid_weight = 1.0
    elif has_incurred:
        if elr_paid_weight is not None and elr_paid_weight != 0.0:
            warn.append(
                "Only 'incurred_losses' is available; elr_paid_weight overridden to 0.0."
            )
        elr_paid_weight = 0.0
    else:
        warn.append(
            "Neither 'paid_losses' nor 'incurred_losses' found in ultimates. "
            "Loss ratio rows will be skipped."
        )
        elr_paid_weight = None

    # -----------------------------------------------------------------------
    # Resolve frequency count weight
    # -----------------------------------------------------------------------
    if has_counts:
        if has_reported and has_closed:
            if freq_rptd_weight is None:
                raise ValueError(
                    "Both 'reported_counts' and 'closed_counts' ultimates are present. "
                    "Supply freq_rptd_weight (float in [0, 1])."
                )
            if not (0.0 <= freq_rptd_weight <= 1.0):
                raise ValueError(f"freq_rptd_weight must be in [0, 1]; got {freq_rptd_weight}.")
        elif has_reported:
            if freq_rptd_weight is not None and freq_rptd_weight != 1.0:
                warn.append(
                    "Only 'reported_counts' is available; freq_rptd_weight overridden to 1.0."
                )
            freq_rptd_weight = 1.0
        else:  # only closed
            if freq_rptd_weight is not None and freq_rptd_weight != 0.0:
                warn.append(
                    "Only 'closed_counts' is available; freq_rptd_weight overridden to 0.0."
                )
            freq_rptd_weight = 0.0

    # -----------------------------------------------------------------------
    # Extract annual trend factors from trend-selections.json
    # -----------------------------------------------------------------------
    if has_counts:
        # Separate severity and frequency trends when counts are present
        severity_trend_annual   = _get_trend_factor(trend_sel, "severity",  fallback=1.0)
        frequency_trend_annual  = _get_trend_factor(trend_sel, "frequency", fallback=1.0)
        loss_ratio_trend_annual = None  # not used when counts are present
    else:
        # No counts — use the loss_ratio trend selected in Step 4 as the sole ELR trend factor.
        # Severity is not separately fitted; the loss_ratio trend captures the combined
        # loss / exposure movement and is stored in the frequency_trend output column.
        severity_trend_annual   = 1.0
        loss_ratio_trend_annual = _get_trend_factor(trend_sel, "loss_ratio", fallback=1.0)
        frequency_trend_annual  = loss_ratio_trend_annual

    exposure_trend_annual = _get_trend_factor(trend_sel, "exposure", fallback=1.0)

    if "severity" not in trend_sel and has_counts:
        warn.append("'severity' not found in trend-selections.json; severity annual trend defaulted to 1.0.")
    if "frequency" not in trend_sel and has_counts:
        warn.append("'frequency' not found in trend-selections.json; frequency annual trend defaulted to 1.0.")
    if "loss_ratio" not in trend_sel and not has_counts:
        warn.append("'loss_ratio' not found in trend-selections.json; loss_ratio annual trend defaulted to 1.0.")
    if "exposure" not in trend_sel:
        warn.append("'exposure' not found in trend-selections.json; exposure annual trend defaulted to 1.0.")

    # Pre-compute the number of origin periods so we can derive trend_step per period.
    # all_origins is sorted oldest → newest; the most recent period (index n-1) has step 0,
    # the next oldest (index n-2) has step 1, and so on.
    n_origins = len(all_origins)
    origin_trend_step: dict[str, int] = {
        op: (n_origins - 1 - i) for i, op in enumerate(all_origins)
    }

    # -----------------------------------------------------------------------
    # Compute rows
    # -----------------------------------------------------------------------
    rows: list[dict] = []
    measure_types_seen: list[str] = []

    # Align exposure to origin periods in pivot
    exp_aligned = exp_series.reindex(all_origins)

    for origin_period in all_origins:
        exp_val = exp_aligned.get(origin_period) if exp_aligned is not None else None
        if pd.isna(exp_val) or exp_val is None:
            warn.append(
                f"No exposure found for origin period '{origin_period}'; skipping all rows for this period."
            )
            continue

        # Compounding step for this origin period
        step = origin_trend_step[origin_period]
        sev_trend_comp  = round(severity_trend_annual  ** step, 6)
        freq_trend_comp = round(frequency_trend_annual ** step, 6)
        exp_trend_comp  = round(exposure_trend_annual  ** step, 6)

        # --- Loss ratio row ---
        if elr_paid_weight is not None:
            paid_ult = pivot.at[origin_period, "paid_losses"] if has_paid else float("nan")
            incurred_ult = pivot.at[origin_period, "incurred_losses"] if has_incurred else float("nan")

            # Weighted blend
            blended_loss = (
                (elr_paid_weight * paid_ult if has_paid and not pd.isna(paid_ult) else 0.0)
                + ((1.0 - elr_paid_weight) * incurred_ult if has_incurred and not pd.isna(incurred_ult) else 0.0)
            )

            # If the blend produced zero because one component was NaN, warn and skip
            if pd.isna(blended_loss):
                warn.append(
                    f"Could not compute blended loss ultimate for origin '{origin_period}'; "
                    "skipping loss ratio row."
                )
            else:
                denominator = exp_val * exp_trend_comp
                if denominator == 0:
                    warn.append(
                        f"Zero denominator (exposure × exposure_trend) for origin '{origin_period}'; "
                        "skipping loss ratio row."
                    )
                else:
                    initial_elr = blended_loss * sev_trend_comp * freq_trend_comp / denominator
                    rows.append({
                        "measure_type": "loss_ratio",
                        "origin_period": origin_period,
                        "blended_ult": round(blended_loss, 2),
                        "exposure": round(float(exp_val), 2),
                        "trend_step": step,
                        "severity_trend": sev_trend_comp,
                        "frequency_trend": freq_trend_comp,
                        "exposure_trend": exp_trend_comp,
                        "initial_value": round(initial_elr, 6),
                    })
                    if "loss_ratio" not in measure_types_seen:
                        measure_types_seen.append("loss_ratio")

        # --- Frequency row ---
        if has_counts:
            rptd_ult = pivot.at[origin_period, "reported_counts"] if has_reported else float("nan")
            closed_ult = pivot.at[origin_period, "closed_counts"] if has_closed else float("nan")

            blended_count = (
                (freq_rptd_weight * rptd_ult if has_reported and not pd.isna(rptd_ult) else 0.0)
                + ((1.0 - freq_rptd_weight) * closed_ult if has_closed and not pd.isna(closed_ult) else 0.0)
            )

            if pd.isna(blended_count):
                warn.append(
                    f"Could not compute blended count ultimate for origin '{origin_period}'; "
                    "skipping frequency row."
                )
            else:
                denominator = exp_val * exp_trend_comp
                if denominator == 0:
                    warn.append(
                        f"Zero denominator (exposure × exposure_trend) for origin '{origin_period}'; "
                        "skipping frequency row."
                    )
                else:
                    initial_freq = blended_count * freq_trend_comp / denominator
                    rows.append({
                        "measure_type": "frequency",
                        "origin_period": origin_period,
                        "blended_ult": round(blended_count, 2),
                        "exposure": round(float(exp_val), 2),
                        "trend_step": step,
                        "severity_trend": None,
                        "frequency_trend": freq_trend_comp,
                        "exposure_trend": exp_trend_comp,
                        "initial_value": round(initial_freq, 6),
                    })
                    if "frequency" not in measure_types_seen:
                        measure_types_seen.append("frequency")

    # -----------------------------------------------------------------------
    # Build and save output
    # -----------------------------------------------------------------------
    col_order = [
        "measure_type", "origin_period",
        "blended_ult",
        "exposure",
        "trend_step",
        "severity_trend", "frequency_trend", "exposure_trend",
        "initial_value",
    ]
    if rows:
        out = pd.DataFrame(rows)[col_order]
        # Sort: loss_ratio rows first, then frequency, then by origin period within each group
        type_order = {"loss_ratio": 0, "frequency": 1}
        out["_type_ord"] = out["measure_type"].map(type_order).fillna(99)
        out["_origin_ord"] = out["origin_period"].map(
            {op: i for i, op in enumerate(all_origins)}
        )
        out = (
            out.sort_values(["_type_ord", "_origin_ord"])
            .drop(columns=["_type_ord", "_origin_ord"])
            .reset_index(drop=True)
        )
    else:
        out = pd.DataFrame(columns=col_order)

    out.to_csv(dest, index=False)

    return ComputeInitialExpectedResult(
        output_path=dest,
        initial_expected_df=out,
        measure_types=measure_types_seen,
        warnings=warn,
    )
