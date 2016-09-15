import operator as python_operator
from collections import namedtuple
from types import FunctionType
from copy import copy


class ParameterSpace:

    def __init__(self, domain, dist=None, name=None, symbol=None):
        domain, dist = ParameterSpace._parse_args(domain, dist)
        self.domain = domain
        self.dist = dist
        self.name = name
        self.symbol = symbol
        self.calls = []
        self.joined = []

    @classmethod
    def _parse_args(cls, domain, dist):
        
        assert type(domain) in (set, ParameterSpace, Operator, type)
        
        if dist != None:
            assert type(dist) in (FunctionType, dict)

        return domain, dist

    def __contains__(self, element):
        for x in self.domain:
            if x == element:
                break
            if isinstance(x, ParameterSpace) and (element in ParameterSpace):
                break
            if (type(x) == Operator) and x.func == element:
                break
        else:
            return False

        return True


    def __or__(self, arg):

        if type(arg) == set:
            arg = ParameterSpace(arg)

        new_ps = ParameterSpace(domain={})

        if type(self.domain) == set:
            new_ps.domain |= self.domain
            new._ps.joined += self.joined

        return 


    def __ior__(self, arg):

        if type(self.domain) != set:
            raise 

        if type(arg) == set:
            arg = ParameterSpace(arg)

        if type(arg.domain) == type(self.domain) == set:
            self.domain |= arg.domain
            self.joined += arg.joined

        else:
            self.joined.append(arg) 



    def __call__(self, *args, **kwargs):
        calls.append(Call(args, kwargs))

    def __str__(self):
        str(domain)


class Operator:
    # TODO: Domain and Stuff?
    def __init__(self, name, func, symbol=None, notation=None):
        if notation is None:
            if symbol is None:
                notation = 'postfix'
            else:
                notation = 'infix'

        self.func = func
        self.name = name.strip()
        self.symbol = symbol
        self.notation = notation

    def __call__(self, *args, **kwargs):
        assert 'args' not in self.__dict__
        assert 'kwargs' not in self.__dict__
        cls_name = self.name.strip()
        cls = type(cls_name, (Operator,), {})
        op = cls(**self.__dict__)
        op.args = args
        op.kwargs = kwargs
        return op

    def __str__(self):
        assert ('args' in self.__dict__) == ('kwargs' in self.__dict__)
        if 'args' in self.__dict__:
            args = map(str, self.args)
            item_format = lambda item : str(item[0]) + '=' + str(item[1])
            kwargs = map(item_format, self.kwargs.items())
        else:
            args = [self.name]
            kwargs = []

        cls_name = type(self).__name__
        args_str = ', '.join([*args, *kwargs])

        return "{name}({args})".format(cls_name, args_str)


class SimpleParameter:

    def __init__(self, domain, dist=None, name=None, symbol=None):
        domain, dist = ParameterSpace._parse_args(domain, dist)
        self.domain = domain
        self.dist = dist
        self.name = name
        self.symbol = symbol
        self.calls = []

    @classmethod
    def _parse_args(cls, domain, dist):
        
        assert type(domain) in (set, ParameterSpace, Operator, type)
        
        if dist != None:
            assert type(dist) in (FunctionType, dict)

        return domain, dist

    def __contains__(self, element):
        for x in self.domain:
            if x == element:
                break
            if isinstance(x, ParameterSpace) and (element in ParameterSpace):
                break
            if (type(x) == Operator) and x.func == element:
                break
        else:
            return False

        return True


    def __or__(self, arg):

        if type(arg) == set:
            arg = ParameterSpace(arg)

        new_ps = ParameterSpace(domain={})

        if type(self.domain) == set:
            new_ps.domain |= self.domain
            new._ps.joined += self.joined



        return 

    def __ior__(self, arg):

        if type(self.domain) != set:
            raise 

        if type(arg) == set:
            arg = ParameterSpace(arg)

        if type(arg.domain) == type(self.domain) == set:
            self.domain |= arg.domain
            self.joined += arg.joined

        else:
            self.joined.append(arg) 



    def __call__(self, *args, **kwargs):
        calls.append(Call(args, kwargs))

    def __str__(self):
        str(domain)







# predefinde operators
add = Operator(name="add", func=python_operator.add, symbol='+', notation='infix')
sub = Operator(name="add", func=python_operator.sub, symbol='-', notation='infix')
mul = Operator(name="mul", func=python_operator.mul, symbol='*', notation='infix')
pow = Operator(name="pow", func=python_operator.mul, symbol='^', notation='infix')


# predefinde parameter spaces
R = ParameterSpace(domain=float, dist=None, name='real numbers', symbol='R')

class Categorical(ParameterSpace):

    def defualt_dist(self):
        return 1/len(self.domain)
