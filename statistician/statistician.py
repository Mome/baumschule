import collections
import configparser
import json
import os
import pprint
import sys
import uuid


import logging

log = logging.getLogger(__name__)


class Statistician:
    def __init__(self):
        self.tasks = []
        self.statistics = []
        self.prediction_algorithms = []


class Task:
    def __init__(self, dataset_path, validation_function):
        self.statistic_dict = {}
        self.dataset = DataSet(dataset_path)
        self.target_function = None
        self.task_description = None


class Statistic(collections.abc.Callable):
    def __init__(self, name, func):
        self.name = name
        self.func = func

    def __call__(self, *args, **keyargs):
        return self.func(*args, **keyargs)


class PredictionAlgorithm(Statistic):
    def __init__(self, name, func):
        super(PredictionAlgorithm, self).__init__(name, func)


class Configuration: # maybe make a dict?

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