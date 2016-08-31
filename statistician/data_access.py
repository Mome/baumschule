from pathlib import PurePosixPath, _Flavour
from itertools import chain
import utils
from collections import defaultdict
from functools import partial
import os
from statistician import get_config


class PurePath:

    source_sep = ':'
    sep = '/'

    def __init__(self, *args, source=None):
        source, parts = self.__class__._parse_args(args, source)
        self._parts = parts
        self._source = source

    @classmethod
    def _parse_args(cls, args, source):
        print('_parse_args(args=%s, source=%s)' % (args, source))
        if (source is None) and (len(args) == 0):
            raise ValueError('Source requiered!')

        args = list(args)
        
        if source is None:
            first_arg = args[0]
            if cls.source_sep in first_arg:
                source, rest = first_arg.split(cls.source_sep, maxsplit=1)
                args[0] = rest
            else:
                source = first_arg
                args = args[1:]

        if cls.sep in source:
            raise ValueError('Separator %s cannot be in source string!' % cls.sep)

        parts = cls._to_parts(args)
        return source, parts

    @classmethod
    def _to_parts(cls, args):
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

    @property
    def relative_path(self):
        return self.sep + self.__class__.sep.join(self.parts)


    def child(self, *relative_path):
        parts = self.parts + self._to_parts(relative_path)
        return self.__class__(*parts, source=self.source)


    def __truediv__(self, key):
        if isinstance(key, str):
            key = (key,)
        return self.child(*key)

    def __eq__(self, key):
        return str(self) == str(key)

    def __str__(self):
        return self.source + self.source_sep + self.relative_path

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, str(self))



class Path(PurePath):

    source_classes = {}

    def __new__(cls, *args, source=None):
        print('first thing')
        if cls is Path:
            purepath = PurePath(*args, source=source)

            if not (purepath.source in cls.source_classes):
                raise ValueError('Unknown source!')

            cls = cls.source_classes[purepath.source]
            print('Regular call in Path: %s' % cls.__name__)
            self = cls(purepath)
        else:
            self = object.__new__(cls)

        return self

    def __init__(self, *args, **keyargs):
        print('boing!!', type(self), args, keyargs)

    def exists(self):
        raise NotImplementedError()


class Group(Path):

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
    }

    source_basepaths = {
    }

    def __new__(cls, purepath, *args, **keyargs):
        print('Call __new__ in LocalPath: %s' % cls.__name__)

        if cls is LocalPath:
            basepath = cls.source_basepaths[purepath.source]
            filetype = utils.get_filetype(basepath)
            cls = cls.get_access_class(filetype)
            
            print('Regular call of: %s' % cls.__name__)
            self = object.__new__(cls)
            self._init(purepath, basepath, filetype)
        else:
            self = object.__new__(cls)
            print('!skipp')
            

        return self

    def _init(self, purepath, basepath=None, filetype=None):

        print('%s : LocalPath._init(self=%s, purepath=%s, filetype=%s'
            % (id(self), type(self).__name__, purepath, filetype))

        if basepath is None:
            basepath = self.__class__.source_basepaths[purepath.source]
        if filetype is None:
            filetype = utils.get_filetype(basepath)

        self._basepath = basepath
        self._filetype = filetype
        self._source = purepath.source
        self._parts = purepath.parts


    @classmethod
    def get_access_class(cls, filetype):
        if filetype in cls.group_classes:
            return cls.group_classes[filetype]

        if filetype in LocalFile.read_functions:
            return LocalFile

        print('GroupPathTypes: %s' % cls.group_classes)
        print('FilePathTypes: %s' % LocalFile.read_functions)
        raise Exception('Unsupported pathtype:%s' % filetype)

    @property
    def filetype(self):
        return self._filetype

    @property
    def basepath(self):
        return self._basepath

    @property
    def real_path(self):
        return self.basepath.rstrip('/') + self.relative_path

    def exists(self):
        return os.path.exists(self.real_path)


class LocalFile(LocalPath, File):

    read_functions = {
        'application/json' : utils.read_json,
        'text/plain' : utils.read_text,
    }

    write_functions = {
        str : utils.write_text,
        dict : utils.write_json,
        list : utils.write_json,
    }

    def _init(self, purepath, basepath=None, filetype=None):

        print('%s : LocalFile.__init__(self=%s, purepath=%s, filetype=%s'
            % (id(self), type(self).__name__, purepath, filetype))

        LocalPath._init(self, purepath, basepath, filetype)
        self.reader = read_functions.get(self.filetype, None)
    
    def read(self):
        if self.reader == None:
            raise TypeError('No reader function for %s.' % self.filetype)
        return self.reader(self.real_path)

    def write(self, obj):
        if type(obj) in self.write_functions:
            write = self.write_functions[type(obj)]
        else:
            # find valid writers
            valid_writers = tuple(
                filter(
                    partial(isinstance, obj),
                    write_functions.keys(),
                ))

            if len(valid_writers) == 0:
                raise ValueError('No writer for object type:%s' % type(obj))
            elif len(valid_writers) == 1:
                write = self.write_functions[valid_writers[0]]
            else:
                raise ValueError('Ambigous write functions for type %s: %s' % type(obj), valid_writers)

        return write(self.real_path, obj)


 
class LocalDirectory(LocalPath, Group):

    def _init(self, purepath, basepath=None, filetype=None):

        print('%s : LocalDirectory._init(self=%s, purepath=%s, filetype=%s'
            % (id(self), type(self).__name__, purepath, filetype))

        LocalPath._init(self, purepath, basepath, filetype)

    def list_groups(self):
        return list(filter(os.path.isdir, iglob(self.real_path)))

    def list_files(self):
        return list(filter(os.path.isfile, iglob(self.real_path)))

    def list_all(self, meta=False):
        return [
            f + self.__calss__.sep if os.path.isdir(path) else path
            for path in iglob(self.real_path)
        ]


Path.source_classes['local'] = LocalPath
LocalPath.group_classes['inode/directory'] = LocalDirectory


def configure_classes(c=None):
    if c is None:
        c = get_config().Dataset

    if 'source_classes' in c:
        Path.source_classes.update(c.source_classes)

    if 'local_group_classes' in c:
        LocalPath.group_classes.update(c.local_group_classes)

    if 'local_source_basepaths' in c:
        LocalPath.source_basepaths.update(c.local_source_basepaths)

    if 'local_read_functions' in c:
        LocalFile.read_functions.update(c.local_read_functions)

    if 'local_write_functions' in c:
        LocalFile.write_functions.update(c.local_write_functions)

configure_classes()
