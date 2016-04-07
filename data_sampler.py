import numpy as np
from functools import partial
from numpy import pi, inf, exp
from collections.abc import Sequence, Mapping

class DataSampler:
    def __init__(self, samplers, sample_number_dists):

        if not isinstance(sample_number_dists, Sequence):
            sample_number_dists = [sample_number_dists]*len(samplers)

        self.samplers = samplers
        self.sample_number_dists = sample_number_dists

    def sample(self):
        sample_numbers = _sample(self.sample_number_dists)
        data_sets = [s.sample(n) for s,n in zip(self.samplers, sample_numbers)]
        return data_sets


class SimpleFunctionSampler:
    def __init__(self, func, sample_dist, residual_dist):
        self.func = func
        self.sample_dist = sample_dist
        self.residual_dist = residual_dist

    def sample(self, sample_number):
        """Generates a simple regression problem. (1D dependent and independet variable)"""
        X = self.sample_dist([sample_number])
        Y = self.func(X) + self.residual_dist([sample_number])
        return X,Y


class FunctionDistribution:
    """"Wraps a function together with a distribution over its parameters."""

    def __init__(self, func_factory, paramter_dists):
        self.func_factory = func_factory
        self.parameter_dists = paramter_dists

    def sample(self):
        """Sample a function from the parameter distributions."""

        parameters = _sample(self.parameter_dists)

        if type(parameters) == dict:
            func = self.func_factory(**parameters)
        else:
            func = self.func_factory(*parameters)
        
        return func


def uniform(a, b):
    assert a <= b
    return lambda x=() : np.random.rand(*x)*(b-a) + a

def normal(mu=0, sigma=1, positive=False):
    assert sigma >= 0

    def dist(x=()):
        sample = np.random.randn(*x)*sigma + mu
        if positive:
            sample = abs(sample)
        return sample

    return dist


def lognormal(mu=0, sigma=1):
    assert sigma >= 0
    return lambda x=() : exp(np.random.randn(*x)*sigma + mu)


def _sample(distributions):

    if isinstance(distributions, Mapping):
        samples = {
            name : dist() if callable(dist) else dist
            for name, dist in distributions.items()
        }
    
    elif isinstance(distributions, Sequence):
        samples = [
            dist() if callable(dist) else dist
            for dist in distributions
        ]
    
    else: raise TypeError('distributions must be Mapping or Sequence!')

    return samples


# --- Functions --- #
def linear(a=1,b=0):
    return lambda x: a*x + b

def sinus(phase=0, ampl=1, freq=1, b=0):
    return lambda x: np.sin(freq*x + phase)*ampl + b

def gabor(lam,theta,psi,phi,gamma,scale):
    def func(x):
        x_prime = x*np.cos(theta)
        y_prime = -x*np.sin(theta)
        in_exp = -(x_prime**2 + gamma**2*y_prime**2)/(2*phi**2)
        in_cos = 2*pi*x_prime/lam + psi
        return scale*np.exp(in_exp)*np.cos(in_cos)
    return func