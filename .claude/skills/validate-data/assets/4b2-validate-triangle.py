"""
goal: Step 6 of validate-data — run validation checks on a triangle dataset.

Triangles are in wide format: rows represent origin (accident) periods and
columns represent development (age/maturity) periods. Values are cumulative
or incremental losses/counts. Each subsequent origin period has fewer
development columns populated (staircase / upper-left pattern).

These checks return raw findings only — no scores, no synthesized conclusions.
The agent (SKILL.md) is responsible for interpreting results, flagging issues
to the user, and requesting confirmation of summary statistics.

Checks (per triangle):
    1.  check_origin_period_column    — exactly one origin/accident period column
    2.  check_dev_period_row          — exactly one development period header row
    3.  check_origin_period_format    — consistent, groupable origin period format
    4.  check_top_left_nulls          — no missing cells in populated top-left region
    5.  check_period_intervals        — regular origin and development period intervals
    6.  check_staircase_pattern       — each later origin period has fewer dev periods
    7.  check_measure_tab_mapping     — one tab per selected measure (file-level)
    8.  check_numeric_values          — triangle numeric cells are numeric or convertible
    9.  check_duplicate_periods       — no duplicate origin or dev period labels
    10. check_paid_vs_incurred        — cumulative paid never > cumulative incurred
    11. check_closed_vs_reported      — cumulative closed never > cumulative reported
    12. check_no_negative_cumulative  — no negative cumulative values
    13. check_large_incrementals      — flag unusually large period-over-period changes

This script contains no user interaction.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

TriangleType = Literal["cumulative", "incremental"]

# Origin period format patterns (same as loss run script)
_ORIGIN_FORMAT_PATTERNS = [
    ("year_only",     re.compile(r"^\d{4}$")),
    ("date",          re.compile(r"^\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}$"
                                 r"|^\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2}$")),
    ("year_quarter",  re.compile(r"^\d{4}[\s\-_]?Q[1-4]$|^Q[1-4][\s\-_]?\d{4}$",
                                 re.IGNORECASE)),
    ("labeled_period",re.compile(r"(origin|accident|org|ay|period)[\s_\-]?\d+",
                                 re.IGNORECASE)),
]

_ORIGIN_RE = re.compile(
    r"\b(org(in)?|origin|accident|acc(ident)?|ay|oy|period|yr|year|\d{4})\b",
    re.IGNORECASE,
)

_DEV_RE = re.compile(
    r"\b(dev(elopment)?[\s_\-]?(pd?|period|age|mon|mo|month|yr|year|\d+)"
    r"|(\d+\s*(mo|month|yr|year|mos|yrs))|age[\s_\-]?\d+|\d+)\b",
    re.IGNORECASE,
)

# Measure keywords → used for tab-name matching
_MEASURE_TAB_PATTERNS: dict[str, re.Pattern] = {
    "incurred_losses": re.compile(r"\b(incurred?|incur)\b", re.IGNORECASE),
    "paid_losses":     re.compile(r"\b(paid|payment)\b",   re.IGNORECASE),
    "reported_counts": re.compile(r"\b(report(ed)?|open|rpt)\b", re.IGNORECASE),
    "closed_counts":   re.compile(r"\b(clos(ed)?|cls)\b",   re.IGNORECASE),
}

# Threshold for "large incremental" flagging (relative change)
_LARGE_INCREMENTAL_THRESHOLD = 2.0   # 200 % period-over-period change


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_numeric_triangle(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """
    Given a raw triangle DataFrame (first col = origin labels, remaining = data),
    return (numeric_df, origin_labels) where numeric_df contains only the data
    columns converted to float.
    """
    origin_labels = df.iloc[:, 0].astype(str).str.strip()
    data = df.iloc[:, 1:].copy()
    for col in data.columns:
        data[col] = pd.to_numeric(
            data[col].astype(str).str.replace(r"[\$,\s]", "", regex=True),
            errors="coerce",
        )
    return data, origin_labels

# ---------------------------------------------------------------------------
# Result dataclasses — raw findings only
# ---------------------------------------------------------------------------

@dataclass
class OriginPeriodColumnFindings:
    """Check 1: Exactly one origin/accident period column."""
    matched_columns: list[str]   # all columns matching origin-period pattern
    found_exactly_one: bool


@dataclass
class DevPeriodRowFindings:
    """Check 2: Exactly one development period header row."""
    # Column names that look like dev period labels
    dev_period_headers: list[str]
    # Column names that do NOT look like dev period labels (possible label cols)
    non_dev_headers: list[str]
    header_appears_valid: bool   # True when ≥ 1 dev-period header found


@dataclass
class OriginFormatFindings:
    """Check 3: Consistent origin period format."""
    detected_formats: list[str]
    is_consistent: bool
    unique_values: list[str]
    unrecognised_values: list[str]


@dataclass
class TopLeftNullFindings:
    """Check 4: Missing cells in the populated top-left region."""
    # Cells that are null but should be populated (row_idx, col_name) pairs
    unexpected_null_cells: list[tuple[int, str]]
    has_unexpected_nulls: bool


@dataclass
class PeriodIntervalFindings:
    """Check 5: Regularity of origin and development period intervals."""
    origin_values: list[str]          # raw origin period strings
    # If parseable to dates/years, the intervals between consecutive periods
    origin_intervals: Optional[list]  # e.g. [1, 1, 1] years or None
    origin_interval_is_regular: Optional[bool]
    dev_period_labels: list[str]      # raw dev period column header strings
    dev_intervals: Optional[list]
    dev_interval_is_regular: Optional[bool]


@dataclass
class StaircaseFindings:
    """Check 6: Each later origin period has fewer development periods of data."""
    # n_populated[i] = number of non-null dev period cells for origin period i
    n_populated_per_origin: list[int]
    is_non_increasing: bool       # True if counts are monotonically non-increasing
    violations: list[tuple[int, int, int, int]]  # (row_i, n_i, row_j, n_j) where n_j > n_i


@dataclass
class MeasureTabFindings:
    """Check 7: One tab per selected measure (file-level check)."""
    all_tab_names: list[str]
    mappings: dict[str, Optional[list[str]]]   # measure → matching tab names
    missing: list[str]                          # measures with no matching tab
    ambiguous: dict[str, list[str]]             # measures with >1 matching tab
    resolved: dict[str, Optional[str]]          # best guess tab per measure


@dataclass
class NumericValueFindings:
    """Check 8: Numeric convertibility of triangle data cells."""
    n_total_cells: int
    n_null_cells: int            # expected upper-right nulls
    n_non_numeric_cells: int
    # (row_idx, col_name, raw_value) for up to 20 non-numeric cells
    non_numeric_examples: list[tuple[int, str, str]]


@dataclass
class DuplicatePeriodFindings:
    """Check 9: Duplicate origin or development period labels."""
    duplicate_origin_periods: list[str]
    duplicate_dev_periods: list[str]


@dataclass
class PaidVsIncurredFindings:
    """Check 10: Cumulative paid never > cumulative incurred."""
    applicable: bool   # False only if either triangle is not present
    # (origin_label, dev_col) pairs where cumulative paid > cumulative incurred
    violations: list[tuple[str, str]]


@dataclass
class ClosedVsReportedFindings:
    """Check 11: Cumulative closed never > cumulative reported."""
    applicable: bool   # False only if either triangle is not present
    violations: list[tuple[str, str]]


@dataclass
class NegativeCumulativeFindings:
    """Check 12: No negative cumulative values for any origin period at any dev age."""
    applicable: bool   # always True when df is provided
    # (origin_label, dev_col, value) for up to 20 violations
    violations: list[tuple[str, str, float]]


@dataclass
class LargeIncrementalFindings:
    """Check 13: Large period-over-period changes in any triangle."""
    # (origin_label, dev_col, pct_change) for changes exceeding threshold
    violations: list[tuple[str, str, float]]
    threshold_pct: float   # threshold used (e.g. 200.0 for 200%)


@dataclass
class TriangleValidationResults:
    """Container for a single triangle's validation results."""
    tab_name: str                           # Excel tab this triangle came from
    triangle_type: TriangleType
    origin_period_col:   OriginPeriodColumnFindings
    dev_period_row:      DevPeriodRowFindings
    origin_format:       OriginFormatFindings
    top_left_nulls:      TopLeftNullFindings
    period_intervals:    PeriodIntervalFindings
    staircase:           StaircaseFindings
    numeric_values:      NumericValueFindings
    duplicate_periods:   DuplicatePeriodFindings
    paid_vs_incurred:    PaidVsIncurredFindings
    closed_vs_reported:  ClosedVsReportedFindings
    no_negative_cumul:   NegativeCumulativeFindings
    large_incrementals:  LargeIncrementalFindings


