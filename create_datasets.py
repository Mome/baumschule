from pylab import *
from pandas import *
from statistician import *

conf = load_configuration()

# create one dimensional data with gaussian noise for regession

func = lambda x : x**3 - 5*x + 2
X = (2*rand(100)-1)*5
Y = func(X) + randn(len(X))
table = array([X,Y])
dataset = DataSet(
	name='poly1',
	tables={'table1':table})
dataset.save(conf['DATA']['path'])

func = lambda x : sin(x)
X = (2*rand(100)-1)*5
Y = func(X) + randn(len(X))
table = array([X,Y])
dataset = DataSet(
	name='sin1',
	tables={'table1':table})
dataset.save(conf['DATA']['path'])

# ----------------------------------------------------- #