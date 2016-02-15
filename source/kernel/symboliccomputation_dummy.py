
''' A module for performing symbolic calculations using Python. '''

import flipper
from math import log10 as log

def gram_schmidt(basis):
	''' Return an orthonormal basis for the subspace generated by basis. '''
	
	basis = [list(row) for row in basis]
	
	dot = flipper.kernel.dot
	for i in range(len(basis)):
		for j in range(i):
			a, b = dot(basis[i], basis[j]), dot(basis[j], basis[j])
			basis[i] = [b * x - a * y for x, y in zip(basis[i], basis[j])]
	return basis

def project(vector, basis):
	''' Return the projection of vector to the subspace generated by basis. '''
	
	dot = flipper.kernel.dot
	orthogonal_basis = gram_schmidt(basis)
	linear_combination = [dot(vector, row) / dot(row, row) for row in orthogonal_basis]
	return [sum(a * b[i] for a, b in zip(linear_combination, orthogonal_basis)) for i in range(len(vector))]

def directed_eigenvector(action_matrix, condition_matrix):
	''' Return an interesting eigenvector of action_matrix which lives inside of the cone C, defined by condition_matrix.
	
	This version is imperfect and is NOT as good as the sage version. Examples are
	known where this function raises a ComputationError while Sage correctly finds
	a rational eigenvector and so raises an AssumptionError.
	
	An eigenvector is interesting if its corresponding eigenvalue is: real, >= 1 and irrational.
	Raises a ComputationError if it cannot find an interesting vectors in C.
	
	Assumes that C contains at most one interesting eigenvector. '''
	
	dot = flipper.kernel.dot
	# Getting the square free representative makes this faster.
	eigenvalues = [eigenvalue.irreducible_representation() for eigenvalue in action_matrix.characteristic_polynomial().square_free().real_roots() if eigenvalue > 1]
	
	for eigenvalue in sorted(eigenvalues, reverse=True):
		# We will calculate the eigenvector ourselves.
		N = flipper.kernel.NumberField(eigenvalue)
		kernel_basis = (action_matrix - N.lmbda).kernel()  # Sage is much better at this than us for large matrices.
		if len(kernel_basis) == 1:  # If rank(kernel) == 1.
			[eigenvector] = kernel_basis
			
			# We might need to flip the eigenvector if we have the inverse basis.
			if sum(eigenvector) < 0: eigenvector = [-x for x in eigenvector]
			
			if flipper.kernel.matrix.nonnegative(eigenvector) and condition_matrix.nonnegative_image(eigenvector):
				return N.lmbda, eigenvector
		else:
			# We cannot handle the case where the rank(kernel) > 1 (yet). This requires solving some linear programming
			# problem over a number field which is likely to be very slow anyway.
			pass
	
	raise flipper.ComputationError('No interesting eigenvalues in cell.')

