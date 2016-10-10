import sys
import os
sys.path.insert(1, os.path.abspath('..'))

import numpy as np
from sklearn.linear_model import ElasticNet
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error as mse

from hypara.data_access import Path
from hypara.parameter import N,R,Parameter
from hypara.optimizer import RandomOptimizer


data = (Path() / "automatic_statistician/02-solar.csv").read()
X,y = data['X'], data['y']

def RMSE(x, y):
    x = x.ravel()
    y = y.ravel()
    return np.sqrt(sum((x-y)**2)/len(x))


def ml_algorithm(alpha, l1_ratio, maxorder, bias):

    X_train, X_val, y_train, y_val = train_test_split(X, y)

    # create designmatrix for training
    design = np.array([
        X_train**i for i in
        range(abs(bias-1), maxorder+1)]).T

    # train, predict and validate
    m = ElasticNet(alpha, l1_ratio)
    #print('design', design.shape, y_train.shape, maxorder, alpha, l1_ratio)
    m.fit(design, y_train)

    # create designmatrix for validation
    design = np.array([
        X_val**i for i in
        range(abs(bias-1), maxorder+1)]).T

    y_pred = m.predict(design)
    error = mse(y_pred, y_val)

    return error


paraspace = Parameter({
    'alpha' : R,
    'l1_ratio' : R,
    'maxorder' : N[1:],
    'bias' : {True, False},
})

ro = RandomOptimizer(ml_algorithm, paraspace)
ro.optimize(1000)

best = ro.get_best()
print('\nAnd the answer is:', best)


# create designmatrix for training
design = np.array([
    X**i for i in
    range(abs(bias-1), maxorder+1)]).T

# train, predict and validate
m = ElasticNet(alpha, l1_ratio)
m.fit(design, y)

# create designmatrix for validation
x = np.linspace(0, 100)
design = np.array([
    X_val**i for i in
    range(abs(bias-1), maxorder+1)]).T

y_pred = m.predict(design)
error = mse(y_pred, y_val)