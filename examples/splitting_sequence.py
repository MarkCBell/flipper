
from __future__ import print_function

from time import time

import flipper
from database import from_database

def main():
	tests = [('S_2_1', 'abcdeF')]
	for surface, word in tests:
		print(word)
		start_time = time()
		S = flipper.examples.abstracttriangulation.SURFACES[surface]()
		mapping_class = S.mapping_class(word)
		mapping_class.splitting_sequence()
		print('Computed in %f' % (time() - start_time))

if __name__ == '__main__':
	main()

