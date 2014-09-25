
''' A module for loading flipper databases. '''

import flipper

import os

DATABASE_DIRECTORY = os.path.join(os.path.dirname(__file__), 'censuses')

def find_databases():
	''' Return a list of all loadable databases. '''
	
	databases = []
	for path in os.listdir(DATABASE_DIRECTORY):
		_, tail = os.path.split(path)
		name, extension = os.path.splitext(tail)
		if extension == '.dat':
			databases.append(name)
	
	return databases

def load(file_name, find=None):
	''' Iterates through the requested database.
	
	If given, only results containing find are returned. '''
	
	assert(isinstance(file_name, flipper.StringType))
	assert(find is None or isinstance(find, flipper.StringType))
	
	if file_name in find_databases():
		for line in open(os.path.join(DATABASE_DIRECTORY, file_name + '.dat')):
			if find is None or line.find(find) != -1:
				line = line.strip()
				if '#' in line:
					line = line[:line.find('#')]
				
				if line:
					yield line.strip().split('\t')
	else:
		raise ValueError('No database named %s in %s' % (file_name, DATABASE_DIRECTORY))

