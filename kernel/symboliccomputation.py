
''' A module for interacting with various symbolic calculation libraries.

This module selects and imports the appropriate library for manipulating algebraic numbers.
Currently there is an interface to sage and 

There used to be an interface to SymPy but this turned out to be extremely unreliable. There 
were 9x9 invertible matrices for which it could only find 1 eigenvalue!

The dummy library also includes a basic implementation of the gram-schmidt orthonormalisation 
process that other libraries may be able to make use of.

Each library provides one function:
	perron_frobenius_eigen(matrix, vector):
		Given a matrix (of type flipper.kernel.Matrix) let L be its dominant eigenvalue and
		V be its corresponding eigenspace. Let v be the orthogonal projection of vector to
		V. Return L, v where L is a NumberFieldElement and v is a list of NumberFieldElements.
		
		Assumes (and checks) that L is real.

More interfaces can be added here. '''

import flipper

from importlib import import_module

# Add new libraries here in order.
libraries = ['symboliccomputation_sage', 'symboliccomputation_dummy']

def load_library():
	''' Return the first available library.
	
	If none are available then an ImportError will be raised. '''
	
	for library in libraries:
		try:
			return import_module('flipper.kernel.' + library)
		except ImportError:
			pass
	
	raise ImportError('No symbolic computation library available.')

def perron_frobenius_eigen(matrix, curve):
	''' Apply the perron_frobenius_eigen function from the correct library. '''
	
	symbolic_computation_library = load_library()
	return symbolic_computation_library.perron_frobenius_eigen(matrix, curve)
	#return symbolic_computation_library.perron_frobenius_eigen(matrix, curve)

