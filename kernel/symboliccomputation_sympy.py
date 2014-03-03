

# WARNING: Sympy really seems to struggle with PF calculations. For example, try:
# [
# [0, 0, -1, 0, 0, 0, 0, 1, 1],
# [0, -1, -2, 1, 1, -1, 0, 2, 1],
# [0, 0, -3, 0, 1, -1, 0, 3, 1],
# [0, 0, -2, 0, 1, 0, 0, 2, 0],
# [0, -1, -1, 1, 1, -1, 0, 1, 1],
# [0, 0, -1, 0, 1, 0, 1, 0, 0],
# [0, 0, -2, -1, 1, 0, 0, 3, 0],
# [-1, 0, -3, -1, 1, 0, 0, 4, 1],
# [0, 0, -1, 1, 0, -1, 0, 1, 1]
# ]
# or:
# [
# [0, -1, -2, 2, 1, 0, 1, 0, 0],
# [0, 0, -1, 1, 1, 0, 0, 0, 0],
# [1, -1, 0, 1, 0, 0, 0, -1, 1],
# [1, -1, -1, 1, 1, 0, 1, -1, 0],
# [0, -1, -1, 1, 1, 0, 0, 0, 1],
# [1, -3, -4, 3, 3, 0, 2, -1, 0],
# [1, -2, -2, 2, 1, 0, 1, -1, 1],
# [1, 0, 1, 1, -1, -1, 0, -1, 1],
# [1, -2, -3, 2, 2, 0, 1, 0, 0]
# ]


import sympy

import Flipper

_name = 'sympy'

def minimal_polynomial_coefficients(value):
	return tuple(int(x) for x in sympy.Poly(sympy.minpoly(value)).all_coeffs()[::-1])

def PF_eigen(matrix):
	# Assumes that matrix is Perron-Frobenius and so has a unique real eigenvalue of largest
	# magnitude. If not an AssumptionError is thrown.
	
	M = sympy.Matrix(matrix.rows)
	eigenvalues = M.eigenvals()
	eigenvalue = max(eigenvalues, key=abs)
	if eigenvalues[eigenvalue] != 1:
		raise Flipper.AssumptionError('Matrix is not Perron-Frobenius.')  # !?! To do.
	
	return minimal_polynomial_coefficients(eigenvalue), None
