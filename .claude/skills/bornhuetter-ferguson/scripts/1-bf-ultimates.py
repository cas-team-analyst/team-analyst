"""
goal: Step 1 of bornhuetter-ferguson — compute Bornhuetter-Ferguson (BF) ultimate
      losses (and optionally counts) for each origin period by combining:
        - the cumulative development factor (CDF) from the chain-ladder ultimates CSV
        - the initial expected ultimate from the initial-expected ultimates CSV
        - the current diagonal value from the chain-ladder ultimates CSV

Formula
-------
    bf_ultimate = ie_ultimate * (1 - 1 / cdf) + current_value

Where:
    ie_ultimate   — initial expected ultimate for that measure / origin period
    cdf           — cumulative development factor to ultimate (from chain-ladder)
    current_value — latest diagonal value for that measure / origin period

Measures handled (any subset may be present):
    paid_losses, incurred_losses, reported_counts, closed_counts

The BF measure name mirrors the chain-ladder measure name.  The corresponding IE
measure type is determined by the mapping:
    paid_losses | incurred_losses  →  "loss_ratio" IE measure type
    reported_counts | closed_counts →  "frequency" IE measure type

inputs:
    cl_ultimates_path   — path to {stem}-chain-ladder-ultimates.csv  (chain-ladder Step 1)
                          columns: measure, origin_period, latest_age, current_value, cdf, ultimate
    ie_ultimates_path   — path to {stem}-initial-expected-ultimates.csv (initial-expected Step 5)
                          columns: measure_type, origin_period, ie_ultimate, …

output columns:
    measure             — chain-ladder measure name (e.g. "paid_losses")
    origin_period       — accident / origin period label
    ie_ultimate         — initial expected ultimate for this measure / origin period
    current_value       — latest diagonal value (from chain-ladder)
    cdf                 — cumulative development factor (from chain-ladder)
    percent_undeveloped  — 1 - 1/cdf  (the "undeveloped" weight applied to IE)
    bf_ultimate         — computed BF ultimate

Output file: {stem}-bf-ultimates.csv saved alongside the chain-ladder ultimates CSV.
  e.g.  trip-canonical-chain-ladder-ultimates.csv
     →  trip-canonical-bf-ultimates.csv

"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import pandas as pd


# ---------------------------------------------------------------------------
# Constants — mapping from CL measure name to IE measure_type
# ---------------------------------------------------------------------------

# Loss measures map to the "loss_ratio" IE measure type
_LOSS_MEASURES: set[str] = {"paid_losses", "incurred_losses"}
# Count measures map to the "frequency" IE measure type
_COUNT_MEASURES: set[str] = {"reported_counts", "closed_counts"}


def _ie_measure_type(cl_measure: str) -> str:
    """Return the IE measure_type that corresponds to a given CL measure name."""
    cl = cl_measure.lower().strip()
    if cl in _LOSS_MEASURES:
        return "loss_ratio"
    if cl in _COUNT_MEASURES:
        return "frequency"
    # Fallback heuristic: names containing "count" → frequency, else → loss_ratio
    if "count" in cl:
        return "frequency"
    return "loss_ratio"


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class ComputeBFUltimatesResult:
    """Outcome of compute_bf_ultimates()."""
    output_path: Path                  # path to the saved BF ultimates CSV
    ultimates_df: pd.DataFrame         # the output DataFrame (in memory)
    measures: list[str]                # CL measure names included in output
    warnings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

def compute_bf_ultimates(
    cl_ultimates_path: str | Path,
    ie_ultimates_path: str | Path,
    output_path: Optional[str | Path] = None,
) -> ComputeBFUltimatesResult:
    """
    Compute Bornhuetter-Ferguson ultimates for each measure / origin period.

    Args:
        cl_ultimates_path: Path to {stem}-chain-ladder-ultimates.csv (chain-ladder Step 1).
                           Must contain: measure, origin_period, current_value, cdf.
        ie_ultimates_path: Path to {stem}-initial-expected-ultimates.csv
                           (initial-expected Step 5).
                           Must contain: measure_type, origin_period, ie_ultimate.
        output_path:       Override output location.  Defaults to
                           {stem}-bf-ultimates.csv alongside the chain-ladder ultimates CSV.

    Returns:
        ComputeBFUltimatesResult with output path, DataFrame, measure list, and warnings.

    Raises:
        FileNotFoundError: If either input file does not exist.
        ValueError:        If required columns are missing.
    """
    cl_path = Path(cl_ultimates_path).expanduser().resolve()
    ie_path = Path(ie_ultimates_path).expanduser().resolve()

    for p in (cl_path, ie_path):
        if not p.exists():
            raise FileNotFoundError(f"File not found: {p}")

    # Derive output path from the CL ultimates file:
    #   trip-canonical-chain-ladder-ultimates.csv → trip-canonical-bf-ultimates.csv
    if output_path is None:
        stem = cl_path.stem  # e.g. "trip-canonical-chain-ladder-ultimates"
        if stem.endswith("-chain-ladder-ultimates"):
            base = stem[: -len("-chain-ladder-ultimates")]
        else:
            base = stem
        dest = cl_path.with_name(f"{base}-bf-ultimates.csv")
    else:
        dest = Path(output_path).expanduser().resolve()

    warn: list[str] = []

    # -----------------------------------------------------------------------
    # Load chain-ladder ultimates
    # -----------------------------------------------------------------------
    cl_df = pd.read_csv(cl_path)
    required_cl = {"measure", "origin_period", "current_value", "cdf"}
    missing_cl = required_cl - set(cl_df.columns)
    if missing_cl:
        raise ValueError(
            f"{cl_path} is missing required columns: {missing_cl}. "
            f"Found: {list(cl_df.columns)}"
        )
    cl_df["measure"]       = cl_df["measure"].astype(str)
    cl_df["origin_period"] = cl_df["origin_period"].astype(str)
    cl_df["current_value"] = pd.to_numeric(cl_df["current_value"], errors="coerce")
    cl_df["cdf"]           = pd.to_numeric(cl_df["cdf"],           errors="coerce")

    # -----------------------------------------------------------------------
    # Load initial-expected ultimates
    # -----------------------------------------------------------------------
    ie_df = pd.read_csv(ie_path)
    required_ie = {"measure_type", "origin_period", "ie_ultimate"}
    missing_ie = required_ie - set(ie_df.columns)
    if missing_ie:
        raise ValueError(
            f"{ie_path} is missing required columns: {missing_ie}. "
            f"Found: {list(ie_df.columns)}"
        )
    ie_df["measure_type"]  = ie_df["measure_type"].astype(str)
    ie_df["origin_period"] = ie_df["origin_period"].astype(str)
    ie_df["ie_ultimate"]   = pd.to_numeric(ie_df["ie_ultimate"], errors="coerce")

    # Build a lookup: (ie_measure_type, origin_period) → ie_ultimate
    ie_lookup: dict[tuple[str, str], float] = {}
    for _, row in ie_df.iterrows():
        key = (row["measure_type"], row["origin_period"])
        ie_lookup[key] = row["ie_ultimate"]

    available_ie_types = set(ie_df["measure_type"].unique())

    # -----------------------------------------------------------------------
    # Compute BF ultimates row by row
    # -----------------------------------------------------------------------
    rows: list[dict] = []
    measures_seen: list[str] = []

    for _, cl_row in cl_df.iterrows():
        measure       = cl_row["measure"]
        origin_period = cl_row["origin_period"]
        current_value = cl_row["current_value"]
        cdf           = cl_row["cdf"]

        # Determine which IE measure type to use for this CL measure
        ie_type = _ie_measure_type(measure)

        if ie_type not in available_ie_types:
            warn.append(
                f"Measure '{measure}' maps to IE type '{ie_type}', which is not present "
                f"in {ie_path.name}. Row skipped."
            )
            continue

        ie_ult = ie_lookup.get((ie_type, origin_period))
        if ie_ult is None:
            warn.append(
                f"No IE ultimate found for IE type '{ie_type}', origin '{origin_period}' "
                f"(needed for CL measure '{measure}'). Row skipped."
            )
            continue

        if pd.isna(current_value):
            warn.append(
                f"Missing current_value for measure '{measure}', origin '{origin_period}'. "
                "Row skipped."
            )
            continue

        if pd.isna(cdf) or cdf == 0:
            warn.append(
                f"Invalid CDF ({cdf!r}) for measure '{measure}', origin '{origin_period}'. "
                "Row skipped."
            )
            continue

        percent_unreported = 1.0 - 1.0 / cdf
        bf_ultimate = ie_ult * percent_unreported + current_value

        rows.append({
            "measure":             measure,
            "origin_period":       origin_period,
            "ie_ultimate":         round(float(ie_ult), 2),
            "current_value":       round(float(current_value), 2),
            "cdf":                 round(float(cdf), 3),
            "percent_unreported":  round(percent_unreported, 6),
            "bf_ultimate":         round(bf_ultimate, 2),
        })

        if measure not in measures_seen:
            measures_seen.append(measure)

    # -----------------------------------------------------------------------
    # Build and save output
    # -----------------------------------------------------------------------
    col_order = [
        "measure", "origin_period",
        "ie_ultimate", "current_value",
        "cdf", "percent_unreported",
        "bf_ultimate",
    ]
    if rows:
        out = pd.DataFrame(rows)[col_order]
        # Preserve the original measure order from the CL file, then sort by origin
        measure_order = {m: i for i, m in enumerate(cl_df["measure"].unique())}
        out["_measure_ord"] = out["measure"].map(measure_order).fillna(999)
        # Sort origin periods chronologically within each measure
        all_origins = out["origin_period"].unique().tolist()

        def _origin_key(lbl: str) -> tuple:
            try:
                return (0, pd.to_datetime(lbl, infer_datetime_format=True).timestamp())
            except Exception:
                pass
            try:
                return (1, float(str(lbl).replace("Q", ".").replace("-", "")))
            except Exception:
                pass
            return (2, lbl)

        origin_order = {op: i for i, op in enumerate(sorted(all_origins, key=_origin_key))}
        out["_origin_ord"] = out["origin_period"].map(origin_order).fillna(999)
        out = (
            out.sort_values(["_measure_ord", "_origin_ord"])
            .drop(columns=["_measure_ord", "_origin_ord"])
            .reset_index(drop=True)
        )
    else:
        out = pd.DataFrame(columns=col_order)

    out.to_csv(dest, index=False)

    return ComputeBFUltimatesResult(
        output_path=dest,
        ultimates_df=out,
        measures=measures_seen,
        warnings=warn,
    )
