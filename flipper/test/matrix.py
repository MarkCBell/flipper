
from __future__ import print_function

import flipper

def main(verbose=False):
	if verbose: print('Running matrix tests.')
	
	M = flipper.kernel.Matrix([[2, 1], [1, 1]])
	N = flipper.kernel.Matrix([[1, -1], [-1, 2]])
	M_inv = flipper.kernel.Matrix([[1, -1], [-1, 2]])
	# M + N = [[3, 0], [0, 3]]
	# M - N = [[1, 2], [2, -1]]
	
	tests = [
		M * N == flipper.kernel.id_matrix(2),
		M.characteristic_polynomial() == flipper.kernel.Polynomial([1, -3, 1]),
		M.determinant() == 1,
		M.kernel() == flipper.kernel.Matrix([]),
		(M + N).determinant() == 9,
		(M - N).determinant() == -5,
		(M**2)**3 == (M**3)**2,  # Check that powers are associative.
		M.inverse() == M_inv,
		M.characteristic_polynomial()(M) == flipper.kernel.zero_matrix(2),  # Check Cayley--Hamilton theorem.
		]
	
	if not all(tests):
		if verbose: print(tests)
		return False
	
	return True

if __name__ == '__main__':
	print(main(verbose=True))

