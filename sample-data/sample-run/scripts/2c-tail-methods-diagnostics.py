# Computes tail factor scenarios for all measures using multiple methods and starting ages.
# Produces tail-scenarios.parquet with diagnostics for selector agents and actuary review.

"""
goal: Compute tail factor scenarios (all methods × starting ages × measures).

inputs:
    ../processed-data/1_triangles.parquet   - Cumulative triangle data
    ../processed-data/2_enhanced.parquet    - Age-to-age factors with weights
    ../processed-data/4_ldf_averages.parquet - Weighted avg LDFs per interval
    ../selections/Chain Ladder Selections - LDFs.xlsx - Selected LDFs

outputs:
    ../processed-data/tail-scenarios.parquet

run-note: When copied to a project, run from the scripts/ directory:
    cd scripts/
    python 2c-tail-methods-diagnostics.py
"""

import json
import math
import numpy as np
import pandas as pd
from pathlib import Path

from modules import config

# Paths from modules/config.py — override here if needed:
INPUT_TRIANGLES = config.PROCESSED_DATA + "1_triangles.parquet"
INPUT_ENHANCED  = config.PROCESSED_DATA + "2_enhanced.parquet"
INPUT_AVERAGES  = config.PROCESSED_DATA + "4_ldf_averages.parquet"
INPUT_EXCEL     = config.SELECTIONS + "Chain Ladder Selections - LDFs.xlsx"
OUTPUT_PATH     = config.PROCESSED_DATA + "tail-scenarios.parquet"

# Minimum starting age by triangle type
AGE_MINIMUMS = {
    "Paid Loss":      60,
    "Closed Count":   60,
    "Incurred Loss":  48,
    "Reported Count": 48,
}
DEFAULT_AGE_MIN = 48

GAP_THRESHOLD = 0.005
MATERIALITY_THRESHOLD = 0.1  # % of CDF
EXP_DEV_K = 8                # future periods for exp_dev_quick infinite-sum approximation


# ── Excel reading ─────────────────────────────────────────────────────────────

import re as _re
_INTERVAL_RE = _re.compile(r'^\d+-\d+$')


def _is_interval_row(row_series):
    vals = [str(v).strip() for v in row_series.iloc[1:] if pd.notna(v) and str(v).strip()]
    matches = sum(1 for v in vals if _INTERVAL_RE.match(v) or v.lower() == 'tail')
    return matches >= 3


def _find_interval_row_above(df, row_idx, max_scan=20):
    for offset in range(1, min(max_scan, row_idx + 1)):
        candidate = df.iloc[row_idx - offset]
        if _is_interval_row(candidate):
            return candidate
    return None


def _read_labeled_selections(df, label):
    mask = df.iloc[:, 0].astype(str).str.strip() == label
    indices = df[mask].index
    if len(indices) == 0:
        return {}
    row_idx = indices[0]
    sel_row = df.iloc[row_idx]
    interval_row = _find_interval_row_above(df, row_idx)
    if interval_row is None:
        return {}
    selections = {}
    for col_idx in range(1, len(sel_row)):
        interval = interval_row.iloc[col_idx]
        val = sel_row.iloc[col_idx]
        if pd.notna(interval) and pd.notna(val):
            try:
                selections[str(interval).strip()] = float(val)
            except (ValueError, TypeError):
                pass
    return selections


def read_selections(excel_path, measure):
    """Read selected LDFs for a measure. Error if no selections. Returns {interval: ldf} without Tail.
    Priority: 'User Selection' → 'Selection' (rules-based AI) → 'AI Selection' (open-ended AI)."""
    try:
        df = pd.read_excel(excel_path, sheet_name=measure, engine='openpyxl',
                           engine_kwargs={'data_only': True})
        for label in ("User Selection", "Rules-Based AI Selection", "Open-Ended AI Selection"):
            sels = _read_labeled_selections(df, label)
            sels_no_tail = {k: v for k, v in sels.items() if k.lower() != 'tail'}
            if sels_no_tail:
                print(f"  Read {len(sels_no_tail)} LDF selections for {measure} (row: '{label}')")
                return sels_no_tail
        raise ValueError(f"No selection row with values found for '{measure}'")
    except ValueError:
        raise
    except Exception as e:
        raise RuntimeError(f"Could not read selections for {measure}: {e}") from e


# ── Interval and age utilities ────────────────────────────────────────────────

def parse_interval(interval):
    """Parse '60-72' → (60, 72)."""
    parts = str(interval).split('-')
    return int(parts[0]), int(parts[1])


def get_all_start_ages(selections):
    """Sorted list of all interval start ages from selections dict."""
    ages = set()
    for interval in selections:
        try:
            start, _ = parse_interval(interval)
            ages.add(start)
        except (ValueError, AttributeError):
            pass
    return sorted(ages)


