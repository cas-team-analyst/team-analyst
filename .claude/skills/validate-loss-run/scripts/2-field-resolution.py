"""
goal: Sub-steps 2-4 of validate-loss-run — encode rules for required empty,
ambiguous, and conflicting fields; build confirmed_measures from working mapping.

The agent (SKILL.md) calls these functions and handles presentation and user input.
Python owns: what is missing / ambiguous / conflicting and what is confirmed_measures.
"""

from __future__ import annotations

from typing import Optional

# ---------------------------------------------------------------------------
# Constants (from SKILL.md rules)
# ---------------------------------------------------------------------------

# Measures that must have at least one column; if none, agent must ask user.
REQUIRED_ALONE: tuple[str, ...] = ("claim_id",)

# Sets where at least one measure must have a column (all empty => agent asks for at least one in set).
REQUIRED_SETS: tuple[tuple[str, ...], ...] = (
    ("accident_date", "origin_period"),
    ("eval_date", "dev_age"),
    ("incurred_losses", "paid_losses", "reported_count", "closed_count"),
)

# Ambiguous: more than one match => user chooses "sum all" or "select one", then column if select one.
AMBIGUOUS_SUM_OR_SELECT: tuple[str, ...] = (
    "incurred_losses",
    "paid_losses",
    "case_reserve",
)

# Ambiguous: more than one match => user must select one column.
AMBIGUOUS_SELECT_ONE: tuple[str, ...] = (
    "claim_id",
    "origin_period",
    "eval_date",
    "dev_age",
    "reported_count",
    "closed_count",
    "open_count",
    "claim_status",
)

# Conflict: all non-empty => user picks exactly one from set.
SINGLE_CHOICE_SETS: tuple[tuple[str, ...], ...] = (
    ("accident_date", "origin_period"),
    ("eval_date", "dev_age"),
    ("closed_date", "claim_status", "closed_count"),
)

# Conflict: all non-empty => user picks exactly two from set.
TWO_CHOICE_SETS: tuple[tuple[str, ...], ...] = (
    ("incurred_losses", "paid_losses", "case_reserve"),
    ("reported_count", "closed_count", "open_count"),
)

# ---------------------------------------------------------------------------
# Resolved view: merge column_matches with working_mapping
# ---------------------------------------------------------------------------


def resolved_columns(
    column_matches: dict[str, list[str]],
    working_mapping: dict[str, str],
) -> dict[str, list[str]]:
    """
    For each measure: if in working_mapping with non-empty value, return that single column;
    else return column_matches for that measure (list, possibly empty).
    """
    out: dict[str, list[str]] = {}
    all_measures = set(column_matches) | set(working_mapping)
    for m in all_measures:
        if m in working_mapping and (working_mapping[m] or "").strip():
            out[m] = [working_mapping[m].strip()]
        else:
            out[m] = list(column_matches.get(m, []))
    return out


# ---------------------------------------------------------------------------
# Required empty
# ---------------------------------------------------------------------------


def get_required_empty(
    column_matches: dict[str, list[str]],
    working_mapping: dict[str, str],
) -> dict[str, list[str] | list[tuple[str, ...]]]:
    """
    Returns what the agent must still resolve for "required" fields.

    - required_alone: list of measure keys that must have a column but currently have none.
    - required_sets: list of tuples (set of measure keys) where every measure in the set
      has no column; agent must get at least one from each set.
    """
    resolved = resolved_columns(column_matches, working_mapping)

    required_alone: list[str] = []
    for m in REQUIRED_ALONE:
        if not resolved.get(m):
            required_alone.append(m)

    required_sets: list[tuple[str, ...]] = []
    for s in REQUIRED_SETS:
        if all(not resolved.get(m) for m in s):
            required_sets.append(s)

    return {"required_alone": required_alone, "required_sets": required_sets}


# ---------------------------------------------------------------------------
# Ambiguous (more than one column)
# ---------------------------------------------------------------------------


def get_ambiguous(
    column_matches: dict[str, list[str]],
    working_mapping: dict[str, str],
) -> dict[str, dict[str, list[str]]]:
    """
    Returns measures that have more than one resolved column, split by handling type.

    - sum_or_select: measure -> list of column names (user may "sum all" or "select one").
    - select_one: measure -> list of column names (user must select one).
    """
    resolved = resolved_columns(column_matches, working_mapping)

    sum_or_select: dict[str, list[str]] = {}
    select_one: dict[str, list[str]] = {}

    for m in AMBIGUOUS_SUM_OR_SELECT:
        cols = resolved.get(m) or []
        if len(cols) > 1:
            sum_or_select[m] = cols

    for m in AMBIGUOUS_SELECT_ONE:
        cols = resolved.get(m) or []
        if len(cols) > 1:
            select_one[m] = cols

    return {"sum_or_select": sum_or_select, "select_one": select_one}


# ---------------------------------------------------------------------------
# Conflict sets (all non-empty => user must choose)
# ---------------------------------------------------------------------------


def get_conflict_sets(
    column_matches: dict[str, list[str]],
    working_mapping: dict[str, str],
) -> dict[str, list[tuple[str, ...]]]:
    """
    Returns sets that are "all non-empty" and thus need user to choose.

    - single_choice: list of tuples (measure keys); user picks exactly one measure from each.
    - two_choice: list of tuples; user picks exactly two measures from each.
    """
    resolved = resolved_columns(column_matches, working_mapping)

    single_choice: list[tuple[str, ...]] = []
    for s in SINGLE_CHOICE_SETS:
        if all((resolved.get(m) or []) for m in s):
            single_choice.append(s)

    two_choice: list[tuple[str, ...]] = []
    for s in TWO_CHOICE_SETS:
        if all((resolved.get(m) or []) for m in s):
            two_choice.append(s)

    return {"single_choice": single_choice, "two_choice": two_choice}


# ---------------------------------------------------------------------------
# Build confirmed_measures for validate_loss_run
# ---------------------------------------------------------------------------


def build_confirmed_measures(working_mapping: dict[str, str]) -> list[str]:
    """
    Returns the list of measure keys that have a non-empty column in working_mapping.
    Pass this as selected_measures to validate_loss_run.
    Conflict resolution is already reflected in working_mapping (agent drops non-selected).
    """
    return [m for m, col in working_mapping.items() if col and str(col).strip()]


# ---------------------------------------------------------------------------
# Ready for validation?
# ---------------------------------------------------------------------------


def is_ready_for_validation(
    column_matches: dict[str, list[str]],
    working_mapping: dict[str, str],
) -> bool:
    """
    True when there is nothing left to resolve: no required empty, no ambiguous,
    no conflict sets. Agent can then proceed to Sub-step 5.
    """
    req = get_required_empty(column_matches, working_mapping)
    if req["required_alone"] or req["required_sets"]:
        return False

    amb = get_ambiguous(column_matches, working_mapping)
    if amb["sum_or_select"] or amb["select_one"]:
        return False

    conflicts = get_conflict_sets(column_matches, working_mapping)
    if conflicts["single_choice"] or conflicts["two_choice"]:
        return False

    return True
