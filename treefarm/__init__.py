
from .core.environment import init_config, init_env
init_config()
init_env()
del init_config, init_env

from .core.environment import get_config, get_env

from .core.domains import R, N, N0, Z, Interval, ParameterList

from .core.parameters import (
    Categorical, Discrete, Continuous, Apply, op,
    join, intersect, power, prod,
)

from .core.simplify import simplify
from .core.display_str import pprint , pformat
from .core.random_variables import sample
from .core.computing_engine import compute
from .core.iterators import iter_instances
from .core.serialize import serialize
from .core.display_dot import to_dot
from .core.optimizer import optimize, optimize_func

from .operations import *

# TODO: put this somewhere else
cont = Continuous
disc = Discrete
catg = Categorical
