"""
goal: Step 5 of validate-data — run validation checks on a loss run dataset.

Loss runs are in long format: one row per claim per evaluation date, with
columns for claim ID, accident/origin period, evaluation date, and financial
amounts (paid loss, incurred loss, reported counts, closed counts).

These checks return raw findings only — no scores, no synthesized conclusions.
The agent (SKILL.md) is responsible for interpreting results, flagging issues
to the user, and requesting confirmation of summary statistics.

Checks:
    1.  check_claim_id_column       — claim number/ID column is present
    2.  check_origin_period_column  — accident/origin period column is present
    3.  check_origin_period_format  — origin periods are consistent and groupable
    4.  check_measure_columns       — exactly one column maps to each selected measure
    5.  check_numeric_measures      — measure columns are numeric or convertible
    6.  check_eval_date_column      — evaluation date column is present
    7.  check_duplicate_rows        — no duplicate claim / eval-date combinations
    8.  check_isolated_issues       — flag individual cells/rows/cols with anomalies

This script contains no user interaction.
"""

import re
from dataclasses import dataclass, field
from typing import Optional
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Column-name regex patterns
# ---------------------------------------------------------------------------

_CLAIM_ID_RE = re.compile(
    r"\b(claim|clm|file|case|suit|ref)\b.*\b(id|num|number|no\.?)\b"
    r"|\b(claim|clm)\b",
    re.IGNORECASE,
)

_ORIGIN_PERIOD_RE = re.compile(
    r"\b(accident|acc(ident)?|origin|org|ay|loss)\b.*\b(date|yr|year|period|pd)\b"
    r"|\b(accident|origin|ay)\b",
    re.IGNORECASE,
)

_EVAL_DATE_RE = re.compile(
    r"\b(eval|evaluation|as.?of|report(ing)?|val(uation)?)\b.*\b(date|dt|yr|year)\b"
    r"|\b(eval|evaluation|as.?of)\b",
    re.IGNORECASE,
)

# Measure keyword patterns (order matters — more specific first)
_MEASURE_PATTERNS: dict[str, re.Pattern] = {
    "incurred_losses":  re.compile(r"\b(incurred?|incur)\b", re.IGNORECASE),
    "paid_losses":      re.compile(r"\b(paid|payment)\b", re.IGNORECASE),
    "reported_counts":  re.compile(r"\b(report(ed)?|open)\b.*\b(count|cnt|claim|num|no)\b"
                                   r"|\b(reported?_count|rpt_cnt)\b", re.IGNORECASE),
    "closed_counts":    re.compile(r"\b(clos(ed)?)\b.*\b(count|cnt|claim|num|no)\b"
                                   r"|\b(closed?_count|cls_cnt)\b", re.IGNORECASE),
}

# Origin-period format patterns used to classify groupability
_ORIGIN_FORMAT_PATTERNS = [
    ("year_only",     re.compile(r"^\d{4}$")),
    ("date",          re.compile(r"^\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}$"
                                 r"|^\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2}$")),
    ("year_quarter",  re.compile(r"^\d{4}[\s\-_]?Q[1-4]$|^Q[1-4][\s\-_]?\d{4}$",
                                 re.IGNORECASE)),
    ("labeled_period",re.compile(r"(origin|accident|org|ay|period)[\s_\-]?\d+",
                                 re.IGNORECASE)),
]


# ---------------------------------------------------------------------------
# Result dataclasses — raw findings only
# ---------------------------------------------------------------------------

@dataclass
class ClaimIdFindings:
    """Check 1: Claim ID/number column."""
    found: bool
    matched_columns: list[str]   # all columns matching the pattern
    selected_column: Optional[str]  # best candidate (first match)


@dataclass
class OriginPeriodFindings:
    """Check 2: Accident/origin period column."""
    found: bool
    matched_columns: list[str]
    selected_column: Optional[str]


@dataclass
class OriginPeriodFormatFindings:
    """Check 3: Consistency and groupability of origin period values."""
    column: Optional[str]             # column examined (None if check 2 failed)
    detected_formats: list[str]       # format labels found (from _ORIGIN_FORMAT_PATTERNS)
    is_consistent: bool               # True if only one format detected
    unique_values: list[str]          # all distinct origin period values
    unrecognised_values: list[str]    # values that matched no known pattern


@dataclass
class MeasureColumnFindings:
    """Check 4: One-to-one mapping from selected measures to columns."""
    # For each selected measure: None = not found, list of str = candidates
    mappings: dict[str, Optional[list[str]]]
    # Measures with no matching column
    missing: list[str]
    # Measures with more than one candidate column
    ambiguous: dict[str, list[str]]
    # Resolved best guess for each measure (first candidate, or None)
    resolved: dict[str, Optional[str]]


