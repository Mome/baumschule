
from ..core.random_variables import sample
from ..core.optimizer import Optimizer


class RandomOptimizer(optimizer):
    def __init__(self, protocol, engine):
        self.protocol = protocol
        self.engine = engine
        self.status = 'stop'

    def start(self):
        status = 'started'

    def stop(self):
        pass

    def pause(self):
        status = 'pause'

    def unpause(self):
        status = 'start'
