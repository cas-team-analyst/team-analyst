"""Map explicit tail-method names to a scalar tail multiplier for chain_ladder.project_triangle."""

from __future__ import annotations

from typing import Any

import numpy as np

from p02a_tail_bondy import bondy_tail_factor, modified_bondy_tail_factor
from p02b_tail_exponential_dev import exponential_dev_tail_factor
from p02c_tail_mcclenahan import mcclenahan_tail_from_factors
from p02d_tail_skurnick import skurnick_tail_factor_from_triangle

TAIL_METHODS = (
    "none",
    "scalar",
    "bondy",
    "modified_bondy",
    "mcclenahan_paid",
    "skurnick_paid",
    "exp_dev_ldf",
)


def resolve_tail_multiplier(
    method: str,
    factors: np.ndarray,
    cumulative_triangle: np.ndarray,
    **kwargs: Any,
) -> float:
    """
    No default path: caller must pass a valid `method` from TAIL_METHODS.
    `scalar` requires kwargs['tail_scalar'].
    """
    m = method.lower().strip()
    if m not in TAIL_METHODS:
        raise ValueError(f"Unknown tail method {method!r}; choose one of {TAIL_METHODS}.")

    if m == "none":
        return 1.0
    if m == "scalar":
        s = kwargs.get("tail_scalar")
        if s is None:
            raise ValueError("tail_method 'scalar' requires tail_scalar.")
        s = float(s)
        if s <= 0:
            raise ValueError("tail_scalar must be positive.")
        return s
    if m == "bondy":
        return bondy_tail_factor(factors)
    if m == "modified_bondy":
        mode = kwargs.get("modified_bondy_mode", "double_dev")
        return modified_bondy_tail_factor(factors, mode=str(mode))
    if m == "mcclenahan_paid":
        mm = kwargs.get("m_months")
        am = kwargs.get("a_months")
        if mm is None or am is None:
            raise ValueError("mcclenahan_paid requires m_months and a_months.")
        return mcclenahan_tail_from_factors(
            factors,
            m_months=float(mm),
            a_months=float(am),
            last_n_ratios=int(kwargs.get("mcclenahan_last_n", 5)),
        )
    if m == "skurnick_paid":
        return skurnick_tail_factor_from_triangle(cumulative_triangle)
    if m == "exp_dev_ldf":
        return exponential_dev_tail_factor(
            factors,
            mode=str(kwargs.get("exp_dev_mode", "quick")),
            future_periods=int(kwargs.get("exp_future_periods", 8)),
            mature_min_t=kwargs.get("exp_mature_min_t"),
            exact_last=bool(kwargs.get("exp_exact_last", False)),
            product_tol=float(kwargs.get("exp_product_tol", 1e-6)),
        )
    raise ValueError(f"Unhandled tail method {m!r}.")
