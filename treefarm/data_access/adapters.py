from statistician import get_config
import datasets
import openml
from glob import iglob
import logging
import os
import utils
from os.path import split, splitext, join, isdir
import numpy
logger = logging.getLogger(__name__)


c = get_config()

if 'openml_apikey' in c:
    openml.apikey = c.openml_apikey


local_dataset_adapters = {
    'inode/directory' : DirectoryAdapter
}


class LocalSourceAdapter(datasets.SourceAdapter):

    def list_groups(self):

        group_infos = {}

        parts = split(self.path)
        wc_index = _first_wildcard(parts)
        group_base = join(parts)[wc_index:]

        for group_path in iglob(self.path):
            
            # extract path informations
            parts = split(group_path)
            relative_path = join(parts[wc_index:])
            base, ext = splitext(relative_path)

            # get correct adapter and load group information
            mime = utils.get_filetype(group_path)
            try:             
                dsa_cls = local_dataset_adapters[mime]
            except KeyError:
                logger.warn(
                    'Skip %s in %s : unsupported filetype : %s'
                    % (relative_path, group_base, mime))
                continue
            else:
                info_dict = dsa_cls(group_path).get_info()

            # set extra fields in info_dict
            if 'name' not in info_dict:
               info_dict['name'] = base
            if ext:
                info_dict['file_extension'] = ext
            info_dict['mimetype'] = mime
            info_dict['group_path'] = group_path
            
            # add to group_info dict
            group_infos[info_dict['name']] = info_dict

        return group_infos


    def get_group(self, info):

        mime = info['mimetype']
        group_path = info['group_path']

        try:
            ds_adapter_cls = local_dataset_adapters[mime]
        except KeyError:
            raise datasets.UsupportedFiletypeError(mime)

        return Group(info, ds_adapter_cls(info))


def _first_wildcard(parts):
    """Finds index first posix-path part with wildcard"""
    for i, part in enumerate(parts):
        if '*' in part or '?' in part:
            return i
    return len(parts)


class DirectoryAdapter(datasets.DatasetAdapter):
    """Standard class to load dataset from files of a directory."""
    
    file_writer = {
        numpy.ndarray : numpy.save,
        pandas.DataFrame : pandas.DataFrame.to_csv,
        str : utils.write_text,
    }

    file_reader = {
        'text/csv' : pandas.read_csv, 
        'text/tab-separated-values' : pandas.read_table,
        'application/x-numpy-data' : numpy.load,
        'application/x-matlab-data' : scipy.io.loadmat,
        'application/json' : utils.read_json,
        'text/plain' : utils.read_str,
    }

    def list_files(self):
        filenames = iglob(join(self.path, '**'), recursive=True)
        no_metafile = lambda path : not DirectoryAdapter._is_metafile(path)
        files = filter(no_metafile, filenames)
        return list(files)

    def list_folders(self):
        ...

    def get_meta(self):
        meta_dict = {}

        def update(path):

            # recursion for subdirectory, infinite loop for 
            for dir_name in filter(isdir, iglob(path)):
                update(dir_name)

            for fname in :
                ftype = utils.get_filetype(path)
                read = DirectoryAdapter.file_reader[ftype]
                tmp_dict = read(ds_path)
                assert isinstance(tmp_dict, dict)
                meta_dict.update(tmp_dict)

    def get_meta(self):
        filenames = iglob(join(self.path, '**'), recursive=True)
        filenames = filter(DirectoryAdapter._is_metafile, filenames)
        filenames = map(split, fnames)
        filenames = sorted(fnames, key=len)

        meta_dict = 
        for fn_split in filenames:
            fn_split

    
    @staticmethod
    def _load_metafile(path):
        ftype = utils.get_filetype(path)
        read = DirectoryAdapter.file_reader[ftype]
        meta_dict = read(ds_path)
        assert isinstance(meta_dict, dict)
        return meta_dict
        

    @staticmethod
    def _is_metafile(path):
        base, ext = splitext(split(path)[-1])
        if base in c.Dataset.Directory.meta_filenames:
            ftype = utils.get_filetype(path)
            if ftype in c.Dataset.Directory.meta_formats:
                return True
        return False



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