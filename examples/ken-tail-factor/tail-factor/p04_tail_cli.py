"""Argparse helpers for required Boor tail-method selection (keeps p05_run_chain_ladder.py small)."""

from __future__ import annotations

import argparse
from typing import Any

from p03_tail_select import TAIL_METHODS


def register_tail_arguments(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--tail-method",
        choices=TAIL_METHODS,
        required=True,
        help="Tail treatment (Boor methods); no default — pick explicitly.",
    )
    p.add_argument("--tail-scalar", type=float, default=None, help="With tail-method scalar, multiply ultimates by this factor.")
    p.add_argument(
        "--modified-bondy-mode",
        choices=("double_dev", "square_ratio"),
        default="double_dev",
        help="With tail-method modified_bondy.",
    )
    p.add_argument("--tail-m-months", type=float, default=None, help="McClenahan: evaluation maturity m in months.")
    p.add_argument("--tail-a-months", type=float, default=None, help="McClenahan: average reporting lag a in months.")
    p.add_argument(
        "--tail-mcclenahan-last-n",
        type=int,
        default=5,
        help="McClenahan: number of late incremental ratios to average for r.",
    )
    p.add_argument(
        "--tail-exp-dev-mode",
        choices=("quick", "product"),
        default="quick",
        help="Method 6: quick closed form vs product of projected link ratios.",
    )
    p.add_argument("--tail-exp-future-periods", type=int, default=8, help="Method 6 quick form: K in 1 + D r^K/(1-r).")
    p.add_argument("--tail-exp-mature-min-t", type=int, default=None, help="Method 6: fit only t >= this year index (Improvement 3).")
    p.add_argument("--tail-exp-exact-last", action="store_true", help="Method 6 Improvement 2 (exact last link).")
    p.add_argument("--tail-exp-product-tol", type=float, default=1e-6, help="Method 6 product mode stopping tolerance on dev portion.")


def tail_kwargs_from_args(ns: argparse.Namespace) -> dict[str, Any]:
    return {
        "tail_scalar": ns.tail_scalar,
        "modified_bondy_mode": ns.modified_bondy_mode,
        "m_months": ns.tail_m_months,
        "a_months": ns.tail_a_months,
        "mcclenahan_last_n": ns.tail_mcclenahan_last_n,
        "exp_dev_mode": ns.tail_exp_dev_mode,
        "exp_future_periods": ns.tail_exp_future_periods,
        "exp_mature_min_t": ns.tail_exp_mature_min_t,
        "exp_exact_last": ns.tail_exp_exact_last,
        "exp_product_tol": ns.tail_exp_product_tol,
    }


def validate_tail_args(ns: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if ns.tail_method == "scalar" and ns.tail_scalar is None:
        parser.error("tail_method 'scalar' requires --tail-scalar.")
    if ns.tail_method == "mcclenahan_paid" and (ns.tail_m_months is None or ns.tail_a_months is None):
        parser.error("tail_method 'mcclenahan_paid' requires --tail-m-months and --tail-a-months.")
