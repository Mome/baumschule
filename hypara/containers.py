class Variable:
    def __init__(self):
        pass


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

        if args and kwargs:
            domain = MixedProduct(args, kwargs)
        elif args:
            params = list(args)
        elif kwargs:
            params = dict(kwargs)

        log.debug('call %s %s %s %s' % (self.name, args, kwargs, params))
        return Call(operator=self, domain=params)


class MixedProduct:
    """Prepresents a product of a list and a dictionary."""
    # TODO: add slices ?

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
        return list(self) # calls __iter__

    def __str__(self):
        args_str = map(str, self.args) 
        kwargs_str = ('%s=%s' % item for item in self.kwargs.items())
        return '(%s)' % ', '.join([*args_str, *kwargs_str])

    def __repr__(self):
        return 'MixedProduct(%s)' % str(self)

mixed = MixedProduct

class Call(MixedProduct):
    def __init__(self, operator, args, kwargs):
        super().__init__(args, kwargs)
        self.operator = operator

    def __str__(self):
        return self.operator + str(super())


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