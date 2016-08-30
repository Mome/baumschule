c.basepath = expanduser('~/data/statistician')

# list of paths to look for datasets, first one is used to store downloaded data
c.Dataset.path = join(c.basepath, 'datasets')
c.Dataset.group_formats = ['inode/directory']
c.Dataset.directory_meta_filenames = ['meta', 'info', '.meta', '.info']
c.Dataset.directory_meta_formats = ['application/json']

c.Dataset.sources = {
    'local' : c.basepath + 'data',
}

