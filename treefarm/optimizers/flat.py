
from itertools import count, chain

import numpy as np
from scipy.stats import stats
import GPy

from ..core.parameters import (
    Primitive, Categorical, Continuous, Discrete, Parameter)
from ..core.optimizer import SequentialOptimizer

class FlatGPOptimizer(SequentialOptimizer):
    def __init__(self, search_space, kernel_cls=None):
        search_space = list(search_space)
        assert all(isinstance(ss, Primitive) for ss in search_space)

        dim_number = sum(
            len(ss) if type(ss) is Categorical else 1
            for ss in search_space)

        if kernel_cls == None:
            kernel_cls = GPy.kern.RBF

        self.transform = construct_transform_func(search_space)
        self.kernel = kernel_cls(dim_number)
        self._construct_transform_func(search_space)
        self.dim_number = dim_number
        self.search_space = search_space

    def fit_model(self, X, Y):
        X = array([transform(x) for x in X])
        m = GPy.models.GPRegression(X, Y, ker)
        m.optimize()
        return m

    def pick_next(self):
        ss = prod(*self.search_space)
        eval_points = tuple(map(sample, ss))
        for ep in eval_points:
            ...


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
            return tuple(it)

        return transfrom



def fit_gp(*args):
    ...



def expected_information(mean_Y, var_Y, best_y):
    """
    One dimensional Expected Improvement.

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
