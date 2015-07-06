
''' A module for performing symbolic calculations using sage. '''

import flipper

from sage.all import Matrix, Polyhedron, lcm, NumberField
from sage.version import version
from math import log10 as log
from distutils.version import StrictVersion

if StrictVersion(version) >= StrictVersion('6.5'):
	def coefficients(polynomial):
		''' Return the coefficients of this polynomial. '''
		
		return polynomial.coefficients(sparse=False)
else:
	def coefficients(polynomial):
		''' Return the coefficients of this polynomial. '''
		
		return polynomial.coeffs()

def minpoly_coefficients(number):
	''' Return the list of coefficients of the minimal polynomial of the given number. '''
	
	polynomial = number.minpoly()
	scale = abs(lcm([x.denominator() for x in coefficients(polynomial)]))
	return [int(scale * x) for x in coefficients(polynomial)]

def approximate(number, accuracy):
	''' Return a string approximating the given number to the given accuracy. '''
	
	s = str(number.n(digits=1))
	mantissa, exponent = s.split('e') if 'e' in s else (s, '0')
	(integer, decimal), exponent = (mantissa.split('.') if '.' in mantissa else (mantissa, '')), int(exponent)
	s = str(number.n(digits=len(integer)+int(exponent)+accuracy))
	mantissa, exponent = s.split('e') if 'e' in s else (s, '0')
	(integer, decimal), exponent = (mantissa.split('.') if '.' in mantissa else (mantissa, '')), int(exponent)
	if exponent >= 0:
		return integer + decimal[:exponent] + '.' + decimal[exponent:exponent+accuracy]
	else:
		return '0.' + '0' * (-exponent-1) + decimal[:accuracy]

def directed_eigenvector(action_matrix, condition_matrix, vector):
	''' Return an interesting eigenvector of action_matrix which lives inside of the cone C, defined by condition_matrix.
	
	This version is perfect, that is a ComputationError is raised if and only if
	C contains no interesting eigenvectors.
	
	An eigenvector is interesting if its corresponding eigenvalue is: real, > 1 and irrational.
	Raises a ComputationError if it cannot find an interesting vectors in C.
	
	vector is guranteed to live inside of C.
	
	Assumes that C contains at most one interesting eigenvector. '''
	
	M = Matrix(action_matrix.rows)
	# Only bother checking the real, stable eigenspaces.
	eigenvalues = [eigenvalue for eigenvalue in M.eigenvalues() if eigenvalue.imag() == 0 and eigenvalue > 1]
	# We have to check ALL eigenspaces. So we do it in order of decreasing real part.
	for eigenvalue in sorted(eigenvalues, reverse=True, key=lambda z: complex(z).real):
		[lam] = NumberField(eigenvalue.minpoly(), 'L', embedding=eigenvalue.n()).gens()
		right_kernel = (M-lam).right_kernel().basis()
		
		if len(right_kernel) == 1:  # If rank(kernel) == 1.
			[eigenvector] = right_kernel
			
			scale = abs(lcm([x.denominator() for entry in eigenvector for x in coefficients(entry.polynomial())]))
			eigenvector_rescaled_coefficients = [[int(scale * x) for x in coefficients(entry.polynomial())] for entry in eigenvector]
			
			eigenvalue_coefficients = minpoly_coefficients(eigenvalue)
			d = int(log(sum(abs(x) for x in eigenvalue_coefficients))) + 1
			N = flipper.kernel.create_number_field(eigenvalue_coefficients, approximate(eigenvalue, 2*d + 1))
			flipper_ev, flipper_eigenvector = N.lmbda, [N.element(entry) for entry in eigenvector_rescaled_coefficients]
			
			# We can't rely on Sage to check this lies in the cone as for elements of NumberFields:
			#  x > y returns True
			# See: https://groups.google.com/forum/#!topic/sage-devel/9eAZnOBvBHM
			if flipper.kernel.matrix.nonnegative(flipper_eigenvector) and condition_matrix.nonnegative_image(flipper_eigenvector):
				return flipper_ev, flipper_eigenvector
		else:
			eqns = [[0] + list(row) for row in (M - eigenvalue)]
			ieqs = [[0] + list(row) for row in condition_matrix]
			
			# This is really slow.
			P = Polyhedron(eqns=eqns, ieqs=ieqs)
			# If dim(P) == 1 then an extremal ray of the cone is an eigenvector.
			# As this is a rational vector it must correspond to a fixed curve.
			# If dim(P)  > 1 then there is a high dimensional invariant subspace.
			if eigenvalue > 1 and P.dim() > 0:
				raise flipper.AssumptionError('Subspace is reducible.')
	
	raise flipper.ComputationError('No interesting eigenvalues in cell.')

