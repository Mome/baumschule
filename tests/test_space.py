import pytest
from treefarm import *

def test_join_sample():
    dom_a = {'a', 'b', 'c'}
    a = convert(dom_a)
    dom_b = N[0:5]
    b = convert(dom_b)
    c = join(a, b)
    for _ in range(10):
        x = sample(c)
        assert x in [*dom_a, 0,1,2,3,4]
