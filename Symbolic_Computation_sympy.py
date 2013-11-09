
import sympy

def simplify(x):
	return x.simplify()

def compute_eigen(matrix):
	M = sympy.Matrix(matrix.rows)
	eigenvalue = max(M.eigenvals())
	N = M - eigenvalue * sympy.eye(matrix.width)
	[eigenvector] = N.nullspace(simplify=True)
	
	return [simplify(x) for x in eigenvector], eigenvalue
