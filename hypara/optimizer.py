# -*- coding: utf-8 -*-
"""
Created on Tue May 24 08:55:01 2016

@author: mome
"""

class ParameterOptimizer:
    def __init__(self, type_, sample_number):
        self.samples_number = sample_number
        self.type_ = type_

    def optimize(model_class, parameters=None):
        if not parameters:
            parameters = {}
        pdist = model_class.default_parameters
        pdist.update(parameters)
        ...

        return results


class FunctionOptimizer:
    def __init__(self, number_of_samples, parameter_distribution):
        self.nos = number_of_samples
        self.paradist = copy(parameter_distribution)

    def send_result(self, sample_index, result):
        raise NotImplementedError()

    def next_parameter(self):
        raise NotImplementedError()

    def __next__(self):
        return self.next_parameter()



class RandomOptimizer(self):
    
    def sample(self):
        pass



