    # -*- coding: utf-8 -*-
"""
Created on Tue May 24 08:55:01 2016

@author: mome
"""

import sys
import os
import threading
from math import inf
import time
import logging

from .serialize import serialize
from .protocol import Protocol
from .computing_engine import SimpleEngine
from ..optimizers.random import RandomOptimizer

log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel('INFO')


# TODO put this into config
def get_default_optimizer():
    """Factory method to create an optimizer."""

    optimizer = RandomOptimizer(
        protocol = Protocol('default'),
        engine = SimpleEngine(),
    )
    return optimizer


def optimize_func(
    func,
    param,
    max_iterations = inf,
    timeout = inf,
    optimizer = None,
    return_object = None):

    assert callable(func)

    operation = op(func) # convert function to operation
    search_space = operation(param) # integrate into search space
    return optimize( # optimize search space
        search_space, max_iterations, timeout, optimizer, return_object)


def optimize(
    search_space,
    max_iterations = inf,
    timeout = inf,
    optimizer = None,
    return_object = None):

    if optimizer is None:
        optimizer = get_default_optimizer()

    optim_obj = Optimization(search_space, optimizer, max_iterations, timeout)

    if return_object is None:
        # check for iteractive cell
        return_object = os.isatty(sys.stdout.fileno())

    if return_object:
        return optim_obj
    else:
        optim_obj.start()

class Optimization(threading.Thread):
    def __init__(self, search_space, optimizer, max_iterations, timeout):
        super().__init__()
        self.optimizer = optimizer
        self.search_space = search_space
        self.max_iterations = max_iterations
        self.timeout = timeout
        self._stop = threading.event()
        self.iteration = 0
        self.start_time = None

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def __iter__(self):
        yield next(self.optimizer)

    def __next__(self):
        return self.optimizer.pick_next(self.search_space)

    def run(self):
        self.start_time = time.time()

        while True:
            if timeout >= start_time - time.time():
                self.stop()
            elif iteration >= self.max_iterations:
                self.stop()
            if stopped():
                break

            self.iteration += 1
            next(self)


class Optimizer:
    def __init__(self, protocol, engine):
        self.protocol = protocol
        self.engine = engine

    def compute_next(self, search_space):
        """Chooses an instance, computes the result and protocols"""
        # maybe use timestructs or datetime here
        start_ts = time.time()
        instance = self.pick_next(search_space)
        select_ts = time.time()
        instance_str = serialize(instance)
        log.info('Compute: %s' % instance_str)
        res = self.engine.evaluate(instance)
        comp_ts = time.time()
        rec = self.protocol.record(
            instance_str, strart_ts, select_ts, comp_ts, res)
        return rec

    def pick_next(self, search_space):
        raise NotImplementedError()
