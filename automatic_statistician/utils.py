import numpy as np

def RMSE(x, y):
    x = x.ravel()
    y = y.ravel()
    return np.sqrt(sum((x-y)**2)/len(x))


def calculate_BIC(model):

    """
    Calculate the Bayesian Information Criterion (BIC) for a GPy `model` with maximum likelihood hyperparameters on a given dataset.
    https://en.wikipedia.org/wiki/Bayesian_information_criterion
    """
    # model.log_likelihood() is the natural logarithm of the marginal likelihood of the Gaussian process.
    # len(model.X) is the number of data points.
    # model._size_transformed() is the number of optimisation parameters.
    return - 2 * model.log_likelihood() + len(model.X) * np.log(model._size_transformed())