@dataclass
class NumericMeasureFindings:
    """Check 5: Numeric format of measure columns."""
    # Column → True if already numeric, False if not, None if column missing
    is_numeric: dict[str, Optional[bool]]
    # Column → True if convertible to numeric after stripping symbols ($, commas)
    is_convertible: dict[str, Optional[bool]]
    # Column → example non-numeric values (up to 5) for non-convertible columns
    problem_values: dict[str, list[str]]


@dataclass
class EvalDateFindings:
    """Check 6: Evaluation date column."""
    found: bool
    matched_columns: list[str]
    selected_column: Optional[str]
    # Distinct evaluation dates found (as strings), sorted
    unique_eval_dates: list[str]


@dataclass
class DuplicateRowFindings:
    """Check 7: Duplicate claim / eval-date rows."""
    claim_column: Optional[str]
    eval_date_column: Optional[str]
    duplicate_count: int          # number of duplicate rows
    # Up to 10 example duplicate (claim_id, eval_date) pairs
    example_duplicates: list[tuple]


@dataclass
class IsolatedIssueFindings:
    """Check 8: Row- and column-level anomalies."""
    # Rows where ALL measure columns are null
    fully_null_measure_rows: list[int]       # list of row indices (0-based)
    # Columns where > threshold % of values are null
    high_null_columns: dict[str, float]      # col → null pct
    # Measure columns containing negative values
    negative_value_columns: dict[str, int]   # col → count of negatives
    # Rows with any negative measure value (up to 20)
    negative_value_rows: list[int]
    # Rows where incurred < paid (logical inconsistency), up to 20
    incurred_less_than_paid_rows: list[int]


@dataclass
class LossRunValidationResults:
    """Container for all loss-run validation check results."""
    claim_id:           ClaimIdFindings
    origin_period:      OriginPeriodFindings
    origin_format:      OriginPeriodFormatFindings
    measure_columns:    MeasureColumnFindings
    numeric_measures:   NumericMeasureFindings
    eval_date:          EvalDateFindings
    duplicates:         DuplicateRowFindings
    isolated_issues:    IsolatedIssueFindings


@dataclass
class LossRunSummaryStatistics:
    """
    Summary statistics returned when all checks pass.
    The agent presents these to the user for confirmation.
    """
    n_rows: int
    n_unique_claims: Optional[int]
    origin_periods: list[str]           # sorted distinct origin period values
    eval_dates: list[str]               # sorted distinct evaluation dates
    measure_ranges: dict[str, dict]     # measure → {min, max, mean, pct_null}


# ---------------------------------------------------------------------------
# Individual check functions
# ---------------------------------------------------------------------------

def check_claim_id_column(df: pd.DataFrame) -> ClaimIdFindings:
    """Check 1 — Find the claim number / ID column."""
    matches = [c for c in df.columns if _CLAIM_ID_RE.search(str(c))]
    return ClaimIdFindings(
        found=len(matches) > 0,
        matched_columns=matches,
        selected_column=matches[0] if matches else None,
    )


def check_origin_period_column(df: pd.DataFrame) -> OriginPeriodFindings:
    """Check 2 — Find the accident / origin period column."""
    matches = [c for c in df.columns if _ORIGIN_PERIOD_RE.search(str(c))]
    return OriginPeriodFindings(
        found=len(matches) > 0,
        matched_columns=matches,
        selected_column=matches[0] if matches else None,
    )


def check_origin_period_format(
    df: pd.DataFrame,
    origin_col: Optional[str],
) -> OriginPeriodFormatFindings:
    """
    Check 3 — Verify that origin period values follow a consistent, groupable format.
    """
    if origin_col is None or origin_col not in df.columns:
        return OriginPeriodFormatFindings(
            column=None,
            detected_formats=[],
            is_consistent=False,
            unique_values=[],
            unrecognised_values=[],
        )

    unique_vals = [str(v).strip() for v in df[origin_col].dropna().unique()]
    detected: set[str] = set()
    unrecognised: list[str] = []

    for val in unique_vals:
        matched = False
        for label, pattern in _ORIGIN_FORMAT_PATTERNS:
            if pattern.search(val):
                detected.add(label)
                matched = True
                break
        if not matched:
            unrecognised.append(val)

    return OriginPeriodFormatFindings(
        column=origin_col,
        detected_formats=sorted(detected),
        is_consistent=len(detected) <= 1 and len(unrecognised) == 0,
        unique_values=sorted(unique_vals),
        unrecognised_values=unrecognised,
    )


