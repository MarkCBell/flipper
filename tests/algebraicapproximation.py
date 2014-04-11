
from __future__ import print_function

import flipper

algebraic_approximation_from_string = flipper.kernel.algebraicapproximation.algebraic_approximation_from_string

def main():
	x = algebraic_approximation_from_string('1.4142135623730951', 2, 2)
	y = algebraic_approximation_from_string('1.41421356237', 2, 2)
	z = algebraic_approximation_from_string('1.000000', 2, 2)
	
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
	except AssertionError:
		return False
	
	return True

if __name__ == '__main__':
	print(main())
