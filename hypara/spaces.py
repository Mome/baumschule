import operator as python_operator
import logging
import textwrap

from .domains import Product, Intervall, Call

log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel('INFO')

# ---------- Classes --------------------------------------------------------- #

class Callable:
    def __call__(self, *args, **kwargs):
        domain = Product(args, kwargs)
        domain = _spacify(domain)
        return CallSpace(self, domain)

class Space(Callable):

    def __init__(self, domain, *, dist=None, name=None, symbol=None):

        if isinstance(domain, Space):
            raise ValueError('Domain cannot be a Space!')

        self.domain = domain
        self.dist = dist
        self.name = name
        self.symbol = symbol

    def __contains__(self, element):
        for D in domain:
            if isinstance(D, Space) and element in D:
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
            repr(self.__class__.__name__),
            repr(self.domain)
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


class AtomicSpace(Space):
    pass


class Categorical(AtomicSpace):
    pass


class Discrete(AtomicSpace):
    def __str__(self):
        return '%s(%s, %s)' % (
            self.__class__.__name__,
            self.domain.sub,
            self.domain.sup,
        )        


class Continuous(AtomicSpace):
    def __str__(self):
        return '%s(%s, %s)' % (
            self.__class__.__name__,
            self.domain.sub,
            self.domain.sup,
        )

class Constant(AtomicSpace):
    pass

class CombinedSpace(Space):
    def __iter__(self):
        return iter(self.domain)

    def __getitem__(self, key):
        return self.domain.__getitem__(key)


class JoinedSpace(CombinedSpace):
    def __init__(self, domain, *args, **kwargs):
        super().__init__(list(domain), *args, **kwargs)

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
    def __init__(self, domain, *args, **kwargs):
        if type(domain) == list:
            domain = Product(domain, {})
        elif type(domain) == dict:
            domain = Product([], domain)
        super().__init__(domain, *args, **kwargs)
 
    def keys(self):
        return self.domain.keys()

    def values(self):
        return self.domain.values()
        
    def items(self):
        return self.domain.items()

    def __iter__(self):
        return self.values()


class CallSpace(ProductSpace):

    notation_values = ['prefix', 'postfix', 'infix', 'name']

    def __init__(self, operator, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.operator = operator

    def __repr__(self):
        return '%s(%s, %s)' % (
            repr(self.__class__.__name__),
            repr(self.operator),
            repr(self.domain),
        )

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

        params = str(self.domain)[1:-1].split(', ')
        params = sep.join(params)

        if op.notation == 'prefix':
            return ''.join([op.name, left, params, right])
        elif op.notation == 'postfix':
            return ''.join([left, params, right, op.name])
        elif op.notation == 'infix':
            return params
        else:
            raise ValueError('unvalid notation')


class Operator(Callable):

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
        return self.name

    def __repr__(self):
        return self.name


# ---------- Functions ------------------------------------------------------- #

def space(domain, *args, **kwargs):

    log.debug('space:' + str(domain))
    
    if isinstance(domain, Space):
        assert not (args or kwargs)
        return domain

    domain = _spacify(domain)
    cls = _pick_class(domain)
    
    return cls(domain, *args, **kwargs)


def _spacify(domain):
    """
    If argument has a valid container type:
    convert elements to Spaces.
    """

    log.debug('_spacify:' + str(domain))

    if isinstance(domain, Space):
        pass

    elif _is_atomic(domain):
        log.debug('_spacify:isatomic')
        pass

    elif type(domain) in (list, tuple):
        domain = list(map(space, domain))

    elif type(domain) == dict:
        # TODO: maybe allow numerical indices
        assert all(type(k) == str for k in domain.keys())
        domain = {k:space(v) for k,v in domain.items()}

    elif type(domain) == set:
        domain = set(map(space, domain))

    elif type(domain) == Product:
        list_part = list(map(space, domain.args))
        dict_part = {k:space(v) for k,v in domain.kwargs.items()}
        domain = Product(list_part, dict_part)

    return domain


atomic_classes = (list, tuple, set, frozenset, Intervall)
non_atomics_classes = (dict, Product, Space)
all_classes = atomic_classes + non_atomics_classes

def _is_atomic(domain):
    """
    Check if argument would evaluate to an atomic sapace.
    """
    assert not isinstance(domain, Space)

    if type(domain) in atomic_classes:

        if type(domain) is Intervall:
            return False

        for d in domain:
            if isinstance(d, all_classes):
                return False

    elif type(domain) in non_atomics_classes:
        return False

    return True


def _pick_class(domain):

    log.debug('_pick_class:' + str(domain))

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
            cls = Categorical
        else:
            cls = JoinedSpace

    else:
        cls = Constant

    """else:
        raise SpaceInferenceError(
            'Cound not find fitting Space class: %s'
            % type(domain))"""

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
    domain = Product(args, kwargs)
    domain = _spacify(domain)
    return ProductSpace(domain)


def join(*args):
    if _is_atomic(args):
        domain = set(args)
    else:
        domain = _spacify(args)
    return JoinedSpace(domain)


def pprint(space):
    print(pformat(space))


def pformat(space):
    stack = []
    prefix = ' '*4
    
    def deeper(space):
        if isinstance(space, AtomicSpace):
            return str(space)

        if space in stack:
            return '...'

        stack.append(space)

        if type(space.domain) == Product:
            params = [
                deeper(arg)
                for arg in space.domain.args
            ]
            params += [
                k + ' = ' + deeper(v)
                for k,v in space.domain.kwargs.items()
            ]

        elif type(space.domain) == list:
            params = [
                deeper(arg)
                for arg in space.domain
            ]
        else:
            raise SpacePrintingError('No good reason!')

        params = textwrap.indent(
            text = ',\n'.join(params),
            prefix = prefix,
        )

        if type(space) == ProductSpace:
            out = '[\n', params, ',\n]'
        elif type(space) == JoinedSpace:
            out = '{\n', params, ',\n}'
        elif type(space) == CallSpace:
            out = str(space.operator), '(\n', params, ',\n)'
        else:
            raise SpacePrintingError('No good reason!')

        stack.pop()
        return ''.join(out)


    return deeper(space)


# ---------- Exceptions ------------------------------------------------------ #

class SpaceInferenceError(Exception):
    pass

class SpaceCombinationError(Exception):
    pass

class SpacePrintingError(Exception):
    pass

# ------ Predifined operators ---------------------------------------------------- #

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
