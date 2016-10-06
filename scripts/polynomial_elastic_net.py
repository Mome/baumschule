import sys 
sys.path.insert(1,"/home/student/m/mmeier/code/statistician/")

from hypara.data_access import Path
from hypara.parameter import N,R,Parameter
from hypara.optimizer import RandomOptimizer
from sklearn.linear_model import ElasticNet
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error as mse


data = (Path() / "automatic_statistician/02-solar.csv").read()
X,y = data['X'], data['y']

def RMSE(x, y):
    x = x.ravel()
    y = y.ravel()
    return np.sqrt(sum((x-y)**2)/len(x))


def ml_algorithm(alpha, l1_ratio, maxorder, bias):

	X_train, X_val, y_train, y_val = train_test_split(X, y)

	# create designmatrix
	design = array([
		X**i for i in
		range(abs(bias-1), maxorder+1)])

	# train, predict and validate
	m = ElasticNet(alpha, l1_ratio)
	m.fit(X_train, y_train)
	y_pred = m.predict(X_train)
	error = mse(y_pred, y_test)

	return error


paraspace = Parameter({
	'alpha' : R,
	'l1_ratio' : R,
	'maxorder' : N[0:],
	'bias' : {0,1},
})

ro = RandomOptimizer(ml_algorithm, paraspace)
ro.optimize(1000)

print('\nAnd the answer is:')
print(ro.get_best())
