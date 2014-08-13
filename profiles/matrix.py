
from __future__ import print_function
from random import randint
from time import time

import flipper

def main(verbose=False, n=1000, k=100, p=3, q=5):
	t = time()
	for i in range(n):
		M = flipper.kernel.Matrix([[randint(-k, k) for _ in range(p)] for _ in range(q)])
		a = M.nontrivial_polytope()
		b = M.nontrivial_polytope2()
		if a != b:
			print(M)
			assert(False)
	return time() - t

if __name__ == '__main__':
	print(main(verbose=True))

