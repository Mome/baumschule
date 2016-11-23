
# This is the treefarm default configuration file
# The environment is automatically added to the namespace with 'env'
# Configuration storage can be accesses with 'env.config'

from os.path import join, expanduser

c.base_path = expanduser('~/treefarm')
c.protocol_path = join(c.base_path, 'protocol')
c.env_path = join(c.base_path, 'environment')
