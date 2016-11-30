from math import inf

from .utils import divisible

class ParameterList:
    """
    Prepresents a product of a list and a dictionary.
    keys(), values() and items() all return from both list and dict part
    keeps order
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

    def update(self, dict_arg, overwrite=True):
        # TODO: make sure numbers are sorted in correctly
        if not overwrite:
            assert not any(dict_arg.keys() for k in self.keys()), \
                'Parameterlists with common keyword argument cannot be combined'
        self.kwargs.update(dict_arg)

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

    @classmethod
    def from_dict(cls, dict_arg):
        return cls.from_items(dict_arg.items())

    @classmethod
    def from_items(cls, items):
        num_items = []
        kwargs = {}
        for k,v in items:
            if type(k) == int:
                num_items.append((k,v))
            elif type(k) == str:
                kwargs[k] = v
            else:
                raise KeyError('Key must be str or int.')
        num_items.sort()
        indices, args = zip(*num_items)
        assert tuple(range(len(indices))) == indices, \
            'integer keys must all integres from 0 to n'
        return cls(args, kwargs)

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
        return ', '.join([*args_str, *kwargs_str])

    def __len__(self):
        return len(self.args) + len(self.kwargs)

    """def __repr__(self):
        args_str = map(repr, self.args)
        kwargs_str = ('%s=%r' % item for item in self.kwargs.items())
        params = ', '.join([*args_str, *kwargs_str])
        return '%s(%s)' % (self.__class__.__name__, params)"""

    def __lshift__(self, arg):
        if type(arg) == ParameterList:
            self.extend(arg.args)
            self.update(arg.kwargs, overwrite=False)
        else:
            self.append(arg)


class Interval:
    """Used to represent a discrete or continous range of values."""

    def __init__(self, start, stop, step, left_closed=True, right_closed=False):
        assert start < stop
        assert step >= 0
        self.start = start
        self.stop = stop
        self.step = step
        self.left_closed = left_closed
        self.right_closed = right_closed

    @property
    def bounded(self):
        return self.start > -inf and self.stop < inf

    @property
    def closed(self):
        return self.left_closed or self.right_closed

    def __contains__(self, arg):
        start, stop, step = self.start, self.stop, self.step

        if isinstance(arg, (int, float)):
            if not (start <= num <= stop):
                return False
            if arg == start :
                return self.left_closed
            if arg == stop and not self.right_closed:
                return False
            if step == 0:
                return True
            return divisible(num - start, step)

        if isinstance(arg, Intervall):
            if not (arg.start in self and arg.stop in self):
                return False
            if step == 0:
                return True
            if arg.step < step:
                return False
            raise NotImplementedError()

        return False

    def __getitem__(self, key):
        # TODO: make step actually more meaningfull
        if not type(key) is slice:
            raise KeyError(key)

        start = self.start if key.start is None else key.start
        stop = self.stop if key.stop is None else key.stop
        step = self.step if key.step is None else key.step
        left_closed = False if start == -inf else self.step or self.left_closed
        right_closed = False if stop == inf else self.step or self.right_closed

        # check types
        for s in (start, stop, step):
            if type(s) not in {int, float}:
                raise KeyError('Start and Stop must be Numbers!')

        return Interval(
            start, stop, step, left_closed, right_closed)

    def __iter__(self):
        if self.step == 0:
            raise NotIterableError('Continuous Interval cannot be iterated.')
        if not self.bounded:
            raise Warning('Iteration of infinite %s will take forever.' % self)
            raise NotImplementedError()

        if self.left_closed:
            yield self.start

        values = iter(range(self.start, self.stop, self.step))
        next(values) # skip start value
        for val in values:
            yield val

        # how to avoid floating point arithmetics erros here
        if self.left_closed and val + self.step == self.stop:
            return self.stop

    def __len__(self):
        if step == 0 or not self.bounded:
            return inf
        bounds = self.left_closed + self.right_closed
        return self.stop - self.start - bounds

    def __str__(self):
        # return 'Interval(%s, %s, %s)' % (self.start, self.stop, self.type_)
        stop, start, step = self.stop, self.start, self.step

        return '{name}{left}{start}:{stop}{step}{right}'.format(
            name = 'Cont' if step == 0 else 'Disc',
            left = '[' if self.left_closed else '(',
            start = '-∞' if start == -inf else start,
            stop = '∞' if stop == inf else stop,
            step = '' if step in {0,1} else ':%s' % step,
            right = ']' if self.right_closed else ')',
        )


# --------------- Predifined Domains ---------------------------------------- #

N = Interval(
    start = 1,
    stop = inf,
    step = 1,
    left_closed = True,
    right_closed = False)

N0 = Interval(
    start = 0,
    stop = inf,
    step = 1,
    left_closed = True,
    right_closed = False)

Z = Interval(
    start = -inf,
    stop = inf,
    step = 1,
    left_closed = False,
    right_closed = False,)

R = Interval(
    start = -inf,
    stop = inf,
    step = 0,
    left_closed = False,
    right_closed = False,)


# -------------------------- Errors ----------------------------------------- #

class NotIterableError(Exception):
    pass
