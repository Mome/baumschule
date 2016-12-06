
from itertools import chain
from math import inf
import time
import logging
import random

import numpy as np

from .flatgp import FlatGPMinimizer
from ..core.spaces import Apply, Primitive, join, Operation, Combination
from ..core.domains import ParameterList
from ..core.space_utils import expand, fc_shape
from ..core.minimizer import SequentialMinimizer
from ..core.protocol import PerfDictProtocol

log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel('DEBUG')

default_av = 1. # aqisition value for unseen expansions

# TODO maybe join TreeFarm and Node ???

class TreeGPMinimizer(SequentialMinimizer):

    def __init__(self, search_space, threshold=1.0):
        super().__init__(search_space)
        self.root = Node(search_space, threshold, self)

    def compute_next(self):
        leaf = self.root.next_node()
        result = leaf.minimizer.compute_next()
        logging.debug('chose_instance:%s' % result)
        start_time = time.time()

        if result['perf'] < self.best_perf:
            # if performance better: update everything
            self.best = result['perf']
            self.best_instance = result['instance']
            self.root.update(self.best)
        else:
            # if performance worse: only update leaf
            # (includes donwn-propagation of aquisition)
            leaf.update(self.best, down_propagate=True)

        result['update_time'] = time.time() - start_time

        for ob in self.observers.values():
            ob.write(**result)

        return result


class Node:
    def __init__(self, search_space, threshold, parent):
        print(type(search_space))
        shape = fc_shape(search_space, include_primitives=False)
        expansions = np.empty(shape, dtype=object)

        self.search_space = search_space
        self.shape = shape
        self.expansions = expansions
        self.threshold = threshold
        self.aquival = threshold # aquisition value
        self.aqui_indices = [] # stores expansion candidates
        self.parent = parent

    def update(self, best_val):
        aquival = self.aquival
        aqui_indices = []
        for index, node in np.ndenumerate(self.expansions):
            if node is None:
                candidate_val = self.threshold
            else:
                node.update(best_val)
                candidate_val = node.aquival

            if candidate_val < aquival:
                aquival = candidate_val
                aqui_indices = [index]
            elif self.aquival == aquival:
                aqui_indices.append(index)

        self.aquival = aquival
        self.aqui_indices = aqui_indices

    def create_node(self, index):
        search_space = expand(self.search_space, index)
        shape = fc_shape(search_space, include_primitives=False)
        if shape:
            node = Node(search_space, self.threshold, self)
        else:
            node = Leaf(search_space, self)
        self.expansions[index] = node

    def next_node(self):
        if self.aqui_indices:
            log.debug('self.aqui_indices:%s' % self.aqui_indices)
            index = random.choice(self.aqui_indices)
        else:
            index = tuple(np.random.randint(x) for x in self.shape)

        if self.expansions[index] is None:
            self.create_node(index)

        node = self.expansions[index]
        return node.next_node()


class Leaf:
    def __init__(self, search_space, parent, minimizer=None):
        if minimizer is None:
            minimizer = FlatGPMinimizer(search_space)

        minimizer.auto_update = False

        self.minimizer = minimizer
        self.search_space = search_space
        self.parent = parent

    @property
    def aquival(self):
        return self.minimizer.best_aquival

    def update(self, best_perf, down_propagate=False):
        self.minimizer.update(best_perf)

        if down_propagate:
            parent = self.parent
            while parent:
                if self.aquival < parent.aquival:
                    parent.aquival = self.aquival
                    parent = self.parent
                else:
                    break

    def next_node(self):
        return self


class DefaultFuture:
    """Represents a future value & delivers a default value."""

    def __init__(self, default):
        self.default = default
        self.future = None

    @property
    def value(self):
        if self.future is None:
            return self.default
        else:
            return self.future
