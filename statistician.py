import collections
import configparser
import json
import os
import pprint
import sys
import uuid

import pandas
import numpy
import scipy.io as sio


class Statistician:
    def __init__(self):
        self.tasks = []
        self.statistics = []
        self.prediction_algorithms = []


class Task:
    def __init__(self, dataset_path, validation_function):
        self.statistic_dict = {}
        self.dataset = DataSet(dataset_path)
        self.target_function = None
        self.task_description = None


class Statistic(collections.abc.Callable):
    def __init__(self, name, func):
        self.name = name
        self.func = func

    def __call__(self, *args, **keyargs):
        return self.func(*args, **keyargs)


class PredictionAlgorithm(Statistic):
    def __init__(self, name, func):
        super(PredictionAlgorithm, self).__init__(name, func)


class DataSet:
    """Represents multiple Datatables in a Dataset."""

    def __init__(self, name, tables=None, meta=None):
        if tables is None:
            tables = {}
        
        if meta is None:
            meta = {}
        
        if 'uuid' not in meta:
            meta['uuid'] = str(uuid.uuid4())

        if name in meta:
            assert name == meta['name']
        else:
            meta['name'] = name

        self.name = name
        self.tables = tables
        self.meta = meta
        self.path = None


    @property
    def uuid(self):
        return uuid.UUID(self.meta['uuid'])

    @classmethod
    def list_all(cls, path=None):

        if path is None:
            path = CONFIG.data_path

        return [
            name for name in os.listdir(path)
            if DataSet.valid_dataset_format(os.path.join(path, name))
            and not name.startswith('.')
        ]

    @staticmethod
    def valid_dataset_format(path):
        """Test whether a path is a folder or in mat format."""

        if not os.path.exists(path):
            return FileNotFoundError('No dataset in: ' + path)

        if os.path.isdir(path):
            return True
        
        ext = os.path.splitext(path)[-1]
        return ext in ['.mat']

    @classmethod
    def load(cls, name, path=None):

        if path is None:
            path = os.path.join(CONFIG.data_path, name)

        if os.path.isdir(path):

            # load meta file
            meta_path = os.path.join(path, 'meta.json')
            if os.path.exists(meta_path):
                with open(meta_path) as f:
                    meta = json.load(f)
            else:
                meta = None

            # load datafiles
            tables = {}
            for filename in os.listdir(path):
                if filename.startswith('.'): continue
                if filename.endswith('~'): continue
                filepath = os.path.join(path, filename)
                if os.path.isdir(filepath): continue
                table = DataSet.read_table(filepath)
                tablename = os.path.splitext(filename)[0]
                tables[tablename] = table

        elif path.endswith('.mat'):

            mat = sio.loadmat(path)
            meta = mat['meta'] if 'meta' in mat else None
            tables = {key:mat[key] for key in mat
                if not (key.startswith('__') or key == 'meta')}
            
        dataset = cls(name, tables, meta)
        dataset.path = path
        return dataset

    @staticmethod
    def read_table(path):
        ext = os.path.splitext(path)[-1]
        if ext == '.csv':
            table = pandas.read_csv(path)
        elif ext == '.tsv':
            table = pandas.read_table(path)
        elif ext == '.npy':
            table = np.load(path)
        else:
            raise IOError('Invalid table format: ' + ext)
        return table

    def __getitem__(self, key):
        return self.tables[key]

    def __str__(self):
        #TableInfo = collections.namedtuple('TableInfo', ['name', 'shape', 'columns'])
        table_info = [
            {'name':name, 'shape':table.shape, 'type':type(table)}
            for name, table in self.tables.items()
        ]
        lines = [
            'DataSet: ' + self.name,
            '---------' + '-'*len(self.name),
            pprint.pformat(table_info),
            '', 'Meta:',
            pprint.pformat(self.meta),
        ]
        return '\n'.join(lines)
        
    def save(self, path=None):
        
        if path is None:
            if not (self.path is None):
                path = self.path
            else:
                raise Exception('Need path for dataset!')

        path = os.path.join(path, self.name)
        if not os.path.exists(path):
            os.mkdir(path)

        # save tables
        for table_name, table in self.items():
            filepath = os.path.join(path, table_name + '.csv')
            pandas.to_csv(filepath)

        # save metafile
        meta_path = os.path.join(path, 'meta.json')
        with open(meta_path, 'w') as f:
            json.dump(self.meta, f)

    #def __str__(self):
    #    table_shapes = ['%sx%s'%tab.shape for tab in self.values()]
    #    content = ' '.join([self.name, 'tables:', *table_shapes])
    #   return ''.join([type(self).__name__, '(', content, ')'])

    def __repr__(self):
        return str(self)



class Configuration(configparser.ConfigParser):

    CONFPATH = os.path.dirname(__file__) # configuration file is stored in source folder
    CONFNAME = 'statistician.cfg'

    _DEFAULT_DICT = {
        'data' : {
            'path' : os.path.expanduser('~/data/statistician'),
        }
    }

    def __init__(self, path=None):
        super(Configuration, self).__init__()

        # add default configuration
        self.read_dict(Configuration._DEFAULT_DICT)

        # add configuration form custom file
        if path is None:
            path = os.path.join(Configuration.CONFPATH, Configuration.CONFNAME)

        self.read(path)
        
        self.data_path = os.path.join(self['data']['path'], 'data')
        self.result_path = os.path.join(self['data']['path'], 'results')
        self.task_path = os.path.join(self['data']['path'], 'tasks')
        self.path = path

    def save(self, path=None):
        if path==None:
            path = self.path
        with open(path, 'w') as f:
            self.write(f)


def init_configfile(path=None):
    # maybe remove old configfile here?
    conf = Configuration(path)
    print('Create new Configuration file in:', conf.path)
    conf.save()


def init_folders(conf=None):
    if conf==None:
        conf = Configuration()
    os.makedirs(conf.data_path, exist_ok=True)
    os.makedirs(conf.result_path, exist_ok=True)
    os.makedirs(conf.task_path, exist_ok=True)


CONFIG = Configuration()

def main():
    args = sys.argv[1:]
    if len(args)==1:
        if args[0] == 'init':
            init_configfile()
            init_folders()
    if len(args)==2:
        if args[0] == 'init':
            if args[1] == 'configfile':
                init_configfile()
            if args[1] == 'folders':
                init_folders()
            else:
                print('Invalid argument for init!')
    else:
        print('invalid number of arguments!')


if __name__=='__main__':
    main()