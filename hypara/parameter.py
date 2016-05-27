from random import random, randint, choice
from numbers import Number
from collections.abc import Sequence
from scipy.stats import rv_continuous, rv_discrete
from scipy.stats._distn_infrastructure import rv_generic

class Parameter:

    typemap = {
        'cat' : 'categorical',
        'cont' : 'continuous',
        'disc' : 'discrete',
    }

    def __init__(self, domain, type_, prior):
        
        if type_:
            if type_ in Parameter.typemap.keys():
                type_ = Parameter.typemap[type_]
            elif not (type_ in Parameter.typemap.values()):
                raise ValueError('Invalid parameter-type.'
            if isinstance(values, Number):
                type_ = 'discrete'
            elif isinstance(values, str):
                type_ = 'categorical'
            elif isinstance(values, rv_continuous):
                type_ = 'continuous'
            elif isinstance(values, rv_discrete):
                type_ = 'discrete'
            elif isinstance(values, Sequence):
                if isinstance(values, range) \
                or all(isinstance(v, Number) for v in values):
                    type_ = 'discrete'
                else:
                    type_ = 'categorical'
            else:
                raise ValueError('Could not infere parameter type.')
        
        self.type_ = type_
        self.values = values
        
    def sample(self):
        values = self.values
        
        if isinstance(values, Number):
            val = values
            
        if isinstance(values, rv_generic):
            val = values.rvs()
        
        if self.type_=="categorical":
            if isinstance(values, Sequence):
                val = choice(values)
            else:
                raise NotImplementedError()
                
        elif self.type_=="discrete":
            if isinstance(values, Sequence):
                val = choice(values)
            else:
                raise NotImplementedError()
        
        elif self.type_=="continuous":
            if isinstance(values, range):
                val = random(range.start, range.end)
            elif isinstance(values, Sequence):
                val = choice(values)
            else:
                raise NotImplementedError()
        else:
            raise ValueError('Invalid parameter-type.')
        
        return val

    def __next__(self):
        return self.sample()
    
    def __iter__(self):
        while True:
            yield next(self)
        
        