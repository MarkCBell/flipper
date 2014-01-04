
from math import log10 as log

from sage.all import Matrix, lcm
from sage.rings.qqbar import AlgebraicNumber

from Flipper.Kernel.Error import AssumptionError
from Flipper.Kernel.AlgebraicApproximation import algebraic_approximation_from_string

_name = 'sage'

algebraic_type = AlgebraicNumber

def simplify_algebraic_type(x):
	x.simplify()
	return x

def string_algebraic_type(x):
	return '%0.4f' % float(x)

def minimal_polynomial_coefficients(number):
	X = tuple(number.minpoly().coefficients())
	scale = lcm([x.denominator() for x in X])
	return tuple(int(scale * x) for x in X)

def hash_algebraic_type(number):
	return minimal_polynomial_coefficients(number)

def degree_algebraic_type(number):
	return len(minimal_polynomial_coefficients(number)) - 1

def log_height_algebraic_type(number):
	return log(max(abs(x) for x in minimal_polynomial_coefficients(number)))

def approximate_algebraic_type(number, accuracy, degree=None):
	# First we need to correct for the fact that we may lose some digits of accuracy
	# if the integer part of the number is big.
	precision = accuracy + max(int(log(number.n(digits=1))), 1)
	if degree is None: degree = algebraic_degree(number)  # If not given, assume that the degree of the number field is the degree of this number.
	A = algebraic_approximation_from_string(str(number.n(digits=precision)), degree, log_height_algebraic_type(number))
	assert(A.interval.accuracy >= accuracy)
	return A


def Perron_Frobenius_eigen(matrix, vector=None):
	# Assumes that matrix is Perron-Frobenius and so has a unique real eigenvalue of largest
	# magnitude. If not an AssumptionError is thrown.
	M = Matrix(matrix.rows)
	eigenvalue = max(M.eigenvalues())
	N = M - eigenvalue
	try:
		[eigenvector] = N.right_kernel().basis()
	except ValueError:
		raise AssumptionError('Matrix is not Perron-Frobenius.')
	
	s = sum(eigenvector)
	if s == 0:
		raise AssumptionError('Matrix is not Perron-Frobenius.')
	
	return [simplify_algebraic_type(x / s) for x in eigenvector], eigenvalue
