
from math import log10 as log

from sage.all import Matrix, lcm, simplify, AlgebraicNumber

import Flipper
from Flipper.kernel.symboliccomputation_dummy import AlgebraicType

_name = 'sage'

def algebraic_simplify(self, value=None):
	if value is not None:
		value.simplify()
		return value
	else:
		self.value.simplify()
		return self

def _minimal_polynomial_coefficients(self):
	X = tuple(self.value.minpoly().coefficients())
	scale = lcm([x.denominator() for x in X])
	return tuple(int(scale * x) for x in X)

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
	precision = accuracy + int(log(max(self.value.n(digits=1), 1))) + 1
	if degree is None: degree = self.algebraic_degree()  # If not given, assume that the degree of the number field is the degree of this number.
	A = Flipper.kernel.algebraicapproximation.algebraic_approximation_from_string(str(self.value.n(digits=precision)), degree, self.algebraic_log_height())
	assert(A.interval.accuracy >= accuracy)
	return A

AlgebraicType.algebraic_simplify = algebraic_simplify
AlgebraicType._minimal_polynomial_coefficients = _minimal_polynomial_coefficients
AlgebraicType.algebraic_hash = algebraic_hash
AlgebraicType.algebraic_degree = algebraic_degree
AlgebraicType.algebraic_log_height = algebraic_log_height
AlgebraicType.algebraic_approximate = algebraic_approximate


def Perron_Frobenius_eigen(matrix, vector=None, condition_matrix=None):
	# Assumes that matrix is Perron-Frobenius and so has a unique real eigenvalue of largest
	# magnitude. If not an AssumptionError is thrown.
	M = Matrix(matrix.rows)
	eigenvalue = max(M.eigenvalues())
	N = M - eigenvalue
	try:
		[eigenvector] = N.right_kernel().basis()
	except ValueError:
		raise Flipper.AssumptionError('Matrix is not Perron-Frobenius.')
	
	s = sum(eigenvector)
	if s == 0:
		raise Flipper.AssumptionError('Matrix is not Perron-Frobenius.')
	
	eigenvector = [AlgebraicType(x / s).algebraic_simplify() for x in eigenvector]
	
	if condition_matrix is not None:
		if not condition_matrix.nonnegative_image(eigenvector):
			raise Flipper.ComputationError('Could not estimate invariant lamination.')  # If not then the curve failed to get close enough to the invariant lamination.
	
	# n = matrix.width  # n = 6, log(n) ~ 0.75.
	# m = matrix.bound()  # log(m) ~ 4.
	# k = n * (log(m) + log(n+1) + log(2))
	# H = log(n) + n**3 * (log(n) + log(m) + k) + n**2 * k
	# H2 = n * (n + m)
	
	# print(m, n)
	# print('eigenvalue bound prediction: %s' % k)
	# print('eigenvalue bound: %s' % log_height_algebraic_type(eigenvalue))
	# print('entry bound prediction: %s' % H)
	# print('entry bound prediction: %s' % H2)
	# print('entry bound: %s '% max(log_height_algebraic_type(entry) for entry in eigenvector))
	
	return eigenvector

def algebraic_type_from_int(integer):
	return AlgebraicType(AlgebraicNumber(integer))
