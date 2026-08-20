from capfib.brute import count, numerals


def test_worked_example_value_one():
    """theory/01-background.md §2: numerals 1000 and 0100 both denote 1."""
    got = {"".join(map(str, t)) for t in numerals(1, places=[1, 1, 2, 3])}
    assert got == {"1000", "0100"}


def test_worked_example_value_five():
    got = {"".join(map(str, t)) for t in numerals(5, places=[1, 1, 2, 3])}
    assert got == {"1020", "0120", "1101", "0011"}


def test_worked_example_value_six():
    got = {"".join(map(str, t)) for t in numerals(6, places=[1, 1, 2, 3])}
    assert got == {"1120", "1011", "0111", "0002"}


def test_digit_caps_respected():
    for t in numerals(12):
        places = [1, 1, 2, 3, 5, 8]
        assert len(t) == len(places)
        assert all(0 <= d <= f for d, f in zip(t, places))


def test_counts_small():
    """R_c(N) for N = 0..20 over all places F_k <= N."""
    expected = [1, 2, 2, 3, 4, 5, 6, 6, 8, 10, 11, 13, 13, 15, 18, 18, 21, 23, 25, 29, 29]
    assert [count(n) for n in range(21)] == expected


def test_count_matches_enumeration():
    for n in range(0, 30):
        assert count(n) == sum(1 for _ in numerals(n))


def test_negative_is_zero():
    assert count(-1) == 0
