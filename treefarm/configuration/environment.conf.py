from os.path import join, dirname, normpath, realpath

c.add_subgroup('environment')

module_path = dirname(__file__)
env_path = join(module_path, '..', 'environments/default_env.py')
env_path = normpath(env_path)
env_path = realpath(env_path)

c.environment.paths = [
    env_path,
]
