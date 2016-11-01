import os
import logging
from glob import iglob
from itertools import chain

import traitlets.config

log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel('DEBUG')


class System:

    DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), ('default_config.py'))
    USER_CONFIG_PATH = os.path.expanduser('~/.config/treefarm.py')

    INSTANCE = None

    def __new__(cls, *args, **kwargs):
        if System.INSTANCE:
            return System.INSTANCE
        return super().__new__(System, *args, **kwargs)

    def __init__(self, config_files=()):
        if System.INSTANCE:
            return
        System.INSTANCE = self

        self.config_files = (System.DEFAULT_CONFIG_PATH, System.USER_CONFIG_PATH) + config_files
        self.config = traitlets.config.Config()
        self.load_config_files(self.config_files)


    def load_config_files(self, config_paths):
        """
        Load multiple config files, merging each of them in turn.

        Parameters
        ==========
        config_paths : sequence of str
            List of config files names to load and merge into the config.
        path : unicode
            The full path to the location of the config files.
            If path is None, config_files are interpreted as absolute paths.
        """
        for cf in chain(*map(iglob, config_paths)):
            if not cf.endswith('.py'):
                log.debug('Skip loading non python configfile %s.' % cf)
                continue
            path, cf = os.path.split(cf)
            loader = traitlets.config.PyFileConfigLoader(cf, path=path)
            try:
                next_config = loader.load_config()
            except traitlets.config.ConfigFileNotFound as e:
                log.warn(str(e))
            except:
                raise
            else:
                log.debug('Merge config: %s' % cf)
                self.config.merge(next_config)


    @classmethod
    def create_config_file(cls, overwrite=False):
        """Copies the content of default config to user config."""

        if not overwrite:
            if os.path.exists(cls.USER_CONFIG_PATH):
                raise Exception('User config file exists!')

        # load default configfile
        with open(cls.DEFAULT_CONFIG_PATH) as cfg_file:
            lines = cfg_file.readlines()

        # comment every non-empty, uncommented line
        for i, line in enumerate(lines):
            if line != '\n' and line[0] != '#':
                lines[i] = '# ' + line

        log.info('Create new Configuration file in:', cls.USER_CONFIG_PATH)
        os.makedirs(os.path.dirname(cls.USER_CONFIG_PATH), exist_ok=True)
        with open(cls.USER_CONFIG_PATH, 'w') as cfg_file:
            cfg_file.writelines(lines)

def get_config():
    return System().config
