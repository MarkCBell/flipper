
from __future__ import print_function

import flipper

def main(verbose=False):
	if verbose: print('Running matrix tests.')
	
	# !?! Add test here.
	M = flipper.kernel.Matrix([[2, 1], [1, 1]])
	N = flipper.kernel.Matrix([[1, -1], [-1, 2]])
	
	tests = [
		M * N == flipper.kernel.id_matrix(2),
		M.char_poly() == flipper.kernel.Polynomial([1, -3, 1]),
		M.determinant() == 1
		]
	
	return all(tests)

if __name__ == '__main__':
	print(main(verbose=True))

