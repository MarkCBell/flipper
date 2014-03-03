
from sage.all import Matrix, lcm, NumberField

import Flipper

_name = 'sage'


def minimal_polynomial_coefficients(value):
	X = tuple(value.minpoly().coeffs())
	scale = abs(lcm([x.denominator() for x in X]))
	return tuple(int(scale * x) for x in X)

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
	
	return minimal_polynomial_coefficients(eigenvalue), [[int(scale * x) for x in v.polynomial().coeffs()] for v in eigenvector]
