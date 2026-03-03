"""
goal: Step 3 of reserving-analysis — compute actuarial diagnostics for all
      (origin_period, development_age) cells where the required measures are
      available, driven by pre-ultimate-diagnostics-registry.yaml.

Inputs:
    canonical_path  — {stem}-canonical.csv produced by extract-canonical Step 1
    metadata_path   — {stem}-canonical-metadata.json produced by extract-canonical Step 2
    registry_path   — pre-ultimate-diagnostics-registry.yaml (defaults to file alongside this script)

Available measures are read from the metadata JSON (`available_measures` field).
Only diagnostics whose required `inputs` are all present in available_measures are
computed; all others are silently skipped.

Recipes supported (same as the registry):
    safe_divide          — numerator / denominator (zero denominator → NaN)
    subtract             — left - right
    nested_divide        — (num_left - num_right) / (den_left - den_right)
    safe_divide_exposure — numerator / exposure (exposure is a per-origin Series)

For `safe_divide_exposure`, an `exposure` argument must be supplied as a
dict or pd.Series mapping origin_period → exposure value.  If exposure is
not provided, those diagnostics are skipped and listed in `skipped_diagnostics`.

Output columns (one row per diagnostic × origin_period × development_age):
    diagnostic_key    — registry key, e.g. "paid_to_incurred"
    label             — human-readable label from registry
    format            — display format hint: "integer", "percentage", "decimal"
    origin_period     — accident/origin period label
    age_to            — development age label ("to" age; same as development_age in the canonical)
    age_from          — predecessor development age for incremental diagnostics;
                        null for cumulative diagnostics and for the first development age
    value             — computed diagnostic value (NaN if inputs missing for that cell)

Rows are sorted by (diagnostic_key, origin_period, age_to).

Output file: {canonical_stem}-diagnostics.csv

This script contains no user interaction.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union

import numpy as np
import pandas as pd
import yaml


# ---------------------------------------------------------------------------
# Sort helpers (consistent with other steps)
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
class DiagnosticsResult:
    """Outcome of compute_diagnostics()."""
    output_path: Path               # path to saved CSV
    diagnostics_df: pd.DataFrame    # long-format diagnostics DataFrame
    computed_diagnostics: list[str] # registry keys that were computed
    skipped_diagnostics: list[dict] # list of {key, label, reason}
    available_measures: list[str]   # as read from metadata


# ---------------------------------------------------------------------------
# Registry helper
# ---------------------------------------------------------------------------

class _Registry:
    def __init__(self, registry_path: Path):
        with registry_path.open("r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        self._diagnostics: dict = cfg.get("diagnostics", {})

    def items(self):
        return self._diagnostics.items()

    def label(self, key: str) -> str:
        return self._diagnostics[key].get("label", key)

    def format(self, key: str) -> str:
        return self._diagnostics[key].get("format", "decimal")


# ---------------------------------------------------------------------------
# Pivot helpers
# ---------------------------------------------------------------------------

def _pivot(df: pd.DataFrame, measure: str) -> pd.DataFrame:
    """
    Return a wide DataFrame: index=origin_period, columns=development_age,
    values=value for the given measure.
    """
    sub = df[df["measure"] == measure].copy()
    return sub.pivot_table(
        index="origin_period",
        columns="development_age",
        values="value",
        aggfunc="first",
    )


def _incremental(wide: pd.DataFrame, sorted_dev_ages: list[str]) -> pd.DataFrame:
    """
    Convert a cumulative wide DataFrame to incremental by taking column-wise
    differences in development age order.  The first development age column
    is kept as-is (its incremental value equals its cumulative value).
    """
    ordered = [a for a in sorted_dev_ages if a in wide.columns]
    w = wide[ordered].copy()
    incr = w.diff(axis=1)
    incr[ordered[0]] = w[ordered[0]]
    return incr


def _wide_to_long(
    key: str,
    wide: pd.DataFrame,
    label: str,
    fmt: str,
    age_from_map: Optional[dict[str, Optional[str]]] = None,
) -> pd.DataFrame:
    """
    Melt a wide result DataFrame to long format.

    Args:
        age_from_map: Optional mapping of development_age → preceding age.
                      When provided (incremental diagnostics), an `age_from`
                      column is populated.  Pass None for cumulative diagnostics.
    """
    melted = wide.reset_index().melt(
        id_vars="origin_period",
        var_name="age_to",
        value_name="value",
    )
    melted["diagnostic_key"] = key
    melted["label"] = label
    melted["format"] = fmt
    if age_from_map is not None:
        melted["age_from"] = melted["age_to"].map(age_from_map)
    else:
        melted["age_from"] = None
    return melted[["diagnostic_key", "label", "format",
                   "origin_period", "age_to", "age_from", "value"]]


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

def compute_diagnostics(
    canonical_path: Union[str, Path],
    metadata_path: Union[str, Path],
    exposure: Optional[Union[dict, "pd.Series"]] = None,
    registry_path: Optional[Union[str, Path]] = None,
    output_path: Optional[Union[str, Path]] = None,
) -> DiagnosticsResult:
    """
    Compute actuarial diagnostics from a canonical long-format CSV.

    Args:
        canonical_path: Path to {stem}-canonical.csv.
        metadata_path:  Path to {stem}-canonical-metadata.json. Used to read
                        `available_measures` so only feasible diagnostics run.
        exposure:       Optional dict or pd.Series mapping origin_period →
                        exposure value. Required for `safe_divide_exposure`
                        diagnostics (e.g. loss rates, frequency).
        registry_path:  Path to pre-ultimate-diagnostics-registry.yaml. Defaults to the
                        file in the same directory as this script.
        output_path:    Override output location. Defaults to
                        {canonical_stem}-diagnostics.csv.

    Returns:
        DiagnosticsResult with output path, the diagnostics DataFrame,
        lists of computed and skipped diagnostics, and available measures.

    Raises:
        FileNotFoundError: If any required input file is not found.
        ValueError:        If required columns are missing.
    """
    # --- Resolve paths ---
    src = Path(canonical_path).expanduser().resolve()
    meta_src = Path(metadata_path).expanduser().resolve()
    if not src.exists():
        raise FileNotFoundError(f"Canonical file not found: {src}")
    if not meta_src.exists():
        raise FileNotFoundError(f"Metadata file not found: {meta_src}")

    if registry_path is None:
        reg_path = Path(__file__).parent / "pre-ultimate-diagnostics-registry.yaml"
    else:
        reg_path = Path(registry_path).expanduser().resolve()
    if not reg_path.exists():
        raise FileNotFoundError(f"Registry not found: {reg_path}")

    if output_path is None:
        dest = f"{src.parent}/pre-ultimate-diagnostics.csv"
    else:
        dest = Path(output_path).expanduser().resolve()

    # --- Load metadata → available measures ---
    meta = json.loads(meta_src.read_text(encoding="utf-8"))
    available_measures: list[str] = meta.get("available_measures", [])

    # --- Load canonical CSV ---
    df = pd.read_csv(src)
    required = {"origin_period", "development_age", "measure", "value"}
    missing_cols = required - set(df.columns)
    if missing_cols:
        raise ValueError(
            f"Canonical CSV is missing required columns: {missing_cols}. "
            f"Found: {list(df.columns)}"
        )
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["origin_period"] = df["origin_period"].astype(str)
    df["development_age"] = df["development_age"].astype(str)
    df["measure"] = df["measure"].astype(str)

    # Sorted development age order (for incremental calculations)
    all_dev_ages = df["development_age"].unique().tolist()
    sorted_dev_ages: list[str] = sorted(all_dev_ages, key=_sort_key)

    # Map each development age to its predecessor (None for the first age).
    # Used to populate age_from for incremental diagnostics.
    age_from_map: dict[str, Optional[str]] = {
        sorted_dev_ages[0]: None,
        **{sorted_dev_ages[i]: sorted_dev_ages[i - 1] for i in range(1, len(sorted_dev_ages))},
    }

    # --- Expose as per-measure pivot cache ---
    pivot_cache: dict[str, pd.DataFrame] = {}
    incr_cache: dict[str, pd.DataFrame] = {}

    def get_wide(measure: str, use_incremental: bool) -> pd.DataFrame:
        if measure not in pivot_cache:
            pivot_cache[measure] = _pivot(df, measure)
        wide = pivot_cache[measure]
        if use_incremental:
            if measure not in incr_cache:
                incr_cache[measure] = _incremental(wide, sorted_dev_ages)
            return incr_cache[measure]
        return wide

    # --- Normalise exposure to pd.Series indexed by origin_period ---
    exposure_series: Optional[pd.Series] = None
    if exposure is not None:
        if isinstance(exposure, dict):
            exposure_series = pd.Series(exposure, name="exposure")
        elif isinstance(exposure, pd.Series):
            exposure_series = exposure.copy()
        exposure_series.index = exposure_series.index.astype(str)

    # --- Registry ---
    registry = _Registry(reg_path)

    # Normalise available_measures to lowercase for matching
    avail_map = {m.lower(): m for m in available_measures}

    def resolve_measure(alias: str) -> Optional[str]:
        alias_l = alias.lower()
        # Exact match first
        if alias_l in avail_map:
            return avail_map[alias_l]
        # Prefix / contains match
        for m in available_measures:
            m_l = m.lower()
            if alias_l in m_l or m_l.startswith(alias_l):
                return m
        return None

    # Registry inputs use short aliases; map to actual canonical measure names
    # (handles cases like "paid" mapping to "paid_losses", etc.)
    def resolve_measure(alias: str) -> Optional[str]:
        alias_l = alias.lower()
        # Exact match first
        for m in available_measures:
            if m.lower() == alias_l:
                return m
        # Prefix / contains match
        for m in available_measures:
            if alias_l in m.lower() or m.lower().startswith(alias_l):
                return m
        return None

    long_parts: list[pd.DataFrame] = []
    computed: list[str] = []
    skipped: list[dict] = []

    for diag_key, spec in registry.items():
        lbl = spec.get("label", diag_key)
        fmt = spec.get("format", "decimal")
        recipe = spec["recipe"]
        args = spec.get("args", {})
        inputs_needed: list[str] = spec.get("inputs", [])

        # --- Check all required inputs are available ---
        resolved: dict[str, str] = {}
        missing_inputs = []
        for alias in inputs_needed:
            m = resolve_measure(alias)
            if m is None:
                missing_inputs.append(alias)
            else:
                resolved[alias] = m

        if missing_inputs:
            skipped.append({
                "key": diag_key,
                "label": lbl,
                "reason": f"missing measures: {missing_inputs}",
            })
            continue

        # --- Compute ---
        try:
            use_incr = args.get("use_incremental", False)

            if recipe == "safe_divide":
                num_wide = get_wide(resolved[args["numerator"]], use_incr)
                den_wide = get_wide(resolved[args["denominator"]], use_incr)
                # Align on shared index/columns
                num_a, den_a = num_wide.align(den_wide, join="inner")
                result_wide = num_a / den_a.replace(0, np.nan)

            elif recipe == "subtract":
                left_wide = get_wide(resolved[args["left"]], use_incr)
                right_wide = get_wide(resolved[args["right"]], use_incr)
                left_a, right_a = left_wide.align(right_wide, join="inner")
                result_wide = left_a - right_a

            elif recipe == "nested_divide":
                num_left = get_wide(resolved[args["numerator_args"]["left"]], False)
                num_right = get_wide(resolved[args["numerator_args"]["right"]], False)
                nl_a, nr_a = num_left.align(num_right, join="inner")
                numerator_wide = nl_a - nr_a

                den_left = get_wide(resolved[args["denominator_args"]["left"]], False)
                den_right = get_wide(resolved[args["denominator_args"]["right"]], False)
                dl_a, dr_a = den_left.align(den_right, join="inner")
                denominator_wide = dl_a - dr_a

                num_a, den_a = numerator_wide.align(denominator_wide, join="inner")
                result_wide = num_a / den_a.replace(0, np.nan)

            elif recipe == "safe_divide_exposure":
                if exposure_series is None:
                    skipped.append({
                        "key": diag_key,
                        "label": lbl,
                        "reason": "exposure not provided",
                    })
                    continue
                num_wide = get_wide(resolved[args["numerator"]], use_incr)
                # Divide each row by the matching exposure value
                result_wide = num_wide.divide(
                    exposure_series.reindex(num_wide.index), axis=0
                )

            else:
                skipped.append({
                    "key": diag_key,
                    "label": lbl,
                    "reason": f"unknown recipe '{recipe}'",
                })
                continue

        except Exception as exc:
            skipped.append({
                "key": diag_key,
                "label": lbl,
                "reason": f"computation error: {exc}",
            })
            continue

        long_parts.append(_wide_to_long(
            diag_key, result_wide, lbl, fmt,
            age_from_map=age_from_map if use_incr else None,
        ))
        computed.append(diag_key)

    # --- Assemble output ---
    if long_parts:
        out = pd.concat(long_parts, ignore_index=True)
        out["value"] = pd.to_numeric(out["value"], errors="coerce")

        # Sort: (diagnostic_key by registry order, age_to, origin_period)
        diag_order = {k: i for i, k in enumerate(registry._diagnostics)}
        origin_order = {
            op: i
            for i, op in enumerate(
                sorted(df["origin_period"].unique().tolist(), key=_sort_key)
            )
        }
        dev_order = {a: i for i, a in enumerate(sorted_dev_ages)}

        out["_d_rank"] = out["diagnostic_key"].map(lambda k: diag_order.get(k, 999))
        out["_a_rank"] = out["age_to"].map(lambda a: dev_order.get(a, 999))
        out["_o_rank"] = out["origin_period"].map(origin_order)
        out = (
            out
            .sort_values(["_d_rank", "_a_rank", "_o_rank"])
            .drop(columns=["_d_rank", "_o_rank", "_a_rank"])
            .reset_index(drop=True)
        )
    else:
        out = pd.DataFrame(
            columns=["diagnostic_key", "label", "format",
                     "origin_period", "age_to", "age_from", "value"]
        )

    out.to_csv(dest, index=False)

    return DiagnosticsResult(
        output_path=dest,
        diagnostics_df=out,
        computed_diagnostics=computed,
        skipped_diagnostics=skipped,
        available_measures=available_measures,
    )
