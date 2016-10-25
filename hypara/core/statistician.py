import collections
import configparser
import json
import os
import pprint
import sys
import uuid


import logging

log = logging.getLogger(__name__)


class System:
    def __init__(self):
        ...

class Configuration(dict):
    """
    Calss to store configurations.
    Basically a wrapper for a dict with some extra properties.
    One instance is unique each system instance.
    """

    # paths of the config files, loaded in this order
    _CONFIGFILES = (
        os.path.join(os.path.dirname(__file__), 'default_config.py'),
        os.path.expanduser('~/.config/hypa_config.py'), # user configuration
    )

    def __init__(self, config_files=()):
        config_files = Configuration._CONFIGFILES + config_files


    def _reload(self, path)

    def _load(self, path):
        pass

    def __get_attr__(self, key):
        _check_key_is_valid(key)
        return super().__get_attr__(key)

    def __get_item__(self, key):
        _check_key_is_valid(key)
        return super().__get_item__(key)

    def __set_attr__(self, key):
        _check_key_is_valid(key)
        return super().__set_attr__(key)

    def __set_item__(self, key):
        _check_key_is_valid(key)
        return super().__set_item__(key)

    @staticmethod
    def _check_key_is_valid(key):
        if (type(key) != str or
            not key.isidentifier() or
            key[0] == '_'):
            raise ValueError('Key must be Python identifier \
                and must not start with an underscore.')
            

class Configuration2: # maybe make a dict?

    # paths of the config files, loaded in this order
    CONFIGFILES = [
        ('default', os.path.join(os.path.dirname(__file__), 'default_config.py')),
        ('user', os.path.expanduser('~/.config/statistician_config.py')),
    ]

    _INSTANCE = None

    _SUBCV = ['Dataset'] # Subconfigurations variabels

    def _add_subc(self, subc_list):
        subcv = {key:Configuration() for key in subc_list}
        subcv.update(self.__dict__)
        self.__dict__ = subcv

    @classmethod
    def _create_instance(cls):
        # namespace definition for exec of CONFIGFILES
        from os.path import join, expanduser
        c = cls() # configuration object
        c._add_subc(cls._SUBCV)

        for name, path in cls.CONFIGFILES:
            log.debug('load', name, 'configuration')
            try:
                with open(path) as cfg_file:
                    cfg_code = cfg_file.read()
            except FileNotFoundError as e:
                log.warning(e)
            else:
                exec(cfg_code)

        cls._INSTANCE = c

    def __contains__(self, element):
        return element in self.__dict__

    @classmethod
    def get_config(cls, reload_=False):
        """ Loads configuration files from Configuration.CONFIGFILES

            Returns: Configuration instance
        """

        if not cls._INSTANCE or reload_:
            cls._create_instance()

        return cls._INSTANCE
    

    @classmethod
    def create_config_file(cls):
        names = list(zip(*CONFIGFILES))
        default_cfg_path = names.find('default')
        user_cfg_path = names.find('user')

        # load default configfile
        with open(default_cfg_path) as default_cfg_file:
            lines = default_cfg_file.readlines()

        # comment every non-empty, uncommented line
        for i, line in enumerate(lines):
            if line and line[0] != '#':
                lines[i] = '#' + line

        log.info('Create new Configuration file in:', user_cfg_pathh)
        os.makedir(os.path.dirname(user_cfg_path), exist_ok=True)
        with open(user_cfg_path, 'w') as user_cfg_file:
            user_cfg_file.writelines(lines)

get_config = Configuration.get_config


def init_folders():
    c = get_config()
    os.makedirs(c.basepath, exist_ok=True)
    os.makedirs(c.Dataset.path[0], exist_ok=True)

def main():
    args = sys.argv[1:]
    if len(args)==1:
        if args[0] == 'init':
            init_configfile()
            init_folders()
    if len(args)==2:
        if args[0] == 'init':
            if args[1] == 'configfile':
                Configuration.create_config_file()
            if args[1] == 'folders':
                init_folders()
            else:
                print('Invalid argument for init!')
    else:
        print('invalid number of arguments!')


if __name__=='__main__':
    main()