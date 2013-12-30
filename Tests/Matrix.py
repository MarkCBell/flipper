
from random import randint

from Flipper.Kernel.Matrix import Matrix, nonnegative_image

def main(n=1000, k=100):
	for i in range(n):
		M = Matrix([[randint(-k,k) for i in range(3)] for j in range(5)], 3)
		nontrivial, certificate = M.nontrivial_polytope()
		if nontrivial and not nonnegative_image(M, certificate):
			print(M)
			print(nontrivial, certificate)
			return False
	
	return True

if __name__ == '__main__':
	print(main())