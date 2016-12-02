# %% Create objective Function
from pylab import *
import scipy.stats as stats
import GPy
objfunc = lambda x : (x**2 - 10*x*sin(x) + cos(x-1)*3) + (x-4)**2
x = linspace(-20,20,101)
#plot(x, objfunc(x))
#show()


# %% Define some functions
def get_extendet_grid(X, n, ratio):
    # get a +10% grid around already evaluated points
    xmin = array(X).max(axis=0)
    xmax = array(X).min(axis=0)
    ext = (xmax - xmin)*ratio
    xmin -= ext
    xmax += ext
    grid = vectorize(linspace)(xmin, xmax, n)
    return grid


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

# %% Initialize model and evaluation points
kernel = GPy.kern.RBF(input_dim=1, variance=1., lengthscale=1.)
X = [-30, 20]
Y = [objfunc(x) for x in X]
best_y = min(Y)


# %% Plot func
def plot_stuff():
    plot()
    axhline(best_y, c='y')
    axvline(best_x, c='g')
    _x = linspace(-2,5,101)
    plot(X_eval, objfunc(X_eval))
    grid()
    show()


# %% Do Bayesian Optimization
# for i in range(100):
mX = reshape(X, (-1,1))
mY = reshape(Y, (-1,1))
m = GPy.models.GPRegression(mX, mY, kernel)
m.optimize()
X_eval = get_extendet_grid(X, n=101, ratio=0.1)
X_eval = reshape(X_eval, (-1,1))
Xe_mean, Xe_var = m.predict(X_eval)
best_y = min(best_y, min(Y))
ei_array = ei1d(Xe_mean, Xe_var, best_y)
best_x = X_eval[argmax(ei_array), 0]
new_y = objfunc(best_x)
X.append(best_x)
Y.append(new_y)

print(len(X))
print(best_y, best_x, new_y)
print(X)
print(Y)

plot_stuff()

#mes = input('Finished iteration: %s best_x=' % i)
#if mes == 'exit':
#    continue
