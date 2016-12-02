
from treefarm import *


# %%
k = Categorical({'a','b'})
n = Discrete(N[0:], symbol='N')
r = Continuous(R[0:9], symbol='R')
G = r + n | k
f = join(add, mul)
call = Apply(f, ParameterList([G], {}))
to_dot(call, 'light')


# %% Define Kernel Grammar
K = Categorical({'RBF', 'LIN'}, symbol='Ϟ')
G = join()
G <<= G*K | G+K | G/K | K
to_dot(G)

# %%
G0 = simplify(G)
to_dot(G0)

# %% Alternative definition
K = Categorical({'RBF', 'LIN'}, symbol='Ϟ')
G = join(K)
G <<= G*K | G+K | K
to_dot(G)

# %%
G0 = simplify(G)
to_dot(G0)

# %% Define with distribution over functions
K = Categorical({'RBF', 'LIN'}, symbol='Ϟ')
G = join()
f = join(add, mul) | div | sub
G <<= f(G, K) | K
to_dot(G)

# %%
G0 = simplify(G)
to_dot(G0, 'dark2')


# %%
a = sample(G0)
to_dot(a)

# %%
b = simplify(a)
pprint(b)
