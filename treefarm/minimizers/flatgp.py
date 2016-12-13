
from itertools import count, chain
from math import inf
import logging
from functools import reduce

import numpy as np
import scipy.stats as stats
import GPy

from ..core.spaces import (
    Primitive, Categorical, Continuous, Discrete, Parameter, quote)
from ..core.minimizer import (
    SequentialMinimizer, FlatMinimizer, minimize_func)
from .simple import RandomMinimizer
from ..core.space_utils import fc_shape, expand, get_crown, get_subspace
from ..core.random_variables import sample

log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel('INFO')


class FlatGPMinimizer(FlatMinimizer, SequentialMinimizer):
    """
    Flat Gaussian Process Minimizer for deterministic response surface.

    Fits a Gaussian process to a list of primitive spaces.
    Transforms categorical spaces into a one-hot coding.
    """

    def __init__(
        self,
        search_space,
        engine = None,
        aquifunc = None,
        kernel = None,
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
                aquisition function minimizer class (default RandomMinimizer)
        """

        super().__init__(search_space=search_space, engine=engine)

        # infere argumments
        if aquifunc == None:
            aquifunc = expected_improvement
        if kernel == None:
            kernel = GPy.kern.Bias(1) + GPy.kern.Linear(1) + GPy.kern.RBF(1)
        if aquiopt_cls == None:
            aquiopt_cls = RandomMinimizer

        # create kernel
        """self.kernel = reduce(
            lambda x,y : x + y, (K(self.dim_number) for K in kernel_cls))"""

        # store to instance
        self.kernel = kernel
        self.aquifunc = aquifunc
        self.aquiopt_cls = aquiopt_cls
        self.auto_update = True
        self.best_aquival = None # best aquisition value
        self.best_aqui_instance = None # instance with best aquisition value


    def fit_model(self):
        X, Y = zip(*self.observers['protocol'])
        X = np.array([self.transform(x) for x in X])
        Y = np.array(Y).reshape(-1, 1)
        log.debug('X.shape %s' % (X.shape,))
        m = GPy.models.GPRegression(X, Y, self.kernel)
        m.Gaussian_noise.constrain_fixed(0.0)
        try:
            m.optimize()
        except np.linalg.linalg.LinAlgError as e:
            print('Optimization failed:', e.message)
        return m

    def update(self, best_perf=None):
        self.model = self.fit_model()

        if best_perf == None:
            best_perf = self.best_perf

        def merrit_func(point):
            point = self.transform(point)
            point = np.array(point).reshape([1,-1])
            x_mean, x_var = self.model.predict(point)
            x_mean = x_mean[0][0]
            x_var = x_var[0][0]
            return self.aquifunc(x_mean, x_var, best_perf)

        # make this an attribute and add clean function
        opt_obj = minimize_func(
            func = merrit_func,
            param = quote(self.search_space),
            minimizer = self.aquiopt_cls,
            max_iter = 100,
        )
        opt_obj.run()

        instances, aquivals = zip(*opt_obj.minimizer.observers['protocol'])
        index = np.argmax(aquivals)
        self.best_aquival = aquivals[index]
        bai = instances[index]
        bai = get_subspace(bai, (0, 0)) # remove merrit+quote
        self.best_aqui_instance = bai


    def pick_next(self):

        if len(self.observers['protocol']) < 2:
            return sample(self.search_space)

        if self.auto_update:
            self.update()

        return self.best_aqui_instance


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
