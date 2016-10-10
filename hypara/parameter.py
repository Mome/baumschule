import random
import operator as python_operator
from collections.abc import Mapping, Sequence
import logging

import numpy.random as rnd

log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel('INFO')


type_abbr = {
    'cat'     : 'categorical',
    'cont'    : 'continuous',
    'disc'    : 'discrete',
    'real'    : 'continuous',
    'natural' : 'continuous',
    float     : 'continuous',
    int       : 'discrete',
    'int'     : 'continuous',
    'flaot'   : 'continuous',
    'integer' : 'continuous',
}

def normalize_type(arg):
    arg = arg.strip().lower()
    if arg is None:
        return None
    if arg in type_abbr.values():
        return arg
    if arg in type_abbr.keys():
        return type_abbr[arg]
    else:
        raise ParameterInferenceError('Unknown type: %s' % arg)


class ParameterSpace:

    def __init__(self, domain, *, dist=None, name=None, symbol=None):
        self.domain = domain
        self._dist = dist
        self.name = name
        self.symbol = symbol
        self._inferred_dist = None

    def sample(self):
        if self._dist:
            return self._dist()
        if not self._inferred_dist:
            self._inferred_dist = self.infer_dist()
        return self._inferred_dist()

    def __contains__(self, element):
        for D in domain:
            if isinstance(D, ParameterSpace) and element in D:
                break
            elif element == D:
                break
        else:
            return True
        return False

    # TODO: may change this to __pformat__
    def print_deep(self, depth=float('inf'), _tabu=None):
        if _tabu is None:
            _tabu = []
        if depth <= 0:
            return ''
        ...

    def __add__(self, arg):
        return add(self, arg)  

    def __sub__(self, arg):
        return sub(self, arg)

    def __mul__(self, arg):
        return mul(self, arg)

    def __truediv__(self, arg):
        return div(self, arg)

    def __or__(self, arg):
        return join(self, arg)


class CombinedSpace(ParameterSpace):
    def __iter__(self):
        return iter(self.domain)

    def __getitem__(self, key):
        return self.domain.__getitem__(key)


class JoinedSpace(CombinedSpace):

    def infer_dist(self):
        def dist():
            # choose subspace
            ss = random.sample(self.domain, 1)[0]
            return ss.sample()
        return dist

    def __str__(self):
        if self.symbol != None:
            return self.symbol
        csl = [str(D) for D in self.domain]
        csl = ', '.join(csl)
        return '{' + csl + '}'

    def __ior__(self, arg):
        self.domain.append(arg)
        return self        


class GeneralProductSpace(CombinedSpace):
    pass


class NamedSpace(GeneralProductSpace):
    def infer_dist(self):
        return lambda : {k:v.sample() for k,v in self.domain.items()}

    def items(self):
        return self.items()

    def __str__(self):
        if self.symbol != None:
            return self.symbol
        csl = ['%s=%s' % item for item in self.domain.items()]
        csl = ', '.join(csl)
        return '[' + csl + ']'


class ProductSpace(GeneralProductSpace):

    def infer_dist(self):
        return lambda : [D.sample() for D in self.domain]

    def __str__(self):
        if self.symbol != None:
            return self.symbol
        csl = [str(D) for D in self.domain]
        csl = ', '.join(csl)
        return '[' + csl + ']'

class SimpleSpace(ParameterSpace):
    def __str__(self):
        if self.symbol:
            return self.symbol
        return str(self.domain)


class Categorical(SimpleSpace):
    def infer_dist(self):
        return lambda : random.sample(self.domain, 1)[0]


class Discrete(SimpleSpace):
    def infer_dist(self):
        dom = self.domain
        assert type(dom) == Intervall
        l_inf = (dom.sub == float('-inf'))
        r_inf = (dom.sup == float('inf'))

        if l_inf and r_inf:
            sample_f = lambda : round(rnd.normal())
        if not l_inf and r_inf:
            sample_f = lambda : round(rnd.lognormal() + dom.sub)
        if l_inf and not r_inf:
            sample_f = lambda : round(-rnd.lognormal() + dom.sup)
        if not l_inf and not r_inf:
            sample_f = lambda : rnd.randint(dom.sub, dom.sup)
        
        return sample_f


class Continuous(SimpleSpace):

    def infer_dist(self):
        dom = self.domain
        assert type(dom) == Intervall
        l_inf = (dom.sub == float('-inf'))
        r_inf = (dom.sup == float('inf'))

        if l_inf and r_inf:
            sample_f = rnd.normal
        if not l_inf and r_inf:
            sample_f = lambda : rnd.lognormal() + dom.sub
        if l_inf and not r_inf:
            sample_f = lambda : -rnd.lognormal() + dom.sup
        if not l_inf and not r_inf:
            sample_f = lambda : rnd.uniform(dom.sub, dom.sup)
        
        return sample_f


