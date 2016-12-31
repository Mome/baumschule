from .domains import ParameterList
from .spaces import Apply, quote, prod, Operation, power, Combination
from .serialize import serialize

class ComputingEngine:
    def evaluate(self, computation_graph):
        raise NotImplementedError()


class SimpleEngine(ComputingEngine):

    def evaluate(self, func_tree):
        # assume simple operators for now

        # only function application can be evaluated
        if not type(func_tree) is Apply:
            return func_tree

        # quotes just get unwrapped
        if func_tree.operation == quote:
            return func_tree.domain

        # evaluate operation
        if type(func_tree.operation) == Apply:
            op = self.evaluate(func_tree.operation)
        else:
            op = func_tree.operation
            
        dom = func_tree.domain

        # combination are evaluated from ouside to inside
        # operations are evaluated from the inside to the outside
        if type(op) == Combination:
            comb = op.func(
                *dom.args,
                **dom.kwargs)
            result = self.evaluate(comb)
        else:
            plist = ParameterList([], {})
            for key, val in func_tree.domain.items():
                val = self.evaluate(val)
                if type(key) == int:
                    if type(val) is ParameterList:
                        plist.update(val, overwrite=False)
                    else:
                        plist.append(val)
                elif type(key) == str:
                    assert key not in plist.keys()
                    plist[key] = val
                else:
                    raise KeyError(
                    'Only str and int allowed as keys! type: %s' % type(key))

            if type(op) == Operation:
                func = op.func
            else:
                func = op

            result = func(
                *plist.args,
                **plist.kwargs)

        return result


compute = SimpleEngine().evaluate
