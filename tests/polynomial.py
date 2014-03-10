
from __future__ import print_function

import Flipper

def main():
	f = Flipper.Polynomial([-2, 0, 1])
	try:
		AA = f.algebraic_approximate_leading_root(10)
		BB = f.algebraic_approximate_leading_root(10, power=2)
		assert(AA * AA == 2)
		assert(BB == 2)
	except ImportError:
		print('Symbolic computation library required but unavailable, test skipped.')
	except AssertionError:
		return False
	
	return True

if __name__ == '__main__':
	print(main())
