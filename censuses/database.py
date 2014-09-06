
''' A module for loading flipper databases. '''
import os

def load(file_name, test=None):
	''' Iterates through the requested database. If given, results are filered by using test'''
	
	# !?! This is not safe.
	for line in open(os.path.join(os.path.dirname(__file__), file_name + '.dat')):
		line = line.strip()
		if '#' in line:
			line = line[:line.find('#')]
		
		if line:
			data = line.strip().split('\t')
			if test is None or test(data):
				yield data

