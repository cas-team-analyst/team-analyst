"""Boor Method 6: exponential decay of link-ratio development portions."""

from __future__ import annotations

import numpy as np

from p01_tail_math import improvement2_rescale_tail, ols_line


def _finite_ldf_slice(factors: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    f = np.asarray(factors, dtype=np.float64).ravel()
    d_all = f - 1.0
    mask = np.isfinite(f) & (f > 1.0) & (d_all > 1e-15)
    if int(np.sum(mask)) < 2:
        raise ValueError("Need at least two finite LDFs with positive development portion for exp-dev fit.")
    t = np.arange(1, f.size + 1, dtype=np.float64)[mask]
    d = d_all[mask]
    return t, d


def fit_exponential_dev_portion(
    factors: np.ndarray,
    *,
    mature_min_t: int | None = None,
    log_d_floor: float = 1e-12,
) -> tuple[float, float, np.ndarray, np.ndarray]:
    """
    Regress ln(d_t) on t (year index 1..). Returns (D, r, t_used, d_used).
    """
    t, d = _finite_ldf_slice(factors)
    if mature_min_t is not None:
        keep = t >= float(mature_min_t)
        t, d = t[keep], d[keep]
        if t.size < 2:
            raise ValueError("mature_min_t leaves fewer than two points.")
    y = np.log(np.maximum(d, log_d_floor))
    b0, b1 = ols_line(t, y)
    return float(np.exp(b0)), float(np.exp(b1)), t, d


def tail_exponential_quick(D: float, r: float, future_periods: int) -> float:
    """Quick tail: 1 + D * r^K / (1-r), |r|<1."""
    if not (0 < r < 1):
        raise ValueError("Quick formula requires 0 < r < 1.")
    if future_periods < 1:
        raise ValueError("future_periods must be at least 1.")
    return 1.0 + D * (r**future_periods) / (1.0 - r)


def tail_exponential_product(D: float, r: float, *, start_t: float, max_extra: int = 40, tol: float = 1e-6) -> float:
    """Multiply implied future link ratios 1 + D*r^t until (LDF-1) < tol."""
    tail = 1.0
    for k in range(1, max_extra + 1):
        t = start_t + float(k)
        dev = D * (r**t)
        if dev < tol:
            break
        tail *= 1.0 + dev
    return tail


def exponential_dev_tail_factor(
    factors: np.ndarray,
    *,
    mode: str = "quick",
    future_periods: int = 8,
    mature_min_t: int | None = None,
    exact_last: bool = False,
    product_tol: float = 1e-6,
) -> float:
    """
    Method 6 end-to-end. `mode`: 'quick' or 'product'.
    """
    f = np.asarray(factors, dtype=np.float64).ravel()
    last_idx_arr = np.where(np.isfinite(f))[0]
    if last_idx_arr.size == 0:
        raise ValueError("No finite link ratios for exponential dev tail.")
    last_idx = int(last_idx_arr[-1])
    t_global = float(last_idx + 1)
    d_last_act = float(f[last_idx] - 1.0)

    D, r, t_used, _ = fit_exponential_dev_portion(factors, mature_min_t=mature_min_t)
    last_t_fit = float(t_used[-1])

    if mode == "quick":
        tail = tail_exponential_quick(D, r, future_periods)
    elif mode == "product":
        tail = tail_exponential_product(D, r, start_t=last_t_fit, tol=product_tol)
    else:
        raise ValueError("mode must be 'quick' or 'product'.")

    if exact_last:
        d_fit_at_last_obs = float(D * (r**t_global))
        tail = improvement2_rescale_tail(tail, d_last_act, d_fit_at_last_obs)
    return tail
