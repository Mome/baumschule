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
import matplotlib.pyplot as plt

import logging

log = logging.getLogger(__name__)


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
            
            tables = {key:mat[key] for key in mat
                if not (key.startswith('__') or key == 'meta')}
            
            if 'meta' in mat:
                meta_json = mat['meta'][0]
                meta = json.loads(meta_json)
            else:
                meta = None
        else:
            raise Exception('Invalid format ...')

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
            {'name':name, 'shape':table.shape, 'type':type(table).__name__}
            for name, table in self.tables.items()
        ]
        lines = [
            'DataSet: ' + self.name,
            '---------' + '-'*len(self.name),
            '', 'Tables:',
            pprint.pformat(table_info),
        ]
        if self.meta and 'kernel' in self.meta:
            lines += ['','Kernel:', self.meta['kernel']]
        return '\n'.join(lines)
        
    def save(self, path=None, format_='.mat'):
        
        if path is None:
            if self.path is None:
                path = CONFIG.data_path
                path = os.path.join(path, self.name)
            else:
                path = self.path
        
        if format_ == '.csv':
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

        elif format_ == '.mat':
            base, ext = os.path.splitext(path)
            data = {'meta' : json.dumps(self.meta), **self.tables}
            sio.savemat(path, data)


    #def __str__(self):
    #    table_shapes = ['%sx%s'%tab.shape for tab in self.values()]
    #    content = ' '.join([self.name, 'tables:', *table_shapes])
    #   return ''.join([type(self).__name__, '(', content, ')'])

    def __repr__(self):
        return str(self)



class Configuration_alt(configparser.ConfigParser):

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


class Configuration:

    # paths of the config files, loaded in this order
    CONFIGFILES = [
        ('default', os.path.join(os.path.dirname(__file__), 'default_config.py')),
        ('user', os.path.expanduser('~/.statistician/statistician_config.py')),
    ]

    _INSTANCE = None

    _SUBCV = ['Dataset'] # Subconfigurations variabels

    def _add_subc(self, subc_list):
        subcv = {key:Configuration() for key in subc_list}
        subcv.update(self.__dict__)
        self.__dict__ = subcv


    @classmethod
    def load_config(cls, reload_=False):
        """ Loads configuration files from Configuration.CONFIGFILES

            Returns: Configuration instance
        """

        if not cls._INSTANCE or reload_:

            # namespace definition for exec of CONFIGFILES
            from os.path import join, expanduser
            c = cls() # configuration object
            c._add_subc(cls._SUBCV)

            for name, path in cls.CONFIGFILES:
                log.debug('load', name, 'configuration')
                try:
                    with open(path) as cfg_file:
                        cfg_code = cfg_file.read()
                except FileNotFoundError as e:
                    log.warning(e)
                else:
                    exec(cfg_code)

            cls._INSTANCE = c

        return cls._INSTANCE
    

    @classmethod
    def create_config_file(cls):
        names = list(zip(*CONFIGFILES))
        default_cfg_path = names.find('default')
        user_cfg_path = names.find('user')

        # load default configfile
        with open(default_cfg_path) as default_cfg_file:
            lines = default_cfg_file.readlines()

        # comment every non-empty, uncommented line
        for i, line in enumerate(lines):
            if line and line[0] != '#':
                lines[i] = '#' + line

        log.info('Create new Configuration file in:', user_cfg_pathh)
        os.makedir(os.path.dirname(user_cfg_path), exist_ok=True)
        with open(user_cfg_path, 'w') as user_cfg_file:
            user_cfg_file.writelines(lines)


def init_folders(conf=None):
    if conf==None:
        conf = Configuration()
    os.makedirs(conf.data_path, exist_ok=True)
    os.makedirs(conf.result_path, exist_ok=True)
    os.makedirs(conf.task_path, exist_ok=True)


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