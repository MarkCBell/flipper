
from __future__ import print_function

import flipper

def main():
	f = flipper.kernel.Polynomial([-2, 0, 1])  # f = x^2 - 2.
	try:
		AA = f.algebraic_approximate_leading_root(10)
		assert(AA * AA == 2)
	except AssertionError:
		return False
	
	return True

if __name__ == '__main__':
	print(main())

