
from sage.all import Matrix, lcm, NumberField, QQbar
from math import log10 as log

import Flipper

symbolic_libaray_name = 'sage'

def largest_root_string(polynomial, accuracy, ):
	K = QQbar['x']
	[x] = K.gens()
	
	f = K(list(polynomial))
	x = max(f.roots())[0]
	precision = accuracy + int(log(max(x.n(digits=1), 1))) + 1
	return x.n(digits=precision).str(no_sci=2)

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
	[lam] = K.gens()
	
	try:
		[eigenvector] = (M - lam).right_kernel().basis()
	except ValueError:
		raise Flipper.AssumptionError('Matrix is not Perron-Frobenius.')
	
	scale = abs(lcm([x.denominator() for v in eigenvector for x in v.polynomial().coeffs()]))
	
	return minimal_polynomial_coefficients(eigenvalue), [[int(scale * x) for x in v.polynomial().coeffs()] for v in eigenvector]
