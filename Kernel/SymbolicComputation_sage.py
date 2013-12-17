
from sage.all import Matrix
from sage.rings.qqbar import AlgebraicNumber
try:
	from Flipper.Kernel.Error import AssumptionError
except ImportError:
	from Error import AssumptionError

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
	return tuple(number.minpoly().coefficients())