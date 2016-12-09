from itertools import chain
from collections import defaultdict
from functools import partial
import os
from glob import iglob
import logging

from . import utils
from ..core.environment import get_config

log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel('INFO')


class PurePath:

    source_sep = ':'
    sep = '/'
    default_source = None

    def __init__(self, source, parts):
        log.debug('PurePath.init(source=%s, parts=%s)' % (source, parts))

        #source, parts = self.__class__._parse_args(args, source)
        if all(p == '..' for p in parts):
            parts = []

        self._parts = parts
        self._source = source

    @classmethod
    def _parse_args(cls, args, source):
        log.debug('_parse_args(args=%s, source=%s)' % (args, source))

        if (source is None) and (len(args) == 0):
            source = cls.default_source
            parts = ()

        else:
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
        # TODO: can I use glob here???
        parts = (a.strip(cls.sep).split(cls.sep) for a in args)

        # remove single dots
        parts = list(filter(lambda p : p not in ('.', ''), chain(*parts)))

        # process /../ parts
        i = 1
        while i < len(parts):
            if parts[i] == '..' and parts[i-1] != '..':
                del parts[i-1:i+1]
                i = max(i-2, 1)
            else:
                i += 1

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

    def child(self, *relative_parts):
        cls = type(self)
        return cls(*self.parts, *relative_parts, source=self.source)

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

    def __new__(cls, *args, **kwargs):
        log.debug('Path.new(cls=%s, args=%s, kwargs=%s)' % (cls.__name__, args, kwargs))

        if cls is Path:

            source, parts = PurePath._parse_args(
                args = args,
                source=kwargs.get('source', None))

            if not (source in cls.source_classes):
                raise ValueError('Unknown source!')

            # choose source class
            # print('Path.source_classes=%s' % cls.source_classes)
            cls = cls.source_classes[source]

            self = cls.__new__(cls, source, parts)
        else:
            self = object.__new__(cls)

        return self

    def child(self, *relative_parts):
        return Path(*self.parts, *relative_parts, source=self.source)

    def list_sources(self):
        return list(self.source_classes.keys())

    def exists(self):
        raise NotImplementedError()


class Group(Path):
    def __init__(self, source, parts):
        log.debug('Group.init(source=%s, parts=%s)' % (source, parts))

    def list_groups(self):
        raise NotImplementedError()

    def list_files(self):
        raise NotImplementedError()


class File(Path):
    def __init__(self, source, parts):
        log.debug('File.init(source=%s, parts=%s)' % (source, parts))

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

    def __new__(cls, *args, **kwargs):
        log.debug('LocalPath.new(cls=%s, args=%s, kwargs=%s)' % (cls.__name__, args, kwargs))

        if cls is LocalPath:
            source = kwargs['source'] if 'source' in kwargs else args[0]
            parts  = kwargs['parts']  if 'parts'  in kwargs else args[1]

            basepath = cls.source_basepaths[source]
            realpath = cls.sep.join([basepath.rstrip('/'), *parts])
            filetype = utils.get_filetype(realpath)

            cls = cls.get_access_class(filetype)
            #print('This is the chose class now!!', cls)

            self = cls.__new__(cls, parts, source)
        else:
            self = object.__new__(cls) # solve this with super ????

        return self

    def __init__(self, source, parts, basepath=None, filetype=None):
        log.debug('LocalPath.init(self=%s, source=%s, parts=%s'
            % (type(self).__name__, source, parts))

        Path.__init__(self, source, parts)

        if basepath is None:
            basepath = self.__class__.source_basepaths[source]
        self._basepath = basepath

        if filetype is None:
            filetype = utils.get_filetype(self.real_path)
        self._filetype = filetype


    @classmethod
    def get_access_class(cls, filetype):
        if filetype in cls.group_classes:
            return cls.group_classes[filetype]

        if filetype in LocalFile.read_functions:
            return LocalFile

        #print('GroupPathTypes: %s' % cls.group_classes)
        #print('FilePathTypes: %s' % LocalFile.read_functions)
        raise Exception('Unsupported pathtype: %s' % filetype)

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
        #print(self.real_path)
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

    def __init__(self, *args, source=None):
        source, parts = self._parse_args(args, source)
        log.debug('LocalFile.init(source=%s, parts=%s)' % (source, parts))
        LocalPath.__init__(self, source, parts)

        self.reader = self.read_functions.get(self.filetype, None)


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

    def __init__(self, *args, source=None):
        source, parts = self._parse_args(args, source)
        log.debug('LocalDirectory.init(source=%s, parts=%s)' % (source, parts))
        LocalPath.__init__(self, source, parts)

    def list_groups(self):
        return list(filter(os.path.isdir, iglob(self.real_path)))

    def list_files(self):
        print('glob', list(iglob(self.real_path)))
        return list(filter(os.path.isfile, iglob(self.real_path)))

    def list_all(self, meta=False):
        real_paths = (
            path + self.sep if os.path.isdir(path) else path
            for path in iglob(self.real_path + self.sep + '*')
        )
        return [self._cut_basepath(rp) for rp in real_paths]

    def _cut_basepath(self, path):
        base = os.path.commonpath((path, self.basepath))
        return path[len(base)+1:]



Path.source_classes['local'] = LocalPath
LocalPath.group_classes['inode/directory'] = LocalDirectory


def configure_classes(c=None):
    if c is None:
        c = get_config().datasets

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

    if 'local_default_source' in c:
        PurePath.default_source = c.local_default_source

configure_classes()
