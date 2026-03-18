"""
goal: Step 2 of project-ultimates — read all available method ultimate files and assemble
      a structured JSON object grouping projections by loss/count category and method.

For each method × measure, the output includes:
    file_path       — absolute path to the source ultimates CSV
    origin_periods  — dict keyed by origin period label, each containing:
        current_value   — latest diagonal value (paid, incurred, reported, or closed)
        ultimate        — projected ultimate
        ibnr            — ultimate - incurred (or reported for counts); null if measure unavailable
        unpaid          — ultimate - paid (or closed for counts); null if measure unavailable

inputs:
    cl_ultimates_path   — path to {stem}-chain-ladder-ultimates.csv  (required; anchor for diagonals)
    ie_ultimates_path   — path to {stem}-initial-expected-ultimates.csv  (optional)
    bf_ultimates_path   — path to {stem}-bf-ultimates.csv  (optional)

output:
    {stem}-method-ultimates.json  saved alongside the chain-ladder ultimates CSV.

JSON structure:
{
  "losses": {
    "paid_losses_chain_ladder": {
      "file_path": "...",
      "origin_periods": {
        "AY 2019": {"current_value": 1000.00, "ultimate": 1200.00, "ibnr": null, "unpaid": 200.00},
        ...
      }
    },
    ...
  },
  "counts": {
    "reported_counts_chain_ladder": { ... },
    ...
  }
}

Notes:
- IBNR  = ultimate - incurred_losses (or reported_counts).  Null when that companion is absent.
- Unpaid = ultimate - paid_losses (or closed_counts).  Null when that companion is absent.
- For initial-expected: current_value is sourced from the chain-ladder diagonal (same measure);
  ie_ultimate is the projected ultimate for that measure type and origin period.
- All monetary values rounded to 2 decimal places.

"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import pandas as pd


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_LOSS_MEASURES = {"paid_losses", "incurred_losses"}
_COUNT_MEASURES = {"reported_counts", "closed_counts"}

# IE measure_type → which CL measures share that type
_IE_TYPE_TO_MEASURES: dict[str, list[str]] = {
    "loss_ratio": ["paid_losses", "incurred_losses"],
    "frequency":  ["reported_counts", "closed_counts"],
}

# For each measure, which other measure is its IBNR companion (incurred/reported)
# and which is its unpaid companion (paid/closed)
_IBNR_COMPANION = {
    "paid_losses":      "incurred_losses",
    "incurred_losses":  "incurred_losses",
    "reported_counts":  "reported_counts",
    "closed_counts":    "reported_counts",
}
_UNPAID_COMPANION = {
    "paid_losses":      "paid_losses",
    "incurred_losses":  "paid_losses",
    "reported_counts":  "closed_counts",
    "closed_counts":    "closed_counts",
}


def _is_loss(measure: str) -> bool:
    m = measure.lower()
    return "count" not in m


def _pretty_method(method_key: str) -> str:
    """Return a display-friendly method key, e.g. 'chain_ladder'."""
    return method_key


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class AssembleUltimatesResult:
    """Outcome of assemble_method_ultimates()."""
    output_path: Path                  # path to the saved JSON
    data: dict                         # the assembled dict (mirrors saved JSON)
    warnings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_cl(cl_path: Path) -> tuple[pd.DataFrame, list[str]]:
    """Load chain-ladder ultimates CSV. Returns (df, warnings)."""
    df = pd.read_csv(cl_path)
    required = {"measure", "origin_period", "current_value", "ultimate"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"{cl_path.name} is missing required columns: {missing}. "
            f"Found: {list(df.columns)}"
        )
    df["measure"]       = df["measure"].astype(str)
    df["origin_period"] = df["origin_period"].astype(str)
    df["current_value"] = pd.to_numeric(df["current_value"], errors="coerce")
    df["ultimate"]      = pd.to_numeric(df["ultimate"],      errors="coerce")
    return df, []


def _load_ie(ie_path: Path, cl_df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Load initial-expected ultimates CSV and join back diagonal current_values
    from the chain-ladder file (keyed by measure type).

    Returns a DataFrame with columns:
        measure, origin_period, current_value, ultimate (= ie_ultimate)
    """
    warn: list[str] = []
    ie_df = pd.read_csv(ie_path)

    required = {"measure_type", "origin_period", "ie_ultimate"}
    missing = required - set(ie_df.columns)
    if missing:
        raise ValueError(
            f"{ie_path.name} is missing required columns: {missing}. "
            f"Found: {list(ie_df.columns)}"
        )
    ie_df["measure_type"]  = ie_df["measure_type"].astype(str)
    ie_df["origin_period"] = ie_df["origin_period"].astype(str)
    ie_df["ie_ultimate"]   = pd.to_numeric(ie_df["ie_ultimate"], errors="coerce")

    # Build diagonal lookup from CL: (measure, origin_period) → current_value
    cl_diag: dict[tuple[str, str], float] = {}
    for _, row in cl_df.iterrows():
        cl_diag[(row["measure"], row["origin_period"])] = row["current_value"]

    rows: list[dict] = []
    for _, row in ie_df.iterrows():
        ie_type      = row["measure_type"]
        origin       = row["origin_period"]
        ie_ultimate  = row["ie_ultimate"]

        # Expand each IE row into one row per CL measure sharing that type
        cl_measures = _IE_TYPE_TO_MEASURES.get(ie_type, [])
        for cl_measure in cl_measures:
            # Only emit a row if this CL measure actually exists in the CL file
            if cl_measure not in cl_df["measure"].values:
                continue
            current_value = cl_diag.get((cl_measure, origin))
            if current_value is None:
                warn.append(
                    f"IE: No diagonal value for measure '{cl_measure}', "
                    f"origin '{origin}'. Using null."
                )
            rows.append({
                "measure":       cl_measure,
                "origin_period": origin,
                "current_value": current_value,
                "ultimate":      float(ie_ultimate) if pd.notna(ie_ultimate) else None,
            })

    if not rows:
        return pd.DataFrame(columns=["measure","origin_period","current_value","ultimate"]), warn

    return pd.DataFrame(rows), warn


