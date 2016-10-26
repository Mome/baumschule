from .domains import Call, Product

class ComputingEngine:
    def __init__(self, cores):
        self.cores = cores

    def evaluate_func(self, function, parameters):
        if type(parameters) == Product:
            result = function(*parameters.args, **parameters.kwargs)
        elif type(parameters) in (list, tuple):
            result = function(*parameters)
        elif type(parameters) == dict:
            result = function(**parameters)
        else:
            result = function(parameters)
        return result

    def evaluate(self, func_tree):
        # assume simple operators for now

        if isinstance(func_tree, Product):
            list_result = [
                self.evaluate(sub)
                for sub in func_tree.args]
            dict_result = {
                key:self.evaluate(val)
                for key, val in func_tree.kwargs.items()}
            domain_result = Product(list_result, dict_result)
        else:
            domain_result = func_tree

        if type(func_tree) == Call:
            result = self.evaluate_func(
                function = func_tree.operator.func,
                parameters = domain_result)
        else:
            result = domain_result

        return result
