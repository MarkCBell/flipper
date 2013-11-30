
import sympy
from sympy.core.add import Add
try:
	from Source.Error import AssumptionError
except ImportError:
	from Error import AssumptionError

_name = 'sympy'

algebraic_type = Add

def simplify(x):
	return x.simplify()

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
	
	return [simplify(x) for x in eigenvector], eigenvalue

def minimal_polynomial_coefficients(number):
	return tuple(sympy.Poly(sympy.minpoly(number)).all_coeffs())