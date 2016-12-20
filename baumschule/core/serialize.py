"""
Pretty formats for parameters.
"""
import logging
import textwrap

from .spaces import Apply, Parameter, Operation
from .space_utils import is_recursive

log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel('INFO')


def serialize(param, lispstyle=False):
    """
    Converts non-recursive trees into a Parseable string.

    Not recursion save.
    """

    assert not is_recursive(param),\
        'serialization of recursive structures not supported yet'

    sep = ', '

    if type(param) == Apply:

        op_name = serialize(param.operation)

        arg_vals = tuple(map(serialize, param.domain.args))
        if param.domain.kwargs:
            kwarg_keys, kwarg_vals = zip(*param.domain.kwargs.items())
            kwarg_vals =  map(serialize, kwarg_vals)
            kwarg_items = [
                '%s=%s' % item for item in zip(kwarg_keys, kwarg_vals)]
        else:
            kwarg_items = ()

        if lispstyle:
            pattern = '({name}{sep1}{args}{sep2}{kwargs})'
        else:
            pattern = '{name}({sep1}{args}{sep2}{kwargs})'

        return pattern.format(
            name = op_name,
            sep1 = sep if lispstyle else '',
            args = sep.join(arg_vals),
            sep2 = sep if arg_vals and kwarg_items else '',
            kwargs = sep.join(kwarg_items),
        )
    else:
        return str(param)


def pformat(param, linebreaks=True, str_func=str):
    stack = []
    prefix = ' '*4
    sep1 = '\n' if linebreaks else ''
    sep2 = '\n' if linebreaks else ' '
    sep3 = ',\n' if linebreaks else ''
    sep4 = ' = '  if linebreaks else '='

    def go_deeper(param):
        log.debug('paramtype:%s' % type(param))
        if not isinstance(param, Apply):
            return str_func(param)

        only_values = all(
            not isinstance(v, Parameter)
            for v in param.domain)

        if only_values:
            return str_func(param)

        if param in stack:
            return type(param).__name__ + ' ...'

        stack.append(param)

        args = [
            go_deeper(arg)
            for arg in param.domain.args
        ]
        args += [
            k + sep4 + go_deeper(v)
            for k,v in param.domain.kwargs.items()
        ]

        args = (',' + sep2).join(args)

        if linebreaks:
            args = textwrap.indent(args, prefix)

        out = param.operation.name, '(', sep1, args, sep3, ')'
        stack.pop()
        return ''.join(out)

    return go_deeper(param)


def pformat_apply(param):
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


def pprint(param, linebreaks=True, str_func=str):
    print(pformat(param, linebreaks, str_func))
