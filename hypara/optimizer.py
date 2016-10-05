    # -*- coding: utf-8 -*-
"""
Created on Tue May 24 08:55:01 2016

@author: mome
"""

from collections import namedtuple
from collections.abc import Sequence, Mapping, Callable

Run = namedtuple('Run', ['algorithm', 'parameter', 'result'])

class Algorithm:
    def __init__(self, name, function):
        self.name = name
        self.function = function


    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)



class RandomOptimizer:

    def __init__(self, algorithm, parameterspace, computing_engine=None):

        if not isinstance(Algorithm, Callable):
            raise ValueError('Algorithm must be Callable!')

        if not isinstance(algorithm, Algorithm):
            algorithm = Algorithm(algorithm.__name__, algorithm)

        self.algorithm = algorithm
        self.parameterspace = parameterspace
        self.computing_engine = computing_engine if computing_engine else ComputingEngine()
        self.records = []
    
    def optimize(self, iterations):
        for i in range(iterations):
            sample = self.parameterspace.sample()
            result = self.computing_engine.evaluate(self.algorithm, sample)
            self.records.append(
                Run(self.algorithm.name, sample, result))

    def get_best(self):
        if not self.records:
            return None
        best = self.records[0]
        for run in self.records:
            if run.result < best.result:
                best = run
        return best


class ComputingEngine:

    def evaluate(self, function, parameters):
        if type(parameters) == Sequence:
            result = function(*parameters)
        elif type(parameters) == Mapping:
            result = function(**parameters)
        else:
            result = function(parameters)
        return result
