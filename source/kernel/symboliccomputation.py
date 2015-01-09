
''' A module for interacting with various symbolic calculation libraries.

This module selects and imports the appropriate library for manipulating algebraic numbers.
Currently there is an interface to sage and a dummy library. A library should raise an
ImportError on import if it cannot be used. The dummy library can always be used, even in
Python 3.

There used to be an interface to SymPy but this turned out to be extremely unreliable. There
were 9x9 invertible matrices for which it could only find 1 eigenvalue!

The dummy library also includes a basic implementation of the gram-schmidt orthonormalisation
process and project function that other libraries may be able to make use of.

Each library provides one function:
	directed_eigenvector(action_matrix, condition_matrix, vector)

More interfaces can be added here. '''

from importlib import import_module

# Add new libraries here in order.
LIBRARIES = ['symboliccomputation_sage', 'symboliccomputation_dummy']

def load_library():
	''' Return the first available library.
	
	If none are available then an ImportError will be raised. '''
	
	for library in LIBRARIES:
		try:
			return import_module('flipper.kernel.' + library)
		except ImportError:
			pass
	
	raise ImportError('No symbolic computation library available.')

def directed_eigenvector(action_matrix, condition_matrix, curve):
	''' Apply the directed_eigenvector function from the correct library. '''
	
	return load_library().directed_eigenvector(action_matrix, condition_matrix, curve)