def _load_bf(bf_path: Path) -> tuple[pd.DataFrame, list[str]]:
    """Load BF ultimates CSV. Returns (df, warnings)."""
    df = pd.read_csv(bf_path)
    required = {"measure", "origin_period", "current_value", "bf_ultimate"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"{bf_path.name} is missing required columns: {missing}. "
            f"Found: {list(df.columns)}"
        )
    df["measure"]       = df["measure"].astype(str)
    df["origin_period"] = df["origin_period"].astype(str)
    df["current_value"] = pd.to_numeric(df["current_value"], errors="coerce")
    df["bf_ultimate"]   = pd.to_numeric(df["bf_ultimate"],   errors="coerce")
    df = df.rename(columns={"bf_ultimate": "ultimate"})
    return df, []


def _build_diagonal_lookup(cl_df: pd.DataFrame) -> dict[tuple[str, str], float]:
    """Build (measure, origin_period) → current_value from the chain-ladder diagonal."""
    return {
        (str(r["measure"]), str(r["origin_period"])): float(r["current_value"])
        for _, r in cl_df.iterrows()
        if pd.notna(r["current_value"])
    }


def _method_block(
    method_df: pd.DataFrame,
    measure: str,
    file_path: Path,
    diagonal: dict[tuple[str, str], float],
) -> dict:
    """
    Build the per-method JSON block for a single measure.

    Args:
        method_df:  DataFrame with columns measure, origin_period, current_value, ultimate.
        measure:    The measure name (e.g. 'paid_losses').
        file_path:  Source CSV path, included in output.
        diagonal:   Full CL diagonal lookup for companion IBNR/unpaid values.
    """
    subset = method_df[method_df["measure"] == measure].copy()

    ibnr_measure   = _IBNR_COMPANION.get(measure)
    unpaid_measure = _UNPAID_COMPANION.get(measure)

    origin_dict: dict[str, dict] = {}
    for _, row in subset.iterrows():
        origin   = row["origin_period"]
        curr_val = float(row["current_value"]) if pd.notna(row["current_value"]) else None
        ultimate = float(row["ultimate"])      if pd.notna(row["ultimate"])      else None

        # IBNR = ultimate - incurred (or reported for counts)
        if ibnr_measure and ultimate is not None:
            companion_val = diagonal.get((ibnr_measure, origin))
            ibnr = round(ultimate - companion_val, 2) if companion_val is not None else None
        else:
            ibnr = None

        # Unpaid = ultimate - paid (or closed for counts)
        if unpaid_measure and ultimate is not None:
            companion_val = diagonal.get((unpaid_measure, origin))
            unpaid = round(ultimate - companion_val, 2) if companion_val is not None else None
        else:
            unpaid = None

        origin_dict[origin] = {
            "current_value": round(curr_val, 2) if curr_val is not None else None,
            "ultimate":      round(ultimate, 2) if ultimate is not None else None,
            "ibnr":          ibnr,
            "unpaid":        unpaid,
        }

    return {
        "file_path":      str(file_path),
        "origin_periods": origin_dict,
    }


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

