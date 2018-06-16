import os

names = os.popen('ls -1a ./converted').read().split('\n')

for name in names:
	new_name = name[:-8] + name[-4:]
	os.system('mv ./converted/{0} ./converted/{1}'.format(name, new_name))
