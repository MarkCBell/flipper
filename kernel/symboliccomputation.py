
# Exact symbolic calculations using types representing algebraic numbers. This is used to:
#	compute the stable lamination exactly.
#	compute splitting sequences.
#
# This module selects and imports the appropriate library for manipulating algebraic numbers.
# Currently there are three to choose from based on: sage, sympy and None, the last of which is
# a dummy library which can't do anything but makes sure that the imports never fail.
# Currently Sage is the best by a _large_ margin and so this is our first choice.
#
# Each library provides a class called AlgebraicType based off of 
# Flipper.kernel.symboliccomputation_dummy.AlgebraicType. The library must define:
#	simplify(self)
#		Puts self into a standard form.
#	minimal_polynomial_coefficients(self):
#		Returns the coefficients of the minimal polynomial of this algebraic number.
#	string_approximate(self, precision, power=1):
#		Returns a string containing an approximation of this algebraic number to the requested power, 
#		correct to the requested precision.
#
# The AlgebraicType also provides:
#	def degree(self):
#		Returns the degree of this number.
#	def log_height(self):
#		Returns the log height of this number.
#	def algebraic_approximate(self, accuracy, power=1):
#		Returns an AlgebraicApproximation of this number, correct to at least the requested accuracy.
# but these are derived automatically from AlgebraicType.minimal_polynomial_coefficients and AlgebraicType.string_approximate.
#
# Each library also provides a function for creating AlgebraicTypes:
#	Perron_Frobenius_eigen(matrix):
#		Given a Perron-Frobenius matrix (of type Flipper.kernel.matrix.Matrix) this must 
#		return its PF eigenvalue L, that is the unique eigenvalue with largest absolute value, 
#		as an AlgebraicType along with either: 
#			A list of integer coefficients [[v_ij]] such that:
#				v_i := sum(v_ij L^j) 
#			is the entries of the corresponding eigenvector, or
#			None.
#
# and a _name variable containing a string identifying the module. This is very useful for debugging.

# You can provide your own algebraic number library so long as it provides these methods and can be cast to a string via str().

_name = None

if _name is None:
	try:
		import Flipper.kernel.symboliccomputation_sage
		AlgebraicType = Flipper.kernel.symboliccomputation_sage.AlgebraicType
		Perron_Frobenius_eigen2 = Flipper.kernel.symboliccomputation_sage.Perron_Frobenius_eigen
		_name = Flipper.kernel.symboliccomputation_sage._name
	except ImportError:
		pass

if _name is None:
	try:
		import Flipper.kernel.symboliccomputation_sympy
		AlgebraicType = Flipper.kernel.symboliccomputation_sympy.AlgebraicType
		Perron_Frobenius_eigen2 = Flipper.kernel.symboliccomputation_sympy.Perron_Frobenius_eigen
		_name = Flipper.kernel.symboliccomputation_sympy._name
	except ImportError:
		pass

if _name is None:
	try:
		import Flipper.kernel.symboliccomputation_dummy
		AlgebraicType = Flipper.kernel.symboliccomputation_dummy.AlgebraicType
		Perron_Frobenius_eigen2 = Flipper.kernel.symboliccomputation_dummy.Perron_Frobenius_eigen
		_name = Flipper.kernel.symboliccomputation_dummy._name
	except ImportError:
		pass

def Perron_Frobenius_eigen(matrix):
	eigenvalue, eigenvector = Perron_Frobenius_eigen2(matrix)
	if eigenvector is None:
		d = eigenvalue.degree()
		w = matrix.width
		
		Id_d = Flipper.kernel.matrix.Id_Matrix(d)
		eigen_companion = Flipper.kernel.matrix.Companion_Matrix(eigenvalue.minimal_polynomial_coefficients())
		
		M2 = matrix.substitute_row(0, [1] * len(matrix))
		M3 = Flipper.kernel.matrix.Id_Matrix(w).substitute_row(0, [0] * w)
		
		M4 = (M2 ^ Id_d) - (M3 ^ eigen_companion)
		
		solution = M4.solve([1] + [0] * (len(M4)-1))
		eigenvector = [solution[i:i+d] for i in range(0, len(solution), d)]
	
	N = Flipper.kernel.numberfield.NumberField(eigenvalue)
	return [N.element(v) for v in eigenvector]

#############################################################################
# We also build some helper functions using these.

def compute_powers(a, b):
	# Given (real > 1) algebraic numbers a == c^m and b == c^n where c is another algebraic number and m & n are coprime 
	# integers returns m, n. This uses a variant of the Euclidean algorithm and can probably be done smarter.
	
	if a == b:
		return (1, 1)
	elif a > b:
		m2, n2 = compute_powers(a / b, b)
		return (m2 + n2, n2)
	else:
		m2, n2 = compute_powers(a, b / a)
		return (m2, n2 + m2)

