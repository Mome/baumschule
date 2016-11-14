from itertools import chain, product

from .parameters import (
    Parameter, Apply, Primitive,
    join)

from .domains import ParameterList

def iterate_instances(param, iter_primitives=True):
    """
    Iterates executable instances of a parameter.

    """

    if not isinstance(param, Parameter):
        yield param

    elif isinstance(param, Primitive):
        if iter_primitives:
            yield from param.domain
        else:
            yield param

    else:
        if param.operation == join:
            yield from chain(*map(iterate_instances, param.domain))

        else:
            if not isinstance(param.operation, Parameter):
                operations = [param.operation]
            else:
                operations = param.operation

            op_iter = iterate_instances(operations)
            pml_iterator = _ii_pml(param.domain)
            for op, pml in product(op_iter, pml_iterator):
                yield Apply(op, pml)



def _ii_pml(pml):
    """
    Iterates over instances of a parameter list.

    """
    keys = tuple(pml.keys())
    inst_iterators = map(iterate_instances, pml.values())
    for instance in product(*inst_iterators):
        d = dict(zip(keys, instance))
        yield ParameterList.from_dict(d)
