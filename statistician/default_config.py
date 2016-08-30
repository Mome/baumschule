
c.basepath = expanduser('~/data/statistician')

# list of paths to look for datasets, first one is used to store downloaded data
c.Dataset.path = join(c.basepath, 'datasets')
c.Dataset.group_formats = ['inode/directory']
c.Dataset.directory_meta_filenames = ['meta', 'info', '.meta', '.info']
c.Dataset.directory_meta_formats = ['application/json']

c.Dataset.sources = {
}

c.Dataset.local_group_classes = {
}

import pandas, numpy, scipy

c.Dataset.local_file_readers = {
    'text/csv' : pandas.read_csv, 
    'text/tab-separated-values' : pandas.read_table,
    'application/x-numpy-data' : numpy.load,
    'application/x-matlab-data' : scipy.io.loadmat,
}

c.Dataset.local_file_writers = {
    numpy.ndarray : numpy.save,
    pandas.DataFrame : pandas.DataFrame.to_csv,
}