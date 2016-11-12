from .parameters import Apply, Operation, Parameter
from .domains import ParameterList


def simplify(param):

    recursion_tracker = {}

    def _simplify(param):
        if type(param) != Apply:
            return param
        if id(param) in recursion_tracker:
            return param

        recursion_tracker[id(param)] = None

        op = param.operation
        dom = ParameterList.from_dict(
            {k:_simplify(v) for k,v in param.domain.items()})

        if isinstance(op, Operation):
            if {'variadic', 'associative'}.issubset(op.properties):
                for D in dom:
                    if type(D) == Apply and D.operation == op:
                        dom = join_same_child_operations(op, dom)

            if 'idempotent' in op.properties:
                dom = delete_duplicate_children(op, dom)

            if 'kommutative' in op.properties:
                ...

        elif isinstance(op, Parameter):
            op = _simplify(op)

        else:
            pass

        new = Apply(op, dom)
        recursion_tracker[id(param)] = new
        return new

    simpler = _simplify(param)
    simpler = replace_nodes(simpler, recursion_tracker)
    return simpler


def replace_nodes(param, tracker):
    if not isinstance(param, Apply):
        return param
    if id(param) in tracker:
        return tracker[id(param)]

    for k,D in param.domain.items():
        D = replace_nodes(D, tracker)
        param.domain[k] = D

    return param

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
