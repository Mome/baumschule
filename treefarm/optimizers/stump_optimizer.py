import numpy as np
from random import choice

from ..core.domains import Product
from ..core.spaces import JoinedSpace, ProductSpace, AtomicSpace

class TreeFarm:

    def __init__(self, space, default_reward):
        self.meta_tree = None
        self.reward_tree = RewardTree(space)
        self.space = space

    def grow(self):
        """
        Samples a stem from a search space.
        """
        stem_path = []
        leafy_crown = []
        sub_rtree = self.reward_tree

        index = self.best_index()
        for sub_rtree.expand(index):
            stem_path.append(index)



        stem.sample()




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
