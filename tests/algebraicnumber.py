
from __future__ import print_function
from time import time

import flipper

algebraic_number_from_info = flipper.kernel.algebraicnumber.algebraic_number_from_info

def main(verbose=False):
	start_time = time()
	a = algebraic_number_from_info([-2, 0, 1], '1.41')  # sqrt(2).
	b = algebraic_number_from_info([-3, 0, 1], '1.732')  # sqrt(3).
	c = algebraic_number_from_info([-1001, 0, 1], '31.639')  # sqrt(1001).
	
	# Add more tests here.
	try:
		assert(a * a == 2)
		assert(b * b == 3)
		assert(a * b == b * a)
		assert((a + 1) * (b + 1) == 1 + a + b + a * b)
		assert((1 + a + b) * (b + 1) == 1 + a + b + b + a * b + b * b)
		assert((1 + a + b) * (1 + a) * (1 + b) == 6 + 5 * a + 4 * b + 3 * a * b)
		assert(10000 * c * c == 10000 * 1001)
	except AssertionError:
		return False
	
	if verbose: print('Time taken: %0.3fs' % (time() - start_time))
	return True

if __name__ == '__main__':
	print(main(verbose=True))

