    # -*- coding: utf-8 -*-
"""
Created on Tue May 24 08:55:01 2016

@author: mome
"""

import sys
from collections import namedtuple
from collections.abc import Sequence, Mapping, Callable

Run = namedtuple('Run', ['algorithm', 'parameter', 'result'])


class Algorithm:
    def __init__(self, name, function):
        self.name = name
        self.function = function


    def __call__(self, *args, **kwargs):
        #print(args, kwargs)
        return self.function(*args, **kwargs)


class Optimizer:
    def __init__(self, algorithm, parameterspace):

        if not isinstance(Algorithm, Callable):
            raise ValueError('Algorithm must be Callable!')

        if not isinstance(algorithm, Algorithm):
            algorithm = Algorithm(algorithm.__name__, algorithm)

        self.algorithm = algorithm
        self.parameterspace = parameterspace
        self.computing_engine = computing_engine if computing_engine else ComputingEngine()
        self.records = []
        self.silent = False


computing_engine = ComputingEngine()
