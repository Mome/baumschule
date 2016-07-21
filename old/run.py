import statistician as stat
import kernel_grammar as kern_gram
import evaluate_kernels as eval_kern
import numpy as np
import matplotlib.pyplot as plt
import GPy

target_func = lambda x : np.sqrt(np.abs(x)) + np.sin(x) + np.cos(x*3)/2 + 3
#target_func = lambda x : x + 3


minx, maxx = (-7,7)
X = (maxx-minx)*np.random.rand(200, 1) + minx
Y = target_func(X) + np.random.randn(len(X), 1)/2

print(X.shape, Y.shape)


x = np.linspace(-7,7,101)
plt.plot(x, target_func(x))
plt.scatter(X,Y)


eval_func = lambda node : eval_kern.evaluate_model(node, X, Y, target_func)

treeroot, error = kern_gram.kernel_search(
    operations = ['*', '+'],
    kernels = ['EXP', 'RBF', 'BIAS', 'LINEAR'],
    eval_func =  eval_func,
    time_out=600
    )

print('Search finished!')

kernel = eval_kern.build_kernel(treeroot.node)
m = GPy.models.GPRegression(X,Y,kernel)

m.plot()

print('\nBefore optimization', m, '\n')

m.optimize()

print('\nAfter optimization', m, '\n')

print('Best model:', treeroot.node, error)

m.plot()
plt.show()