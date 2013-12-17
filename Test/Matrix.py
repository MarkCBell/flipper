
from random import randint

from Flipper.Kernel.Matrix import Matrix

def main(n=1000, k=100):
	for i in range(n):
		M = Matrix([[randint(-k,k) for i in range(3)] for j in range(5)], 3)
		print('==M==')
		print(M)
		print(M.nontrivial_polytope())

if __name__ == '__main__':
	main()