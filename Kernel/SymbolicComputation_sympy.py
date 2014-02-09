

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

from math import log10 as log

import sympy

import Flipper
from Flipper.Kernel.SymbolicComputation_dummy import Algebraic_Type

_name = 'sympy'

def algebraic_simplify(self, value=None):
	if value is not None:
		return sympy.simplify(value)
	else:
		return Algebraic_Type(sympy.simplify(self.value))

def _minimal_polynomial_coefficients(self):
	return tuple(int(x) for x in sympy.Poly(sympy.minpoly(self.value)).all_coeffs()[::-1])

# We take the coefficients of the minimal polynomial of each entry and sort them. This has the nice property that there is a
# uniform bound on the number of collisions.
def algebraic_hash(self):
	return self._minimal_polynomial_coefficients()

def algebraic_degree(self):
	return len(self._minimal_polynomial_coefficients()) - 1

def algebraic_log_height(self):
	return log(max(abs(x) for x in self._minimal_polynomial_coefficients()))

def algebraic_approximate(self, accuracy, degree=None):
	if degree is None: degree = self.algebraic_degree()  # If not given, assume that the degree of the number field is the degree of this number.
	
	if self.value.is_Integer:
		return Flipper.Kernel.AlgebraicApproximation.algebraic_approximation_from_int(self.value, accuracy, degree, self.algebraic_log_height())
	else:
		# First we need to correct for the fact that we may lose some digits of accuracy
		# if the integer part of the number is big.
		precision = accuracy + int(log(max(sympy.N(self.value, n=1), 1))) + 1
		A = Flipper.Kernel.AlgebraicApproximation.algebraic_approximation_from_string(str(sympy.N(self.value, n=precision)), degree, self.algebraic_log_height())
		assert(A.interval.accuracy >= accuracy)
		return A

Algebraic_Type.algebraic_simplify = algebraic_simplify
Algebraic_Type._minimal_polynomial_coefficients = _minimal_polynomial_coefficients
Algebraic_Type.algebraic_hash = algebraic_hash
Algebraic_Type.algebraic_degree = algebraic_degree
Algebraic_Type.algebraic_log_height = algebraic_log_height
Algebraic_Type.algebraic_approximate = algebraic_approximate


def Perron_Frobenius_eigen(matrix, vector=None, condition_matrix=None):
	# Assumes that matrix is Perron-Frobenius and so has a unique real eigenvalue of largest
	# magnitude. If not an AssumptionError is thrown.
	
	M = sympy.Matrix(matrix.rows)
	eigenvalue = max(M.eigenvals())
	N = M - eigenvalue * sympy.eye(matrix.width)
	try:
		[eigenvector] = N.nullspace(simplify=True)
	except ValueError:
		raise Flipper.Kernel.Error.AssumptionError('Matrix is not Perron-Frobenius.')
	
	s = sum(eigenvector)
	if s == 0:
		raise Flipper.Kernel.Error.AssumptionError('Matrix is not Perron-Frobenius.')
	
	eigenvalue = Algebraic_Type(eigenvalue)
	eigenvector = [Algebraic_Type(x / s).algebraic_simplify() for x in eigenvector]
	
	if condition_matrix is not None:
		if not condition_matrix.nonnegative_image(eigenvector):
			raise Flipper.Kernel.Error.ComputationError('Could not estimate invariant lamination.')  # If not then the curve failed to get close enough to the invariant lamination.
	
	return eigenvector, eigenvalue

def algebraic_type_from_int(integer):
	return Algebraic_Type(integer)
