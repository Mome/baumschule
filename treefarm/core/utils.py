def execfile(fname, glob=None, loc=None, compiler=None):
    """
    Execute a Python file.
    Taken from ipython_genutils.py3compat.
    """
    glob = glob if glob else {}
    loc = loc if (loc is not None) else glob
    with open(fname, 'rb') as f:
        compiler = compiler or compile
        exec(compiler(f.read(), fname, 'exec'), glob, loc)
