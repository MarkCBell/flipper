
from sage.all import Matrix, lcm, NumberField
from flipper.kernel.symboliccomputation_dummy import project

import flipper
# !! Eventually change.

def minpoly_coefficients(algebraic_number):
	polynomial = algebraic_number.minpoly()
	scale = abs(lcm([x.denominator() for x in polynomial.coeffs()]))
	return [int(scale * x) for x in polynomial.coeffs()]

def PF_eigen(matrix, vector):
	dot = flipper.kernel.matrix.dot
	
	M = Matrix(matrix.rows)
	eigenvalue = max(M.eigenvalues(), key=lambda z: (z.abs(), z.real()))
	# Make sure that the eigenvalue that we've got is real.
	if eigenvalue.imag() != 0:
		raise flipper.AssumptionError('Largest eigenvalue is not real.')
	
	eigenvalue_coefficients = minpoly_coefficients(eigenvalue)
	
	[lam] = NumberField(eigenvalue.minpoly(), 'L', embedding=eigenvalue.n()).gens()
	eigenvector = project(vector, (M - lam).right_kernel().basis())
	
	eigenvector_coefficients = [list(entry.polynomial().coeffs()) for entry in eigenvector]
	scale = abs(lcm([x.denominator() for entry in eigenvector for x in entry.polynomial().coeffs()]))
	eigenvector_rescaled_coefficients = [[int(scale * x) for x in entry.polynomial().coeffs()] for entry in eigenvector]
	
	eigenvalue_polynomial = flipper.kernel.Polynomial(eigenvalue_coefficients)
	d = sum(abs(x) for x in eigenvalue_polynomial)
	N = flipper.kernel.number_field_helper(eigenvalue_coefficients, str(eigenvalue.n(digits=d)))
	return N.lmbda, [N.element(entry) for entry in eigenvector_rescaled_coefficients]

def PF_eigen2(matrix, vector):
	M = Matrix(matrix.rows)
	
	eigenvalue = max(M.eigenvalues(), key=lambda z: (z.abs(), z.real()))
	# Make sure that the eigenvalue that we've got is real.
	if eigenvalue.imag() != 0:
		raise flipper.AssumptionError('Largest eigenvalue is not real.')
	
	# !?! Check this 100.
	flipper_eigenvalue = flipper.kernel.algebraic_number_helper(minpoly_coefficients(eigenvalue), str(eigenvalue.n(digits=100)))
	
	K = NumberField(eigenvalue.minpoly(), 'x')
	[lam] = NumberField(eigenvalue.minpoly(), 'L', embedding=eigenvalue.n()).gens()
	eigenvector = project(vector, (M - lam).right_kernel().basis())
	norm = sum(eigenvector)
	eigenvector = [entry / norm for entry in eigenvector]
	
	flipper_eigenvector = [algebraic_ring_element_from_info(minpoly_coefficients(entry), str(entry.n(digits=100))) for entry in eigenvector]  # Check.
	
	return flipper_eigenvalue, flipper_eigenvector

