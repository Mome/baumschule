import os
import collections
import configparser
import uuid
import json
import numpy
import sys

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
        if not (tables is None):
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
        meta_path = os.path.join(path, 'meta.json')
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
            
            table = numpy.loadtxt(filepath, delimiter='\t')
            table = table.T # transpose table, because table was stored transposed
            tables[filename] = table
            
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
            table = table.T # transpose table file looks nice
            numpy.savetxt(filepath, table, delimiter='\t')

        # save metafile
        meta_path = os.path.join(path, 'meta.json')
        with open(meta_path, 'w') as f:
            json.dump(self.meta, f)

    def __str__(self):
        table_shapes = ['%sx%s'%tab.shape for tab in self.values()]
        content = ' '.join([self.name, 'tables:', *table_shapes])
        return ''.join([type(self).__name__, '(', content, ')'])

    def __repr__(self):
        return str(self)



class Configuration(configparser.ConfigParser):

    CONFPATH = os.path.dirname(__file__) # configuration file is stored in source folder
    CONFNAME = 'statistician.cfg'
    singleton = True

    _DEFAULT_DICT = {
        'data' : {
            'path' : os.path.expanduser('~/data/statistician'),
        }
    }

    def __init__(self, path=None):
        super(Configuration, self).__init__()
        
        # make sure only on instance is created of `Configuration`
        if Configuration.singleton:
            Configuration.singleton = False
        else:
            raise Exception('Configuration already loaded!')
        
        # add default configuration
        self.read_dict(Configuration._DEFAULT_DICT)

        # add configuration form custom file
        if path is None:
            path = os.path.join(Configuration.CONFPATH, Configuration.CONFNAME)
            if os.path.exists(path):
                self.read(path)
        else:
            self.read(path)
        
        self.datasets_path = os.path.join(self['data']['path'], 'datasets')
        self.results_path = os.path.join(self['data']['path'], 'results')
        self.tasks_path = os.path.join(self['data']['path'], 'tasks')
        self.path = path

    def save(self, path=None):
        if path==None:
            path = self.path
        with open(path, 'w') as f:
            self.write(f)

    def load(self, path=None):
        if path==None:
            path = self.path
        self.read(path)

    def __del__(self):
        Configuration.singleton = True

def init_configfile(path=None):
    # maybe remove old configfile here?
    conf = Configuration(path)
    print('Create new Configuration file in:', conf.path)
    conf.save()

def init_folders(conf=None):
    if conf==None:
        conf = Configuration()
    os.makedirs(conf.datasets_path, exist_ok=True)
    os.makedirs(conf.results_path, exist_ok=True)
    os.makedirs(conf.tasks_path, exist_ok=True)

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