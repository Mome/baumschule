
from itertools import count, chain
from math import inf
import logging

import numpy as np
import scipy.stats as stats
import GPy

from ..core.parameters import (
    Primitive, Categorical, Continuous, Discrete, Parameter, quote)
from ..core.optimizer import SequentialOptimizer, optimize_func
from .simple import RandomOptimizer
from ..core.space_utils import fc_shape, expand, get_crown, get_subspace
from ..core.random_variables import sample

log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel('DEBUG')


class FlatGPOptimizer(SequentialOptimizer):
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

        super().__init__(search_space, engine)

        # infere argumments
        if aquifunc == None:
            aquifunc = expected_improvement
        if kernel_cls == None:
            kernel_cls = GPy.kern.RBF
        if aquiopt_cls == None:
            aquiopt_cls = RandomOptimizer

        # calc dimensions of the Gaussian process
        dim_number = sum(
            len(ss) if type(ss) is Categorical else 1
            for ss in get_crown(search_space))

        # kernel and transformation function
        self.transform = self.construct_transform_func(search_space)
        self.kernel = kernel_cls(dim_number)

        # store to instance
        self.dim_number = dim_number
        self.aquifunc = aquifunc
        self.aquiopt_cls = aquiopt_cls

    def fit_model(self):
        X, Y = zip(*self.protocol)
        X = np.array([self.transform(x) for x in X])
        Y = np.array(Y).reshape(-1, 1)
        log.debug('X.shape %s' % (X.shape,))
        print('X', X)
        print('Y', Y)
        m = GPy.models.GPRegression(X, Y, self.kernel)
        m.optimize()
        return m

    def pick_next(self):

        if len(self.protocol) < 2:
            return sample(self.search_space)

        m = self.fit_model()
        #m.plot()

        def merrit_func(point):
            print('point1', point)
            point = self.transform(point)
            point = np.array(point).reshape([1,-1])
            print('point2', point)
            nonlocal m
            x_mean, x_var = m.predict(point)
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
        best = points[np.argmin(errors)]
        best = get_subspace(best, (0,0))

        return best

    @staticmethod
    def construct_transform_func(search_space):
        """
        Returns a function that maps points from the search space into
        a numerical vector space (i.e. applies one hot coding to categories)

        Example:
            If the third entry in a search space is {'A','B','C'},
            the translations become: {'A':(0,0,1), 'B':(0,1,0), 'C':(1,0,0)}
            transform([1,3,'A',9]) -> [1,3,0,0,1,9]
        """
        crown, crown_indices = get_crown(search_space, include_primitives=True)

        translations = {}
        for i,ss in enumerate(crown):
            if type(ss) != Categorical:
                continue
            one_hot = lambda j : tuple(int(j==x) for x in range(len(ss)))
            code = map(one_hot, count())
            items = zip(ss.domain, code)
            translations[i] = dict(items)

        def transform(tree):
            vector = [get_subspace(tree, i) for i in crown_indices]
            print('vector', vector)
            it = chain.from_iterable(
                translations[i][val] if i in translations else [val]
                for i,val in enumerate(vector))
            return np.array(tuple(it))

        return transform


def expected_improvement(mean_Y, var_Y, best_y):
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
