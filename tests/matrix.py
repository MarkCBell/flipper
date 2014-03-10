
from __future__ import print_function
from random import randint

import Flipper

def main(n=1000, k=100):
	try:
		for _ in range(n):
			M = Flipper.Matrix([[randint(-k, k) for _ in range(3)] for _ in range(5)], 3)
			nontrivial, certificate = M.nontrivial_polytope()
			assert(not nontrivial or M.nonnegative_image(certificate))
	except AssertionError:
		return False
	
	return True

if __name__ == '__main__':
	print(main())
