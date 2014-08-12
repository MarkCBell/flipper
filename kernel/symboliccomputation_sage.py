
from sage.all import Matrix, lcm, NumberField
from flipper.kernel.symboliccomputation_dummy import project

import flipper
# !! Eventually change.

def minpoly_coefficients(algebraic_number):
	polynomial = algebraic_number.minpoly()
	scale = abs(lcm([x.denominator() for x in polynomial.coeffs()]))
	return [int(scale * x) for x in polynomial.coeffs()]

def minpoly_coefficients2(algebraic_number):
	polynomial = algebraic_number.polynomial()
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
	eigenvector = project(vector, (M - lam).right_kernel_matrix().rows())
	eigenvector_coefficients = [minpoly_coefficients2(entry) for entry in eigenvector]
	
	eigenvalue_polynomial = flipper.kernel.Polynomial(eigenvalue_coefficients)
	N = flipper.kernel.NumberField(eigenvalue_polynomial)
	return N.lmbda, [N.element(v) for v in eigenvector_coefficients]

def PF_eigen2(matrix, vector):
	algebraic_ring_element_from_info = flipper.kernel.algebraicnumber.algebraic_number_from_info
	M = Matrix(matrix.rows)
	
	eigenvalue = max(M.eigenvalues(), key=lambda z: (z.abs(), z.real()))
	# Make sure that the eigenvalue that we've got is real.
	if eigenvalue.imag() != 0:
		raise flipper.AssumptionError('Largest eigenvalue is not real.')
	
	flipper_eigenvalue = algebraic_ring_element_from_info(minpoly_coefficients(eigenvalue), str(eigenvalue.n(100)))  # !?! Check this 100.
	
	eigenvector = project(vector, (M - eigenvalue).right_kernel().basis())
	flipper_eigenvector = [algebraic_ring_element_from_info(minpoly_coefficients(entry), str(entry.n(100))) for entry in eigenvector]  # Check.
	
	return flipper_eigenvalue, flipper_eigenvector

