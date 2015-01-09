
from __future__ import print_function

import flipper

from time import time

def main():
	tests = [('S_2_1', 'abcdeF')]
	for surface, word in tests:
		print(word)
		start_time = time()
		flipper.load.equipped_triangulation(surface).mapping_class(word).splitting_sequence()
		print('Computed in %0.3fs' % (time() - start_time))

if __name__ == '__main__':
	main()

