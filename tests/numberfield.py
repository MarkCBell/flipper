
from __future__ import print_function

import flipper

def main():
	
	# !?! TO DO.
	
	try:
		f = flipper.kernel.polynomial.polynomial_root_from_info([-2, 0, 1], '1.41')  # sqrt(2).
		N = flipper.kernel.NumberField(f)  # QQ(sqrt(2)).
		x = N.lmbda  # sqrt(2)
		assert(x * x == 2)
	except AssertionError:
		return False
	
	return True

if __name__ == '__main__':
	print(main())

