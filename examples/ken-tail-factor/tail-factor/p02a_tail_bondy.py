"""Boor Methods 1-2: Bondy and Modified Bondy tail factors."""

from __future__ import annotations

import numpy as np

from p01_tail_math import last_finite_ldf


def bondy_tail_factor(factors: np.ndarray) -> float:
    """Method 1: tail = last credible link ratio."""
    return last_finite_ldf(factors)


def modified_bondy_tail_factor(factors: np.ndarray, *, mode: str = "double_dev") -> float:
    """
    Method 2: double the development portion (1+2d) or square the full ratio.
    `mode`: 'double_dev' or 'square_ratio'.
    """
    last = last_finite_ldf(factors)
    d = last - 1.0
    if mode == "double_dev":
        return 1.0 + 2.0 * d
    if mode == "square_ratio":
        return last * last
    raise ValueError("mode must be 'double_dev' or 'square_ratio'.")
