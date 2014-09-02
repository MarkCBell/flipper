
from __future__ import print_function

import flipper

algebraic_approximation = flipper.kernel.algebraic_approximation

def main(verbose=False):
	if verbose: print('Running algebraic approximation tests.')
	
	# We acutally need quite a lot of accuracy in the given strings.
	x = algebraic_approximation('1.4142135623730950488016887242096980785696718753769480', 2, 2)
	y = algebraic_approximation('1.4142135623730950488016887242096980', 2, 2)
	z = algebraic_approximation('1.000000000000', 2, 2)
	
	try:
		assert(x == y)
		assert(z != y)
		assert(x + y == x + x)
		assert(x * x == 2)
		assert(y * y == 2)
		assert(y * y + x == 2 + x)
		assert(y * (y + y) == 4)
		assert(x * x == y * y)
		assert(x + x > 0)
		assert(-(x + x) < 0)
		assert(x > z > 0)
	except AssertionError:
		return False
	
	return True

if __name__ == '__main__':
	print(main(verbose=True))

