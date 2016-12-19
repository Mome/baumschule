# %% preliminaries
import sys, os

from pylab import *
from treefarm import *
from treefarm.minimizers.flatgp import FlatGPMinimizer, expected_improvement
from treefarm.core.utils import get_minium_states
from treefarm.core.space_utils import get_subspace, to_space
from time import sleep
import GPy

kernel_dict = {
    'RBF' : GPy.kern.RBF,
    'EXP' : GPy.kern.Exponential,
    'BIAS': GPy.kern.Bias,
    'LINEAR' : GPy.kern.Linear,
}

K = convert(set(kernel_dict.keys()))
K.symbol = 'K'
K = op(kernel_dict.get)(K)(1)

G = join()
G <<= K+G | K*G | K
G = simplify(G)

if os.path.exists('wild_kernel_names.npy'):
    names = list(np.load('wild_kernel_names.npy'))
else:
    names = []

if os.path.exists('wild_kernel_search.npy'):
    perf_stor = list(np.load('wild_kernel_search.npy'))
else:
    perf_stor = []

def str_deep(kern):
    try :
        L = [str_deep(k) for k in kern.parts]
        out = kern.name + '(' + ','.join(L) + ')'
    except:
        out = kern.name
    return out

@operation
def test_kernel(kernel):

    def f(x):
        return sin(x) * x / 2 + x**2 / 20 - 10*exp(-(x - 10)**2) + 8

    search_space = op(f)(R[-1000:1000])

    print('test kernel:', str_deep(kernel))

    outer_iterations = 10
    for i in range(outer_iterations):
        print('iteration', i, end='')

        obj = minimize(
            search_space = search_space,
            max_iter = 30,
            minimizer = FlatGPMinimizer(search_space, kernel=kernel),
            )
        obj.run()
        if 'min_perfs' not in locals():
            min_perfs = np.array(get_minium_states(obj.minimizer.protocol))
        else:
            min_perfs += np.array(get_minium_states(obj.minimizer.protocol))
        print(':', min_perfs[-1]/(i+1))

    out = min_perfs / outer_iterations
    perf_stor.append(out)
    names.append(str_deep(kernel))
    return out[-1]


kernel_ss = test_kernel(G)

min_obj = minimize(kernel_ss, max_iter=10)


#min_obj.run()

def plot_and_dump():
    _perf_stor = np.array(perf_stor)
    _perf_stor.dump('wild_kernel_search.npy')
    np.array(names).dump('wild_kernel_names.npy')

    # %%
    figure("Performances")
    for k, mperfs in zip(names, _perf_stor):
        plot(mperfs, label=str(k))
    legend()

    figure("log-Performances")
    for k, mperfs in zip(names, _perf_stor):
        plot(np.log(mperfs), label=str(k))
    legend()
    show()
