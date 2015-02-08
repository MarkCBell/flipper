
''' Stores the documentation for flipper. '''

import os
import sys
import subprocess

def open_documentation(verbose=False):
	''' Open the flipper users guide using the default pdf viewer. '''
	
	datadir = os.path.dirname(__file__)
	disk_file = os.path.join(datadir, 'flipper.pdf')
	if verbose: print('Opening:')
	if verbose: print(disk_file)
	if sys.platform.startswith('darwin'):
		command = 'open'
	elif sys.platform.startswith('win'):
		command = 'start'
	else:
		command = 'xdg-open'
	
	# Note that the command contains no user provided data.
	# So setting shell=True should be safe.
	subprocess.call([command, disk_file])

