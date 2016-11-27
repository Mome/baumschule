
from time import sleep

from ..core.random_variables import sample
from ..core.optimizer import SequentialOptimizer


class RandomSearcher(SequentialOptimizer):
    def pick_next(self, search_space):
        sleep(0.1)
        return sample(search_space)
