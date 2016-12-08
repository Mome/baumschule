from math import inf
import pytest
from treefarm.core.domains import ParameterList, Interval, R, N, Z

A = Interval(-12.6, 18.5, 0.1, False, True)
B = Interval(-12.6, 18.5, 0.1, True, False)
C = Interval(-123.65, 122.79, 11.11, False, True)

def test_other():
    assert N.closed is True
    assert R.closed is False
    assert A.bounded is True
    assert N.bounded is False

def test_contains():
    for i in [0, 1, -100, 111.111, -.5]:
        assert i in R
    for i in [inf, -inf]:
        assert i not in R

    for i in [1, 100, 3, 5]:
        assert i in N
    for i in [inf, -inf, .01, 0, -1, -.3]:
        assert i not in N

    for i in [18.5, 0, 1.1, -1.1]:
        assert i in A
    for i in [inf, -inf, -12.6, 0.11, -0.23]:
        assert i not in A

    for i in [-12.6, 0, 1.1, -1.1]:
        assert i in B
    for i in [18.5, 0.11, -0.23]:
        assert i not in B

    for i in [-112.54]:
        assert i in C
    for i in [-123.65, 122.79]:
        assert i not in C

def test_iter():
    for i, j in enumerate(N[:10], 1):
        assert i == j
