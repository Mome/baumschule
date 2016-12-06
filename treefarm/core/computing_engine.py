from .domains import ParameterList
from .spaces import Apply, quote, prod

class ComputingEngine:
    def evaluate(self, computation_graph):
        raise NotImplementedError()


class SimpleEngine(ComputingEngine):

    def evaluate(self, func_tree):
        # assume simple operators for now

        # only function application can be evaluated
        if not type(func_tree) is Apply:
            return func_tree

        if func_tree.operation == quote:
            return func_tree.domain

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

        """list_result = [
            self.evaluate(sub)
            for sub in func_tree.domain.args]
        dict_result = {
            key:self.evaluate(val)
            for key, val in func_tree.domain.kwargs.items()}"""

        #print(func_tree.operation, plist.args, plist.kwargs)

        result = func_tree.operation.func(
            *plist.args,
            **plist.kwargs)

        return result


compute = SimpleEngine().evaluate
