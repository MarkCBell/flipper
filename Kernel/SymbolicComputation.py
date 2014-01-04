
# Exact symbolic calculations using types representing algebraic numbers. This is used to:
#	compute the stable lamination exactly.
#	compute splitting sequences.
#	Construct Algebric_Approximations.

# This module provides seven things to do with algebraic numbers.
#	1) algebraic_type:
#		The type used to represent algebraic numbers.
#	2) algebraic_string(number):
#		Given an algebraic_type this returns that number as a nice string, otherwise return str(number).
#	3) algebraic_simplify(number):
#		Given an algebraic_type this returns that number in a standard form, otherwise return number.
#	4) algebraic_degree(number):
#		Returns the degree of number.
#	5) algebraic_height(number):
#		Returns the height of number.
#	6) algebraic_approximate(number, accuracy, degree=None):
#		Returns an AlgebraicApproximation of the number correct to the required accuracy.
#	7) Perron_Frobenius_eigen(matrix):
#		Given a Perron-Frobenius matrix (of type Matrix.Matrix) this must returns the unique pair (eigenvector, eigenvalue) with largest eigenvalue
#		and eigenvector whose sum of entries is one.
#		If the matrix is not Perron-Frobenius an AsumptionError should be thrown.
#		The eigenvalue must be an algebraic_type and the eigenvector must be a list of algebraic_types.

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
#	4) hash_algebraic_type
#		Returns a hashable object from an algebraic_type.
#	5) degree_algebraic_type
#		Same as 4) above but is only required to work for numbers of algebraic_type.
#	6) height_algebraic_type
#		Same as 5) above but is only required to work for numbers of algebraic_type.
#	7) approximate_algebraic_type
#		Same as 6) above but is only required to work for numbers of algebraic_type.
#	8) Perron_Frobenius_eigen
#		Same as 7) above.
#	9) _name:
#		A string containing the name of the library being used. Very useful for debugging.

from math import log10 as log

from Flipper.Kernel.AlgebraicApproximation import Algebraic_Approximation, algebraic_approximation_from_int, log_height_int

_name = None
# if _name is None:
	# try:
		# from Flipper.Kernel.SymbolicComputation_custom import algebraic_type, simplify_algebraic_type, string_algebraic_type, \
			# hash_algebraic_type, degree_algebraic_type, log_height_algebraic_type, approximate_algebraic_type, Perron_Frobenius_eigen, _name
	# except ImportError:
		# pass

if _name is None:
	try:
		from Flipper.Kernel.SymbolicComputation_sage import algebraic_type, simplify_algebraic_type, string_algebraic_type, \
			hash_algebraic_type, degree_algebraic_type, log_height_algebraic_type, approximate_algebraic_type, Perron_Frobenius_eigen, _name
	except ImportError:
		pass

if _name is None:
	try:
		from Flipper.Kernel.SymbolicComputation_sympy import algebraic_type, simplify_algebraic_type, string_algebraic_type, \
			hash_algebraic_type, degree_algebraic_type, log_height_algebraic_type, approximate_algebraic_type, Perron_Frobenius_eigen, _name
	except ImportError:
		pass

if _name is None:
	try:
		from Flipper.Kernel.SymbolicComputation_dummy import algebraic_type, simplify_algebraic_type, string_algebraic_type, \
			hash_algebraic_type, degree_algebraic_type, log_height_algebraic_type, approximate_algebraic_type, Perron_Frobenius_eigen, _name
	except ImportError:
		pass

#############################################################################
# We also build some helper functions using these.

def algebraic_simplify(number):
	if isinstance(number, algebraic_type):
		return simplify_algebraic_type(number)
	else:
		return number

def algebraic_string(number):
	if isinstance(number, algebraic_type):
		return string_algebraic_type(number)
	else:
		return str(number)

def algebraic_degree(number):
	if isinstance(number, algebraic_type):
		return degree_algebraic_type(number)
	elif isinstance(number, Algebraic_Approximation):
		return number.degree
	elif isinstance(number, int):
		return 1
	else:
		return NotImplemented

def algebraic_log_height(number):
	if isinstance(number, algebraic_type):
		return log_height_algebraic_type(number)
	elif isinstance(number, Algebraic_Approximation):
		return number.log_height
	elif isinstance(number, int):
		return log(max(abs(number), 1))
	else:
		return NotImplemented

def algebraic_approximate(number, accuracy, degree=None):
	if isinstance(number, algebraic_type):
		return approximate_algebraic_type(number, accuracy, degree)
	elif isinstance(number, int):
		if degree is None: degree = 1
		return algebraic_approximation_from_int(number, accuracy, degree, log_height_int(number))
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

