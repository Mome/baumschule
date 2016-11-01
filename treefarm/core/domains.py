class ParameterList:
    """
    Prepresents a product of a list and a dictionary.
    """

    def __init__(self, args, kwargs):
        self.args = list(args)
        self.kwargs = dict(kwargs)

    def keys(self):
        yield from range(len(self.args))
        yield from sorted(self.kwargs.keys())

    def values(self):
        yield from self.args
        for k in sorted(self.kwargs.keys()):
            yield self.__getitem__(k)

    def items(self):
        yield from enumerate(self.args)
        yield from sorted(self.kwargs.items())

    def append(self, value):
        self.args.append(value)

    def extend(self, list_arg):
        self.args.extend(list_arg)

    def update(self, dict_arg):
        # TODO: make sure numbers are sorted in correctly
        self.kwargs.update(arg)

    def get(self, key, default=None):
        if key in self.keys():
            return self[key]
        else:
            return default

    def __iter__(self):
        return self.values()

    @staticmethod
    def _test_slice(key):
        if key.start == None:
            raise KeyError('Start cannot be None!')
        if key.stop == None:
            raise KeyError('Stop cannot be None!')
        if key.step != None:
            raise KeyError('Step must be None!')

    def __getitem__(self, key):
        if type(key) == int:
            return self.args[key]
        elif type(key) == str:
            return  self.kwargs[key]
        else:
            raise ValueError('Invalid index/key type: %s' % type(key))

    def __setitem__(self, key, val):
        if type(key) == int:
            self.args[key] = val
        elif type(key) == str:
            self.kwargs[key] = val
        else:
            raise ValueError('Only str and int are valied keys.')

    def __str__(self):
        args_str = map(str, self.args)
        kwargs_str = ('%s=%s' % item for item in self.kwargs.items())
        return '[' + ', '.join([*args_str, *kwargs_str]) + ']'

    def __len__(self):
        return len(self.args) + len(self.kwargs)

    def __repr__(self):
        args_str = map(repr, self.args)
        kwargs_str = ('%s=%r' % item for item in self.kwargs.items())
        params = ', '.join([*args_str, *kwargs_str])
        return '%s(%s)' % (self.__class__.__name__, params)


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
                bounding = step,
            )
        else:
            raise KeyError(key)

        return new

    def __str__(self):
        return 'Intervall(%s, %s, %s)' % (self.sub, self.sup, self.type_)


# ------ Predifined Domains ----------------------------------------- #

N = Intervall(
    sub=float('-inf'),
    sup=float('inf'),
    type_='discrete',
    bounding='unbounded',)

R = Intervall(
    sub=float('-inf'),
    sup=float('inf'),
    type_='continuous',
    bounding='unbounded',)
