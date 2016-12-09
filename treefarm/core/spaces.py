import logging
import operator as python_operator

from .domains import Interval, ParameterList
from .environment import get_env

log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel('INFO')


class Callable:
    def __call__(self, *args, **kwargs):
        log.debug('call: %s %s' % (args, kwargs))
        domain = ParameterList(args, kwargs)
        return Apply(self, domain)


class Parameter(Callable):
    # not callable yet
    def __init__(self, domain, *, dist=None, name=None, symbol=None):
        log.debug('domain: %s' % domain)

        if isinstance(domain, Parameter):
            raise ValueError('Domain cannot be a Space!')

        self.domain = domain
        self.dist = dist
        self.name = name
        self.symbol = symbol

    def __contains__(self, element):
        # TODO This needs to be much more sophisticated!
        for D in self.domain:
            if isinstance(D, Parameter) and element in D:
                break
            elif element == D:
                break
        else:
            return True
        return False

    def __str__(self):
        name = self.__class__.__name__
        return '%s(%s)' % (name, '...')

    def __or__(self, arg):
        return join(self, arg)

    def __and__(self, args):
        return intersect(self, arg)

    def __xor__(self, arg):
        return power(self, arg)

    def __floordiv__(self, arg):
        raise NotImplementedError()

    def __add__(self, arg):
        return get_env().add(self, arg)

    def __sub__(self, arg):
        return get_env().sub(self, arg)

    def __mul__(self, arg):
        return get_env().mul(self, arg)

    def __truediv__(self, arg):
        return get_env().div(self, arg)

    def __pow__(self, arg):
        return get_env().pow(self, arg)

    def __matmul__(self, *args, **kwargs):
        return apply(self, *args, **kwargs)


class Apply(Parameter):
    def __init__(self, operation, *args, **kwargs):
        log.debug('create apply: %s' % operation)
        super().__init__(*args, **kwargs)
        self.operation = operation

    def __lshift__(self, arg):
        self.domain << arg

    def __rshift__(self, arg):
        arg << self.domain

    def __ilshift__(self, arg):
        self.domain << arg
        return self

    def __irshift__(self, arg):
        raise TypeError('unsupported operand type(s) for =<<: %r and %r'
            % (type(self), type(arg)))


class Primitive(Parameter):
    pass
    """def __len__(self):
        return len(self.domain)"""

class Categorical(Primitive):
    def __str__(self):
        return '{' + ','.join(str(D) for D in self.domain) + '}'

class Discrete(Primitive):
    def __str__(self):
        if type(self.domain) == Interval:
            return str(self.domain)
        else:
            return 'Disc[' + ','.join(str(D) for D in self.domain) + ']'
        return out

class Continuous(Primitive):
    def __str__(self):
        return str(self.domain)



class Operation(Callable):

    NOTATIONS = {'prefix', 'postfix', 'infix', 'name'}

    def __init__(self, func, name, *,
        properties=None,
        notation=None,
        symbol=None,
        dist=None):
        """
        symbol : Tripel or str the form of (left, sep, right)
        """

        if notation is None:
            notation = 'prefix'
        if properties is None:
            properties = ()

        assert notation in self.NOTATIONS

        self.func = func
        self.name = name
        self.properties = frozenset(properties)
        self.symbol = symbol
        self.notation = notation
        self.dist = dist

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Operator(' + self.name + ')'

    def __matmul__(self, arg):
        return self(arg)

    """def __call__(self, arg):
        apply_obj = super().__call__(arg)
        apply_obj.dist = self.dist
        return apply_obj"""

class Combination(Operation):
    """
    Difference between a combination and other operations is that
    Combinations ether represent a structure themselfs or are replaced by
    structures before the evaluation of other operations.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def op(func, name=None, **kwargs):
    if name is None:
        name = func.__name__
        if name == '<lambda>':
            log.warn('You should give a proper name to the function.')
    return Operation(func, name, **kwargs)


"""def power(arg1, arg2):
    assert type(arg2) == int
    arg = prod(*([arg1]*arg2))
    return ParameterList(arg, {})"""


# --------------------- Combinations --------------------- #

def join_func(*args, **kwargs):
    raise Exception('Join is not supposed to be executed!')

def intersect_func(*args, **kwargs):
    raise Exception('Intersect is not supposed to be executed!')

def prod_func(*args, **kwargs):
    new_args = []
    for a in args:
        if type(a) == ParameterList:
            new_args.extend(a)
        else:
            new_args.append(a)
    return ParameterList(new_args, kwargs)

def power_func(arg1, arg2):
    assert type(arg2) == int
    print('inner power', arg1, arg2)
    return prod(*([arg1]*arg2))


def apply_func(operation, *args, **kwargs):
    return Apply(operation, *args, **kwargs)


join = Combination(
    func=join_func,
    name='join',
    properties=(
        'associative', # evaluation order irrelevant
        'commutative', # argument order irrelevant
        'idempotent',  # identical arguments have no effect
        'variadic'),   # operation can be called with arbitrary arity
    symbol='∪',
    notation='infix')

intersect = Combination(
    func=intersect_func,
    name='intersect',
    properties=(
        'associative',
        'commutative',
        'idempotent',
        'variadic'),
    symbol='∩',
    notation='infix')

prod = Operation(
    func=prod_func,
    name='prod',
    properties=(
        'associative',
        'variadic'),
    symbol='×',
    notation='infix')

power = Combination(
    func=power_func,
    name='power',
    properties={},
    symbol='^',
    notation='infix')

# ----- other operations -----

quote = Operation(
    func=None,
    name='quote')

apply = Operation(
    func = apply_func,
    name = 'apply'
)
