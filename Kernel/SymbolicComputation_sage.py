
from math import log10 as log

from sage.all import Matrix, lcm
from sage.rings.qqbar import AlgebraicNumber

from Flipper.Kernel.Error import AssumptionError

_name = 'sage'

algebraic_type = AlgebraicNumber

def simplify_algebraic_type(x):
	x.simplify()
	return x

def string_algebraic_type(x):
	return '%0.4f' % float(x)

def Perron_Frobenius_eigen(matrix):
	# Assumes that matrix is Perron-Frobenius and so has a unique real eigenvalue of largest
	# magnitude. If not an AssumptionError is thrown.
	M = Matrix(matrix.rows)
	eigenvalue = max(M.eigenvalues())
	N = M - eigenvalue
	try:
		[eigenvector] = N.right_kernel().basis()
	except ValueError:
		raise AssumptionError('Matrix is not Perron-Frobenius.')
	
	return [simplify_algebraic_type(x) for x in eigenvector], eigenvalue

def minimal_polynomial_coefficients(number):
	X = tuple(number.minpoly().coefficients())
	scale = lcm([x.denominator() for x in X])
	return tuple(int(scale * x) for x in X)

def symbolic_approximate(number, accuracy):
	# First we need to correct for the fact that we may lose some digits of accuracy
	# if the integer part of the number is big.
	precision = accuracy + max(int(log(number.n(digits=1))), 1)
	return str(number.n(digits=precision))
