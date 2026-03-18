"""
goal: Step 5 of initial-expected — compute initial expected ultimate losses and
      (optionally) initial expected ultimate counts per origin period from the
      selected initial expected loss ratio / frequency (Step 4 output) combined
      with per-period trend factors and exposures (Step 2 output).

Formulas
--------

When count measures ARE present:
    initial_expected_loss_ult(origin)
        = selected_elr
          * exposure
          * exposure_trend
          / (severity_trend * frequency_trend)

When count measures are NOT present:
    initial_expected_loss_ult(origin)
        = selected_elr
          * exposure
          * exposure_trend
          / frequency_trend          # frequency_trend column stores the compounded
                                     # loss_ratio trend when no counts are present

Initial expected counts (only when count measures are present):
    initial_expected_counts(origin)
        = selected_frequency
          * exposure
          * exposure_trend
          / frequency_trend

Where the trend factors (severity_trend, frequency_trend, exposure_trend) and
exposure values are taken directly from the `{stem}-initial-expected.csv` rows
produced in Step 2, which already store the compounded per-period values.

inputs:
    initial_expected_path       — path to {stem}-initial-expected.csv (Step 2 output)
                                  provides: exposure, severity_trend, frequency_trend,
                                            exposure_trend per origin period
    ie_selections_path          — path to {stem}-initial-expected-selections.json (Step 4 output)
                                  provides: selected_average for loss_ratio and/or frequency

output columns:
    measure_type                — "loss_ratio" or "frequency"
    origin_period               — accident / origin period label
    selected_ie_value           — the selected initial expected value (ELR or freq) from Step 4
    exposure                    — exposure for this origin period
    severity_trend              — compounded severity factor for this period (loss_ratio rows;
                                  null for frequency rows; always 1.0 when no counts present)
    frequency_trend             — compounded frequency or loss_ratio factor for this period
    exposure_trend              — compounded exposure factor for this period
    ie_ultimate                 — computed initial expected ultimate (losses or counts)

Output file: {stem}-initial-expected-ultimates.csv saved alongside the initial-expected CSV.
  e.g.  trip-canonical-initial-expected.csv
     →  trip-canonical-initial-expected-ultimates.csv

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
class ComputeIEUltimatesResult:
    """Outcome of compute_ie_ultimates()."""
    output_path: Path                  # path to the saved ultimates CSV
    ultimates_df: pd.DataFrame         # the output DataFrame (in memory)
    measure_types: list[str]           # measure types present: "loss_ratio" and/or "frequency"
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


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

def compute_ie_ultimates(
    initial_expected_path: str | Path,
    ie_selections_path: str | Path,
    output_path: Optional[str | Path] = None,
) -> ComputeIEUltimatesResult:
    """
    Compute initial expected ultimate losses and (optionally) counts per origin period.

    Args:
        initial_expected_path: Path to {stem}-initial-expected.csv (Step 2 output).
                               Provides per-origin-period exposure and compounded trend factors.
        ie_selections_path:    Path to {stem}-initial-expected-selections.json (Step 4 output).
                               Provides the selected ELR and/or frequency value.
        output_path:           Override output location. Defaults to
                               {stem}-initial-expected-ultimates.csv alongside the input CSV.

    Returns:
        ComputeIEUltimatesResult with output path, DataFrame, measure types, and warnings.

    Raises:
        FileNotFoundError: If any input file does not exist.
        ValueError:        If required columns or keys are missing.
    """
    ie_path  = Path(initial_expected_path).expanduser().resolve()
    sel_path = Path(ie_selections_path).expanduser().resolve()

    for p in (ie_path, sel_path):
        if not p.exists():
            raise FileNotFoundError(f"File not found: {p}")

    if output_path is None:
        dest = ie_path.with_name(f"{ie_path.stem}-ultimates.csv")
    else:
        dest = Path(output_path).expanduser().resolve()

    warn: list[str] = []

    # -----------------------------------------------------------------------
    # Load initial-expected CSV
    # -----------------------------------------------------------------------
    ie_df = pd.read_csv(ie_path)
    required_ie = {
        "measure_type", "origin_period",
        "exposure", "severity_trend", "frequency_trend", "exposure_trend",
    }
    missing_ie = required_ie - set(ie_df.columns)
    if missing_ie:
        raise ValueError(
            f"{ie_path} is missing required columns: {missing_ie}. "
            f"Found: {list(ie_df.columns)}"
        )
    ie_df["measure_type"]    = ie_df["measure_type"].astype(str)
    ie_df["origin_period"]   = ie_df["origin_period"].astype(str)
    ie_df["exposure"]        = pd.to_numeric(ie_df["exposure"],        errors="coerce")
    ie_df["severity_trend"]  = pd.to_numeric(ie_df["severity_trend"],  errors="coerce")
    ie_df["frequency_trend"] = pd.to_numeric(ie_df["frequency_trend"], errors="coerce")
    ie_df["exposure_trend"]  = pd.to_numeric(ie_df["exposure_trend"],  errors="coerce")

    available_measure_types = set(ie_df["measure_type"].unique())
    has_loss_ratio = "loss_ratio" in available_measure_types
    has_frequency  = "frequency"  in available_measure_types

    # Counts are present when frequency rows exist in the initial-expected output.
    # When counts are absent, the frequency_trend column holds the compounded
    # loss_ratio trend and severity_trend is 1.0 for every loss_ratio row.
    counts_present = has_frequency

    # -----------------------------------------------------------------------
    # Load IE selections JSON
    # -----------------------------------------------------------------------
    with open(sel_path, "r") as f:
        selections: dict = json.load(f)
    if not isinstance(selections, dict):
        raise ValueError(f"{sel_path} must be a JSON object keyed by measure type.")

    # Retrieve selected values
    elr_block  = selections.get("loss_ratio")
    freq_block = selections.get("frequency")

    selected_elr  = float(elr_block["selected_average"])  if elr_block  else None
    selected_freq = float(freq_block["selected_average"]) if freq_block else None

    if has_loss_ratio and selected_elr is None:
        raise ValueError(
            "loss_ratio rows found in initial-expected CSV but "
            "'loss_ratio' key is absent from selections JSON."
        )
    if has_frequency and selected_freq is None:
        raise ValueError(
            "frequency rows found in initial-expected CSV but "
            "'frequency' key is absent from selections JSON."
        )

    # -----------------------------------------------------------------------
    # Build output rows
    # -----------------------------------------------------------------------
    rows: list[dict] = []
    measure_types_seen: list[str] = []

    def _process_measure(measure_type: str, selected_value: float) -> None:
        mdf = ie_df[ie_df["measure_type"] == measure_type].copy()
        if mdf.empty:
            return

        all_origins = _sort_origin_periods(mdf["origin_period"].tolist())
        mdf = mdf.set_index("origin_period").reindex(all_origins)

        for origin_period in all_origins:
            row_data = mdf.loc[origin_period]
            exposure        = row_data["exposure"]
            sev_trend       = row_data["severity_trend"]
            freq_trend      = row_data["frequency_trend"]
            exp_trend       = row_data["exposure_trend"]

            # Skip if any required component is missing
            missing_fields = [
                name for name, val in [
                    ("exposure",       exposure),
                    ("frequency_trend", freq_trend),
                    ("exposure_trend",  exp_trend),
                ]
                if pd.isna(val)
            ]
            if missing_fields:
                warn.append(
                    f"{measure_type} | {origin_period}: missing {missing_fields}; "
                    "row skipped."
                )
                continue

            # For loss_ratio rows, severity_trend may be null when no counts are
            # present (stored as 1.0 in Step 2) — treat NaN safely as 1.0.
            if measure_type == "loss_ratio":
                sev_trend_val = 1.0 if pd.isna(sev_trend) else float(sev_trend)
            else:
                sev_trend_val = None  # not used for frequency rows

            # Compute initial expected ultimate
            if measure_type == "loss_ratio":
                numerator   = selected_value * float(exposure) * float(exp_trend)
                if counts_present:
                    denominator = sev_trend_val * float(freq_trend)
                else:
                    # When no counts: frequency_trend holds the compounded loss_ratio trend
                    denominator = float(freq_trend)

                if denominator == 0:
                    warn.append(
                        f"loss_ratio | {origin_period}: zero denominator "
                        "(severity_trend × frequency_trend); row skipped."
                    )
                    continue
                ie_ultimate = numerator / denominator

            else:  # frequency
                denominator = float(freq_trend)
                if denominator == 0:
                    warn.append(
                        f"frequency | {origin_period}: zero frequency_trend denominator; "
                        "row skipped."
                    )
                    continue
                ie_ultimate = selected_value * float(exposure) * float(exp_trend) / denominator

            rows.append({
                "measure_type":     measure_type,
                "origin_period":    origin_period,
                "selected_ie_value": selected_value,
                "exposure":         round(float(exposure), 2),
                "severity_trend":   round(sev_trend_val, 6) if sev_trend_val is not None else None,
                "frequency_trend":  round(float(freq_trend), 6),
                "exposure_trend":   round(float(exp_trend), 6),
                "ie_ultimate":      round(ie_ultimate, 2),
            })

        if any(r["measure_type"] == measure_type for r in rows):
            if measure_type not in measure_types_seen:
                measure_types_seen.append(measure_type)

    if has_loss_ratio:
        _process_measure("loss_ratio", selected_elr)
    if has_frequency:
        _process_measure("frequency", selected_freq)

    # -----------------------------------------------------------------------
    # Build and save output
    # -----------------------------------------------------------------------
    col_order = [
        "measure_type", "origin_period",
        "selected_ie_value",
        "exposure",
        "severity_trend", "frequency_trend", "exposure_trend",
        "ie_ultimate",
    ]
    if rows:
        out = pd.DataFrame(rows)[col_order]
        type_order = {"loss_ratio": 0, "frequency": 1}
        out["_type_ord"] = out["measure_type"].map(type_order).fillna(99)
        all_origins_global = _sort_origin_periods(out["origin_period"].unique().tolist())
        out["_origin_ord"] = out["origin_period"].map(
            {op: i for i, op in enumerate(all_origins_global)}
        )
        out = (
            out.sort_values(["_type_ord", "_origin_ord"])
            .drop(columns=["_type_ord", "_origin_ord"])
            .reset_index(drop=True)
        )
    else:
        out = pd.DataFrame(columns=col_order)

    out.to_csv(dest, index=False)

    return ComputeIEUltimatesResult(
        output_path=dest,
        ultimates_df=out,
        measure_types=measure_types_seen,
        warnings=warn,
    )