def intervals_from_starting_age(selections, starting_age):
    """
    Return [(interval_str, ldf), ...] for intervals with start_age >= starting_age, sorted.
    """
    result = []
    for interval, ldf in selections.items():
        try:
            start, _ = parse_interval(interval)
            if start >= starting_age:
                result.append((start, interval, ldf))
        except (ValueError, AttributeError):
            pass
    result.sort(key=lambda x: x[0])
    return [(r[1], r[2]) for r in result]


def get_cutoff_age(selections):
    """Find the tail cutoff age from the last selected LDF interval."""
    all_ages = get_all_start_ages(selections)
    if not all_ages:
        return None
    max_start = max(all_ages)
    for interval in selections:
        start, end = parse_interval(interval)
        if start == max_start:
            return end
    return None


def get_all_ata_stats(df_enhanced, measure):
    """Compute min, max, avg, slope, CV over all empirical ATAs for context."""
    df_m = df_enhanced[df_enhanced['measure'].astype(str) == measure]
    if df_m.empty:
        return {'min': None, 'max': None, 'avg': None, 'slope': None, 'cv': None}
    
    # We want these stats per interval, or across all intervals?
    # "we should restate the averages slope and cv as context for sleection (add to excel and md) and also add min/max becuse the fitted values would ideally stauy within the min and max of the age to age factors"
    # Wait, the min and max of the age-to-age factors.
    # The LDF selector sees averages for each interval. The tail selector should probably see the min/max of the averages?
    # Or the min/max of ALL individual ATAs? "min and max of the age to age factors"
    
    # Just return overall min/max of the ATAs? Or min/max of the averages?
    # Usually "min and max of the age to age factors" means the min and max of the *averages* so the fitted curve doesn't go crazy. Let's just calculate the min/max of the weighted averages since that's what's modeled.
    return {}



# ── WLS curve fitting ─────────────────────────────────────────────────────────

def _wls_linear(t_vals, y_vals, weights):
    """WLS fit y = a + b*t. Returns (a, b) or None."""
    valid = [(t, y, w) for t, y, w in zip(t_vals, y_vals, weights)
             if np.isfinite(y) and w > 0]
    if len(valid) < 2:
        valid = [(t, y, 1.0) for t, y, w in zip(t_vals, y_vals, weights) if np.isfinite(y)]
    if len(valid) < 2:
        return None

    tv = np.array([v[0] for v in valid], dtype=float)
    yv = np.array([v[1] for v in valid], dtype=float)
    wv = np.sqrt(np.array([v[2] for v in valid], dtype=float))

    A = np.column_stack([np.ones_like(tv), tv]) * wv[:, None]
    b = yv * wv
    try:
        coeffs, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
        return float(coeffs[0]), float(coeffs[1])
    except Exception:
        return None


def _wls_quadratic(t_vals, y_vals, weights):
    """WLS fit y = b0 + b1*t + b2*t^2. Returns (b0, b1, b2) or None."""
    valid = [(t, y, w) for t, y, w in zip(t_vals, y_vals, weights)
             if np.isfinite(y) and w > 0]
    if len(valid) < 3:
        valid = [(t, y, 1.0) for t, y, w in zip(t_vals, y_vals, weights) if np.isfinite(y)]
    if len(valid) < 3:
        return None

    tv = np.array([v[0] for v in valid], dtype=float)
    yv = np.array([v[1] for v in valid], dtype=float)
    wv = np.sqrt(np.array([v[2] for v in valid], dtype=float))

    A = np.column_stack([np.ones_like(tv), tv, tv**2]) * wv[:, None]
    b = yv * wv
    try:
        coeffs, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
        return float(coeffs[0]), float(coeffs[1]), float(coeffs[2])
    except Exception:
        return None


def _fit_exp_dev(factors, weights):
    """
    Fit ln(d_t) = ln(D) + t*ln(r) with WLS on factors and weights.
    Returns (D, r) or None. d_t = factor_t - 1.
    """
    d_vals = [f - 1 for f in factors]
    log_d = [np.log(d) if d > 0 else np.nan for d in d_vals]
    t_vals = list(range(len(factors)))
    result = _wls_linear(t_vals, log_d, weights)
    if result is None:
        return None
    a, b = result
    D, r = np.exp(a), np.exp(b)
    return (float(D), float(r)) if r > 0 else None


def _fit_double_exp(factors, weights):
    """
    Fit ln(d_t) = b0 + b1*t + b2*t^2 with WLS.
    Returns (b0, b1, b2) or None.
    """
    d_vals = [f - 1 for f in factors]
    log_d = [np.log(d) if d > 0 else np.nan for d in d_vals]
    t_vals = list(range(len(factors)))
    return _wls_quadratic(t_vals, log_d, weights)


