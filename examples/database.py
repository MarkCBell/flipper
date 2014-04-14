
import os

def from_database(file_name):
	for line in open(os.path.join(os.path.dirname(__file__), file_name)):
		line = line.strip()
		if '#' in line:
			line = line[:line.find('#')]
		if line:
			yield line.strip().split('\t')

