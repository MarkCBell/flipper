
from __future__ import print_function
from math import log10 as log
from itertools import product

import flipper

interval = flipper.kernel.create_interval

def main(verbose=False):
	if verbose: print('Running interval tests.')
	
	w = interval('0.10')
	x = interval('10000.0')
	y = interval('1.14571')
	z = interval('1.00000')
	a = interval('-1.200000')
	b = interval('1.4142135623')
	
	# Check:
	#	acc(I + J) >= min(acc(I), acc(J)) - 1,
	#	acc(I * J) >= min(acc(I), acc(J)) - log(I.lower + J.lower + 1)
	#	acc(I / J) >= min(acc(I), acc(J)) - log+(J)  # If J > I.
	#	acc(x * I) >= acc(I) - log+(x)
	
	for I, J in product([w, x, y, z, a, b], repeat=2):
		m = min(I.accuracy, J.accuracy)
		if not ((I + J).accuracy >= m - 1): return False
		if not ((I * J).accuracy >= m - log(max(I.lower + J.lower + 1, 1))): return False
		# if not ((I / J).accuracy >= m - J.log_plus()): return False  # Should only do this test when J > I.
	
	return True

if __name__ == '__main__':
	print(main(verbose=True))

