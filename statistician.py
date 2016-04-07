import os
import collections
import configparser
import uuid
import json
import numpy


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


class DataSet(dict):
    """Represents multiple Datatables in a Dataset."""

    def __init__(self, name, tables=None, meta=None):
        if tables:
            for table_name, table in tables.items():
                assert isinstance(table, numpy.ndarray)
                self[table_name] = table
        
        if meta is None:
            meta = {}
        
        if 'uuid' not in meta:
            meta['uuid'] = str(uuid.uuid4())

        if name in meta:
            assert name == meta['name']
        else:
            meta['name'] = name

        self.name = name
        self.meta = meta
        self.path = None


    @property
    def uuid(self):
        return uuid.UUID(self.meta['uuid'])

 
    @classmethod
    def load_all(cls, path):
        dataset_list = []
        for dirname in os.listdir(path):
            dataset_path = os.path.join(path, dirname)
            if not os.path.isdir(dataset_path):
                continue
            if dirname.startswith('.'):
                continue
            dataset = cls.load(dataset_path)
            dataset_list.append(dataset)
        return dataset_list


    @classmethod
    def load(cls, path):
        name = os.path.basename(path)

        # load meta file
        meta = None
        meta_path = os.path.join(path, 'meta')
        if os.path.exists(meta_path):
            with open(meta_path) as f:
                meta = json.load(f)

        # load datafiles
        tables = {}
        for filename in os.listdir(path):
            filepath = os.path.join(path, filename)
            
            if os.path.isdir(filepath): continue
            if filename.startswith('.'): continue
            if not filename.endswith('.csv'): continue
            
            tables[filename] = numpy.loadtxt(filepath)
            
        dataset = cls(name, tables, meta)
        dataset.path = path
        return dataset


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
            numpy.savetxt(filepath, table)

        # save metafile
        meta_path = os.path.join(path, 'meta')
        with open(meta_path, 'w') as f:
            json.dump(self.meta, f)

    def __str__(self):
        table_shapes = ['%sx%s'%tab.shape for tab in self.values()]
        content = ' '.join([self.name, 'tables:', *table_shapes])
        return ''.join([type(self).__name__, '(', content, ')'])

    def __repr__(self):
        return str(self)


def load_configuration():

    CONFPATH = os.path.dirname(__file__) # configuration file is stored in source folder
    CONFNAME = 'memory_networks.cfg'

    default_config = {
    'DATA' : {
        'path' : os.path.expanduser('~/data/statistician'),
        }
    }

    fullpath = os.path.join(CONFPATH, CONFNAME)
    conf = configparser.ConfigParser()
    conf.read_dict(default_config)
    if os.path.exists(fullpath):
        conf.read(fullpath)
    else:
        print('No configuration file found. Create new one in:', CONFPATH)
        with open(fullpath, 'w') as f:
            conf.write(f)

    return conf
