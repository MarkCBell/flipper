
from __future__ import print_function
from math import log10 as log
from itertools import product

import flipper
interval_helper = flipper.kernel.interval.interval_helper

def main(verbose=False):
	if verbose: print('Running interval tests.')
	
	w = interval_helper('0.10')
	x = interval_helper('10000.0')
	y = interval_helper('1.14571')
	z = interval_helper('1.00000')
	a = interval_helper('-1.200000')
	b = interval_helper('1.4142135623')
	
	# Check:
	#	acc(I + J) >= min(acc(I), acc(J)) - 1,
	#	acc(I * J) >= min(acc(I), acc(J)) - log(I.lower + J.lower + 1)
	#	acc(I / J) >= min(acc(I), acc(J)) - log+(J)  # If J > I.
	#	acc(x * I) >= acc(I) - log+(x)
	
	try:
		for I, J in product([w, x, y, z, a, b], repeat=2):
			m = min(I.accuracy, J.accuracy)
			assert((I + J).accuracy >= m - 1)
			assert((I * J).accuracy >= m - log(max(I.lower + J.lower + 1, 1)))
			# assert((I / J).accuracy >= m - J.log_plus)  # Should only do this test when J > I.
	except AssertionError:
		return False
	
	return True

if __name__ == '__main__':
	print(main(verbose=True))

