from .core.parameters import (
    Categorical, Discrete, Continuous,
    join, prod, intersect,
    mul, add, div, sub,
)

from .core.simplify import simplify

from .core.display_dot import to_dot
from .core.display_str import pprint , pformat
from .core.domains import R, N, N0, Z, Intervall, ParameterList

cont = Continuous
disc = Discrete
catg = Categorical
