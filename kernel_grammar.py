from itertools import combinations_with_replacement as combi_wr
import time
from random import choice

# ---- parser to construct kernel trees from string ---- #
OPERATIONS = ['mul', 'add']
KERNELS = ['EXP', 'RBF']
cfg_grammar ="""
node -> K | '(' K OP K ')'
"""
cfg_grammar += '\n'.join([
        "OP -> '" + "' | '".join(OPERATIONS) + "'",
        "K -> '"  + "' | '".join(KERNELS) + "'",
    ])
#import nltk
#parser = nltk.ChartParser(nltk.CFG.fromstring(cfg_grammar))


def kernel_search(kernels, operations, eval_func, time_out=0):

    start = time.time()
    root = TreeRoot()
    best_error = float('inf')

    # choose initial Kernel
    for K in kernels:
        root.node = GrammarLeaf(K)
        error = eval_func(root)
        if error < best_error:
            best_kernel = K
            best_error = error
            print('error', error)

    root.node = GrammarLeaf(best_kernel)
    agenda = [(root, 'node')]

    while agenda:
        node, pos = agenda.pop()
        leaf = node.__dict__[pos]
        better_operation = None

        for op in operations:
            for K1, K2 in combi_wr(kernels, 2):
                L1 = GrammarLeaf(K1)
                L2 = GrammarLeaf(K2)
                new_node = GrammarTree(L1, op, L2)
                node.__dict__[pos] = new_node

                try:
                    error = eval_func(root)
                except Exception as e:
                    print('Evaluation failed:', e)
                    node.__dict__[pos] = GrammarLeaf
                    continue
                
                print('error', error, '\n')
                if error < best_error:
                    better_kernels = (L1, L2)
                    better_operation = op
                    best_error = error

        if better_operation :
            new_node.first = better_kernels[0]
            new_node.second = better_kernels[0]
            new_node.operation = better_operation
            agenda.append((new_node, 'first'))
            agenda.append((new_node, 'second'))
            #print('improve:', str(node))
        else:
            node.__dict__[pos] = leaf

        if time_out:
            if time_out < time.time()-start:
                print('# ---------------- Time out! --------------------- #')
                break

    return root, best_error


class TreeRoot():
    def __init__(self, node=None):
        self.node = node

    @classmethod
    def from_string(cls, string):
        string = string.replace('\n',' ')
        string = string.replace('\t',' ')
        bgt = cls._from_string(string)
        return TreeRoot(bgt)

    @classmethod
    def _from_string(cls, string):
        string = string.strip()

    """@classmethod
    def _from_string(cls, string):
        string = string.strip()
        if string.startswith('[') and string.endswith(']'):



            string = string[1:-1] # cut brackets
            string = string.strip()
            parts  = string.split()
            parts  = list(filter(bool, parts))
            print('parts',parts)
            first = cls._from_string(parts[0])
            op = parts[1]
            second = cls._from_string(parts[2])
            out = GrammarTree(first, op, second)
        else:
            out = GrammarLeaf(string)

        return out"""

    def __str__(self):
        return 'TreeRoot(' + str(self.node) + ')'

    def __repr__(self):
        return str(self)


class GrammarTree:

    def __init__(self, first=None, operation=None, second=None):
        self.first = first
        self.operation = operation
        self.second = second

    def __str__(self):
        content = ' '.join([str(self.first), self.operation, str(self.second)])
        return '(' + content + ')'


class GrammarLeaf:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name
