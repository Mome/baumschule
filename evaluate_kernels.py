import GPy
from kernel_grammar import GrammarTree, GrammarLeaf, TreeRoot
import numpy as np

kernel_dict = {
    'RBF' : lambda : GPy.kern.RBF(input_dim=1, variance=1., lengthscale=1.),
    'EXP' : lambda : GPy.kern.Exponential(1),
    'BIAS': lambda : GPy.kern.Bias(1),
    'LINEAR' : lambda : GPy.kern.Linear(1),
}

operation_dict = {
    'add' : 'add',
    'mul' : 'mul',
    '+' : 'add',
    '*' : 'mul',
}


def perform_operation(K1, op, K2):
    if op == 'add':
        combi = K1 + K2
    elif op == 'mul':
        combi = K1 * K2
    else:
        raise TypeError('No such operation:', op)
    return combi


def build_kernel(node, c=0):
    #print(node, c)
    if isinstance(node, GrammarTree):
        K1 = build_kernel(node.first, c+1)
        K2 = build_kernel(node.second, c+1)
        op = operation_dict[node.operation]
        kernel = perform_operation(K1, op, K2)
    elif isinstance(node, GrammarLeaf):
        name = node.name.upper()
        kernel = kernel_dict[name]()
    else:
        raise Exception('Invalid class:', type(node), node)
    return kernel


def evaluate_model(node, X, Y, targetfunc):
    if isinstance(node, TreeRoot):
        node = node.node

    print('Test:', node)
    kernel = build_kernel(node)
    
    #X = np.matrix(X).T
    #Y = np.matrix(Y).T

    #print('Regression kernel type:', type(kernel))
    m = GPy.models.GPRegression(X,Y,kernel)
    m.optimize()

    n = 20
    val_X = (X.max()-X.min())*np.random.rand(n,1) + X.min()

    real_Y = targetfunc(val_X)
    pred_mean, pred_var = m.predict(val_X)

    error = RMSE(real_Y, pred_mean)
    return error


def RMSE(x, y):
    x = x.ravel()
    y = y.ravel()
    return np.sqrt(sum((x-y)**2)/len(x))



