
from math import log10 as log

from sage.all import Matrix, lcm, NumberField

import Flipper
from Flipper.kernel.symboliccomputation_dummy import AlgebraicType, eigenvector_from_eigenvalue

_name = 'sage'

def algebraic_simplify(self):
	self.value.simplify()

def algebraic_minimal_polynomial_coefficients(self):
	X = tuple(self.value.minpoly().coeffs())
	scale = abs(lcm([x.denominator() for x in X]))
	return tuple(int(scale * x) for x in X)

def algebraic_approximate(self, accuracy, degree=None, power=1):
	# First we need to correct for the fact that we may lose some digits of accuracy
	# if the integer part of the number is big.
	precision = accuracy + int(log(max((self.value**power).n(digits=1), 1))) + 1
	if degree is None: degree = self.algebraic_degree()  # If not given, assume that the degree of the number field is the degree of this number.
	A = Flipper.kernel.algebraicapproximation.algebraic_approximation_from_string(str((self.value**power).n(digits=precision)), degree, self.algebraic_log_height())
	assert(A.interval.accuracy >= accuracy)
	return A

AlgebraicType.algebraic_simplify = algebraic_simplify
AlgebraicType.algebraic_minimal_polynomial_coefficients = algebraic_minimal_polynomial_coefficients
AlgebraicType.algebraic_approximate = algebraic_approximate


def Perron_Frobenius_eigen(matrix):
	# Assumes that matrix is Perron-Frobenius and so has a unique real eigenvalue of largest
	# magnitude. If not an AssumptionError is thrown.
	
	# We could use the eigenvector_from_eigenvalue function.
	# M = Matrix(matrix.rows)
	# eigenvalue = AlgebraicType(max(M.eigenvalues(), key=abs))
	#
	# return eigenvector_from_eigenvalue(matrix, eigenvalue)
	# but this is much faster.
		
	M = Matrix(matrix.rows)
	eigenvalue = max(M.eigenvalues(), key=abs)
	K = NumberField(eigenvalue.minpoly(), 'L')
	lam = K.gens()[0]
	
	try:
		[eigenvector] = (M - lam).right_kernel().basis()
	except ValueError:
		raise Flipper.AssumptionError('Matrix is not Perron-Frobenius.')
	
	scale = abs(lcm([x.denominator() for v in eigenvector for x in v.polynomial().coeffs()]))
	
	N = Flipper.kernel.numberfield.NumberField(AlgebraicType(eigenvalue))
	return [N.element([int(scale * x) for x in v.polynomial().coeffs()]) for v in eigenvector]
