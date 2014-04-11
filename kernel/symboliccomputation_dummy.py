
from functools import reduce

import flipper

symbolic_libaray_name = 'dummy'

# This is a duplicate of symboliccomputation_sage.
def gram_schmidt(rows):
	for i in range(len(rows)):
		for j in range(i):
			a = flipper.kernel.matrix.dot(rows[i], rows[j])
			b = flipper.kernel.matrix.dot(rows[j], rows[j])
			rows[i] = [b * x - a * y for x, y in zip(rows[i], rows[j])]
	return rows

def PF_eigen(matrix, vector):
	eigenvalue_polynomial = matrix.char_poly().simplify()  # This may not be irreducible.
	eigenvalue_coefficients = eigenvalue_polynomial.coefficients
	
	# We will calculate the eigenvector ourselves.
	N = flipper.kernel.NumberField(eigenvalue_polynomial)
	orthogonal_kernel_basis = (matrix - N.lmbda).kernel()  # Sage is much better at this than us for large matrices.
	dim_ker = len(orthogonal_kernel_basis)
	row_lengths = [dot(row, row) for row in orthogon_kernel_basis] 
	product_lengths = [reduce(lambda x, y: x*y, [row_lengths[j] for j in range(dim_ker) if j != i], 1) for i in range(dim_ker)]
	linear_combination = [dot(vector, row) * product_length for row, product_length in zip(orthogon_kernel_basis, product_lengths)]
	eigenvector = [sum(a * n[i] for a, n in zip(linear_combination, orthogon_kernel_basis)) for i in range(matrix.width)]
	eigenvector_coefficients = [x.linear_combination for x in eigenvector]
	
	return eigenvalue_coefficients, eigenvector_coefficients

