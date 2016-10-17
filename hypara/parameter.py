import operator as python_operator
from collections.abc import Mapping, Sequence
import logging

from . import random_variables

log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel('INFO')


default_sampler = random_variables.sample

class OperatorCallable:
    def __call__(self, *args, **kwargs):
        assert bool(args) != bool(kwargs)

        if args and kwargs:
            domain = MixedProduct(args, kwargs)
        elif args:
            params = list(args)
        elif kwargs:
            params = dict(kwargs)

        log.debug('call %s %s %s %s' % (self.name, args, kwargs, params))
        return OperatorCall(operator=self, domain=params)

class ParameterSpace:

    def __init__(self, domain, *, dist=None, name=None, symbol=None):
        if isinstance(domain, ParameterSpace):
            raise ValueError('Domain cannot be a ParameterSpace!')
        self.domain = domain
        self.dist = dist
        self.name = name
        self.symbol = symbol

    def sample(self):
        if self.dist:
            return self.dist()
        else:
            return default_sampler(self)

    # TODO may change this to __pformat__ (figure out how pprint works)
    def print_deep(self, depth=float('inf'), _tabu=None):
        if _tabu is None:
            _tabu = []
        if depth <= 0:
            return ''
        ...        

    def __contains__(self, element):
        for D in domain:
            if isinstance(D, ParameterSpace) and element in D:
                break
            elif element == D:
                break
        else:
            return True
        return False

    def __str__(self):
        if self.symbol:
            return self.symbol
        return str(self.domain)

    def __repr__(self):
        return '%s(%s)' % (
            str(self.__class__.__name__),
            str(self)
        )

    def __or__(self, arg):
        return join(self, arg)

    def __add__(self, arg):
        return add(self, arg)  

    def __sub__(self, arg):
        return sub(self, arg)

    def __mul__(self, arg):
        return mul(self, arg)

    def __truediv__(self, arg):
        # alias for div
        return truediv(self, arg)

    def __floordiv__(self, arg):
        return floordiv(self, arg)


class CombinedSpace(ParameterSpace):
    def __iter__(self):
        return iter(self.domain)

    def __getitem__(self, key):
        return self.domain.__getitem__(key)


class JoinedSpace(CombinedSpace, OperatorCallable):

    def __str__(self):
        if self.symbol != None:
            s = self.symbol
        else :
            csl = [str(D) for D in self.domain]
            csl = ', '.join(csl)
            s =  '{' + csl + '}'

        return s

    def __ior__(self, arg):
        self.domain.append(arg)
        return self        


class GeneralProductSpace(CombinedSpace):
    pass


class NamedSpace(GeneralProductSpace):

    def keys(self):
        return self.domain.keys()

    def values(self):
        return self.domain.values()
        
    def items(self):
        return self.domain.items()

    def __iter__(self):
        return self.values()

    def __str__(self):
        if self.symbol != None:
            return self.symbol
        csl = ['%s=%s' % item for item in self.domain.items()]
        csl = ', '.join(csl)
        return '[' + csl + ']'


class ProductSpace(GeneralProductSpace):
    def __str__(self):
        if self.symbol:
            return self.symbol
        else:
            return '[%s]' % ', '.join(map(str, self.domain))

class MixedProductSpace(ProductSpace, NamedSpace):
    pass

class SimpleSpace(ParameterSpace):
    def __repr__(self):
        return str(self)

class Categorical(SimpleSpace):
    pass

class Discrete(SimpleSpace):
    def __str__(self):
        return '%s(%s, %s)' % (
            self.__class__.__name__,
            self.domain.sub,
            self.domain.sup,
        )        

class Continuous(SimpleSpace):
    def __str__(self):
        return '%s(%s, %s)' % (
            self.__class__.__name__,
            self.domain.sub,
            self.domain.sup,
        )
        
class Constant(SimpleSpace):
    pass

class OperatorCall(CombinedSpace):
    def __init__(self, operator, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.operator = operator

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
            return ''.join([op.name, left, params, right])
        elif op.notation == 'postfix':
            return ''.join([left, params, right, op.name])
        elif op.notation == 'infix':
            return params
        else:
            raise ValueError('unvalid notation')

        
class Operator(OperatorCallable):

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

    def __str__(self):
        return '%s(name=%s)' % (
            self.__class__.__name__,
            self.name
        )


class MixedProduct:
    """Prepresents a product of a list and a dictionary."""
    # TODO: add slices

    def __init__(self, args, kwargs):
        self.args = list(args)
        self.kwargs = dict(kwargs)

    def __getitem__(self, key):
        print(key, type(key))
        if type(key) == int:
            return self.args[key]
        elif type(key) == str:
            return self.kwargs[key]
        else:
            raise ValueError('Only str and int are valied keys.')

    def __setitem__(self, key, val):
        if type(key) == int:
            self.args[key] = val
        elif type(key) == str:
            self.kwargs[key] = val
        else:
            raise ValueError('Only str and int are valied keys.')

    def __iter__(self):
        yield from self.args
        yield from self.kwargs.values()

    def keys(self):
        return [*range(len(self.args)), *self.kwargs.values()]

    def values(self):
        return list(self)

    def __str__(self):
        args_str = map(str, self.args) 
        kwargs_str = ('%s=%s' % item for item in self.kwargs.items())
        return '[%s]' % ', '.join([*args_str, *kwargs_str])

    def __repr__(self):
        return 'MixedProduct(%s)' % str(self)


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

    def __add__(self, other):
        return Parameter(self) + Parameter(other)

    def __sub__(self, other):
        return Parameter(self) - Parameter(other)

    def __mul__(self, other):
        return Parameter(self) * Parameter(other)

    def __truediv__(self, other):
        return Parameter(self) / Parameter(other)

    def __floordiv__(self, other):
        return Parameter(self) // Parameter(other)

    def __pow__(self, other):
        return Parameter(self) ** Parameter(other)

    def __or__(self, other):
        return join(self, other)



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

Par = Parameter


def prod(*args, **kwargs):
    # ether args or kwargs must be given
    if args and kwargs:
        raise ParameterInferenceError()

    product = []
    if args:
        for a in args:
            if isinstance(a, ProductSpace):
                product.extend(a.domain)
            else:
                product.append(a)
    return ProductSpace(a)


def join(*args):
    args = [Parameter(a) for a in args]
    return JoinedSpace(args)


N = Intervall(float('-inf'), float('inf'), type_='discrete', bounding='unbounded')
R = Intervall(float('-inf'), float('inf'), type_='continuous', bounding='unbounded')
#N, R = Parameter(N, symbol='N'), Parameter(R, symbol='R') 

# predefinde operators
add = Operator(name="add", func=python_operator.add, symbols='+', notation='infix')
sub = Operator(name="sub", func=python_operator.sub, symbols='-', notation='infix')
mul = Operator(name="mul", func=python_operator.mul, symbols='*', notation='infix')
pow = Operator(name="pow", func=python_operator.pow, symbols='^', notation='infix')
truediv = Operator(name="div", func=python_operator.truediv, symbols='/', notation='infix')
floordiv = Operator(name="floordiv", func=python_operator.floordiv, symbols='//', notation='infix')
div = truediv

class ParameterInferenceError(Exception):
    pass
