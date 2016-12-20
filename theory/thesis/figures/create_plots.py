from scipy.stats import multivariate_normal as gauss
import GPy
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['xtick.labelsize'] = 16

kern = GPy.kern.RBF(1.)

x = np.linspace(0, 10, 201).reshape([-1,1])

K = kern.K(x)


# plot priors
for i in range(3):
    y = gauss.rvs(np.zeros(len(x)), K)
    plt.plot(x,y)
plt.savefig(filename='prior_plot.pdf', format='pdf')


# plot with noise
x,y = zip((2,2), (4,3), (7,-1))
X = np.array(x).reshape(-1,1)
Y = np.array(y).reshape(-1,1)
plt.figure()
model = GPy.models.GPRegression(X, Y, kernel=kern)
model.plot()
plt.savefig(filename='posterior_with_noise.pdf', format='pdf')


# plot fit without noise
kern = GPy.kern.RBF(1.)

x,y = zip((2,2), (4,3), (7,-1))
X = np.array(x).reshape(-1,1)
Y = np.array(y).reshape(-1,1)
plt.figure()
model = GPy.models.GPRegression(X, Y, kernel=kern)
model.Gaussian_noise.variance = 0.0
model.plot()
plt.savefig(filename='posterior_no_noise.pdf', format='pdf')

# plot with exp kernel with noise
kern = GPy.kern.Exponential(1.)
x,y = zip((2,2), (4,3), (7,-1))
X = np.array(x).reshape(-1,1)
Y = np.array(y).reshape(-1,1)
plt.figure()
model = GPy.models.GPRegression(X, Y, kernel=kern)
model.plot()
plt.savefig(filename='posterior_exp.pdf', format='pdf')
