
from importlib import import_module
from math import log10 as log

import Flipper

# Exact symbolic calculations using types representing algebraic numbers. This is used to:
#	compute the stable lamination exactly, and
#	compute splitting sequences.
#
# This module selects and imports the appropriate library for manipulating algebraic numbers.
# Currently there is only an interface to sage though more can easily be added. We used to 
# have an interface to SymPy but this turned out to be extremely unreliable, there were 9x9 
# invertible matrices for which it could only find 1 eigenvalue!
#
# Each library provides one function:
#	PF_eigen(matrix):
#		Given a Perron-Frobenius matrix (of type Flipper.kernel.Matrix) with PF eigenvalue / vector L, v 
#		(i.e. the unique eigenvalue with largest absolute value) this must return a pair (c, l) where:
#			c is a list of the coefficients of the minimal polynomial of L, and 
#			v is either: 
#				A list of integer coefficients [[v_ij]] such that v_i := sum(v_ij L^j) are the entries of the corresponding eigenvector, or
#				None.
# 
# and a symbolic_libaray_name variable containing a string identifying the module. This is very useful for debugging.
#
# You can provide your own library so long as it provides this function. Just add its name to the list and dictionary below.

### Add new libraries here ###
load_order = ['sage']
libraries = {'sage':'symboliccomputation_sage'}

def load_library(library_name=None):
	for library in ([library_name] + load_order) if library_name in libraries else load_order:
		try:
			return import_module('Flipper.kernel.' + libraries[library])
		except ImportError:
			pass
	
	raise ImportError('No symbolic computation library available.')

def Perron_Frobenius_eigen(matrix):
	symbolic_computation_library = load_library()
	eigenvalue_coefficients, eigenvector = symbolic_computation_library.PF_eigen(matrix)
	eigenvalue_polynomial = Flipper.kernel.Polynomial(eigenvalue_coefficients)
	print(eigenvalue_polynomial)
	print(matrix.char_poly())
	#if eigenvector is None:
	if True
		# We will calculate the eigenvector ourselves.
		# Suppose that M is an nxn matrix and deg(\lambda) = d. Let C be the companion matrix of \lambda
		
		# We now consider QQ(\lambda) as a vector space over QQ with basis 1, \lambda, ..., \lambda^{d-1}. 
		# Therefore finding a vector in ker(matrix - \lambda id) with entries in QQ(\lambda) is equivalent 
		# to finding a vector in ken(M ^ id_d - C ^ id_n) with entries in QQ, where ^ denotes the tensor
		# product of matrices. We can now do this just by using linear algebra.
		
		print(matrix)
		d = eigenvalue_polynomial.degree
		n = matrix.width
		
		Id_d = Flipper.kernel.Id_Matrix(d)
		eigen_companion = eigenvalue_polynomial.companion_matrix()
		
		M2 = matrix.substitute_row(0, [1] * n)
		M3 = Flipper.kernel.Id_Matrix(n).substitute_row(0, [0] * n)
		M4 = (M2 ^ Id_d) - (M3 ^ eigen_companion)
		print(M4)
		
		solution = M4.solve([1] + [0] * (len(M4)-1))
		print(solution)
		eigenvector = [solution[i:i+d] for i in range(0, len(solution), d)]
	
	N = Flipper.kernel.NumberField(eigenvalue_polynomial)
	return [N.element(v) for v in eigenvector]

