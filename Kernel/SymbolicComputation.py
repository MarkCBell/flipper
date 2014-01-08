
# Exact symbolic calculations using types representing algebraic numbers. This is used to:
#	compute the stable lamination exactly.
#	compute splitting sequences.

# This module selects and imports the appropriate library for manipulating algebraic numbers.
# Currently there are three to choose from based on: sage, sympy and None, the last of which is
# a dummy library which can't do anything but makes sure that the imports never fail.
# Currently Sage is the best by a _large_ margin and so this is our first choice.
#
# Each library provides a class called Algebraic_Type. The main methods of which are:
#	algebraic_simplify(self, value=None)
#		Puts self into a standard form or, if given a value, returns that in standard form.
#	algebraic_hash(self)
#		Returns a sortable, hasahble value representing this algebraic number.
#	algebraic_hash_ratio(self, other)
#		Returns a sortable, hasahble value representing this algebraic number divided by other.
#	algebraic_degree(self)
#		Returns the degree of this algebraic number.
#	algebraic_log_height(self):
#		Returns the log_10 of the height of this algebraic number.
#	algebraic_approximate(self, accuracy, degree=None)
#		Returns an algebraic approximation of this algebraic number, correct to the requested accuracy.
#
# Typically each library sets these methods to work with its underlying type. Additonally, 
# Lamination.splitting_sequence(exact=True) requires that Algebraic_Type implements:
#		addition, subtraction, division, comparison and equality (+, -, /, <, ==) 
# both with integers and other Algebraic_Types.
#
# Each library also provides two functions for creating Algebraic_Types:
#	Perron_Frobenius_eigen(matrix, vector=None):
#		Given a Perron-Frobenius matrix (of type Matrix.Matrix) this must returns the unique pair 
#		(eigenvector, eigenvalue) with largest eigenvalue and eigenvector whose sum of entries is one. 
#		The eigenvalue must be an algebraic_type and the eigenvector must be a list of algebraic_types. 
#	algebraic_type_from_int(integer):
#		Returns an Algebraic_Type representing the given integer.
# and a _name variable containing a string identifying the module. This is very useful for debugging.

# You can provide your own algebraic number library so long as it provides these methods and can be cast to a string via str().

# Notes: 
#	1) If we were sensible / careful / willing to take a constant multiplicative slowdown we could probably replace the division 
#		requirement by multiplication.
#	2) We actually provide interfaces to several different libraries such as sympy and sage. 

from math import log10 as log

_name = None
# if _name is None:
	# try:
		# from Flipper.Kernel.SymbolicComputation_prototype import Algebraic_Type, Perron_Frobenius_eigen, algebraic_type_from_int, _name
	# except ImportError:
		# pass

if _name is None:
	try:
		from Flipper.Kernel.SymbolicComputation_sage import Algebraic_Type, Perron_Frobenius_eigen, algebraic_type_from_int, _name
	except ImportError:
		pass

if _name is None:
	try:
		from Flipper.Kernel.SymbolicComputation_sympy import Algebraic_Type, Perron_Frobenius_eigen, algebraic_type_from_int, _name
	except ImportError:
		pass

if _name is None:
	try:
		from Flipper.Kernel.SymbolicComputation_dummy import Algebraic_Type, Perron_Frobenius_eigen, algebraic_type_from_int, _name
	except ImportError:
		pass

#############################################################################
# We also build some helper functions using these.

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

