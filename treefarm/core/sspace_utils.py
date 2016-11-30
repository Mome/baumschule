
from .parameters import Apply, Combination, Primitive


def expand(sspace, index_vector, include_primitives=False):
    # TODO shall accept slices?
    # TODO how to index numerical primitives?
    # TODO no index with strings yet

    fcs = fc_shape(sspace, include_primitives)
    assert len(index_vector) == len(fcs)

    index_iter = iter(index_vector)

    def _expand(sspace):
        if type(sspace) == Apply:
            dom = sspace.domain
            op = sspace.operation
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
                params = zip(dom.keys(), chosen_values)
                dom = ParameterList.from_items(params)
                return Apply(op, dom)

        elif isinstance(sspace, Primitive):
            if include_primitives:
                raise NotImplementedError(
                    'Indexing primitives not allowed yet.')
            else:
                return sspace
        else:
            raise NotImplementedError('Not a parameter.')

    return _expand(sspace)


def fc_shape(sspace, include_primitives=True):
    """
    Returns the flat choice shape of a search space.

    """
    _fc_shape = lambda ss : fc_shape(ss, include_primitives)

    shape = []
    if type(sspace) == Apply:
        dom = sspace.domain
        op = sspace.operation
        if isinstance(op, Combination):
            if op == join:
                shape.append(len(dom))
            else:
                raise NotImplementedError('Only join as combination allowed.')
        else:
            if isinstance(op, Apply):
                subshapes = _fc_shape(op)
                shape.extend(subshapes)

            subshapes = map(_fc_shape, dom)
            shape.extend(chain(*subshapes))

    elif isinstance(sspace, Primitive):
        if include_primitives:
            shape.append(len(sspace))

    else:
        raise NotImplementedError('Not a parameter.')

    return tuple(shape)
