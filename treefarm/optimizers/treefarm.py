
from itertools import chain


from ..core.parameters import Apply, Primitive, join, Operation, Combination
from ..core.domains import ParameterList

class TreeFarm:

    def __init__(self, search_space):
        ...


def expand(search_space, index_vector, include_primitives=False):
    # TODO shall accept slices?
    # TODO how to index numerical primitives?
    # TODO no index with strings yet

    fcs = fc_shape(search_space, include_primitives)
    assert len(index_vector) == len(fcs)

    index_iter = iter(index_vector)

    def _expand(search_space):
        if type(search_space) == Apply:
            dom = search_space.domain
            op = search_space.operation
            if isinstance(op, Combination):
                if op == join:
                    # TODO get a problem here, if indexed by key!!
                    return dom[next(index_iter)]
                else:
                    raise NotImplementedError(
                        'Join only as combination allowed.')
            else:
                if isinstance(op, Apply):
                    op = _expand(op)

                chosen_values = map(_expand, dom.values())
                params = dict(zip(dom.keys(), chosen_values))
                dom = ParameterList([], params)
                return Apply(op, dom)

        elif isinstance(search_space, Primitive):
            if include_primitives:
                raise NotImplementedError(
                    'Indexing primitives not allowed yet.')
            else:
                return search_space
        else:
            raise NotImplementedError('Not a parameter.')

    return _expand(search_space)




def fc_shape(search_space, include_primitives=True):
    """
    Returns the flat choice shape of a search space.

    """
    _fc_shape = lambda ss : fc_shape(ss, include_primitives)

    shape = []
    if type(search_space) == Apply:
        dom = search_space.domain
        op = search_space.operation
        if isinstance(op, Combination):
            if op == join:
                print('append op join')
                shape.append(len(dom))
            else:
                raise NotImplementedError('Only join as combination allowed.')
        else:
            if isinstance(op, Apply):
                subshapes = _fc_shape(op)
                print('extend dom Apply')
                shape.extend(subshapes)

            subshapes = map(_fc_shape, dom)
            print('extend dom Apply')
            shape.extend(chain(*subshapes))

    elif isinstance(search_space, Primitive):
        if include_primitives:
            print('append include primitives')
            shape.append(len(search_space))

    else:
        raise NotImplementedError('Not a parameter.')

    return tuple(shape)