@dataclass
class TriangleSummaryStatistics:
    """
    Summary statistics returned when all checks pass.
    The agent presents these to the user for confirmation.
    """
    tab_name: str
    n_origin_periods: int
    n_dev_periods: int
    origin_periods: list[str]
    dev_periods: list[str]
    value_ranges: dict   # {min, max, mean} across all populated cells
    pct_populated: float # % of cells that are non-null


# ---------------------------------------------------------------------------
# Individual check functions
# ---------------------------------------------------------------------------

def check_origin_period_column(df: pd.DataFrame) -> OriginPeriodColumnFindings:
    """Check 1 — Verify exactly one origin/accident period column is present."""
    matches = [c for c in df.columns if _ORIGIN_RE.search(str(c))]
    # Also count the first column as a candidate if it contains string labels
    first_col = df.columns[0]
    if first_col not in matches:
        first_vals = df.iloc[:, 0].dropna().astype(str)
        if first_vals.apply(lambda v: bool(re.search(
            r"\d{4}|(origin|accident|org|ay|period)", v, re.IGNORECASE
        ))).mean() > 0.5:
            matches = [first_col] + matches

    return OriginPeriodColumnFindings(
        matched_columns=matches,
        found_exactly_one=len(matches) == 1,
    )


def check_dev_period_row(df: pd.DataFrame) -> DevPeriodRowFindings:
    """Check 2 — Verify the column headers look like development period labels."""
    dev_hdrs    = [str(c) for c in df.columns[1:] if _DEV_RE.search(str(c))]
    non_dev_hdrs= [str(c) for c in df.columns[1:] if not _DEV_RE.search(str(c))]
    return DevPeriodRowFindings(
        dev_period_headers=dev_hdrs,
        non_dev_headers=non_dev_hdrs,
        header_appears_valid=len(dev_hdrs) > 0,
    )


