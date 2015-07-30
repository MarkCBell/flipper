
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

def directed_eigenvector(action_matrix, condition_matrix, vector):
	''' Return an interesting eigenvector of action_matrix which lives inside of the cone C, defined by condition_matrix.
	
	This version is imperfect and is NOT as good as the sage version. Examples are
	known where this function raises a ComputationError while Sage correctly finds
	a rational eigenvector and so raises an AssumptionError.
	
	An eigenvector is interesting if its corresponding eigenvalue is: real, >= 1 and irrational.
	Raises a ComputationError if it cannot find an interesting vectors in C.
	
	vector is guranteed to live inside of C.
	
	Assumes that C contains at most one interesting eigenvector. '''
	
	dot = flipper.kernel.dot
	# Getting the square free representative makes this faster.
	eigenvalues = [eigenvalue for eigenvalue in action_matrix.characteristic_polynomial().square_free().real_roots() if eigenvalue > 1]
	
	k = max(flipper.kernel.height_int(entry) for row in action_matrix for entry in row)
	n = action_matrix.width  # This bounds the degree of an eigenvalue.
	height = n * k + n * log(n) + 2 * n  # This bounds the height of an eigenvalue.
	precision = int(2 * n * height + 1)  # Note that we need the 2* here as sorted will compare by subtraction.
	for eigenvalue in sorted(eigenvalues, reverse=True, key=lambda x: x.algebraic_approximation(precision)):
		# We will calculate the eigenvector ourselves.
		N = flipper.kernel.NumberField(eigenvalue)
		kernel_basis = (action_matrix - N.lmbda).kernel()  # Sage is much better at this than us for large matrices.
		# Can't do division so can't do: eigenvector = project(vector, kernel_basis)
		row_lengths = [dot(row, row) for row in kernel_basis]
		product_lengths = [flipper.kernel.product([row_lengths[j] for j in range(len(kernel_basis)) if j != i]) for i in range(len(kernel_basis))]
		linear_combination = [dot(vector, row) * product_length for row, product_length in zip(kernel_basis, product_lengths)]
		
		eigenvector = [sum(a * n[i] for a, n in zip(linear_combination, kernel_basis)) for i in range(action_matrix.width)]
		
		if condition_matrix.nonnegative_image(eigenvector):
			return N.lmbda, eigenvector
	
	raise flipper.ComputationError('No interesting eigenvalues in cell.')

