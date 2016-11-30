
from itertools import chain

import numpy as np

from ..core.parameters import Apply, Primitive, join, Operation, Combination
from ..core.domains import ParameterList
from ..core.sspace_utils import expand, fc_shape

default_av = 1. # aqisition value for unseen expansions

class TreeFarm:

    def __init__(self, search_space):
        self.search_space = search_space
        self.fc_shape = fc_shape(search_space, False)
        self.expansions = np.empty(self.fc_shape, dtype=object)
        self.av = default_av

    def update_av(self):
        self.av = max(
            ex.av if ex else default_av
            for ex in self.expansions.flat)

    def iteration(self):
        ...






def subspace_of(space1, space2):
    # wow this is hard

    if isinstance(space1, Apply):
        if space1.operation ==
        type1 = 'apply'
    if isinstance(space1, Primitive):
        ...



    if isinstance(space1, Apply) and isinstance(space2, Apply):
        ...

    elif isinstance(space1, Apply):
        ...

    elif isinstance(space1, Apply):
        ...

    else


def primitive_in_primitive(self, prim1, prim2):
    ...
