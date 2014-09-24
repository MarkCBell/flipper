
from __future__ import print_function

import flipper

algebraic_approximation = flipper.kernel.algebraic_approximation

def main(verbose=False):
	if verbose: print('Running algebraic approximation tests.')
	
	# We acutally need quite a lot of accuracy in the given strings.
	x = algebraic_approximation('1.4142135623730950488016887242096980785696718753769480', 2, 2)
	y = algebraic_approximation('1.4142135623730950488016887242096980', 2, 2)
	z = algebraic_approximation('1.000000000000', 2, 2)
	
	if not (x == y): return False
	if not (z != y): return False
	if not (x + y == x + x): return False
	if not (x * x == 2): return False
	if not (y * y == 2): return False
	if not (y * y + x == 2 + x): return False
	if not (y * (y + y) == 4): return False
	if not (x * x == y * y): return False
	if not (x + x > 0): return False
	if not (-(x + x) < 0): return False
	if not (x > z > 0): return False
	
	return True

if __name__ == '__main__':
	print(main(verbose=True))

