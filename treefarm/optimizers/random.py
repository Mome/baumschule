
from ..core.random_variables import sample
from ..core.optimizer import Optimizer

class Solver(Optimizer):
    def __next__(self):
        return sample(self.search_space)
