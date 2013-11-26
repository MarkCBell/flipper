
from Error import AssumptionError
from sage.all import Matrix

_name = 'sage'

def simplify(x):
	x.simplify()
	return x

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
	
	return [simplify(x) for x in eigenvector], eigenvalue

def minimal_polynomial_coefficients(number):
	return tuple(number.minpoly().coefficients())