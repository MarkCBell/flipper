
from sage.all import Matrix, lcm, NumberField
from flipper.kernel.symboliccomputation_dummy import gram_schmidt

import flipper

symbolic_libaray_name = 'sage'

def PF_eigen(matrix, vector):
	dot = flipper.kernel.matrix.dot
	
	M = Matrix(matrix.rows)
	eigenvalue = max(M.eigenvalues(), key=abs)
	# Make sure that the eigenvalue that we've got is real.
	if eigenvalue.imag() != 0:
		raise flipper.AssumptionError('Largest eigenvalue is not real.')
	
	polynomial = eigenvalue.minpoly()
	scale = abs(lcm([x.denominator() for x in polynomial.coeffs()]))
	eigenvalue_coefficients = [int(scale * x) for x in polynomial.coeffs()]
	
	K = NumberField(polynomial, 'L', embedding=eigenvalue.n())
	[lam] = K.gens()
	
	orthogonal_kernel_basis = gram_schmidt((M - lam).right_kernel_matrix().rows())
	row_lengths = [dot(row, row) for row in orthogonal_kernel_basis] 
	linear_combination = [dot(vector, row) / row_length for row, row_length in zip(orthogonal_kernel_basis, row_lengths)]
	eigenvector = [sum(a * n[i] for a, n in zip(linear_combination, orthogonal_kernel_basis)) for i in range(matrix.width)]
	
	scale2 = abs(lcm([x.denominator() for v in eigenvector for x in v.polynomial().coeffs()]))
	eigenvector_coefficients = [[int(scale2 * x) for x in v.polynomial().coeffs()] for v in eigenvector]
	
	return eigenvalue_coefficients, eigenvector_coefficients

