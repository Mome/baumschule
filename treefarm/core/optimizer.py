    # -*- coding: utf-8 -*-
"""
Created on Tue May 24 08:55:01 2016

@author: mome
"""

import sys
from collections import namedtuple
from collections.abc import Sequence, Mapping, Callable
from math import inf
import time

from .serialize import serialize


def optimize(self, func, param, iterations=None, timeout=None):
    assert callable(func)

    if optimizer is None:
        ...
    elif type(optimizer) is str:
        ...

    if iterations and timeout:
        stopcrit = lambda : iterations < i or start_time - time.time() < timeout
    elif iterations:
        stopcrit = lambda : iterations < i
    if timeout is None:
        stopcrit = lambda : start_time - time.time() < timeout

    start_time = time.time()
    instance = sample(param)


class Optimizer(Thread):
    def __init__(self, protocol, engine, search_space):
        self.protocol = protocol
        self.engine = engine
        self.space = space
        self.status = 'stop'

    def run(self):
        status = 'started'
        while status == 'started':
            parameter = next(self)
            perf = engine.compute(parameter)
            protocol.write(
                name = serialize(parameter),
                performance = perf,
            )

    def stop(self):
        """Tells the optimizer to stop, after finishing the last computation."""
        status = 'stop'

    def kill(self):
        """Stop without finnishing computation."""
        raise NotImplementedError()

    def __next__(self):
        """Returns the next value to execute."""
        raise NotImplementedError()
