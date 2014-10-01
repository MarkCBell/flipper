
import os
import sys
import subprocess

def open_documentation():
	datadir = os.path.dirname(__file__)
	disk_file = os.path.join(datadir, 'docs', 'flipper.pdf')
	print(disk_file)
	if sys.platform.startswith('darwin'):
		command = 'xdg-open'
	elif sys.platform.startswith('win'):
		command = 'start'
	else:
		command = 'xdg-open'
	
	subprocess.call([command, disk_file])

if __name__ == '__main__':
	open_documentation()