def _r_squared_log_d(factors, fitted_log_d_vals):
    """R² on ln(factor-1) scale. fitted_log_d_vals aligned to positive-d factors."""
    d_vals = [f - 1 for f in factors]
    obs = [np.log(d) for d in d_vals if d > 0]
    if len(obs) < 2 or len(obs) != len(fitted_log_d_vals):
        return None
    obs_arr = np.array(obs)
    fit_arr = np.array(fitted_log_d_vals)
    ss_res = np.sum((obs_arr - fit_arr) ** 2)
    ss_tot = np.sum((obs_arr - np.mean(obs_arr)) ** 2)
    return float(1 - ss_res / ss_tot) if ss_tot > 0 else None


# ── Tail methods ──────────────────────────────────────────────────────────────

def tail_bondy(factors):
    return float(factors[-1]) if factors else None


def tail_modified_bondy_double_dev(factors):
    if not factors:
        return None
    d = factors[-1] - 1
    return float(1 + 2 * d)


def tail_modified_bondy_square_ratio(factors):
    return float(factors[-1] ** 2) if factors else None


def tail_exp_dev_quick(factors, weights, K=EXP_DEV_K):
    params = _fit_exp_dev(factors, weights)
    if params is None:
        return None, None
    D, r = params
    if not (0 < r < 1):
        return None, None
    tail = 1 + D * (r ** K) / (1 - r)
    return float(tail), params


def tail_exp_dev_quick_exact_last(factors, weights, K=EXP_DEV_K):
    """Boor Improvement 2: 1 + (d_actual/d_fitted) * (tail_fitted - 1)."""
    params = _fit_exp_dev(factors, weights)
    if params is None:
        return None, None
    D, r = params
    if not (0 < r < 1):
        return None, None
    n = len(factors)
    tail_fitted = 1 + D * (r ** K) / (1 - r)
    # Rescale at last observed interval
    last_t = n - 1
    d_actual = factors[last_t] - 1
    d_fitted = D * (r ** last_t)
    if d_fitted <= 0 or d_actual <= 0:
        return float(tail_fitted), params
    rescale = d_actual / d_fitted
    return float(1 + rescale * (tail_fitted - 1)), params


def tail_exp_dev_product(factors, weights):
    params = _fit_exp_dev(factors, weights)
    if params is None:
        return None, None
    D, r = params
    if not (0 < r < 1):
        return None, None
    n = len(factors)
    tail = 1.0
    for t in range(n, n + 10000):
        dev = D * (r ** t)
        if dev < 1e-6:
            break
        tail *= (1 + dev)
    return float(tail), params


def tail_double_exp(factors, weights):
    params = _fit_double_exp(factors, weights)
    if params is None:
        return None, None
    b0, b1, b2 = params
    if b2 >= 0:
        return None, None  # Quadratic diverges → infinite tail
    n = len(factors)
    tail = 1.0
    for t in range(n, n + 10000):
        dev = np.exp(b0 + b1 * t + b2 * t ** 2)
        if dev < 1e-6:
            break
        tail += dev
    return float(tail), params


def tail_mcclenahan(factors, max_age):
    """McClenahan closed-form tail."""
    if len(factors) < 3:
        return None, None

    m_months = max_age + 12
    a_months = 6

    cum = [100.0]
    for f in factors:
        cum.append(cum[-1] * f)

    incs = [cum[i + 1] - cum[i] for i in range(len(cum) - 1)]
    if len(incs) < 2:
        return None, None

    ratios = []
    for i in range(1, len(incs)):
        if incs[i - 1] > 0:
            ratio = incs[i] / incs[i - 1]
            if ratio < 1:
                ratios.append(ratio)

    if not ratios:
        return None, None

    sample = ratios[-5:] if len(ratios) >= 5 else ratios
    r = float(np.mean(sample))
    if not (0 < r < 1):
        return None, None

    p = r ** (1 / 12)
    q = 1 - p
    exp = m_months - a_months - 10
    denom = 12 * q - (p ** exp) * (1 - p ** 12)
    if abs(denom) < 1e-12:
        return None, None

    tail = 12 * q / denom
    if not (tail > 1 and np.isfinite(tail)):
        return None, None
    return float(tail), {'r': r}


def tail_skurnick(cum_2d):
    """
    Skurnick tail from oldest AY incrementals.
    cum_2d: 2D array, oldest AY = row 0, columns = ages from starting_age onward.
    Returns (tail, params) or (None, None).
    """
    if cum_2d is None or cum_2d.shape[0] == 0:
        return None, None

    oldest = cum_2d[0]
    incs = []
    for i in range(len(oldest) - 1):
        if np.isfinite(oldest[i]) and np.isfinite(oldest[i + 1]) and oldest[i] > 0:
            inc = oldest[i + 1] - oldest[i]
            if inc > 0:
                incs.append(float(inc))

    if len(incs) < 2:
        return None, None

    y_vals = np.arange(len(incs), dtype=float)
    log_incs = np.log(np.array(incs))
    A_mat = np.column_stack([np.ones_like(y_vals), y_vals])
    try:
        coeffs, _, _, _ = np.linalg.lstsq(A_mat, log_incs, rcond=None)
        ln_A, ln_r = coeffs
    except Exception:
        return None, None

    r = float(np.exp(ln_r))
    if not (0 < r < 1):
        return None, None

    n = len(incs)
    denom = 1 - r - r ** n
    if abs(denom) < 1e-10:
        return None, None
    tail = (1 - r) / denom
    if not (tail > 1 and np.isfinite(tail)):
        return None, None
    return float(tail), {'r': r, 'A': float(np.exp(ln_A)), 'n': n}


