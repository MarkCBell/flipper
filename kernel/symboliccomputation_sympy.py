

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
from Flipper.kernel.symboliccomputation_dummy import AlgebraicType, eigenvector_from_eigenvalue

_name = 'sympy'

def algebraic_simplify(self):
	self.value = sympy.simplify(self.value)

def algebraic_minimal_polynomial_coefficients(self):
	return tuple(int(x) for x in sympy.Poly(sympy.minpoly(self.value)).all_coeffs()[::-1])

def algebraic_approximate(self, accuracy, degree=None, power=1):
	if degree is None: degree = self.algebraic_degree()  # If not given, assume that the degree of the number field is the degree of this number.
	
	# First we need to correct for the fact that we may lose some digits of accuracy
	# if the integer part of the number is big.
	precision = accuracy + int(log(max(sympy.N(self.value**power, n=1), 1))) + 1
	A = Flipper.kernel.algebraicapproximation.algebraic_approximation_from_string(str(sympy.N(self.value**power, n=precision)), degree, self.algebraic_log_height())
	assert(A.interval.accuracy >= accuracy)
	return A

AlgebraicType.algebraic_simplify = algebraic_simplify
AlgebraicType.algebraic_minimal_polynomial_coefficients = algebraic_minimal_polynomial_coefficients
AlgebraicType.algebraic_approximate = algebraic_approximate


def Perron_Frobenius_eigen(matrix):
	# Assumes that matrix is Perron-Frobenius and so has a unique real eigenvalue of largest
	# magnitude. If not an AssumptionError is thrown.
	
	M = sympy.Matrix(matrix.rows)
	eigenvalue = AlgebraicType(max(M.eigenvals(), key=abs))
	
	return eigenvector_from_eigenvalue(matrix, eigenvalue)
