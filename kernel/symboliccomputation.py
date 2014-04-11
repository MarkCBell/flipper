
from importlib import import_module
from math import log10 as log

import flipper

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
#	PF_eigen(matrix, vector):
#		Given a matrix (of type flipper.kernel.Matrix) let L be its demoninant eigenvalue
#		and v = (v_1 ... v_k) the orthogonal projection of vector to the eigenspace of L. 
#		This returns the list of coefficients of a small (ideally minimal) integral polynomial 
#		of L and a list of list of integers [[v_ij]] such that v_i = sum(v_ij L**j). Throws
#		a flipper.AssertionError if L is not real.
# 
# and a symbolic_libaray_name variable containing a string identifying the module. This is very useful for debugging.
#
# You can provide your own library so long as it provides this function. Just add its name to the list and dictionary below.

### Add new libraries here ###
load_order = ['sage', 'dummy']
libraries = {'sage':'symboliccomputation_sage', 'dummy':'symboliccomputation_dummy'}

def load_library(library_name=None):
	for library in ([library_name] + load_order) if library_name in libraries else load_order:
		try:
			return import_module('flipper.kernel.' + libraries[library])
		except ImportError:
			pass
	
	raise ImportError('No symbolic computation library available.')

def Perron_Frobenius_eigen(matrix, curve):
	symbolic_computation_library = load_library()
	eigenvalue_coefficients, eigenvector_coefficients = symbolic_computation_library.PF_eigen(matrix, curve)
	eigenvalue_polynomial = flipper.kernel.Polynomial(eigenvalue_coefficients)
	
	N = flipper.kernel.NumberField(eigenvalue_polynomial)
	eigenvector = [N.element(v) for v in eigenvector_coefficients]
	
	return eigenvector

