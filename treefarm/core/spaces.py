import operator as python_operator
import logging
import textwrap

from .domains import Product, Intervall, Call

log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel('INFO')

# ---------- Classes -------------------------------------------------------- #

class Callable:
    def __call__(self, *args, **kwargs):
        domain = Product(args, kwargs)
        domain = _spacify(domain)
        return CallSpace(self, domain)

class Space(Callable):

    # TODO - add this feature maybe later
    """def __new__(cls, domain=None, *args, **kwargs):

        if cls is Space:
            log.debug('new_sapce:' + str(domain))

            if domain is None:
                domain = JoinedSpace([])

            if isinstance(domain, Space):
                assert not (args or kwargs)
                return domain

            other_cls = _pick_class(domain)

            #return cls(domain, *args, **kwargs)
            #self = cls.__new__(cls, source, parts)
        else:
            self = object.__new__(cls)

        return self"""

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
            self.__class__.__name__,
            repr(self.domain)
        )

    def __or__(self, arg):
        return TempCollection([self, arg])

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
    def __str__(self):
        if type(self.domain) == Intervall:
            return '%s(%s, %s)' % (
                self.__class__.__name__,
                self.domain.sub,
                self.domain.sup,)
        else:
            return super().__str__()


class Categorical(AtomicSpace):
    def __len__(self):
        return len(self.domain)


class Discrete(AtomicSpace):
    def __repr__(self):
        return str(self)


class Continuous(AtomicSpace):
    def __repr__(self):
        return str(self)


class Constant(AtomicSpace):
    pass


class Variable(AtomicSpace):
    def __init__(self, name, domain=None, *args, **kwargs):
        super().__init__(domain, *args, **kwargs)
        self.name = name

    @property
    def value(self):
        return self.domain

    @value.setter
    def value(self, value):
        self.domain = value
var = Variable

class CombinedSpace(Space):
    def __str__(self):
        return pformat(self, linebreaks=False)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.domain)

    def __iter__(self):
        return iter(self.domain)

    def __getitem__(self, key):
        return self.domain.__getitem__(key)

    def __lshift__(self, arg):
        if type(arg) == TempCollection:
            arg = _spacify(arg)
            self.domain.extend(arg)
        else:
            self.domain.append(to_space(arg))

    def __ilshift__(self, arg):
        self.__lshift__(arg)
        return self

    def __len__(self):
        return len(self.domain)


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
            self.__class__.__name__,
            repr(self.operator),
            repr(self.domain),
        )

    def __str__(self):
        op = self.operator

        if type(op) == Operator:
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
                out = ''.join([op.name, left, params, right])
            elif op.notation == 'postfix':
                out = ''.join([left, params, right, op.name])
            elif op.notation == 'infix':
                out = params
            else:
                raise ValueError('unvalid notation')

        else:
            return str(op) + super().__str__()

        return out


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
        return 'Operator(' + self.name + ')'


# ---------- Functions ------------------------------------------------------ #

def to_space(domain=None, *args, **kwargs):

    if domain is None:
        domain = JoinedSpace([])

    if isinstance(domain, Space):
        assert not (args or kwargs)
        return domain

    if not _is_atomic(domain):
        domain = _spacify(domain)

    cls = _pick_class(domain)

    return cls(domain, *args, **kwargs)


def _spacify(domain):
    """
    Converts the elements of a container to spaces.
    """

    #log.debug('_spacify:' + str(domain))

    if isinstance(domain, Space):
        raise SpaceInferenceError('Should not be called with a Space.')

    elif isinstance(domain, (list, tuple)):
        domain = list(map(to_space, domain))

    elif isinstance(domain, dict):
        # TODO: maybe allow numerical indices
        assert all(type(k) == str for k in domain.keys())
        domain = {k:to_space(v) for k,v in domain.items()}

    elif isinstance(domain, set):
        domain = set(map(to_space, domain))

    elif type(domain) == Product:
        list_part = list(map(to_space, domain.args))
        dict_part = {k:to_space(v) for k,v in domain.kwargs.items()}
        domain = Product(list_part, dict_part)

    return domain


