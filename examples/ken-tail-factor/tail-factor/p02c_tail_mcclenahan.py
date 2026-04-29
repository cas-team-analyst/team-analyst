"""Boor Method 4: McClenahan exponential decay on incremental paid (synthetic path from LDFs)."""

from __future__ import annotations

import numpy as np

from p01_tail_math import estimate_tail_ratio_incrementals, synthetic_cumulative_incrementals


def mcclenahan_tail_factor_closed_form(r_annual: float, m_months: float, a_months: float) -> float:
    """
    Tail = 12q / (12q - p^(m-a-10) * (1 - p^12)), p = r^(1/12), q = 1-p.
    Requires denominator > 0 and 0 < r < 1.
    """
    if not (0 < r_annual < 1):
        raise ValueError("McClenahan requires 0 < r_annual < 1.")
    p = float(r_annual ** (1.0 / 12.0))
    q = 1.0 - p
    expo = m_months - a_months - 10.0
    num = 12.0 * q
    adj = (p**expo) * (1.0 - p**12)
    den = num - adj
    if den <= 0:
        raise ValueError("McClenahan denominator non-positive; check m_months, a_months, and r_annual.")
    return num / den


def mcclenahan_tail_from_factors(
    factors: np.ndarray,
    *,
    m_months: float,
    a_months: float,
    base: float = 100.0,
    last_n_ratios: int = 5,
) -> float:
    """Estimate r from synthetic incrementals, then closed-form tail."""
    _, inc = synthetic_cumulative_incrementals(factors, base=base)
    r = estimate_tail_ratio_incrementals(inc, last_n=last_n_ratios)
    return mcclenahan_tail_factor_closed_form(r, m_months, a_months)
