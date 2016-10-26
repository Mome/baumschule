
import sys, os
sys.path.append(os.path.expanduser('~/code/statistician'))

import hypara
c = hypa.get_config()

c.basepath = expanduser('~/data/hypa')


c.Dataset.source_classes = {
}

# for local file access
c.Dataset.directory_meta_filenames = ['meta', 'info', '.meta', '.info']
c.Dataset.directory_meta_formats = ['application/json']

c.Dataset.local_source_basepaths = {
    'local' : join(c.basepath, 'datasets')
}

c.Dataset.local_default_source = 'local'

c.Dataset.local_group_classes = {
}

import pandas, numpy, scipy

# maps from a mime type to function
# that reads a file on the local file system
c.Dataset.local_read_functions = {
    'text/csv' : pandas.read_csv, 
    'text/tab-separated-values' : pandas.read_table,
    'application/x-numpy-data' : numpy.load,
    'application/x-matlab-data' : scipy.io.loadmat,
}


def df_to_csv(path, df):
	import pandas
	pandas.DataFrame.to_csv(df, path)

# maps from a object type to write function
c.Dataset.local_write_functions = {
    numpy.ndarray : numpy.save,
    pandas.DataFrame : df_to_csv, 
}

