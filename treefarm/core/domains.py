from math import inf

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
        num_items = []
        kwargs = {}
        for k,v in dict_arg.items():
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
        return '[' + ', '.join([*args_str, *kwargs_str]) + ']'

    def __len__(self):
        return len(self.args) + len(self.kwargs)

    def __repr__(self):
        args_str = map(repr, self.args)
        kwargs_str = ('%s=%r' % item for item in self.kwargs.items())
        params = ', '.join([*args_str, *kwargs_str])
        return '%s(%s)' % (self.__class__.__name__, params)

    def __lshift__(self, arg):
        if type(arg) == ParameterList:
            self.extend(arg.args)
            self.update(arg.kwargs, overwrite=False)
        else:
            self.append(arg)


class Intervall:
    """Used to represent a discrete or continous range of values."""

    def __init__(self, start, stop, step, left_open=False, right_open=True):
        assert start < stop
        assert step >= 0
        self.start = start
        self.stop = stop
        self.step = step
        self.left_open = left_open
        self.right_open = right_open

    def __iter__(self):
        if self.step == 0:
            raise NotIterableError('Continuous intervall cannot be iterated.')
        if not self.bounded:
            raise Warning('Iteration of infinite %s will take forever.' % self)
            raise NotImplementedError()

        if not self.left_open:
            yield self.start

        values = iter(range(self.start, self.stop, self.step))
        next(values) # skip start value
        yield from values

        if self.stop in self:
            yield self.stop

    def __contains__(self, num):
        start, stop, step = self.start, self.stop, self.step
        if start > num > stop:
            return False
        if num == start :
            return not self.left_open
        if num == stop :
            return not self.right_open
        if step == 0:
            return True
        return not ((num - start) % step)

    def __getitem__(self, key):

        if type(key) is slice:

            start, stop, step = key.start, key.stop, key.step

            if start is None:
                start = self.start
            if stop is None:
                stop = self.stop
            if step is None:
                # TODO: fit default bounding settings
                step = 'bounded'

            if not (isinstance(start, (int, float))
                or isinstance(step,  (int, float))):
                raise KeyError('Start and Stop must be Integers!')

            new = Intervall(
                start = start,
                stop = stop,
                type_ = self.type_,
                bounding = step,
            )
        else:
            raise KeyError(key)

        return new

    def __str__(self):
        # return 'Intervall(%s, %s, %s)' % (self.start, self.stop, self.type_)
        stop, start, step = self.stop, self.start, self.step

        return '{name}{left}{start}:{stop}{step}{right}'.format(
            name = 'Cont' if step == 0 else 'Disc',
            left = '(' if self.left_open else '[',
            start = '-∞' if start == -inf else start,
            stop = '∞' if stop == inf else stop,
            step = '' if step in {0,1} else ':%s' % step,
            right = ')' if self.right_open else ']',
        )

    @property
    def bounded(self):
        return self.start == -inf or self.stop == inf

    @property
    def closed(self):
        return not (self.left_open or self.right_open)

    def __len__(self):
        if step==0 or not self.bounded:
            return inf
        bounds = 2 - self.left_open - self.right_open
        return self.stop - self.start - bounds


# --------------- Predifined Domains ---------------------------------------- #

N = Intervall(
    start = 1,
    stop = inf,
    step = 1,
    left_open = False,
    right_open = False)

N0 = Intervall(
    start = 0,
    stop = inf,
    step = 1,
    left_open = False,
    right_open = False)

Z = Intervall(
    start = -inf,
    stop = inf,
    step = 1,
    left_open = True,
    right_open = True,)

R = Intervall(
    start = -inf,
    stop = inf,
    step = 1,
    left_open = True,
    right_open = True,)


# -------------------------- Errors ----------------------------------------- #

class NotIterableError(Exception):
    pass
