    # -*- coding: utf-8 -*-
"""
Created on Tue May 24 08:55:01 2016

@author: mome
"""

from collections import namedtuple
from collections.abc import Sequence, Mapping

Run = namedtuple('Run', ['algorithm', 'parameter', 'result'])

class RandomOptimizer:

    def __init__(self, computing_engine, algorithm, parameterspace):
        self.computing_engine = computing_engine
        self.records = []
    
    def optimize(iterations):
        for i in range(iterations):
            sample = parameterspace()
            result = computing_engine.evaluate(algorithm, sample)
            records.append(Run(function, sample, result))

    def get_best(self):
        if not self.records:
            return None
        best = self.records[0]
        for run in self.records:
            if run.result < best.result:
                best = run
        return best


def ComputingEngine:

    def evaluate(function, parameters):
        if type(parameters) == Sequence:
            result = function(*parameters)
        elif type(parameters) == Mapping:
            result = function(**parameters)
        else:
            result = function(parameters)
    return result