def check_measure_columns(
    df: pd.DataFrame,
    selected_measures: list[str],
) -> MeasureColumnFindings:
    """
    Check 4 — Confirm exactly one column maps to each selected measure.

    Args:
        df: The loaded DataFrame.
        selected_measures: List of measure keys the user said are present,
            e.g. ["incurred_losses", "paid_losses"].
    """
    mappings: dict[str, Optional[list[str]]] = {}
    for measure in selected_measures:
        pattern = _MEASURE_PATTERNS.get(measure)
        if pattern is None:
            mappings[measure] = None
            continue
        candidates = [c for c in df.columns if pattern.search(str(c))]
        mappings[measure] = candidates if candidates else None

    missing   = [m for m, cols in mappings.items() if not cols]
    ambiguous = {m: cols for m, cols in mappings.items() if cols and len(cols) > 1}
    resolved  = {m: (cols[0] if cols else None) for m, cols in mappings.items()}

    return MeasureColumnFindings(
        mappings=mappings,
        missing=missing,
        ambiguous=ambiguous,
        resolved=resolved,
    )


def _try_convert_numeric(series: pd.Series) -> pd.Series:
    """Strip common currency/formatting characters and attempt numeric conversion."""
    cleaned = series.astype(str).str.replace(r"[\$,\s]", "", regex=True)
    return pd.to_numeric(cleaned, errors="coerce")


def check_numeric_measures(
    df: pd.DataFrame,
    resolved_columns: dict[str, Optional[str]],
) -> NumericMeasureFindings:
    """
    Check 5 — Verify that measure columns are numeric or convertible to numeric.

    Args:
        resolved_columns: output of MeasureColumnFindings.resolved — maps
            measure keys to best-guess column names.
    """
    is_numeric:     dict[str, Optional[bool]] = {}
    is_convertible: dict[str, Optional[bool]] = {}
    problem_values: dict[str, list[str]] = {}

    for measure, col in resolved_columns.items():
        if col is None or col not in df.columns:
            is_numeric[measure] = None
            is_convertible[measure] = None
            problem_values[measure] = []
            continue

        series = df[col].dropna()
        if pd.api.types.is_numeric_dtype(series):
            is_numeric[measure] = True
            is_convertible[measure] = True
            problem_values[measure] = []
        else:
            is_numeric[measure] = False
            converted = _try_convert_numeric(series)
            n_failed = converted.isna().sum()
            is_convertible[measure] = (n_failed == 0)
            if n_failed > 0:
                bad_mask = converted.isna()
                problem_values[measure] = (
                    series[bad_mask].astype(str).unique()[:5].tolist()
                )
            else:
                problem_values[measure] = []

    return NumericMeasureFindings(
        is_numeric=is_numeric,
        is_convertible=is_convertible,
        problem_values=problem_values,
    )


def check_eval_date_column(df: pd.DataFrame) -> EvalDateFindings:
    """Check 6 — Find the evaluation date column and list distinct eval dates."""
    matches = [c for c in df.columns if _EVAL_DATE_RE.search(str(c))]
    selected = matches[0] if matches else None

    unique_dates: list[str] = []
    if selected and selected in df.columns:
        unique_dates = sorted(
            df[selected].dropna().astype(str).unique().tolist()
        )

    return EvalDateFindings(
        found=len(matches) > 0,
        matched_columns=matches,
        selected_column=selected,
        unique_eval_dates=unique_dates,
    )


def check_duplicate_rows(
    df: pd.DataFrame,
    claim_col: Optional[str],
    eval_col: Optional[str],
) -> DuplicateRowFindings:
    """Check 7 — Identify duplicate (claim, eval-date) row pairs."""
    if not claim_col or not eval_col:
        return DuplicateRowFindings(
            claim_column=claim_col,
            eval_date_column=eval_col,
            duplicate_count=0,
            example_duplicates=[],
        )

    subset = [claim_col, eval_col]
    dupes = df[df.duplicated(subset=subset, keep=False)]
    dup_count = len(dupes)
    examples: list[tuple] = []
    if dup_count > 0:
        pairs = dupes[subset].drop_duplicates()
        examples = list(pairs.itertuples(index=False, name=None))[:10]

    return DuplicateRowFindings(
        claim_column=claim_col,
        eval_date_column=eval_col,
        duplicate_count=dup_count,
        example_duplicates=examples,
    )


