
''' A module for performing symbolic calculations using sage. '''

import flipper

from sage.all import Matrix, lcm, NumberField
from flipper.kernel.symboliccomputation_dummy import project

def minpoly_coefficients(number):
	''' Return the list of coefficients of the minimal polynomial of the given number. '''
	
	polynomial = number.minpoly()
	scale = abs(lcm([x.denominator() for x in polynomial.coeffs()]))
	return [int(scale * x) for x in polynomial.coeffs()]

def approximate(number, accuracy):
	''' Return a string approximating the given number to the given accuracy. '''
	
	s = str(number.n(digits=1))
	i, _ = s.split('.') if '.' in s else (s, '')
	s2 = str(number.n(digits=len(i)+accuracy))
	i2, r2 = s2.split('.') if '.' in s2 else (s2, '')
	return i2 + '.' + r2[:accuracy]

def perron_frobenius_eigen(matrix, vector):
	''' Return the dominant eigenvalue of matrix and the projection of vector to its corresponding eigenspace.
	
	Assumes (and checks) that the dominant eigenvalue is real. '''
	
	M = Matrix(matrix.rows)
	eigenvalue = max(M.eigenvalues(), key=lambda z: (z.abs(), z.real()))
	if eigenvalue.imag() != 0:  # Make sure that the eigenvalue that we've got is real.
		raise flipper.AssumptionError('Largest eigenvalue is not real.')
	
	eigenvalue_coefficients = minpoly_coefficients(eigenvalue)
	
	[lam] = NumberField(eigenvalue.minpoly(), 'L', embedding=eigenvalue.n()).gens()
	eigenvector = project(vector, (M - lam).right_kernel().basis())
	
	scale = abs(lcm([x.denominator() for entry in eigenvector for x in entry.polynomial().coeffs()]))
	eigenvector_rescaled_coefficients = [[int(scale * x) for x in entry.polynomial().coeffs()] for entry in eigenvector]
	
	eigenvalue_polynomial = flipper.kernel.Polynomial(eigenvalue_coefficients)
	d = sum(abs(x) for x in eigenvalue_polynomial)
	N = flipper.kernel.number_field(eigenvalue_coefficients, approximate(eigenvalue, d))
	return N.lmbda, [N.element(entry) for entry in eigenvector_rescaled_coefficients]

def perron_frobenius_eigen2(matrix, vector):
	''' Return the dominant eigenvalue of matrix and the projection of vector to its corresponding eigenspace.
	
	Assumes (and checks) that the dominant eigenvalue is real. '''
	
	M = Matrix(matrix.rows)
	eigenvalue = max(M.eigenvalues(), key=lambda z: (z.abs(), z.real()))
	if eigenvalue.imag() != 0:  # Make sure that the eigenvalue that we've got is real.
		raise flipper.AssumptionError('Largest eigenvalue is not real.')
	
	# !?! Check this 100.
	flipper_eigenvalue = flipper.kernel.algebraic_number(minpoly_coefficients(eigenvalue), str(eigenvalue.n(digits=100)))
	
	[lam] = NumberField(eigenvalue.minpoly(), 'L', embedding=eigenvalue.n()).gens()
	eigenvector = project(vector, (M - lam).right_kernel().basis())
	norm = sum(eigenvector)
	eigenvector = [entry / norm for entry in eigenvector]
	
	# and check this 100 too.
	flipper_eigenvector = [flipper.kernel.algebraic_number(minpoly_coefficients(entry), approximate(entry, 100)) for entry in eigenvector]
	
	return flipper_eigenvalue, flipper_eigenvector

