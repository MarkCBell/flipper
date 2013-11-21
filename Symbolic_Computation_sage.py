
from sage.all import Matrix

_name = 'sage'

def simplify(x):
	x.simplify()
	return x

def compute_eigen(matrix):
	M = Matrix(matrix.rows)
	eigenvalue = max(M.eigenvalues())
	N = M - eigenvalue
	[eigenvector] = N.right_kernel().basis()
	
	return [simplify(x) for x in eigenvector], eigenvalue
