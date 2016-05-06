
''' A module for interacting with various symbolic calculation libraries.

This module selects and imports the appropriate interface for manipulating algebraic numbers.
Currently there is an interface to sage, cypari and a dummy library. A library should raise an
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
INTERFACES = ['sage', 'cypari', 'dummy']

def load_interface():
	''' Return the first available interface.
	
	If none are available then an ImportError will be raised.
	This should nver happen thanks to the dummy interface provided. '''
	
	for interface in INTERFACES:
		try:
			module = import_module('flipper.kernel.interface.' + interface)
			# We could add some code here to find out which interface was loaded.
			return module
		except ImportError:
			pass
	
	raise ImportError('No symbolic computation interface available.')

def directed_eigenvector(action_matrix, condition_matrix):
	''' Return an interesting eigenvector of action_matrix which lives inside of the cone C, defined by condition_matrix.
	
	An eigenvector is interesting if its corresponding eigenvalue is: real, > 1, irrational and bigger than all
	of its Galois conjugates.
	
	Raises a ComputationError if it cannot find an interesting vectors in C.
	Assumes that C contains at most one interesting eigenvector. '''
	
	return load_interface().directed_eigenvector(action_matrix, condition_matrix)