# ── Per-AY weight lookup ──────────────────────────────────────────────────────

def build_ay_weights(df_enhanced, measure, intervals_from_start):
    """
    Return {period: [weight_per_interval_t]} for AY LOO.
    Weight at interval t = df_enhanced weight for (period, interval).
    """
    df_m = df_enhanced[df_enhanced['measure'].astype(str) == measure]
    result = {}
    for period in df_m['period'].astype(str).unique():
        row_weights = []
        for interval, _ in intervals_from_start:
            mask = (df_m['period'].astype(str) == period) & \
                   (df_m['interval'].astype(str) == str(interval))
            w_vals = df_m[mask]['weight'].dropna()
            row_weights.append(float(w_vals.iloc[0]) if not w_vals.empty else 0.0)
        result[period] = row_weights
    return result


def aggregate_weights(ay_weights, intervals_from_start):
    """Sum weights across all AYs per interval."""
    n = len(intervals_from_start)
    total = [0.0] * n
    for row_weights in ay_weights.values():
        for t, w in enumerate(row_weights):
            total[t] += w
    return total


def loo_weights_excluding(ay_weights, exclude_period, total_weights):
    """Total weights with exclude_period removed."""
    excl = ay_weights.get(exclude_period, [0.0] * len(total_weights))
    return [max(total_weights[t] - excl[t], 0.0) for t in range(len(total_weights))]


# ── Diagnostics ───────────────────────────────────────────────────────────────

def starting_point_diagnostics(df_enhanced, measure, starting_age, selections):
    intervals_start = intervals_from_starting_age(selections, starting_age)
    n_factors = len(intervals_start)
    factors = [ldf for _, ldf in intervals_start]

    # n_ay_contributing: AYs with data at starting_age
    df_m = df_enhanced[df_enhanced['measure'].astype(str) == measure]
    # age column may be categorical/string
    age_str = str(starting_age)
    df_at_age = df_m[df_m['age'].astype(str) == age_str]
    n_ay = int(df_at_age['period'].nunique())

    # is_monotone_from_here
    is_monotone = all(factors[i] >= factors[i + 1] for i in range(len(factors) - 1)) \
        if len(factors) > 1 else True

    # cv_at_starting_age: CV of individual AY ldfs at the first interval from starting_age
    cv = None
    if intervals_start:
        first_interval = intervals_start[0][0]
        df_int = df_m[df_m['interval'].astype(str) == str(first_interval)]
        ldf_vals = df_int['ldf'].dropna()
        if len(ldf_vals) >= 2 and ldf_vals.mean() != 0:
            cv = float(ldf_vals.std() / ldf_vals.mean())

    # slope_sign_changes
    sign_changes = 0
    if len(factors) > 2:
        diffs = [factors[i + 1] - factors[i] for i in range(len(factors) - 1)]
        for i in range(len(diffs) - 1):
            if diffs[i] * diffs[i + 1] < 0:
                sign_changes += 1

    return {
        'n_factors_in_fit': n_factors,
        'n_ay_contributing': n_ay,
        'is_monotone_from_here': bool(is_monotone),
        'cv_at_starting_age': cv,
        'slope_sign_changes': sign_changes,
    }


def fit_diagnostics_exp_dev(factors, weights, ay_weights, total_weights, params, K=EXP_DEV_K):
    if params is None:
        return _empty_fit_diag()
    D, r = params
    n = len(factors)

    # R²
    fitted_log_d = [float(np.log(D * r ** t)) for t in range(n) if (factors[t] - 1) > 0]
    r2 = _r_squared_log_d(factors, fitted_log_d)

    # Residuals
    resid = {}
    for t in range(n):
        d = factors[t] - 1
        if d > 0:
            resid[str(t)] = float(np.log(d) - np.log(D * r ** t))

    # AY LOO
    loo_tails = []
    for period, _ in ay_weights.items():
        loo_w = loo_weights_excluding(ay_weights, period, total_weights)
        p = _fit_exp_dev(factors, loo_w)
        if p and 0 < p[1] < 1:
            D_l, r_l = p
            loo_tails.append(1 + D_l * (r_l ** K) / (1 - r_l))

    return _loo_result(r2, resid, loo_tails)


