
from math import log10 as log

import sympy
from sympy.core.expr import Expr

from Flipper.Kernel.Error import AssumptionError, ComputationError
from Flipper.Kernel.Matrix import nonnegative_image
from Flipper.Kernel.AlgebraicApproximation import algebraic_approximation_from_string
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
	# First we need to correct for the fact that we may lose some digits of accuracy
	# if the integer part of the number is big.
	precision = accuracy + max(int(log(sympy.N(self.value, n=1))), 1)
	if degree is None: degree = self.algebraic_degree()  # If not given, assume that the degree of the number field is the degree of this number.
	A = algebraic_approximation_from_string(str(sympy.N(self.value, n=precision)), degree, self.algebraic_log_height())
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
		raise AssumptionError('Matrix is not Perron-Frobenius.')
	
	s = sum(eigenvector)
	if s == 0:
		raise AssumptionError('Matrix is not Perron-Frobenius.')
	
	eigenvector = [Algebraic_Type(x / s).algebraic_simplify() for x in eigenvector]
	
	if condition_matrix is not None:
		if not nonnegative_image(condition_matrix, eigenvector):
			raise ComputationError('Could not estimate invariant lamination.')  # If not then the curve failed to get close enough to the invariant lamination.
	
	# n = matrix.width  # n = 6, log(n) ~ 0.75.
	# m = matrix.bound()  # log(m) ~ 4.
	# k = n * (log(m) + log(n+1) + log(2))
	# H = log(n) + n**3 * (log(n) + log(m) + k) + n**2 * k
	
	# print(m, n)
	# print('eigenvalue bound prediction: %s' % k)
	# print('eigenvalue bound: %s' % log_height_algebraic_type(eigenvalue))
	# print('entry bound prediction: %s' % H)
	# print('entry bound: %s '% max(log_height_algebraic_type(entry) for entry in eigenvector))
	
	return eigenvector, eigenvalue
