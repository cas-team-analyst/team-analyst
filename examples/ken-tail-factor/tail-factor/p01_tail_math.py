"""Shared helpers for Boor-style tail estimation (regression, synthetic paths)."""

from __future__ import annotations

import numpy as np


def ols_line(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Unweighted OLS: y ~ b0 + b1 * x. Returns (intercept, slope)."""
    x = np.asarray(x, dtype=np.float64).ravel()
    y = np.asarray(y, dtype=np.float64).ravel()
    mask = np.isfinite(x) & np.isfinite(y)
    if int(np.sum(mask)) < 2:
        raise ValueError("Need at least two finite points for regression.")
    x = x[mask]
    y = y[mask]
    x_mean = float(np.mean(x))
    y_mean = float(np.mean(y))
    b1 = float(np.sum((x - x_mean) * (y - y_mean)) / np.sum((x - x_mean) ** 2))
    b0 = y_mean - b1 * x_mean
    return b0, b1


def last_finite_ldf(factors: np.ndarray) -> float:
    f = np.asarray(factors, dtype=np.float64).ravel()
    idx = np.where(np.isfinite(f))[0]
    if idx.size == 0:
        raise ValueError("No finite link ratios available for Bondy-style tail.")
    return float(f[idx[-1]])


def synthetic_cumulative_incrementals(factors: np.ndarray, base: float = 100.0) -> tuple[np.ndarray, np.ndarray]:
    """
    McClenahan-style synthetic paid path: cum[0]=base, cum[j]=cum[j-1]*f[j-1].
    inc[0]=cum[0], inc[j]=cum[j]-cum[j-1] for j>=1.
    """
    f = np.asarray(factors, dtype=np.float64).ravel()
    cum: list[float] = [float(base)]
    for j in range(f.size):
        if not np.isfinite(f[j]) or cum[-1] <= 0:
            break
        cum.append(cum[-1] * float(f[j]))
    c = np.array(cum, dtype=np.float64)
    inc = np.diff(c, prepend=c[0])
    inc[0] = c[0]
    return c, inc


def estimate_tail_ratio_incrementals(inc: np.ndarray, *, last_n: int = 5) -> float:
    """Mean of late incremental ratios inc[j]/inc[j-1] where ratio < 1 (McClenahan tail decay)."""
    inc = np.asarray(inc, dtype=np.float64).ravel()
    if inc.size < 3:
        raise ValueError("Need at least three incremental points to estimate decay.")
    ratios = inc[1:] / inc[:-1]
    ratios = ratios[np.isfinite(ratios) & (ratios > 0) & (ratios < 1.0)]
    if ratios.size == 0:
        raise ValueError("No decaying incremental ratios (<1) found for McClenahan r estimate.")
    k = min(last_n, int(ratios.size))
    tail = ratios[-k:]
    return float(np.mean(tail))


def incrementals_oldest_row(cumulative: np.ndarray) -> np.ndarray:
    """First row = oldest accident year; return positive finite incrementals along the row."""
    row = np.asarray(cumulative[0, :], dtype=np.float64).ravel()
    idx = np.where(np.isfinite(row))[0]
    if idx.size < 2:
        raise ValueError("Oldest row needs at least two finite cumulative values.")
    seg = row[idx[0] : idx[-1] + 1]
    inc = np.diff(seg, prepend=seg[0])
    inc[0] = seg[0]
    inc = inc[np.isfinite(inc) & (inc > 0)]
    if inc.size < 2:
        raise ValueError("Could not derive positive incrementals for Skurnick fit.")
    return inc


def improvement2_rescale_tail(tail_fitted: float, d_actual: float, d_fitted: float) -> float:
    """Boor Improvement 2: 1 + (d_actual/d_fitted)*(tail_fitted - 1)."""
    if d_fitted <= 0 or not np.isfinite(d_actual):
        raise ValueError("improvement2 requires positive d_fitted and finite d_actual.")
    return 1.0 + (d_actual / d_fitted) * (tail_fitted - 1.0)
