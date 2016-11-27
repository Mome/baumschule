from os import makedirs
from os.path import join, dirname, expanduser, exists, normpath
import logging
from glob import iglob
from itertools import chain
from keyword import iskeyword

from .utils import execfile

log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel('DEBUG')

DEFAULT_CONFIG_FOLDER = join(dirname(__file__), '..', 'configuration/*')
USER_CONFIG_FOLDER = expanduser('~/.config/treefarm.conf.py')
USER_CONFIG_FILE = expanduser('~/.config/treefarm/*')


# ---------- classes ---------- #

class Environment(dict):

    VARNAME = 'env'

    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = name

    def __getattr__(self, arg):
        return self[arg]

    def __setattr__(self, key, value):
        self._check_key(key)
        if key.startswith('_'):
            super().__setattr__(key, value)
        else:
            self[key] = value

    @classmethod
    def _check_key(cls, key):
        assert type(key) is str
        #assert not key.startswith('_')
        assert key.isidentifier()
        assert not iskeyword(key)
        assert key not in dir(cls)

    def add_subgroup(self, name):
        self._check_key(name)
        if not name in self:
            self[name] = Configuration()

    def add_ops(self, *ops):
        for op in ops:
            assert 'name' in vars(op)
            self[op.name] = op

    def load_path(self, *paths):
        f = lambda p : iglob(normpath(expanduser(p)))
        for filename in sorted(chain(*map(f, paths))):
            glob = {
                self.VARNAME : self,
                '__file__' : filename,
            }
            execfile(filename,  glob)


class Configuration(Environment):

    VARNAME = 'c'

    def __init__(self):
        super().__init__('configuration')


# ---------- initializers ---------- #

def init_config_file(path=USER_CONFIG_FILE, overwrite=False):
    """Copies the content of default config to user config."""

    if exists(path) and not overwrite:
        raise FileExistsError()

    # load default configfile
    with open(path) as cfg_file:
        lines = cfg_file.readlines()

    # comment every non-empty, uncommented line
    for i, line in enumerate(lines):
        if line != '\n' and line[0] != '#':
            lines[i] = '# ' + line

    log.info('Create new Configuration file in:', path)
    os.makedirs(dirname(path), exist_ok=True)
    with open(path, 'w') as cfg_file:
        cfg_file.writelines(lines)


def init_config():
    global config
    config = Configuration()
    config.load_path(DEFAULT_CONFIG_FOLDER)
    if exists(USER_CONFIG_FILE):
        config.load_path(USER_CONFIG_FILE)
    if exists(USER_CONFIG_FOLDER):
        config.load_path(USER_CONFIG_FOLDER)


def init_env():
    global env
    env = Environment('default')
    paths = config.environment.paths
    if type(paths) is str:
        env.load_path(paths)
    else:
        env.load_path(*paths)


# ---------- getters ---------- #

def get_config():
    return config

def get_env():
    return env
