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

from .parameters import op
from .serialize import serialize
from .protocol import Protocol
from .computing_engine import SimpleEngine
from .environment import get_config

log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel('INFO')
conf = get_config()


def optimize_func(
    func,
    param,
    max_iter = inf,
    timeout = inf,
    optimizer = 'default',
    return_object = None):

    assert callable(func)

    operation = op(func) # convert function to operation
    search_space = operation(param) # integrate into search space
    return optimize( # optimize search space
        search_space, max_iter, timeout, optimizer, return_object)


def optimize(
    search_space,
    max_iter = inf,
    timeout = inf,
    optimizer = 'default',
    return_object = False):

    if type(optimizer) is str:
        optimizer = conf.optimizers[optimizer]
    if type(optimizer) is type:
        optimizer = optimizer(search_space)

    opt_obj = Optimization(optimizer, max_iter, timeout)

    """if return_object is None:
        # check for iteractive cell
        return_object = sys.stdout.isatty()"""

    if return_object:
        return opt_obj
    else:
        assert max_iter < inf or timeout < inf, 'set max_iter or timeout'
        opt_obj.run()
        prot = opt_obj.optimizer.protocol
        perfs = list(zip(*prot))[1]
        index = perfs.index(min(perfs))
        return prot[index]


class Optimization(threading.Thread):
    def __init__(self, optimizer, max_iter, timeout):
        super().__init__()
        self.optimizer = optimizer
        self.max_iter = max_iter
        self.timeout = timeout
        self._stop = threading.Event()
        self.iteration = 0
        self.start_time = None
        self.observers = []

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def __iter__(self):
        self.start_time = time.time()
        reason = 'external'

        while True:
            if self.iteration >= self.max_iter:
                reason = 'max_iteration'
                self.stop()
            elif self.timeout <= time.time() - self.start_time:
                reason = 'timeout'
                self.stop()

            if self.stopped():
                break

            yield next(self)

        log.debug('optimization finished: %s' % reason)

    def __next__(self):
        self.iteration += 1
        record = self.optimizer.compute_next()
        self.write(record)
        return record

    def write(self, *args, **kwargs):
        for ob in self.optimizer.observers:
            ob.write(*args, **kwargs)
        for ob in self.observers:
            ob.write(*args, **kwargs)

    def run(self):
        for _ in iter(self):
            pass


class Optimizer:
    def __init__(self, search_space, engine=None):
        if engine is None:
            engine = SimpleEngine()
        self.search_space = search_space
        self.engine = engine
        self.protocol = []
        self.observers = []
        self.best = inf


class SequentialOptimizer(Optimizer):

    def compute_next(self):
        """Chooses an instance, computes the result and protocols"""
        # maybe use timestructs or datetime here
        start_ts = time.time()
        point = self.pick_next()
        select_ts = time.time()
        sample_str = serialize(point)
        log.debug('Compute: %s' % sample_str)
        result = self.engine.evaluate(point)
        comp_ts = time.time()
        self.protocol.append((point, result))

        if result < self.best:
            self.best = result

        record = {
            'sample_str' : sample_str,
            'start_ts' : start_ts,
            'select_ts' : select_ts,
            'comp_ts' : comp_ts,
            'result' : result,
        }
        return record

    def pick_next(self):
        raise NotImplementedError()


# TODO put this into config
from ..optimizers.simple import RandomOptimizer
def get_default_optimizer():
    return RandomOptimizer()
