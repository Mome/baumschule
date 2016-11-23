



def fit_gp(crown, kernel):
    dim = sum(for node in crown)


def ei1d(mean_Y, var_Y, best_y):
    """
    One dimensional Expected Improvement.

    Paramameters
    ------------
    mean_Y : ndarray
    var_Y : ndarray
    best_y : saclar
    """

    # TODO use multivar normal here ??
    ratio = best_y / sqrt(var_Y)
    lhs = (best_y - mean_Y)*stats.norm.cdf(ratio)
    rhs = stats.norm.pdf(ratio)
    return lhs - rhs



# %%
from numpy import *
a = array([1,2,3])
