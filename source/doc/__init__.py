
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
	
	# Note that the command contains no user provided data.
	# So even setting shell=True should be safe.
	if sys.platform.startswith('darwin'):
		subprocess.call(['open', disk_file])
	elif sys.platform.startswith('win'):
		os.startfile(disk_file)
	else:
		subprocess.call(['xdg-open', disk_file])