def fit_diagnostics_double_exp(factors, weights, ay_weights, total_weights, params):
    if params is None:
        return _empty_fit_diag()
    b0, b1, b2 = params
    n = len(factors)

    fitted_log_d = [float(b0 + b1 * t + b2 * t ** 2) for t in range(n) if (factors[t] - 1) > 0]
    r2 = _r_squared_log_d(factors, fitted_log_d)

    resid = {}
    for t in range(n):
        d = factors[t] - 1
        if d > 0:
            resid[str(t)] = float(np.log(d) - (b0 + b1 * t + b2 * t ** 2))

    loo_tails = []
    for period in ay_weights:
        loo_w = loo_weights_excluding(ay_weights, period, total_weights)
        p = _fit_double_exp(factors, loo_w)
        if p:
            b0l, b1l, b2l = p
            tail_l = 1.0
            for t in range(n, n + 10000):
                dev = np.exp(b0l + b1l * t + b2l * t ** 2)
                if dev < 1e-6:
                    break
                tail_l += dev
            loo_tails.append(tail_l)

    return _loo_result(r2, resid, loo_tails)


def fit_diagnostics_bondy(df_enhanced, measure, starting_age, selections):
    intervals_start = intervals_from_starting_age(selections, starting_age)
    if not intervals_start:
        return _empty_fit_diag()
    last_interval = intervals_start[-1][0]
    df_m = df_enhanced[df_enhanced['measure'].astype(str) == measure]
    df_last = df_m[df_m['interval'].astype(str) == str(last_interval)].dropna(subset=['ldf'])
    if len(df_last) < 2:
        return _empty_fit_diag()
    loo_tails = []
    for period in df_last['period'].astype(str).unique():
        df_loo = df_last[df_last['period'].astype(str) != period]
        if df_loo.empty:
            continue
        w = df_loo['weight'].fillna(1.0)
        if w.sum() > 0:
            loo_tails.append(float((df_loo['ldf'] * w).sum() / w.sum()))
    return _loo_result(None, None, loo_tails)


def fit_diagnostics_skurnick(incs, ln_A, ln_r):
    """R² of ln(inc) regression for Skurnick."""
    if incs is None or len(incs) < 2:
        return _empty_fit_diag()
    y_vals = np.arange(len(incs), dtype=float)
    log_incs = np.log(np.array(incs))
    fitted = ln_A + ln_r * y_vals
    ss_res = np.sum((log_incs - fitted) ** 2)
    ss_tot = np.sum((log_incs - np.mean(log_incs)) ** 2)
    r2 = float(1 - ss_res / ss_tot) if ss_tot > 0 else None
    return {'r_squared': r2, 'residuals_json': None, 'loo_std_dev': None, 'loo_min': None, 'loo_max': None}


def _empty_fit_diag():
    return {'r_squared': None, 'residuals_json': None, 'loo_std_dev': None, 'loo_min': None, 'loo_max': None}


def _loo_result(r2, resid, loo_tails):
    return {
        'r_squared': r2,
        'residuals_json': json.dumps(resid) if resid else None,
        'loo_std_dev': float(np.std(loo_tails)) if len(loo_tails) >= 2 else None,
        'loo_min':     float(np.min(loo_tails)) if loo_tails else None,
        'loo_max':     float(np.max(loo_tails)) if loo_tails else None,
    }


def compute_gap(factors, params, method):
    """Gap between fitted d at t=0 and actual d at t=0 (in factor-1 space)."""
    no_curve = {'bondy', 'modified_bondy_double_dev', 'modified_bondy_square_ratio',
                'mcclenahan', 'skurnick'}
    if method in no_curve or params is None or not factors:
        return None, False
    d_actual = factors[0] - 1
    if d_actual <= 0:
        return None, False
    if isinstance(params, tuple) and len(params) == 2:
        D, r = params
        d_fitted = D  # D * r^0
    elif isinstance(params, tuple) and len(params) == 3:
        b0, b1, b2 = params
        d_fitted = np.exp(b0)  # at t=0
    else:
        return None, False
    gap = abs(d_actual - d_fitted)
    return float(gap), bool(gap > GAP_THRESHOLD)


