import numpy as np
import random

from .spaces import (
    JoinedSpace,
    ProductSpace,
    Categorical,
    Discrete,
    Continuous,
    CallSpace,
    Constant,
    )

from .domains import (
    Intervall,
    Product,
    Call,
)

# --- sample from spaces -- #
def sample(space):
    if space.dist:
        dist = space.dist
    dist = get_default_dist(space)
    return dist()

def get_default_dist(space):
    """
    Returns a function
    """

    if type(space) is JoinedSpace:
        def dist():
            sub = random.sample(space.domain, 1)[0]
            return sample(sub)

    elif isinstance(space, ProductSpace):
        def inner_dist():
            arg_samples = [
                sample(sub)
                for sub in space.domain.args
            ]
            kw_samples = {
                key:sample(sub)
                for key, sub in space.domain.kwargs.items()
            }
            return Product(arg_samples, kw_samples)

        if type(space) == CallSpace:
            print('match')
            def dist():
                product = inner_dist()
                return Call(space.operator, product.args, product.kwargs)
        else:
            dist = inner_dist

    elif type(space) is Categorical:
        def dist():
            return random.sample(space.domain, 1)[0]

    elif type(space) == Discrete:
        dom = space.domain
        assert type(dom) == Intervall
        l_inf = (dom.sub == float('-inf'))
        r_inf = (dom.sup == float('inf'))

        if l_inf and r_inf:
            dist = lambda : round(np.random.normal())
        if not l_inf and r_inf:
            dist = lambda : round(np.random.lognormal() + dom.sub)
        if l_inf and not r_inf:
            dist = lambda : round(-np.random.lognormal() + dom.sup)
        if not l_inf and not r_inf:
            dist = lambda : np.random.randint(dom.sub, dom.sup)

    elif type(space) == Continuous :
        dom = space.domain
        assert type(dom) == Intervall
        l_inf = (dom.sub == float('-inf'))
        r_inf = (dom.sup == float('inf'))

        if l_inf and r_inf:
            dist = np.random.normal
        if not l_inf and r_inf:
            dist = lambda : np.random.lognormal() + dom.sub
        if l_inf and not r_inf:
            dist = lambda : -np.random.lognormal() + dom.sup
        if not l_inf and not r_inf:
            dist = lambda : np.random.uniform(dom.sub, dom.sup)

    elif isinstance(space, Constant):
        dist = lambda : space.domain

    else:
        raise DistributionInferenceError(
            'No default distribution for type: %s' % type(space))

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
