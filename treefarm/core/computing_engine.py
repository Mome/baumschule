from .domains import ParameterList
from .parameters import Apply

class ComputingEngine:
    def evaluate(self, computation_graph):
        raise NotImplementedError()


class SimpleEngine(ComputingEngine):

    def evaluate(self, func_tree):
        # assume simple operators for now

        # only function application can be evaluated
        if not type(func_tree) is Apply:
            return func_tree

        list_result = [
            self.evaluate(sub)
            for sub in func_tree.domain.args]
        dict_result = {
            key:self.evaluate(val)
            for key, val in func_tree.domain.kwargs.items()}

        result = func_tree.operation.func(
            *list_result,
            **dict_result)

        return result


compute = SimpleEngine().evaluate
