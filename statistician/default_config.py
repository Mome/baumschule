c.basepath = expanduser('~/data/statistician')

# list of paths to look for datasets, first one is used to store downloaded data
c.Dataset.path = join(c.basepath, 'datasets')
c.Dataset.default_format = 'mat'