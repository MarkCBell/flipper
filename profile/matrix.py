
from __future__ import print_function
from random import randint
from time import time

import flipper

def main(n=1000, k=100, p=3, q=5):
	for i in range(n):
		print(i)
		M = flipper.kernel.Matrix([[randint(-k, k) for _ in range(p)] for _ in range(q)])
		t = time()
		a = M.nontrivial_polytope()
		r = time()
		b = M.nontrivial_polytope2()
		s = time()
		print(r-t, s-r)
		if a != b:
			print(M)
			assert(False)

if __name__ == '__main__':
	main()
