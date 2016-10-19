from sklearn import svm
from sklearn import datasets
from sklearn import cross_validation
from matplotlib.pyplot import *
import numpy as np
from sacred import Experiment



# load data
digits = datasets.load_digits()
print(digits.data.shape)
print(digits.target.shape)


ex = Experiment('sacred_test_config')

@ex.config
def my_config():
    gamma = 0.001
    C = 100.
    kernel = 'rbf'

@ex.automain
def execute_experiment(gamma, C, kernel):
    clf = svm.SVC(
        gamma = gamma,
        C = C,
        kernel = kernel)

    # split data
    X_train, X_test, y_train, y_test = cross_validation.train_test_split(digits.data, digits.target)

    # train model
    clf.fit(X_train, y_train)

    # validate
    error = clf.score(X_test, y_test)

    print(error)
    return error


