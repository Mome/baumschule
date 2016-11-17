
from .parameters import Apply, Operation

sep = ' '

def serialize(param, lispstyle=False):
    """
    Converts non-recursive trees into a Parseable string.

    Not recursion save.
    """

    if type(param) == Apply:
        assert type(param.operation) == Operation
        arg_vals = map(serialize, param.domain.args)
        if param.domain.kwargs:
            kwarg_keys, kwarg_vals = zip(*param.domain.kwargs.items())
            kwarg_vals =  map(serialize, param.domain.args)
            kwarg_items = [
                '='.join(k,v) for k,v in zip(kwarg_vals, kwarg_keys)]
        else:
            kwarg_items = ()

        if lispstyle:
            pattern = '({name}{sep1}{args}{sep2}{kwargs})'
        else:
            pattern = '{name}({sep1}{args}{sep2}{kwargs})'

        return pattern.format(
            name = param.operation.name,
            sep1 = sep,
            args = sep.join(arg_vals),
            sep2 = sep if arg_vals and kwarg_items else '',
            kwargs = sep.join(kwarg_items),
        )
    else:
        return str(param)


"""
def deserialize(string, param):
    """
    Deserializes an instance given a parameter.

    """

    ...



Node = namedtuple('Node', [name, sons])
def parse(string):

    tmp_str = string.replace('(', sep + '(' + sep)
    tmp_str = string.replace(')', sep + ')' + sep)
    tokens = list(filter(bool, tmp_str.split(sep)))

    assert tokens[0] != '()'

    stack = []
    node = Apply(tokens.pop(), ParameterList([], {}))
    for t in tokens:
        if token == '(':
            stack.append(node)
            pmlist"""
