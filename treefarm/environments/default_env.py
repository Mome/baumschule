from treefarm.operations import math
from treefarm.operations import containers

env.add_ops(*containers.__all__)
env.add_ops(*math.__all__)
