import math

import pytest

from capfib.gf import coefficients
from capfib.saddle import log_R_bound, log_R_bound_at

PHI = (1 + 5 ** 0.5) / 2
LOG_PHI = math.log(PHI)


def test_is_an_upper_bound():
    counts = coefficients(600)
    for n in (100, 200, 400, 600):
        assert log_R_bound_at(n) > math.log(counts[n])


def test_leading_constant_approaches_quarter_log_phi():
    """Local slope d(log R)/d((log N)^2) converges to 1/(4 log phi)."""
    target = 1.0 / (4 * LOG_PHI)
    pts = []
    for e in (100, 200, 400, 800):
        L = e * math.log(10)
        pts.append((L * L, log_R_bound(L)))
    slopes = [(pts[i + 1][1] - pts[i][1]) / (pts[i + 1][0] - pts[i][0])
              for i in range(len(pts) - 1)]
    assert slopes == sorted(slopes), "slope should rise monotonically"
    assert slopes[-1] == pytest.approx(target, abs=0.005)
    assert abs(slopes[-1] - 1.0 / (2 * LOG_PHI)) > 0.4, "rules out 1/(2 log phi)"
    assert abs(slopes[-1] - 1.0 / (8 * LOG_PHI)) > 0.2, "rules out 1/(8 log phi)"


def test_rejects_boundary_minimiser():
    """A bracket too narrow to contain the minimiser must raise, not return."""
    with pytest.raises(ValueError, match="bracket"):
        log_R_bound(math.log(10 ** 100), half=1e-9)
