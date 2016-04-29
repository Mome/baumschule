import GPy
from kernel_composition import KernelComposition
import numpy as np
from utils import RMSE, calculate_BIC
import matplotlib.pyplot as plt
import signal
import sys
import scipy.io as sio

max_depth = 10
n = 50 
compositions = ['*', '+']
kernels = ['SE', 'LIN', 'PER', 'RQ']

# create sample data
# target_func = lambda x : np.sqrt(np.abs(x)) + np.sin(x) + np.cos(x*3)/2 + 3
# minx, maxx = (-7,7)
# X = (maxx-minx)*np.random.rand(200, 1) + minx
# Y = target_func(X) + np.random.randn(len(X), 1)/2

# load data
#data = sio.loadmat('../data/03-mauna2003.mat') # figure 4
data = sio.loadmat('../data/02-solar.mat') # figure 5
#data = sio.loadmat('../data/01-airline.mat') # figure 6

X = data['X']
Y = data['y']

print('Data shape:', X.shape, Y.shape)

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


kernel_search = KernelComposition.search(basekernels=kernels, compositions=compositions)

scores = []
error = None

while not terminate:

    try:
        K = kernel_search.send(error)
    except Exception as e:
        print(e)
        terminate = True
        continue

    if max_depth and len(K.kernels) > max_depth:
        terminate = True
        continue

    # fit the model
    m = GPy.models.GPRegression(X, Y, K.compile())
    m.optimize() # magic

    # Crossvalidation
    #val_X = (X.max()-X.min())*np.random.rand(n,1) + X.min()
    #real_Y = target_func(val_X)
    #pred_mean, pred_var = m.predict(val_X)
    #error = RMSE(real_Y, pred_mean)

    # Bayesian Information Criterion
    error = calculate_BIC(m)

    scores.append((K, error))
    print(error, '\t', K)

print('Search finished!')



kernels, errors = zip(*scores)

min_error = min(errors)
best_K = kernels[errors.index(min_error)]

m = GPy.models.GPRegression(X,Y, K.compile())

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