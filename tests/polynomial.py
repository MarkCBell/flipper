
from __future__ import print_function

import flipper

def main(verbose=False):
	if verbose: print('Running polynomial tests.')
	
	f = flipper.kernel.Polynomial([-2, 0, 1])  # f = x^2 - 2.
	g = flipper.kernel.Polynomial([0, 2])  # g = 2x.
	h = flipper.kernel.Polynomial([-2, 2, 1])
	# rt2 = flipper.kernel.polynomial_root_helper([-2, 0, 1], '1.41')  # sqrt(2).
	
	try:
		assert(g == f.derivative())
		assert(h == f + g)
	except AssertionError:
		return False
	
	return True

if __name__ == '__main__':
	print(main(verbose=True))

