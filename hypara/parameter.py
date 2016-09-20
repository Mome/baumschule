from collections.abc import Sequence
from random import choice
import operator as python_operator

import numpy.random as rnd

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
        raise Parameter_inferenceError('Unknown type: %s' % arg)


class ParameterSpace:

    def __init__(self, domain, *, dist=None, name=None, symbol=None):
        print('call da self')
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

    def __or__(self, arg):
        return JoinedSpace([self, arg])

class CombinedSpace(ParameterSpace):
    def __iter__(self):
        return self.domain

    def __getitem__(self, key):
        return self.domain.__getitem__(key)


class JoinedSpace(CombinedSpace):

    def infer_dist(self):
        def dist():
            # choose subspace
            ss = choice(self.domain)
            return ss.sample()
        return dist

    def __str__(self):
        if self.symbol != None:
            return self.symbol
        csl = [str(D) for D in self.domain]
        csl = ', '.join(csl)
        return '{' + csl + '}'      


class GeneralProductSpace(CombinedSpace):
    pass


class NamedProductSpace(GeneralProductSpace):
    def infer_dist(self):
        return lambda : {k:v.sample() for k,v in self.domain.items()}

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
        return str(self.domain)


class Categorical(SimpleSpace):
    def infer_dist(self):
        return lambda : choice(self.domain)


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


class OperatorSpace(GeneralProductSpace):
    pass

class Operator:
    def __init__(self, func, name=None, symbol=None, notation=None):
        if notation is None:
            if symbol is None:
                notation = 'postfix'
            else:
                notation = 'infix'

        self.func = func
        self.name = name.strip() if name else name
        self.symbol = symbol
        self.notation = notation

    def __call__(self, *args, **kwargs):
        OperatorSpace
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

    def __call__(self, *args, **kwargs):
        calls.append(Call(args, kwargs))

    def __str__(self):
        str(domain)


def Parameter(domain, *args, **kwargs):
    if isinstance(domain, Sequence):    
        high_level = any(isinstance(val, ParameterSpace) for val in domain)
    if isinstance(domain, dict):
        high_level = any(isinstance(val, ParameterSpace) for val in domain.values())
    else:
        high_level = False

    if high_level and type(domain) is set:
        cls = JoinedSpace
    elif high_level and type(domain) in (list, tuple):
        cls = ProductSpace
    elif high_level and type(domain) is dict:
        cls = NamedProductSpace
    elif not high_level and type(domain) is set:
        cls = Categorical
    elif not high_level and type(domain) in (list, tuple):
        cls = Discrete
    elif not high_level and type(domain) is Intervall:
        if domain.type_ == 'continuous':
            cls = Continuous
        elif domain.type_ == 'discrete':
            cls = Discrete
    elif not high_level:
        cls = Constant
    else:
        raise Parameter_inferenceError('Cound not find fitting Parameter class!')

    print('put', domain, ',', args, 'and', kwargs, 'in', cls)
    
    return cls(domain, *args, **kwargs)


def prod(*args, **kwargs):
    if args and kwargs:
        raise Parameter_inferenceError('Cannot construct product from args and kwargs (Sequence and map)!')
    if args:
        return ProductSpace(args)
    if kwargs:
        return NamedProductSpace(kwargs)

def join(*args):
    args = [a if isinstance(a, ParameterSpace) else Parameter(a) for a in args]
    return JoinedSpace(args)



N = Intervall(float('-inf'), float('inf'), type_='discrete', bounding='unbounded')
R = Intervall(float('-inf'), float('inf'), type_='continuous', bounding='unbounded')


# predefinde operators
add = Operator(name="add", func=python_operator.add, symbol='+', notation='infix')
sub = Operator(name="add", func=python_operator.sub, symbol='-', notation='infix')
mul = Operator(name="mul", func=python_operator.mul, symbol='*', notation='infix')
pow = Operator(name="pow", func=python_operator.mul, symbol='^', notation='infix')





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
class Parameter_inferenceError(Exception):
    pass


        
        