
''' A module for performing symbolic calculations using sage. '''

import flipper

from sage.all import Matrix, Polyhedron, lcm, NumberField, AA
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

def directed_eigenvector(action_matrix, condition_matrix, vector):
	''' Return an interesting eigenvector of action_matrix which lives inside of the cone C, defined by condition_matrix.
	
	This version is perfect, that is a ComputationError is raised if and only if
	C contains no interesting eigenvectors.
	
	An eigenvector is interesting if its corresponding eigenvalue is: real, >= 1 and irrational.
	Raises a ComputationError if it cannot find an interesting vectors in C.
	
	vector is guranteed to live inside of C.
	
	Assumes that C contains at most one eigenvector and no rational eigenvectors. '''
	
	M = Matrix(action_matrix.rows)
	# We have to check ALL eigenspaces. So we do it in order of decreasing real part.
	for eigenvalue in sorted(M.eigenvalues(), reverse=True, key=lambda z: complex(z).real):
		# Only bother checking the real eigenspaces.
		if eigenvalue.imag() == 0 and eigenvalue >= 1:
			[lam] = NumberField(eigenvalue.minpoly(), 'L', embedding=eigenvalue.n()).gens()
			right_kernel = (M-lam).right_kernel().basis()
			
			if len(right_kernel) == 1:  # If rank(kernel) == 1.
				[eigenvector] = right_kernel
				if condition_matrix.nonnegative_image(eigenvector):
					eigenvalue_coefficients = minpoly_coefficients(eigenvalue)
					
					scale = abs(lcm([x.denominator() for entry in eigenvector for x in entry.polynomial().coeffs()]))
					eigenvector_rescaled_coefficients = [[int(scale * x) for x in entry.polynomial().coeffs()] for entry in eigenvector]
					
					d = sum(abs(x) for x in eigenvalue_coefficients)
					N = flipper.kernel.create_number_field(eigenvalue_coefficients, approximate(eigenvalue, d))
					return N.lmbda, [N.element(entry) for entry in eigenvector_rescaled_coefficients]
			else:
				eqns = [[0] + list(row) for row in (M - eigenvalue)]
				ieqs = [[0] + list(row) for row in condition_matrix]
				
				# This is really slow.
				P = Polyhedron(eqns=eqns, ieqs=ieqs)
				# If dim(P) == 1 then an extremal vertex of the cone is an eigenvalue.
				# As this is a rational vector it must correspond to a fixed curve.
				# If dim(P)  > 1 then there is a high dimensional invariant subspace.
				if P.dim() > 0:
					raise flipper.AssumptionError('Subspace is reducible.')
	
	raise flipper.ComputationError('No interesting eigenvalues in cell.')

def directed_eigenvector2(matrix, vector):
	''' Return the dominant eigenvalue of matrix and the projection of vector to its corresponding eigenspace.
	
	Assumes (and checks) that the dominant eigenvalue is real. '''
	
	M = Matrix(matrix.rows)
	eigenvalue = max(M.eigenvalues(), key=lambda z: (z.abs(), z.real()))
	if eigenvalue.imag() != 0:  # Make sure that the eigenvalue that we've got is real.
		raise flipper.AssumptionError('Largest eigenvalue is not real.')
	
	# !?! Check this 100.
	flipper_eigenvalue = flipper.kernel.create_algebraic_number(minpoly_coefficients(eigenvalue), str(eigenvalue.n(digits=100)))
	
	[lam] = NumberField(eigenvalue.minpoly(), 'L', embedding=eigenvalue.n()).gens()
	eigenvector = project(vector, (M - lam).right_kernel().basis())
	norm = sum(eigenvector)
	eigenvector = [entry / norm for entry in eigenvector]
	
	# and check this 100 too.
	flipper_eigenvector = [flipper.kernel.create_algebraic_number(minpoly_coefficients(entry), approximate(entry, 100)) for entry in eigenvector]
	
	return flipper_eigenvalue, flipper_eigenvector

