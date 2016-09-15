class Algorithm:

    domain = NotImplemented
    codomain = NotImplemented
    parameter_space = NotImplemented
    
    def configure(self, *args, **kwargs):
        raise NotImplementedError()

    def execute(self, *args, **kwargs):
        raise NotImplementedError()

    def __call__(self, *args, **kwargs):
        return self.execute(*args, **kwargs) 


class MlAlgorithm(Algorithm):
    
    def fit(self, *args, **kwargs):
        raise NotImplementedError() 

