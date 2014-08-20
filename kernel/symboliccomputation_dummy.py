
import flipper
# !! Eventually change.

def gram_schmidt(rows):
	dot = flipper.kernel.matrix.dot
	for i in range(len(rows)):
		for j in range(i):
			a, b = dot(rows[i], rows[j]), dot(rows[j], rows[j])
			rows[i] = [b * x - a * y for x, y in zip(rows[i], rows[j])]
	return rows

def project(vector, basis):
	dot = flipper.kernel.matrix.dot
	orthogonal_basis = gram_schmidt(basis)
	linear_combination = [dot(vector, row) / dot(row, row) for row in orthogonal_basis]
	return [sum(a * b[i] for a, b in zip(linear_combination, orthogonal_basis)) for i in range(len(vector))]

def PF_eigen(matrix, vector):
	dot = flipper.kernel.matrix.dot
	eigenvalue_polynomial = matrix.char_poly().simplify()  # This may not be irreducible.
	eigenvalue_coefficients = eigenvalue_polynomial.coefficients
	
	# We will calculate the eigenvector ourselves.
	N = flipper.kernel.NumberField(eigenvalue_polynomial)
	orthogonal_kernel_basis = (matrix - N.lmbda).kernel()  # Sage is much better at this than us for large matrices.
	# eigenvector = project(vector, orthogonal_kernel_basis)
	dim_ker = len(orthogonal_kernel_basis)
	row_lengths = [dot(row, row) for row in orthogonal_kernel_basis]
	product_lengths = [flipper.kernel.product([row_lengths[j] for j in range(dim_ker) if j != i]) for i in range(dim_ker)]
	linear_combination = [dot(vector, row) * product_length for row, product_length in zip(orthogonal_kernel_basis, product_lengths)]
	eigenvector = [sum(a * n[i] for a, n in zip(linear_combination, orthogonal_kernel_basis)) for i in range(matrix.width)]
	eigenvector_coefficients = [x.linear_combination for x in eigenvector]
	
	return eigenvalue_coefficients, eigenvector_coefficients

