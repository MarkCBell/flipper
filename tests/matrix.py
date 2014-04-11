
from __future__ import print_function
from random import randint

import flipper

def main(n=1000, k=100):
	try:
		for _ in range(n):
			M = flipper.kernel.Matrix([[randint(-k, k) for _ in range(3)] for _ in range(5)])
			M.nontrivial_polytope()
	except AssertionError:
		return False
	
	return True

if __name__ == '__main__':
	print(main())
