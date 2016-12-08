import pytest
from treefarm import *

def test_add():
    assert compute(sample(join(3) + join(5))) == 8

def test_mul():
    assert compute(sample(join(10) * join(4))) == 40 
