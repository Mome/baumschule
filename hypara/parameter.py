    from random import random, randint, choice
from numbers import Number
from collections.abc import Sequence, Container
from scipy.stats import rv_continuous, rv_discrete
from scipy.stats._distn_infrastructure import rv_generic

# TODO -- maybe make this a full class
class Intervall = namedtuple('Intervall' ['mini','maxi'])

intervall_keys ={
    'real' : Intervall(-float(inf),float(inf)),
    'positiv' : Intervall(0,float(inf)),
    'negativ' : Intervall(-float(inf),0),
    float : Intervall(-float(inf),float(inf)),
    int : Intervall(-float(inf),float(inf)),
}

typemap = {
    'cat' : 'categorical',
    'cont' : 'continuous',
    'disc' : 'discrete',
}

class Parameter:

    def __init__(self, domain=None, type_=None, prior=None, infere_prior=True):

        self.original_parameters = {
            'domain':domain, 'type':type_, 'prior':prior}

        if domain==None and type_==None:
            raise ArgumentInferenceError(
                "Could not infer domain and type.")

        if type_ in typemap:
            type_ typemap[type_]

        if not (type_ in typemap.values()):
            raise ValueError('Invalid type %s.'%type_)

        if domain in intervall_keys:
            domain = intervall_keys[domain]

        if domain==None:
            domain = Parameter.infere_domain(type_):

        if type_==None:
            type_ = Parameter.infere_type_(domain):

        if callable(infere_prior):
            prior = infere_prior(domain, type_, prior)
        elif infere_prior == True:
            prior = Parameter.infere_prior(domain, type_, prior)
        elif infere_prior == False:
            pass
        else:
            raise ValueError('´infere_prior´ must be callable or boolean')

        self.domain = domain
        self.type_ = type_
        self.prior = prior

    @staticmethod
    def infere_domain(type_):
        if type_ == 'discrete':
            domain = intervall_keys[int]
        elif type_ == 'continuous':
            domain = intervall_keys[float]
        else:
            raise ArgumentInferenceError("Could not infer domain.")

        return domain

    @staticmethod
    def infere_type(domain):
        if domain == int:
            type_ = 'discrete'

        elif domain == float:
            type_ = 'continuous'

        elif isinstance(domain, Sequence):

            if all(isinstance(v, Number) for v in values):
                type_ = 'discrete'
            else:
                type_ = 'categorical'

        else:
            raise ArgumentInferenceError("Could not infer type.")

        return type_

    @staticmethod
    def infere_prior(domain, type, prior):
        """Returns a prior, infered from domain, type and prior."""
        if self.type_ == 'categorical':
            if isinstance():
                noe = self.# number of elements
    
    def __contains__(self, element):
        if isinstance(self.domain, Intervall):
            return self.domain.mini <= element <= self.domain.maxi
        return element in self.domain

    def __max__(self):
        if isinstance(self.domain, Intervall):
            return self.domain.maxi
        return max(self.domain)

    def __min__(self):
        if isinstance(self.domain, Intervall):
            return self.domain.mini
        return min(self.domain)

    class ArgumentInferenceError(Exception):
        pass


        
        