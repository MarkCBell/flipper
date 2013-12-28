
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
#		Given an algebraic_type this must return that number in a standard form, otherwise return int(x).
#	4) Perron_Frobenius_eigen(matrix):
#		Given a Perron-Frobenius matrix (of type Matrix.Matrix) this must returns the unique pair (eigenvector, eigenvalue) with largest eigenvalue.
#		If the matrix is not Perron-Frobenius an AsumptionError should be thrown.
#		The eigenvalue must be an algebraic_type and the eigenvector must be a list of algebraic_types.
#	5) minimal_polynomial_coefficients(number):
#		Returns the coefficients of the minimal polynomial of an algebraic_type as a tuple of integers.
#	6) symbolic_approximate(number, precision):
#		Returns a string containing number to precision digits of accuracy.
#	7) degree(number):
#		Returns the degree of an algebraic number.
#	8) height(number):
#		Returns the height of an algebraic number.

# Notes: 
#	1) We do not actually care what algebraic_type is but it must implement;
#		addition, subtraction, division, comparison, equality (+, -, /, <, ==).
#		both with integers and other algebraic_types.
#	2) If we were sensible / careful / willing to take a constant multiplicative slowdown we could probably replace the division 
#		requirement by multiplication.
#	3) We actually provide interfaces to several different libraries such as sympy and sage. Currently Sage is the best by a _large_ margin.

# We select a library interface here. We first try sage, then sympy and finally just load the dummy library which can't do anything.
# To use your own library add its script to this folder and add that scripts name to the list below.

possible_libraries = [
	'Flipper.Kernel.SymbolicComputation_sage',
	'Flipper.Kernel.SymbolicComputation_sympy',
	'Flipper.Kernel.SymbolicComputation_dummy']

required_imports = ['algebraic_type', 'simplify_algebraic_type', 'string_algebraic_type', 'Perron_Frobenius_eigen', 'minimal_polynomial_coefficients', 'symbolic_approximate', '_name']
def import_library(possible_libraries, required_imports):
	for library in possible_libraries:
		try:
			return __import__(library, fromlist=required_imports)
		except ImportError:
			pass

library = import_library(possible_libraries, required_imports)
algebraic_type = library.algebraic_type
simplify_algebraic_type = library.simplify_algebraic_type
string_algebraic_type = library.string_algebraic_type
Perron_Frobenius_eigen = library.Perron_Frobenius_eigen
minimal_polynomial_coefficients = library.minimal_polynomial_coefficients
symbolic_approximate = library.symbolic_approximate
_name = library._name

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

def symbolic_degree(x):
	return len(minimal_polynomial_coefficients(x)) - 1

def symbolic_height(x):
	return max(abs(x) for x in minimal_polynomial_coefficients(x))

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

