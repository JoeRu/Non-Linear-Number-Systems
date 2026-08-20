"""Regression for the four-term expansion

    log R_c(N) = a (log N)^2 + b log N loglog N + c log N + d + o(1)

Convergence in the leading term is slow, so a plain ratio to (log N)^2 is a
poor estimator of `a`; this fit and the local slope in `capfib.saddle` are the
two usable ones.
"""

from collections.abc import Sequence

import numpy as np


def design_matrix(ns: Sequence[float]) -> np.ndarray:
    """Columns [L^2, L log L, L, 1] with L = log N."""
    L = np.log(np.asarray(ns, dtype=float))
    return np.column_stack([L * L, L * np.log(L), L, np.ones_like(L)])


def fit_expansion(ns: Sequence[float], log_rs: Sequence[float]) -> dict[str, float]:
    """Least-squares fit; returns the coefficients as {a, b, c, d}."""
    coef, *_ = np.linalg.lstsq(
        design_matrix(ns), np.asarray(log_rs, dtype=float), rcond=None
    )
    return {"a": float(coef[0]), "b": float(coef[1]),
            "c": float(coef[2]), "d": float(coef[3])}
