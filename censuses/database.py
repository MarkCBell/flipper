
import os

def load(file_name):
	for line in open(os.path.join(os.path.dirname(__file__), file_name + '.dat')):
		line = line.strip()
		if '#' in line:
			line = line[:line.find('#')]
		if line:
			yield line.strip().split('\t')

