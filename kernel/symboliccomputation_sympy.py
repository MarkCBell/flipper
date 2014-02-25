

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


from math import log10 as log

import sympy

import Flipper
from Flipper.kernel.symboliccomputation_dummy import AlgebraicType

_name = 'sympy'

def simplify(self):
	self.value = sympy.simplify(self.value)

def minimal_polynomial_coefficients(self):
	return tuple(int(x) for x in sympy.Poly(sympy.minpoly(self.value)).all_coeffs()[::-1])

def string_approximate(self, precision, power=1):
	return str(sympy.N(self.value**power, n=precision))

AlgebraicType.simplify = simplify
AlgebraicType.minimal_polynomial_coefficients = minimal_polynomial_coefficients
AlgebraicType.string_approximate = string_approximate


def Perron_Frobenius_eigen(matrix):
	# Assumes that matrix is Perron-Frobenius and so has a unique real eigenvalue of largest
	# magnitude. If not an AssumptionError is thrown.
	
	M = sympy.Matrix(matrix.rows)
	try:
		eigenvalue = AlgebraicType(max(M.eigenvals(), key=abs))
	except:
		raise Flipper.AssumptionError('Matrix is not Perron-Frobenius.')  # !?! To do.
	
	return eigenvalue, None
