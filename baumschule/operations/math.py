import operator as pyop

from ..core.spaces import Operation


def add_op(*args):
    out = args[0]
    for x in args[1:]:
        out = out + x
    return out

def mul_op(*args):
    out = args[0]
    for x in args[1:]:
        out = out * x
    return out

# ---------------------- Artihmetics --------------------- #

add = Operation(
    name="add",
    func=add_op,
    properties=(
        'associative',
        'commutative',
        'variadic'),
    symbol='+',
    notation='infix')

sub = Operation(
    name="sub",
    func=pyop.sub,
    symbol='-',
    notation='infix')

mul = Operation(
    name="mul",
    func=mul_op,
    properties=(
        'associative',
        'commutative',
        'variadic'),
    symbol='⋅',
    notation='infix')

pow = Operation(
    name="pow",
    func=pyop.pow,
    symbol='^',
    notation='infix')

truediv = Operation(
    name="div",
    func=pyop.truediv,
    symbol='÷',
    notation='infix')

floordiv = Operation(
    name="floordiv",
    func=pyop.floordiv,
    symbol='//',
    notation='infix')

div = truediv

__all__ = [add, sub, mul, div, pow]
