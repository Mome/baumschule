""" Implements the kernelsearch described in:
Duvenaud, David, et al. (2013)
"Structure discovery in nonparametric regression through compositional kernel search."
"""

from itertools import chain
from random import choice
import operator
import GPy.kern


class KernelComposition:

    TRANSLATIONS = {
        'RQ'       : lambda : GPy.kern.RatQuad(1),
        'SE'       : lambda : GPy.kern.ExpQuad(1),
        'Exp'      : lambda : GPy.kern.Exponential(1),
        'Bias'     : lambda : GPy.kern.Bias(1),
        'Lin'      : lambda : GPy.kern.Linear(1),
        'MLP'      : lambda : GPy.kern.MLP(1),
        'Brown'    : lambda : GPy.kern.Brownian(1),
        'Spline'    : lambda : GPy.kern.Spline(1),
        'Mat32'    : lambda : GPy.kern.Matern32(1),
        'Mat52'    : lambda : GPy.kern.Matern52(1),
        'Per'      : lambda : GPy.kern.StdPeriodic(1),
        'Cos'      : lambda : GPy.kern.Cosine(1),
        'PerExp'   : lambda : GPy.kern.PeriodicExponential(1),
        'PerMat32' : lambda : GPy.kern.PeriodicMatern32(1),
        'PerMat52' : lambda : GPy.kern.PeriodicMatern52(1),
        
        'add' : operator.add,
        'mul' : operator.mul,
        '+'   : operator.add,
        '*'   : operator.mul,
    }

    def __init__(self, kernels=(None,), compositions=()):

        assert (len(kernels)-1 == len(compositions))

        self.kernels = tuple(kernels)
        self.compositions = tuple(compositions)


    def basekernel_replacements(self, kernels):

        replaced_kerns = list(self.kernels)

        for i, old_K in enumerate(self.kernels):
            for new_K in kernels:
                if old_K == new_K:
                    continue
                replaced_kerns[i] = new_K
                yield KernelComposition(replaced_kerns, self.compositions)
            replaced_kerns[i] = old_K


    def basekernel_compositions(self, kernels, compositions):
        """Iterates over composion."""

        new_comps = list(self.compositions) + [None]
        new_kerns = list(self.kernels) + [None]

        for comp in compositions:
            for K in kernels:
                new_comps[-1] = comp
                new_kerns[-1] = K
                yield KernelComposition(new_kerns, new_comps)


    def __str__(self):
        return ' '.join(chain(*zip(self.kernels, self.compositions), self.kernels[-1:]))


    @classmethod
    def from_string(cls, string):
        #### TODO - whitespace independent parsing
        #### TODO - maybe integrate in constructor
        parts = [p for p in string.split() if p]
        return cls(parts[::2], parts[1::2])


    def search(self=None, basekernels=(), compositions=()):
        """Greedy search thourgh kernel space."""

        assert basekernels or compositions
        current = self

        # initialize with random basekernel
        if current == None:
            current = KernelComposition([choice(basekernels)])
            lowest_error = yield current
        else:
            lowest_error = float('inf')

        already_yielded = set(str(current)) # stores all evaluated kernels
        kernel_path = []

        while True:

            lowest_error = float('inf')

            new_kernels = chain(
                current.basekernel_replacements(basekernels),
                current.basekernel_compositions(basekernels, compositions))

            for new_K in new_kernels:
                if str(new_K) in already_yielded:
                    continue
                
                error_val = yield new_K
                already_yielded.add(str(new_K))

                while error_val == None:
                    error_val = yield kernel_path

                if error_val < lowest_error:
                    lowest_error = error_val
                    current = new_K

            kernel_path.append((current, lowest_error))


    def empty(self):
        return self.kernels[0] is None


    def compile(self):
        if self.empty(): raise Exception('Nothing to compile: KernelComposition is empty!')

        # normalize ids
        kernels = [k_id.upper() for k_id in self.kernels]
        compositions = [c_id.lower() for c_id in self.compositions]

        # pick actual gpy kernels and composition functions
        kernels = [KernelComposition.TRANSLATIONS[k_id] for k_id in kernels]
        compositions = [KernelComposition.TRANSLATIONS[c_id] for c_id in compositions]

        # instanciate kernels
        kernels = [K() for K in kernels]

        compiled_kernel = kernels[0]

        for K, comp in zip(kernels[1:], compositions):
            compiled_kernel = comp(compiled_kernel, K)

        return compiled_kernel

    





# maybe for later use, now the linear representation of the composition is sufficient
"""class KernelTree:

    def __init__(self, basekernel=None, composition=None, subtree=None):

        # both composition and subtree must have no value or both must have a value
        assert (composition and subtree) or (not composition and not subtree)

        self.basekernel = basekernel
        self.composition = composition
        self.subtree = subtree
        

    def basekernel_replacements(self, kernels):
        "Iterates over replacements of basekernels in the Kernel Tree with all other basekernels.""

        for K in kernels:
            if K == self.basekernel:
                continue
            yield KernelTree(K, self.composition, self.subtree)

        if self.subtree:
            for tree in self.subtree.basekernel_replacements(kernels):
                yield KernelTree(self.basekernel, self.composition, tree)


    def basekernel_composition(self, compositions, kernels):
        "Iterates over current kerneltree composed with other kernels.""

        # composition is only allowed with root nodes for now
        assert self.parent == None

        for comp in compositions:
            for K in kernels:
                yield KernelTree(
                    parent = self.parent,
                    basekernel = K,
                    composition = comp,
                    subtree = self)


    def __str__(self):
        return ' '.join([str(self.first), self.operation, str(self.second)])


    @classmethod
    def from_string(cls, string):
        parts = [p for p in string.split() if p]
        *rest_kernels, last_kernel = parts[::2]
        compositions = parts[1::2]


    def search(self=None, basekernels=(), compositions=()):

        assert basekernels or compositions

        if self == None:
            self = TreeRoot()

        scores = yield from self.basekernel_composition




        tested_kernels = [] # stores all evaluated kernels
        kernel_path = [] # stores kernel compositions which have been the best for one iterations

        best_error = float('inf')
        best_kernel = TreeRoot()

        for """


        
