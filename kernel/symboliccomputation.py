

# !! Eventually change.

# Exact symbolic calculations using types representing algebraic numbers. This is used to:
#	compute the stable lamination exactly, and
#	compute splitting sequences.
#
# This module selects and imports the appropriate library for manipulating algebraic numbers.
# Currently there is only an interface to sage though more can easily be added. We used to
# have an interface to SymPy but this turned out to be extremely unreliable, there were 9x9
# invertible matrices for which it could only find 1 eigenvalue!
#
# There is also a dummy library which has a basic implementation of the gram schmidt 
# orthonormalisation process that other libraries may be able to make use of.
#
# Each library provides one function:
#	PF_eigen(matrix, vector):
#		Given a matrix (of type flipper.kernel.Matrix) let L be its demoninant eigenvalue
#		and v = (v_1 ... v_k) the orthogonal projection of vector to the eigenspace of L.
#		This returns the list of coefficients of a small (ideally minimal) integral polynomial
#		of L and a list of list of integers [[v_ij]] such that:
#			v_i = sum(v_ij L**j).
#		Throws a flipper.AssertionError if L is not real.
#
# You can provide your own library so long as it provides this function. Just add its name to the list and dictionary below.

import flipper

from importlib import import_module

### Add new libraries here ###
libraries = ['symboliccomputation_sage', 'symboliccomputation_dummy']

def load_library():
	for library in libraries:
		try:
			return import_module('flipper.kernel.' + library)
		except ImportError:
			pass
	
	raise ImportError('No symbolic computation library available.')

def Perron_Frobenius_eigen(matrix, curve):
	symbolic_computation_library = load_library()
	return symbolic_computation_library.PF_eigen(matrix, curve)
	#return symbolic_computation_library.PF_eigen2(matrix, curve)