def check_origin_period_format(df: pd.DataFrame) -> OriginFormatFindings:
    """Check 3 — Verify origin period values follow a consistent groupable format."""
    vals = df.iloc[:, 0].dropna().astype(str).str.strip().tolist()
    detected: set[str] = set()
    unrecognised: list[str] = []
    for v in vals:
        matched = False
        for label, pat in _ORIGIN_FORMAT_PATTERNS:
            if pat.search(v):
                detected.add(label)
                matched = True
                break
        if not matched:
            unrecognised.append(v)
    return OriginFormatFindings(
        detected_formats=sorted(detected),
        is_consistent=len(detected) <= 1 and not unrecognised,
        unique_values=vals,
        unrecognised_values=unrecognised,
    )


def check_top_left_nulls(df: pd.DataFrame) -> TopLeftNullFindings:
    """
    Check 4 — Find null cells that appear inside the populated top-left region.

    The top-left region is defined as: for each origin period row, all columns
    up to and including the last non-null development value in that row.
    """
    data, _ = _extract_numeric_triangle(df)
    unexpected: list[tuple[int, str]] = []

    for row_idx in range(len(data)):
        row = data.iloc[row_idx]
        non_null_positions = [i for i, v in enumerate(row) if pd.notna(v)]
        if not non_null_positions:
            continue
        last_pos = non_null_positions[-1]
        for col_i in range(last_pos):
            if pd.isna(row.iloc[col_i]):
                unexpected.append((row_idx, str(data.columns[col_i])))

    return TopLeftNullFindings(
        unexpected_null_cells=unexpected,
        has_unexpected_nulls=len(unexpected) > 0,
    )