def assemble_method_ultimates(
    cl_ultimates_path: str | Path,
    ie_ultimates_path: Optional[str | Path] = None,
    bf_ultimates_path: Optional[str | Path] = None,
    output_path: Optional[str | Path] = None,
) -> AssembleUltimatesResult:
    """
    Assemble a structured JSON of all available method ultimates.

    Args:
        cl_ultimates_path:  Path to {stem}-chain-ladder-ultimates.csv (required).
        ie_ultimates_path:  Path to {stem}-initial-expected-ultimates.csv (optional).
        bf_ultimates_path:  Path to {stem}-bf-ultimates.csv (optional).
        output_path:        Override output location. Defaults to
                            {stem}-method-ultimates.json alongside the CL ultimates CSV.

    Returns:
        AssembleUltimatesResult with output path, assembled data dict, and warnings.

    Raises:
        FileNotFoundError: If cl_ultimates_path does not exist.
        ValueError:        If required columns are missing from any input file.
    """
    cl_path = Path(cl_ultimates_path).expanduser().resolve()
    if not cl_path.exists():
        raise FileNotFoundError(f"Chain-ladder ultimates file not found: {cl_path}")

    warn: list[str] = []

    # Derive output path
    if output_path is None:
        stem = cl_path.stem  # e.g. "trip-canonical-chain-ladder-ultimates"
        if stem.endswith("-chain-ladder-ultimates"):
            base = stem[: -len("-chain-ladder-ultimates")]
        else:
            base = stem
        dest = cl_path.with_name(f"{base}-method-ultimates.json")
    else:
        dest = Path(output_path).expanduser().resolve()

    # -----------------------------------------------------------------------
    # Load inputs
    # -----------------------------------------------------------------------
    cl_df, cl_warn = _load_cl(cl_path)
    warn.extend(cl_warn)

    diagonal = _build_diagonal_lookup(cl_df)

    # Available methods: (method_key, df, file_path)
    methods: list[tuple[str, pd.DataFrame, Path]] = [
        ("chain_ladder", cl_df, cl_path),
    ]

    if ie_ultimates_path is not None:
        ie_path = Path(ie_ultimates_path).expanduser().resolve()
        if not ie_path.exists():
            warn.append(f"Initial-expected ultimates file not found: {ie_path}. Skipping.")
        else:
            ie_df, ie_warn = _load_ie(ie_path, cl_df)
            warn.extend(ie_warn)
            methods.append(("initial_expected", ie_df, ie_path))

    if bf_ultimates_path is not None:
        bf_path = Path(bf_ultimates_path).expanduser().resolve()
        if not bf_path.exists():
            warn.append(f"BF ultimates file not found: {bf_path}. Skipping.")
        else:
            bf_df, bf_warn = _load_bf(bf_path)
            warn.extend(bf_warn)
            methods.append(("bornhuetter_ferguson", bf_df, bf_path))

    # -----------------------------------------------------------------------
    # Assemble output structure
    # -----------------------------------------------------------------------
    result: dict = {"losses": {}, "counts": {}}

    all_measures: list[str] = list(cl_df["measure"].unique())

    for method_key, method_df, method_path in methods:
        # Determine which measures are present in this method's file
        method_measures = [m for m in all_measures if m in method_df["measure"].values]

        for measure in method_measures:
            category = "losses" if _is_loss(measure) else "counts"
            entry_key = f"{measure}_{method_key}"

            block = _method_block(method_df, measure, method_path, diagonal)
            result[category][entry_key] = block

    # Remove empty top-level categories
    result = {k: v for k, v in result.items() if v}

    # -----------------------------------------------------------------------
    # Save
    # -----------------------------------------------------------------------
    with open(dest, "w") as f:
        json.dump(result, f, indent=2)

    return AssembleUltimatesResult(
        output_path=dest,
        data=result,
        warnings=warn,
    )
