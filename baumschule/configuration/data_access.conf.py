import sys, os
sys.path.append(os.path.expanduser('~/code/treefarm'))

c.add_subgroup('datasets')

c.datasets.source_classes = {
}

# for local file access
c.datasets.directory_meta_filenames = ['meta', 'info', '.meta', '.info']
c.datasets.directory_meta_formats = ['application/json']

c.datasets.local_source_basepaths = {
    'local' : os.path.join(c.base_path, 'datasets')
}

c.datasets.local_default_source = 'local'

c.datasets.local_group_classes = {
}

import pandas, numpy, scipy

# maps from a mime type to function
# that reads a file on the local file system
c.datasets.local_read_functions = {
    'text/csv' : pandas.read_csv,
    'text/tab-separated-values' : pandas.read_table,
    'application/x-numpy-data' : numpy.load,
    'application/x-matlab-data' : scipy.io.loadmat,
}


def df_to_csv(path, df):
	import pandas
	pandas.DataFrame.to_csv(df, path)

# maps from a object type to write function
c.datasets.local_write_functions = {
    numpy.ndarray : numpy.save,
    pandas.DataFrame : df_to_csv,
}
