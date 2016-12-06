from itertools import chain, product
from functools import partial

from .spaces import (
    Parameter, Apply, Primitive,
    join)

from .domains import ParameterList

def iter_instances(param, iter_primitives=True):
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
        iteri = partial(iter_instances, iter_primitives=iter_primitives)
        if param.operation == join:

            yield from chain(*map(iteri, param.domain))

        else:
            if not isinstance(param.operation, Parameter):
                operations = [param.operation]
            else:
                operations = param.operation

            op_iter = iteri(operations)
            pml_iterator = _ii_pml(param.domain, iter_primitives)
            for op, pml in product(op_iter, pml_iterator):
                yield Apply(op, pml)



def _ii_pml(pml, iter_primitives):
    """
    Iterates over instances of a parameter list.

    """
    keys = tuple(pml.keys())
    iteri = partial(iter_instances, iter_primitives=iter_primitives)
    inst_iterators = map(iteri, pml.values())
    for instance in product(*inst_iterators):
        d = dict(zip(keys, instance))
        yield ParameterList.from_dict(d)


# notions of containment
# - subset
# - substructure
# - element
# - direct substructure
# - direct subset
#
#
#
