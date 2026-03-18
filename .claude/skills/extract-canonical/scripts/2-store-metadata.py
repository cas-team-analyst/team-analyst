"""
goal: Step 2 of extract-canonical — read the canonical long-format CSV produced
      by Step 1 and store structured metadata to a companion JSON file.

Metadata is split into two categories:

  Data-derived (computed automatically from the canonical CSV):
    origin_period_start       — earliest origin period label
    origin_period_end         — latest origin period label
    origin_period_count       — number of distinct origin periods
    origin_period_interval    — inferred interval ("annual", "quarterly",
                                "semi-annual", "biennial", or "irregular")
    origin_periods            — full sorted list of origin period labels
    development_age_start     — earliest development age label
    development_age_end       — latest development age label
    development_age_count     — number of distinct development ages
    development_age_interval  — inferred interval between dev ages (same labels as origin)
    development_ages          — full sorted list
    available_measures        — list of distinct measure values found in CSV
    total_populated_cells     — total non-null (origin, dev_age, measure) rows
    per_measure_stats         — {measure: {count, min, max, mean, total}}
    valuation_date_check      — whether the user-supplied valuation_date is
                                consistent with the data's latest periods
    source_canonical_path     — absolute path to the canonical CSV
    created_at                — ISO 8601 UTC timestamp of metadata creation

  User-supplied (passed in by the agent after gathering from the user):
    loss_currency             — e.g. "USD", "GBP"
    valuation_date            — e.g. "2024-12-31"
    line_of_business          — e.g. "Workers Compensation"
    specific_coverage         — e.g. "Medical Only" or null
    data_source_format        — "triangle" or "loss_run"
    notes                     — optional free-text notes from the user

Output file: {canonical_stem}-metadata.json
  e.g.  C:/data/triangles-canonical.csv
     →  C:/data/triangles-canonical-metadata.json

"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional

import pandas as pd


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

DataSourceFormat = Literal["triangle", "loss_run"]

_INTERVAL_MONTHS: dict[str, float] = {
    "annual":      12.0,
    "semi-annual":  6.0,
    "quarterly":    3.0,
    "biennial":    24.0,
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _try_parse_numeric(label: str) -> Optional[float]:
    """Extract a leading/trailing integer or float from a period label."""
    import re
    m = re.search(r"(\d+(?:\.\d+)?)", str(label))
    return float(m.group(1)) if m else None


def _try_parse_date(label: str) -> Optional[pd.Timestamp]:
    """Attempt to parse a label as a date. Returns None on failure."""
    try:
        return pd.to_datetime(label, infer_datetime_format=True)
    except Exception:
        return None


def _sort_key(label: str):
    """Unified sort key: prefer date, then numeric, then string."""
    dt = _try_parse_date(label)
    if dt is not None:
        return (0, dt.timestamp(), "")
    num = _try_parse_numeric(label)
    if num is not None:
        return (1, num, "")
    return (2, 0.0, label)


def _infer_interval(sorted_labels: list[str]) -> str:
    """
    Infer the period interval from a sorted list of labels.
    Attempts date-based intervals first, then numeric-based.
    Returns one of: "annual", "semi-annual", "quarterly", "biennial",
                    "monthly", "irregular", or "indeterminate".
    """
    if len(sorted_labels) < 2:
        return "indeterminate"

    # --- Try date-based intervals ---
    dates = [_try_parse_date(v) for v in sorted_labels]
    if all(d is not None for d in dates):
        deltas_months = [
            (dates[i + 1] - dates[i]).days / 30.4375
            for i in range(len(dates) - 1)
        ]
        avg = sum(deltas_months) / len(deltas_months)
        if all(abs(d - avg) < 1.0 for d in deltas_months):
            for name, months in _INTERVAL_MONTHS.items():
                if abs(avg - months) < 1.5:
                    return name
            if abs(avg - 1.0) < 0.5:
                return "monthly"
        return "irregular"

    # --- Try numeric-based intervals ---
    nums = [_try_parse_numeric(v) for v in sorted_labels]
    if all(n is not None for n in nums):
        deltas = [nums[i + 1] - nums[i] for i in range(len(nums) - 1)]
        if len(set(round(d, 4) for d in deltas)) == 1:
            d = deltas[0]
            for name, months in _INTERVAL_MONTHS.items():
                if abs(d - months) < 0.5:
                    return name
            return f"every_{round(d, 1)}_units"
        return "irregular"

    return "indeterminate"


def _measure_stats(df: pd.DataFrame, measure: str) -> dict:
    sub = df.loc[df["measure"] == measure, "value"].dropna()
    if sub.empty:
        return {"count": 0, "min": None, "max": None, "mean": None, "total": None}
    return {
        "count": int(len(sub)),
        "min":   round(float(sub.min()),  4),
        "max":   round(float(sub.max()),  4),
        "mean":  round(float(sub.mean()), 4),
        "total": round(float(sub.sum()),  4),
    }
    


# Interval length in months for each inferred label
_INTERVAL_LENGTH_MONTHS: dict[str, int] = {
    "annual":      12,
    "semi-annual":  6,
    "quarterly":    3,
    "biennial":    24,
    "monthly":      1,
}


def _origin_period_start(label: str, origin_interval: str) -> Optional[pd.Timestamp]:
    """
    Resolve the *start* date of one origin period from its label and the
    inferred interval type.

    Supports:
      - 4-digit year labels ("2020")            → Jan 1 of that year
      - Quarter labels ("2020Q1", "Q1 2020")    → first day of that quarter
      - ISO / recognisable date strings          → parsed directly
    Returns None if the label cannot be resolved.
    """
    import re
    label = str(label).strip()

    # --- Quarter pattern: YYYYQ#, Q# YYYY, YYYY-Q# ---
    q_match = re.search(
        r"(?:(\d{4})[^\d]*Q(\d)|(Q(\d))[^\d]*(\d{4}))",
        label, re.IGNORECASE,
    )
    if q_match:
        if q_match.group(1):  # YYYY Q#
            year, quarter = int(q_match.group(1)), int(q_match.group(2))
        else:                  # Q# YYYY
            quarter, year = int(q_match.group(4)), int(q_match.group(5))
        quarter = max(1, min(4, quarter))
        month_start = (quarter - 1) * 3 + 1
        return pd.Timestamp(f"{year}-{month_start:02d}-01")

    # --- 4-digit year only ---
    if re.fullmatch(r"\d{4}", label):
        return pd.Timestamp(f"{label}-01-01")

    # --- Generic date parse ---
    return _try_parse_date(label)


def _check_valuation_date(
    valuation_date: str,
    oldest_origin: str | None,   # origin_periods[0] — the earliest accident period
    max_dev_age: str | None,     # dev_ages[-1]      — the largest development age
    origin_interval: str = "annual",
) -> dict:
    """
    Validate the user-supplied valuation date against the actuarial formula:

        base             = end of oldest origin period
                         = start_of_oldest_period + interval_months − 1 day
        expected_valuation = base + max_development_age (months)

    Examples:
      Annual AY 2020, max dev age 60 months:
        base = Dec 31, 2020; expected = Dec 31, 2025
      Quarterly 2020Q1, max dev age 60 months:
        base = Mar 31, 2020; expected = Mar 31, 2025

    Falls back to a direct date comparison if dev ages are explicit date labels.

    Returns a dict with:
        consistent: bool | None   (None = could not determine)
        expected:   str | None    — the implied valuation date (ISO format)
        message:    str
    """
    vd = _try_parse_date(valuation_date)
    if vd is None:
        return {
            "consistent": None,
            "expected": None,
            "message": (
                f"Could not parse valuation_date '{valuation_date}' as a date. "
                "Manual confirmation required."
            ),
        }

    # --- Case 1: dev age labels are actual dates ---
    # The maximum dev age date is the implied valuation date directly.
    if max_dev_age is not None:
        dev_age_date = _try_parse_date(max_dev_age)
        if dev_age_date is not None:
            consistent = (vd == dev_age_date)
            return {
                "consistent": consistent,
                "expected": str(dev_age_date.date()),
                "message": (
                    f"Implied valuation date (max development age label): {dev_age_date.date()}. "
                    + ("Consistent." if consistent
                       else f"Supplied date {valuation_date} does not match.")
                ),
            }

    # --- Case 2: numeric development ages (months) ---
    if oldest_origin is None or max_dev_age is None:
        return {
            "consistent": None,
            "expected": None,
            "message": "Insufficient period data to compute implied valuation date.",
        }

    # Resolve start date of oldest origin period
    period_start = _origin_period_start(oldest_origin, origin_interval)
    if period_start is None:
        return {
            "consistent": None,
            "expected": None,
            "message": (
                f"Could not resolve start date of oldest origin period "
                f"'{oldest_origin}' (interval: {origin_interval}). "
                "Manual confirmation required."
            ),
        }

    # Resolve interval length in months (how long one origin period spans)
    interval_months = _INTERVAL_LENGTH_MONTHS.get(origin_interval)
    if interval_months is None:
        return {
            "consistent": None,
            "expected": None,
            "message": (
                f"Interval '{origin_interval}' is not mappable to a fixed month count "
                "(e.g. irregular). Manual confirmation required."
            ),
        }

    # Base = end of oldest origin period = period_start + interval_months - 1 day
    base = (
        period_start
        + pd.DateOffset(months=interval_months)
        - pd.DateOffset(days=1)
    )

    # Resolve max dev age in months
    dev_months = _try_parse_numeric(max_dev_age)
    if dev_months is None:
        return {
            "consistent": None,
            "expected": None,
            "message": (
                f"Could not parse max development age '{max_dev_age}' as a number of months. "
                "Manual confirmation required."
            ),
        }

    # Expected valuation date: end of oldest period + max dev age
    expected = base + pd.DateOffset(months=int(dev_months))
    consistent = (vd == expected)

    return {
        "consistent": consistent,
        "expected": str(expected.date()),
        "message": (
            f"Implied valuation date: end of '{oldest_origin}' ({base.date()}) "
            f"+ {int(dev_months)} months = {expected.date()}. "
            + ("Consistent." if consistent
               else f"Supplied date {valuation_date} does not match — please verify.")
        ),
    }


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class MetadataResult:
    """Outcome of store_metadata()."""
    output_path: Path          # path to the saved JSON file
    valuation_date_check: dict # consistency check result (for the agent to surface)


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

def store_metadata(
    canonical_path: str | Path,
    # User-supplied
    loss_currency: str,
    valuation_date: str,
    line_of_business: str,
    data_source_format: DataSourceFormat,
    specific_coverage: Optional[str] = None,
    notes: Optional[str] = None,
    output_path: Optional[str | Path] = None,
) -> MetadataResult:
    """
    Read the canonical CSV produced by Step 1, derive data-level metadata,
    combine with user-supplied context, and save a structured JSON file.

    Args:
        canonical_path:     Path to the canonical long-format CSV.
        loss_currency:      ISO 4217 currency code or free text, e.g. "USD".
        valuation_date:     As-of date for the data, e.g. "2024-12-31".
                            Validated against the implied diagonal in the data.
        line_of_business:   e.g. "Workers Compensation", "General Liability".
        data_source_format: "triangle" or "loss_run".
        specific_coverage:  Optional sub-coverage, e.g. "Medical Only". None if N/A.
        notes:              Optional free-text notes.
        output_path:        Override for JSON output location. Defaults to
                            {canonical_stem}-metadata.json in the same directory.

    Returns:
        MetadataResult with the output path and valuation date check details.

    Raises:
        FileNotFoundError: If canonical_path does not exist.
        ValueError:        If the canonical CSV is missing required columns.
    """
    src = Path(canonical_path).expanduser().resolve()
    if not src.exists():
        raise FileNotFoundError(f"Canonical file not found: {src}")

    dest: Path
    if output_path is None:
        dest = src.with_name(f"{src.stem}-metadata.json")
    else:
        dest = Path(output_path).expanduser().resolve()

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

    # --- Derive period lists ---
    origin_periods  = sorted(df["origin_period"].dropna().astype(str).unique(),
                             key=_sort_key)
    dev_ages        = sorted(df["development_age"].dropna().astype(str).unique(),
                             key=_sort_key)
    available_measures = sorted(df["measure"].dropna().unique().tolist())

    # --- Intervals ---
    origin_interval = _infer_interval(origin_periods)
    dev_interval    = _infer_interval(dev_ages)

    # --- Valuation date check ---
    vd_check = _check_valuation_date(
        valuation_date,
        oldest_origin=origin_periods[0] if origin_periods else None,
        max_dev_age=dev_ages[-1] if dev_ages else None,
        origin_interval=origin_interval,
    )

    # --- Per-measure stats ---
    per_measure = {m: _measure_stats(df, m) for m in available_measures}

    # --- Assemble metadata dict ---
    metadata: dict = {
        # ── User-supplied ──────────────────────────────────────────────────
        "loss_currency":       loss_currency,
        "valuation_date":      valuation_date,
        "line_of_business":    line_of_business,
        "specific_coverage":   specific_coverage,
        "data_source_format":  data_source_format,
        "notes":               notes,

        # ── Data-derived: periods ─────────────────────────────────────────
        "origin_period_start":    origin_periods[0]  if origin_periods else None,
        "origin_period_end":      origin_periods[-1] if origin_periods else None,
        "origin_period_count":    len(origin_periods),
        "origin_period_interval": origin_interval,
        "origin_periods":         origin_periods,

        "development_age_start":    dev_ages[0]  if dev_ages else None,
        "development_age_end":      dev_ages[-1] if dev_ages else None,
        "development_age_count":    len(dev_ages),
        "development_age_interval": dev_interval,
        "development_ages":         dev_ages,

        # ── Data-derived: content ─────────────────────────────────────────
        "available_measures":     available_measures,
        "total_populated_cells":  int(df["value"].notna().sum()),
        "per_measure_stats":      per_measure,

        # ── Valuation date confirmation ────────────────────────────────
        "valuation_date_check":   vd_check,

        # ── Provenance ─────────────────────────────────────────────────
        "source_canonical_path": str(src),
        "created_at":            datetime.now(timezone.utc).isoformat(),
    }

    dest.write_text(json.dumps(metadata, indent=2, default=str), encoding="utf-8")

    return MetadataResult(output_path=dest, valuation_date_check=vd_check)
