
from time import sleep

from ..core.random_variables import sample
from ..core.minimizer import SequentialMinimizer


class RandomMinimizer(SequentialMinimizer):
    """
    Samples from search space distribution.

    """

    def pick_next(self):
        return sample(self.search_space)


class ExhaustiveMinimizer(SequentialMinimizer):
    """
    Iterates over all instances of an iterable search space.

    """

    def __init__(self, search_space, protocol, engine):
        super().__init__(search_space, protocol, engine)
        self.iterator = iter(search_space)

    def pick_next(self):
        return next(self.iterator)
