
from __future__ import print_function

from time import time

import flipper

def main():
	tests = [('S_2_1', 'abcdeF')]
	for surface, word in tests:
		print(word)
		start_time = time()
		flipper.load.equipped_triangulation(surface).mapping_class(word).splitting_sequences()
		print('Computed in %0.3fs' % (time() - start_time))

if __name__ == '__main__':
	main()

