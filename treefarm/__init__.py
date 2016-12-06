
from .core.environment import init_config, init_env
init_config()
init_env()
del init_config, init_env

from .core.environment import get_config, get_env

from .core.domains import R, N, N0, Z, Interval, ParameterList

from .core.spaces import (
    Categorical, Discrete, Continuous, Apply, op,
    join, intersect, power, prod,
)


from .core.simplify import simplify
from .core.random_variables import sample
from .core.computing_engine import compute
from .core.iterators import iter_instances
from .core.serialize import serialize, pprint , pformat
from .core.to_graphviz import todot
from .core.minimizer import minimize, minimize_func
from .core.space_utils import to_space
convert = to_space

from .operations import *

# TODO: put this somewhere else
cont = Continuous
disc = Discrete
catg = Categorical
