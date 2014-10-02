
from __future__ import print_function

import flipper

algebraic_approximation = flipper.kernel.create_algebraic_approximation

def main(verbose=False):
	if verbose: print('Running algebraic approximation tests.')
	
	# We acutally need quite a lot of accuracy in the given strings.
	x = algebraic_approximation('1.4142135623730950488016887242096980785696718753769480', 2, 2)
	y = algebraic_approximation('1.4142135623730950488016887242096980', 2, 2)
	z = algebraic_approximation('1.000000000000', 2, 2)
	
	tests = [
		x == y,
		z != y,
		x + y == x + x,
		x * x == 2,
		y * y == 2,
		y * y + x == 2 + x,
		y * (y + y) == 4,
		x * x == y * y,
		x + x > 0,
		-(x + x) < 0,
		x > z > 0
		]
	
	return all(tests)

if __name__ == '__main__':
	print(main(verbose=True))

