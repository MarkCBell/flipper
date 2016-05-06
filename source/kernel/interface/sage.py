
''' A module for interfacing with Sage. '''

from __future__ import absolute_import

import flipper

from sage.all import Matrix, NumberField, lcm

def directed_eigenvector(action_matrix, condition_matrix):
	''' An implementation of flipper.kernel.symboliccomputation.directed_eigenvector() using Sage.
	
	See the docstring of the above function for further details. '''
	
	M = Matrix(action_matrix.rows)
	
	for polynomial, _ in M.characteristic_polynomial().factor():
		degree = int(polynomial.degree())
		
		if degree > 1:
			flipper_polynomial_roots = flipper.kernel.Polynomial([int(x) for x in polynomial.coefficients(sparse=False)]).real_roots()
			
			if len(flipper_polynomial_roots) > 0:
				# We need only consider the largest root as it has to be >=1 and bigger than all of its Galois conjugates.
				flipper_polynomial_root = max(flipper_polynomial_roots)
				
				if flipper_polynomial_root >= 1:
					# Compute the kernel:
					K = NumberField(polynomial, 'L')
					a = K.gen()
					
					kernel_basis = (M - a).right_kernel().basis()
					
					basis = [[entry.polynomial().coefficients(sparse=False) for entry in v] for v in kernel_basis]
					scale = lcm([int(coeff.denominator()) for v in basis for entry in v for coeff in entry])
					scaled_basis = [[[int(int(coeff.numerator()) * scale) / int(coeff.denominator()) for coeff in entry] for entry in v] for v in basis]
					
					N = flipper.kernel.NumberField(flipper_polynomial_root)
					flipper_basis_matrix = flipper.kernel.Matrix([[N.element(entry) for entry in v] for v in scaled_basis])
					
					if len(flipper_basis_matrix) == 1:  # If rank(kernel) == 1.
						[flipper_eigenvector] = flipper_basis_matrix
						if flipper.kernel.matrix.nonnegative(flipper_eigenvector) and condition_matrix.nonnegative_image(flipper_eigenvector):
							return N.lmbda, flipper_eigenvector
					else:
						# We could use sage.Polyhedron here.
						T = (flipper.kernel.id_matrix(condition_matrix.width).join(condition_matrix)) * flipper_basis_matrix.transpose()
						try:
							linear_combination = T.find_vector_with_nonnegative_image()
							return N.lmbda, flipper_basis_matrix.transpose()(linear_combination)
						except flipper.AssumptionError:  # Eigenspace is disjoint from the cone.
							pass
	
	raise flipper.ComputationError('No interesting eigenvalues in cell.')

