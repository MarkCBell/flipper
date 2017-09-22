
import sys
import subprocess

def open_documentation(verbose=False):
	''' Open the flipper documentation. '''
	
	path = 'http://flipper.readthedocs.io/en/latest/'
	
	if sys.platform.startswith('darwin'):
		subprocess.call(['open', path])
	elif sys.platform.startswith('win'):
		os.startfile(path)
	else:
		subprocess.call(['xdg-open', path])

if __name__ == '__main__':
	open_documentation()

