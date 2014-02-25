
from math import log10 as log

from sage.all import Matrix, lcm, NumberField

import Flipper
from Flipper.kernel.symboliccomputation_dummy import AlgebraicType

_name = 'sage'

def simplify(self):
	self.value.simplify()

def minimal_polynomial_coefficients(self):
	X = tuple(self.value.minpoly().coeffs())
	scale = abs(lcm([x.denominator() for x in X]))
	return tuple(int(scale * x) for x in X)

def string_approximate(self, precision, power=1):
	# First we need to correct for the fact that we may lose some digits of accuracy
	# if the integer part of the number is big.
	return str((self.value**power).n(digits=precision))

AlgebraicType.simplify = simplify
AlgebraicType.minimal_polynomial_coefficients = minimal_polynomial_coefficients
AlgebraicType.string_approximate = string_approximate


def PF_eigen(matrix):
	# Assumes that matrix is Perron-Frobenius and so has a unique real eigenvalue of largest
	# magnitude. If not an AssumptionError is thrown.
	
	M = Matrix(matrix.rows)
	eigenvalue = max(M.eigenvalues(), key=abs)
	
	# We could just return None as the eigenvector but this is much faster.
	K = NumberField(eigenvalue.minpoly(), 'L')
	lam = K.gens()[0]
	
	try:
		[eigenvector] = (M - lam).right_kernel().basis()
	except ValueError:
		raise Flipper.AssumptionError('Matrix is not Perron-Frobenius.')
	
	scale = abs(lcm([x.denominator() for v in eigenvector for x in v.polynomial().coeffs()]))
	
	return AlgebraicType(eigenvalue), [[int(scale * x) for x in v.polynomial().coeffs()] for v in eigenvector]
