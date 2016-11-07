import treefarm
s = treefarm.System()
print('blubs', id(s))

c.basepath = os.path.expanduser('~/treefarm')
c.configfiles = os.path.expanduser('~/treefarm')

c.otherstuff.blub = 'yes'
