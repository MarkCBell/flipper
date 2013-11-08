# Exact symbolic calculations using types representing algebraic numbers. This is used to:
#	compute the stable lamination exactly.
#	compute splitting sequences.

import sympy

# This module provides two functions which return types storing algebraic numbers.
#	1) compute_eigen(matrix):
#		Given a matrix (of type Matrix.Matrix) this must returns the pair (eigenvector, eigenvalue) with largest eigenvalue for matrix.
#		The eigenvalue must be an algebraic number and the eigenvector must be a list of algebraic numbers.
#	2) simplify(x):
#		Given a type representing an algebraic number this must return that algebraic number in a standard form.
#
# Notes: 
#	1) We do not care what type is used to represent the algebraic numbers however we require that they implement;
#		addition, subtraction, division, comparison, equality (+, -, /, <, ==).
#		both with integers and other algebraic numbers of the same type.
#	2) Currently we use sympy which represents algebraic numbers by sympy.core.add.Add classes.
#	3) If we were sensible / careful / willing to take a constant multiplicative slowdown we could probably replace the division requirement by multiplication.

def compute_eigen(matrix):
	# We use sympy.Matrix.eigenvects() and so this can be incredibly slow (hundreds of seconds).
	# We use sympy.Matrix.eigenvals() and sympy.Matix.nullspace and so this can be quite slow (dozens of seconds).
	M = sympy.Matrix(matrix.rows)
	
	eigenvalue = max(M.eigenvals())
	N = M - eigenvalue * sympy.eye(matrix.width)
	eigenvector = N.nullspace(simplify=True)[0]
	
	return [simplify(x) for x in eigenvector], eigenvalue
	
	# eigenvalue, multiplicity, [eigenvector] = max(M.eigenvects(), key=lambda v: v[0])  # Get the (eigenvalue, multiplicity, [eigenvectors]) corresponding to the largest eigenvalue.
	# return [simplify(x) for x in eigenvector], eigenvalue

def simplify(x):
	return x.simplify()
