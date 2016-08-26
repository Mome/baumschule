from statistician import get_config
import datasets
import openml
from glob import glob
import logging
import os
import utils
from os.path import split, splitext, join

logger = logging.getLogger(__name__)


c = get_config()

if 'openml_apikey' in c:
    openml.apikey = c.openml_apikey


local_dataset_adapters = {
    'inode/directory' : DirectoryAdapter
}


class LocalSourceAdapter(datasets.SourceAdapter):

    
    def list_datasets(self):

        dataset_info = {}

        for fullpath in glob(self.path):
            parts = split(fullpath)
            i = _first_wildcard(parts)
            rel_path = ...
            base, ext = splitext(fname) # TODO: chage this to first okkurance of a * or ?

            mimetype = utils.get_filetype(fullpath)

            dsa = local_dataset_adapters[mimetype]
            info_dict = DirectoryAdapter(fullpath).get_info()

            else:
                logger.debug(
                    'Skip %s in %s : unsupported filetype : %s'
                    % (fname, self.path, mimetype))
                continue

            if 'name' not in info_dict:
               info_dict['name'] = base

            if ext:
                info_dict['file_extension'] = ext

            info_dict['mimetype'] = mimetype
            info_dict['fullpath'] = fullpath
            
            dataset_info[info_dict['name']] = info_dict

        return dataset_info

    

    def get_data(self, info):
        info['mimetype']


def _first_wildcard(parts)
    """Finds index first posix-path part with wildcard"""
    for i, part in enumerate(parts):
        if '*' in part or '?' in part:
            return i
    return len(parts)



class DirectoryAdapter(datasets.DatasetAdapter):
    """Standard class to load dataset from files of a directory."""
    ....
    

class Hdf5Adapter(datasets.DatasetAdapter):
    """Standard class to load dataset from hdf5 files."""
    ...

class MatAdapter(datasets.DatasetAdapter):
    """Standard class to load dataset from .mat files."""
    ...


class OpenmlSourceAdapter(datasets.SourceAdapter):

    @property
    def name(self):
        return 'openml'
    
    def list_datasets(self):
        return openml.datasets.list_datasets()

    def download(self, id_):
        oml_ds = openml.datasets.get_dataset(id_)
        return oml_ds



database_adapters = [
    OpenMLDatabaseAdapter()
]