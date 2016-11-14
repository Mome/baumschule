from .core.parameters import (
    Categorical, Discrete, Continuous, Apply,
    join, prod, intersect,
    mul, add, div, sub,
)

from .core.simplify import simplify
from .core.display_dot import to_dot
from .core.display_str import pprint , pformat
from .core.domains import R, N, N0, Z, Interval, ParameterList
from .core.random_variables import sample
from .core.computing_engine import compute
from .core.iterators import iterate_instances


cont = Continuous
disc = Discrete
catg = Categorical
