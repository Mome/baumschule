
from itertools import count, chain
from math import inf

import numpy as np
from scipy.stats import stats
import GPy

from ..core.parameters import (
    Primitive, Categorical, Continuous, Discrete, Parameter)
from ..core.optimizer import SequentialOptimizer
from . import RandomOptimizer
from .sspace_utils import fc_shape, expand
from ..core.random_variables import sample


class FlatGPOptimizer(SequentialOptimizer):
    """
    Flat Gaussian Process Optimizer for deterministic response surface.

    Fits a Gaussian process to a list of primitive spaces.
    Transforms categorical spaces into a one-hot coding.
    """

    def __init__(self, search_space, protocol, engine,
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
            aqui_optimizer :
                aquisition function optimizer (default RandomOptimizer)
        """

        # assure integrity of search_space and call superconstructor
        search_space = list(search_space)
        assert all(isinstance(ss, Primitive) for ss in search_space)
        super().__init__(search_space, protocol, engine)

        # infere argumments
        if aqui_func == None:
            aquifunc = expected_improvement
        if kernel_cls == None:
            kernel_cls = GPy.kern.RBF
        if aquiopt_cls == None:
            aquiopt_cls = RandomOptimizer

        # calc dimensions of the Gaussian process
        dim_number = sum(
            len(ss) if type(ss) is Categorical else 1
            for ss in search_space)

        # kerenel and transformation function
        self.transform = self.construct_transform_func(search_space)
        self.kernel = kernel_cls(dim_number)

        # store to instance
        self.dim_number = dim_number
        self.aquiopt_cls = aquiopt_cls
        self.aquiopt_factory = aquiopt_factory
        self.best = inf


    def fit_model(self):
        X, Y = zip(self.samples)
        X = array([transform(x) for x in self.X])
        print(X.shape)
        m = GPy.models.GPRegression(X, Y, self.kernel)
        m.optimize()
        return m


    def pick_next(self):

        if len(self.protocol) < 2:
            return sample(self.search_space)

        m = self.fit_model()

        def objfunc(point):
            point = self.transform(point)
            nonlocal m
            x_mean, x_var = m.predict(point)
            return self.aquifunc(point)

        opt_obj = optimize_func(
            func = objfunc,
            param = self.search_space,
            optimizer = self.aquiopt_cls,
            max_iter = 100,
            return_object = True,
        )
        opt_obj.run()
        points, perf = opt_obj.optimizer.samples
        best = points[np.argmax(perf)]

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
        translations = {}
        for i,ss in enumerate(search_space):
            if type(ss) != Categorical:
                continue
            one_hot = lambda j : tuple(int(j==x) for x in range(len(ss)))
            code = map(one_hot, count())
            items = zip(ss.domain, code)
            translations[i] = dict(items)

        def transfrom(vector):
            it = chain.from_iterable(
                translations[i][val] if i in translations else [val]
                for i,val in enumerate(vector))
            return np.array(it).reshape(-1, 1)

        return transfrom



def expected_improvement(mean_Y, var_Y, best_y):
    """
    The expected improvment aquisition function.

    Paramameters
    ------------
    mean_Y : ndarray
    var_Y : ndarray
    best_y : saclar
    """

    ratio = best_y / sqrt(var_Y)
    lhs = (best_y - mean_Y)*stats.norm.cdf(ratio)
    rhs = stats.norm.pdf(ratio)
    return lhs - rhs


def get_crown(search_space):
    crown = []

    def _find_choice_points(subspace):
        if (isinstance(search_space, Apply)
            and search_space.operation != join):
                _find_choice_points(search_space.operation)
                for subs in search_space.domain:
                    _find_choice_points(subs)
        else:
            crown.append(subspace)

    _find_choice_points(search_space)
    return crown
