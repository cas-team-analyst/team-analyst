"""
goal: Sub-step 2 of validate-loss-run — identify which fields are present in the loaded exposure.

Scans DataFrame column names against measure keyword patterns so the correct columns are used for validation and transformation.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional
import pandas as pd

# ---------------------------------------------------------------------------
# Measure keyword patterns (exposure measures)
# ---------------------------------------------------------------------------

# Column-name patterns — used for loss run format
# (order matters: more-specific patterns are listed first)
_EXPOSURE_MEASURE_RE: dict[str, re.Pattern] = {
    "origin_period":    re.compile(r"\b(origin|accident|org|ay|period)[\s_\-]?\d+", re.IGNORECASE),
    "premium":  re.compile(r"\b(premium|earned\s*premium)\b", re.IGNORECASE),
    "exposure": re.compile(r"\b(exposure|exposures)\b", re.IGNORECASE),
}

# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class ExposureFields:
    """
    Result of guessing which exposure data elements are present.

    column_matches       — measure → list of matching column names
    """
    column_matches: dict[str, list[str]]                  # measure → column names (loss run)

# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

def identify_exposure_fields(sheet: pd.DataFrame) -> ExposureFields:
    """
    Scan a loaded file for evidence of each standard measure and classify.

    Args:
        sheets: A dictionary of DataFrames, keyed by sheet name.

    Returns:
        ExposureFields with guessed measures and column matches.
    """

    column_matches: dict[str, list[str]] = {m: [] for m in _EXPOSURE_MEASURE_RE.keys()}
    for measure, pattern in _EXPOSURE_MEASURE_RE.items():
        column_matches[measure] = [c for c in sheet.columns if pattern.search(c)]

    return ExposureFields(
        column_matches=column_matches,
    )
