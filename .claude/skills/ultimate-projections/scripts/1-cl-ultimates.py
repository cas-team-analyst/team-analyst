"""
goal: Step 2 of ultimate-projections — project chain ladder method ultimate losses by applying the
      selected LDFs and tail factor from ldf-selections.json to the latest diagonal
      of each measure from the diagonal CSV produced by extract-canonical Step 3.

inputs:
    ldf_selections_path  — path to {stem}-ldf-selections.json produced by Step 1
    diagonal_path        — path to {stem}-canonical-diagonal.csv produced by extract-canonical Step 3

output columns:
    measure            — triangle / measure name
    origin_period      — accident / origin period label
    latest_age         — development age from the diagonal
    current_value      — projected-from value (diagonal value for this measure)
    cdf                — cumulative development factor from latest_age to ultimate
    ultimate           — current_value * cdf

Output file: {ldf_selections_stem}-ultimates.csv saved alongside ldf-selections.json.
  e.g.  trip-canonical-ldf-selections.json
     →  trip-canonical-ldf-selections-ultimates.csv

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
class ProjectCLUltimatesResult:
    """Outcome of project_ultimates()."""
    output_path: Path           # path to the saved ultimates CSV
    ultimates_df: pd.DataFrame  # the ultimates DataFrame (in memory)
    measures: list[str]         # measures present in the output
    warnings: list[str] = field(default_factory=list)


def _calculate_cdfs(intervals: list[dict], tail_factor: float) -> dict[str, float]:
    """
    Calculate CDFs from the interval list in ldf-selections.json.

    Args:
        intervals: list of {"age_from": str, "age_to": str, "selected_ldf": float, ...}
        tail_factor: tail factor to apply beyond the last development age

    Returns:
        dict mapping age_from (str) → CDF to ultimate, plus age_to of the
        last interval → tail_factor.
    """
    if not intervals:
        return {}

    # Sorted by age_from numerically, falling back to lexicographic
    def _age_key(iv: dict) -> float:
        try:
            return float(iv["age_from"])
        except (ValueError, TypeError):
            return 0.0

    sorted_ivs = sorted(intervals, key=_age_key)

    # The CDF at the last interval's age_from = selected_ldf * tail_factor
    # Then work backwards: CDF[age_from[i]] = ldf[i] * CDF[age_from[i+1]]
    cdfs: dict[str, float] = {}
    n = len(sorted_ivs)

    # CDF for the last age_to (beyond all intervals) = tail_factor
    last_age_to = str(sorted_ivs[-1]["age_to"])
    cdfs[last_age_to] = tail_factor

    # Fill backwards
    for iv in reversed(sorted_ivs):
        age_from = str(iv["age_from"])
        age_to = str(iv["age_to"])
        ldf = float(iv["selected_ldf"])
        cdf_next = cdfs[age_to]
        cdfs[age_from] = round(ldf * cdf_next, 3)

    return cdfs


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

def project_cl_ultimates(
    ldf_selections_path: str | Path,
    diagonal_path: str | Path,
    output_path: Optional[str | Path] = None,
) -> ProjectCLUltimatesResult:
    """
    Project ultimate losses from ldf-selections.json and the diagonal CSV.

    Args:
        ldf_selections_path: Path to {stem}-ldf-selections.json (Step 1 output).
        diagonal_path:       Path to {stem}-canonical-diagonal.csv (extract-canonical Step 3 output).
        output_path:         Override output location. Defaults to
                             {ldf_selections_stem}-ultimates.csv alongside the JSON.

    Returns:
        ProjectUltimatesResult with output path, ultimates DataFrame, and metadata.

    Raises:
        FileNotFoundError: If either input file does not exist.
        ValueError:        If required columns are missing or the JSON is malformed.
    """
    sel_path = Path(ldf_selections_path).expanduser().resolve()
    diag_path = Path(diagonal_path).expanduser().resolve()

    if not sel_path.exists():
        raise FileNotFoundError(f"LDF selections file not found: {sel_path}")
    if not diag_path.exists():
        raise FileNotFoundError(f"Diagonal CSV not found: {diag_path}")

    if output_path is None:
        dest = sel_path.with_name(f"{sel_path.stem}-ultimates.csv")
    else:
        dest = Path(output_path).expanduser().resolve()

    # --- Load selections JSON ---
    with open(sel_path, "r") as f:
        selections: dict = json.load(f)

    if not isinstance(selections, dict):
        raise ValueError(f"{sel_path} must be a JSON object keyed by measure name.")

    # --- Load diagonal CSV ---
    diag_df = pd.read_csv(diag_path)
    required_cols = {"measure", "origin_period", "development_age", "value"}
    missing = required_cols - set(diag_df.columns)
    if missing:
        raise ValueError(
            f"{diag_path} is missing required columns: {missing}. "
            f"Found: {list(diag_df.columns)}"
        )
    diag_df["value"] = pd.to_numeric(diag_df["value"], errors="coerce")
    diag_df["measure"] = diag_df["measure"].astype(str)
    diag_df["origin_period"] = diag_df["origin_period"].astype(str)
    diag_df["development_age"] = diag_df["development_age"].astype(str)

    diagonal = diag_df

    warnings: list[str] = []
    rows: list[dict] = []
    measures_seen: list[str] = []

    for measure, measure_sel in selections.items():
        if not isinstance(measure_sel, dict):
            warnings.append(f"Skipping measure '{measure}': value is not an object.")
            continue

        intervals = measure_sel.get("intervals", [])
        tail_block = measure_sel.get("tail", {})
        tail_factor = float(tail_block.get("selected_ldf", 1.0))

        if not intervals:
            warnings.append(f"Skipping measure '{measure}': no intervals defined.")
            continue

        cdfs = _calculate_cdfs(intervals, tail_factor)

        measure_diag = diagonal[diagonal["measure"] == measure]
        if measure_diag.empty:
            warnings.append(
                f"No canonical data found for measure '{measure}'; skipping."
            )
            continue

        measures_seen.append(measure)

        for _, row in measure_diag.iterrows():
            origin_period = row["origin_period"]
            latest_age = str(row["development_age"])
            current_value = float(row["value"])

            if latest_age not in cdfs:
                warnings.append(
                    f"No CDF available for measure '{measure}', origin '{origin_period}', "
                    f"age {latest_age}. Skipping row."
                )
                continue

            cdf = cdfs[latest_age]
            ultimate = round(current_value * cdf, 2)

            rows.append({
                "measure": measure,
                "origin_period": origin_period,
                "latest_age": latest_age,
                "current_value": round(current_value, 2),
                "cdf": round(cdf, 3),
                "ultimate": ultimate,
            })

    if rows:
        out = pd.DataFrame(rows)
    else:
        out = pd.DataFrame(
            columns=["measure", "origin_period", "latest_age",
                     "current_value", "cdf", "ultimate"]
        )

    out.to_csv(dest, index=False)

    return ProjectCLUltimatesResult(
        output_path=dest,
        ultimates_df=out,
        measures=measures_seen,
        warnings=warnings,
    )
