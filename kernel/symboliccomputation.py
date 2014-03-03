
# Exact symbolic calculations using types representing algebraic numbers. This is used to:
#	compute the stable lamination exactly, and
#	compute splitting sequences.
#
# This module selects and imports the appropriate library for manipulating algebraic numbers.
# Currently there are three to choose from based on: sage, sympy and None, the last of which is
# a dummy library which can't do anything but makes sure that the imports never fail.
# Currently Sage is the best by a _large_ margin and so this is our first choice.
#
# Each library provides a single function:
#	PF_eigen(matrix):
#		Given a Perron-Frobenius matrix (of type Flipper.kernel.matrix.Matrix) with PF eigenvalue / vector L, v 
#		(i.e. the unique eigenvalue with largest absolute value) this must return a pair (c, l) where:
#			c is a list of the coefficients of the minimal polynomial of L, and 
#			v is either: 
#				A list of integer coefficients [[v_ij]] such that v_i := sum(v_ij L^j) are the entries of the corresponding eigenvector, or
#				None.
#
# and a _name variable containing a string identifying the module. This is very useful for debugging.
#
# You can provide your own algebraic number library so long as it provides this function.

_name = None

if _name is None:
	try:
		import Flipper.kernel.symboliccomputation_sage
		PF_eigen = Flipper.kernel.symboliccomputation_sage.PF_eigen
		_name = Flipper.kernel.symboliccomputation_sage._name
	except ImportError:
		pass

if _name is None:
	try:
		import Flipper.kernel.symboliccomputation_sympy
		PF_eigen = Flipper.kernel.symboliccomputation_sympy.PF_eigen
		_name = Flipper.kernel.symboliccomputation_sympy._name
	except ImportError:
		pass

if _name is None:
	try:
		import Flipper.kernel.symboliccomputation_dummy
		PF_eigen = Flipper.kernel.symboliccomputation_dummy.PF_eigen
		_name = Flipper.kernel.symboliccomputation_dummy._name
	except ImportError:
		pass

def Perron_Frobenius_eigen(matrix):
	eigenvalue_coefficients, eigenvector = PF_eigen(matrix)
	if eigenvector is None:
		# We will calculate the eigenvector ourselves. 
		# Suppose that M is an nxn matrix and deg(\lambda) = d. Let C be the companion matrix of \lambda
		
		# We now consider QQ(\lambda) as a vector space over QQ with basis 1, \lambda, ..., \lambda^{d-1}. 
		# Therefore finding a vector in ker(matrix - \lambda id) with entries in QQ(\lambda) is equivalent 
		# to finding a vector in ken(M ^ id_d - C ^ id_n) with entries in QQ, where ^ denotes the tensor
		# product of matrices. We can now do this just by using linear algebra.
		
		d = eigenvalue.degree()
		n = matrix.width
		
		Id_d = Flipper.kernel.matrix.Id_Matrix(d)
		eigen_companion = Flipper.kernel.matrix.Companion_Matrix(eigenvalue.minimal_polynomial_coefficients())
		
		M2 = matrix.substitute_row(0, [1] * len(matrix))
		M3 = Flipper.kernel.matrix.Id_Matrix(n).substitute_row(0, [0] * n)
		
		M4 = (M2 ^ Id_d) - (M3 ^ eigen_companion)
		
		solution = M4.solve([1] + [0] * (len(M4)-1))
		eigenvector = [solution[i:i+d] for i in range(0, len(solution), d)]
	
	N = Flipper.kernel.numberfield.NumberField(Flipper.Polynomial(eigenvalue_coefficients))
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

