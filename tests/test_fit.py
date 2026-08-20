import math

import numpy as np
import pytest

from capfib.fit import design_matrix, fit_expansion


def test_recovers_known_coefficients():
    ns = [10.0 ** k for k in range(5, 61)]
    truth = {"a": 0.519522, "b": 0.3, "c": 1.1, "d": 2.0}
    L = np.log(np.array(ns))
    log_rs = truth["a"] * L * L + truth["b"] * L * np.log(L) + truth["c"] * L + truth["d"]
    got = fit_expansion(ns, log_rs)
    for k, v in truth.items():
        assert got[k] == pytest.approx(v, rel=1e-6)


def test_design_matrix_shape_and_columns():
    ns = [100.0, 1000.0, 10000.0]
    m = design_matrix(ns)
    assert m.shape == (3, 4)
    L = math.log(100.0)
    assert m[0, 0] == pytest.approx(L * L)
    assert m[0, 1] == pytest.approx(L * math.log(L))
    assert m[0, 2] == pytest.approx(L)
    assert m[0, 3] == pytest.approx(1.0)