class Constant(SimpleSpace):
    def infer_dist(self):
        return lambda : self.domain


class Intervall:

    bounding_values = {
        'bounded',
        'unbounded',
        'left_bounded',
        'right_bounded',
    }

    def __init__(self, sub, sup, type_, bounding='bounded'):
        assert bounding in self.bounding_values
        assert type_ in ['discrete', 'continuous']
        assert sub < sup
        self.sub = sub
        self.sup = sup
        self.type_ = type_
        self.bounding = bounding
        
    def __contains__(self, num):
        if self.type_ == 'discrete':
            if abs(num)!=float('inf') and round(num) != num:
                return False
        if self.bounding == 'bounded':
            return self.sub <= num <= self.sup
        if self.bounding == 'unbounded':
            return self.sub < num < self.sup
        if self.bounding == 'left_bounded':
            return self.sub <= num < self.sup
        if self.bounding == 'right_bounded':
            return self.sub < num <= self.sup      
        
    def __getitem__(self, key):
        if type(key) is slice:

            start, stop, step = key.start, key.stop, key.step

            if start is None:
                start = self.sub
            if stop is None:
                stop = self.sup
            if step is None:
                # TODO: fit default bounding settings
                step = 'bounded'
            
            if not (isinstance(start, (int, float))
                or isinstance(step,  (int, float))):
                raise KeyError('Start and Stop must be Integers!')

            new = Intervall(
                sub = start,
                sup = stop,
                type_ = self.type_,
                bounding = step)

        else:
            raise KeyError(key)

        return new

    def __str__(self):
        return 'Intervall(%s, %s, %s)' % (self.sub, self.sup, self.type_)


class OperatorSpace(CombinedSpace):
    def __init__(self, operator, domain):
        self.operator = operator
        self.domain = domain

    def __str__(self):
        op = self.operator

        if op.notation == 'name':
            if op.symbols:
                return str(op.symbols)
            return op.name

        if op.symbols:
            if len(op.symbols) == 3:
                left, sep, right = op.symbols
            elif len(op.symbols) == 2:
                left, right = op.symbols
                sep = ', '
            elif len(op.symbols) == 1:
                sep, = op.symbols
                left, right = '()'  
            else:
                raise ValueError('len(symboles) must be >=3')
        else:
            left, sep, right = ('(', ', ', ')')

        if isinstance(self.domain, NamedSpace):
            params = sep.join('%s=%s' % item for item in self.domain.items())
        else:
            params = sep.join(str(d) for d in self.domain)

        if op.notation == 'prefix':
            return '%s%s' % (name, params)
        elif op.notation == 'postfix':
            return '%s%s' % (params, name)
        elif op.notation == 'infix':
            return params
        else:
            raise ValueError('unvalid notation')

    def sample(self):
        domsamp = self.domain.sample()
        log.debug('In sample of %s: %s, %s' % (self.operator.name, type(domsamp), type(self.domain)))
        if isinstance(domsamp, Sequence) and isinstance(domsamp, Mapping):
            res = self.operator.func(*domsamp, **domsamp)
        elif isinstance(domsamp, Sequence):
            res = self.operator.func(*domsamp)
        elif isinstance(domsamp, Mapping):
            res = self.operator.func(**domsamp)
        else:
            res = self.operator.func(domsamp)
        return res


class Operator:

    notation_values = ['prefix', 'postfix', 'infix', 'name']

    def __init__(self, func, name, notation=None, symbols=None):
        """
        symbols : Tripel or str the form of (left, sep, right)
        """
        
        if notation is None:
            notation = 'prefix'

        assert notation in self.notation_values         
        
        self.func = func
        self.name = name
        self.symbols = symbols
        self.notation = notation


    def __call__(self, *args, **kwargs):
        assert bool(args) != bool(kwargs)

        if args:
            params = prod(*args)
        else:
            params = prod(**kwargs)

        log.debug('call %s %s %s %s' % (self.name, args, kwargs, params))
        return OperatorSpace(operator=self, domain=params)


