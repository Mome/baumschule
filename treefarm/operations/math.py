import operator as pyop

from ..core.parameters import Operation

# ---------------------- Artihmetics --------------------- #

add = Operation(
    name="add",
    func=pyop.add,
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
    func=pyop.mul,
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
