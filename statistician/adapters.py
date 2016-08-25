from statistician import get_config
import datasets
import openml
from glob import glob
import logging
import os
import utils
from os.path import split, splitext

logger = logging.getLogger(__name__)


c = get_config()

if 'openml_apikey' in c:
    openml.apikey = c.openml_apikey





class LocalSourceAdapter(datasets.SourceAdapter):
    
    dataset_adapters = 

    def list_datasets(self):

        dataset_info = {}

        for abspath in glob(self.path):
            fname = split(abspath)[-1]
            base, ext = splitext(fname)

            mimetype = utils.get_filetype(abspath)

            if mimetype == 'inode/directory':
                info_dict = DirectoryAdapter(abspath).get_info()

            else:
                logger.debug(
                    'Skip %s in %s : unsupported filetype : %s'
                    % (fname, self.path, mimetype))
                continue

            if 'name' not in info_dict:
               info_dict['name'] = base 

            info_dict['mimetype'] = mimetype
            info_dict['abspath'] = abspath
            info_dict['file_extension'] = ext
            
            dataset_info[info_dict['name']] = info_dict

        return dataset_info



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