import numpy as np
from random import choice

from ..core.domains import Product
from ..core.spaces import JoinedSpace, ProductSpace, AtomicSpace

class TreeFarm:

    def __init__(self, space, default_reward):
        self.meta_tree = None
        self.reward_tree = RewardTree(space)
        self.space = space
        self.stump_path = ()


def RewardTree:
    def __init__(self, keys, crown, default_reward):
        self.keys = []
        self.crown = []
        shape = []
        for i, branch in enumerate(crown):
            if isinstance(AtomicSpace, branch):
                continue
            self.crown.append(branch)
            self.keys.append(keys[i])
            shape.append(len(branch))


        self.default_reward = default_reward
        self.reward = default_reward
        self.subtrees = np.empty(shape, dtype=object)

    def best_index(self):
        rewards = self.get_rewards()
        best_val = rewards.max()
        indices = where(self.rewards == best_val)
        chosen_index = choice(zip(*indices))
        return [self.keys(i) for i in chosen_index]

    def get_rewards(self):
        rew = RewardTree._get_rewards(self.subtrees)
        return array(rew)

    def expand(self, index):
        sub = self.subtrees[index]
        if sub is None:
            key = [self.keys[i] for i in index]
            crown = [
                branch[k]
                for k, branch in zip(key, self.crown)
            ]
            bare_crown = [
                branch for branch in new_crown
                if not isinstance(AtomicSpace, branch)
            ]
            sub = RewardTree(bare_crown, self.default_reward)
            self.subtrees[index] = sub
        return sub

    def _get_rewards(self, trees):
        if trees == None:
            rew = self.default_reward
        elif type(trees) == RewardTree:
            rew = trees.reward
        else:
            rew = [self.get_rewards(sub) for sub in trees]
        return rew



def grow(space, tree_indices):
    
    stem = pull_up(space)
    tree_indices = list(tuple(i) for i in tree_indices)
    for t_index in tree_indices:
        n_index, bare = find_bare(stem) # n_index stands for node index
        stem[*n_index] = bare[t_index]

    return stem



        
def find_bare(tree, index=()):
     """
     Iterrates over (index, subspace)-pairs of bare nodes!

     """

    if isinstance(tree, Space):
        if type(tree) is JoinedSpace:
            return tree, index

        if type(tree) is AtomicSpace:
            return

        raise ValueError('%s space not allowed here!' % s)

    if isinstance(tree, Product):

        arg_gen = ((index + (i,), grow(sub)) for i, sub in enumerate(space.domain.args))
        yield from filter(bool, arg_gen)

        kwarg_gen = ((index + (k,), grow(sub)) for k,sub in space.domain.kwargs.items())
        yield from filter(lambda item : item[1], kwarg_gen)


def pull_up(space):
    """
    Converts Product Spaces to Products and Callspaces Calls
    until a joined spaces forms a child.

    """

    if type(space) is JoinedSpace:
        return space

    if isinstance(space, AtomicSpace):
        return space

    elif type(sub) in [ProductSpace, CalledSpace]:
        arg_tree = [grow(sub) for sub in space.domain.args]
        kwarg_tree = {k:sub for k,sub in space.domain.kwargs.items()}

        if type(sub) is ProductSpace:
            subtree = Product(arg_tree, kwarg_tree)
        else:
            subtree = Product(arg_tree, kwarg_tree)

        return subtree

    else:
        raise ValueError("Non-space inside space!: %s" % type(sub))


