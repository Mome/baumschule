import numpy as np 
import random

from . import parameter as p


# ------ Distributions ------ #

def normal(mean=0, std=1, *, name=None):
    return p.Parameter(
        domain = p.R,
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


# --- sample from parameters -- #


def sample(param):

    if isinstance(param, p.Call):
        domsamp = param.domain.sample()
        log.debug('In sample of %s: %s, %s' % (param.operator.name, type(domsamp), type(param.domain)))
        if isinstance(domsamp, Sequence) and isinstance(domsamp, Mapping):
            res = param.operator.func(*domsamp, **domsamp)
        elif isinstance(domsamp, Sequence):
            res = param.operator.func(*domsamp)
        elif isinstance(domsamp, Mapping):
            res = param.operator.func(**domsamp)
        else:
            res = param.operator.func(domsamp)
        return res

    if param.dist:
        return param.dist()
    return defaultdist(param)()


def defaultdist(param):

    if isinstance(param, p.JoinedSpace):

        def dist():
            # choose subspace
            ss = random.sample(param.domain, 1)[0]
            return ss.sample()

    elif isinstance(param, p.NamedSpace):
        dist =  lambda : {
            k:v.sample()
            for k,v in param.domain.items()
        }

    elif isinstance(param, p.ProductSpace):
        dist = lambda : [D.sample() for D in param.domain]

    elif isinstance(param, p.Categorical):
        dist = lambda : random.sample(param.domain, 1)[0]

    elif isinstance(param, p.Discrete):
        dom = param.domain
        assert type(dom) == p.Intervall
        l_inf = (dom.sub == float('-inf'))
        r_inf = (dom.sup == float('inf'))

        if l_inf and r_inf:
            sample_f = lambda : round(np.random.normal())
        if not l_inf and r_inf:
            sample_f = lambda : round(np.random.lognormal() + dom.sub)
        if l_inf and not r_inf:
            sample_f = lambda : round(-np.random.lognormal() + dom.sup)
        if not l_inf and not r_inf:
            sample_f = lambda : np.random.randint(dom.sub, dom.sup)
        
        return sample_f

    elif isinstance(param, p.Continuous):
        dom = param.domain
        assert type(dom) == p.Intervall
        l_inf = (dom.sub == float('-inf'))
        r_inf = (dom.sup == float('inf'))

        if l_inf and r_inf:
            sample_f = np.random.normal
        if not l_inf and r_inf:
            sample_f = lambda : np.random.lognormal() + dom.sub
        if l_inf and not r_inf:
            sample_f = lambda : -np.random.lognormal() + dom.sup
        if not l_inf and not r_inf:
            sample_f = lambda : np.random.uniform(dom.sub, dom.sup)
        
        return sample_f

    elif isinstance(param, p.Constant):
        dist = lambda : param.domain

    return dist