def reserve_impact_diagnostics(selections_all, tail, df_triangles, measure):
    """pct_of_cdf, materiality_ok, sensitivity reserve deltas."""
    empty = {
        'pct_of_cdf': None, 'materiality_ok': None,
        'sensitivity_plus10_reserve_delta': None,
        'sensitivity_minus10_reserve_delta': None,
        'sensitivity_plus20_reserve_delta': None,
        'sensitivity_minus20_reserve_delta': None,
    }
    if tail is None or tail <= 1:
        return empty

    cdf_no_tail = 1.0
    for ldf in selections_all.values():
        if pd.notna(ldf):
            cdf_no_tail *= float(ldf)
    full_cdf = cdf_no_tail * tail

    if full_cdf <= 1:
        return empty

    pct = (tail - 1) / (full_cdf - 1) * 100.0
    materiality_ok = bool(pct < MATERIALITY_THRESHOLD)

    # Diagonal: most recent value per AY
    df_m = df_triangles[df_triangles['measure'].astype(str) == measure].copy()
    if df_m.empty:
        diagonal_sum = 0.0
    else:
        df_m['age_int'] = pd.to_numeric(df_m['age'].astype(str), errors='coerce')
        diag = df_m.groupby('period', observed=True).apply(
            lambda g: g.loc[g['age_int'].idxmax(), 'value'], include_groups=False
        )
        diagonal_sum = float(diag.sum())

    base_reserve = diagonal_sum * (1 - 1 / full_cdf)

    def delta(t_factor):
        cdf_new = cdf_no_tail * t_factor
        if cdf_new <= 0:
            return None
        return float(diagonal_sum * (1 - 1 / cdf_new) - base_reserve)

    return {
        'pct_of_cdf': float(pct),
        'materiality_ok': materiality_ok,
        'sensitivity_plus10_reserve_delta':   delta(tail * 1.10),
        'sensitivity_minus10_reserve_delta':  delta(tail * 0.90),
        'sensitivity_plus20_reserve_delta':   delta(tail * 1.20),
        'sensitivity_minus20_reserve_delta':  delta(tail * 0.80),
    }


# ── Skurnick data preparation ─────────────────────────────────────────────────

def build_skurnick_array(df_triangles, measure, starting_age):
    """
    2D cumulative array for Skurnick, oldest AY = row 0.
    Returns (array, ages_list) or (None, None).
    """
    df_m = df_triangles[df_triangles['measure'].astype(str) == measure].copy()
    if df_m.empty:
        return None, None
    df_m['age_int']    = pd.to_numeric(df_m['age'].astype(str), errors='coerce')
    df_m['period_int'] = pd.to_numeric(df_m['period'].astype(str), errors='coerce')
    ages = sorted(a for a in df_m['age_int'].dropna().unique() if a >= starting_age)
    if len(ages) < 2:
        return None, None
    periods = sorted(df_m['period_int'].dropna().unique())  # ascending = oldest first
    rows = []
    for p in periods:
        row = []
        for a in ages:
            sub = df_m[(df_m['period_int'] == p) & (df_m['age_int'] == a)]['value']
            row.append(float(sub.iloc[0]) if not sub.empty else np.nan)
        rows.append(row)
    return np.array(rows, dtype=float), ages


def _skurnick_internals(cum_2d):
    """Return (incs, ln_A, ln_r) for R² computation, or (None, None, None)."""
    if cum_2d is None or cum_2d.shape[0] == 0:
        return None, None, None
    oldest = cum_2d[0]
    incs = []
    for i in range(len(oldest) - 1):
        if np.isfinite(oldest[i]) and np.isfinite(oldest[i + 1]) and oldest[i] > 0:
            inc = oldest[i + 1] - oldest[i]
            if inc > 0:
                incs.append(float(inc))
    if len(incs) < 2:
        return None, None, None
    y = np.arange(len(incs), dtype=float)
    log_incs = np.log(np.array(incs))
    A_mat = np.column_stack([np.ones_like(y), y])
    try:
        coeffs, _, _, _ = np.linalg.lstsq(A_mat, log_incs, rcond=None)
        return incs, float(coeffs[0]), float(coeffs[1])
    except Exception:
        return None, None, None


# ── Main processing ───────────────────────────────────────────────────────────

MEASURE_BANNERS = {
    "Paid Loss":      "Paid loss tails typically materially longer than incurred loss",
    "Incurred Loss":  "Incurred loss tails shorter than paid; case reserve development shapes pattern",
    "Closed Count":   "Closed count tails materially longer than reported count",
    "Reported Count": "Reported count tails shorter than closed count",
}