def _try_parse_period_values(values: list[str]) -> Optional[list]:
    """
    Attempt to extract comparable numeric values from period labels to calculate
    intervals. Tries: 4-digit year, labeled integer (e.g. 'Period 3'), quarter.
    Returns a list of floats or None if cannot parse.
    """
    nums = []
    for v in values:
        # Year only
        m = re.search(r"\b(\d{4})\b", v)
        if m:
            year = int(m.group(1))
            # Check for quarter suffix
            q = re.search(r"Q(\d)", v, re.IGNORECASE)
            nums.append(year + (int(q.group(1)) - 1) / 4.0 if q else float(year))
            continue
        # Labeled integer (e.g. "Period 3", "Dev Pd 4", "12 mo")
        m = re.search(r"(\d+)", v)
        if m:
            nums.append(float(m.group(1)))
            continue
        return None  # unparseable
    return nums if len(nums) == len(values) else None


def check_period_intervals(df: pd.DataFrame) -> PeriodIntervalFindings:
    """Check 5 — Verify that origin and development period intervals are regular."""
    origin_vals = df.iloc[:, 0].dropna().astype(str).str.strip().tolist()
    dev_cols    = [str(c) for c in df.columns[1:]]

    origin_nums = _try_parse_period_values(origin_vals)
    dev_nums    = _try_parse_period_values(dev_cols)

    def _intervals(nums):
        if nums is None or len(nums) < 2:
            return None
        return [round(nums[i+1] - nums[i], 4) for i in range(len(nums) - 1)]

    origin_ivs  = _intervals(origin_nums)
    dev_ivs     = _intervals(dev_nums)

    origin_reg  = (len(set(origin_ivs)) == 1) if origin_ivs else None
    dev_reg     = (len(set(dev_ivs)) == 1)     if dev_ivs    else None

    return PeriodIntervalFindings(
        origin_values=origin_vals,
        origin_intervals=origin_ivs,
        origin_interval_is_regular=origin_reg,
        dev_period_labels=dev_cols,
        dev_intervals=dev_ivs,
        dev_interval_is_regular=dev_reg,
    )


def check_staircase_pattern(df: pd.DataFrame) -> StaircaseFindings:
    """Check 6 — Each successive origin period row should have ≤ dev periods populated."""
    data, _ = _extract_numeric_triangle(df)
    counts = [int(row.notna().sum()) for _, row in data.iterrows()]
    violations: list[tuple[int, int, int, int]] = []
    for i in range(len(counts) - 1):
        if counts[i+1] > counts[i]:
            violations.append((i, counts[i], i+1, counts[i+1]))
    return StaircaseFindings(
        n_populated_per_origin=counts,
        is_non_increasing=len(violations) == 0,
        violations=violations,
    )


def check_measure_tab_mapping(
    file_path: str | Path,
    selected_measures: list[str],
) -> MeasureTabFindings:
    """
    Check 7 — Verify that exactly one Excel tab maps to each selected measure.
    CSV files always return a single anonymous tab.
    """
    path = Path(file_path)
    ext  = path.suffix.lower()

    if ext == ".csv":
        tab_names = ["(csv — single sheet)"]
    else:
        xl = pd.ExcelFile(path, engine="xlrd" if ext == ".xls" else "openpyxl")
        tab_names = xl.sheet_names

    mappings: dict[str, Optional[list[str]]] = {}
    for measure in selected_measures:
        pat = _MEASURE_TAB_PATTERNS.get(measure)
        if pat is None:
            mappings[measure] = None
            continue
        candidates = [t for t in tab_names if pat.search(str(t))]
        mappings[measure] = candidates if candidates else None

    missing   = [m for m, tabs in mappings.items() if not tabs]
    ambiguous = {m: tabs for m, tabs in mappings.items() if tabs and len(tabs) > 1}
    resolved  = {m: (tabs[0] if tabs else None) for m, tabs in mappings.items()}

    return MeasureTabFindings(
        all_tab_names=tab_names,
        mappings=mappings,
        missing=missing,
        ambiguous=ambiguous,
        resolved=resolved,
    )


