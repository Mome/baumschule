
from .core.environment import init_config, init_env
init_config()
init_env()
del init_config, init_env

from .core.environment import get_config, get_env

from .core.domains import R, N, N0, Z, Interval, ParameterList

from .core.spaces import (
    Categorical, Discrete, Continuous, Apply, operation, op,
    join, intersect, power, prod, quote
)


from .core.simplify import simplify
from .core.random_variables import sample
from .core.computing_engine import compute
from .core.iterators import iter_instances
from .core.serialize import serialize, pprint , pformat
from .core.to_graphviz import todot
from .core.minimizer import minimize, minimize_func
from .core.space_utils import to_space, is_recursive
from .data_access import data_access as da
convert = to_space

from .operations import *

# TODO: put this somewhere else
def load(filename):
    return da.Path('local:/' + filename).read()

cont = Continuous
disc = Discrete
catg = Categorical