def process_measure(measure, selections, df_enhanced, df_averages, df_triangles):
    banner = MEASURE_BANNERS.get(measure, "")
    print(f"\n{'='*60}\nMeasure: {measure}")
    if banner:
        print(f"  [{banner}]")

    cutoff_age = get_cutoff_age(selections)
    if cutoff_age is None:
        print(f"  WARNING: No cutoff age found for {measure}. Skipping.")
        return []
    print(f"  Tail Cutoff inferred from selections: {cutoff_age}")

    # The starting_age for the fit is the earliest selected interval.
    # The tail factor will represent the development from cutoff_age to ultimate.
    # But wait, Skurnick needs starting_age = cutoff_age because it fits on incrementals *after* the cutoff.
    # Actually, the user said: "Only fit the tail curves on the selected LDFs up to the cutoff."
    
    all_ages = get_all_start_ages(selections)
    min_start_age = min(all_ages) if all_ages else 12
    max_age_in_triangles = df_triangles[df_triangles['measure'].astype(str) == measure]['age'].astype(float).max()
    max_age = int(max_age_in_triangles) if pd.notna(max_age_in_triangles) else 120

    intervals_fit = sorted([ (parse_interval(k)[0], k, v) for k,v in selections.items() ], key=lambda x: x[0])
    intervals_str = [(k, v) for _, k, v in intervals_fit]
    factors = [ldf for _, ldf in intervals_str]

    if len(factors) < 2:
         print(f"  WARNING: Need at least 2 selected LDFs for {measure}. Skipping.")
         return []

    # AY weights for WLS and LOO
    ay_wts = build_ay_weights(df_enhanced, measure, intervals_str)
    total_wts = aggregate_weights(ay_wts, intervals_str)

    # Starting point diagnostics (shared across methods) - use cutoff_age to evaluate variance at the cutoff
    sp = starting_point_diagnostics(df_enhanced, measure, min_start_age, selections)

    # Skurnick data - we pass min_start_age because we fit on all data available in the selected range
    # Or should Skurnick fit on incrementals? Skurnick fits on the oldest AY's incrementals.
    cum_2d, _ = build_skurnick_array(df_triangles, measure, min_start_age)
    skurnick_incs, sk_ln_A, sk_ln_r = _skurnick_internals(cum_2d)

    # Get the cutoff interval string
    cutoff_interval = intervals_fit[-1][1]

    # Calculate min, max empirical ATAs for the cutoff interval
    df_m = df_enhanced[(df_enhanced['measure'].astype(str) == measure) & (df_enhanced['interval'].astype(str) == cutoff_interval)].dropna(subset=['ldf'])
    min_ata = float(df_m['ldf'].min()) if len(df_m) > 0 else None
    max_ata = float(df_m['ldf'].max()) if len(df_m) > 0 else None

    # Get avg, cv, slope from df_averages for the cutoff interval
    df_a = df_averages[(df_averages['measure'].astype(str) == measure) & (df_averages['interval'].astype(str) == cutoff_interval)]
    if not df_a.empty:
        avg_ata   = float(df_a['weighted_all'].iloc[0]) if pd.notna(df_a['weighted_all'].iloc[0]) else None
        min_ata   = float(df_a['min_all'].iloc[0]) if pd.notna(df_a['min_all'].iloc[0]) else min_ata
        max_ata   = float(df_a['max_all'].iloc[0]) if pd.notna(df_a['max_all'].iloc[0]) else max_ata
        cv_ata    = float(df_a['cv_10yr'].iloc[0]) if pd.notna(df_a['cv_10yr'].iloc[0]) else None
        slope_ata = float(df_a['slope_10yr'].iloc[0]) if pd.notna(df_a['slope_10yr'].iloc[0]) else None
    else:
        avg_ata = None
        cv_ata = None
        slope_ata = None

    method_results = []

    # Bondy
    t = tail_bondy(factors)
    if t:
        fd = fit_diagnostics_bondy(df_enhanced, measure, min_start_age, selections)
        method_results.append(('bondy', None, t, fd))

    # Modified Bondy Double Dev
    t = tail_modified_bondy_double_dev(factors)
    if t:
        method_results.append(('modified_bondy_double_dev', None, t, _empty_fit_diag()))

    # Modified Bondy Square Ratio
    t = tail_modified_bondy_square_ratio(factors)
    if t:
        method_results.append(('modified_bondy_square_ratio', None, t, _empty_fit_diag()))

    # Exp Dev Quick
    t, params = tail_exp_dev_quick(factors, total_wts)
    if t:
        fd = fit_diagnostics_exp_dev(factors, total_wts, ay_wts, total_wts, params)
        method_results.append(('exp_dev_quick', params, t, fd))

    # Exp Dev Quick Exact Last
    t, params = tail_exp_dev_quick_exact_last(factors, total_wts)
    if t:
        fd = fit_diagnostics_exp_dev(factors, total_wts, ay_wts, total_wts, params)
        method_results.append(('exp_dev_quick_exact_last', params, t, fd))

    # Exp Dev Product
    t, params = tail_exp_dev_product(factors, total_wts)
    if t:
        fd = fit_diagnostics_exp_dev(factors, total_wts, ay_wts, total_wts, params)
        method_results.append(('exp_dev_product', params, t, fd))

    # Double Exp
    t, params = tail_double_exp(factors, total_wts)
    if t:
        fd = fit_diagnostics_double_exp(factors, total_wts, ay_wts, total_wts, params)
        method_results.append(('double_exp', params, t, fd))

    # McClenahan
    t, params = tail_mcclenahan(factors, max_age)
    if t:
        method_results.append(('mcclenahan', params, t, _empty_fit_diag()))

    # Skurnick
    t, params = tail_skurnick(cum_2d)
    if t:
        fd = fit_diagnostics_skurnick(skurnick_incs, sk_ln_A, sk_ln_r)
        method_results.append(('skurnick', params, t, fd))

    rows = []
    for method_key, params, tail_val, fit_diag in method_results:
        gap, gap_flag = compute_gap(factors, params, method_key)
        ri = reserve_impact_diagnostics(selections, tail_val, df_triangles, measure)

        rows.append({
            'measure': measure,
            'starting_age': min_start_age,
            'cutoff_age': cutoff_age,
            'method': method_key,
            'method_params': json.dumps(
                {k: round(v, 8) if isinstance(v, float) else v for k, v in params.items()}
                if isinstance(params, dict)
                else list(params) if isinstance(params, tuple)
                else params
            ) if params is not None else None,
            'tail_factor': tail_val,
            'n_factors_in_fit':      sp['n_factors_in_fit'],
            'n_ay_contributing':     sp['n_ay_contributing'],
            'is_monotone_from_here': sp['is_monotone_from_here'],
            'cv_at_starting_age':    cv_ata,
            'slope_sign_changes':    sp['slope_sign_changes'],
            'min_selected_ldf':      min_ata,
            'max_selected_ldf':      max_ata,
            'avg_selected_ldf':      avg_ata,
            'r_squared':             fit_diag['r_squared'],
            'loo_std_dev':           fit_diag['loo_std_dev'],
            'loo_min':               fit_diag['loo_min'],
            'loo_max':               fit_diag['loo_max'],
            'gap_to_last_observed':  gap,
            'gap_flag':              gap_flag,
            'pct_of_cdf':            ri['pct_of_cdf'],
            'materiality_ok':        ri['materiality_ok'],
            'sensitivity_plus10_reserve_delta':   ri['sensitivity_plus10_reserve_delta'],
            'sensitivity_minus10_reserve_delta':  ri['sensitivity_minus10_reserve_delta'],
            'sensitivity_plus20_reserve_delta':   ri['sensitivity_plus20_reserve_delta'],
            'sensitivity_minus20_reserve_delta':  ri['sensitivity_minus20_reserve_delta'],
            'residuals_json':        fit_diag['residuals_json'],
        })
        r2_str = f"R²={fit_diag['r_squared']:.3f}" if fit_diag['r_squared'] else "R²=N/A"
        print(f"  {method_key:35s} | cutoff={cutoff_age:3d} | tail={tail_val:.4f} | {r2_str}")

    return rows


