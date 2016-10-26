from .optimizer import Optimizer

from ..core.spaces import ProductSpace, CallSpace, JoinedSpace, AtomicSpace

def ExhaustiveOptimizer(Optimizer):
	"""Itterates over all instances of """

	def __init__(self):
		...

	@staticmethod
	def iterate(space):
		if isinstance(space, ProductSpace):
			for sub in space.domain.args:
				...
			for sub ...


