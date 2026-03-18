"""
goal: Step 3 of identify-format — run a tab-only diagnostic on loaded data.

Returns raw findings: tab count, tab names, and which tab names match
loss-run, exposure, or triangle patterns. The agent uses these to guess
the data format.
"""

import re
from dataclasses import dataclass
import pandas as pd


# ---------------------------------------------------------------------------
# Tab-name regex patterns
# ---------------------------------------------------------------------------

# Tab/sheet names that indicate loss run (claim) data
_LOSS_RUN_RE = re.compile(
    r"\b(loss\s*run|lossrun|claim|claims|loss(es)?|loss\s*data|claim\s*data)\b",
    re.IGNORECASE,
)

# Tab/sheet names that indicate exposure (premium/exposure) data
_EXPOSURE_RE = re.compile(
    r"\b(exposure|exposures|premium|earned\s*premium|exposure\s*data|premium\s*data)\b",
    re.IGNORECASE,
)

# Tab/sheet names that indicate triangle data
# (order matters: more-specific patterns are listed first)
_TRIANGLE_RE: dict[str, re.Pattern] = {
    "incurred_losses":  re.compile(r"\b(incurred?|incur)\b", re.IGNORECASE),
    "paid_losses":      re.compile(r"\b(paid|payment)\b", re.IGNORECASE),
    "reported_counts":  re.compile(r"\b(report(ed)?|open)\b.*\b(count|cnt|claim|num|no)\b"
                                   r"|\b(reported?_count|rpt_cnt)\b", re.IGNORECASE),
    "closed_counts":    re.compile(r"\b(clos(ed)?)\b.*\b(count|cnt|claim|num|no)\b"
                                   r"|\b(closed?_count|cls_cnt)\b", re.IGNORECASE),
}

# ---------------------------------------------------------------------------
# Result dataclass — raw findings only
# ---------------------------------------------------------------------------

@dataclass
class TabCheckResults:
    """Tab-only format check: count, names, and which names match loss-run/exposure/triangle patterns."""
    tab_count: int
    tab_names: list[str]
    tabs_matching_loss_run: list[str]
    tabs_matching_exposure: list[str]
    tabs_matching_triangle: list[str]


def identify_tabs(sheets: dict[str, pd.DataFrame]) -> TabCheckResults:
    """
    Run the tab-only format check and return raw findings.

    Args:
        sheets: Map of tab/sheet name to DataFrame (e.g. from load_data).

    Returns:
        TabCheckResults with tab_count, tab_names, and tabs_matching_* lists.
    """
    if not sheets:
        raise ValueError("No sheets found in sheets dict")

    tab_names = list(sheets.keys())
    tab_count = len(tab_names)

    tabs_matching_loss_run = [name for name in tab_names if _LOSS_RUN_RE.search(name)]
    tabs_matching_exposure = [name for name in tab_names if _EXPOSURE_RE.search(name)]

    tabs_matching_triangle: dict[str, list[str]] = {m: [] for m in _TRIANGLE_RE.keys()}
    for measure, pattern in _TRIANGLE_RE.items():
        tabs_matching_triangle[measure] = [name for name in tab_names if pattern.search(name)]

    return TabCheckResults(
        tab_count=tab_count,
        tab_names=tab_names,
        tabs_matching_loss_run=tabs_matching_loss_run,
        tabs_matching_exposure=tabs_matching_exposure,
        tabs_matching_triangle=tabs_matching_triangle,
    )