def check_isolated_issues(
    df: pd.DataFrame,
    resolved_columns: dict[str, Optional[str]],
    null_threshold_pct: float = 20.0,
) -> IsolatedIssueFindings:
    """
    Check 8 — Flag row- and column-level anomalies in measure columns.

    Args:
        df: The loaded DataFrame.
        resolved_columns: Measure → column name mapping.
        null_threshold_pct: Columns with null % above this are flagged.
    """
    measure_cols = [c for c in resolved_columns.values() if c and c in df.columns]

    # Rows where ALL measure columns are null
    if measure_cols:
        all_null_mask = df[measure_cols].isna().all(axis=1)
        fully_null_rows = df.index[all_null_mask].tolist()
    else:
        fully_null_rows = []

    # Columns with high null rates
    high_null: dict[str, float] = {}
    for col in measure_cols:
        pct = df[col].isna().mean() * 100
        if pct > null_threshold_pct:
            high_null[col] = round(pct, 1)

    # Columns and rows with negative values
    neg_cols: dict[str, int] = {}
    neg_rows: set[int] = set()
    for col in measure_cols:
        numeric = pd.to_numeric(df[col], errors="coerce")
        mask = numeric < 0
        count = int(mask.sum())
        if count > 0:
            neg_cols[col] = count
            neg_rows.update(df.index[mask].tolist())

    # Incurred < paid logical check
    incurred_col = resolved_columns.get("incurred_losses")
    paid_col     = resolved_columns.get("paid_losses")
    inc_lt_paid_rows: list[int] = []

    if (
        incurred_col and paid_col
        and incurred_col in df.columns
        and paid_col in df.columns
    ):
        inc_num  = pd.to_numeric(df[incurred_col], errors="coerce")
        paid_num = pd.to_numeric(df[paid_col],     errors="coerce")
        mask = (inc_num < paid_num) & inc_num.notna() & paid_num.notna()
        inc_lt_paid_rows = df.index[mask].tolist()[:20]

    return IsolatedIssueFindings(
        fully_null_measure_rows=fully_null_rows,
        high_null_columns=high_null,
        negative_value_columns=neg_cols,
        negative_value_rows=sorted(neg_rows)[:20],
        incurred_less_than_paid_rows=inc_lt_paid_rows,
    )


# ---------------------------------------------------------------------------
# Summary statistics (only built when all checks pass)
# ---------------------------------------------------------------------------

def build_summary_statistics(
    df: pd.DataFrame,
    claim_col: Optional[str],
    origin_col: Optional[str],
    eval_col: Optional[str],
    resolved_columns: dict[str, Optional[str]],
) -> LossRunSummaryStatistics:
    """
    Build summary statistics for the agent to present to the user for confirmation.
    Called only after isolated issues have been reviewed/resolved.
    """
    n_unique_claims = (
        int(df[claim_col].nunique()) if claim_col and claim_col in df.columns else None
    )
    origin_periods: list[str] = []
    if origin_col and origin_col in df.columns:
        origin_periods = sorted(df[origin_col].dropna().astype(str).unique().tolist())

    eval_dates: list[str] = []
    if eval_col and eval_col in df.columns:
        eval_dates = sorted(df[eval_col].dropna().astype(str).unique().tolist())

    measure_ranges: dict[str, dict] = {}
    for measure, col in resolved_columns.items():
        if not col or col not in df.columns:
            measure_ranges[measure] = {}
            continue
        series = pd.to_numeric(df[col], errors="coerce")
        pct_null = round(series.isna().mean() * 100, 1)
        measure_ranges[measure] = {
            "column": col,
            "min":      round(float(series.min()), 2) if series.notna().any() else None,
            "max":      round(float(series.max()), 2) if series.notna().any() else None,
            "mean":     round(float(series.mean()), 2) if series.notna().any() else None,
            "pct_null": pct_null,
        }

    return LossRunSummaryStatistics(
        n_rows=len(df),
        n_unique_claims=n_unique_claims,
        origin_periods=origin_periods,
        eval_dates=eval_dates,
        measure_ranges=measure_ranges,
    )


# ---------------------------------------------------------------------------
# Convenience wrapper — run all checks at once
# ---------------------------------------------------------------------------

def validate_loss_run(
    df: pd.DataFrame,
    selected_measures: list[str],
) -> LossRunValidationResults:
    """
    Run all loss-run validation checks and return a results container.

    Args:
        df: The DataFrame loaded in step 1.
        selected_measures: List of measure keys confirmed by the user in step 4,
            e.g. ["incurred_losses", "paid_losses", "reported_counts"].
            Valid keys: "incurred_losses", "paid_losses", "reported_counts",
                        "closed_counts".

    Returns:
        LossRunValidationResults with raw findings from all eight checks.
    """
    claim   = check_claim_id_column(df)
    origin  = check_origin_period_column(df)
    fmt     = check_origin_period_format(df, origin.selected_column)
    measures = check_measure_columns(df, selected_measures)
    numeric = check_numeric_measures(df, measures.resolved)
    evdate  = check_eval_date_column(df)
    dupes   = check_duplicate_rows(df, claim.selected_column, evdate.selected_column)
    issues  = check_isolated_issues(df, measures.resolved)

    return LossRunValidationResults(
        claim_id=claim,
        origin_period=origin,
        origin_format=fmt,
        measure_columns=measures,
        numeric_measures=numeric,
        eval_date=evdate,
        duplicates=dupes,
        isolated_issues=issues,
    )
