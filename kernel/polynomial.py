
from fractions import Fraction
from math import log10 as log

import Flipper

# In Python3 we can just do round(fraction, accuracy) however this
# doesn't exist in Python2 so we recreate it here. 
def round_fraction(fraction, accuracy):
	shifted = fraction * 10**accuracy
	# We will always round down.
	numerator = shifted.numerator // shifted.denominator
	
	# If we tried to return a Fraction then we might lose most of the 
	# accuracy that we created due to simplification.
	return (numerator, accuracy)

def ceiling_fraction(fraction):
	numerator, accuracy = round_fraction(fraction, 0)
	return numerator + 1

# This class represents an integral polynomial. In various places we will assume that it is 
# irreducible and / or monic.
class Polynomial(object):
	def __init__(self, coefficients):
		self.coefficients = coefficients
		self.height = max(abs(x) for x in self.coefficients) if self.coefficients else 1
		self.log_height = log(self.height)
		self.degree = len(self.coefficients) - 1
		self._old_root = None
		self._root = Fraction(self.height * self.degree, 1)
		self.accuracy = -1
	
	def __iter__(self):
		return iter(self.coefficients)
	
	def __repr__(self):
		return ' + '.join('%d x^%d' % (coefficient, index) for index, coefficient in enumerate(self))
	
	def __call__(self, other):
		return sum(coefficient * other**index for index, coefficient in enumerate(self))
	
	def derivative(self):
		return Polynomial([index * coefficient for index, coefficient in enumerate(self)][1:]) 
	
	def find_leading_root(self, accuracy):
		if self.accuracy < accuracy:
			f = self
			f_prime = self.derivative()
			# Iterate using Newton's method until the error becomes small enough. 
			while self.accuracy < accuracy:
				self._old_root, self._root = self._root, self._root - f(self._root) / f_prime(self._root)
				if self._old_root == self._root: 
					self.accuracy = accuracy
				else:
					self.accuracy = log(abs(self._root.denominator)) + log(abs(self._old_root.denominator)) - log(abs(self._root.numerator * self._old_root.denominator - self._old_root.numerator * self._root.denominator))
		
		return self._root
	
	def algebraic_approximate_leading_root(self, accuracy, power=1):
		# Returns an algebraic approximation of this polynomials leading root raised to the requested power
		# which is correct to at least accuracy decimal places.
		power_error = int(log(ceiling_fraction(self.find_leading_root(accuracy)))) + 1
		
		working_accuracy = accuracy + power * power_error
		numerator, precision = round_fraction(self.find_leading_root(working_accuracy), working_accuracy)
		
		return Flipper.kernel.algebraicapproximation.algebraic_approximation_from_fraction(numerator, precision, self.degree, self.log_height)**power
