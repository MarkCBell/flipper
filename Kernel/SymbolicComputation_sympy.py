
from math import log10 as log

import sympy
from sympy.core.expr import Expr

from Flipper.Kernel.Error import AssumptionError

_name = 'sympy'

algebraic_type = Expr

def simplify_algebraic_type(x):
	return sympy.simplify(x)

def string_algebraic_type(x):
	return '%0.4f' % float(x)

def Perron_Frobenius_eigen(matrix):
	# Assumes that matrix is Perron-Frobenius and so has a unique real eigenvalue of largest
	# magnitude. If not an AssumptionError is thrown.
	M = sympy.Matrix(matrix.rows)
	eigenvalue = max(M.eigenvals())
	N = M - eigenvalue * sympy.eye(matrix.width)
	try:
		[eigenvector] = N.nullspace(simplify=True)
	except ValueError:
		raise AssumptionError('Matrix is not Perron-Frobenius.')
	
	return [simplify_algebraic_type(x) for x in eigenvector], eigenvalue

def minimal_polynomial_coefficients(number):
	return tuple(int(x) for x in sympy.Poly(sympy.minpoly(number)).all_coeffs()[::-1])

def symbolic_approximate(number, accuracy):
	# First we need to correct for the fact that we may lose some digits of accuracy
	# if the integer part of the number is big.
	precision = accuracy + max(int(log(sympy.N(number, n=1))), 1)
	return str(sympy.N(number, n=precision))
