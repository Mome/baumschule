import os
import logging
from glob import iglob
from keyword import iskeyword
from utils import execfile

from .domains import ParameterList
from .parameters import Operation, op

log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel('DEBUG')


def create_config_file(path, overwrite=False):
    """Copies the content of default config to user config."""

    if not overwrite:
        if os.path.exists(path):
            return

    # load default configfile
    with open(path) as cfg_file:
        lines = cfg_file.readlines()

    # comment every non-empty, uncommented line
    for i, line in enumerate(lines):
        if line != '\n' and line[0] != '#':
            lines[i] = '# ' + line

    log.info('Create new Configuration file in:', path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as cfg_file:
        cfg_file.writelines(lines)


class Environment(ParameterList):
    """
    Basically a ParameterList with configuration.
    """
    def __init__(self):
        self.config = Configuration()

    def load(fname):
        logging.info('load:' + fname)
        execfile(fname, glob={'env':env})

    def add(self, arg):
        if type(arg) == Operation:
            self[arg.name] = arg
        else:
            raise NotImplemented()


class Configuration(dict):

    def __getattr__(self, arg):
        return self[arg]

    def __setattr__(self, key, value):
        self[arg] = value

    @classmethod
    def _check_key(cls, key):
        assert type(key) is str
        assert key.isidentifier()
        assert not iskeyword(key)

    def add_group(self, name):
        _check_key(name)
        self[name] = Configuration()

def get_env():
    'topenv' in globals():
        return env
    global env
    set_env()
    return env

def get_config():
    return get_env().config

def add_operator(arg):
    get_env().add(arg)

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), ('default_config.py'))
USER_CONFIG_PATH = os.path.expanduser('~/.config/treefarm.py')

def set_env(path=None):
    global env
    env = Environment()
    env.load(DEFAULT_CONFIG_PATH)
    if path is None:
        path = USER_CONFIG_PATH
    env.load(path)
