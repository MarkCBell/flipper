

from __future__ import print_function

import os

def main():
	print('Available examples:')
	for example_name in sorted(os.listdir(os.path.dirname(__file__))):
		name, extension = os.path.splitext(example_name)
		if extension == '.py' and not name.startswith('_'):
			print('\tflipper.example.%s' % name)
	print('The --show flag can be used to see an examples source code.')

if __name__ == '__main__':
	main()

