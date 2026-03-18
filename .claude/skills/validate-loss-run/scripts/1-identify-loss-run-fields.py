"""
goal: Sub-step 1 of validate-loss-run — identify which fields are present in the loaded loss run.

Scans DataFrame column names against measure keyword patterns so the correct columns are used for validation and transformation.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional
import pandas as pd

# ---------------------------------------------------------------------------
# Measure keyword patterns (loss-run measures)
# ---------------------------------------------------------------------------

# Column-name patterns — used for loss run format
# (order matters: more-specific patterns are listed first)
_LOSS_RUN_MEASURE_RE: dict[str, re.Pattern] = {
    "claim_id":         re.compile(r"\b(claim|clm|file|case|suit|ref)\b.*\b(id|num|number|no\.?)\b"
                                   r"|\b(claim|clm)\b", re.IGNORECASE),
    "accident_date":    re.compile(r"\b(accident|acc(ident)?|date\s*of\s*loss|dol)\b.*\b(date|dt|yr|year|loss)\b"
                                   r"|\b(accident|acc(ident)?|date\s*of\s*loss|dol)\b", re.IGNORECASE),
    "closed_date":      re.compile(r"\b(close|closed|closed\s*date)\b.*\b(date|dt|yr|year)\b"
                                   r"|\b(close|closed|closed\s*date)\b", re.IGNORECASE),
    "origin_period":    re.compile(r"\b(origin|accident|org|ay|period)[\s_\-]?\d+", re.IGNORECASE),
    "eval_date":        re.compile(r"\b(eval|evaluation|as.?of|report(ing)?|val(uation)?)\b.*\b(date|dt|yr|year)\b"
                                   r"|\b(eval|evaluation|as.?of)\b", re.IGNORECASE),
    "dev_age":          re.compile(r"\b(dev(elopment)?[\s_\-]?(pd?|period|age|mon|mo|month|yr|year|\d+)"
                                   r"|(\d+\s*(mo|month|yr|year|mos|yrs))|age[\s_\-]?\d+)\b", re.IGNORECASE),
    "incurred_losses":  re.compile(r"\b(incurred?|incur)\b", re.IGNORECASE),
    "paid_losses":      re.compile(r"\b(paid|payment)\b", re.IGNORECASE),
    "case_reserve":     re.compile(r"\b(case|clm|file|case|suit|ref)\b.*\b(reserve|reserve\s*amount|reserve\s*value)\b"
                                   r"|\b(case|clm|file|case|suit|ref)\b", re.IGNORECASE),
    "reported_count":  re.compile(r"\b(report(ed)?|open)\b.*\b(count|cnt|claim|num|no)\b"
                                   r"|\b(reported?_count|rpt_cnt)\b", re.IGNORECASE),
    "closed_count":    re.compile(r"\b(clos(ed)?)\b.*\b(count|cnt|claim|num|no)\b"
                                   r"|\b(closed?_count|cls_cnt)\b", re.IGNORECASE),
    "open_count":      re.compile(r"\b(open)\b.*\b(count|cnt|claim|num|no)\b"
                                   r"|\b(open?_count|opn_cnt)\b", re.IGNORECASE),
    "claim_status":     re.compile(r"\b(status|status\s*of\s*claim)\b.*\b(open|closed|paid|unpaid|settled|resolved)\b"
                                   r"|\b(status|status\s*of\s*claim)\b", re.IGNORECASE),
}

# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class LossRunFields:
    """
    Result of guessing which loss run data elements are present.

    columns              — list of all column names
    column_matches       — measure → list of matching column names (loss run)
    
    """
    columns: list[str]
    column_matches: dict[str, list[str]]                  # measure → column names (loss run)

# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

def identify_loss_run_fields(sheet: pd.DataFrame) -> ElementGuess:
    """
    Scan a loaded file for evidence of each standard measure and classify.

    Args:
        sheets: A dictionary of DataFrames, keyed by sheet name.

    Returns:
        ElementGuess with guessed measures and column matches.
    """

    columns = sheet.columns.tolist()

    column_matches: dict[str, list[str]] = {m: [] for m in _LOSS_RUN_MEASURE_RE.keys()}
    for measure, pattern in _LOSS_RUN_MEASURE_RE.items():
        column_matches[measure] = [c for c in sheet.columns if pattern.search(c)]

    return LossRunFields(
        columns=columns,
        column_matches=column_matches,
    )
