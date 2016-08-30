from pathlib import PurePosixPath, _Flavour
from statistician import get_config
from itertools import chain


c = get_config()

class Path(PurePath):

    def __new__(cls, *args, source=None):
        if cls is Path:
            ppath = PurePath(args)

            if source not in c.Dataset.sources:
                raise ValueError('Unknown source!')

            cls = c.Dataset.sources[source]

        return object.__new__(cls, *parts, source=source)
        

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

