
from itertools import count, chain
from math import inf
import logging
from functools import reduce

import numpy as np
import scipy.stats as stats
import GPy

from ..core.parameters import (
    Primitive, Categorical, Continuous, Discrete, Parameter, quote)
from ..core.optimizer import (
    SequentialOptimizer, FlatOptimizer, optimize_func)
from .simple import RandomOptimizer
from ..core.space_utils import fc_shape, expand, get_crown, get_subspace
from ..core.random_variables import sample

log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel('DEBUG')


class FlatGPOptimizer(FlatOptimizer, SequentialOptimizer):
    """
    Flat Gaussian Process Optimizer for deterministic response surface.

    Fits a Gaussian process to a list of primitive spaces.
    Transforms categorical spaces into a one-hot coding.
    """

    def __init__(
        self,
        search_space,
        engine = None,
        aquifunc = None,
        kernel_cls = None,
        aquiopt_cls = None,
        ):
        """
        Parameters
        ----------
            search_space : core.parameter.Parameter
            protocol : core.protocol.Protocol
            engine : core.computing_engine.ComputingEngine
            aquifunc :
                aquisition function (default EI)
            kernel_cls :
                kernel class (default RBF)
            aquiopt_cls:
                aquisition function optimizer class (default RandomOptimizer)
        """

        super().__init__(search_space=search_space, engine=engine)

        # infere argumments
        if aquifunc == None:
            aquifunc = expected_improvement
        if kernel_cls == None:
            kernel_cls = [GPy.kern.RBF, GPy.kern.Bias]
        if aquiopt_cls == None:
            aquiopt_cls = RandomOptimizer

        # create kernel
        self.kernel = reduce(
            lambda x,y : x + y, (K(self.dim_number) for K in kernel_cls))

        # store to instance
        self.aquifunc = aquifunc
        self.aquiopt_cls = aquiopt_cls


    def fit_model(self):
        X, Y = zip(*self.protocol)
        X = np.array([self.transform(x) for x in X])
        Y = np.array(Y).reshape(-1, 1)
        log.debug('X.shape %s' % (X.shape,))
        m = GPy.models.GPRegression(X, Y, self.kernel)
        m.Gaussian_noise.constrain_fixed(0.0)
        m.optimize()
        return m


    def pick_next(self):

        if len(self.protocol) < 2:
            return sample(self.search_space)

        self.model = self.fit_model()
        #m.plot()

        def merrit_func(point):
            point = self.transform(point)
            point = np.array(point).reshape([1,-1])
            x_mean, x_var = self.model.predict(point)
            x_mean = x_mean[0][0]
            x_var = x_var[0][0]
            return self.aquifunc(x_mean, x_var, self.best)

        opt_obj = optimize_func(
            func = merrit_func,
            param = quote(self.search_space),
            optimizer = self.aquiopt_cls,
            max_iter = 100,
            return_object = True,
        )
        opt_obj.run()
        points, errors = zip(*opt_obj.optimizer.protocol)
        best = points[np.argmax(errors)]
        best = get_subspace(best, (0,0))

        return best


def expected_improvement0(mean_Y, var_Y, best_y):
    """
    The expected improvment aquisition function.

    Paramameters
    ------------
    mean_Y : ndarray
    var_Y : ndarray
    best_y : saclar
    """

    ratio = best_y / np.sqrt(var_Y)
    lhs = (best_y - mean_Y)*stats.norm.cdf(ratio)
    rhs = stats.norm.pdf(ratio)
    return lhs - rhs


def expected_improvement(mean_Y , var_Y, best_y):
    s = np.sqrt(var_Y)
    ratio = (best_y - mean_Y) / s
    lhs = (best_y - mean_Y)*stats.norm.cdf(ratio)
    rhs = stats.norm.pdf(ratio)*s
    return lhs + rhs
