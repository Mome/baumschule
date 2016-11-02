from .parameters import Apply
from .domains import ParameterList

def simplify(param):
    if type(param) != Apply:
        return param

    op = param.operation
    dom = ParameterList.from_dict(
        {k:simplify(v) for k,v in param.domain.items()})

    if {'variadic', 'associative'}.issubset(op.properties):
        for D in dom:
            if type(D) == Apply and D.operation == op:
                dom = join_same_child_operations(op, dom)

    if 'idempotent' in op.properties:
        dom = delete_duplicate_children(op, dom)

    if 'kommutative' in op.properties:
        ...

    return Apply(op, dom)


def join_same_child_operations(op, dom):
    new_dom = ParameterList([], {})
    for key, val in dom.items():
        if type(val) == Apply and val.operation == op:
            new_dom.extend(val.domain)
        else:
            if type(key) == str:
                new_dom[key] = val
            else:
                new_dom.append(val)
    return new_dom


def delete_duplicate_children(op, dom):
    """Does not touch keyword arguments ..."""
    args = []
    for val in dom.args:
        if val not in args:
            args.append(val)
    dom = ParameterList(args, dom.kwargs)
    return dom