def Parameter(domain, *args, **kwargs):

    if isinstance(domain, ParameterSpace):
        assert not (args or kwargs)
        return domain

    if type(domain) in (list, tuple):
        domain = list(map(Parameter, domain))
        cls = ProductSpace 

    elif type(domain) == dict:
        assert all(type(k) == str for k in domain.keys())
        domain = {k:Parameter(v) for k,v in domain.items()}
        cls = NamedSpace

    elif type(domain) == set:
        high_level = any(isinstance(d, ParameterSpace) for d in domain)
        if high_level:
            domain = set(map(Parameter, domain))
            cls = JoinedSpace      
        else:
            cls = Categorical

    elif type(domain) == Intervall:
        if domain.type_ == 'continuous':
            cls = Continuous
        elif domain.type_ == 'discrete':
            cls = Discrete

    else:
        cls = Constant
    
    if 'cls' not in locals():
        raise ParameterInferenceError('Cound not find fitting Parameter class!')

    log.debug('New Parameter: %s, %s and %s in %s' % (domain, args, kwargs, cls))
    
    return cls(domain, *args, **kwargs)


def parametrify(seq_or_map):
    """
    Converts values inside a Sequence or a Mapping into ParameterSpaces.
    """
    arg_cls = type(seq_or_map)
    if isinstance(seq_or_map, Sequence):
        seq = map(Parameter, seq_or_map)
        out = arg_cls(seq)
    else:
        mapping = ((k, Parameter(v)) for k,v in seq_or_map.items())
        out = arg_cls(mapping)
    return out


def prod(*args, **kwargs):
    # ether args or kwargs must be given
    assert bool(args) != bool(kwargs)
   
    if args:
        args = parametrify(args)
        out = ProductSpace(args) 
    elif kwargs:
        kwargs = parametrify(kwargs)
        out = NamedSpace(kwargs)

    return out


def join(*args):
    args = [Parameter(a) for a in args]
    return JoinedSpace(args)


N = Intervall(float('-inf'), float('inf'), type_='discrete', bounding='unbounded')
R = Intervall(float('-inf'), float('inf'), type_='continuous', bounding='unbounded')
#N, R = Parameter(N, symbol='N'), Parameter(R, symbol='R') 

# predefinde operators
add = Operator(name="add", func=python_operator.add, symbols='+', notation='infix')
sub = Operator(name="add", func=python_operator.sub, symbols='-', notation='infix')
mul = Operator(name="mul", func=python_operator.mul, symbols='*', notation='infix')
div = Operator(name="div", func=python_operator.truediv, symbols='/', notation='infix')
pow = Operator(name="pow", func=python_operator.mul, symbols='^', notation='infix')


# predefinde distribution
def normal(mean=0, std=1, *, name=None):
    return Parameter(
        domain = R,
        dist = lambda : rnd.normal(mean, std),
        name = name,
    )
gauss = normal


lognormal = rnd.lognormal()
poisson = ...
binomial = ...
bernoulli = ...
uniform = rnd.randint(0, 1)
laplace = ...


# ------ Distributions ------ #


# look at this for future type and prior inference and stuff
'''
class Parameter:

    def __init__(self, domain=None, type_=None, prior=None, infere_prior=True):

        if isinstance(domain, str):
            domain = domain.strip().lower()

        self.original_parameters = {
            'domain': domain, 'type': type_, 'prior': prior}

        if domain==None and type_==None:
            raise ArgumentInferenceError(
                "Could not infer domain and type.")

        if type_ in typemap:
            type_ = typemap[type_]

        if not (type_ in typemap.values()):
            raise ValueError('Invalid type: %s'%type_)

        if type_==None:
            type_ = Parameter.infere_type(domain)

        if isinstance(domain, (str,type)):
            if domain in intervall_keys:
                domain = intervall_keys[domain]

        if domain==None:
            domain = Parameter.infere_domain(type_)

        if callable(infere_prior):
            prior = infere_prior(domain, type_, prior)
        elif infere_prior == True:
            prior = Parameter.infere_prior(domain, type_, prior)
        elif infere_prior == False:
            pass
        else:
            raise ValueError('"infere_prior" must be callable or boolean')

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

        elif domain in [float, 'probability']:
            type_ = 'continuous'

        elif isinstance(domain, Sequence) and not isinstance(domain, str):

            if all(isinstance(val, Number) for val in domain):
                type_ = 'discrete'
            else:
                type_ = 'categorical'

        else:
            raise ArgumentInferenceError("Could not infer type.")

        return type_

    @staticmethod
    def infere_prior(domain, type_, prior):
        Returns a prior, infered from domain, type and prior.

        if type_ == 'categorical':
            if isinstance(domain, Sequence):
                ...

        return prior

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
'''
class ParameterInferenceError(Exception):
    pass


        
        