_always_atomic = (Intervall,)
_potential_atomic = (list, tuple, set, frozenset)
_never_atomic = (dict, Product, Space)

def _is_atomic(domain):
    """
    Check whether the argument should evaluate to an atomic space.
    """
    if isinstance(domain, Space):
        raise SpaceError('Should not be called with a Space.')

    if type(domain) in _never_atomic:
        return False

    elif type(domain) in _potential_atomic:
        all_cls = _always_atomic + _potential_atomic + _never_atomic
        return not any(
            isinstance(d, all_cls)
            for d in domain)

    else:
        return True


def _pick_class(domain):

    #log.debug('_pick_class:' + str(domain))

    if isinstance(domain, Space):
        raise SpaceInferenceError('Should not be called with a Space.')

    atomic = _is_atomic(domain)

    if atomic:

        if type(domain) in (tuple,list):
            cls = Discrete

        elif type(domain) == set:
            cls = Categorical

        elif type(domain) == Intervall:
            if domain.type_ == 'continuous':
                cls = Continuous
            elif domain.type_ == 'discrete':
                cls = Discrete

        else: cls = Constant

    else:
        if type(domain) == set:
            cls = JoinedSpace
        elif type(domain) in (list, tuple, dict, Product):
            cls = ProductSpace

        elif type(domain) == Call:
            cls = CallSpace

    if 'cls' not in locals():
        raise SpaceInferenceError(
            'Cound not find fitting Space class for %satomic %s'
            % ('' if atomic else 'non-', type(domain)))

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
    if len(args) == 0:
        return JoinedSpace([])
    if _is_atomic(args):
        return Categorical(args)
    else:
        domain = _spacify(args)
        return JoinedSpace(domain)


def pprint(space, linebreaks=True, str_func=str):
    print(pformat(space, linebreaks, str_func))


def pformat(space, linebreaks=True, str_func=str):
    stack = []
    prefix = ' '*4
    sep1 = '\n' if linebreaks else ''
    sep2 = '\n' if linebreaks else ' '
    sep3 = ',\n' if linebreaks else ''
    sep4 = ' = '  if linebreaks else '='

    def go_deeper(space):
        log.debug('spacetype:%s' % type(space))
        if isinstance(space, AtomicSpace):
            return str_func(space)

        only_constants = all(
            isinstance(v, Constant) or not isinstance(v, Space)
            for v in space.domain)

        if (only_constants):
            return str_func(space)

        if space in stack:
            return type(space).__name__ + ' ...'

        stack.append(space)

        if type(space.domain) == Product:
            params = [
                go_deeper(arg)
                for arg in space.domain.args
            ]
            params += [
                k + sep4 + go_deeper(v)
                for k,v in space.domain.kwargs.items()
            ]

        elif type(space.domain) == list:
            params = [go_deeper(arg) for arg in space.domain]

        else:
            raise SpaceFormattingError(
                'Invalid domain type: %s' % type(space.domain))

        params = (',' + sep2).join(params)

        if linebreaks:
            params = textwrap.indent(params, prefix)

        # TODO: This part should be changed for repr
        if type(space) == ProductSpace:
            out = '[', sep1, params, sep3, ']'
        elif type(space) == JoinedSpace:
            out = '{', sep1, params, sep3, '}'
        elif type(space) == CallSpace:
            out = str_func(space.operator), '(', sep1, params, sep3, ')'
        else:
            raise SpaceFormattingError(
                'Invalid domain type: %s' % type(space.domain))

        stack.pop()
        return ''.join(out)


    return go_deeper(space)


class TempCollection(list):
    def __or__(self, arg):
        if type(arg) == TempCollection:
            self.extend(arg)
        else:
            self.append(arg)
        return self


# ---------- Exceptions ----------------------------------------------------- #

class SpaceError(Exception):
    pass

class SpaceInferenceError(SpaceError):
    pass

class SpaceCombinationError(SpaceError):
    pass

class SpaceFormattingError(SpaceError):
    pass


# ------ Predifined operators ----------------------------------------------- #

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
