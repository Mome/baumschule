from ..core.environment import Environment
from ..core.spaces import Operation

# ------------------ container operations ---------------------- #

def dict_func(*args, **kwargs):
    return {**dict(enumerate(args), **kwargs)}

def list_func(*args, **kwargs):
    return [*args, *kwargs.values()]

def set_func(*args, **kwargs):
    return {*args, *kwargs.values()}

def tuple_func(*args, **kwargs):
    return args + tuple(kwargs.values())


dict_op = Operation(
    func=dict_func,
    name='dict',
    properties={'variadic'},
)

list_op = Operation(
    func=list_func,
    name='list',
    properties={'variadic'},
)

set_op = Operation(
    func=set_func,
    name='dict',
    properties={
        'commutative', # argument order irrelevant
        'idempotent',  # identical arguments have no effect
        'variadic'},
)

tuple_op = Operation(
    func=tuple_func,
    name='tuple',
    properties={'variadic'},
)


__all__ = [dict_op, list_op, set_op, tuple_op]
