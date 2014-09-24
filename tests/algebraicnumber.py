
from __future__ import print_function

import flipper

algebraic_number = flipper.kernel.algebraic_number

def main(verbose=False):
	if verbose: print('Running algebraic number tests.')
	
	a = algebraic_number([-2, 0, 1], '1.41')  # sqrt(2).
	b = algebraic_number([-3, 0, 1], '1.732')  # sqrt(3).
	c = algebraic_number([-1001, 0, 1], '31.639')  # sqrt(1001).
	
	# Add more tests here.
	if not (a * a == 2): return False
	if not (b * b == 3): return False
	if not (a * b == b * a): return False
	if not ((a + 1) * (b + 1) == 1 + a + b + a * b): return False
	if not ((1 + a + b) * (b + 1) == 1 + a + b + b + a * b + b * b): return False
	if not ((1 + a + b) * (1 + a) * (1 + b) == 6 + 5 * a + 4 * b + 3 * a * b): return False
	if not (10000 * c * c == 10000 * 1001): return False
	
	return True

if __name__ == '__main__':
	print(main(verbose=True))

