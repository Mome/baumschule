import numpy as np
import matplotlib.pyplot as plt

from treefarm import *
from treefarm.core.space_utils import get_subspace
from treefarm.core.utils import get_minium_states

plotting = False

def zero_counter(*point):
    return sum(x != 0 for x in point)

def summer(*point):
    return sum(point)

ss = op(zero_counter)(
    disc(list(range(10))),
    disc(list(range(10))),
    disc(list(range(10))),
    disc(list(range(10))),
    disc(list(range(10))),
    disc(list(range(10))),
)
max_iter = 100
sum_perfs1 = np.zeros(max_iter)
sum_perfs2 = np.zeros(max_iter)


for _ in range(10):
    # %% construct optimization object
    obj1 = minimize(
        search_space = ss,
        max_iter = max_iter-1,
        return_object = True,
        minimizer = "flatgp",
        )
    obj1.run()
    min_perfs1 = get_minium_states(obj1.minimizer.protocol)
    sum_perfs1 += min_perfs1

    # %%
    obj2 = minimize(
        search_space = ss,
        max_iter = max_iter-1,
        return_object = True,
        minimizer = "random",
        )
    obj2.run()
    min_perfs2 = get_minium_states(obj2.minimizer.protocol)
    sum_perfs2 += min_perfs2


# %%
if plotting:
    plt.figure("Performances")
    plt.plot(sum_perfs1 / 10, label='BO best')
    plt.plot(sum_perfs2 / 10, label='random')
    plt.legend()
    plt.show()
