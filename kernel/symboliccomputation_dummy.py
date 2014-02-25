
from math import log10 as log

import Flipper

_name = 'dummy'

# This symbolic calculation library provides a dummy AlgebraicType class which
# holds a single value and can add, subtract ...
# Other librarys can modify this class to save them from implementing 
# all of these features from scratch. Features which don't work should be removed
# by setting the functions to NotImplemented.

class AlgebraicType(object):
	def __init__(self, value):
		# We make sure to always start by using AlgebraicType.simplify(), just to be safe.
		self.value = value
		self.simplify()
	
	def __str__(self):
		return str(self.value)
	
	def __repr__(self):
		return repr(self.value)
	
	def simplify(self):
		pass
	
	def minimal_polynomial_coefficients(self):
		return None
	
	def degree(self):
		return len(self.minimal_polynomial_coefficients()) - 1
	
	def log_height(self):
		return log(max(abs(x) for x in self.minimal_polynomial_coefficients()))
	
	def string_approximate(self, precision, power=1):
		return '1.0'
	
	def algebraic_approximate(self, accuracy, power=1):
		# First we need to correct for the fact that we may lose some digits of accuracy if the integer part of the number is big.
		precision = accuracy + len(self.string_approximate(1))
		A = Flipper.kernel.algebraicapproximation.algebraic_approximation_from_string(self.string_approximate(precision), self.degree(), self.log_height())
		assert(A.interval.accuracy >= accuracy)
		return A

def Perron_Frobenius_eigen(matrix):
	raise ImportError('Dummy symbolic computation library cannot do this calculation.')
	return None, None
