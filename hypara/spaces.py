import operator as python_operator
import logging

from . import random_variables
from .domains import Call, Product, Intervall

log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel('INFO')

default_sampler = random_variables.sample


# ---------- Classes --------------------------------------------------------- #

class SpaceCallable:
    def __call__(self, *args, **kwargs):
        return CallSpace(
            operator=self,
            domain=Product(args, kwargs),
        )


class Space(OperatorCallable):

    def __init__(self, domain, *, dist=None, name=None, symbol=None):

        if isinstance(domain, Space):
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


class SimpleSpace(Space):
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


class CombinedSpace(Space):
    def __iter__(self):
        return iter(self.domain)

    def __getitem__(self, key):
        return self.domain.__getitem__(key)


class JoinedSpace(CombinedSpace):

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


class ProductSpace(CombinedSpace):
        def __str__(self):
        if self.symbol:
            return self.symbol
        else:
            return '[%s]' % ', '.join(map(str, self.domain))

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



class CallSpace(ProductSpace):

    notation_values = ['prefix', 'postfix', 'infix', 'name']

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


# ---------- Functions ------------------------------------------------------- #

def space(domain, *args, **kwargs):
    domain = _spacify(domain)

    if isinstance(domain, ParameterSpace):
        assert not (args or kwargs)
        return domain

    cls = _pick_class(domain)
    if not _is_atomic(domain):
        domain = _spacify(domain)
    
    return cls(domain, *args, **kwargs)


def _spacify(domain):
    """
    If argument has a valid container type:
    convert elements to Spaces.
    """

    if isinstance(arg, Space):
        raise SpaceInferenceError()

    if type(domain) in (list, tuple):
        domain = list(map(Parameter, domain))

    elif type(domain) == dict:
        # TODO: maybe allow numerical indices
        assert all(type(k) == str for k in domain.keys())
        domain = {k:Parameter(v) for k,v in domain.items()}

    elif type(domain) == set:
        if 
        if high_level:
            domain = set(map(Parameter, domain))
            cls = JoinedSpace      
        else:
            cls = Categorical

    elif type(domain) == containers.MixedProducts:
        cls = MixedSpace

    if 'cls' not in locals():
        raise SpaceInferenceError('Cound not find fitting Parameter class!')

    return domain


valid_containers = {list, tuple, dict, set, frozenset, Call, MixedProduct}
def _is_atomic(arg):
    """
    Check if argument would evaluate to an atomic parameter.
    """
    assert not isinstance(arg, ParameterSpace)

    if arg in valid_containers:
        return any(
            isinstance(d, (ParameterSpace, *valid_containers))
            for d in domain)

    return True


def _pick_class(arg):
    if isinstance(domain, Space):
        raise SpaceInferenceError('Already a Space!')

    if type(domain) in (list, tuple, dict, Product):
        cls = ProductSpace

    elif type(domain) == Call:
        cls = CallSpace

    elif type(domain) == Intervall:
        if domain.type_ == 'continuous':
            cls = Continuous
        elif domain.type_ == 'discrete':
            cls = Discrete

    elif type(domain) == set:
        if _is_atomic(domain):
            cls = JoinedSpace
        else:
            cls = Categorical

    else:
        raise SpaceInferenceError('Cound not find fitting Space class!')

    return cls


def direct_prod(*args):
    # TODO: add support for spaces as arguments
    list_part = []
    dict_part = {}

    for arg in args:
        if type(arg) == list:
            list_part.extend(arg)

        elif type(arg) == dict:
            if any(key in dict_part for key in arg):
                raise SpaceCombinationError("Multiple keys.")
            dict_part.update(arg)

        elif type(arg) == Product:
            if any(key in dict_part for key in arg.kwargs):
                raise SpaceCombinationError("Multiple keys.")
            list_part.extend(arg.args)
            dict_part.update(arg.kwargs)

    domain = Product(list_part, dict_part)
    return ProductSpace(domain)


def prod(*args, **kwargs):
    args = _spacify(kwargs)
    kwargs = _spacify(kwargs)
    domain = Product(args, kwargs)
    return ProductSpace(domain)


def join(*args):
    if _is_atomic(args):
        domain = set(args)
    else:
        domain = _spacify(args)
    return JoinedSpace(domain)


# ---------- Exceptions ------------------------------------------------------ #

class SpaceInferenceError(Exception):
    pass

class SpaceCombinationError(Exception):
    pass


# ------ Predifined Stuff ---------------------------------------------------- #

N = space(
    Intervall(
        sub=float('-inf'),
        sup=float('inf'),
        type_='discrete',
        bounding='unbounded',))

R = space(
    Intervall(
        sub=float('-inf'),
        sup=float('inf'),
        type_='continuous',
        bounding='unbounded',))

add = Operator(
    name="add",
    func=python_operator.add,
    symbols='+',
    notation='infix')

sub = Operator(
    name="sub",
    func=python_operator.sub,
    symbols='-',
    notation='infix')

mul = Operator(
    name="mul",
    func=python_operator.mul,
    symbols='*',
    notation='infix')

pow = Operator(name="pow",
    func=python_operator.pow,
    symbols='^',
    notation='infix')

truediv = Operator(name="div",
    func=python_operator.truediv,
    symbols='/',
    notation='infix')

floordiv = Operator(
    name="floordiv",
    func=python_operator.floordiv,
    symbols='//',
    notation='infix')
div = truediv
