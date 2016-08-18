import numpy as np
import scipy.io  # this is the SciPy module that loads mat-files
import matplotlib.pyplot as plt
from datetime import datetime, date, time
import pandas as pd
import os

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
    return - 2 * model.log_likelihood() + np.log(len(model.X)) * model.size


def read_mat(path):
    """Reads a pandas.DataFrame from a matfile"""
    # source http://poquitopicante.blogspot.de/2014/05/loading-matlab-mat-file-into-pandas.html
    mat = scipy.io.loadmat(path)  # load mat-file
    mdata = mat['measuredData']  # variable in mat file
    mdtype = mdata.dtype  # dtypes of structures are "unsized objects"
    # * SciPy reads in structures as structured NumPy arrays of dtype object
    # * The size of the array is the size of the structure array, not the number
    #   elements in any particular field. The shape defaults to 2-dimensional.
    # * For convenience make a dictionary of the data using the names from dtypes
    # * Since the structure has only one element, but is 2-D, index it at [0, 0]
    ndata = {n: mdata[n][0, 0] for n in mdtype.names}
    # Reconstruct the columns of the data table from just the time series
    # Use the number of intervals to test if a field is a column or metadata
    columns = [n for n, v in ndata.iteritems() if v.size == ndata['numIntervals']]
    # now make a data frame, setting the time stamps as the index
    df = pd.DataFrame(np.concatenate([ndata[c] for c in columns], axis=1),
                      index=[datetime(*ts) for ts in ndata['timestamps']],
                      columns=columns)
    return df

def mat_to_csv(path):
    d = scipy.io.loadmat(path)
    x = pd.DataFrame(d['X'], columns=['x'])
    y = pd.DataFrame(d['y'], columns=['y'])
    df = pd.concat([x,y], axis=1)
    df = y
    new_name = os.path.splitext(os.path.basename(path))[0] + '.csv'
    df.to_csv(new_name)

def mat_to_hdf(path):
    d = scipy.io.loadmat(path)
    x = pd.DataFrame(d['X'])
    y = pd.DataFrame(d['y'])
    new_name = os.path.splitext(os.path.basename(path))[0] + '.hdf'
    x.to_hdf(new_name, 'X')
    y.to_hdf(new_name, 'y')