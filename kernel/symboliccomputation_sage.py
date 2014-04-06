
from sage.all import Matrix, lcm, NumberField, QQ
from sage.rings.number_field.number_field import NumberField_generic

import Flipper

symbolic_libaray_name = 'sage'

def gram_schmidt(rows):
	dot = Flipper.kernel.matrix.dot
	for i in range(len(rows)):
		for j in range(i):
			a = dot(rows[i], rows[j])
			b = dot(rows[j], rows[j])
			rows[i] = [b * x - a * y for x, y in zip(rows[i], rows[j])]
	return rows

def PF_eigen(matrix, vector):
	dot = Flipper.kernel.matrix.dot
	
	M = Matrix(matrix.rows)
	eigenvalue = max(M.eigenvalues(), key=abs)
	
	# We need to be a little careful, for some reason sage needs a variable name if eigenvalue is a rational.
	polynomial = eigenvalue.minpoly()  # if eigenvalue not in QQ else eigenvalue.minpoly('x')
	scale = abs(lcm([x.denominator() for x in polynomial.coeffs()]))
	eigenvalue_coefficients = [int(scale * x) for x in polynomial.coeffs()]
	
	K = NumberField(polynomial, 'L', embedding=eigenvalue.n())
	[lam] = K.gens()
	
	orthogon_kernel_basis = gram_schmidt((M - lam).right_kernel_matrix().rows())
	row_lengths = [dot(row, row) for row in orthogon_kernel_basis] 
	linear_combination = [dot(vector, row) / row_length for row, row_length in zip(orthogon_kernel_basis, row_lengths)]
	eigenvector = [sum(a * n[i] for a, n in zip(linear_combination, orthogon_kernel_basis)) for i in range(matrix.width)]
	
	scale2 = abs(lcm([x.denominator() for v in eigenvector for x in v.polynomial().coeffs()]))
	eigenvector_coefficients = [[int(scale2 * x) for x in v.polynomial().coeffs()] for v in eigenvector]
	
	return eigenvalue_coefficients, eigenvector_coefficients

