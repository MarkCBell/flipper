
from math import log10 as log

import sympy
from sympy.core.expr import Expr

from Flipper.Kernel.Error import AssumptionError, ComputationError
from Flipper.Kernel.Matrix import nonnegative_image
from Flipper.Kernel.AlgebraicApproximation import algebraic_approximation_from_string

_name = 'sympy'

algebraic_type = Expr

def simplify_algebraic_type(number):
	return sympy.simplify(number)

def string_algebraic_type(number):
	return '%0.4f' % float(number)

def minimal_polynomial_coefficients(number):
	return tuple(int(x) for x in sympy.Poly(sympy.minpoly(number)).all_coeffs()[::-1])

def hash_algebraic_type(number):
	return minimal_polynomial_coefficients(number)

def degree_algebraic_type(number):
	return len(minimal_polynomial_coefficients(number)) - 1

def log_height_algebraic_type(number):
	return log(max(abs(x) for x in minimal_polynomial_coefficients(number)))

def approximate_algebraic_type(number, accuracy, degree=None):
	# First we need to correct for the fact that we may lose some digits of accuracy
	# if the integer part of the number is big.
	precision = accuracy + max(int(log(sympy.N(number, n=1))), 1)
	if degree is None: degree = algebraic_degree(number)  # If not given, assume that the degree of the number field is the degree of this number.
	A = algebraic_approximation_from_string(str(sympy.N(number, n=precision)), degree, log_height_algebraic_type(number))
	assert(A.interval.accuracy >= accuracy)
	return A


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
	
	eigenvector = [simplify_algebraic_type(x / s) for x in eigenvector]
	
	if condition_matrix is not None:
		if not nonnegative_image(condition_matrix, eigenvector):
			raise ComputationError('Could not estimate invariant lamination.')  # If not then the curve failed to get close enough to the invariant lamination.
	
	n = matrix.width  # n = 6, log(n) ~ 0.75.
	m = matrix.bound()  # log(m) ~ 4.
	k = n * (log(2) + log(n+1) + log(m))
	H = log(n) + n**3 * (log(n) + log(m)) + n**2 * k
	
	print(m, n)
	print('eigenvalue bound prediction: %s' % k)
	print('eigenvalue bound: %s' % log_height_algebraic_type(eigenvalue))
	print('entry bound prediction: %s' % H)
	print('entry bound: %s '% max(log_height_algebraic_type(entry) for entry in eigenvector))
	
	return eigenvector, eigenvalue
