"""Boor Method 5: Skurnick simplification (log-linear fit to incremental paid, oldest AY)."""

from __future__ import annotations

import numpy as np

from p01_tail_math import incrementals_oldest_row, ols_line


def skurnick_tail_factor_from_incrementals(inc: np.ndarray) -> float:
    """
    Fit ln(inc_y) = ln(A) + y * ln(r), y = 1..Y (Boor / Skurnick).
    Closed form used in Boor's handout: tail = (1-r) / (1 - r - r^n) with n = Y.
    """
    inc = np.asarray(inc, dtype=np.float64).ravel()
    y = np.arange(1, inc.size + 1, dtype=np.float64)
    b0, b1 = ols_line(y, np.log(inc))
    r = float(np.exp(b1))
    if not (0 < r < 1):
        raise ValueError("Skurnick fit requires decay r in (0,1); check incrementals and maturity window.")
    n = int(inc.size)
    den = 1.0 - r - r**n
    if den <= 0:
        raise ValueError("Skurnick denominator non-positive; r and n incompatible with this tail form.")
    return float((1.0 - r) / den)


def skurnick_tail_factor_from_triangle(cumulative: np.ndarray) -> float:
    inc = incrementals_oldest_row(cumulative)
    return skurnick_tail_factor_from_incrementals(inc)
