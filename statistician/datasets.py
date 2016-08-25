from statistician import get_config
import logging
import openml
from os.path import join
import os
import json
import pandas
import numpy
import scipy

log = logging.getLogger(__name__)
c = get_config()

class Dataset:
    """Represents multiple Datatables in a Dataset."""

    def __init__(self, name, tables=None, meta=None):
        if tables is None:
            tables = {}
        
        if meta is None:
            meta = {}

        if name in meta:
            assert name == meta['name']
        else:
            meta['name'] = name

        self.name = name
        self.tables = tables
        self.meta = meta
        self.path = None

    @classmethod
    def list_all(cls, path=None):

        if path is None:
            path = CONFIG.data_path

        return [
            name for name in os.listdir(path)
            if Dataset.valid_dataset_format(join(path, name))
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
            path = join(CONFIG.data_path, name)

        if os.path.isdir(path):

            # load meta file
            meta_path = join(path, 'meta.json')
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
                filepath = join(path, filename)
                if os.path.isdir(filepath): continue
                table = Dataset.read_table(filepath)
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

    def save(self, path=None, format_=None):

        if format_ is None:
            format_ = c.Dataset.default_format
        
        if path is None:
            if self.path is None:
                path = CONFIG.data_path
                path = join(path, self.name)
            else:
                path = self.path
        
        if format_ == '.csv':
            if not os.path.exists(path):
                os.mkdir(path)

            # save tables
            for table_name, table in self.items():
                filepath = join(path, table_name + '.csv')
                pandas.to_csv(filepath)

            # save metafile
            meta_path = join(path, 'meta.json')
            with open(meta_path, 'w') as f:
                json.dump(self.meta, f)

        elif format_ == '.mat':
            base, ext = os.path.splitext(path)
            data = {'meta' : json.dumps(self.meta), **self.tables}
            sio.savemat(path, data)

    def __getitem__(self, key):
        return self.tables[key]

    def __str__(self):
        #TableInfo = collections.namedtuple('TableInfo', ['name', 'shape', 'columns'])
        table_info = [
            {'name':name, 'shape':table.shape, 'type':type(table).__name__}
            for name, table in self.tables.items()
        ]
        lines = [
            'Dataset: ' + self.name,
            '---------' + '-'*len(self.name),
            '', 'Tables:',
            pprint.pformat(table_info),
        ]
        if self.meta and 'kernel' in self.meta:
            lines += ['','Kernel:', self.meta['kernel']]
        return '\n'.join(lines)


class DatasetInfo:
    """Stores meta-information of a dataset."""

    mendatory = ['name', 'files']

    def __init__(self):
        ...

    @classmethod
    def load(cls, name):
        ...

    def save(self, name=None):
        if name is None:
            name = self.name
        ...

    def get_dataset(self):
        ...


class DatasetIndex(dict):
    """Stores a list of available datasets information."""

    def __init__(self):
        try:
            self.load()
        except FileNotFoundError:
            self.update_index()

    def save(self):
        filepath = join(c.basepath, 'dataset_index.json')
        with open(filepath, 'w') as f:
            json.dump(dict(self), f)

    def load(self):
        filepath = join(c.basepath, 'dataset_index.json')
        with open(filepath) as f:
            dsi_dict = json.load(f)
        self.clear()
        self.update(dsi_dict)

    def as_dataframe(self, source):
        df = pandas.DataFrame(self[source])
        df.set_index('did', inplace=True)
        return df

    def update_index(self, source='all'):
        
        if source == 'all' or source == 'local':
            local_dataindex = self.get('local', {})
            for fname in os.listdir():
                meta_info = Dataset.load_meta(fname)
                local_dataindex[fname] = meta_info
            self['local'] = local_dataindex

        if source == 'all' or source == 'local':
            openml_dataindex = openml.datasets.list_datasets()
            self['openml'] = openml_dataindex

        log.debug('dataset index updating complete')


class SourceAdapter:
    def list_datasets(self):
        raise NotImplementedError()

    def get_dataset(self, source):
        raise NotImplementedError()

class DatasetAdapter: # or call GroupAdapter ???
    def __init__(self, path):
        self.path = path

    def load(self):
        raise NotImplementedError()

    def save(self):
        raise NotImplementedError()

    def load_info(self):
        raise NotImplementedError()

    def save_info(self):
        raise NotImplementedError()


# -------------- Data File IO -------------- #

read_funcs = {
    '.csv' : pandas.read_csv, 
    '.tsv' : pandas.read_table,
    '.npy' : numpy.load,
    '.mat' : scipy.io.loadmat,
    #'.h5'  : lambda path : h5py.File(path).read(),
}

table_write_funcs = {
    ''
}


def read_table(path):

    ext = os.path.splitext(path)[-1]
    read = read_funcs('.csv')

    return table

@staticmethod
def write_table(table, path, format_):
    ...

# -------------------------------------------- #