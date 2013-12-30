
# Exact symbolic calculations using types representing algebraic numbers. This is used to:
#	compute the stable lamination exactly.
#	compute splitting sequences.
#	Construct Algebric_Approximations.

# This module provides 8 things to do with algebraic numbers.
#	1) algebraic_type:
#		The type used to represent algebraic numbers.
#	2) algebraic_string(x):
#		Given an algebraic_type this must return that number as a nice string, otherwise return str(x).
#	3) algebraic_simplify(x):
#		Given an algebraic_type this must return that number in a standard form, otherwise return x.
#	4) Perron_Frobenius_eigen(matrix):
#		Given a Perron-Frobenius matrix (of type Matrix.Matrix) this must returns the unique pair (eigenvector, eigenvalue) with largest eigenvalue.
#		If the matrix is not Perron-Frobenius an AsumptionError should be thrown.
#		The eigenvalue must be an algebraic_type and the eigenvector must be a list of algebraic_types.
#	5) minimal_polynomial_coefficients(number):
#		Returns the coefficients of the minimal polynomial of an algebraic_type as a tuple of integers.
#	6) symbolic_approximate(number, accuracy):
#		Returns a string containing number to accuracy digits of accuracy.
#	7) symbolic_degree(number):
#		Returns the degree of an algebraic number.
#	8) symbolic_height(number):
#		Returns the height of an algebraic number.

# Notes: 
#	1) We do not actually care what algebraic_type is but it must implement;
#		addition, subtraction, division, comparison, equality (+, -, /, <, ==).
#		both with integers and other algebraic_types.
#	2) If we were sensible / careful / willing to take a constant multiplicative slowdown we could probably replace the division 
#		requirement by multiplication.
#	3) We actually provide interfaces to several different libraries such as sympy and sage. Currently Sage is the best by a _large_ margin.

# We select a library interface here. We first try sage, then sympy and finally just load the dummy library which can't do anything.
# To use your own library add its script to this folder and duplicate one of the blocks below. If must provide the following:
#	1) algebraic_type:
#		Same as 1) above.
#	2) simplify_algebraic_type
#		Given an algebraic_type this must return that number in a standard form.
#	3) string_algebraic_type
#		Given an algebraic_type this must return that number as a nice string.
#	4) Perron_Frobenius_eigen
#		Same as 4) above.
#	5) minimal_polynomial_coefficients  
#		Same as 5) above.
#	6) symbolic_approximate
#		Same as 6) above.
#	7) _name:
#		A string containing the name of the library being used. Useful for debugging.

_name = None
if _name is None:
	try:
		from Flipper.Kernel.SymbolicComputation_sage import algebraic_type, simplify_algebraic_type, string_algebraic_type, Perron_Frobenius_eigen, minimal_polynomial_coefficients, symbolic_approximate, _name
	except ImportError:
		pass

if _name is None:
	try:
		from Flipper.Kernel.SymbolicComputation_sympy import algebraic_type, simplify_algebraic_type, string_algebraic_type, Perron_Frobenius_eigen, minimal_polynomial_coefficients, symbolic_approximate, _name
	except ImportError:
		pass

if _name is None:
	try:
		from Flipper.Kernel.SymbolicComputation_dummy import algebraic_type, simplify_algebraic_type, string_algebraic_type, Perron_Frobenius_eigen, minimal_polynomial_coefficients, symbolic_approximate, _name
	except ImportError:
		pass

#############################################################################
# We also build some helper functions using these.

def algebraic_simplify(x):
	if isinstance(x, algebraic_type):
		return simplify_algebraic_type(x)
	else:
		return x

def algebraic_string(x):
	if isinstance(x, algebraic_type):
		return string_algebraic_type(x)
	else:
		return str(x)

def symbolic_degree(number):
	if isinstance(number, algebraic_type):
		return len(minimal_polynomial_coefficients(number)) - 1
	elif isinstance(number, int):
		return 1
	else:
		return NotImplemented

def symbolic_height(number):
	if isinstance(number, algebraic_type):
		return max(abs(x) for x in minimal_polynomial_coefficients(number))
	elif isinstance(number, int):
		return max(abs(number), 1)
	else:
		return NotImplemented

def compute_powers(a, b):
	# Given (real > 1) algebraic numbers a == c^m and b == c^n where c is another algebraic number and m & n are coprime 
	# integers returns m, n. This uses a variant of the Euclidean algorithm and can probably be done smarter.
	
	a, b = algebraic_simplify(a), algebraic_simplify(b)
	if a == b:
		return (1, 1)
	elif a > b:
		m2, n2 = compute_powers(a / b, b)
		return (m2 + n2, n2)
	else:
		m2, n2 = compute_powers(a, b / a)
		return (m2, n2 + m2)

