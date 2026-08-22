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
    """The measured local slope d(log R)/d((log N)^2) sits at 1/(4 log phi).

    Three finite differences of the Legendre transform, at N = 10^100, 10^200,
    10^400, 10^800: 0.5107, 0.5146, 0.5168, rising toward
    1/(4 log phi) = 0.5195. This is a *measurement of the transform*, over four
    sampled points, and that is all it is. It does not bound C_c: a leading
    coefficient is a limit, and three finite differences constrain no limit.

    What the numbers are away from is worth stating precisely, because the
    wording here was backwards until the pre-PR gate caught it. The measured
    slopes are **below** 1/(2 log phi) = 1.0390, not above it, and **above**
    1/(8 log phi) = 0.2598. The distances are asserted so a drift toward either
    candidate would fail; neither distance is what rules the candidate out.

    Both candidates are ruled out on paper, not here:

    * 1/(2 log phi) by T2 of docs/phases/phase2_bounds.md, which proves the
      transform's leading coefficient is 1/(4 log phi), together with T1
      putting log R_c(N) at or below the transform.
    * 1/(8 log phi) by C5, unconditionally, by a route that does not pass
      through this measurement at all.

    `saddle-tightness`, which Phase 0.5 had to assume to read anything off this
    measurement, has been a theorem since Phase 2.
    """
    target = 1.0 / (4 * LOG_PHI)
    pts = []
    for e in (100, 200, 400, 800):
        L = e * math.log(10)
        pts.append((L * L, log_R_bound(L)))
    slopes = [(pts[i + 1][1] - pts[i][1]) / (pts[i + 1][0] - pts[i][0])
              for i in range(len(pts) - 1)]
    assert slopes == sorted(slopes), "slope should rise monotonically"
    assert slopes[-1] == pytest.approx(target, abs=0.005)
    assert slopes[-1] < 1.0 / (2 * LOG_PHI), (
        "the measured slopes lie BELOW 1/(2 log phi) = 1.0390, not above it -- "
        "0.5107, 0.5146, 0.5168 against 1.0390. This assertion records which "
        "side they are on; the reason 1/(2 log phi) is excluded is T2 plus T1 "
        "in docs/phases/phase2_bounds.md, not this measurement"
    )
    assert abs(slopes[-1] - 1.0 / (2 * LOG_PHI)) > 0.4, (
        "the measured slope has drifted toward 1/(2 log phi); it should sit "
        "near 1/(4 log phi) = 0.5195, about 0.52 below that candidate"
    )
    assert slopes[-1] > 1.0 / (8 * LOG_PHI), (
        "the measured slopes lie above 1/(8 log phi) = 0.2598"
    )
    assert abs(slopes[-1] - 1.0 / (8 * LOG_PHI)) > 0.2, (
        "the measured slope has drifted toward 1/(8 log phi). Being above it is "
        "not what excludes it: this is an upper bound on log R_c, so a smaller "
        "true constant is entirely compatible with a larger measured slope. "
        "What excludes 1/(8 log phi) is C5 of docs/phases/phase2_bounds.md"
    )


def test_rejects_boundary_minimiser():
    """A bracket too narrow to contain the minimiser must raise, not return."""
    with pytest.raises(ValueError, match="bracket"):
        log_R_bound(math.log(10 ** 100), half=1e-9)
