from pylab import *
from statistician import *
from data_sampler import *

conf = Configuration()

# --------- create tasks -------- #
func_dists = [
    [
        'linear', linear,
        {
            'a' : uniform(-3 , 3),
            'b' : uniform(-20, 20),
        }
    ],
    [
        'sinus', sinus,
        {
            'phase' : uniform(-pi , pi),
            'ampl'  : lognormal(mu=2),
            'freq'  : normal(2,1,positive=True),
            'b'     : normal()
        }
    ],
    [
        'gabor', gabor,
        {
            'lam'   : normal(mu=1),
            'theta' : uniform(-pi , pi),
            'psi'   : uniform(-pi , pi),
            'phi'   : lognormal(),
            'gamma' : normal(),
            'scale' : lognormal(5)
        }
    ],
]

# create function distributions
functions = [FunctionDistribution(func,args).sample() for name, func, args in func_dists]
names = [name + str(randint(10)) for name, func, args in func_dists]

sample_dist = uniform(-10,10) # sample data distribution (distibution of X values)
residual_dist = normal()      # residual distribution
samplers = [SimpleFunctionSampler(func, sample_dist, residual_dist) for func in functions]

# actually samples the datasets
tables = DataSampler(samplers, 100).sample()
tables = [{'table1':asarray(t)} for t in tables]
print('Shapes:', *[t['table1'].shape for t in tables])
datasets = [DataSet(n,t) for n, t in zip(names, tables)]
for ds in datasets: ds.save(conf.datasets_path)


"""
tasks = [SimpleTask(func,X,Y) for func,(X,Y) in zip(functions, data_sets)]

for group in grouper(tasks,9):
    figure()
    for i,t in enumerate(group):
        subplot(3,3,i+1)
        scatter(t.X, t.Y)
        x = linspace(min(t.X),max(t.X),1001)
        plot(x,t.func(x))"""


# create one dimensional data with gaussian noise for regession
func = lambda x : x**3 - 5*x + 2
X = (2*rand(100)-1)*5
Y = func(X) + randn(len(X))
table = array([X,Y])
dataset = DataSet(
    name='poly1',
    tables={'table1':table})
dataset.save(conf.datasets_path)

func = lambda x : sin(x)
X = (2*rand(100)-1)*5
Y = func(X) + randn(len(X))
table = array([X,Y])
dataset = DataSet(
    name='sin1',
    tables={'table1':table})
dataset.save(conf.datasets_path)
# ----------------------------------------------------- #