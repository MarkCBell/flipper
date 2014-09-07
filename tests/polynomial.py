
from __future__ import print_function

import flipper

def main(verbose=False):
	if verbose: print('Running polynomial tests.')
	
	f = flipper.kernel.Polynomial([-2, 0, 1])  # f = x^2 - 2.
	g = flipper.kernel.Polynomial([0, 2])  # g = 2x.
	h = flipper.kernel.Polynomial([-2, 2, 1])
	f2 = flipper.kernel.Polynomial([1, -7, 19, -26, 19, -7, 1])
	
	try:
		assert(g == f.derivative())
		assert(h == f + g)
		assert(len(f.primitive_roots()) == 2)
		assert(len(f2.primitive_roots()) == 3)
	except AssertionError:
		return False
	
	return True

if __name__ == '__main__':
	print(main(verbose=True))

