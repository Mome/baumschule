
from itertools import chain
from math import inf
import logging

import numpy as np

from .flatgp import FlatGPOptimizer
from ..core.parameters import Apply, Primitive, join, Operation, Combination
from ..core.domains import ParameterList
from ..core.space_utils import expand, fc_shape
from ..core.optimizer import SequentialOptimizer
from ..core.protocol import PerfDictProtocol

log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel('DEBUG')

default_av = 1. # aqisition value for unseen expansions

# TODO maybe join TreeFarm and Node ???

class TreeGPOptimizer(SequentialOptimizer):

    def __init__(self, search_space, threshold=1.0):
        super().__init__(search_space)
        self.root = Node(search_space, threshold, self)
        self.best = inf

    def compute_next(self):
        leaf = self.root.next_node()
        result = leaf.optimizer.compute_next()
        logging.debug('chose_instance:%s' % result)
        start_time = time.time()

        if result['perf'] < self.best:
            # if performance better: update everything
            self.best = result['perf']
            root.update(self.best)
        else:
            # if performance worse: only update leaf
            # (includes donwn-propagation of aquisition)
            leaf.update(self.best)

        result['update_time'] = time.time() - start_time
        return result

    """def pick_next():
        nn = root.next_node()
        next_instance = nn.optimizer.pick_next()

        return next_instance"""

    def update():
        updates = {}
        for key in self.observers['propagator']:
            instance, perf = self.observers['propagator'].pop()
            node = chosen_nodes.pop(key)
            node.observers['protocol'].append(())
            updates.add(node)


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
        self.aqui_indices = []

    def update(self, record):
        aquival = self.aquival
        aqui_indices = []
        for index, node in np.ndenumerate(self.expansions):
            if node is None:
                candidate_val = self.threshold
            else:
                node.update_aquival(best_val)
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
            node = Leaf(search_space)
        self.expansions[index] = node

    def next_node(self):
        if self.aqui_indices:
            index = np.random.choice(self.aqui_indices)
        else:
            index = tuple(np.randint(x) for x in self.shape)
        node = self.expansions[index]
        if node is None:
            self.create_node(index)
        return node.next_node()


class Leaf:
    def __init__(self, search_space, parent, optimizer=None):
        if optimizer is None:
            optimizer = FlatGPOptimizer(search_space)
        self.optimizer = optimizer
        self.search_space = search_space


class DefaultFuture:
    """Represents a future value & delivers a default value."""

    def __init__(self, default):
        self.default = default
        self._value = None

    @property
    def value(self):
        if self._value is None:
            return self.default
        else:
            return self._value
