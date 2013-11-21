# Exact symbolic calculations using types representing algebraic numbers. This is used to:
#	compute the stable lamination exactly.
#	compute splitting sequences.

# This module provides two functions which return types storing algebraic numbers.
#	1) compute_eigen(matrix):
#		Given a matrix (of type Matrix.Matrix) this must returns the pair (eigenvector, eigenvalue) with largest eigenvalue for matrix.
#		The eigenvalue must be an algebraic number and the eigenvector must be a list of algebraic numbers.
#	2) simplify(x):
#		Given a type representing an algebraic number this must return that algebraic number in a standard form.

# Notes: 
#	1) We do not actually care what type is used to represent the algebraic numbers however we require that they implement;
#		addition, subtraction, division, comparison, equality (+, -, /, <, ==).
#		both with integers and other algebraic numbers of the same type.
#		Some debugging code (currently commented out) may try and print out floating point representations by using float().
#	2) If we were sensible / careful / willing to take a constant multiplicative slowdown we could probably replace the division 
#		requirement by multiplication.
#	3) We actually provide interfaces to several different libraries such as sympy and sage.

# We select a library interface here. we first try sage, then sympy and finally just load the dummy library.
try:
	from Symbolic_Computation_sage import simplify, compute_eigen, _name # Sage
except ImportError:
	try:
		from Symbolic_Computation_sympy import simplify, compute_eigen, _name  # Sympy
	except ImportError:
		from Symbolic_Computation_dummy import simplify, compute_eigen, _name  # Dummy

def compute_powers(a, b):
	# Given (real > 1) algebraic numbers a == c^m and b == c^n where c is another algebraic number and m & n are coprime 
	# integers returns m, n. This uses a variant of the Euclidean algorithm and can probably be done smarter.
	
	a, b = simplify(a), simplify(b)
	if a == b:
		return (1, 1)
	elif a > b:
		m2, n2 = compute_powers(a / b, b)
		return (m2 + n2, n2)
	else:
		m2, n2 = compute_powers(a, b / a)
		return (m2, n2 + m2)
