""" Implements the kernelsearch described in:
Duvenaud, David, et al. (2013)
"Structure discovery in nonparametric regression through compositional kernel search."
"""

from itertools import chain
from random import choice
import operator
import GPy.kern
from functools import reduce


class KernelComposition:

    TRANSLATIONS = {
        'RQ'       : lambda : GPy.kern.RatQuad(1),
        'RBF'       : lambda : GPy.kern.RBF(1),
        'Exp'      : lambda : GPy.kern.Exponential(1),
        'Bias'     : lambda : GPy.kern.Bias(1),
        'Lin'      : lambda : GPy.kern.Linear(1),
        'MLP'      : lambda : GPy.kern.MLP(1),
        'Brown'    : lambda : GPy.kern.Brownian(1),
        'Spline'    :lambda : GPy.kern.Spline(1),
        'Mat32'    : lambda : GPy.kern.Matern32(1),
        'Mat52'    : lambda : GPy.kern.Matern52(1),
        'Per'      : lambda : GPy.kern.StdPeriodic(1),
        'Cos'      : lambda : GPy.kern.Cosine(1),
        'PerExp'   : lambda : GPy.kern.PeriodicExponential(1),
        'PerMat32' : lambda : GPy.kern.PeriodicMatern32(1),
        'PerMat52' : lambda : GPy.kern.PeriodicMatern52(1),
        
        '+'   : operator.add,
        '*'   : operator.mul,
    }

    def __init__(self, kernels=('None',), compositions=()):

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
        #### TODO - maybe integrate in constructor
        parts = [p for p in string.split() if p]
        return cls(parts[::2], parts[1::2])


    def search(self=None, basekernels=(), compositions=()):
        """Greedy search thourgh kernel space."""

        assert basekernels or compositions
        current = self

        # initialize with random basekernel
        if current == None:
            current = KernelComposition()
            lowest_error = float('inf')

        already_yielded = set(str(current)) # stores all evaluated kernels
        kernel_path = []

        print('Start with', current, 'for exapansion!\n')

        while True:

            lowest_error = float('inf')

            if current.kernels[0] == 'None':
                new_kernels = current.basekernel_replacements(basekernels)
            elif not current.compositions:
                new_kernels = current.basekernel_compositions(basekernels, compositions)
            else:
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
            print('Chose', current, ' for exapansion!\n')


    def empty(self):
        return self.kernels[0] is None


    def compile(self, bind_multiplication_stronger=True):
        if self.empty(): raise Exception('Nothing to compile: KernelComposition is empty!')

        # pick actual gpy kernels
        kernels = [KernelComposition.TRANSLATIONS[k_id] for k_id in self.kernels]
        kernels = [K() for K in kernels] # instanciate kernels

        if bind_multiplication_stronger:

            # sort into bins for multiplication
            bins = [[kernels[0]]]
            for comp, K in zip(self.compositions, kernels[1:]):
                if comp in ('+', 'add'):
                    bins.append([K])
                elif comp in ('*', 'mul'):
                    bins[-1].append(K)
                else:
                    raise Exception('No a valid operator:' + c)


            # make a product of each bin and then sum it up
            for i,b in enumerate(bins):
                m = b[0]
                for K in b[1:]:
                    m = m*K
                bins[i] = m

            # sum up bins
            compiled_kernel = bins[0]
            for b in bins[1:]:
                compiled_kernel = compiled_kernel + b

        else: # strict left to right binding !
            compositions = [KernelComposition.TRANSLATIONS[c_id] for c_id in compositions]
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


        
