from capfib.brute import count
from capfib.dp import counts
from capfib.fib import fibonacci


def test_dp_matches_oracle_to_200():
    """Spec §4.2, first half of the gate."""
    arr = counts(200)
    for n in range(201):
        assert arr[n] == count(n), f"mismatch at N={n}"


def test_dp_zero():
    assert counts(0) == [1]


def test_section4_table():
    """Reproduces the n = 1..10 table of theory/01-background.md §4.

    Columns: max value, total numerals S(n), max representations, gap count.
    Note this table fixes the length at exactly n places, which UNDERCOUNTS
    R_c(N) -- it is a property of the length-n system, not of R_c.
    """
    expected = {
        1:  (1,    2,          1,      0),
        2:  (2,    4,          2,      0),
        3:  (6,    12,         2,      0),
        4:  (15,   48,         4,      0),
        5:  (40,   288,        10,     0),
        6:  (104,  2592,       37,     0),
        7:  (273,  36288,      202,    0),
        8:  (714,  798336,     1746,   0),
        9:  (1870, 27941760,   23638,  0),
        10: (4895, 1564738560, 510384, 0),
    }
    for n, (maxval, total, most, gaps) in expected.items():
        F = fibonacci(n)
        assert sum(f * f for f in F) == maxval
        arr = counts(maxval, places=F)
        s = 1
        for f in F:
            s *= f + 1
        assert s == total
        assert max(arr) == most
        assert arr.count(0) == gaps, "completeness: no gaps anywhere in range"
