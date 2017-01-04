
from time import sleep

from ..core.random_variables import sample
from ..core.minimizer import SequentialMinimizer
from ..core.simplify import simplify


class RandomMinimizer(SequentialMinimizer):
    """
    Samples from search space distribution.

    """

    def pick_next(self):
        instance = sample(self.search_space)
        #instance = simplify(instance)
        return instance


class ExhaustiveMinimizer(SequentialMinimizer):
    """
    Iterates over all instances of an iterable search space.

    """

    def __init__(self, search_space, protocol, engine):
        super().__init__(search_space, protocol, engine)
        self.iterator = iter(search_space)

    def pick_next(self):
        instance = next(self.iterator)
        #instance = simplify(instance)
        return instance
