    # -*- coding: utf-8 -*-
"""
Created on Tue May 24 08:55:01 2016

@author: mome
"""

from abc import ABCMeta, abstractmethod, abstractclassmethod

from multiprocessing import Process

class Model(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, parameters):
        pass
    
    @abstractmethod
    def fit(self, training_data, validation_data=None, pretraining_data=None):
        pass
    
    @abstractmethod
    def predict(self, X):
        pass
    """
    @property
    @abstractclassmethod
    def parameter_distribution(cls):
        pass"""

"""
class Optimizer:
    def __init__(self):
        ...
    
    def optimize_single(self, algorithm, parameter_dict, iterations=None, timeout=None):
                
        while True:
            pass"""
            
class A():
    parameter_distribution = {}
    def __init__(self, parameters):
        self.parameters = parameters

    def fit(self, training_data, validation_data=None, pretraining_data=None):
        pass
    
    def predict(self, X):
        pass

a = A({})

print('isinstance:', isinstance(a, Model))