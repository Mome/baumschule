from treefarm.core.display_dot import to_dot
from treefarm.core.parameters import *
from treefarm.core.domains import *


k = Categorical({'a','b'})
n = Discrete(N[0:])
r = Continuous(R[0:9])
G = r + n | k
f = join(add, mul)
call = Apply(f, ParameterList(G, {}))

to_dot(call)
