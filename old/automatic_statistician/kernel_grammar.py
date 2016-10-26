def kernel_replacements(tree, kernels):
	if type(left.tree) == str:
		for kern in kernels:
			if kern == left.tree: continue
			new_tree = copy(tree)
			new_tree.left = kern
			return new_tree
	if type(tree.right == str):
		pass



class GrammarTree:

    def __init__(self, left=None, operator=None, right=None):
        self.left = left
        self.operator = operator
        self.right = right

    def __str__(self):
        content = [str(self.first), self.operation, str(self.second)]
        return '(' + ' '.join(content) + ')'

    def __iter__(self):
    	"""Iterates over all non-leaf subtree-nodes."""
    	yield self
    	if not isinstance(self.left, str):
    		yield from self.left
    	if not isinstance(self.right, str):
    		yield from self.right