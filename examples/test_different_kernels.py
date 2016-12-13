# %% preliminaries
import sys

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

kernels = [
    GPy.kern.RBF(1),
    GPy.kern.RBF(1) + GPy.kern.Linear(1),
    GPy.kern.RBF(1) + GPy.kern.Bias(1),
    GPy.kern.RBF(1) + GPy.kern.Linear(1) + GPy.kern.Bias(1),
    GPy.kern.Linear(1) + GPy.kern.Bias(1),
    GPy.kern.Linear(1),
    GPy.kern.Bias(1),
]

kernels_str ="""RBF
RBF + Linear
RBF + Bias
RBF + Linear + Bias
Linear + Bias
Linear
Bias""".split('\n')

def test_kernel(kernel):

    def f(x):
        return sin(x) * x / 2 + x**2 / 20 - 10*exp(-(x - 10)**2) + 8

    search_space = op(f)(R[-1000:1000])

    print('test kernel:', kernel)
    sys.stdout.flush()

    for i in range(outer_iterations):
        print('iteration', i, end='')

        obj = minimize(
            search_space = ss,
            max_iter = 30,
            minimizer = FlatGPMinimizer(ss, kernel=kernel),
            )
        obj.run()
        if 'min_perfs' not in locals():
            min_perfs = np.array(get_minium_states(obj.minimizer.protocol))
        else:
            min_perfs += np.array(get_minium_states(obj.minimizer.protocol))
        print(':', min_perfs[-1]/(i+1))

    return min_perfs / outer_iterations



min_perfss = np.array([
    test_kernel(search_space, k, 10)
    for k in kernels
])

min_perfss.dump('kerel_test.npy')

# %%
figure("Performances")
for k, mperfs in zip(kernels_str, min_perfss):
    plot(mperfs, label=str(k))
legend()

figure("log-Performances")
for k, mperfs in zip(kernels_str, min_perfss):
    plot(np.log(mperfs), label=str(k))
legend()
show()