def main():
    print("Loading data...")
    df_triangles = pd.read_parquet(INPUT_TRIANGLES)
    df_enhanced  = pd.read_parquet(INPUT_ENHANCED)
    df_averages  = pd.read_parquet(INPUT_AVERAGES)

    if not Path(INPUT_EXCEL).exists():
        raise FileNotFoundError(
            f"Selections file not found: {INPUT_EXCEL}\n"
            "Run 2a, make LDF selections, then run 2b before running this script."
        )

    measures = [m for m in df_triangles['measure'].astype(str).unique() if m != 'Exposure']
    print(f"  Measures: {measures}")

    all_rows = []
    for measure in measures:
        try:
            selections = read_selections(INPUT_EXCEL, measure)
        except (ValueError, RuntimeError) as e:
            print(f"  ERROR reading selections for {measure}: {e}")
            continue

        rows = process_measure(measure, selections, df_enhanced, df_averages, df_triangles)
        all_rows.extend(rows)

    if not all_rows:
        raise RuntimeError("No scenarios computed. Verify selections exist and data is valid.")

    df_out = pd.DataFrame(all_rows)

    float_cols = [
        'tail_factor', 'cv_at_starting_age', 'r_squared', 'loo_std_dev', 'loo_min', 'loo_max',
        'gap_to_last_observed', 'pct_of_cdf',
        'sensitivity_plus10_reserve_delta', 'sensitivity_minus10_reserve_delta',
        'sensitivity_plus20_reserve_delta', 'sensitivity_minus20_reserve_delta',
    ]
    for col in float_cols:
        df_out[col] = pd.to_numeric(df_out[col], errors='coerce')

    for col in ['is_monotone_from_here', 'gap_flag', 'materiality_ok']:
        df_out[col] = df_out[col].astype('boolean')

    for col in ['n_factors_in_fit', 'n_ay_contributing', 'slope_sign_changes', 'starting_age']:
        df_out[col] = pd.to_numeric(df_out[col], errors='coerce').astype('Int64')

    df_out.to_parquet(OUTPUT_PATH, index=False)
    df_out.to_csv(OUTPUT_PATH.replace('.parquet', '.csv'), index=False)
    print(f"\nSaved {len(df_out)} scenarios to {OUTPUT_PATH.replace('.parquet', '.[parquet|csv]')}")
    print("parquet preserves categorical types, CSV for inspection")
    print("\nSummary by measure and method:")
    print(df_out.groupby(['measure', 'method'])['tail_factor']
          .agg(['count', 'min', 'max']).to_string())


if __name__ == "__main__":
    main()
