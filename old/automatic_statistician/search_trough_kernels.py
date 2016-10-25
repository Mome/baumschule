import GPy
from kernel_composition import KernelComposition
import numpy as np
from utils import RMSE, calculate_BIC
import matplotlib.pyplot as plt
import signal
import sys
import scipy.io as sio
from numpy.random import shuffle
from statistician import DataSet

import warnings
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning, module="numpy")


max_depth = 4
compositions = ['*', '+']
kernels = ['RBF', 'Per', 'Lin', 'Brown', 'RQ']
refresh_splitting = False
do_crossval = False


# load data
data = DataSet.load('02-solar.mat')

print(data)

X = data['X']
Y = data['y']

print()
print('Ctrl+C to stop search ones.')

# finish search with Ctrl+C
terminate = False
def signal_handler(signal, frame):
    global terminate
    if terminate:
        sys.exit(0)
    else:
        print(' --> Finishing! Do again to kill!')
        terminate = True
signal.signal(signal.SIGINT, signal_handler)

init_kern = KernelComposition()

kernel_search = init_kern.search(basekernels=kernels, compositions=compositions)

scores = []
error = None

while not terminate:

    if do_crossval and (error is None or refresh_splitting):
        # split data in two sets
        random_index = np.arange(len(X))
        shuffle(random_index)
        cutpoint = 2*len(X)//3
        train_index = random_index[:cutpoint]
        val_index = random_index[cutpoint:]
        X_train = X[train_index]
        X_val = X[val_index]
        Y_train = Y[train_index]
        Y_val = Y[val_index]

    try:
        K = kernel_search.send(error)
    except Exception as e:
        print('Search Error:', e)
        terminate = True
        continue

    if max_depth and len(K.kernels) > max_depth:
        print('Max depth reached!')
        terminate = True
        continue

    # fit the model
    if do_crossval:
        m = GPy.models.GPRegression(X_train, Y_train, K.compile())
    else:
        m = GPy.models.GPRegression(X, Y, K.compile())
    m.optimize() # magic

    # Crossvalidation
    #val_X = (X.max()-X.min())*np.random.rand(n,1) + X.min()
    #real_Y = target_func(val_X)
    if do_crossval:
        pred_mean, pred_var = m.predict(X_val)
        error = RMSE(Y_val, pred_mean)
    else:
        # Bayesian Information Criterion
        error = calculate_BIC(m)

    scores.append((K, error))
    print(error, '\t', m.log_likelihood(), '\t', K)

print('Search finished!')



kernels, errors = zip(*scores)

min_error = min(errors)
best_K = kernels[errors.index(min_error)]

m = GPy.models.GPRegression(X,Y, best_K.compile())

# plotting
#x = np.linspace(-7,7,101)
#plt.plot(x, target_func(x))
#plt.scatter(X,Y)

m.plot()
plt.title(str(best_K) + ', unoptimized')

print('\nBefore optimization', m, '\n')

m.optimize()

print('\nAfter optimization', m, '\n')

print('Best model:', best_K, min_error)

m.plot()
plt.title(str(best_K) + ', optimized')
plt.show()