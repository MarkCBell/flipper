
# Exact symbolic calculations using types representing algebraic numbers. This is used to:
#	compute the stable lamination exactly.
#	compute splitting sequences.

# This module provides four things to do with algebraic numbers.
#	1) algebraic_type:
#		The type used to represent algebraic numbers. We will only ever call simplify on things of this type.
#	2) simplify(x):
#		Given an algebraic_type this must return that number in a standard form.
#	3) Perron_Frobenius_eigen(matrix):
#		Given a Perron-Frobenius matrix (of type Matrix.Matrix) this must returns the unique pair (eigenvector, eigenvalue) with largest eigenvalue.
#		If the matrix is not Perron-Frobenius an AsumptionError should be thrown.
#		The eigenvalue must be an algebraic_type and the eigenvector must be a list of algebraic_types.
#	4) minimal_polynomial_coefficients(number):
#		Returns the coefficients of the minimal polynomial of an algebraic_type as a tuple of integers.

# Notes: 
#	1) We do not actually care what algebraic_type is but it must implement;
#		addition, subtraction, division, comparison, equality (+, -, /, <, ==).
#		both with integers and other algebraic_types.
#	2) Some debugging code (currently commented out) may try and print out floating point representations by using float(algebraic_type).
#	3) If we were sensible / careful / willing to take a constant multiplicative slowdown we could probably replace the division 
#		requirement by multiplication.
#	4) We actually provide interfaces to several different libraries such as sympy and sage. Currently Sage is the best by a _large_ margin.

# We select a library interface here. we first try sage, then sympy and finally just load the dummy library which can't do anything.
try:
	from Source.Symbolic_Computation_sage import algebraic_type, simplify, Perron_Frobenius_eigen, minimal_polynomial_coefficients, _name  # Sage
except ImportError:
	try:
		from Source.Symbolic_Computation_sympy import algebraic_type, simplify, Perron_Frobenius_eigen, minimal_polynomial_coefficients, _name  # Sympy
	except ImportError:
		try:
			from Source.Symbolic_Computation_dummy import algebraic_type, simplify, Perron_Frobenius_eigen, minimal_polynomial_coefficients, _name  # Dummy
		except:
			try:
				from Symbolic_Computation_sage import algebraic_type, simplify, Perron_Frobenius_eigen, minimal_polynomial_coefficients, _name  # Sage
			except ImportError:
				try:
					from Symbolic_Computation_sympy import algebraic_type, simplify, Perron_Frobenius_eigen, minimal_polynomial_coefficients, _name  # Sympy
				except ImportError:
					from Symbolic_Computation_dummy import algebraic_type, simplify, Perron_Frobenius_eigen, minimal_polynomial_coefficients, _name  # Dummy

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
