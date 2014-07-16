
from __future__ import print_function
from random import randint
from time import time

import Flipper


def main(n=1000, k=100, p=3, q=5):
	try:
		for i in range(n):
			print(i)
			M = Flipper.kernel.Matrix([[randint(-k, k) for _ in range(p)] for _ in range(q)])
			t = time()
			a = M.nontrivial_polytope()
			r = time()
			b = M.nontrivial_polytope2()
			s = time()
			print(r-t, s-r)
			if a != b:
				print(M)
				print('Foo')
				assert(False)
	except AssertionError:
		return False
	
	return True

if __name__ == '__main__':
	main(p=5, q=20)

