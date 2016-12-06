
import random
import logging

import numpy as np

from .spaces import (
    Apply, Categorical, Discrete, Continuous, join
)

from .domains import ParameterList, Interval
from .serialize import serialize

log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel('INFO')

# --- sample from params -- #
def sample(param):
    log.debug('sample:%s' % param)
    if vars(param).get('dist', False):
        dist = param.dist
    dist = get_default_dist(param)
    return dist()


def get_default_dist(param):
    """
    Returns a function
    """

    if type(param) is Categorical:
        dist = default_categorical(param)

    elif type(param) is Discrete:
        dist = default_discrete(param)

    elif type(param) is Continuous:
        dist = default_continous(param)

    elif type(param) is Apply:
        dist = default_apply(param)

    else:
        dist = lambda : param

    return dist


def default_categorical(param):
    def dist():
        return random.sample(param.domain, 1)[0]
    return dist


def default_discrete(param):

    if type(param.domain) == Interval:
        start = param.domain.start
        stop = param.domain.stop
        l_inf = (start == float('-inf'))
        r_inf = (stop == float('inf'))
    else:
        dom = sorted(param.domain)
        start = dom[0]
        stop = dom[-1]
        l_inf = r_inf = False

    if l_inf and r_inf:
        dist = lambda : round(np.random.normal())
    if not l_inf and r_inf:
        dist = lambda : round(np.random.lognormal() + start)
    if l_inf and not r_inf:
        dist = lambda : round(-np.random.lognormal() + stop)
    if not l_inf and not r_inf:
        dist = lambda : np.random.randint(start, stop)

    return dist


def default_continous(param):
    dom = param.domain
    assert type(dom) == Interval; 'Continous domain type must be Interval.'

    l_inf = (dom.start == float('-inf'))
    r_inf = (dom.stop == float('inf'))

    if l_inf and r_inf:
        dist = np.random.normal
    if not l_inf and r_inf:
        dist = lambda : np.random.lognormal() + dom.start
    if l_inf and not r_inf:
        dist = lambda : -np.random.lognormal() + dom.stop
    if not l_inf and not r_inf:
        dist = lambda : np.random.uniform(dom.start, dom.stop)

    return dist


def default_apply(param):

    if param.operation == join:
        def dist():
            start = random.sample(set(param.domain), 1)[0]
            return sample(start)

    else:
        def inner_dist():
            args = [
                sample(start)
                for start in param.domain.args
            ]
            kwargs = {
                key:sample(start)
                for key, start in param.domain.kwargs.items()
            }
            return ParameterList(args, kwargs)


        def dist():
            plist = inner_dist()
            operation = sample(param.operation)
            return Apply(operation, plist)

    return dist


# ------ Distributions ------ #

def normal(mean=0, std=1, *, name=None):
    return s.Parameter(
        domain = R,
        dist = lambda : np.random.normal(mean, std),
        name = name,
    )
gauss = normal


lognormal = np.random.lognormal()
poisson = ...
binomial = ...
bernoulli = ...
uniform = np.random.randint(0, 1)
laplace = ...


class DistributionInferenceError(Exception):
    pass
