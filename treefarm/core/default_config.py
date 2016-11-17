
# This is the treefarm default configuration file
# The environment is automatically added to the namespace with 'env'
# Configuration storage can be accesses with 'env.config'

from os import join, expanduser

c = env.config
c.base_path = expanduser('~/treefarm')
c.protocol_path = join(base_path, 'protocol')