def check_numeric_values(df: pd.DataFrame) -> NumericValueFindings:
    """Check 8 — Verify all data cells are numeric or convertible to numeric."""
    data_raw = df.iloc[:, 1:]
    total    = data_raw.size
    n_null   = int(data_raw.isna().sum().sum())
    non_num_examples: list[tuple[int, str, str]] = []

    for col in data_raw.columns:
        for row_idx, val in enumerate(data_raw[col]):
            if pd.isna(val):
                continue
            converted = pd.to_numeric(
                str(val).replace("$","").replace(",","").strip(),
                errors="coerce",
            )
            if pd.isna(converted):
                if len(non_num_examples) < 20:
                    non_num_examples.append((row_idx, str(col), str(val)))

    return NumericValueFindings(
        n_total_cells=total,
        n_null_cells=n_null,
        n_non_numeric_cells=len(non_num_examples),
        non_numeric_examples=non_num_examples,
    )


def check_duplicate_periods(df: pd.DataFrame) -> DuplicatePeriodFindings:
    """Check 9 — Flag duplicate origin period rows or development period columns."""
    origin_vals = df.iloc[:, 0].astype(str).str.strip().tolist()
    dev_cols    = [str(c) for c in df.columns[1:]]

    seen_origin: set[str] = set()
    dup_origin: list[str] = []
    for v in origin_vals:
        if v in seen_origin:
            dup_origin.append(v)
        seen_origin.add(v)

    seen_dev: set[str] = set()
    dup_dev: list[str] = []
    for v in dev_cols:
        if v in seen_dev:
            dup_dev.append(v)
        seen_dev.add(v)

    return DuplicatePeriodFindings(
        duplicate_origin_periods=dup_origin,
        duplicate_dev_periods=dup_dev,
    )


