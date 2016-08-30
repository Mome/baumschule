from pathlib import PurePosixPath, _Flavour
from itertools import chain
import utils
from collections import defaultdict
from functools import partial

from statistician import get_config


class PurePath:

    source_sep = ':'
    sep = '/'

    def __init__(self, *args, source=None):
        pars, source = self.__class__._parse_args(source, args)
        self._parts = parts
        self._source = source

    @classmethod
    def _parse_args(args, source):
        if (source is None) and (len(args) == 0):
            raise ValueError('Source requiered!')

        args = list(args)
        
        if source is None:
            first_arg = args[0]
            if self.source_sep in first_arg:
                source, rest = first_arg.split(self.source_sep, maxsplit=1)
                args[0] = rest
            else:
                source = first_arg
                args = args[1:]

        if self.sep in source:
            raise ValueError('Separator %s cannot be in source string!' % self.sep)

        parts = self.to_parts(*args)
        return source, parts

    @classmethod
    def to_parts(cls, *args):
        parts = (a.strip(cls.sep).split(cls.sep) for a in args)
        parts = chain(*parts)
        parts = filter(lambda p : p != '.', parts)
        parts = tuple(chain(parts))
        return parts

    @property
    def parent(self):
        cls = self.__class__
        parts = [] if self.parts == [] else self.parts[:-1]
        return cls(*parts, source=self.source)

    @property
    def parts(self):
        return self._parts
   
    @property
    def source(self):
        return self._source

    def child(self, *relative_path):
        parts = self.parts + self.to_parts(*relative_path)
        return self.__class__(*parts, source=self.source)
     
    def __truediv__(self, key):
        if isinstance(key, str):
            key = (key,)
        return self.child(*key)

    def __eq__(self, key):
        return str(self) == str(key)

    def __str__(self):
        return self.source + self.source_sep + self.sep + self.sep.join(self.parts)

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, str(self))



class Path(PurePath):

    sources = {}

    def __new__(cls, *args, source=None):
        if cls is Path:
            ppath = PurePath(args)

            if not (source in cls.sources):
                raise ValueError('Unknown source!')

            cls = cls.sources[source]

        return object.__new__(cls, *parts, source=source)


class Group(LocalPath):
    def __init__(self):
        print(self)

    def list_groups(self):
        raise NotImplementedError()

    def list_files(self):
        raise NotImplementedError()


class File(Path):
    
    def load(self):
        raise NotImplementedError()

    def meta(self):
        raise NotImplementedError()

    def save(self, obj):
        raise NotImplementedError()


class LocalPath(Path):

    group_classes = {
        'inode/direcotry' : LocalDirectory,
    }

    def __new__(cls, base_path):

        filetype = utils.get_filetype(base_path)

        if cls is LocalPath:
            cls = get_access_class(filetype)

        self = object.__new__(cls, base_path)
        return self        

    @classmethod
    def get_access_class(cls, filetype):
        if filetype in cls.group_classes:
            return cls.group_classes[filetype]

        if filetype in LocalFile.file_classes:
            return partial(LocalFile, filetype=filetype)

        raise Exception('Unsupported pathtype:%s' % filetype)


class LocalFile(LocalPath, File):

    file_readers = {
        'application/json' : utils.read_json,
        'text/plain' : utils.read_str,
    }

    file_writers = {
        str : utils.write_text,
        dict : utils.wirte_json,
        list : utils.wirte_json,
    }

    def __init__(self, base_path, filetype=None):
        if filetype is None:
            filetype = utils.get_filetype(base_path)
        self.base_path = base_path
        self.filetype = filetype

    def load(self):
        ...

    def save(self, obj):
        ...


class LocalDirectory(LocalPath, Group):
    pass


def configure_clases(c=None):
    if c is None:
        c = get_config().Dataset

    if 'sources' in c:
        Path.sources.update(c.sources)

    if 'local_group_classes' in c:
        LocalPath.group_classes.update(c.local_group_classes)

    if 'local_file_readers' in c:
        File.file_readers.update(c.local_file_readers)

    if 'local_file_writers' in c:
        File.file_readers.update(c.local_file_writers)

        
