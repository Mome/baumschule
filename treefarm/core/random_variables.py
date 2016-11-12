
import numpy as np

from .parameters import (
    Apply, Categorical, Discrete, Continuous
)


# --- sample from spaces -- #
def sample(param):
    if param.dist:
        dist = param.dist
    dist = get_default_dist(param)
    return dist()


def get_default_dist(param):
    """
    Returns a function
    """


    if type(param) is Apply:

        if param.operation == join:
            def dist():
                sub = random.sample(space.domain, 1)[0]
                return sample(sub)

        else:
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

    else:
        dist = lambda : param

    return dist


def default_categorical(param):

    def dist():
        return random.sample(param.domain, 1)[0]

    return dist


def default_discrete(param):

    if type(param.domain) == Interval:
        sub = param.domain.sub
        sup = param.domain.sup
        l_inf = (sub == float('-inf'))
        r_inf = (sup == float('inf'))
    else:
        dom = sorted(param.domain)
        sub = dom[0]
        sup = dom[-1]
        l_inf = r_inf = False

    if l_inf and r_inf:
        dist = lambda : round(np.random.normal())
    if not l_inf and r_inf:
        dist = lambda : round(np.random.lognormal() + sub)
    if l_inf and not r_inf:
        dist = lambda : round(-np.random.lognormal() + sup)
    if not l_inf and not r_inf:
        dist = lambda : np.random.randint(sub, sup)

    return dist


def default_continous(param):
    dom = param.domain
    assert type(dom) == Intervall; 'Continous domain type must be Intervall.'

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