def _align_triangles(
    df_a: pd.DataFrame,
    df_b: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """
    Align two triangle DataFrames on their common origin periods (first column)
    and return numeric data frames plus the shared origin labels.
    """
    data_a, orig_a = _extract_numeric_triangle(df_a)
    data_b, orig_b = _extract_numeric_triangle(df_b)

    df_a2 = data_a.copy(); df_a2.insert(0, "__origin__", orig_a.values)
    df_b2 = data_b.copy(); df_b2.insert(0, "__origin__", orig_b.values)

    merged = df_a2.merge(df_b2, on="__origin__", suffixes=("_a", "_b"))
    common_origins = merged["__origin__"].tolist()

    # Find common dev columns
    cols_a = [c for c in df_a2.columns if c != "__origin__"]
    cols_b = [c for c in df_b2.columns if c != "__origin__"]
    common_devs = [c for c in cols_a if c in set(cols_b)]

    aligned_a = merged[[f"{c}_a" if f"{c}_a" in merged.columns else c
                         for c in [f"{d}_a" for d in common_devs]]].copy()
    aligned_b = merged[[f"{c}_b" if f"{c}_b" in merged.columns else c
                         for c in [f"{d}_b" for d in common_devs]]].copy()
    aligned_a.columns = common_devs
    aligned_b.columns = common_devs

    return aligned_a, aligned_b, common_origins


def check_paid_vs_incurred(
    df_paid: Optional[pd.DataFrame],
    df_incurred: Optional[pd.DataFrame],
) -> PaidVsIncurredFindings:
    """
    Check 10 — Cumulative paid never > cumulative incurred.
    Input DataFrames must already be in cumulative form.
    """
    if df_paid is None or df_incurred is None:
        return PaidVsIncurredFindings(applicable=False, violations=[])

    paid_align, inc_align, origins = _align_triangles(df_paid, df_incurred)

    violations: list[tuple[str, str]] = []
    for row_i, origin in enumerate(origins):
        for col in paid_align.columns:
            p = paid_align.iloc[row_i][col]
            i = inc_align.iloc[row_i][col]
            if pd.notna(p) and pd.notna(i) and p > i:
                violations.append((str(origin), str(col)))

    return PaidVsIncurredFindings(applicable=True, violations=violations)


def check_closed_vs_reported(
    df_closed: Optional[pd.DataFrame],
    df_reported: Optional[pd.DataFrame],
) -> ClosedVsReportedFindings:
    """
    Check 11 — Cumulative closed never > cumulative reported.
    Input DataFrames must already be in cumulative form.
    """
    if df_closed is None or df_reported is None:
        return ClosedVsReportedFindings(applicable=False, violations=[])

    closed_align, rep_align, origins = _align_triangles(df_closed, df_reported)

    violations: list[tuple[str, str]] = []
    for row_i, origin in enumerate(origins):
        for col in closed_align.columns:
            c = closed_align.iloc[row_i][col]
            r = rep_align.iloc[row_i][col]
            if pd.notna(c) and pd.notna(r) and c > r:
                violations.append((str(origin), str(col)))

    return ClosedVsReportedFindings(applicable=True, violations=violations)


def check_no_negative_cumulative(
    df: pd.DataFrame,
) -> NegativeCumulativeFindings:
    """
    Check 12 — No negative cumulative values.
    Input DataFrame must already be in cumulative form.
    """
    data, origins = _extract_numeric_triangle(df)

    violations: list[tuple[str, str, float]] = []
    for row_i, origin in enumerate(origins):
        for col in data.columns:
            val = data.iloc[row_i][col]
            if pd.notna(val) and val < 0:
                violations.append((str(origin), str(col), float(val)))
                if len(violations) >= 20:
                    return NegativeCumulativeFindings(
                        applicable=True, violations=violations
                    )

    return NegativeCumulativeFindings(applicable=True, violations=violations)


def check_large_incrementals(
    df: pd.DataFrame,
    threshold_pct: float = _LARGE_INCREMENTAL_THRESHOLD * 100,
) -> LargeIncrementalFindings:
    """
    Check 13 — Flag cells where period-over-period change exceeds threshold_pct %.
    Works on both cumulative and incremental triangles (computes incrementals either way).
    """
    data, origins = _extract_numeric_triangle(df)

    # Compute incrementals (diff across columns)
    incremental = data.diff(axis=1)
    base        = data.shift(axis=1).abs()

    # % change = incremental / |prior period value|
    pct_change  = (incremental / base.replace(0, np.nan)).abs() * 100

    violations: list[tuple[str, str, float]] = []
    threshold = threshold_pct

    for row_i, origin in enumerate(origins):
        for col in pct_change.columns:
            pct = pct_change.iloc[row_i][col]
            if pd.notna(pct) and pct > threshold:
                violations.append((str(origin), str(col), round(float(pct), 1)))

    return LargeIncrementalFindings(
        violations=violations,
        threshold_pct=threshold_pct,
    )


# ---------------------------------------------------------------------------
# Summary statistics (only built when all checks pass)
# ---------------------------------------------------------------------------

def build_summary_statistics(
    df: pd.DataFrame,
    tab_name: str,
    triangle_type: TriangleType,
) -> TriangleSummaryStatistics:
    """
    Build summary statistics for a single triangle for the agent to present.
    Called only after all checks have been reviewed/resolved.
    """
    data, origins = _extract_numeric_triangle(df)
    origin_list = origins.tolist()
    dev_list    = [str(c) for c in data.columns]

    all_vals = data.values.flatten()
    populated = all_vals[~np.isnan(all_vals)]
    pct_pop  = round(len(populated) / len(all_vals) * 100, 1) if len(all_vals) > 0 else 0.0

    return TriangleSummaryStatistics(
        tab_name=tab_name,
        n_origin_periods=len(origin_list),
        n_dev_periods=len(dev_list),
        origin_periods=origin_list,
        dev_periods=dev_list,
        value_ranges={
            "min":  round(float(populated.min()), 2)  if len(populated) > 0 else None,
            "max":  round(float(populated.max()), 2)  if len(populated) > 0 else None,
            "mean": round(float(populated.mean()), 2) if len(populated) > 0 else None,
        },
        pct_populated=pct_pop,
    )


# ---------------------------------------------------------------------------
# Per-triangle convenience wrapper
# ---------------------------------------------------------------------------

def validate_triangle(
    df: pd.DataFrame,
    tab_name: str,
    triangle_type: TriangleType,
    df_paid: Optional[pd.DataFrame] = None,
    df_incurred: Optional[pd.DataFrame] = None,
    df_closed: Optional[pd.DataFrame] = None,
    df_reported: Optional[pd.DataFrame] = None,
) -> TriangleValidationResults:
    """
    Run all per-triangle validation checks and return a results container.

    Args:
        df:            The triangle DataFrame (first col = origin labels,
                       remaining cols = dev period data).
        tab_name:      Name of the Excel tab this triangle came from.
        triangle_type: "cumulative" or "incremental".
        df_paid / df_incurred / df_closed / df_reported:
                       Other measure triangles (optional), used for cross-checks
                       10 and 11. Pass None if a measure is not available.

    Returns:
        TriangleValidationResults with raw findings from all 13 checks.
    """
    return TriangleValidationResults(
        tab_name=tab_name,
        triangle_type=triangle_type,
        origin_period_col  = check_origin_period_column(df),
        dev_period_row     = check_dev_period_row(df),
        origin_format      = check_origin_period_format(df),
        top_left_nulls     = check_top_left_nulls(df),
        period_intervals   = check_period_intervals(df),
        staircase          = check_staircase_pattern(df),
        numeric_values     = check_numeric_values(df),
        duplicate_periods  = check_duplicate_periods(df),
        paid_vs_incurred   = check_paid_vs_incurred(df_paid, df_incurred),
        closed_vs_reported = check_closed_vs_reported(df_closed, df_reported),
        no_negative_cumul  = check_no_negative_cumulative(df),
        large_incrementals = check_large_incrementals(df),
        # Tab mapping is a file-level check — call check_measure_tab_mapping() separately
        # and attach the result if needed; not duplicated here to avoid re-reading the file.
    )


def validate_all_triangles(
    file_path: str | Path,
    selected_measures: list[str],
    triangle_type: TriangleType,
    resolved_tabs: dict[str, str],
) -> tuple[MeasureTabFindings, dict[str, TriangleValidationResults]]:
    """
    File-level entry point: run tab mapping check then validate each triangle.

    Args:
        file_path:        Path to the Excel (or CSV) file.
        selected_measures: Measures the user said are present, e.g.
                          ["incurred_losses", "paid_losses"].
        triangle_type:    "cumulative" or "incremental".
        resolved_tabs:    Agent's resolved mapping of measure → tab name after
                          any ambiguity was cleared with the user in Step 7a.
                          e.g. {"incurred_losses": "Incurred", "paid_losses": "Paid"}.

    Returns:
        (MeasureTabFindings, dict of measure → TriangleValidationResults)
    """
    path = Path(file_path)
    ext  = path.suffix.lower()

    # File-level tab check
    tab_findings = check_measure_tab_mapping(file_path, selected_measures)

    # Load each resolved triangle
    dfs: dict[str, pd.DataFrame] = {}
    for measure, tab in resolved_tabs.items():
        if tab is None:
            continue
        if ext == ".csv":
            dfs[measure] = pd.read_csv(path)
        else:
            dfs[measure] = pd.read_excel(
                path, sheet_name=tab,
                engine="xlrd" if ext == ".xls" else "openpyxl",
            )

    # Run per-triangle checks
    results: dict[str, TriangleValidationResults] = {}
    for measure, df in dfs.items():
        results[measure] = validate_triangle(
            df=df,
            tab_name=resolved_tabs.get(measure, ""),
            triangle_type=triangle_type,
            df_paid     = dfs.get("paid_losses"),
            df_incurred = dfs.get("incurred_losses"),
            df_closed   = dfs.get("closed_counts"),
            df_reported = dfs.get("reported_counts"),
        )

    return tab_findings, results
